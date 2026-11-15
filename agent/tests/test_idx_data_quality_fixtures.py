"""Shareable synthetic DATA-03 fixture pack, driven by its manifest.

Every bar, date, calendar and record in ``fixtures/idx_data_quality`` is
synthetic (year 2030). Nothing comes from a vendor or from BEI, so the pack can
be shared; the calendar is a fixture, not an IDX calendar.

Network provider cases replace the HTTP layer beneath each provider, not the
loader: ``yahoo_client.throttled_get_json`` for Yahoo and
``yfinance.data.YfData.get``/``cache_get`` for yfinance, so the real yfinance
library decides what a failed or empty response looks like. Responses are
synthetic Yahoo v8 chart payloads; no request leaves the process.
"""

from datetime import date
import json
from pathlib import Path

import pandas as pd
import pytest
import requests
import yfinance
from yfinance import cache as yf_cache
from yfinance import data as yf_data

from backtest.loaders import local_loader, yahoo_client, yahoo_loader, yfinance_loader
from backtest.loaders.base import NoAvailableSourceError
from src.market_data import fetch_market_data
from src.markets.idx_bar_quality import (
    IDXCorporateAction,
    IDXDelisting,
    IDXSuspension,
    audit_daily_bars,
    audit_series_events,
)
from src.markets.idx_rules import IDXSessionCalendar

PACK = Path(__file__).parent / "fixtures" / "idx_data_quality"
MANIFEST = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
REQUIRED_CATEGORIES = {
    "normal",
    "missing_bar",
    "zero_volume",
    "split",
    "dividend",
    "suspension",
    "delisting",
    "stale",
    "provider_failure",
}


def _day(value):
    return date.fromisoformat(value)


def _calendar():
    spec = MANIFEST["calendar"]
    return IDXSessionCalendar(
        source=spec["source"],
        covered_from=_day(spec["covered_from"]),
        covered_until=_day(spec["covered_until"]),
        sessions=frozenset(_day(day) for day in spec["sessions"]),
    )


def _records():
    spec = MANIFEST["records"]
    suspensions = tuple(
        IDXSuspension(
            symbol=item["symbol"],
            source=item["source"],
            first_day=_day(item["first_day"]),
            last_day=_day(item["last_day"]),
        )
        for item in spec["suspensions"]
    )
    delistings = tuple(
        IDXDelisting(symbol=item["symbol"], source=item["source"], effective_day=_day(item["effective_day"]))
        for item in spec["delistings"]
    )
    actions = tuple(
        IDXCorporateAction(symbol=item["symbol"], source=item["source"], kind=item["kind"], ex_day=_day(item["ex_day"]))
        for item in spec["corporate_actions"]
    )
    return suspensions, delistings, actions


def _read_bars(name):
    frame = pd.read_csv(PACK / name, parse_dates=["date"]).set_index("date")
    frame.index = pd.DatetimeIndex(frame.index, name=None)
    return frame


BAR_CASES = MANIFEST["bar_cases"]
PROVIDER_CASES = MANIFEST["provider_cases"]
NETWORK_CASES = MANIFEST.get("network_provider_cases", [])


def test_pack_declares_itself_synthetic_and_covers_every_data03_category():
    assert MANIFEST["synthetic"] is True
    assert "synthetic" in (PACK / "README.md").read_text(encoding="utf-8").lower()
    categories = {case["category"] for case in BAR_CASES + PROVIDER_CASES}
    assert REQUIRED_CATEGORIES <= categories


def test_every_pack_file_is_referenced_and_every_reference_exists():
    referenced = {case["file"] for case in BAR_CASES + PROVIDER_CASES}
    referenced |= {
        response["file"]
        for case in NETWORK_CASES
        for response in case["responses"].values()
        if response["kind"] == "bars"
    }
    on_disk = {path.name for path in PACK.glob("*.csv")}
    assert referenced == on_disk


def test_every_record_and_case_symbol_is_a_synthetic_idx_code():
    symbols = {case["symbol"] for case in BAR_CASES + PROVIDER_CASES + NETWORK_CASES}
    for group in MANIFEST["records"].values():
        symbols |= {item["symbol"] for item in group}
    assert all(symbol.startswith("SYN") and symbol.endswith(".JK") for symbol in symbols)


@pytest.mark.parametrize("case", BAR_CASES, ids=[case["id"] for case in BAR_CASES])
def test_bar_case_findings_match_the_manifest(case):
    frame = _read_bars(case["file"])
    before = frame.copy(deep=True)
    calendar = _calendar()
    suspensions, delistings, actions = _records()

    daily = audit_daily_bars(case["symbol"], frame, calendar=calendar, suspensions=suspensions)
    events = audit_series_events(
        case["symbol"],
        frame,
        as_of=_day(case["as_of"]),
        calendar=calendar,
        suspensions=suspensions,
        delistings=delistings,
        corporate_actions=actions,
    )

    for key, value in case["expect"].get("daily_bar_audit", {}).items():
        assert daily[key] == value, key
    for key, value in case["expect"].get("series_event_audit", {}).items():
        assert events[key] == value, key
    json.dumps([daily, events], allow_nan=False)
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("case", PROVIDER_CASES, ids=[case["id"] for case in PROVIDER_CASES])
def test_provider_case_is_reported_as_the_manifest_reason(case, monkeypatch):
    entry = {"symbol": case["symbol"], "type": "csv", "path": str(PACK / case["file"])}
    monkeypatch.setattr(local_loader, "_load_config", lambda: {"sources": [entry]})

    def resolver(source):
        assert source == "local", "explicit local must never attempt a network fallback"
        return local_loader.DataLoader

    result = fetch_market_data(
        codes=[case["symbol"]],
        start_date=case["start"],
        end_date=case["end"],
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )

    assert result["_diagnostics"][case["symbol"]]["attempts"] == [{"source": "local", "reason": case["reason"]}]
    assert case["symbol"] not in {key for key in result if not key.startswith("_")}


