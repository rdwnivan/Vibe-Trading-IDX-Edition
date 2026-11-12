"""Raw synthetic volume contracts at the Yahoo/yfinance acquisition boundary."""

from decimal import Decimal
import json

import numpy as np
import pandas as pd
import pytest

from backtest.loaders import local_loader, yahoo_client, yahoo_loader, yfinance_loader
from backtest.loaders.base import NoAvailableSourceError, loader_cache_get, loader_cache_put
from src.market_data import fetch_market_data
from src.tools.idx_research_tool import IDXResearchTool


@pytest.fixture
def raw_bars():
    return pd.DataFrame(
        {"Open": 100.0, "High": 110.0, "Low": 90.0, "Close": 105.0, "Volume": 1000.0},
        index=pd.date_range("2026-09-01", periods=21),
    )


def chart_payload(frame):
    return {
        "chart": {
            "error": None,
            "result": [
                {
                    "meta": {"currency": "IDR"},
                    "timestamp": [int(day.timestamp()) for day in frame.index],
                    "indicators": {"quote": [{key.lower(): frame[key].tolist() for key in frame}]},
                }
            ],
        }
    }


@pytest.fixture(params=["yahoo", "yfinance"])
def transport(request, monkeypatch, raw_bars):
    monkeypatch.setattr(yahoo_client, "throttled_get_json", lambda *a, **k: chart_payload(raw_bars))
    monkeypatch.setattr(yfinance_loader.yf, "download", lambda *a, **k: raw_bars)

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfinance_loader.yf, "Ticker", Ticker)
    loaders = {"yahoo": yahoo_loader.DataLoader, "yfinance": yfinance_loader.DataLoader}
    return request.param, loaders[request.param]


