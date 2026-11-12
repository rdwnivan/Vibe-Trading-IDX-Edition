"""A YAML list item without a symbol mapping must not poison valid sources."""

from datetime import date
import logging

import pandas as pd
import pytest
import yaml

from backtest.loaders import local_loader
from backtest.loaders.registry import get_loader_cls_with_fallback
from src.market_data import fetch_market_data


@pytest.fixture
def configured(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    monkeypatch.setattr(local_loader, "_CONFIG_PATH", config)

    def configure(entries):
        config.write_text(yaml.safe_dump({"sources": entries}), encoding="utf-8")
        return local_loader.DataLoader()

    return configure


@pytest.fixture
def sources(tmp_path):
    path = tmp_path / "bars.csv"
    pd.DataFrame(
        {
            "date": ["2026-09-01", "2026-09-02"],
            "open": [100, 100],
            "high": [110, 110],
            "low": [90, 90],
            "close": [105, 105],
            "volume": [0, None],
        }
    ).to_csv(path, index=False)
    return [
        {"symbol": "BBCA.JK", "path": str(path)},
        {"symbol": "AAPL.US", "path": str(path)},
    ]


@pytest.mark.parametrize("invalid", [None, False, 123, 1.5, "SYNTHETIC_PRIVATE_MARKER", [], [{"symbol": "BBCA.JK"}]])
@pytest.mark.parametrize("position", [0, 1, 2])
def test_non_mapping_entry_warns_without_poisoning_healthy_symbols(configured, sources, invalid, position, caplog):
    entries = sources.copy()
    entries.insert(position, invalid)
    loader = configured(entries)
    assert loader.is_available() is True

    with caplog.at_level(logging.WARNING, logger=local_loader.__name__):
        first = loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")
        repeated = loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")

    assert set(first) == {"BBCA.JK", "AAPL.US"}
    assert first["BBCA.JK"]["close"].tolist() == [105, 105]
    assert first["BBCA.JK"]["volume"].iloc[0] == 0
    assert pd.isna(first["BBCA.JK"]["volume"].iloc[1])
    assert first["AAPL.US"]["close"].tolist() == [105, 105]
    pd.testing.assert_frame_equal(first["BBCA.JK"], repeated["BBCA.JK"])
    pd.testing.assert_frame_equal(first["AAPL.US"], repeated["AAPL.US"])
    assert caplog.messages == [
        f"local loader: sources entry {position + 1} must be a mapping; skipping unassigned entry"
    ]
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text


def test_unassigned_entry_does_not_change_failure_empty_or_peer_provenance(configured, sources, tmp_path, caplog):
    empty = tmp_path / "empty.csv"
    empty.write_text("date,open,high,low,close,volume\n", encoding="utf-8")
    configured(
        [
            "SYNTHETIC_PRIVATE_MARKER",
            {"symbol": "BBCA.JK", "path": ""},
            {**sources[0], "symbol": "BBRI.JK"},
            {"symbol": "TLKM.JK", "path": str(empty)},
        ]
    )

    def resolver(source):
        assert source == "local", "explicit local must never resolve a network source"
        return get_loader_cls_with_fallback(source)

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
    assert result["BBRI.JK"][0]["close"] == 105
    assert result["BBRI.JK"][0]["volume"] == 0
    assert result["BBRI.JK"][1]["volume"] is None
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert "quote_currency" not in result["_provenance"]["BBRI.JK"]
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text
    assert "sources entry 1 must be a mapping" in caplog.text


def test_unassigned_entry_is_reported_even_with_healthy_positive_cache(
    configured, sources, tmp_path, monkeypatch, caplog
):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    first = configured(sources).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    cache_files = sorted((tmp_path / "cache").rglob("*.*"))
    assert cache_files, "exercise a populated persistent cache"
    before = {path: path.read_bytes() for path in cache_files}

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged healthy source should reuse its positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    with caplog.at_level(logging.WARNING, logger=local_loader.__name__):
        after = configured([None, *sources]).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")

    pd.testing.assert_frame_equal(first["BBCA.JK"], after["BBCA.JK"])
    assert caplog.messages == ["local loader: sources entry 1 must be a mapping; skipping unassigned entry"]
    assert sorted((tmp_path / "cache").rglob("*.*")) == cache_files
    assert {path: path.read_bytes() for path in cache_files} == before


@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_duplicate_symbol_keeps_last_mapping_and_outer_whitespace_policy(configured, sources, symbol):
    # Pin existing selection; this task does not choose a new duplicate policy.
    loader = configured(
        [
            {"symbol": symbol, "path": ""},
            {**sources[0], "symbol": f" {symbol} "},
        ]
    )
    assert loader.fetch([symbol], "2026-09-01", "2026-09-03")[symbol]["close"].tolist() == [105, 105]


@pytest.mark.parametrize("entry", [{}, {"symbol": ""}, {"symbol": " \t"}])
def test_absent_or_blank_symbol_keeps_existing_unassigned_policy(configured, sources, entry):
    loader = configured([entry, *sources])
    assert loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]["close"].tolist() == [105, 105]


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        False,
        True,
        123,
        1.5,
        float("nan"),
        [],
        ["SYNTHETIC_PRIVATE_MARKER"],
        {},
        {"private": "SYNTHETIC_PRIVATE_MARKER"},
        date(2026, 9, 1),
    ],
)
@pytest.mark.parametrize("position", [0, 1, 2])
def test_non_string_symbol_warns_without_poisoning_healthy_symbols(configured, sources, invalid, position, caplog):
    entries = sources.copy()
    entries.insert(position, {"symbol": invalid, "path": "SYNTHETIC_PRIVATE_MARKER"})
    loader = configured(entries)
    assert loader.is_available() is True

    with caplog.at_level(logging.WARNING, logger=local_loader.__name__):
        first = loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")
        repeated = loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")

    assert set(first) == {"BBCA.JK", "AAPL.US"}
    assert first["BBCA.JK"]["close"].tolist() == [105, 105]
    assert first["BBCA.JK"]["volume"].iloc[0] == 0
    assert pd.isna(first["BBCA.JK"]["volume"].iloc[1])
    assert first["AAPL.US"]["close"].tolist() == [105, 105]
    pd.testing.assert_frame_equal(first["BBCA.JK"], repeated["BBCA.JK"])
    pd.testing.assert_frame_equal(first["AAPL.US"], repeated["AAPL.US"])
    assert caplog.messages == [
        f"local loader: sources entry {position + 1} symbol must be a string; skipping unassigned entry"
    ]
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text


