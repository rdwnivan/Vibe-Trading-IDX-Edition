"""Synthetic date-schema checks; no production timestamp semantics are inferred."""

import pandas as pd
import pytest
import yaml

from backtest.loaders import local_loader
from backtest.loaders.base import loader_cache_path
from src.market_data import fetch_market_data


def bars(count=1):
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01", periods=count),
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
            "volume": 0.0,
        }
    )


@pytest.fixture
def configured(monkeypatch, tmp_path):
    config = tmp_path / "config.yaml"
    monkeypatch.setattr(local_loader, "_CONFIG_PATH", config)

    def configure(frame, *, kind="csv", symbol="BBCA.JK", **settings):
        path = tmp_path / (symbol + "." + kind)
        entry = {"symbol": symbol, "type": kind, **settings}
        if kind == "duckdb":
            import duckdb

            with duckdb.connect(str(path)) as connection:
                connection.register("source", frame)
                connection.execute("CREATE OR REPLACE TABLE bars AS SELECT * FROM source")
            entry.update(db_path=str(path), query="SELECT * FROM bars")
        elif kind == "parquet":
            # Decoder boundary stub; CSV and DuckDB exercise real synthetic files.
            path.touch()
            monkeypatch.setattr(pd, "read_parquet", lambda *a, **k: frame.copy(deep=True))
            entry["path"] = str(path)
        else:
            frame.to_csv(path, index=False)
            entry["path"] = str(path)
        config.write_text(yaml.safe_dump({"sources": [entry]}), encoding="utf-8")
        return entry

    return configure


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("count", [0, 1])
@pytest.mark.parametrize("columns", [{}, {"date": "absent_time"}])
def test_idx_missing_date_schema_is_failure_even_when_empty(configured, kind, count, columns):
    configured(bars(count).drop(columns="date"), kind=kind, columns=columns)
    with pytest.raises(ValueError, match="IDX local dates require a date column or DatetimeIndex"):
        local_loader.DataLoader().fetch(["local:BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_incorrect_date_mapping_does_not_borrow_unmapped_column(configured, kind):
    configured(bars(), kind=kind, columns={"date": "absent_time"})
    with pytest.raises(ValueError, match="IDX local dates require"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
@pytest.mark.parametrize("count", [0, 1])
def test_non_idx_missing_date_schema_retains_no_data_policy(configured, kind, count):
    configured(bars(count).drop(columns="date"), kind=kind, symbol="AAPL.US")
    assert local_loader.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_empty_valid_mapped_schema_remains_no_data(configured, kind):
    configured(bars(0).rename(columns={"date": "Session"}), kind=kind, columns={"date": "Session"})
    assert local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_mapped_date_preserves_observations_without_metadata(configured, kind):
    frame = bars(2).rename(columns={"date": "Session"})
    frame["Session"] = ["01/09/2026", "02/09/2026"]
    frame["volume"] = [0, None]
    configured(frame, kind=kind, columns={"date": "Session"}, date_format="%d/%m/%Y")
    result = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert result.index.tolist() == [pd.Timestamp("2026-09-01"), pd.Timestamp("2026-09-02")]
    assert result["close"].tolist() == [105, 105]
    assert result["volume"].iloc[0] == 0
    assert pd.isna(result["volume"].iloc[1])
    assert result.attrs == {}


@pytest.mark.parametrize("date_format", [None, "%Y-%m-%d"])
def test_idx_datetime_index_remains_date_source(configured, date_format):
    frame = bars().set_index("date")
    frame.index.name = "bar_time"
    configured(frame, kind="parquet", columns={"date": "absent_time"}, date_format=date_format)
    result = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert result.index.tolist() == [pd.Timestamp("2026-09-01")]


@pytest.mark.parametrize("date_format", [None, "%Y-%m-%d"])
def test_idx_empty_datetime_index_remains_valid_schema(configured, date_format):
    configured(bars(0).set_index("date"), kind="parquet", date_format=date_format)
    assert local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


def test_idx_explicit_date_column_still_wins_over_datetime_index(configured):
    frame = bars()
    frame.index = pd.DatetimeIndex(["2026-08-01"], name="date")
    configured(frame, kind="parquet")
    result = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert result.index.tolist() == [pd.Timestamp("2026-09-01")]


def test_missing_schema_is_not_negative_cached_and_corrected_file_is_read(configured, monkeypatch, tmp_path):
    entry = configured(bars().drop(columns="date"))
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    args = dict(
        source="local",
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-03",
        fields=[local_loader._source_cache_identity(entry), *local_loader._IDX_CACHE_FIELDS],
    )
    with pytest.raises(ValueError, match="IDX local dates require"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    assert not loader_cache_path(**args).exists()
    configured(bars())
    result = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert result["close"].tolist() == [105]


def test_missing_schema_replaces_cached_valid_source_without_hiding_failure(configured, monkeypatch, tmp_path):
    configured(bars())
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    first = local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert first["close"].tolist() == [105]
    configured(bars().drop(columns="date"))
    with pytest.raises(ValueError, match="IDX local dates require"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    assert len(list((tmp_path / "cache").rglob("*.json"))) == 1


def test_idx_missing_schema_is_fetch_failed_and_peers_keep_data_or_no_data(configured, tmp_path):
    invalid = configured(bars().drop(columns="date"))
    empty = tmp_path / "empty.csv"
    bars(0).to_csv(empty, index=False)
    healthy = tmp_path / "healthy.csv"
    frame = bars(2)
    frame["volume"] = [0, None]
    frame.to_csv(healthy, index=False)
    config = {
        "sources": [invalid, {"symbol": "BBRI.JK", "path": str(healthy)}, {"symbol": "TLKM.JK", "path": str(empty)}]
    }
    local_loader._CONFIG_PATH.write_text(yaml.safe_dump(config), encoding="utf-8")

    def resolver(source):
        assert source == "local", "explicit local must never attempt network fallback"
        return local_loader.DataLoader

    result = fetch_market_data(
        codes=["local:BBCA.JK", "BBRI.JK", "TLKM.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )
    assert result["_diagnostics"]["local:BBCA.JK"]["attempts"] == [{"source": "local", "reason": "fetch_failed"}]
    assert result["_diagnostics"]["TLKM.JK"]["attempts"] == [{"source": "local", "reason": "no_data"}]
    assert result["BBRI.JK"][0]["volume"] == 0
    assert result["BBRI.JK"][1]["volume"] is None
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert result["_provenance"]["BBRI.JK"]["attempts"] == []
