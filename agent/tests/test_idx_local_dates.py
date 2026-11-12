"""Synthetic local-date rejection; UTC behavior is pinned, not certified for IDX."""

import pandas as pd
import pytest

from backtest.loaders import local_loader
from backtest.loaders.base import loader_cache_get, loader_cache_put
from src.market_data import fetch_market_data


def bars(dates):
    return pd.DataFrame({"date": dates, "open": 100, "high": 110, "low": 90, "close": 105, "volume": 0})


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
            # Optional decoder boundary only; CSV and DuckDB use real files.
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
@pytest.mark.parametrize("invalid", ["not-a-date", "2026-02-30", "9999-09-01", None])
def test_idx_invalid_date_rejects_series_before_row_can_disappear(configured, kind, invalid):
    configured(bars(["2026-09-01", invalid, "2026-09-03"]), kind=kind)
    with pytest.raises(ValueError, match="IDX local dates"):
        local_loader.DataLoader().fetch(["local:BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_all_invalid_dates_are_failure_not_empty(configured, kind):
    configured(bars(["not-a-date"]), kind=kind, date_format="%Y-%m-%d")
    with pytest.raises(ValueError, match="IDX local dates"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_idx_date_format_mismatch_rejects_instead_of_shortening(configured):
    configured(bars(["01/09/2026", "2026-09-02"]), date_format="%d/%m/%Y")
    with pytest.raises(ValueError, match="IDX local dates"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


def test_idx_invalid_datetime_index_rejects_before_resampling(configured):
    frame = bars(["unused", "unused"]).drop(columns="date")
    frame.index = pd.DatetimeIndex([pd.Timestamp("2026-09-01"), pd.NaT], name="bar_time")
    configured(frame, kind="parquet")
    with pytest.raises(ValueError, match="IDX local dates"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_non_idx_invalid_date_keeps_existing_drop_policy(configured, kind):
    configured(bars(["2026-09-01", "not-a-date", "2026-09-03"]), kind=kind, symbol="AAPL.US")
    frame = local_loader.DataLoader().fetch(["AAPL.US"], "2026-09-01", "2026-09-03")["AAPL.US"]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-01"), pd.Timestamp("2026-09-03")]
    assert frame["volume"].tolist() == [0, 0]


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_idx_empty_file_with_schema_is_no_data(configured, kind):
    configured(bars([]), kind=kind)
    assert local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


def test_idx_valid_dates_outside_requested_range_are_no_data(configured):
    configured(bars(["2026-08-31", "2026-09-04"]))
    assert local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_local_utc_conversion_and_half_open_end_remain_existing_contract(configured, symbol):
    # 23:59 +07 is 16:59 UTC on Sep 1; 06:59 +07 is still Aug 31 UTC.
    configured(
        bars(["2026-09-01T06:59:59+07:00", "2026-09-01T23:59:59+07:00", "2026-09-02T07:00:00+07:00"]),
        symbol=symbol,
    )
    frame = local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-01", interval="1H")[symbol]
    assert frame.index.tolist() == [pd.Timestamp("2026-09-01 16:00:00")]
    assert frame["volume"].tolist() == [0]
    assert "quote_currency" not in frame.attrs


def test_idx_bad_date_cannot_be_hidden_by_previous_volume_cache(configured, monkeypatch, tmp_path):
    entry = configured(bars(["2026-09-01", "not-a-date"]))
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    legacy = bars(["2026-09-01"]).set_index("date")
    legacy.index = pd.DatetimeIndex(legacy.index, name="trade_date")
    args = dict(
        source="local",
        symbol="BBCA.JK",
        timeframe="1D",
        start_date="2026-09-01",
        end_date="2026-09-03",
        source_revision=local_loader._source_file_revision(entry),
    )
    old_fields = [local_loader._source_cache_identity(entry), "idx_local_volume_v1"]
    loader_cache_put(**args, fields=old_fields, frame=legacy)

    with pytest.raises(ValueError, match="IDX local dates"):
        local_loader.DataLoader().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(loader_cache_get(**args, fields=old_fields), legacy)


def test_idx_bad_date_is_fetch_failed_while_empty_peer_is_no_data(configured, monkeypatch, tmp_path):
    invalid = configured(bars(["2026-09-01", "not-a-date"]))
    empty = tmp_path / "empty.csv"
    bars([]).to_csv(empty, index=False)
    healthy = tmp_path / "healthy.csv"
    bars(["2026-09-01"]).to_csv(healthy, index=False)
    monkeypatch.setattr(
        local_loader,
        "_load_config",
        lambda: {
            "sources": [invalid, {"symbol": "BBRI.JK", "path": str(healthy)}, {"symbol": "TLKM.JK", "path": str(empty)}]
        },
    )

    def resolver(source):
        assert source == "local", "explicit local must never attempt network fallback"
        return local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK", "BBRI.JK", "TLKM.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        as_frames=True,
        include_provenance=True,
        loader_resolver=resolver,
    )
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == [{"source": "local", "reason": "fetch_failed"}]
    assert result["_diagnostics"]["TLKM.JK"]["attempts"] == [{"source": "local", "reason": "no_data"}]
    assert result["BBRI.JK"]["volume"].tolist() == [0]
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert result["_provenance"]["BBRI.JK"]["attempts"] == []