def test_network_cases_cover_failure_and_empty_for_yahoo_and_yfinance():
    explicit = {(case["source"], case["expect"]["attempts"][0]["reason"]) for case in NETWORK_CASES if case["source"]}
    assert {
        ("yahoo", "fetch_failed"),
        ("yahoo", "no_data"),
        ("yfinance", "fetch_failed"),
        ("yfinance", "no_data"),
    } <= explicit
    assert any(case["source"] is None for case in NETWORK_CASES), "the default yahoo -> yfinance chain is covered"


def _chart_payload(symbol, response):
    """A synthetic Yahoo v8 chart payload: empty, or the bars of a pack CSV at 09:00 WIB."""
    meta = {
        "currency": "IDR",
        "symbol": symbol,
        "exchangeName": "JKT",
        "instrumentType": "EQUITY",
        "exchangeTimezoneName": "Asia/Jakarta",
        "timezone": "WIB",
        "gmtoffset": 25200,
        "dataGranularity": "1d",
        "regularMarketPrice": 1000.0,
    }
    result = {"meta": meta, "indicators": {"quote": [{}], "adjclose": [{}]}}
    if response["kind"] == "bars":
        frame = _read_bars(response["file"])
        stamps = frame.index.tz_localize("Asia/Jakarta") + pd.Timedelta(hours=9)
        result["timestamp"] = [int(stamp.timestamp()) for stamp in stamps]
        result["indicators"] = {
            "quote": [{column: frame[column].tolist() for column in ("open", "high", "low", "close", "volume")}],
            "adjclose": [{"adjclose": frame["close"].tolist()}],
        }
    return {"chart": {"result": [result], "error": None}}


def _http_failure(response):
    if response["kind"] == "connection_error":
        return requests.exceptions.ConnectionError("synthetic connection refused")
    failed = requests.models.Response()
    failed.status_code = response["status"]
    return requests.exceptions.HTTPError(f"synthetic HTTP {response['status']}", response=failed)


class _NullTzCache:
    """Keep yfinance's timezone cache off the operator's cache directory."""

    dummy = True

    def lookup(self, _key):
        return None

    def store(self, _key, _value):
        return None


@pytest.fixture
def network_responses(monkeypatch):
    """Install per-provider synthetic HTTP responses; return the setter."""
    monkeypatch.setattr(yf_cache, "get_tz_cache", lambda: _NullTzCache())
    monkeypatch.setattr(yahoo_client, "_min_interval", lambda: 0.0)

    def install(symbol, responses):
        yahoo = responses.get("yahoo")
        yf = responses.get("yfinance")

        def yahoo_get_json(url, **_kwargs):
            assert yahoo is not None, "yahoo was not expected to be called"
            if yahoo["kind"] in ("connection_error", "http_status"):
                raise _http_failure(yahoo)
            return _chart_payload(symbol, yahoo)

        def yfinance_get(self, url, params=None, timeout=30, **_kwargs):
            assert yf is not None, "yfinance was not expected to be called"
            if yf["kind"] in ("connection_error", "http_status"):
                raise _http_failure(yf)
            reply = requests.models.Response()
            reply.status_code = 200
            # Like Yahoo, only the dated daily request carries bars; the 5-day
            # hourly metadata request yfinance makes for the currency gets meta only.
            dated_daily = (params or {}).get("interval") == "1d" and "period1" in (params or {})
            reply._content = json.dumps(_chart_payload(symbol, yf if dated_daily else {"kind": "empty_chart"})).encode()
            reply.headers["Content-Type"] = "application/json"
            reply.url = url
            return reply

        monkeypatch.setattr(yahoo_client, "throttled_get_json", yahoo_get_json)
        monkeypatch.setattr(yf_data.YfData, "get", yfinance_get)
        monkeypatch.setattr(yf_data.YfData, "cache_get", yfinance_get)

    return install


def _network_resolver(case):
    """Resolve only the providers the case gives a response; the rest of the chain is unavailable."""
    loaders = {"yahoo": yahoo_loader.DataLoader, "yfinance": yfinance_loader.DataLoader}

    def resolve(source):
        if source not in case["responses"]:
            raise NoAvailableSourceError(f"{source} is not part of this network case")
        return loaders[source]

    return resolve


def _provider_attempts(attempts):
    return [attempt for attempt in attempts if attempt["reason"] != "source_unavailable"]


@pytest.mark.parametrize("case", NETWORK_CASES, ids=[case["id"] for case in NETWORK_CASES])
def test_network_provider_case_is_reported_as_the_manifest_expects(case, network_responses):
    network_responses(case["symbol"], case["responses"])

    result = fetch_market_data(
        codes=[case["symbol"]],
        start_date=case["start"],
        end_date=case["end"],
        source=case["source"] or "auto",
        include_provenance=True,
        loader_resolver=_network_resolver(case),
    )

    expect = case["expect"]
    if expect["served_by"] is None:
        assert _provider_attempts(result["_diagnostics"][case["symbol"]]["attempts"]) == expect["attempts"]
        assert case["symbol"] not in {key for key in result if not key.startswith("_")}
    else:
        provenance = result["_provenance"][case["symbol"]]
        assert provenance["source"] == expect["served_by"]
        assert _provider_attempts(provenance["attempts"]) == expect["attempts"]
        assert len(result[case["symbol"]]) == len(_read_bars(case["responses"][expect["served_by"]]["file"]))


def test_yfinance_is_the_real_library_under_the_network_cases():
    assert yfinance_loader.yf is yfinance
