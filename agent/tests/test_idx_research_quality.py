"""Synthetic observations for the personal research boundary, not exchange data."""

import json
import logging
import sys
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
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


@pytest.mark.parametrize(
    "key,value,expected_code",
    [
        ("quote_currency", "USD", "currency_declaration"),
        ("exchange_timezone", "UTC", "session_timezone"),
        ("interval", "1W", "daily_interval"),
        ("volume_unit", "lots", "share_volume_unit"),
        ("adjustment", None, "adjustment_declaration"),
    ],
)
def test_rejection_identifies_metadata_contract(observation, key, value, expected_code, caplog):
    _, _, provenance = observation
    provenance[key] = value

    with caplog.at_level(logging.WARNING):
        item = research()["items"][0]

    assert item["reason"] == "invalid_data_or_metadata"
    assert item["quality_issue"] == {"code": expected_code}
    assert expected_code in caplog.text
    assert "bars" not in item


@pytest.mark.parametrize(
    "dates,expected_code",
    [
        (pd.Index(range(21)), "unique_bar_dates"),
        (pd.DatetimeIndex(["2026-09-01"] * 21), "unique_bar_dates"),
        (pd.DatetimeIndex([pd.NaT] * 21), "unique_bar_dates"),
        (pd.date_range("2026-09-01", periods=21, tz="Asia/Jakarta"), "local_session_dates"),
        (pd.date_range("2026-09-01 12:00", periods=21), "local_session_dates"),
        (pd.date_range("2026-10-01", periods=21), "requested_date_window"),
        (pd.date_range("2026-08-01", periods=21), "requested_date_window"),
    ],
)
def test_rejection_identifies_date_contract(observation, dates, expected_code):
    _, frame, _ = observation
    frame.index = dates

    item = research()["items"][0]

    assert item["quality_issue"] == {"code": expected_code}
    assert "recency" not in item


@pytest.mark.parametrize(
    "column,value,expected_code",
    [("high", 95.0, "price_values"), ("open", float("nan"), "price_values"), ("volume", -1.0, "volume_values")],
)
def test_rejection_identifies_value_contract_before_display_tail(observation, column, value, expected_code):
    _, frame, _ = observation
    frame.loc[frame.index[0], column] = value

    item = research()["items"][0]

    assert item["quality_issue"] == {"code": expected_code}
    assert "analysis" not in item


def test_rejection_does_not_copy_raw_exception_into_diagnostic_or_log(observation, caplog):
    _, frame, _ = observation
    frame["volume"] = frame["volume"].astype(object)
    frame.loc[frame.index[0], "volume"] = "synthetic-private-value"

    with caplog.at_level(logging.WARNING):
        item = research()["items"][0]

    assert item["quality_issue"] == {"code": "volume_values"}
    assert "synthetic-private-value" not in json.dumps(item)
    assert "synthetic-private-value" not in caplog.text


@pytest.mark.parametrize("column,expected_code", [("open", "price_values"), ("volume", "volume_values")])
def test_missing_required_column_has_validation_diagnostic(observation, column, expected_code):
    data, frame, _ = observation
    data["BBCA.JK"] = frame.drop(columns=[column])

    item = research()["items"][0]

    assert item["quality_issue"] == {"code": expected_code}
    assert item["reason"] == "invalid_data_or_metadata"


def research():
    return json.loads(
        idx_research_tool.IDXResearchTool().execute(
            codes=["BBCA.JK"],
            lookback=20,
            end_date="2026-10-01",
        )
    )


@pytest.mark.parametrize("column", ["open", "high", "low", "close", "volume"])
@pytest.mark.parametrize("conflicting", [False, True])
def test_duplicate_required_columns_reject_observation_without_mutation(observation, column, conflicting, caplog):
    data, frame, _ = observation
    duplicate = frame[[column]].copy()
    if conflicting:
        duplicate.iloc[0, 0] = 7654321
    ambiguous = pd.concat([frame, duplicate], axis=1)
    data["BBCA.JK"] = ambiguous
    original = ambiguous.copy(deep=True)

    with caplog.at_level(logging.WARNING):
        item = research()["items"][0]

    expected_code = "volume_values" if column == "volume" else "price_values"
    assert item["status"] == "unavailable"
    assert item["reason"] == "invalid_data_or_metadata"
    assert item["quality_issue"] == {"code": expected_code}
    assert "bars" not in item
    assert "analysis" not in item
    assert "7654321" not in json.dumps(item) + caplog.text
    assert expected_code in caplog.text
    pd.testing.assert_frame_equal(ambiguous, original)


