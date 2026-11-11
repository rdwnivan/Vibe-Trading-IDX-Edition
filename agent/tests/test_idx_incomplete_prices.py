"""Synthetic partial-price responses at the two Yahoo transport boundaries."""

import copy

import pandas as pd
import pytest

from backtest.loaders import yahoo_client, yahoo_loader, yfinance_loader
from backtest.loaders.base import NoAvailableSourceError, loader_cache_put
from src.market_data import fetch_market_data


@pytest.fixture
def raw_prices():
    return pd.DataFrame(
        {
            "Open": [100.0] * 3,
            "High": [110.0] * 3,
            "Low": [90.0] * 3,
            "Close": [105.0] * 3,
            "Volume": [1000.0, 0.0, float("nan")],
        },
        index=pd.date_range("2026-09-01", periods=3),
    )


@pytest.fixture(params=["yahoo", "yfinance"])
def transport(request, monkeypatch, raw_prices):
    source = request.param

    def fake_chart(*args, **kwargs):
        payload = {
            "chart": {
                "result": [
                    {
                        "meta": {"currency": "IDR"},
                        "timestamp": [int(day.timestamp()) for day in raw_prices.index],
                        "indicators": {
                            "quote": [{column.lower(): raw_prices[column].tolist() for column in raw_prices}]
                        },
                    }
                ],
                "error": None,
            }
        }
        return payload

    monkeypatch.setattr(yahoo_client, "throttled_get_json", fake_chart)
    monkeypatch.setattr(yfinance_loader.yf, "download", lambda *args, **kwargs: raw_prices)

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfinance_loader.yf, "Ticker", Ticker)
    loader = yahoo_loader.DataLoader if source == "yahoo" else yfinance_loader.DataLoader
    return source, loader


@pytest.mark.parametrize("column", ["Open", "High", "Low", "Close"])
@pytest.mark.parametrize("value", [None, "not-a-price"])
def test_idx_rejects_partial_prices_before_they_disappear(transport, raw_prices, column, value):
    raw_prices[column] = raw_prices[column].astype(object)
    raw_prices.loc[raw_prices.index[0], column] = value
    before = raw_prices.copy(deep=True)
    _, loader = transport
    with pytest.raises(ValueError, match="OHLC|prices"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(raw_prices, before)


def test_idx_rejects_missing_price_field(transport, raw_prices):
    raw_prices.drop(columns="High", inplace=True)
    _, loader = transport
    with pytest.raises(ValueError, match="OHLC|prices"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_idx_rejects_all_nonnumeric_prices_instead_of_calling_them_padding(transport, raw_prices):
    raw_prices[["Open", "High", "Low", "Close"]] = "not-a-price"
    _, loader = transport
    with pytest.raises(ValueError, match="OHLC|prices"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_idx_rejects_absent_prices_with_observed_zero_volume(transport, raw_prices):
    raw_prices.loc[raw_prices.index[1], ["Open", "High", "Low", "Close"]] = None
    _, loader = transport
    with pytest.raises(ValueError, match="OHLC|prices"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_idx_omits_only_fully_absent_slots_without_filling_prices(transport, raw_prices):
    raw_prices.loc[raw_prices.index[0], :] = None
    _, loader = transport
    frame = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-02"), pd.Timestamp("2026-09-03")]
    assert frame["close"].tolist() == [105.0, 105.0]
    assert frame.iloc[0]["volume"] == 0.0
    assert pd.isna(frame.iloc[1]["volume"])


def test_entirely_absent_response_stays_empty(transport, raw_prices):
    raw_prices.loc[:, :] = float("nan")
    _, loader = transport
    assert loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


def test_numeric_strings_remain_valid_observations(transport, raw_prices):
    raw_prices[["Open", "High", "Low", "Close"]] = raw_prices[["Open", "High", "Low", "Close"]].astype(str)
    _, loader = transport
    frame = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame["close"].tolist() == [105.0, 105.0, 105.0]


def test_new_idx_cache_avoids_reacquisition(transport, raw_prices, monkeypatch, tmp_path):
    _, loader = transport
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    original = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    raw_prices.loc[raw_prices.index[0], "High"] = None
    cached = loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    pd.testing.assert_frame_equal(cached, original, check_freq=False)
    assert cached.attrs == original.attrs


def test_non_idx_preserves_existing_partial_price_drop_policy(transport, raw_prices):
    raw_prices.loc[raw_prices.index[0], "High"] = None
    _, loader = transport
    frame = loader().fetch(["AAPL.US"], "2026-09-01", "2026-09-03")["AAPL.US"]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-02"), pd.Timestamp("2026-09-03")]


@pytest.mark.parametrize("old_fields", [None, ["idx_strict_ohlc_v1"]])
def test_partial_price_fetch_bypasses_old_cache(transport, raw_prices, monkeypatch, tmp_path, old_fields):
    source, loader = transport
    legacy = raw_prices.iloc[1:].rename(columns=str.lower)
    legacy.index.name = "trade_date"
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path))
    loader_cache_put(
        source=source,
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-03",
        fields=old_fields,
        frame=legacy,
    )
    raw_prices.loc[raw_prices.index[0], "High"] = None
    with pytest.raises(ValueError, match="OHLC|prices"):
        loader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_automatic_fallback_retains_partial_price_failure(raw_prices, monkeypatch):
    broken = raw_prices.copy(deep=True)
    broken.loc[broken.index[0], "High"] = None
    rows = [
        {"trade_date": int(day.timestamp()), **row.to_dict()}
        for day, row in broken.rename(columns=str.lower).iterrows()
    ]
    monkeypatch.setattr(yahoo_client, "get_chart", lambda *args, **kwargs: (copy.deepcopy(rows), "IDR"))
    monkeypatch.setattr(yfinance_loader.yf, "download", lambda *args, **kwargs: raw_prices)

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfinance_loader.yf, "Ticker", Ticker)
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        include_provenance=True,
        loader_resolver=lambda source: {"yahoo": yahoo_loader.DataLoader, "yfinance": yfinance_loader.DataLoader}[
            source
        ],
    )
    assert result["_provenance"]["BBCA.JK"]["source"] == "yfinance"
    assert result["_provenance"]["BBCA.JK"]["attempts"] == [{"source": "yahoo", "reason": "fetch_failed"}]


