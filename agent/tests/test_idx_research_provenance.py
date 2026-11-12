"""Synthetic acquisition/provenance shape failures at the shared research boundary."""

import json
import logging
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from src.api.idx_research_routes import register_idx_research_routes
from src.tools import idx_research_tool


@pytest.fixture
def observation(monkeypatch):
    """Supply frames at the acquisition boundary without provider or account I/O."""
    frame = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000.0},
        index=pd.date_range("2026-09-01", periods=21),
    )
    provenance = {
        "source": "yahoo",
        "quote_currency": "IDR",
        "exchange_timezone": "Asia/Jakarta",
        "interval": "1D",
        "volume_unit": "shares",
        "adjustment": "unknown",
        "freshness": "not_evaluated",
    }
    data = {"BBCA.JK": frame, "_provenance": {"BBCA.JK": provenance}}
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: data)
    return data, frame, provenance


def research():
    return json.loads(
        idx_research_tool.IDXResearchTool().execute(
            codes=["BBCA.JK"],
            lookback=20,
            end_date="2026-10-01",
        )
    )


@pytest.mark.parametrize("field", ["symbol", "market", "exchange"])
@pytest.mark.parametrize("value", [None, "", "synthetic-private-identity", 17, False, [], {}])
def test_conflicting_declared_identity_rejects_only_that_observation(observation, field, value, caplog):
    _, frame, provenance = observation
    provenance[field] = value
    original_frame = frame.copy(deep=True)
    original_provenance = json.loads(json.dumps(provenance))

    with caplog.at_level(logging.WARNING):
        result = research()

    item = result["items"][0]
    assert result["status"] == "unavailable"
    assert item["reason"] == "invalid_data_or_metadata"
    assert item["quality_issue"] == {"code": "instrument_identity"}
    assert "bars" not in item
    assert "analysis" not in item
    assert "instrument_identity" in caplog.text
    assert "synthetic-private-identity" not in caplog.text
    assert provenance == item["provenance"] == original_provenance
    pd.testing.assert_frame_equal(frame, original_frame)


@pytest.mark.parametrize(
    "declaration",
    [
        {},
        {"symbol": "BBCA.JK"},
        {"market": "id_equity"},
        {"exchange": "IDX"},
        {"symbol": "BBCA.JK", "market": "id_equity"},
        {"symbol": "BBCA.JK", "exchange": "IDX"},
        {"market": "id_equity", "exchange": "IDX"},
        {"symbol": "BBCA.JK", "market": "id_equity", "exchange": "IDX"},
    ],
)
def test_matching_or_absent_identity_preserves_legacy_observations(observation, declaration):
    _, _, provenance = observation
    provenance.update(declaration)

    item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["analysis"]["latest_close"] == 105.0
    assert item["provenance"] == provenance
    assert item["analysis"]["read_identity"]["provenance"] == provenance


@pytest.mark.parametrize(
    "field,value",
    [("symbol", "BBRI.JK"), ("market", "us_equity"), ("exchange", "NYSE"), ("symbol", "bbca.jk")],
)
def test_http_conflicting_identity_preserves_healthy_peer_with_one_acquisition(observation, monkeypatch, field, value):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance, symbol="BBRI.JK", market="id_equity", exchange="IDX")
    provenance[field] = value
    calls = []

    def acquire(**kwargs):
        calls.append(kwargs)
        return data

    monkeypatch.setattr(idx_research_tool, "fetch_market_data", acquire)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "instrument_identity"}
    assert result["items"][1]["status"] == "ok"
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert len(calls) == 1
    assert result["backtest_enabled"] is False


def test_cli_conflicting_identity_emits_partial_json_and_exit_two(observation, monkeypatch, capsys):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance, symbol="BBRI.JK")
    provenance["symbol"] = "BBRI.JK"
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "instrument_identity"}
    assert result["items"][1]["status"] == "ok"


def test_empty_symbol_keeps_acquisition_reason_despite_conflicting_identity(observation):
    data, _, provenance = observation
    data["BBCA.JK"] = pd.DataFrame()
    provenance.update(symbol="BBRI.JK", market="us_equity", exchange="NYSE")

    item = research()["items"][0]

    assert item["reason"] == "no_data_or_source_failure"
    assert "quality_issue" not in item


