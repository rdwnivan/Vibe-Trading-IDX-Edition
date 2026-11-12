"""Synthetic unavailable-data diagnostics at the personal research boundary."""

from copy import deepcopy
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
def acquisition(monkeypatch):
    frame = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 0.0},
        index=pd.date_range("2026-09-01", periods=21),
    )
    data = {
        "BBCA.JK": frame,
        "BBRI.JK": pd.DataFrame(),
        "_provenance": {
            "BBCA.JK": {
                "source": "yahoo",
                "quote_currency": "IDR",
                "exchange_timezone": "Asia/Jakarta",
                "interval": "1D",
                "volume_unit": "shares",
                "adjustment": "unknown",
            }
        },
    }
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: data)
    return data


def research(codes=None):
    return json.loads(
        idx_research_tool.IDXResearchTool().execute(
            codes=codes if codes is not None else ["BBCA.JK", "BBRI.JK"],
            lookback=20,
            end_date="2026-10-01",
        )
    )


@pytest.mark.parametrize("container", [[], ["private-value"], "private-value", 17, False])
def test_non_object_diagnostics_container_preserves_partial_result(acquisition, container, caplog):
    acquisition["_diagnostics"] = container
    original = acquisition["BBCA.JK"].copy(deep=True)

    with caplog.at_level(logging.WARNING):
        result = research()

    assert result["status"] == "partial"
    assert result["items"][0]["analysis"]["latest_close"] == 105.0
    assert result["items"][0]["volume_coverage"]["zero_bar_count"] == 20
    assert result["items"][1] == {
        "symbol": "BBRI.JK",
        "status": "unavailable",
        "provenance": None,
        "reason": "no_data_or_source_failure",
        "diagnostics": None,
    }
    assert "invalid acquisition diagnostics for BBRI.JK" in caplog.text
    assert "private-value" not in json.dumps(result) + caplog.text
    assert acquisition["_diagnostics"] is container
    pd.testing.assert_frame_equal(acquisition["BBCA.JK"], original)


@pytest.mark.parametrize("entry", [[], ["private-value"], "private-value", 17, False, float("nan"), pd.DataFrame()])
def test_non_object_symbol_diagnostics_are_not_returned(acquisition, entry, caplog):
    acquisition["_diagnostics"] = {"BBRI.JK": entry}

    with caplog.at_level(logging.WARNING):
        result = research()

    assert result["status"] == "partial"
    assert result["items"][1]["diagnostics"] is None
    assert result["items"][1]["reason"] == "no_data_or_source_failure"
    assert "quality_issue" not in result["items"][1]
    assert "invalid acquisition diagnostics for BBRI.JK" in caplog.text
    assert "private-value" not in json.dumps(result) + caplog.text
    assert acquisition["_diagnostics"]["BBRI.JK"] is entry


@pytest.mark.parametrize("diagnostics", [None, {}, {"BBRI.JK": None}])
def test_absent_diagnostics_remain_unknown_without_quality_rejection(acquisition, diagnostics, caplog):
    acquisition["_diagnostics"] = diagnostics

    result = research()

    assert result["status"] == "partial"
    assert result["items"][1]["diagnostics"] is None
    assert "quality_issue" not in result["items"][1]
    assert "invalid acquisition diagnostics" not in caplog.text


def test_missing_diagnostics_key_keeps_all_empty_result_unavailable(acquisition):
    result = research(["BBRI.JK", "TLKM.JK"])

    assert result["ok"] is True
    assert result["status"] == "unavailable"
    assert result["items"][0]["diagnostics"] is None
    assert result["items"][1]["diagnostics"] is None
    assert result["backtest_enabled"] is False


def test_malformed_diagnostics_keeps_all_empty_result_unavailable(acquisition, caplog):
    acquisition["_diagnostics"] = ["private-value"]

    result = research(["BBRI.JK", "TLKM.JK"])

    assert result["ok"] is True
    assert result["status"] == "unavailable"
    assert result["items"][0]["diagnostics"] is None
    assert result["items"][1]["diagnostics"] is None
    assert "invalid acquisition diagnostics for BBRI.JK" in caplog.text
    assert "invalid acquisition diagnostics for TLKM.JK" in caplog.text
    assert "private-value" not in json.dumps(result) + caplog.text


def test_healthy_observation_does_not_consume_unavailable_diagnostics(acquisition, caplog):
    acquisition["_diagnostics"] = ["private-value"]

    result = research(["BBCA.JK"])

    assert result["status"] == "ok"
    assert "diagnostics" not in result["items"][0]
    assert "invalid acquisition diagnostics" not in caplog.text
    assert "private-value" not in json.dumps(result)


def test_valid_diagnostics_neighbor_keeps_attempt_order_and_recovery(acquisition):
    valid = {
        "attempts": [{"source": "yahoo", "reason": "fetch_failed"}, {"source": "yfinance", "reason": "no_data"}],
        "recovery": "Check symbol, venue and requested date range.",
    }
    acquisition["_diagnostics"] = {"BBRI.JK": ["private-value"], "TLKM.JK": valid}
    original = deepcopy(acquisition["_diagnostics"])

    result = research(["BBCA.JK", "BBRI.JK", "TLKM.JK"])

    assert result["status"] == "partial"
    assert "diagnostics" not in result["items"][0]
    assert result["items"][1]["diagnostics"] is None
    assert result["items"][2]["diagnostics"] == valid
    assert acquisition["_diagnostics"] == original


