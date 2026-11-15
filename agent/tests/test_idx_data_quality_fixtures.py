"""Shareable synthetic DATA-03 fixture pack, driven by its manifest.

Every bar, date, calendar and record in ``fixtures/idx_data_quality`` is
synthetic (year 2030). Nothing comes from a vendor or from BEI, so the pack can
be shared; the calendar is a fixture, not an IDX calendar.
"""

from datetime import date
import json
from pathlib import Path

import pandas as pd
import pytest

from backtest.loaders import local_loader
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


def test_pack_declares_itself_synthetic_and_covers_every_data03_category():
    assert MANIFEST["synthetic"] is True
    assert "synthetic" in (PACK / "README.md").read_text(encoding="utf-8").lower()
    categories = {case["category"] for case in BAR_CASES + PROVIDER_CASES}
    assert REQUIRED_CATEGORIES <= categories


def test_every_pack_file_is_referenced_and_every_reference_exists():
    referenced = {case["file"] for case in BAR_CASES + PROVIDER_CASES}
    on_disk = {path.name for path in PACK.glob("*.csv")}
    assert referenced == on_disk


def test_every_record_and_case_symbol_is_a_synthetic_idx_code():
    symbols = {case["symbol"] for case in BAR_CASES + PROVIDER_CASES}
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
