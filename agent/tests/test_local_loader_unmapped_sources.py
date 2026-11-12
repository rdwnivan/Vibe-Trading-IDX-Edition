"""Distinguish an unusable source list from a valid index without observations."""

import pandas as pd
import pytest
import yaml

from backtest.loaders import local_loader
from backtest.loaders.registry import get_loader_cls_with_fallback
from src.market_data import fetch_market_data


ERROR = "local loader: nonempty sources must define at least one nonblank string symbol"
UNMAPPED = [
    pytest.param([None, False, 42, "SYNTHETIC_PRIVATE_MARKER"], id="non-mappings"),
    pytest.param([{"symbol": None}, {"symbol": 600519}, {"symbol": ["SYNTHETIC_PRIVATE_MARKER"]}], id="non-string"),
    pytest.param([{}, {"symbol": ""}, {"symbol": " \t"}], id="absent-blank"),
    pytest.param([None, {"symbol": False}, {}, {"symbol": " "}], id="mixed-unassigned"),
]


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
    return {"sources": [{"symbol": symbol, "path": str(bars)} for symbol in ["BBCA.JK", "AAPL.US"]]}


@pytest.mark.parametrize("entries", UNMAPPED)
@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_nonempty_unmapped_list_rejects_repeated_fetch_and_recovers(
    config_path, valid_document, entries, symbol, caplog
):
    config_path.write_text(yaml.safe_dump({"sources": entries}), encoding="utf-8")
    loader = local_loader.DataLoader()
    # Availability remains the existing declaration check, not reader validation.
    assert loader.is_available() is True
    assert get_loader_cls_with_fallback("local") is local_loader.DataLoader
    with pytest.raises(ValueError, match=f"^{ERROR}$"):
        loader.fetch([symbol], "2026-09-01", "2026-09-03")
    with pytest.raises(ValueError, match=f"^{ERROR}$"):
        loader.fetch([symbol], "2026-09-01", "2026-09-03")
    config_path.write_text(yaml.safe_dump(valid_document), encoding="utf-8")
    assert loader.fetch([symbol], "2026-09-01", "2026-09-03")[symbol]["close"].tolist() == [105, 105]
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text


@pytest.mark.parametrize("entries", UNMAPPED)
@pytest.mark.parametrize("resolved", [True, False])
def test_unmapped_list_is_fetch_failure_without_network_fallback(config_path, entries, resolved, caplog):
    config_path.write_text(yaml.safe_dump({"sources": entries}), encoding="utf-8")

    def resolver(source):
        assert source == "local", "explicit local must not resolve a network source"
        return get_loader_cls_with_fallback(source) if resolved else local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK", "AAPL.US"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )
    expected = [{"source": "local", "reason": "fetch_failed"}]
    assert result["_diagnostics"]["BBCA.JK"]["attempts"] == expected
    assert result["_diagnostics"]["AAPL.US"]["attempts"] == expected
    assert "BBCA.JK" not in result and "AAPL.US" not in result
    assert ERROR in caplog.text
    assert "SYNTHETIC_PRIVATE_MARKER" not in caplog.text


@pytest.mark.parametrize("document", [None, {}, {"sources": []}])
def test_absent_or_empty_configuration_keeps_direct_omission(config_path, document):
    if document is not None:
        config_path.write_text(yaml.safe_dump(document), encoding="utf-8")
    loader = local_loader.DataLoader()
    assert loader.is_available() is False
    assert loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03") == {}
    assert loader.fetch(["BBCA.JK", "AAPL.US"], "2026-09-01", "2026-09-03") == {}


@pytest.mark.parametrize("resolved", [True, False])
def test_valid_index_preserves_unconfigured_empty_failed_and_healthy_outcomes(
    config_path, valid_document, tmp_path, resolved, caplog
):
    empty = tmp_path / "empty.csv"
    empty.write_text("date,open,high,low,close,volume\n", encoding="utf-8")
    entries = [
        None,
        {"symbol": False},
        {},
        {"symbol": " "},
        *valid_document["sources"],
        {"symbol": "TLKM.JK", "path": str(empty)},
        {"symbol": "BMRI.JK", "path": str(tmp_path / "absent.csv")},
        {"symbol": "ASII.JK", "path": str(empty), "columns": {"date": "missing"}},
    ]
    config_path.write_text(yaml.safe_dump({"sources": entries}), encoding="utf-8")

    def resolver(source):
        assert source == "local"
        return get_loader_cls_with_fallback(source) if resolved else local_loader.DataLoader

    result = fetch_market_data(
        codes=["BBCA.JK", "AAPL.US", "ANTM.JK", "MSFT.US", "TLKM.JK", "BMRI.JK", "ASII.JK"],
        start_date="2026-09-01",
        end_date="2026-09-03",
        source="local",
        include_provenance=True,
        loader_resolver=resolver,
    )
    assert result["BBCA.JK"][0]["close"] == 105
    assert result["AAPL.US"][0]["close"] == 105
    assert result["BBCA.JK"][0]["volume"] == 0
    assert result["BBCA.JK"][1]["volume"] is None
    assert result["_provenance"]["BBCA.JK"]["source"] == "local"
    assert result["_provenance"]["AAPL.US"]["source"] == "local"
    no_data = [{"source": "local", "reason": "no_data"}]
    failed = [{"source": "local", "reason": "fetch_failed"}]
    assert result["_diagnostics"]["ANTM.JK"]["attempts"] == no_data
    assert result["_diagnostics"]["MSFT.US"]["attempts"] == no_data
    assert result["_diagnostics"]["TLKM.JK"]["attempts"] == no_data
    assert result["_diagnostics"]["BMRI.JK"]["attempts"] == failed
    assert result["_diagnostics"]["ASII.JK"]["attempts"] == failed
    assert "sources entry 1 must be a mapping" in caplog.text
    assert "sources entry 2 symbol must be a string" in caplog.text


@pytest.mark.parametrize("symbol", ["BBCA.JK", "AAPL.US"])
def test_unmapped_list_cannot_use_or_modify_positive_cache(config_path, valid_document, tmp_path, monkeypatch, symbol):
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE", "1")
    cache = tmp_path / "cache"
    monkeypatch.setenv("VIBE_TRADING_DATA_CACHE_ROOT", str(cache))
    valid = yaml.safe_dump(valid_document)
    config_path.write_text(valid, encoding="utf-8")
    snapshot = local_loader.DataLoader()
    first = snapshot.fetch([symbol], "2026-09-01", "2026-09-03")
    before = {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()}
    assert before, "exercise a populated persistent cache"
    config_path.write_text("sources: [{symbol: null}]", encoding="utf-8")
    failed = local_loader.DataLoader()
    with pytest.raises(ValueError, match=f"^{ERROR}$"):
        failed.fetch([symbol], "2026-09-01", "2026-09-03")
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged source must reuse positive cache")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    # A successfully loaded instance retains its existing in-memory snapshot.
    pd.testing.assert_frame_equal(first[symbol], snapshot.fetch([symbol], "2026-09-01", "2026-09-03")[symbol])
    config_path.write_text(valid, encoding="utf-8")
    restored = failed.fetch([symbol], "2026-09-01", "2026-09-03")
    pd.testing.assert_frame_equal(first[symbol], restored[symbol])
    assert {p: p.read_bytes() for p in cache.rglob("*.*") if p.is_file()} == before
