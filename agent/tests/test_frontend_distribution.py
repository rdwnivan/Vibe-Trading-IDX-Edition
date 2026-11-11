"""Distribution artifacts must carry the UI, independent of a source checkout."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("layout", ["source", "desktop", "wheel"])
def test_frontend_resolution_is_code_relative(layout, tmp_path, monkeypatch):
    from src.api import frontend

    root = tmp_path / layout
    package_root = root / ("agent" if layout == "source" else "Lib/site-packages")
    repo_root = root if layout == "source" else root / "Lib"
    api = package_root / "src" / "api"
    source_dist = repo_root / "frontend" / "dist"
    source_dist.mkdir(parents=True)
    (source_dist / "index.html").write_text("source UI")
    monkeypatch.setattr(frontend, "__file__", str(api / "frontend.py"))
    monkeypatch.chdir(tmp_path)
    if layout == "wheel":
        expected = api / "_frontend"
        expected.mkdir(parents=True)
        (expected / "index.html").write_text("packaged UI")
    else:
        expected = source_dist
    assert frontend.resolve_frontend_dist() == expected
    assert frontend.resolve_frontend_dist(repo_root) == expected


@pytest.fixture
def distribution_source(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for name in ("pyproject.toml", "MANIFEST.in", "README.md", "LICENSE", "setup.py"):
        shutil.copyfile(ROOT / name, source / name)
    api = source / "agent" / "src" / "api"
    api.mkdir(parents=True)
    (api.parent / "__init__.py").write_text("")
    (api / "__init__.py").write_text("")
    for name in ("frontend.py", "spa.py"):
        shutil.copyfile(ROOT / "agent" / "src" / "api" / name, api / name)
    dist = source / "frontend" / "dist"
    (dist / "assets" / "nested").mkdir(parents=True)
    (dist / "index.html").write_text('<html><script src="/assets/app.js"></script></html>')
    (dist / "assets" / "app.js").write_text("/* fixture build */")
    (dist / "assets" / "nested" / "font.woff2").write_bytes(b"fixture-font")
    return source


@pytest.fixture(scope="module")
def build_python(tmp_path_factory):
    pytest.importorskip("setuptools", reason="offline packaging tests require an already available setuptools backend")
    root = tmp_path_factory.mktemp("packaging-python")
    result = subprocess.run([sys.executable, "-m", "venv", str(root)], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def build_environment():
    env = {
        key: os.environ[key]
        for key in (
            "SYSTEMROOT",
            "WINDIR",
            "COMSPEC",
            "PATH",
            "TEMP",
            "TMP",
            "HOME",
            "USERPROFILE",
            "APPDATA",
            "LOCALAPPDATA",
            "USERNAME",
            "USER",
            "LOGNAME",
        )
        if key in os.environ
    }
    env.update(
        PIP_CONFIG_FILE=os.devnull,
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        PIP_NO_INDEX="1",
        PIP_NO_CACHE_DIR="1",
        PYTHONNOUSERSITE="1",
    )
    # The isolated builder reuses this backend; it never provisions build requirements.
    backend = importlib.util.find_spec("setuptools")
    if backend is not None and backend.origin is not None:
        env["PYTHONPATH"] = str(Path(backend.origin).resolve().parents[1])
    return env


def build_wheel(source, output, build_python):
    return subprocess.run(
        [
            str(build_python),
            "-m",
            "pip",
            "wheel",
            "--no-index",
            "--no-build-isolation",
            "--no-deps",
            "--wheel-dir",
            str(output),
            str(source),
        ],
        cwd=source.parent,
        env=build_environment(),
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_wheel_build_uses_only_the_available_backend_without_package_indexes(tmp_path, monkeypatch):
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", run)

    build_wheel(tmp_path / "source", tmp_path / "wheels", Path("fixture-python"))

    args, kwargs = calls[0]
    assert {"--no-index", "--no-build-isolation", "--no-deps"} <= set(args)
    assert kwargs["env"]["PIP_NO_INDEX"] == "1"
    assert kwargs["env"]["PIP_CONFIG_FILE"] == os.devnull


@pytest.mark.integration
def test_wheel_contains_built_ui_and_resolves_it_outside_checkout(distribution_source, tmp_path, build_python):
    output = tmp_path / "wheels"
    result = build_wheel(distribution_source, output, build_python)
    assert result.returncode == 0, result.stdout + result.stderr
    installed = tmp_path / "installed"
    with zipfile.ZipFile(next(output.glob("*.whl"))) as wheel:
        assert "src/api/_frontend/index.html" in wheel.namelist()
        assert "src/api/_frontend/assets/app.js" in wheel.namelist()
        assert "src/api/_frontend/assets/nested/font.woff2" in wheel.namelist()
        wheel.extractall(installed)
    # Remove the original build: an installed package must never reach back to it.
    shutil.rmtree(distribution_source)
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from src.api.frontend import resolve_frontend_dist
from src.api.spa import SPAStaticFiles
from fastapi import FastAPI
from fastapi.testclient import TestClient
dist = resolve_frontend_dist()
assert dist.is_relative_to(Path(sys.argv[1]))
app = FastAPI()
app.mount('/', SPAStaticFiles(directory=dist, html=True))
client = TestClient(app)
assert client.get('/research/idx').text == (dist / 'index.html').read_text()
assert client.get('/assets/app.js').text == '/* fixture build */'
assert client.get('/assets/nested/font.woff2').content == b'fixture-font'
print('installed SPA and nested assets OK')
""",
            str(installed),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    assert "installed SPA and nested assets OK" in probe.stdout


@pytest.mark.integration
def test_wheel_without_frontend_build_fails_with_remediation(distribution_source, tmp_path, build_python):
    shutil.rmtree(distribution_source / "frontend" / "dist")
    result = build_wheel(distribution_source, tmp_path / "wheels", build_python)
    assert result.returncode != 0
    assert "npm ci" in result.stdout + result.stderr
    assert "npm run build" in result.stdout + result.stderr


@pytest.mark.integration
def test_editable_development_install_can_precede_frontend_build(distribution_source, build_python):
    shutil.rmtree(distribution_source / "frontend" / "dist")
    result = subprocess.run(
        [
            str(build_python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-build-isolation",
            "--no-deps",
            "--editable",
            str(distribution_source),
        ],
        cwd=distribution_source.parent,
        env=build_environment(),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
