"""Block real network traffic through curl_cffi for the whole test suite.

yfinance (``Ticker.history``, ``yf.download``) and the browser-impersonating
HTTP helpers send requests through curl_cffi. curl_cffi opens its sockets inside
libcurl, in C, so ``pytest-socket`` (``--disable-socket``, ``--allow-hosts``)
never sees them: a test that forgets to stub one of those paths quietly calls
the real provider. That is how two IDX research tests ended up fetching
BBCA.JK/BBRI.JK from Yahoo on every run (2026-11-16).

``install()`` replaces every curl_cffi entry point that can open a connection
with a function that records the attempt and raises ``CurlCffiNetworkBlocked``.
Raising alone is not enough: yfinance catches broad exceptions and returns an
empty frame, so the conftest also fails any test that has a recorded attempt
once it finishes (see ``take_attempts``).

A test that really needs the network marks itself
``@pytest.mark.allow_curl_cffi_network``. The default suite has none.
"""

from __future__ import annotations

import functools
import os
from collections.abc import Callable
from typing import Any

ALLOW_MARKER = "allow_curl_cffi_network"

# (class attribute path, is_async). Session.request covers get/post/stream and
# the module-level curl_cffi.requests.get(...) helpers, which all delegate to it;
# ws_connect performs its own handshake; Curl.perform is the libcurl call the
# sync paths end in, kept as a backstop for code that drives Curl directly.
_TARGETS: tuple[tuple[str, str, bool], ...] = (
    ("curl_cffi.requests", "Session.request", False),
    ("curl_cffi.requests", "Session.ws_connect", False),
    ("curl_cffi.requests", "AsyncSession.request", True),
    ("curl_cffi.requests", "AsyncSession.ws_connect", False),
    ("curl_cffi", "Curl.perform", False),
)

_attempts: list[str] = []
_originals: dict[tuple[type, str], Callable[..., Any]] = {}
_allowed = False


class CurlCffiNetworkBlocked(RuntimeError):
    """A test tried to open a real connection through curl_cffi."""


def _describe(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    url = kwargs.get("url")
    if url is None:
        # request(self, method, url, ...) / ws_connect(self, url, ...)
        positional = [a for a in args[1:] if isinstance(a, str)]
        url = positional[-1] if positional else "<unknown url>"
    test = os.environ.get("PYTEST_CURRENT_TEST", "<outside a test>")
    return f"{test}: curl_cffi {name} -> {url}"


def _blocked(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> CurlCffiNetworkBlocked:
    where = _describe(name, args, kwargs)
    _attempts.append(where)
    return CurlCffiNetworkBlocked(
        f"Real network access through curl_cffi is blocked in tests ({where}). "
        "Stub the provider call (for yfinance IDX symbols, yfinance_loader._idx_history "
        "and yf.download), or mark the test @pytest.mark.allow_curl_cffi_network if it "
        "must reach the network."
    )


def _wrap(name: str, original: Callable[..., Any], is_async: bool) -> Callable[..., Any]:
    if is_async:

        @functools.wraps(original)
        async def guarded_async(*args: Any, **kwargs: Any) -> Any:
            if _allowed:
                return await original(*args, **kwargs)
            raise _blocked(name, args, kwargs)

        return guarded_async

    @functools.wraps(original)
    def guarded(*args: Any, **kwargs: Any) -> Any:
        if _allowed:
            return original(*args, **kwargs)
        raise _blocked(name, args, kwargs)

    return guarded


def install() -> bool:
    """Patch curl_cffi in place. Returns False when curl_cffi is not installed."""
    import importlib

    try:
        importlib.import_module("curl_cffi.requests")
    except ImportError:
        return False
    for module_name, attr_path, is_async in _TARGETS:
        owner_name, method = attr_path.split(".")
        owner = getattr(importlib.import_module(module_name), owner_name, None)
        original = getattr(owner, method, None) if owner is not None else None
        if original is None or (owner, method) in _originals:
            continue
        _originals[(owner, method)] = original
        setattr(owner, method, _wrap(attr_path, original, is_async))
    return True


def installed() -> bool:
    return bool(_originals)


def set_allowed(allowed: bool) -> None:
    """Let the current test through (``allow_curl_cffi_network``) or block again."""
    global _allowed
    _allowed = allowed


def take_attempts() -> list[str]:
    """Return and clear the blocked attempts recorded since the last call."""
    taken = list(_attempts)
    _attempts.clear()
    return taken
