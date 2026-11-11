"""Bundle the prebuilt Web UI; Node is a build-time requirement for maintainers."""

from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
from setuptools.errors import SetupError


ROOT = Path(__file__).resolve().parent
FRONTEND_DIST = ROOT / "frontend" / "dist"


def require_frontend_build():
    if not (FRONTEND_DIST / "index.html").is_file():
        raise SetupError("Web UI build missing. Before packaging, run: cd frontend && npm ci && npm run build")


class BuildWithFrontend(build_py):
    def run(self):
        # Editable development serves frontend/dist directly; it does not
        # distribute assets and may be installed before the first Vite build.
        if self.editable_mode:
            return super().run()
        require_frontend_build()
        super().run()
        target = Path(self.build_lib) / "src" / "api" / "_frontend"
        # This directory is generated build output. Replace it so repeated
        # builds cannot ship obsolete hashed bundles from an earlier UI.
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(FRONTEND_DIST, target)


class SourceWithFrontend(sdist):
    def run(self):
        require_frontend_build()
        super().run()


setup(cmdclass={"build_py": BuildWithFrontend, "sdist": SourceWithFrontend})
