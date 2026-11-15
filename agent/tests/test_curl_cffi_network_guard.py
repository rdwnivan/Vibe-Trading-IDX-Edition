"""The suite-wide curl_cffi guard (tests/_curl_cffi_guard.py) blocks real requests.

Each test drains the recorded attempts itself; otherwise the conftest teardown
check would (correctly) fail it for having tried.
"""

from __future__ import annotations

import pytest

from tests import _curl_cffi_guard as guard

curl_requests = pytest.importorskip("curl_cffi.requests")

URL = "https://query2.finance.yahoo.com/v8/finance/chart/BBCA.JK"


def test_guard_is_installed_for_the_suite():
    assert guard.installed()


def test_sync_session_request_is_blocked_and_names_the_test():
    with pytest.raises(guard.CurlCffiNetworkBlocked, match="BBCA.JK"):
        curl_requests.Session().get(URL)
    attempts = guard.take_attempts()
    assert len(attempts) == 1
    assert "test_sync_session_request_is_blocked_and_names_the_test" in attempts[0]
    assert URL in attempts[0]


def test_module_level_get_is_blocked():
    with pytest.raises(guard.CurlCffiNetworkBlocked):
        curl_requests.get(URL)
    assert len(guard.take_attempts()) == 1


def test_async_session_request_is_blocked():
    # Driven by hand rather than asyncio.run: under --disable-socket the event
    # loop cannot create its self-pipe socketpair. The guard raises on the first
    # step, before anything is awaited, so no loop is needed.
    coro = curl_requests.AsyncSession.request(object(), "GET", URL)
    with pytest.raises(guard.CurlCffiNetworkBlocked):
        coro.send(None)
    assert len(guard.take_attempts()) == 1


def test_raw_curl_perform_is_blocked():
    from curl_cffi import Curl

    with pytest.raises(guard.CurlCffiNetworkBlocked):
        Curl().perform()
    assert len(guard.take_attempts()) == 1


def test_swallowed_attempt_is_still_recorded():
    # yfinance catches broad exceptions and returns an empty frame. The guard must
    # still remember the attempt so the conftest teardown check can fail the test.
    try:
        curl_requests.Session().get(URL)
    except Exception:  # noqa: BLE001 - imitating the library's swallow on purpose
        pass
    assert len(guard.take_attempts()) == 1


def test_yfinance_history_cannot_reach_yahoo():
    yf = pytest.importorskip("yfinance")
    try:
        yf.Ticker("BBCA.JK").history(period="5d", raise_errors=True)
    except Exception:  # noqa: BLE001 - whatever yfinance turns the block into
        pass
    attempts = guard.take_attempts()
    assert attempts, "yfinance reached Yahoo without going through the guarded curl_cffi entry points"
    assert all("yahoo" in a for a in attempts)


def _sentinel_original():
    sentinel = object()
    calls = []

    def original(*args, **kwargs):
        calls.append(kwargs.get("url"))
        return sentinel

    return guard._wrap("Session.request", original, is_async=False), sentinel, calls


@pytest.mark.allow_curl_cffi_network
def test_allow_marker_passes_through_to_the_original():
    # A stand-in original keeps this off the network while exercising the real
    # marker -> conftest -> set_allowed path.
    wrapped, sentinel, calls = _sentinel_original()
    assert wrapped(object(), method="GET", url=URL) is sentinel
    assert calls == [URL]
    assert guard.take_attempts() == []


def test_without_the_marker_the_original_is_never_called():
    wrapped, _, calls = _sentinel_original()
    with pytest.raises(guard.CurlCffiNetworkBlocked):
        wrapped(object(), method="GET", url=URL)
    assert calls == []
    assert len(guard.take_attempts()) == 1