@pytest.mark.parametrize("diagnostics", [False, {"BBRI.JK": "private-value"}])
def test_http_malformed_diagnostics_returns_partial_json(acquisition, diagnostics):
    acquisition["_diagnostics"] = diagnostics
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
    assert response.json()["status"] == "partial"
    assert response.json()["items"][0]["status"] == "ok"
    assert response.json()["items"][1]["diagnostics"] is None


@pytest.mark.parametrize("diagnostics", [False, {"BBRI.JK": "private-value"}])
def test_cli_malformed_diagnostics_emits_partial_json_and_exit_two(acquisition, diagnostics, monkeypatch, capsys):
    acquisition["_diagnostics"] = diagnostics
    monkeypatch.setattr(
        sys,
        "argv",
        ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"],
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][1]["diagnostics"] is None


@pytest.fixture(params=["nan", "infinity", "frame", "set", "invalid_key", "cycle", "too_deep"])
def unserializable_diagnostics(request):
    """Synthetic nested objects; no provider response or private data."""
    value = {"attempts": [{"source": "yahoo", "reason": "fetch_failed"}], "recovery": "synthetic-marker"}
    malformed = {
        "nan": float("nan"),
        "infinity": float("inf"),
        "frame": pd.DataFrame({"value": [1]}),
        "set": {"synthetic-marker"},
        "invalid_key": {("synthetic-marker",): "value"},
    }
    if request.param == "too_deep":
        nested = None
        # Python 3.12's C JSON encoder has a separate recursion bound;
        # the Python recursion limit alone does not force serialization failure.
        for _ in range(10_000):
            nested = [nested]
        value["extra"] = nested
    else:
        value["extra"] = value if request.param == "cycle" else malformed[request.param]
    return value


def test_nested_non_json_diagnostics_preserve_healthy_and_valid_neighbors(
    acquisition, unserializable_diagnostics, caplog
):
    valid = {
        "attempts": [{"source": "yahoo", "reason": "fetch_failed"}, {"source": "yfinance", "reason": "no_data"}],
        "recovery": "Check requested date range.",
        "extra": {"unknown": None, "zero": 0, "flag": False},
    }
    acquisition["_diagnostics"] = {"BBRI.JK": unserializable_diagnostics, "TLKM.JK": valid}
    original_frame = acquisition["BBCA.JK"].copy(deep=True)
    original_valid = deepcopy(valid)

    with caplog.at_level(logging.WARNING):
        result = research(["BBCA.JK", "BBRI.JK", "TLKM.JK"])

    assert result["status"] == "partial"
    assert result["backtest_enabled"] is False
    assert result["items"][0]["analysis"]["latest_close"] == 105.0
    assert result["items"][0]["volume_coverage"]["zero_bar_count"] == 20
    assert result["items"][1] == {
        "symbol": "BBRI.JK",
        "status": "unavailable",
        "provenance": None,
        "reason": "no_data_or_source_failure",
        "diagnostics": None,
    }
    assert result["items"][2]["diagnostics"] == original_valid
    assert valid == original_valid
    assert acquisition["_diagnostics"]["BBRI.JK"] is unserializable_diagnostics
    assert unserializable_diagnostics["recovery"] == "synthetic-marker"
    assert "invalid acquisition diagnostics for BBRI.JK" in caplog.text
    assert "synthetic-marker" not in json.dumps(result) + caplog.text
    pd.testing.assert_frame_equal(acquisition["BBCA.JK"], original_frame)


def test_http_nested_non_json_diagnostics_return_partial_json(acquisition, unserializable_diagnostics):
    acquisition["_diagnostics"] = {"BBRI.JK": unserializable_diagnostics}
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
    assert response.json()["status"] == "partial"
    assert response.json()["items"][0]["status"] == "ok"
    assert response.json()["items"][1]["diagnostics"] is None


def test_cli_nested_non_json_diagnostics_emit_json_and_exit_two(
    acquisition, unserializable_diagnostics, monkeypatch, capsys
):
    acquisition["_diagnostics"] = {"BBRI.JK": unserializable_diagnostics}
    monkeypatch.setattr(
        sys,
        "argv",
        ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"],
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][1]["diagnostics"] is None


def test_all_empty_observations_with_nested_non_json_diagnostics_remain_unavailable(acquisition, caplog):
    acquisition["_diagnostics"] = {"BBRI.JK": {"attempts": [{"reason": float("nan")}]}}

    result = research(["BBRI.JK", "TLKM.JK"])

    assert result["ok"] is True
    assert result["status"] == "unavailable"
    assert result["items"][0]["diagnostics"] is None
    assert result["items"][1]["diagnostics"] is None
    assert "invalid acquisition diagnostics for BBRI.JK" in caplog.text
    assert "invalid acquisition diagnostics for TLKM.JK" not in caplog.text


def test_healthy_observation_ignores_nested_non_json_diagnostics(acquisition, caplog):
    acquisition["_diagnostics"] = {"BBCA.JK": {"attempts": [{"reason": float("nan")}]}}

    result = research(["BBCA.JK"])

    assert result["status"] == "ok"
    assert "diagnostics" not in result["items"][0]
    assert "invalid acquisition diagnostics" not in caplog.text