def test_non_string_symbol_preserves_failure_empty_and_healthy_peer_outcomes(configured, sources, tmp_path, caplog):
    empty = tmp_path / "empty.csv"
    empty.write_text("date,open,high,low,close,volume\n", encoding="utf-8")
    configured(
        [
            {"symbol": {"private": "SYNTHETIC_PRIVATE_MARKER"}, "path": "SYNTHETIC_PRIVATE_MARKER"},
            {"symbol": "BBCA.JK", "path": ""},
            {**sources[0], "symbol": "BBRI.JK"},
            {"symbol": "TLKM.JK", "path": str(empty)},
        ]
    )

    def resolver(source):
        assert source == "local", "explicit local must never resolve a network source"
        return get_loader_cls_with_fallback(source)

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
    assert result["BBRI.JK"][0]["close"] == 105
    assert result["BBRI.JK"][0]["volume"] == 0
    assert result["BBRI.JK"][1]["volume"] is None
    assert result["_provenance"]["BBRI.JK"]["source"] == "local"
    assert "quote_currency" not in result["_provenance"]["BBRI.JK"]
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text
    assert "sources entry 1 symbol must be a string" in caplog.text


def test_non_string_symbol_warning_precedes_positive_cache_lookup(configured, sources, tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(tmp_path / "cache"))
    first = configured(sources).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    cache_files = sorted((tmp_path / "cache").rglob("*.*"))
    assert cache_files, "exercise a populated persistent cache"
    before = {path: path.read_bytes() for path in cache_files}

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged healthy source should reuse its positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    with caplog.at_level(logging.WARNING, logger=local_loader.__name__):
        after = configured([{"symbol": None}, *sources]).fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")

    pd.testing.assert_frame_equal(first["BBCA.JK"], after["BBCA.JK"])
    assert caplog.messages == ["local loader: sources entry 1 symbol must be a string; skipping unassigned entry"]
    assert sorted((tmp_path / "cache").rglob("*.*")) == cache_files
    assert {path: path.read_bytes() for path in cache_files} == before


def test_non_string_symbol_is_not_coerced_to_a_requested_string(configured, sources, caplog):
    # Keep a valid index: a wholly unassigned list now fails as configuration.
    loader = configured([{**sources[0], "symbol": 600519}, *sources])
    assert loader.fetch(["600519"], "2026-09-01", "2026-09-03") == {}
    assert "sources entry 1 symbol must be a string" in caplog.text


def test_numeric_string_symbol_keeps_existing_local_matching(configured, sources, caplog):
    loader = configured([{**sources[0], "symbol": " 600519 "}])
    assert loader.fetch(["600519"], "2026-09-01", "2026-09-03")["600519"]["close"].tolist() == [105, 105]
    assert caplog.messages == []


def test_string_symbol_matching_remains_case_sensitive(configured, sources):
    loader = configured([sources[0], {"symbol": "bbca.jk", "path": ""}])
    assert loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]["close"].tolist() == [105, 105]
