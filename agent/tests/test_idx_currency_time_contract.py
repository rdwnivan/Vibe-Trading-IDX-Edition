"""IDX-02 contract: IDR isolation in baskets and Jakarta session-date boundaries.

All market observations below are synthetic.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from backtest.loaders.yahoo_loader import DataLoader as YahooLoader
from src.tools.portfolio_risk_tool import PortfolioRiskXrayTool

# 17:00 UTC is midnight in Jakarta (UTC+7, no DST). One second earlier is still
# the previous Jakarta session date.
_LAST_SECOND_OF_NOV_2 = "2026-11-02T16:59:59Z"
_FIRST_SECOND_OF_NOV_3 = "2026-11-02T17:00:00Z"


def _records(seed: int, periods: int = 80) -> list[dict]:
    rng = np.random.default_rng(seed)
    closes = 1000 * np.cumprod(1 + rng.normal(0, 0.01, periods))
    dates = pd.date_range("2026-01-01", periods=periods, freq="B")
    return [{"date": d.date().isoformat(), "close": float(c)} for d, c in zip(dates, closes)]


def _run_risk(symbols: list[str]) -> tuple[dict, list[dict]]:
    calls: list[dict] = []

    def fetch(**kwargs):
        calls.append(kwargs)
        return {sym: _records(i) for i, sym in enumerate(kwargs["codes"])}

    raw = PortfolioRiskXrayTool(data_fetcher=fetch).execute(
        symbols=symbols, start_date="2026-01-01", end_date="2026-06-01"
    )
    return json.loads(raw), calls


@pytest.mark.parametrize(
    "symbols,other",
    [
        (["BBCA.JK", "AAPL"], "USD"),
        (["BBRI.JK", "600519.SH"], "CNY"),
        (["0700.HK", "BBCA.JK"], "HKD"),
    ],
)
def test_risk_xray_refuses_to_blend_idr_with_another_currency(symbols, other):
    result, calls = _run_risk(symbols)

    assert result["status"] == "error"
    assert "IDR" in result["error"] and other in result["error"]
    assert calls == [], "prices must not be fetched for a basket that cannot be priced in one currency"


def test_risk_xray_refuses_idr_with_an_unclassifiable_member():
    result, calls = _run_risk(["BBCA.JK", "BBCA-W.JK"])

    assert result["status"] == "error"
    assert calls == []


def test_risk_xray_accepts_an_idr_only_basket():
    result, calls = _run_risk(["BBCA.JK", "BBRI.JK"])

    assert result["status"] == "ok", result
    assert calls[0]["codes"] == ["BBCA.JK", "BBRI.JK"]


def test_risk_xray_keeps_existing_mixed_baskets_without_idr():
    # Pre-IDX behavior for other markets is preserved; the guard is IDX-scoped.
    result, _ = _run_risk(["AAPL", "0700.HK"])

    assert result["status"] == "ok", result


def _yahoo_payload(*timestamps: str) -> list[dict]:
    return [
        {
            "trade_date": int(pd.Timestamp(ts).timestamp()),
            "open": 100 + i,
            "high": 110 + i,
            "low": 90 + i,
            "close": 105 + i,
            "volume": 1_000 + i,
        }
        for i, ts in enumerate(timestamps)
    ]


def test_yahoo_idx_session_date_flips_exactly_at_jakarta_midnight(monkeypatch):
    import backtest.loaders.yahoo_loader as yahoo

    payload = _yahoo_payload(_LAST_SECOND_OF_NOV_2, _FIRST_SECOND_OF_NOV_3)
    monkeypatch.setattr(yahoo.yahoo_client, "get_chart", lambda *a, **k: (payload, "IDR"))

    frame = YahooLoader().fetch(["BBCA.JK"], "2026-11-02", "2026-11-03")["BBCA.JK"]

    assert list(frame.index) == [pd.Timestamp("2026-11-02"), pd.Timestamp("2026-11-03")]
    assert list(frame["volume"]) == [1_000, 1_001]
    assert frame.attrs["exchange_timezone"] == "Asia/Jakarta"
    assert frame.attrs["volume_unit"] == "shares"


def test_yahoo_non_idx_daily_dates_stay_on_utc(monkeypatch):
    # Control: the Jakarta conversion must not leak into other markets.
    import backtest.loaders.yahoo_loader as yahoo

    payload = _yahoo_payload(_FIRST_SECOND_OF_NOV_3)
    monkeypatch.setattr(yahoo.yahoo_client, "get_chart", lambda *a, **k: (payload, "USD"))

    frame = YahooLoader().fetch(["AAPL.US"], "2026-11-02", "2026-11-03")["AAPL.US"]

    assert list(frame.index) == [pd.Timestamp("2026-11-02")]


def test_yfinance_idx_session_date_flips_exactly_at_jakarta_midnight(monkeypatch):
    import backtest.loaders.yfinance_loader as yfl

    raw = pd.DataFrame(
        {
            "Open": [100, 101],
            "High": [110, 111],
            "Low": [90, 91],
            "Close": [105, 106],
            "Volume": [1_000, 1_001],
        },
        index=pd.DatetimeIndex([_LAST_SECOND_OF_NOV_2, _FIRST_SECOND_OF_NOV_3]),
    )

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfl.yf, "download", lambda *a, **k: raw)
    monkeypatch.setattr(yfl.yf, "Ticker", Ticker)

    frame = yfl.DataLoader().fetch(["BBCA.JK"], "2026-11-02", "2026-11-03")["BBCA.JK"]

    assert list(frame.index) == [pd.Timestamp("2026-11-02"), pd.Timestamp("2026-11-03")]
    assert list(frame["volume"]) == [1_000, 1_001]
    assert frame.attrs["quote_currency"] == "IDR"
    assert frame.attrs["volume_unit"] == "shares"