@pytest.mark.parametrize(
    "value",
    [
        "not-volume",
        "",
        "NaN",
        "Infinity",
        "1e9999",
        -1,
        float("inf"),
        -float("inf"),
        True,
        np.bool_(False),
        1 + 0j,
        np.complex64(1 + 2j),
        complex(float("nan"), 0),
        10**400,
        Decimal("1e9999"),
    ],
    ids=[
        "text",
        "empty-text",
        "nan-text",
        "inf-text",
        "overflow-text",
        "negative",
        "inf",
        "negative-inf",
        "bool",
        "numpy-bool",
        "complex-real",
        "numpy-complex",
        "complex-nan",
        "huge-int",
        "decimal-overflow",
    ],
)
def test_idx_rejects_invalid_raw_volume_without_mutating_input(transport, raw_bars, value):
    raw_bars["Volume"] = raw_bars["Volume"].astype(object)
    raw_bars.at[raw_bars.index[0], "Volume"] = value
    before = raw_bars.copy(deep=True)
    _, loader = transport
    with pytest.raises(ValueError, match="volume"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")
    pd.testing.assert_frame_equal(raw_bars, before)


@pytest.mark.parametrize("missing", [None, float("nan"), pd.NA])
def test_idx_preserves_missing_volume_and_observed_zero(transport, raw_bars, missing):
    raw_bars["Volume"] = raw_bars["Volume"].astype(object)
    raw_bars.at[raw_bars.index[0], "Volume"] = missing
    raw_bars.at[raw_bars.index[1], "Volume"] = 0
    _, loader = transport
    frame = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame.iloc[1]["volume"] == 0
    assert frame.iloc[2]["volume"] == 1000
    assert len(frame) == 21
    assert frame.attrs["data_quality"] == "incomplete"


def test_idx_accepts_numeric_volume_strings(transport, raw_bars):
    raw_bars["Volume"] = "1000"
    _, loader = transport
    frame = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    assert frame["volume"].tolist() == [1000.0] * 21


def test_complex_nan_volume_cannot_hide_as_an_absent_slot(transport, raw_bars):
    raw_bars["Volume"] = raw_bars["Volume"].astype(object)
    raw_bars.loc[raw_bars.index[0], ["Open", "High", "Low", "Close"]] = None
    raw_bars.at[raw_bars.index[0], "Volume"] = complex(float("nan"), 0)
    _, loader = transport
    with pytest.raises(ValueError):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")


def test_idx_missing_volume_field_stays_missing(transport, raw_bars):
    raw_bars.drop(columns="Volume", inplace=True)
    _, loader = transport
    frame = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    assert frame["volume"].isna().all()
    assert len(frame) == 21


def test_non_idx_retains_existing_invalid_volume_coercion(transport, raw_bars):
    raw_bars["Volume"] = "not-volume"
    _, loader = transport
    frame = loader().fetch(["AAPL.US"], "2026-09-01", "2026-09-21")["AAPL.US"]
    assert frame["volume"].tolist() == [0.0] * 21


def test_idx_reacquires_instead_of_using_cache_that_lost_invalid_volume(transport, raw_bars, monkeypatch, tmp_path):
    source, loader = transport
    legacy = raw_bars.rename(columns=str.lower)
    legacy["volume"] = float("nan")
    legacy.index.name = "trade_date"
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    cache_args = dict(source=source, symbol="BBCA.JK", timeframe="1D", start_date="2026-09-01", end_date="2026-09-21")
    loader_cache_put(**cache_args, fields=["idx_complete_ohlc_v2"], frame=legacy)
    raw_bars["Volume"] = "not-volume"
    with pytest.raises(ValueError, match="volume"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")
    assert loader_cache_get(**cache_args, fields=["idx_complete_ohlc_v2"]) is not None


def test_current_cache_retains_null_zero_and_metadata(transport, raw_bars, monkeypatch, tmp_path):
    _, loader = transport
    raw_bars.loc[raw_bars.index[0], "Volume"] = float("nan")
    raw_bars.loc[raw_bars.index[1], "Volume"] = 0
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    first = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    raw_bars["Volume"] = "not-volume"
    cached = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    pd.testing.assert_frame_equal(cached, first, check_freq=False)
    assert cached.attrs == first.attrs


def test_invalid_volume_fallback_preserves_actual_source_and_failure(raw_bars, transport, monkeypatch):
    broken = raw_bars.copy()
    broken["Volume"] = "not-volume"
    monkeypatch.setattr(yahoo_client, "throttled_get_json", lambda *a, **k: chart_payload(broken))
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-09-01",
        end_date="2026-09-21",
        include_provenance=True,
        loader_resolver=lambda source: {"yahoo": yahoo_loader.DataLoader, "yfinance": yfinance_loader.DataLoader}[
            source
        ],
    )
    provenance = result["_provenance"]["BBCA.JK"]
    assert provenance["source"] == "yfinance"
    assert provenance["attempts"] == [{"source": "yahoo", "reason": "fetch_failed"}]
    assert provenance["quote_currency"] == "IDR"
    assert provenance["volume_unit"] == "shares"
    assert provenance["exchange_timezone"] == "Asia/Jakarta"
    assert provenance["interval"] == "1D"
    assert provenance["adjustment"] == "split_dividend"


def test_research_rejects_invalid_volume_while_preserving_healthy_peer(raw_bars, transport, monkeypatch):
    broken = raw_bars.copy()
    broken["Volume"] = "not-volume"

    def chart(url, **kwargs):
        return chart_payload(broken if url.endswith("BBCA.JK") else raw_bars)

    def download(tickers, **kwargs):
        return broken if "BBCA.JK" in tickers else raw_bars

    def resolver(source):
        if source not in ("yahoo", "yfinance"):
            raise NoAvailableSourceError("Synthetic transports only")
        return {"yahoo": yahoo_loader.DataLoader, "yfinance": yfinance_loader.DataLoader}[source]

    monkeypatch.setattr(yahoo_client, "throttled_get_json", chart)
    monkeypatch.setattr(yfinance_loader.yf, "download", download)
    monkeypatch.setattr(
        "src.tools.idx_research_tool.fetch_market_data",
        lambda **kwargs: fetch_market_data(**kwargs, loader_resolver=resolver),
    )
    result = json.loads(IDXResearchTool().execute(codes=["BBCA.JK", "BBRI.JK"], lookback=20, end_date="2026-09-21"))
    assert result["status"] == "partial"
    assert result["items"][0]["status"] == "unavailable"
    assert result["items"][0]["diagnostics"]["attempts"][:2] == [
        {"source": "yahoo", "reason": "fetch_failed"},
        {"source": "yfinance", "reason": "fetch_failed"},
    ]
    assert result["items"][1]["status"] == "ok"
    assert len(result["items"][1]["bars"]) == 20
    assert result["items"][1]["provenance"]["attempts"] == []
    assert result["backtest_enabled"] is False


def test_local_loader_declaration_does_not_supply_idx_metadata(monkeypatch, tmp_path):
    # Volume is now preserved as missing; IDX metadata acceptance remains separate.
    path = tmp_path / "synthetic.csv"
    path.write_text("date,open,high,low,close\n2026-09-01,100,110,90,105\n", encoding="utf-8")
    monkeypatch.setattr(local_loader, "_load_config", lambda: {"sources": [{"symbol": "BBCA.JK", "path": str(path)}]})
    assert "id_equity" in local_loader.DataLoader.markets
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-21")["BBCA.JK"]
    assert frame["volume"].isna().all()
    assert "quote_currency" not in frame.attrs
    assert "volume_unit" not in frame.attrs

    def resolver(source):
        if source != "local":
            raise NoAvailableSourceError("Only synthetic local data is configured")
        return local_loader.DataLoader

    monkeypatch.setattr(
        "src.tools.idx_research_tool.fetch_market_data",
        lambda **kwargs: fetch_market_data(**kwargs, loader_resolver=resolver),
    )
    result = json.loads(IDXResearchTool().execute(codes=["BBCA.JK"], lookback=20, end_date="2026-09-21"))
    assert result["items"][0]["status"] == "unavailable"
    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
