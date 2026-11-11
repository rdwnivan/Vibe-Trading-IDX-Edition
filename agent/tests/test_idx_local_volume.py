"""Synthetic Local Data Bridge volume observations, without IDX metadata claims."""

import json

import numpy as np
import pandas as pd
import pytest

from backtest.loaders import local_loader
from backtest.loaders.base import loader_cache_get, loader_cache_put
from src.market_data import fetch_market_data
from src.tools.idx_research_tool import IDXResearchTool


@pytest.fixture
def configured(monkeypatch, tmp_path):
    def configure(frame, symbol="BBCA.JK", kind="csv"):
        path = tmp_path / (symbol + "." + kind)
        entry = {"symbol": symbol, "type": kind}
        if kind == "duckdb":
            import duckdb

            with duckdb.connect(str(path)) as connection:
                connection.register("source", frame)
                connection.execute("CREATE TABLE bars AS SELECT * FROM source")
            entry.update(db_path=str(path), query="SELECT * FROM bars")
        elif kind == "parquet":
            path.touch()
            monkeypatch.setattr(pd, "read_parquet", lambda *a, **k: frame.copy(deep=True))
            entry["path"] = str(path)
        else:
            frame.to_csv(path, index=False)
            entry["path"] = str(path)
        monkeypatch.setattr(local_loader, "_load_config", lambda: {"sources": [entry]})
        return entry

    return configure


def bars(volumes):
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01 01:00", periods=4, freq="h"),
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
        }
    )
    if volumes is not None:
        frame["volume"] = pd.Series(volumes, dtype=object)
    return frame


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_absent_volume_column_stays_missing(configured, kind):
    configured(bars(None), kind=kind)
    frame = local_loader.DataLoader().fetch(["local:BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    assert frame["volume"].isna().all()
    assert frame["close"].tolist() == [105.0]
    assert "quote_currency" not in frame.attrs
    assert "volume_unit" not in frame.attrs


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("volumes", [[None] * 4, [100, None, 0, 200]])
def test_idx_daily_volume_requires_every_observed_constituent(configured, kind, volumes):
    configured(bars(volumes), kind=kind)
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    assert len(frame) == 1
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame.iloc[0]["open"] == 100
    assert frame.iloc[0]["close"] == 105


@pytest.mark.parametrize("volumes,expected", [([0, 0, 0, 0], 0), ([100, 0, 200, 300], 600)])
def test_idx_observed_zero_and_complete_volume_totals_are_preserved(configured, volumes, expected):
    configured(bars(volumes))
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    assert frame["volume"].tolist() == [expected]


def test_idx_native_hourly_volume_preserves_null_zero_and_value(configured):
    configured(bars([None, 0, 100, 200]))
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01", interval="1H")["BBCA.JK"]
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame["volume"].iloc[1:].tolist() == [0, 100, 200]


@pytest.mark.parametrize(
    "value",
    ["invalid-volume", True, np.bool_(False), complex(1, 0), np.complex64(1 + 2j), -1, float("inf"), "1e9999", 10**400],
)
def test_idx_invalid_volume_rejected_before_reader_coercion(configured, value):
    # Parquet boundary stub retains raw scalar types; real CSV/DB cannot encode all of these.
    configured(bars([value, 0, 100, 200]), kind="parquet")
    with pytest.raises(ValueError, match="volume"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


def test_idx_overflowing_aggregate_rejected(configured):
    configured(bars([1e308] * 4))
    with pytest.raises(ValueError, match="volume"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("kind", ["csv", "duckdb"])
@pytest.mark.parametrize("value", ["invalid-volume", "True", "1e9999"])
def test_real_readers_reject_invalid_volume_strings(configured, kind, value):
    configured(bars([value, "0", "100", "200"]), kind=kind)
    with pytest.raises(ValueError, match="volume"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_numeric_volume_strings_remain_supported(configured, kind):
    configured(bars(["100", "0", "200", "300"]), kind=kind)
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    assert frame["volume"].tolist() == [600.0]


def test_missing_volume_only_affects_its_aggregate_and_empty_days_stay_absent(configured):
    first = bars([None, 0, 100, 200])
    third = bars([100, 0, 200, 300])
    third["date"] = third["date"] + pd.Timedelta(days=2)
    configured(pd.concat([first, third], ignore_index=True))
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-01"), pd.Timestamp("2026-09-03")]
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame.iloc[1]["volume"] == 600


@pytest.mark.parametrize("volumes,expected", [(None, 0), ([None] * 4, 0), ([100, None, 0, 200], 300)])
def test_non_idx_local_volume_retains_existing_policy(configured, volumes, expected):
    configured(bars(volumes), symbol="AAPL.US")
    frame = local_loader.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-01")["AAPL.US"]
    assert frame["volume"].tolist() == [expected]


def test_idx_old_local_cache_cannot_hide_fabricated_zero(configured, monkeypatch, tmp_path):
    entry = configured(bars(None))
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    legacy = pd.DataFrame(
        {"open": [100.0], "high": [110.0], "low": [90.0], "close": [105.0], "volume": [0.0]},
        index=pd.DatetimeIndex(["2026-09-01"], name="trade_date"),
    )
    args = dict(
        source="local",
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-01",
        source_revision=local_loader._source_file_revision(entry),
    )
    old_fields = [local_loader._source_cache_identity(entry)]
    loader_cache_put(**args, fields=old_fields, frame=legacy)
    frame = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    assert frame["volume"].isna().all()
    assert loader_cache_get(**args, fields=old_fields)["volume"].tolist() == [0.0]

    def unexpected_read(*args, **kwargs):
        raise AssertionError("new valid cache must avoid acquisition")

    monkeypatch.setitem(local_loader._READERS, "csv", unexpected_read)
    cached = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-01")["BBCA.JK"]
    pd.testing.assert_frame_equal(cached, frame, check_freq=False)


def test_idx_invalid_local_series_keeps_peer_and_disallows_network_fallback(monkeypatch, tmp_path):
    broken = tmp_path / "broken.csv"
    healthy = tmp_path / "healthy.csv"
    bars(["invalid-volume", 0, 100, 200]).to_csv(broken, index=False)
    bars([100, 0, 200, 300]).to_csv(healthy, index=False)
    monkeypatch.setattr(
        local_loader,
        "_load_config",
        lambda: {"sources": [{"symbol": "BBCA.JK", "path": str(broken)}, {"symbol": "BBRI.JK", "path": str(healthy)}]},
    )
    sources = []

    def resolver(source):
        sources.append(source)
        assert source == "local", "explicit local must never try a network loader"
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
    assert result["BBRI.JK"]["volume"].tolist() == [600.0]
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == [{"source": "local", "reason": "fetch_failed"}]
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert result["_provenance"]["BBRI.JK"]["attempts"] == []
    assert sources == ["local", "local"]


def test_local_volume_fix_does_not_certify_idx_research_metadata(configured, monkeypatch):
    configured(bars(None))
    monkeypatch.setattr(
        "src.tools.idx_research_tool.fetch_market_data",
        lambda **kwargs: fetch_market_data(
            **{**kwargs, "source": "local"}, loader_resolver=lambda source: local_loader.DataLoader
        ),
    )
    result = json.loads(IDXResearchTool().execute(codes=["BBCA.JK"], lookback=20, end_date="2026-09-01"))
    assert result["items"][0]["status"] == "unavailable"
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert result["backtest_enabled"] is False
