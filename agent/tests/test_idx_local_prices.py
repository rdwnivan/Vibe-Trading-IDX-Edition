"""Synthetic Local Data Bridge OHLC failures before filtering and aggregation."""

import numpy as np
import pandas as pd
import pytest

from backtest.loaders import local_loader
from backtest.loaders.base import loader_cache_get, loader_cache_put
from src.market_data import fetch_market_data


def bars():
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01 01:00", periods=3, freq="h"),
            "open": [100.0] * 3,
            "high": [110.0] * 3,
            "low": [90.0] * 3,
            "close": [105.0] * 3,
            "volume": [100, 0, None],
        }
    )


@pytest.fixture
def configured(monkeypatch, tmp_path):
    def configure(frame, *, kind="csv", symbol="BBCA.JK", **settings):
        path = tmp_path / (symbol + "." + kind)
        entry = {"symbol": symbol, "type": kind, **settings}
        if kind == "duckdb":
            import duckdb

            with duckdb.connect(str(path)) as connection:
                connection.register("source", frame)
                connection.execute("CREATE TABLE bars AS SELECT * FROM source")
            entry.update(db_path=str(path), query="SELECT * FROM bars")
        elif kind == "parquet":
            # Decoder boundary stub; CSV and DuckDB exercise real file readers.
            path.touch()
            monkeypatch.setattr(pd, "read_parquet", lambda *a, **k: frame.copy(deep=True))
            entry["path"] = str(path)
        else:
            frame.to_csv(path, index=False)
            entry["path"] = str(path)
        monkeypatch.setattr(local_loader, "_load_config", lambda: {"sources": [entry]})
        return entry

    return configure


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("column", ["open", "high", "low", "close"])
@pytest.mark.parametrize("value", [None, "bad-price", float("inf"), "1e9999", 0, -1])
def test_idx_bad_price_rejects_series_before_resampling(configured, kind, column, value):
    frame = bars().astype({column: object})
    frame.loc[1, column] = value
    configured(frame, kind=kind)
    with pytest.raises(ValueError, match="prices|OHLC"):
        local_loader.DataLoader().fetch(["local:BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("column", ["open", "high", "low", "close"])
def test_idx_missing_price_field_is_failure_not_empty(configured, kind, column):
    configured(bars().drop(columns=column), kind=kind)
    with pytest.raises(ValueError, match="OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("volume", [None, 0])
def test_idx_dated_row_with_all_missing_ohlc_is_not_padding(configured, kind, volume):
    frame = bars()
    frame.loc[1, ["open", "high", "low", "close"]] = None
    frame.loc[1, "volume"] = volume
    configured(frame, kind=kind)
    with pytest.raises(ValueError, match="prices|OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("value", [True, np.bool_(False), complex(100, 0), np.complex64(100 + 1j)])
def test_idx_raw_boolean_or_complex_prices_are_rejected(configured, value):
    frame = bars().astype({"open": object, "high": object, "low": object, "close": object})
    # Equal boolean/complex prices could survive structure checks or float casting.
    frame.loc[1, ["open", "high", "low", "close"]] = value
    configured(frame, kind="parquet")
    with pytest.raises(ValueError, match="prices|OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("column,value", [("high", 80), ("low", 120), ("open", 120), ("close", 120)])
def test_idx_structural_price_violation_rejects_instead_of_dropping(configured, column, value):
    frame = bars()
    frame.loc[1, column] = value
    configured(frame)
    with pytest.raises(ValueError, match="OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


def test_idx_ohlc_defect_outside_request_still_rejects_file(configured):
    frame = bars()
    frame.loc[0, "date"] = pd.Timestamp("2026-08-31")
    frame.loc[0, "high"] = None
    configured(frame)
    with pytest.raises(ValueError, match="prices|OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_valid_numeric_price_strings_keep_ohlc_and_volume_null_zero(configured, kind):
    frame = bars().astype({column: str for column in ["open", "high", "low", "close"]})
    configured(frame, kind=kind)
    result = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01", interval="1H")["BBCA.JK"]
    assert result["close"].tolist() == [105, 105, 105]
    assert result["volume"].iloc[:2].tolist() == [100, 0]
    assert pd.isna(result["volume"].iloc[2])
    assert "quote_currency" not in result.attrs
    assert "volume_unit" not in result.attrs


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("bad_close", [None, "bad-price", 120])
def test_non_idx_price_drop_policy_is_preserved(configured, kind, bad_close):
    frame = bars().astype({"close": object})
    frame.loc[1, "close"] = bad_close
    configured(frame, kind=kind, symbol="AAPL.US")
    result = local_loader.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-01", interval="1H")["AAPL.US"]
    assert result["close"].tolist() == [105, 105]


def test_idx_price_fix_bypasses_old_date_cache_without_deleting_it(configured, monkeypatch, tmp_path):
    raw = bars()
    raw.loc[1, "high"] = None
    entry = configured(raw)
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    legacy = bars().drop(columns="date").iloc[:1]
    legacy.index = pd.DatetimeIndex(["2026-09-01"], name="trade_date")
    args = dict(
        source="local",
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-01",
        source_revision=local_loader._source_file_revision(entry),
    )
    old_fields = [local_loader._source_cache_identity(entry), "idx_local_volume_v1", "idx_local_dates_v1"]
    loader_cache_put(**args, fields=old_fields, frame=legacy)
    with pytest.raises(ValueError, match="prices|OHLC"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")
    pd.testing.assert_frame_equal(loader_cache_get(**args, fields=old_fields), legacy)


def test_idx_valid_price_cache_can_be_reused(configured, monkeypatch, tmp_path):
    configured(bars())
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    first = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]

    def unexpected_read(*args, **kwargs):
        raise AssertionError("validated cache should avoid reacquisition")

    monkeypatch.setitem(local_loader._READERS, "csv", unexpected_read)
    second = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    pd.testing.assert_frame_equal(first, second, check_freq=False)


def test_idx_invalid_price_keeps_healthy_peer_and_explicit_local_provenance(configured, monkeypatch, tmp_path):
    raw = bars()
    raw.loc[1, "high"] = None
    invalid = configured(raw)
    healthy = tmp_path / "healthy.csv"
    bars().to_csv(healthy, index=False)
    monkeypatch.setattr(
        local_loader, "_load_config", lambda: {"sources": [invalid, {"symbol": "BBRI.JK", "path": str(healthy)}]}
    )

    def resolver(source):
        assert source == "local", "explicit local must never try a network source"
        return local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK", "BBRI.JK"],
        start_date="2026-09-01",
        end_date="2026-09-01",
        source="local",
        as_frames=True,
        include_provenance=True,
        loader_resolver=resolver,
    )
    assert "BBCA.JK" not in result
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == [{"source": "local", "reason": "fetch_failed"}]
    assert result["BBRI.JK"]["close"].tolist() == [105]
    assert pd.isna(result["BBRI.JK"]["volume"].iloc[0])
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert result["_provenance"]["BBRI.JK"]["attempts"] == []