@pytest.mark.parametrize("container", [None, [], ["private-value"], "private-value", 17, False])
def test_malformed_provenance_container_rejects_observation_without_crashing(observation, container, caplog):
    data, frame, _ = observation
    data["_provenance"] = container
    original = frame.copy(deep=True)

    with caplog.at_level(logging.WARNING):
        result = research()

    assert result["status"] == "unavailable"
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert result["items"][0]["provenance"] is None
    assert "private-value" not in json.dumps(result) + caplog.text
    assert "currency_declaration" in caplog.text
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("payload", [None, [], "private-value", 17, False])
def test_non_object_acquisition_returns_structured_error(monkeypatch, payload, caplog):
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: payload)

    with caplog.at_level(logging.WARNING):
        result = research()

    assert result == {"ok": False, "error": "market data acquisition failed; retry later or check loader configuration"}
    assert "acquisition failed (TypeError)" in caplog.text
    assert "private-value" not in json.dumps(result) + caplog.text


def test_http_malformed_provenance_preserves_empty_symbol_and_structured_rejection(observation):
    data, _, _ = observation
    data["_provenance"] = None
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "unavailable"
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert result["items"][1]["reason"] == "no_data_or_source_failure"
    assert "quality_issue" not in result["items"][1]
    assert result["backtest_enabled"] is False