@pytest.mark.parametrize("symbol_first", [False, True])
def test_hierarchical_columns_are_rejected_without_guessing_a_symbol_level(observation, symbol_first):
    data, frame, _ = observation
    ambiguous = pd.concat({"BBCA.JK": frame}, axis=1)
    if not symbol_first:
        ambiguous.columns = ambiguous.columns.swaplevel()
    data["BBCA.JK"] = ambiguous
    original = ambiguous.copy(deep=True)

    item = research()["items"][0]

    assert item["status"] == "unavailable"
    assert item["quality_issue"] == {"code": "price_values"}
    assert "analysis" not in item
    pd.testing.assert_frame_equal(ambiguous, original)


def test_duplicate_unused_columns_do_not_reject_valid_ohlcv(observation):
    data, frame, _ = observation
    extra = pd.DataFrame({"unused": "not-an-observation"}, index=frame.index)
    data["BBCA.JK"] = pd.concat([frame, extra, extra], axis=1)
    original = data["BBCA.JK"].copy(deep=True)

    item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["analysis"]["latest_close"] == 105.0
    assert item["volume_coverage"]["available_bar_count"] == 20
    pd.testing.assert_frame_equal(data["BBCA.JK"], original)


@pytest.mark.parametrize("column", ["close", "volume", None])
def test_http_ambiguous_columns_keep_healthy_watchlist_peer(observation, column):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    data["BBCA.JK"] = (
        pd.concat([frame, frame[[column]]], axis=1)
        if column is not None
        else pd.concat({"BBCA.JK": frame}, axis=1).swaplevel(axis=1)
    )
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
    assert result["items"][0]["quality_issue"] == {"code": "volume_values" if column == "volume" else "price_values"}
    assert result["items"][1]["status"] == "ok"
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert result["backtest_enabled"] is False


@pytest.mark.parametrize("column", ["close", "volume", None])
def test_cli_ambiguous_columns_emit_partial_json_and_exit_two(observation, column, monkeypatch, capsys):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    data["BBCA.JK"] = (
        pd.concat([frame, frame[[column]]], axis=1)
        if column is not None
        else pd.concat({"BBCA.JK": frame}, axis=1).swaplevel(axis=1)
    )
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "volume_values" if column == "volume" else "price_values"}
    assert result["items"][1]["status"] == "ok"


@pytest.mark.parametrize(
    "column,expected_code",
    [
        ("open", "price_values"),
        ("high", "price_values"),
        ("low", "price_values"),
        ("close", "price_values"),
        ("volume", "volume_values"),
    ],
)
@pytest.mark.parametrize("scalar", [complex, np.complex64, np.complex128])
@pytest.mark.parametrize("imaginary", [0, 7])
def test_complex_ohlcv_is_rejected_before_display_tail(observation, column, expected_code, scalar, imaginary):
    _, frame, _ = observation
    frame[column] = frame[column].astype(object)
    # The oldest bar would disappear from the 20-bar analysis window.
    frame.loc[frame.index[0], column] = scalar(frame.loc[frame.index[0], column] + imaginary * 1j)
    original = frame.copy(deep=True)

    item = research()["items"][0]

    assert item["status"] == "unavailable"
    assert item["quality_issue"] == {"code": expected_code}
    assert "bars" not in item
    assert "analysis" not in item
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("column,expected_code", [("close", "price_values"), ("volume", "volume_values")])
def test_complex_column_is_rejected_without_lossy_conversion(observation, column, expected_code):
    _, frame, _ = observation
    frame[column] = frame[column].astype("complex128")

    item = research()["items"][0]

    assert item["status"] == "unavailable"
    assert item["quality_issue"] == {"code": expected_code}


