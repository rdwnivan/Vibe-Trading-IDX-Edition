"""Zero-volume price-change findings on the personal research surface.

Synthetic observations only; 999999.9999 imitates a vendor placeholder price.
"""

import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from src.api.idx_research_routes import register_idx_research_routes
from src.tools import idx_research_tool

SENTINEL = 999999.9999


@pytest.fixture
def observation(monkeypatch):
    frame = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000.0},
        index=pd.date_range("2026-09-01", periods=21),
    )
    provenance = {
        "source": "yahoo",
        "quote_currency": "IDR",
        "exchange_timezone": "Asia/Jakarta",
        "interval": "1D",
        "volume_unit": "shares",
        "adjustment": "unknown",
        "freshness": "not_evaluated",
    }
    data = {"BBCA.JK": frame, "_provenance": {"BBCA.JK": provenance}}
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: data)
    return data, frame, provenance


def research():
    return json.loads(
        idx_research_tool.IDXResearchTool().execute(codes=["BBCA.JK"], lookback=20, end_date="2026-10-01")
    )


def placeholder(frame, position):
    frame.iloc[position, frame.columns.get_indexer(["open", "high", "low", "close"])] = SENTINEL
    frame.iloc[position, frame.columns.get_loc("volume")] = 0.0


def test_clean_observation_reports_no_price_change_and_no_calendar_check(observation):
    item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["bar_audit"] == {
        "policy": "idx_daily_bar_audit_v1",
        "calendar_verified": False,
        "zero_volume_price_change_dates": [],
    }


def test_placeholder_rows_are_reported_but_the_observation_is_kept(observation, caplog):
    _, frame, _ = observation
    placeholder(frame, 10)
    placeholder(frame, 11)
    original = frame.copy(deep=True)

    with caplog.at_level(logging.WARNING):
        item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["bar_audit"]["zero_volume_price_change_dates"] == ["2026-09-11", "2026-09-12"]
    # Reported, never repaired: the bars and indicators still carry the value.
    assert [bar["close"] for bar in item["bars"] if bar["date"] == "2026-09-11"] == [SENTINEL]
    pd.testing.assert_frame_equal(frame, original)
    assert "BBCA.JK zero-volume price change on 2 bars" in caplog.text
    assert str(SENTINEL) not in caplog.text


def test_flat_zero_volume_row_repeating_the_close_is_not_a_price_change(observation):
    _, frame, _ = observation
    frame.iloc[10, frame.columns.get_indexer(["open", "high", "low", "close"])] = 105.0
    frame.iloc[10, frame.columns.get_loc("volume")] = 0.0

    item = research()["items"][0]

    assert item["bar_audit"]["zero_volume_price_change_dates"] == []
    assert item["volume_coverage"]["zero_bar_count"] == 1


def test_placeholders_before_any_traded_bar_are_not_judged(observation):
    _, frame, _ = observation
    # Bar 0 falls outside lookback=20; bar 1 is the first analyzed bar. With no
    # traded bar before either, there is no close to compare against.
    placeholder(frame, 0)
    placeholder(frame, 1)

    item = research()["items"][0]

    assert item["bars"][0]["date"] == "2026-09-02"
    assert item["bar_audit"]["zero_volume_price_change_dates"] == []


def test_findings_outside_the_analyzed_window_are_not_reported(observation):
    data, frame, _ = observation
    longer = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000.0},
        index=pd.date_range("2026-09-01", periods=25),
    )
    placeholder(longer, 2)  # 2026-09-03, before the 20-bar window
    placeholder(longer, 10)  # 2026-09-11, inside it
    data["BBCA.JK"] = longer

    item = research()["items"][0]

    assert item["bars"][0]["date"] == "2026-09-06"
    assert item["bar_audit"]["zero_volume_price_change_dates"] == ["2026-09-11"]


def test_window_start_placeholder_is_judged_against_a_traded_bar_outside_the_window(observation):
    _, frame, _ = observation
    placeholder(frame, 1)

    item = research()["items"][0]

    assert item["bar_audit"]["zero_volume_price_change_dates"] == ["2026-09-02"]


def test_missing_volume_is_not_a_zero_volume_finding(observation):
    _, frame, _ = observation
    frame.iloc[10, frame.columns.get_indexer(["open", "high", "low", "close"])] = SENTINEL
    frame.iloc[10, frame.columns.get_loc("volume")] = float("nan")

    item = research()["items"][0]

    assert item["bar_audit"]["zero_volume_price_change_dates"] == []


def test_rejected_and_unavailable_symbols_carry_no_bar_audit(observation):
    data, frame, provenance = observation
    provenance["quote_currency"] = "USD"
    data["BBRI.JK"] = None

    result = json.loads(
        idx_research_tool.IDXResearchTool().execute(codes=["BBCA.JK", "BBRI.JK"], lookback=20, end_date="2026-10-01")
    )

    assert all("bar_audit" not in item for item in result["items"])


def test_http_route_returns_the_same_finding(observation):
    data, frame, provenance = observation
    placeholder(frame, 15)
    data["BBRI.JK"] = frame.copy(deep=True).assign(volume=1000.0, close=105.0, open=100.0, high=110.0, low=90.0)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["bar_audit"]["zero_volume_price_change_dates"] == ["2026-09-16"]
    assert items[1]["bar_audit"]["zero_volume_price_change_dates"] == []
