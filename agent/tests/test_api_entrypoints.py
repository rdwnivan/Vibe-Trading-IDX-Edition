"""Subprocess entry points use one assembler without touching private state."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.fixture(scope="module")
def isolated_source(tmp_path_factory):
    root = tmp_path_factory.mktemp("api-entrypoints")
    source = Path(__file__).resolve().parents[1]
    # Copy code/package data only, never legacy state or a developer's dotenv.
    for directory in ("src", "cli", "backtest"):
        for path in (source / directory).rglob("*"):
            if path.is_file() and path.suffix in {".py", ".json", ".yaml", ".md"}:
                target = root / "agent" / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
    shutil.copyfile(source / "api_server.py", root / "agent" / "api_server.py")
    home = root / "home"
    home.mkdir()
    env = {
        key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "TEMP", "TMP") if key in os.environ
    }
    env.update(
        HOME=str(home),
        USERPROFILE=str(home),
        APPDATA=str(home / "appdata"),
        LOCALAPPDATA=str(home / "localappdata"),
        VIBE_TRADING_HOME=str(home / "runtime"),
        PYTHONPATH=str(root / "agent"),
        PYTHONNOUSERSITE="1",
    )
    # Imports must remain offline; --help never enters lifespan/preflight.
    (root / "agent" / "sitecustomize.py").write_text(
        "import socket\n"
        "def offline(*args, **kwargs):\n"
        "    raise AssertionError('entry point test attempted network access')\n"
        "socket.socket.connect = offline\n"
        "socket.socket.connect_ex = offline\n",
        encoding="utf-8",
    )
    return root, env


def _run(isolated_source, *args):
    root, env = isolated_source
    return subprocess.run(
        [sys.executable, *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )


@pytest.mark.parametrize(
    "entry",
    [
        ["agent/api_server.py"],
        ["-m", "api_server"],
        ["-m", "agent.api_server"],
        ["-m", "cli", "serve"],
    ],
)
def test_server_entrypoint_help_reaches_argument_parser(isolated_source, entry):
    result = _run(isolated_source, *entry, "--help")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "--host" in result.stdout
    assert "--port" in result.stdout


@pytest.mark.parametrize("module", ["api_server", "agent.api_server"])
def test_import_names_share_the_same_host_and_app(isolated_source, module):
    result = _run(
        isolated_source,
        "-c",
        f"""
import importlib
first = importlib.import_module({module!r})
canonical = importlib.import_module('api_server')
qualified = importlib.import_module('agent.api_server')
assert first is canonical is qualified, 'duplicate API host modules'
assert first.app is canonical.app is qualified.app
assert first._lifespan is canonical._lifespan is qualified._lifespan
assert any(getattr(r, 'path', '') == '/health' for r in first.app.routes)
print('single-host-app')
""",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "single-host-app" in result.stdout


@pytest.mark.parametrize("entry", ["file", "api_server", "agent.api_server"])
def test_executable_entrypoint_serves_the_registered_host_app(isolated_source, entry):
    result = _run(
        isolated_source,
        "-c",
        f"""
import importlib, runpy, sys, uvicorn
def verify(app, **kwargs):
    canonical = importlib.import_module('api_server')
    qualified = importlib.import_module('agent.api_server')
    assert canonical is qualified, 'duplicate API host modules'
    assert canonical.app is app, 'server received a different app'
    assert canonical._lifespan is qualified._lifespan
    assert kwargs['host'] == '127.0.0.1'
    print('serving-host-app')
uvicorn.run = verify
sys.argv = ['api_server', '--host', '127.0.0.1']
if {entry!r} == 'file':
    runpy.run_path('agent/api_server.py', run_name='__main__')
else:
    runpy.run_module({entry!r}, run_name='__main__', alter_sys=True)
""",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "serving-host-app" in result.stdout
