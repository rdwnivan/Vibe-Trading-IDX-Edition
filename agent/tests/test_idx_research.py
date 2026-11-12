"""Personal watchlist contracts; all observations are synthetic."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from backtest.loaders import yahoo_client
from backtest.loaders import yfinance_loader
from src.api.idx_research_routes import register_idx_research_routes
from src.tools.idx_research_tool import IDXResearchTool


@pytest.fixture
def chart(monkeypatch):
    calls = []

    def get_chart(code, **kwargs):
        calls.append(code)
        if code == "BBRI.JK":
            return [], "IDR"
        dates = pd.bdate_range("2026-08-03", periods=40)
        rows = [
            {
                "trade_date": int(stamp.tz_localize("Asia/Jakarta").timestamp()),
                "open": 100 + i,
                "high": 110 + i,
                "low": 90 + i,
                "close": 105 + i,
                "volume": None if i == 39 else 1000,
            }
            for i, stamp in enumerate(dates)
        ]
        return rows, "IDR"

    monkeypatch.setattr(yahoo_client, "get_chart", get_chart)
    # Stub the other vendor transport too; exercise real routing without network.
    monkeypatch.setattr(yfinance_loader.yf, "download", lambda *a, **k: pd.DataFrame())
    return calls


def run(**kwargs):
    return json.loads(
        IDXResearchTool().execute(**{"codes": ["BBCA.JK"], "lookback": 20, "end_date": "2026-10-01", **kwargs})
    )


def test_watchlist_chart_and_indicators_use_one_observation(chart):
    result = run()
    item = result["items"][0]
    assert chart == ["BBCA.JK"]
    assert result["status"] == "ok"
    assert len(item["bars"]) == item["analysis"]["read_identity"]["bar_count"] == 20
    assert item["bars"][-1]["close"] == item["analysis"]["latest_close"] == 144
    assert item["analysis"]["indicators"]["sma_20"] == 134.5
    assert item["analysis"]["indicators"]["sma_200"] is None
    assert item["analysis"]["indicators"]["macd"] is None
    assert item["bars"][-1]["volume"] is None
    assert item["analysis"]["indicators"]["volume"]["latest"] is None
    assert item["provenance"]["quote_currency"] == "IDR"
    assert item["provenance"]["source"] == "yahoo"
    assert item["provenance"]["adjustment"] == "unknown"
    assert result["calendar_completeness"] == "not_verified"
    assert result["backtest_enabled"] is False


def test_yfinance_adjusted_fallback_keeps_served_levels_and_provenance(chart, monkeypatch):
    def failed_chart(*args, **kwargs):
        raise ValueError("Synthetic Yahoo outage")

    # This is the already adjusted download result; no real corporate event.
    raw = pd.DataFrame(
        {"Open": 95.0, "High": 95.0, "Low": 95.0, "Close": 95.0, "Volume": 1000.0},
        index=pd.date_range("2026-09-01", periods=20),
    )
    raw.loc[raw.index[-10:], ["Open", "High", "Low", "Close"]] = 100.0

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    def download(*args, **kwargs):
        assert kwargs["auto_adjust"] is True
        return raw.copy(deep=True)

    monkeypatch.setattr(yahoo_client, "get_chart", failed_chart)
    monkeypatch.setattr(yfinance_loader.yf, "download", download)
    monkeypatch.setattr(yfinance_loader.yf, "Ticker", Ticker)

    result = run()

    item = result["items"][0]
    assert item["status"] == "ok"
    assert item["bars"][9]["close"] == 95.0
    assert item["bars"][10]["close"] == 100.0
    assert item["analysis"]["indicators"]["sma_20"] == 97.5
    assert item["provenance"]["source"] == "yfinance"
    assert item["provenance"]["adjustment"] == "split_dividend"
    assert item["provenance"]["fallback_used"] is True
    assert item["provenance"]["attempts"] == [{"source": "yahoo", "reason": "fetch_failed"}]


@pytest.mark.parametrize(
    "codes",
    [["BBCA"], ["AAPL.US"], ["BBCA-W.JK"], ["local:BBCA.JK"], ["BBCA.JK", "bbca.jk"], [], ["BBCA.JK"] * 9, [None]],
)
def test_invalid_watchlist_rejected_before_network(chart, codes):
    assert run(codes=codes)["ok"] is False
    assert chart == []


@pytest.mark.parametrize(
    "options",
    [
        {"lookback": True},
        {"lookback": 19},
        {"lookback": 501},
        {"end_date": "20261001"},
        {"end_date": "bad"},
        {"end_date": "0001-01-01"},
    ],
)
def test_invalid_window_rejected_before_network(chart, options):
    assert run(**options)["ok"] is False
    assert chart == []


def test_partial_watchlist_keeps_unavailable_symbol_visible(chart):
    result = run(codes=["BBCA.JK", "BBRI.JK"])
    assert result["status"] == "partial"
    assert [(item["symbol"], item["status"]) for item in result["items"]] == [
        ("BBCA.JK", "ok"),
        ("BBRI.JK", "unavailable"),
    ]
    assert "bars" not in result["items"][1]
    assert result["items"][1]["diagnostics"]["attempts"]


def test_wrong_currency_does_not_become_idr(chart, monkeypatch):
    monkeypatch.setattr(
        yahoo_client,
        "get_chart",
        lambda *a, **k: (
            [
                {
                    "trade_date": int(pd.Timestamp("2026-09-01T00:00Z").timestamp()),
                    "open": 100,
                    "high": 110,
                    "low": 90,
                    "close": 105,
                    "volume": 1000,
                }
            ],
            "USD",
        ),
    )
    result = run()
    assert result["status"] == "unavailable"
    assert "analysis" not in result["items"][0]


def test_route_requires_auth_before_acquisition(chart):
    app = FastAPI()

    async def denied():
        raise HTTPException(401, "Authentication required")

    register_idx_research_routes(app, denied)
    response = TestClient(app).post("/api/research/idx", json={"codes": ["BBCA.JK"]})
    assert response.status_code == 401
    assert chart == []


def test_route_and_tool_have_identical_results(chart):
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    client = TestClient(app)
    response = client.post("/api/research/idx", json={"codes": ["BBCA.JK"], "lookback": 20, "end_date": "2026-10-01"})
    assert response.status_code == 200
    assert response.json()["items"][0]["analysis"]["latest_close"] == 144
    assert client.post("/api/research/idx", json={"codes": ["BBCA"]}).status_code == 400
    assert client.post("/api/research/idx", json={"codes": ["BBCA.JK"], "lookback": True}).status_code == 422
