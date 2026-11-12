"""A declared sources container must be a list on every local loader route."""

from datetime import date

import pandas as pd
import pytest
import yaml

from backtest.loaders import local_loader
from backtest.loaders.registry import get_loader_cls_with_fallback
from src.market_data import fetch_market_data


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    path = tmp_path / "config.yaml"
    monkeypatch.setattr(local_loader, "_CONFIG_PATH", path)
    return path


@pytest.fixture
def valid_document(tmp_path):
    bars = tmp_path / "bars.csv"
    bars.write_text(
        "date,open,high,low,close,volume\n2026-09-01,100,110,90,105,0\n2026-09-02,100,110,90,105,\n",
        encoding="utf-8",
    )
    return {"sources": [{"symbol": "BBCA.JK", "path": str(bars)}, {"symbol": "AAPL.US", "path": str(bars)}]}


@pytest.mark.parametrize(
    "sources",
    [
        None,
        False,
        True,
        0,
        42,
        0.0,
        1.5,
        float("nan"),
        "",
        "SYNTHETIC_PRIVATE_MARKER",
        {},
        {"private": "SYNTHETIC_PRIVATE_MARKER"},
        date(2026, 9, 1),
    ],
)
@pytest.mark.parametrize("surface", ["availability", "fetch", "resolver"])
def test_declared_non_list_sources_raise_specific_error(config_path, sources, surface):
    config_path.write_text(yaml.safe_dump({"sources": sources}), encoding="utf-8")
    loader = local_loader.DataLoader()
    calls = {
        "availability": loader.is_available,
        "fetch": lambda: loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03"),
        "resolver": lambda: get_loader_cls_with_fallback("local"),
    }
    with pytest.raises(ValueError, match="^local loader: sources must be a list$"):
        calls[surface]()


@pytest.mark.parametrize("document", [{}, {"annotation": "allowed"}, {"sources": []}])
def test_sources_absent_or_empty_list_keeps_existing_behavior(config_path, document):
    config_path.write_text(yaml.safe_dump(document), encoding="utf-8")
    loader = local_loader.DataLoader()
    assert loader.is_available() is False
    assert loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize("invalid", [None, {}])
def test_failed_sources_validation_is_retried_on_same_instance(config_path, valid_document, invalid):
    config_path.write_text(yaml.safe_dump({"sources": invalid}), encoding="utf-8")
    loader = local_loader.DataLoader()
    with pytest.raises(ValueError, match="sources must be a list"):
        loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")
    with pytest.raises(ValueError, match="sources must be a list"):
        loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")
    config_path.write_text(yaml.safe_dump(valid_document), encoding="utf-8")
    result = loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03")
    assert result["BBCA.JK"]["close"].tolist() == [105, 105]
    assert result["AAPL.US"]["close"].tolist() == [105, 105]


@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_sources_validation_precedes_positive_cache_without_changing_cache(
    config_path,
    valid_document,
    tmp_path,
    monkeypatch,
    symbol,
):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    cache = tmp_path / "cache"
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(cache))
    valid = yaml.safe_dump(valid_document)
    config_path.write_text(valid, encoding="utf-8")
    first = local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    before = {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()}
    assert before, "exercise a populated cache"
    config_path.write_text("sources: {}", encoding="utf-8")
    with pytest.raises(ValueError, match="sources must be a list"):
        local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before
    config_path.write_text(valid, encoding="utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged healthy source must reuse positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    restored = local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(first[symbol], restored[symbol])
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before


@pytest.mark.parametrize("invalid", [None, {"private": "SYNTHETIC_PRIVATE_MARKER"}])
@pytest.mark.parametrize("resolved", [True, False])
def test_bad_sources_are_failure_without_network_fallback(config_path, invalid, resolved, caplog):
    config_path.write_text(yaml.safe_dump({"sources": invalid}), encoding="utf-8")

    def resolver(source):
        assert source == "local", "explicit local must not resolve network sources"
        return get_loader_cls_with_fallback(source) if resolved else local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK", "AAPL.US"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )
    expected = [{"source": "local", "reason": "source_unavailable" if resolved else "fetch_failed"}]
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == expected
    assert result["_diagnostics"]["AAPL.US"]["attempts"] == expected
    assert "BBCA.JK" not in result and "AAPL.US" not in result
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text


def test_list_preserves_healthy_peers_empty_data_and_entry_warnings(config_path, valid_document, tmp_path, caplog):
    empty = tmp_path / "empty.csv"
    empty.write_text("date,open,high,low,close,volume\n", encoding="utf-8")
    entries = [None, {"symbol": None}, *valid_document["sources"], {"symbol": "TLKM.JK", "path": str(empty)}]
    config_path.write_text(yaml.safe_dump({"sources": entries}), encoding="utf-8")
    result = fetch_market_data(
        codes=["BBCA.JK", "AAPL.US", "TLKM.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=get_loader_cls_with_fallback,
    )
    assert result["BBCA.JK"][0]["close"] == 105
    assert result["AAPL.US"][0]["close"] == 105
    assert result["BBCA.JK"][0]["volume"] == 0
    assert result["BBCA.JK"][1]["volume"] is None
    assert result["_provenance"]["BBCA.JK"]["source"] == "local"
    assert result["_diagnostics"]["TLKM.JK"]["attempts"] == [{"source": "local", "reason": "no_data"}]
    assert "sources entry 1 must be a mapping" in caplog.text
    assert "sources entry 2 symbol must be a string" in caplog.text