def test_cli_malformed_provenance_emits_json_and_exit_two(observation, monkeypatch, capsys):
    data, _, _ = observation
    data["_provenance"] = ["private-value"]
    monkeypatch.setattr(sys, "argv", ["idx_research", "BBCA.JK", "--lookback", "20", "--end-date", "2026-10-01"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert "private-value" not in json.dumps(result)


def test_http_non_object_acquisition_returns_bad_request(monkeypatch):
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: None)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post("/api/research/idx", json={"codes": ["BBCA.JK"]})

    assert response.status_code == 400
    assert response.json() == {
        "ok": False,
        "error": "market data acquisition failed; retry later or check loader configuration",
    }


def test_cli_non_object_acquisition_returns_json_and_exit_two(monkeypatch, capsys):
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: [])
    monkeypatch.setattr(sys, "argv", ["idx_research", "BBCA.JK"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    assert exit_info.value.code == 2
    assert json.loads(capsys.readouterr().out) == {
        "ok": False,
        "error": "market data acquisition failed; retry later or check loader configuration",
    }


@pytest.mark.parametrize("entry", [None, [], ["private-value"], "private-value", 17, False])
def test_invalid_symbol_provenance_preserves_healthy_neighbor(observation, entry):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    data["_provenance"]["BBCA.JK"] = entry

    result = json.loads(
        idx_research_tool.IDXResearchTool().execute(
            codes=["BBCA.JK", "BBRI.JK"],
            lookback=20,
            end_date="2026-10-01",
        )
    )

    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert result["items"][0]["provenance"] is None
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert result["items"][1]["provenance"] == provenance
    assert "private-value" not in json.dumps(result)


@pytest.mark.parametrize("missing_map", [False, True])
def test_missing_provenance_is_not_reconstructed_from_frame_attributes(observation, missing_map):
    data, frame, provenance = observation
    frame.attrs.update(provenance)
    data["_provenance"] = {}
    if missing_map:
        del data["_provenance"]

    item = research()["items"][0]

    assert item["quality_issue"] == {"code": "currency_declaration"}
    assert item["provenance"] is None


@pytest.fixture(params=["nan", "infinity", "set", "frame", "key", "cycle", "deep"])
def unserializable_metadata(request):
    """Synthetic metadata; never a captured provider payload."""
    cycle = {"marker": "private-value"}
    cycle["self"] = cycle
    deep = {"marker": "private-value"}
    for _ in range(10_000):
        deep = {"nested": deep}
    return {
        "nan": {"private-value": float("nan")},
        "infinity": {"private-value": float("inf")},
        "set": {"private-value": {1, 2}},
        "frame": {"private-value": pd.DataFrame()},
        "key": {("private-value",): 1},
        "cycle": cycle,
        "deep": deep,
    }[request.param]


@pytest.fixture
def watchlist(observation):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    return data, frame, provenance


@pytest.mark.parametrize("has_bars", [True, False], ids=["with-bars", "without-bars"])
def test_non_json_provenance_is_isolated_per_symbol(watchlist, unserializable_metadata, has_bars, caplog):
    data, frame, provenance = watchlist
    provenance["data_quality"] = unserializable_metadata
    original = frame.copy(deep=True)
    if not has_bars:
        data["BBCA.JK"] = pd.DataFrame()

    with caplog.at_level(logging.WARNING):
        result = json.loads(
            idx_research_tool.IDXResearchTool().execute(
                codes=["BBCA.JK", "BBRI.JK"], lookback=20, end_date="2026-10-01"
            )
        )

    assert result["ok"] is True
    assert result["status"] == "partial"
    rejected, healthy = result["items"]
    assert rejected["provenance"] is None
    assert rejected["status"] == "unavailable"
    if has_bars:
        assert rejected["quality_issue"] == {"code": "currency_declaration"}
        assert rejected["reason"] == "invalid_data_or_metadata"
    else:
        assert rejected["reason"] == "no_data_or_source_failure"
        assert "quality_issue" not in rejected
    assert healthy["status"] == "ok"
    assert healthy["analysis"]["latest_close"] == 105.0
    assert healthy["provenance"]["source"] == "yahoo"
    assert result["backtest_enabled"] is False
    assert "invalid acquisition provenance for BBCA.JK" in caplog.text
    assert "private-value" not in json.dumps(result) + caplog.text
    assert provenance["data_quality"] is unserializable_metadata
    assert data["_provenance"]["BBCA.JK"] is provenance
    pd.testing.assert_frame_equal(frame, original)


def test_http_non_json_provenance_keeps_healthy_result(watchlist, unserializable_metadata):
    _, _, provenance = watchlist
    provenance["data_quality"] = unserializable_metadata
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["provenance"] is None
    assert result["items"][0]["quality_issue"] == {"code": "currency_declaration"}
    assert result["items"][1]["analysis"]["latest_close"] == 105.0


def test_cli_non_json_provenance_emits_partial_json(watchlist, unserializable_metadata, monkeypatch, capsys):
    _, _, provenance = watchlist
    provenance["data_quality"] = unserializable_metadata
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["provenance"] is None
    assert result["items"][1]["analysis"]["latest_close"] == 105.0


@pytest.mark.parametrize("has_bars", [True, False], ids=["with-bars", "without-bars"])
def test_json_provenance_keeps_nested_values_and_attempt_order(watchlist, has_bars):
    data, _, provenance = watchlist
    provenance.update(
        data_quality={"note": None, "counts": [0, 1], "label": "sintetis"},
        attempts=[{"source": "yahoo", "reason": "fetch_failed"}, {"source": "yfinance", "reason": "ok"}],
    )
    if not has_bars:
        data["BBCA.JK"] = pd.DataFrame()

    result = research()

    assert result["items"][0]["provenance"] == provenance
    assert data["_provenance"]["BBCA.JK"] is provenance


def test_non_json_provenance_with_all_data_empty_remains_unavailable(watchlist, unserializable_metadata, caplog):
    data, _, provenance = watchlist
    provenance["data_quality"] = unserializable_metadata
    data["BBCA.JK"] = pd.DataFrame()
    data["BBRI.JK"] = pd.DataFrame()

    result = json.loads(
        idx_research_tool.IDXResearchTool().execute(codes=["BBCA.JK", "BBRI.JK"], lookback=20, end_date="2026-10-01")
    )

    assert result["ok"] is True
    assert result["status"] == "unavailable"
    assert result["items"][0]["provenance"] is None
    assert result["items"][0]["reason"] == "no_data_or_source_failure"
    assert "quality_issue" not in result["items"][0]
    assert result["items"][1]["provenance"] == data["_provenance"]["BBRI.JK"]
    assert "private-value" not in json.dumps(result) + caplog.text


def test_valid_nested_provenance_reaches_analysis_identity(watchlist):
    _, _, provenance = watchlist
    provenance["data_quality"] = {"missing": None, "zero": 0, "note": "sintetis"}

    result = research()

    assert result["status"] == "ok"
    assert result["items"][0]["analysis"]["read_identity"]["provenance"] == provenance