def test_complex_volume_keeps_healthy_symbol_in_http_partial_result(observation, caplog):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame["volume"] = frame["volume"].astype(object)
    frame.loc[frame.index[-1], "volume"] = np.complex128(1000 + 1234567j)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client, caplog.at_level(logging.WARNING):
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "volume_values"}
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert "BBCA.JK (volume_values; ValueError)" in caplog.text
    assert "1234567" not in response.text + caplog.text
    assert result["backtest_enabled"] is False


def test_cli_complex_volume_returns_partial_json_and_exit_two(observation, monkeypatch, capsys):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame["volume"] = frame["volume"].astype(object)
    frame.loc[frame.index[0], "volume"] = np.complex128(1000 + 7j)
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "volume_values"}
    assert result["items"][1]["status"] == "ok"


@pytest.mark.parametrize(
    "volumes,expected",
    [
        ([1000.0] * 21, (20, 0, 0)),
        ([None] * 21, (0, 20, 0)),
        ([0.0] * 21, (20, 0, 20)),
        ([None] + [1000.0] * 18 + [0.0, None], (19, 1, 1)),
    ],
)
def test_volume_coverage_counts_only_analyzed_bars(observation, volumes, expected):
    _, frame, provenance = observation
    frame["volume"] = volumes
    original = frame.copy(deep=True)
    original_provenance = dict(provenance)

    item = research()["items"][0]

    available, missing, zero = expected
    assert item["status"] == "ok"
    assert item["volume_coverage"] == {
        "bar_count": 20,
        "available_bar_count": available,
        "missing_bar_count": missing,
        "zero_bar_count": zero,
    }
    assert item["volume_coverage"]["bar_count"] == item["analysis"]["read_identity"]["bar_count"]
    pd.testing.assert_frame_equal(frame, original)
    assert provenance == original_provenance


def test_volume_coverage_does_not_invent_bars_for_date_gaps(observation):
    data, frame, _ = observation
    frame["volume"] = pd.Series(0, index=frame.index, dtype="Int64")
    frame.loc[frame.index[-1], "volume"] = pd.NA
    data["BBCA.JK"] = frame.drop(frame.index[10]).iloc[::-1]

    item = research()["items"][0]

    assert item["volume_coverage"] == {
        "bar_count": 20,
        "available_bar_count": 19,
        "missing_bar_count": 1,
        "zero_bar_count": 19,
    }
    assert item["bars"][10]["date"] == "2026-09-12"
    assert item["bars"][-1]["volume"] is None
    assert item["analysis"]["indicators"]["volume"]["sma_20"] is None


def test_volume_coverage_uses_short_observation_count_instead_of_requested_limit(observation):
    data, frame, _ = observation
    data["BBCA.JK"] = frame.iloc[-1:].assign(volume=None)

    result = research()

    item = result["items"][0]
    assert result["lookback"] == 20
    assert item["volume_coverage"] == {
        "bar_count": 1,
        "available_bar_count": 0,
        "missing_bar_count": 1,
        "zero_bar_count": 0,
    }
    assert item["analysis"]["read_identity"]["bar_count"] == 1
    assert item["analysis"]["indicators"]["sma_20"] is None


def test_http_partial_keeps_volume_coverage_only_for_valid_observation(observation):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame.loc[frame.index[-1], "volume"] = float("nan")
    data["BBRI.JK"].loc[frame.index[0], "volume"] = -1
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK", "TLKM.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["volume_coverage"] == {
        "bar_count": 20,
        "available_bar_count": 19,
        "missing_bar_count": 1,
        "zero_bar_count": 0,
    }
    assert result["items"][1]["quality_issue"] == {"code": "volume_values"}
    assert "volume_coverage" not in result["items"][1]
    assert result["items"][2]["reason"] == "no_data_or_source_failure"
    assert "volume_coverage" not in result["items"][2]
    assert result["backtest_enabled"] is False


