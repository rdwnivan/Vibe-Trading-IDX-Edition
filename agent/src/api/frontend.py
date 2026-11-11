"""Locate immutable UI assets for wheel, source, and desktop installations."""

from pathlib import Path


def resolve_frontend_dist(repo_root: Path | None = None) -> Path:
    """Prefer the UI shipped with this package, then the source/desktop layout.

    The fallback is code-relative, never relative to the working directory or
    runtime home. A missing build is reported by the server startup caller.
    """
    bundled = Path(__file__).resolve().parent / "_frontend"
    if (bundled / "index.html").is_file():
        return bundled
    root = repo_root if repo_root is not None else Path(__file__).resolve().parents[3]
    return root / "frontend" / "dist"
