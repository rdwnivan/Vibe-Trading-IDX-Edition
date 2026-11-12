"""Local bridge document shape is checked before indexing or cache lookup."""

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


@pytest.mark.parametrize(
    "document",
    [
        False,
        True,
        0,
        42,
        0.0,
        1.5,
        float("nan"),
        "",
        "SYNTHETIC_PRIVATE_MARKER",
        [],
        [{"private": "SYNTHETIC_PRIVATE_MARKER"}],
        date(2026, 9, 1),
    ],
)
@pytest.mark.parametrize("surface", ["availability", "fetch", "resolver"])
def test_non_mapping_document_raises_specific_sanitized_error(config_path, document, surface):
    config_path.write_text(yaml.safe_dump(document), encoding="utf-8")
    loader = local_loader.DataLoader()
    calls = {
        "availability": loader.is_available,
        "fetch": lambda: loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03"),
        "resolver": lambda: get_loader_cls_with_fallback("local"),
    }
    with pytest.raises(ValueError, match="^local loader: configuration document must be a mapping$"):
        calls[surface]()


@pytest.mark.parametrize("content", ["", "# empty document\n", "null", "~", "{}", "annotation: allowed", "sources: []"])
def test_empty_or_mapping_without_sources_keeps_existing_behavior(config_path, content):
    config_path.write_text(content, encoding="utf-8")
    loader = local_loader.DataLoader()
    assert loader.is_available() is False
    assert loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03") == {}


def test_absent_document_keeps_existing_behavior(config_path):
    assert not config_path.exists()
    loader = local_loader.DataLoader()
    assert loader.is_available() is False
    assert loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03") == {}


def test_rejected_document_can_be_corrected_on_same_instance(config_path, tmp_path):
    config_path.write_text("false", encoding="utf-8")
    loader = local_loader.DataLoader()
    with pytest.raises(ValueError, match="configuration document must be a mapping"):
        loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")
    path = tmp_path / "bars.csv"
    path.write_text(
        "date,open,high,low,close,volume\n2026-09-01,100,110,90,105,0\n2026-09-02,100,110,90,105,\n",
        encoding="utf-8",
    )
    config_path.write_text(yaml.safe_dump({"sources": [{"symbol": "BBCA.JK", "path": str(path)}]}), encoding="utf-8")
    assert loader.fetch(["BBCA.JK"], "2026-09-01", "2026-09-03")["BBCA.JK"]["close"].tolist() == [105, 105]


@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_bad_document_is_rejected_before_positive_cache_and_cache_remains_usable(
    config_path,
    tmp_path,
    monkeypatch,
    symbol,
):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    cache = tmp_path / "cache"
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(cache))
    path = tmp_path / "bars.csv"
    path.write_text(
        "date,open,high,low,close,volume\n2026-09-01,100,110,90,105,0\n2026-09-02,100,110,90,105,\n",
        encoding="utf-8",
    )
    valid = yaml.safe_dump({"sources": [{"symbol": symbol, "path": str(path)}]})
    config_path.write_text(valid, encoding="utf-8")
    first = local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    before = {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()}
    assert before, "exercise a populated cache"
    config_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="configuration document must be a mapping"):
        local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before
    config_path.write_text(valid, encoding="utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("restored unchanged source must reuse positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    restored = local_loader.DataLoader().fetch([symbol], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(restored[symbol], first[symbol])
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before


@pytest.mark.parametrize("resolve", [True, False])
def test_malformed_document_is_source_failure_without_network_fallback(config_path, resolve, caplog):
    config_path.write_text("false", encoding="utf-8")

    def resolver(source):
        assert source == "local", "explicit local must not resolve network sources"
        return get_loader_cls_with_fallback(source) if resolve else local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == [
        {"source": "local", "reason": "source_unavailable" if resolve else "fetch_failed"}
    ]
    assert "BBCA.JK" not in result