def test_cli_missing_volume_keeps_success_and_publishes_coverage(observation, monkeypatch, capsys):
    _, frame, _ = observation
    frame["volume"] = float("nan")
    monkeypatch.setattr(sys, "argv", ["idx_research", "BBCA.JK", "--lookback", "20", "--end-date", "2026-10-01"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 0
    assert result["status"] == "ok"
    assert result["items"][0]["volume_coverage"] == {
        "bar_count": 20,
        "available_bar_count": 0,
        "missing_bar_count": 20,
        "zero_bar_count": 0,
    }
    assert result["items"][0]["analysis"]["indicators"]["volume"]["latest"] is None


@pytest.mark.parametrize(
    "column,expected_code",
    [
        ("open", "price_values"),
        ("high", "price_values"),
        ("low", "price_values"),
        ("close", "price_values"),
        ("volume", "volume_values"),
    ],
)
@pytest.mark.parametrize("value", [True, False])
def test_boolean_ohlcv_is_rejected_before_display_tail(observation, column, expected_code, value):
    _, frame, _ = observation
    # Unit prices keep True inside OHLC bounds; bool is still not a price.
    frame.loc[:, ["open", "high", "low", "close"]] = 1.0
    frame[column] = frame[column].astype(object)
    frame.loc[frame.index[0], column] = value
    original = frame.copy(deep=True)

    item = research()["items"][0]

    assert item["status"] == "unavailable"
    assert item["quality_issue"] == {"code": expected_code}
    assert "bars" not in item
    assert "analysis" not in item
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("column,expected_code", [("high", "price_values"), ("volume", "volume_values")])
def test_numeric_overflow_rejects_only_defective_symbol_over_http(observation, column, expected_code, caplog):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame[column] = frame[column].astype(object)
    frame.loc[frame.index[0], column] = 10**400
    original = frame.copy(deep=True)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client, caplog.at_level(logging.WARNING):
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": expected_code}
    assert "bars" not in result["items"][0]
    assert result["items"][1]["status"] == "ok"
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert "IDX research rejected bars for BBCA.JK" in caplog.text
    assert str(10**400) not in response.text + caplog.text
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("dtype", ["bool", "boolean"])
def test_boolean_volume_column_is_not_interpreted_as_one_share(observation, dtype):
    _, frame, _ = observation
    frame["volume"] = pd.Series(True, index=frame.index, dtype=dtype)

    item = research()["items"][0]

    assert item["status"] == "unavailable"
    assert item["quality_issue"] == {"code": "volume_values"}


@pytest.mark.parametrize("dtype", ["int64", "float64", "Int64", "Float64"])
def test_numeric_dtypes_keep_prices_and_zero_volume(observation, dtype):
    data, frame, _ = observation
    data["BBCA.JK"] = frame.astype(dtype)
    data["BBCA.JK"].loc[frame.index[-1], "volume"] = 0

    item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["analysis"]["latest_close"] == 105.0
    assert item["bars"][-1]["volume"] == 0.0
    assert item["analysis"]["indicators"]["volume"]["latest"] == 0.0


def test_cli_numeric_overflow_emits_partial_json_and_exit_two(observation, monkeypatch, capsys):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame["volume"] = frame["volume"].astype(object)
    frame.loc[frame.index[0], "volume"] = 10**400
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "volume_values"}
    assert result["items"][1]["status"] == "ok"
    assert result["backtest_enabled"] is False


def test_finite_volume_with_overflowing_mean_is_rejected_per_symbol_over_http(observation, caplog):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    # Each input is finite; summing the 20-bar window exceeds float range.
    frame["volume"] = 1e308
    original = frame.copy(deep=True)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client, caplog.at_level(logging.WARNING):
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-01"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "indicator_calculation"}
    assert "bars" not in result["items"][0]
    assert "analysis" not in result["items"][0]
    assert result["items"][1]["status"] == "ok"
    assert result["items"][1]["analysis"]["latest_close"] == 105.0
    assert "BBCA.JK (indicator_calculation; ValueError)" in caplog.text
    assert "Out of range float" not in caplog.text
    assert "Infinity" not in response.text
    pd.testing.assert_frame_equal(frame, original)


def test_cli_overflowing_indicator_emits_partial_json_and_exit_two(observation, monkeypatch, capsys):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    frame["volume"] = 1e308
    monkeypatch.setattr(
        sys, "argv", ["idx_research", "BBCA.JK", "BBRI.JK", "--lookback", "20", "--end-date", "2026-10-01"]
    )

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    output = capsys.readouterr().out
    result = json.loads(output)
    assert exit_info.value.code == 2
    assert result["status"] == "partial"
    assert result["items"][0]["quality_issue"] == {"code": "indicator_calculation"}
    assert result["items"][1]["status"] == "ok"
    assert result["backtest_enabled"] is False
    assert "Infinity" not in output


@pytest.mark.parametrize("prices", [[1e155, 2e155] * 10 + [1e155], [1e308, 1e307] * 10 + [1e308]])
def test_finite_prices_with_nonfinite_indicators_are_unavailable(observation, prices):
    data, frame, _ = observation
    # Equal OHLC on each date is valid. Variance overflows for the first
    # sequence; the second also produces NaN in the existing calculations.
    data["BBCA.JK"] = frame.assign(open=prices, high=prices, low=prices, close=prices)
    original = data["BBCA.JK"].copy(deep=True)

    result = research()

    assert result["ok"] is True
    assert result["status"] == "unavailable"
    assert result["items"][0]["quality_issue"] == {"code": "indicator_calculation"}
    assert "bars" not in result["items"][0]
    assert "analysis" not in result["items"][0]
    pd.testing.assert_frame_equal(data["BBCA.JK"], original)


def test_large_finite_indicator_results_and_insufficient_history_nulls_remain_available(observation):
    _, frame, _ = observation
    frame["volume"] = 1e300

    item = research()["items"][0]

    assert item["status"] == "ok"
    assert item["analysis"]["indicators"]["volume"]["sma_20"] == pytest.approx(1e300)
    assert item["analysis"]["indicators"]["volume"]["ratio_20"] == pytest.approx(1.0)
    assert item["analysis"]["indicators"]["sma_50"] is None
    assert item["analysis"]["indicators"]["macd"] is None
    assert item["bars"][-1]["volume"] == 1e300
    assert "quality_issue" not in item


@pytest.mark.parametrize(
    "column,value",
    [
        ("high", 95.0),
        ("close", 0.0),
        ("open", float("nan")),
        ("high", float("inf")),
        ("volume", -1.0),
        ("volume", float("inf")),
    ],
)
def test_invalid_bar_outside_display_tail_rejects_entire_observation(observation, column, value, caplog):
    _, frame, _ = observation
    # The first of 21 bars is outside the requested 20-bar display tail.
    frame.loc[frame.index[0], column] = value

    with caplog.at_level(logging.WARNING):
        result = research()

    assert result["status"] == "unavailable"
    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert "bars" not in result["items"][0]
    assert "analysis" not in result["items"][0]
    assert "IDX research rejected bars for BBCA.JK" in caplog.text


@pytest.mark.parametrize(
    "key,value",
    [
        ("interval", "1W"),
        ("interval", None),
        ("volume_unit", "lots"),
        ("volume_unit", None),
    ],
)
def test_incompatible_or_missing_units_are_not_used_for_indicators(observation, key, value):
    _, _, provenance = observation
    provenance[key] = value

    result = research()

    assert result["status"] == "unavailable"
    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert result["items"][0]["provenance"][key] == value
    assert "analysis" not in result["items"][0]


@pytest.mark.parametrize("key", ["interval", "volume_unit"])
def test_absent_unit_metadata_is_not_inferred(observation, key):
    _, _, provenance = observation
    del provenance[key]

    result = research()

    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert key not in result["items"][0]["provenance"]


@pytest.mark.parametrize("adjustment", [None, "", "   ", True, ["split_dividend"]])
def test_missing_adjustment_declaration_rejects_observation(observation, adjustment, caplog):
    _, _, provenance = observation
    provenance["adjustment"] = adjustment

    with caplog.at_level(logging.WARNING):
        result = research()

    item = result["items"][0]
    assert item["status"] == "unavailable"
    assert item["reason"] == "invalid_data_or_metadata"
    assert item["provenance"]["adjustment"] == adjustment
    assert "analysis" not in item
    assert "bars" not in item
    assert "recency" not in item
    assert "IDX research rejected bars for BBCA.JK" in caplog.text


def test_absent_adjustment_is_not_inferred_from_source(observation):
    _, _, provenance = observation
    del provenance["adjustment"]

    result = research()

    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert "adjustment" not in result["items"][0]["provenance"]


@pytest.mark.parametrize(
    "adjustment,before,after,expected_sma",
    [
        ("unknown", 200.0, 100.0, 150.0),
        ("raw", 200.0, 100.0, 150.0),
        ("split", 100.0, 100.0, 100.0),
        ("split_dividend", 95.0, 100.0, 97.5),
    ],
)
def test_synthetic_event_prices_are_never_readjusted(observation, adjustment, before, after, expected_sma):
    data, frame, provenance = observation
    # Model a split-like jump or a dividend-adjusted level, not a real event.
    # Exactly ten bars at each level survive the 20-bar display boundary.
    frame.loc[:, ["open", "high", "low", "close"]] = before
    frame.loc[frame.index[-10:], ["open", "high", "low", "close"]] = after
    provenance["adjustment"] = adjustment
    original = frame.copy(deep=True)
    original_provenance = dict(provenance)

    result = research()

    item = result["items"][0]
    assert item["status"] == "ok"
    assert item["bars"][9]["close"] == before
    assert item["bars"][10]["close"] == after
    assert item["analysis"]["latest_close"] == after
    assert item["analysis"]["indicators"]["sma_20"] == expected_sma
    assert item["provenance"] == original_provenance
    assert item["analysis"]["read_identity"]["provenance"] == original_provenance
    assert result["calendar_completeness"] == "not_verified"
    assert result["backtest_enabled"] is False
    pd.testing.assert_frame_equal(data["BBCA.JK"], original)
    assert provenance == original_provenance


def test_valid_observation_is_trimmed_without_mutating_acquired_frame(observation):
    _, frame, provenance = observation
    original = frame.copy(deep=True)
    original_provenance = dict(provenance)

    result = research()

    item = result["items"][0]
    assert item["status"] == "ok"
    assert len(item["bars"]) == item["analysis"]["read_identity"]["bar_count"] == 20
    assert "quality_issue" not in item
    assert item["bars"][0]["date"] == "2026-09-02"
    pd.testing.assert_frame_equal(frame, original)
    assert provenance == original_provenance


def test_zero_and_missing_volume_and_date_gaps_remain_observed(observation):
    data, frame, _ = observation
    frame.loc[frame.index[-2], "volume"] = 0.0
    frame.loc[frame.index[-1], "volume"] = float("nan")
    data["BBCA.JK"] = frame.drop(frame.index[10]).iloc[::-1]

    result = research()

    item = result["items"][0]
    assert result["status"] == "ok"
    assert len(item["bars"]) == 20
    assert item["bars"][0]["date"] == "2026-09-01"
    assert item["bars"][10]["date"] == "2026-09-12"
    assert item["bars"][-2]["volume"] == 0.0
    assert item["bars"][-1]["volume"] is None
    assert item["analysis"]["indicators"]["volume"]["latest"] is None
    assert item["provenance"]["adjustment"] == "unknown"
    assert item["provenance"]["freshness"] == "not_evaluated"
    assert result["calendar_completeness"] == "not_verified"
    assert result["backtest_enabled"] is False


@pytest.mark.parametrize(
    "defect,expected_code", [("negative_volume", "volume_values"), ("missing_adjustment", "adjustment_declaration")]
)
def test_http_keeps_healthy_symbol_when_other_observation_is_invalid(observation, defect, expected_code):
    data, frame, provenance = observation
    data["BBRI.JK"] = frame.copy(deep=True)
    data["_provenance"]["BBRI.JK"] = dict(provenance)
    if defect == "negative_volume":
        frame.loc[frame.index[0], "volume"] = -1.0
    else:
        del provenance["adjustment"]
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={
                "codes": ["BBCA.JK", "BBRI.JK"],
                "lookback": 20,
                "end_date": "2026-10-01",
            },
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert result["items"][0]["quality_issue"] == {"code": expected_code}
    assert "analysis" not in result["items"][0]
    assert result["items"][1]["status"] == "ok"
    assert "quality_issue" not in result["items"][1]
    assert len(result["items"][1]["bars"]) == 20
    assert result["items"][1]["analysis"]["latest_close"] == 105.0


@pytest.mark.parametrize(
    "last_date,age,status",
    [("2026-10-01", 0, "within_window"), ("2026-09-17", 14, "within_window"), ("2026-09-16", 15, "warning")],
)
def test_recency_uses_calendar_days_relative_to_requested_end(observation, last_date, age, status):
    _, frame, _ = observation
    frame.index = pd.date_range(end=last_date, periods=21)

    result = research()

    assert result["status"] == "ok"
    assert result["items"][0]["recency"] == {
        "policy": "calendar_age_warning_v1",
        "reference_date": "2026-10-01",
        "last_bar_date": last_date,
        "age_calendar_days": age,
        "warning_after_calendar_days": 14,
        "status": status,
        "calendar_verified": False,
    }


def test_old_observation_warns_without_changing_bars_or_source_metadata(observation, caplog):
    _, frame, provenance = observation
    # A recent cache retrieval and contradictory as-of must not refresh old bars.
    provenance.update(retrieved_at="2026-10-01T10:00:00Z", data_as_of="2026-10-01")
    frame.index = pd.date_range(end="2026-09-16", periods=21)
    original = frame.copy(deep=True)
    original_provenance = dict(provenance)

    with caplog.at_level(logging.WARNING):
        result = research()

    item = result["items"][0]
    assert item["recency"]["status"] == "warning"
    assert item["analysis"]["latest_date"] == "2026-09-16"
    assert item["bars"][-1]["date"] == "2026-09-16"
    assert item["provenance"] == original_provenance
    assert "IDX research old observation for BBCA.JK (15 calendar days)" in caplog.text
    pd.testing.assert_frame_equal(frame, original)
    assert provenance == original_provenance


def test_default_recency_reference_uses_jakarta_today(observation, monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            # Still September 30 in UTC, already October 1 in Jakarta.
            return datetime(2026, 9, 30, 18, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(idx_research_tool, "datetime", Clock)

    result = json.loads(idx_research_tool.IDXResearchTool().execute(codes=["BBCA.JK"], lookback=20))

    assert result["requested_end_date"] == "2026-10-01"
    assert result["items"][0]["recency"]["reference_date"] == "2026-10-01"
    assert result["items"][0]["recency"]["age_calendar_days"] == 10


def test_empty_observation_does_not_claim_recency(observation):
    data, frame, _ = observation
    data["BBCA.JK"] = frame.iloc[:0]

    result = research()

    assert result["items"][0]["status"] == "unavailable"
    assert "recency" not in result["items"][0]
    assert "quality_issue" not in result["items"][0]


def test_invalid_observation_does_not_claim_recency(observation):
    _, frame, _ = observation
    frame.loc[frame.index[0], "close"] = -1.0

    result = research()

    assert result["items"][0]["status"] == "unavailable"
    assert "recency" not in result["items"][0]


def test_future_observation_is_rejected_instead_of_reporting_negative_age(observation):
    _, frame, _ = observation
    frame.index = pd.date_range("2026-10-01", periods=21)

    result = research()

    assert result["items"][0]["status"] == "unavailable"
    assert "recency" not in result["items"][0]


def test_http_returns_old_observation_warning_alongside_unavailable_symbol(observation):
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post(
            "/api/research/idx",
            json={"codes": ["BBCA.JK", "BBRI.JK"], "lookback": 20, "end_date": "2026-10-10"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "partial"
    assert result["items"][0]["status"] == "ok"
    assert result["items"][0]["recency"]["age_calendar_days"] == 19
    assert result["items"][0]["recency"]["status"] == "warning"
    assert result["items"][1]["status"] == "unavailable"
    assert "recency" not in result["items"][1]


def test_cli_emits_recency_warning_with_success_for_available_data(observation, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["idx_research", "BBCA.JK", "--lookback", "20", "--end-date", "2026-10-10"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 0
    assert result["status"] == "ok"
    assert result["items"][0]["recency"]["status"] == "warning"


def test_cli_rejects_missing_adjustment_with_unavailable_exit(observation, monkeypatch, capsys):
    _, _, provenance = observation
    del provenance["adjustment"]
    monkeypatch.setattr(sys, "argv", ["idx_research", "BBCA.JK", "--lookback", "20", "--end-date", "2026-10-01"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 2
    assert result["status"] == "unavailable"
    assert result["items"][0]["reason"] == "invalid_data_or_metadata"
    assert result["items"][0]["quality_issue"] == {"code": "adjustment_declaration"}
    assert "analysis" not in result["items"][0]