def test_shared_idx_preserves_healthy_peer_when_one_series_is_rejected(raw_prices, monkeypatch):
    broken = raw_prices.copy(deep=True)
    broken.loc[broken.index[0], "High"] = None

    def download(tickers, **kwargs):
        return broken if "BBCA.JK" in tickers else raw_prices

    def resolver(source):
        if source != "yfinance":
            raise NoAvailableSourceError("Only synthetic yfinance is configured")
        return yfinance_loader.DataLoader

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfinance_loader.yf, "download", download)
    monkeypatch.setattr(yfinance_loader.yf, "Ticker", Ticker)
    result = fetch_market_data(
        codes=["BBCA.JK", "BBRI.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="yfinance",
        include_provenance=True,
        as_frames=True,
        loader_resolver=resolver,
    )
    assert "BBCA.JK" not in result
    assert result["BBRI.JK"]["close"].tolist() == [105.0, 105.0, 105.0]
    assert result["_provenance"]["BBRI.JK"]["attempts"] == []
    assert result["_diagnostics"]["BBCA.JK"]["attempts"][0] == {"source": "yfinance", "reason": "fetch_failed"}


def test_shared_non_idx_still_batches_provider_download(raw_prices, monkeypatch):
    downloads = []

    def download(tickers, **kwargs):
        downloads.append(tickers)
        return pd.concat({"AAPL": raw_prices, "MSFT": raw_prices}, axis=1)

    monkeypatch.setattr(yfinance_loader.yf, "download", download)
    result = fetch_market_data(
        codes=["AAPL.US", "MSFT.US"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="yfinance",
        as_frames=True,
        loader_resolver=lambda source: yfinance_loader.DataLoader,
    )
    assert result["AAPL.US"]["close"].tolist() == [105.0, 105.0, 105.0]
    assert result["MSFT.US"]["close"].tolist() == [105.0, 105.0, 105.0]
    assert downloads == [["AAPL", "MSFT"]]
