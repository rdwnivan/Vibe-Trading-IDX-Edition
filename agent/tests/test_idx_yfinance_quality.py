"""Synthetic provider defects; no exchange observations or implied event labels."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from backtest.loaders import yfinance_loader as yfl
from backtest.loaders.base import NoAvailableSourceError, loader_cache_put
from src.api.idx_research_routes import register_idx_research_routes
from src.market_data import fetch_market_data
from src.tools import idx_research_tool


def only_yfinance(source):
    if source != "yfinance":
        raise NoAvailableSourceError("Only the synthetic yfinance source is configured")
    return yfl.DataLoader


@pytest.fixture
def raw_bars(monkeypatch):
    raw = pd.DataFrame(
        {
            "Open": [100.0] * 3,
            "High": [110.0] * 3,
            "Low": [90.0] * 3,
            "Close": [105.0] * 3,
            "Volume": [1000.0, 0.0, float("nan")],
        },
        index=pd.date_range("2026-09-01", periods=3),
    )
    monkeypatch.setattr(yfl.yf, "download", lambda *args, **kwargs: raw)

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfl.yf, "Ticker", Ticker)
    return raw


@pytest.mark.parametrize(
    ("column", "value"),
    [("High", 80.0), ("Low", 120.0), ("Open", 120.0), ("Close", 80.0), ("Low", 0.0), ("Low", -1.0)],
)
def test_idx_fetch_rejects_structural_defect_instead_of_dropping_bar(raw_bars, column, value):
    raw_bars.loc[raw_bars.index[0], column] = value
    before = raw_bars.copy(deep=True)
    with pytest.raises(ValueError, match="OHLC"):
        yfl.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(raw_bars, before)


def test_non_idx_fetch_keeps_existing_drop_policy(raw_bars):
    raw_bars.loc[raw_bars.index[0], "High"] = 80.0
    frame = yfl.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-03")["AAPL.US"]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-02"), pd.Timestamp("2026-09-03")]
    assert frame["volume"].tolist() == [0.0, 0.0]


def test_valid_idx_fetch_preserves_all_bars_and_missing_volume(raw_bars):
    frame = yfl.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame.index.equals(raw_bars.index)
    assert frame["close"].tolist() == [105.0, 105.0, 105.0]
    assert frame.iloc[1]["volume"] == 0.0
    assert pd.isna(frame.iloc[2]["volume"])
    assert frame.attrs["source"] == "yfinance"
    assert frame.attrs["quote_currency"] == "IDR"


def test_shared_data_reports_structural_defect_as_fetch_failure(raw_bars):
    raw_bars.loc[raw_bars.index[0], "High"] = 80.0
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="yfinance",
        loader_resolver=only_yfinance,
        include_provenance=True,
    )
    assert "BBCA.JK" not in result
    assert result["_diagnostics"]["BBCA.JK"]["attempts"][0] == {
        "source": "yfinance",
        "reason": "fetch_failed",
    }


def test_idx_fetch_does_not_reuse_cache_created_by_drop_policy(raw_bars, monkeypatch, tmp_path):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    legacy = yfl._normalize_frame(raw_bars.iloc[1:], "1D", idx=True)
    loader_cache_put(
        source="yfinance",
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-03",
        fields=None,
        frame=legacy,
    )
    raw_bars.loc[raw_bars.index[0], "High"] = 80.0
    with pytest.raises(ValueError, match="OHLC"):
        yfl.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_valid_idx_cache_roundtrip_preserves_metadata_without_downloading(raw_bars, monkeypatch, tmp_path):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    original = yfl.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]

    def unexpected_download(*args, **kwargs):
        pytest.fail("validated IDX cache should avoid provider access")

    monkeypatch.setattr(yfl.yf, "download", unexpected_download)
    cached = yfl.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    # Parquet preserves session dates, not pandas' inferred frequency hint.
    pd.testing.assert_frame_equal(cached, original, check_freq=False)
    assert cached.attrs == original.attrs


def test_non_idx_fetch_still_uses_existing_cache_identity(raw_bars, monkeypatch, tmp_path):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    legacy = yfl._normalize_frame(raw_bars, "1D")
    loader_cache_put(
        source="yfinance",
        symbol="AAPL",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-03",
        fields=None,
        frame=legacy,
    )

    def unexpected_download(*args, **kwargs):
        pytest.fail("non-IDX legacy cache remains valid")

    monkeypatch.setattr(yfl.yf, "download", unexpected_download)
    frame = yfl.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-03")["AAPL.US"]
    pd.testing.assert_frame_equal(frame, legacy, check_freq=False)


def test_http_research_exposes_rejected_provider_series(raw_bars, monkeypatch):
    raw_bars.loc[raw_bars.index[0], "High"] = 80.0
    monkeypatch.setattr(
        idx_research_tool,
        "fetch_market_data",
        lambda **kwargs: fetch_market_data(**kwargs, loader_resolver=only_yfinance),
    )

    async def authorized_fixture():
        pass

    app = FastAPI()
    register_idx_research_routes(app, authorized_fixture)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK"], "lookback": 20, "end_date": "2026-09-03"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["backtest_enabled"] is False
    item = body["items"][0]
    assert item["reason"] == "no_data_or_source_failure"
    assert "bars" not in item
    assert {"source": "yfinance", "reason": "fetch_failed"} in item["diagnostics"]["attempts"]
