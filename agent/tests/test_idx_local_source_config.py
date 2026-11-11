"""Malformed IDX local reader declarations are failures, not empty datasets."""

import pandas as pd
import pytest
import yaml

from backtest.loaders import local_loader
from src.market_data import fetch_market_data


def bars(count=2):
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01", periods=count),
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
            "volume": [0, None][:count],
        }
    )


@pytest.fixture
def configured(monkeypatch, tmp_path):
    path = tmp_path / "config.yaml"
    monkeypatch.setattr(local_loader, "_CONFIG_PATH", path)

    def configure(*entries):
        path.write_text(yaml.safe_dump({"sources": list(entries)}), encoding="utf-8")
        return local_loader.DataLoader()

    return configure


@pytest.fixture
def sources(tmp_path):
    import duckdb

    csv = tmp_path / "bars.csv"
    bars().to_csv(csv, index=False)
    database = tmp_path / "bars.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.register("source", bars())
        connection.execute("CREATE TABLE bars AS SELECT * FROM source")
    return {
        "csv": {"symbol": "BBCA.JK", "type": "csv", "path": str(csv)},
        "parquet": {"symbol": "BBCA.JK", "type": "parquet", "path": str(tmp_path / "bars.parquet")},
        "duckdb": {"symbol": "BBCA.JK", "type": "duckdb", "db_path": str(database), "query": "SELECT * FROM bars"},
    }


@pytest.mark.parametrize("invalid", ["unsupported-synthetic", "", " \t", None, False, 123, [], {}])
def test_idx_invalid_type_is_explicit_configuration_failure(configured, sources, invalid):
    loader = configured({**sources["csv"], "type": invalid})
    with pytest.raises(ValueError, match="IDX local source requires a supported type"):
        loader.fetch(["local:BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize(
    "kind, field", [("csv", "path"), ("parquet", "path"), ("duckdb", "db_path"), ("duckdb", "query")]
)
@pytest.mark.parametrize("invalid", ["", " \t", None, False, 123, [], {}])
def test_idx_required_reader_field_is_nonblank_string(configured, sources, kind, field, invalid):
    loader = configured({**sources[kind], field: invalid})
    with pytest.raises(ValueError, match=f"IDX local source requires a nonblank string {field}"):
        loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize(
    "kind, field", [("csv", "path"), ("parquet", "path"), ("duckdb", "db_path"), ("duckdb", "query")]
)
def test_idx_absent_reader_field_is_configuration_failure(configured, sources, kind, field):
    entry = sources[kind].copy()
    del entry[field]
    loader = configured(entry)
    with pytest.raises(ValueError, match=f"IDX local source requires a nonblank string {field}"):
        loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize(
    "kind, field", [("csv", "path"), ("parquet", "path"), ("duckdb", "db_path"), ("duckdb", "query")]
)
def test_invalid_declaration_is_rejected_before_reader_io(configured, sources, monkeypatch, kind, field):
    import duckdb

    def forbidden(*args, **kwargs):
        pytest.fail("invalid declaration must not reach reader I/O")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    monkeypatch.setattr(pd, "read_parquet", forbidden)
    monkeypatch.setattr(duckdb, "connect", forbidden)
    loader = configured({**sources[kind], field: ""})
    with pytest.raises(ValueError, match="IDX local source requires"):
        loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_valid_local_declaration_preserves_prices_and_zero_missing_volume(configured, sources, monkeypatch, kind):
    monkeypatch.setattr(pd, "read_parquet", lambda *a, **k: bars())
    entry = {**sources[kind], "type": "  " + kind.upper() + "  "}
    loader = configured(entry)
    frame = loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame["close"].tolist() == [105, 105]
    assert frame["volume"].iloc[0] == 0
    assert pd.isna(frame["volume"].iloc[1])
    assert frame.attrs == {}


def test_omitted_type_remains_default_csv(configured, sources):
    entry = sources["csv"].copy()
    del entry["type"]
    frame = configured(entry).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    assert frame["close"].tolist() == [105, 105]


@pytest.mark.parametrize("kind", ["csv", "duckdb", "parquet"])
def test_empty_valid_source_is_still_no_data(configured, sources, tmp_path, monkeypatch, kind):
    import duckdb

    empty_csv = tmp_path / "empty.csv"
    bars(0).to_csv(empty_csv, index=False)
    with duckdb.connect(sources["duckdb"]["db_path"]) as connection:
        connection.execute("DELETE FROM bars")
    monkeypatch.setattr(pd, "read_parquet", lambda *a, **k: bars(0))
    entries = {**sources, "csv": {**sources["csv"], "path": str(empty_csv)}}
    assert configured(entries[kind]).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize(
    "kind, changes",
    [
        ("csv", {"type": "unsupported"}),
        ("csv", {"path": ""}),
        ("csv", {"path": None}),
        ("parquet", {"path": " "}),
        ("duckdb", {"query": ""}),
        ("duckdb", {"query": None}),
    ],
)
def test_non_idx_configuration_keeps_existing_omission_policy(configured, sources, kind, changes):
    loader = configured({**sources[kind], **changes, "symbol": "AAPL.US"})
    assert loader.fetch(["AAPL.US"], "2026-09-01", "2026-09-03") == {}


def test_bad_declaration_errors_do_not_echo_raw_type(configured, caplog):
    raw_type = "SYNTHETIC_PRIVATE_MARKER"
    loader = configured({"symbol": "BBCA.JK", "type": raw_type})
    with pytest.raises(ValueError, match="IDX local source requires a supported type") as caught:
        loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    assert raw_type not in str(caught.value)
    assert raw_type not in caplog.text


def test_changed_configuration_cannot_reuse_positive_cache(configured, sources, monkeypatch, tmp_path):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    entry = sources["csv"]
    first = configured(entry).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    cache_files = sorted((tmp_path / "cache").rglob("*.*"))
    assert cache_files, "exercise a populated cache"
    before = {path: path.read_bytes() for path in cache_files}
    with pytest.raises(ValueError, match="IDX local source requires"):
        configured({**entry, "path": ""}).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    assert {path: path.read_bytes() for path in cache_files} == before
    assert sorted((tmp_path / "cache").rglob("*.*")) == cache_files

    def forbidden(*args, **kwargs):
        pytest.fail("corrected unchanged declaration should reuse its positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    restored = configured(entry).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]
    pd.testing.assert_frame_equal(restored, first)


def test_configuration_failure_is_isolated_from_empty_and_healthy_peers(configured, sources, tmp_path):
    empty = tmp_path / "empty.csv"
    bars(0).to_csv(empty, index=False)
    configured(
        {**sources["csv"], "path": ""},
        {**sources["csv"], "symbol": "BBRI.JK"},
        {"symbol": "TLKM.JK", "path": str(empty)},
    )

    def resolver(source):
        assert source == "local", "explicit local must never attempt a network fallback"
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


def test_unconfigured_symbol_remains_no_data(configured):
    assert configured().fetch(["BBCA.JK"], "2026-09-01", "2026-09-03") == {}
