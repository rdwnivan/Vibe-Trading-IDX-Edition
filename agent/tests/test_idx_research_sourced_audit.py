"""Opt-in sourced calendar and event-record files on the personal research surface.

Bars are synthetic. The calendar and MLPT record are the sourced fixtures
(BEI Peng-00171/BEI.POP/09-2025; Peng-SPT-00097 and Peng-UPT-00108); the
corporate-action and delisting records written here are synthetic and say so.
"""

from datetime import date, timedelta
import json
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from src.api.idx_research_routes import register_idx_research_routes
from src.config.accessor import reset_env_config
from src.markets.idx_calendar_file import load_session_calendar
from src.tools import idx_research_tool

FIXTURES = Path(__file__).parent / "fixtures"
CALENDAR = FIXTURES / "idx_calendar" / "bei_sessions_2026.json"
MLPT_RECORD = FIXTURES / "idx_event_records" / "mlpt_2026-03_suspension.json"
CALENDAR_ENV = "VIBE_TRADING_IDX_CALENDAR_PATH"
RECORDS_ENV = "VIBE_TRADING_IDX_EVENT_RECORDS_PATH"
END = "2026-04-30"
PROVENANCE = {
    "source": "yahoo",
    "quote_currency": "IDR",
    "exchange_timezone": "Asia/Jakarta",
    "interval": "1D",
    "volume_unit": "shares",
    "adjustment": "unknown",
    "freshness": "not_evaluated",
}


def _sessions(first, last):
    calendar = load_session_calendar(CALENDAR)
    return sorted(day for day in calendar.sessions if first <= day <= last)


@pytest.fixture
def observation(monkeypatch):
    """MLPT bars on 2026 sessions 18 Feb–24 Apr, flat zero volume on 27 Mar, plus a Good Friday row."""
    days = _sessions(date(2026, 2, 18), date(2026, 4, 24))
    days.append(date(2026, 4, 3))  # BEI closure (Peng-00171/BEI.POP/09-2025)
    days.sort()
    frame = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000.0},
        index=pd.DatetimeIndex([pd.Timestamp(day) for day in days]),
    )
    for halted in ("2026-03-27", "2026-04-03"):
        frame.loc[pd.Timestamp(halted), ["open", "high", "low", "close", "volume"]] = [105.0] * 4 + [0.0]
    data = {"MLPT.JK": frame, "_provenance": {"MLPT.JK": dict(PROVENANCE)}}
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: data)
    return data, frame


@pytest.fixture
def configure(monkeypatch):
    def configure(calendar=None, records=None):
        for name, value in ((CALENDAR_ENV, calendar), (RECORDS_ENV, records)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, str(value))
        reset_env_config()

    yield configure
    reset_env_config()


def research(codes=("MLPT.JK",), lookback=40):
    return json.loads(idx_research_tool.IDXResearchTool().execute(codes=list(codes), lookback=lookback, end_date=END))


def test_without_env_the_response_has_no_new_fields(observation, configure):
    configure()
    result = research()
    item = result["items"][0]

    assert "sourced_reference" not in result
    assert "sourced_audit" not in item
    assert item["bar_audit"] == {
        "policy": "idx_daily_bar_audit_v1",
        "calendar_verified": False,
        "zero_volume_price_change_dates": [],
    }
    assert item["recency"]["calendar_verified"] is False
    assert item["recency"]["warning_after_calendar_days"] == 14


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_env_values_count_as_not_configured(observation, configure, blank):
    configure(calendar=blank, records=blank)
    result = research()

    assert "sourced_reference" not in result
    assert "sourced_audit" not in result["items"][0]


def test_sourced_calendar_and_records_add_findings_without_changing_bar_audit(observation, configure):
    configure(calendar=CALENDAR, records=MLPT_RECORD)
    result = research()
    item = result["items"][0]
    reference = result["sourced_reference"]

    assert reference["policy"] == "idx_sourced_reference_v1"
    assert reference["calendar"]["status"] == "loaded"
    assert reference["calendar"]["covered_from"] == "2026-01-01"
    assert reference["calendar"]["covered_until"] == "2026-12-31"
    assert "Peng-00171/BEI.POP/09-2025" in reference["calendar"]["source"]
    assert reference["event_records"] == {
        "status": "loaded",
        "suspension_count": 1,
        "delisting_count": 0,
        "corporate_action_count": 0,
    }

    audit = item["sourced_audit"]
    assert audit["policy"] == "idx_sourced_audit_v1"
    assert audit["calendar_verified"] is True
    assert audit["off_calendar_dates"] == ["2026-04-03"]
    assert audit["uncovered_dates"] == []
    assert audit["missing_session_dates"] == []
    assert audit["zero_volume_flat_bars"] == [{"date": "2026-03-27", "status": "suspended"}]
    assert audit["traded_during_suspension_dates"] == []
    assert len(audit["suspension_sources"]) == 1
    assert audit["series_end"] == {
        "as_of": END,
        "last_bar_date": "2026-04-24",
        "status": "ended_or_stale",
        "sessions_after_last_bar": 4,
        "delisting_effective_date": None,
    }
    assert audit["ex_date_moves"] == []
    assert audit["bars_after_delisting_dates"] == []

    # The v1 contract and the 14-day calendar-age recency stay as they were.
    assert item["bar_audit"] == {
        "policy": "idx_daily_bar_audit_v1",
        "calendar_verified": False,
        "zero_volume_price_change_dates": [],
    }
    assert item["recency"]["status"] == "within_window"
    assert item["recency"]["calendar_verified"] is False
    assert result["calendar_completeness"] == "not_verified"
    assert result["backtest_enabled"] is False
    # Reported, never repaired: the holiday row stays in the bars.
    assert "2026-04-03" in [bar["date"] for bar in item["bars"]]


def test_without_a_record_the_halt_day_is_untraded_or_suspended(observation, configure):
    configure(calendar=CALENDAR)
    result = research()
    audit = result["items"][0]["sourced_audit"]

    assert result["sourced_reference"]["event_records"] == {"status": "not_configured"}
    assert audit["zero_volume_flat_bars"] == [{"date": "2026-03-27", "status": "untraded_or_suspended"}]
    assert audit["suspension_sources"] == []


def test_records_without_a_calendar_leave_calendar_findings_unknown(observation, configure):
    configure(records=MLPT_RECORD)
    result = research()
    audit = result["items"][0]["sourced_audit"]

    assert result["sourced_reference"]["calendar"] == {"status": "not_configured"}
    assert audit["calendar_verified"] is False
    assert audit["off_calendar_dates"] is None
    assert audit["missing_session_dates"] is None
    assert audit["series_end"]["status"] == "unverified"
    assert audit["series_end"]["sessions_after_last_bar"] is None
    # The Good Friday row is flat and zero-volume too; without a calendar it is not judged closed.
    assert audit["zero_volume_flat_bars"] == [
        {"date": "2026-03-27", "status": "suspended"},
        {"date": "2026-04-03", "status": "untraded_or_suspended"},
    ]


def test_findings_are_limited_to_the_analyzed_window(observation, configure):
    _, frame = observation
    # lookback 20 requests bars from 21 March; 27 March stays in the observation.
    frame.drop(frame.index[frame.index < pd.Timestamp("2026-03-21")], inplace=True)
    configure(calendar=CALENDAR, records=MLPT_RECORD)
    # The last 20 rows start on 30 March: 3 April is inside, 27 March is not.
    audit = research(lookback=20)["items"][0]["sourced_audit"]

    assert audit["off_calendar_dates"] == ["2026-04-03"]
    assert audit["zero_volume_flat_bars"] == []


def test_missing_sessions_and_supplied_ex_dates_are_reported(observation, configure, tmp_path):
    _, frame = observation
    frame.drop(pd.Timestamp("2026-04-14"), inplace=True)
    records = tmp_path / "records.json"
    records.write_text(
        json.dumps(
            {
                "schema": "idx_event_records_v1",
                "corporate_actions": [
                    {
                        "symbol": "MLPT.JK",
                        "source": "synthetic test record",
                        "kind": "cash_dividend",
                        "ex_day": "2026-04-15",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    frame.loc[pd.Timestamp("2026-04-15") :, ["open", "high", "low", "close"]] = 100.0
    configure(calendar=CALENDAR, records=records)

    audit = research()["items"][0]["sourced_audit"]

    assert audit["missing_session_dates"] == ["2026-04-14"]
    [move] = audit["ex_date_moves"]
    assert move["ex_date"] == "2026-04-15"
    assert move["kind"] == "cash_dividend"
    assert move["previous_bar_date"] == "2026-04-13"
    assert move["previous_close"] == 105.0
    assert move["close"] == 100.0


def test_a_supplied_delisting_marks_the_series_delisted(observation, configure, tmp_path):
    records = tmp_path / "records.json"
    records.write_text(
        json.dumps(
            {
                "schema": "idx_event_records_v1",
                "delistings": [{"symbol": "MLPT.JK", "source": "synthetic test record", "effective_day": "2026-04-27"}],
            }
        ),
        encoding="utf-8",
    )
    configure(calendar=CALENDAR, records=records)

    audit = research()["items"][0]["sourced_audit"]

    assert audit["series_end"]["status"] == "delisted"
    assert audit["series_end"]["delisting_effective_date"] == "2026-04-27"
    assert audit["bars_after_delisting_dates"] == []
    assert audit["delisting_sources"] == ["synthetic test record"]


MARKER = "PRIVATE-MARKER-7f3a"


@pytest.mark.parametrize(
    "content",
    [
        None,  # absent file
        "{" + MARKER,
        json.dumps({"schema": "idx_session_calendar_v1", "source": MARKER}),
        json.dumps({"schema": "idx_event_records_v1", "suspensions": [{"symbol": MARKER}]}),
    ],
)
def test_unreadable_or_invalid_files_degrade_without_echoing_content_or_path(
    observation, configure, tmp_path, caplog, content
):
    folder = tmp_path / MARKER
    folder.mkdir()
    bad = folder / "bad.json"
    if content is not None:
        bad.write_text(content, encoding="utf-8")
    configure(calendar=bad, records=bad)

    with caplog.at_level(logging.DEBUG):
        raw = idx_research_tool.IDXResearchTool().execute(codes=["MLPT.JK"], lookback=40, end_date=END)
    result = json.loads(raw)

    assert result["ok"] is True
    assert result["items"][0]["status"] == "ok"
    issue = {"status": "unavailable", "issue": "unreadable_or_invalid"}
    assert result["sourced_reference"]["calendar"] == issue
    assert result["sourced_reference"]["event_records"] == issue
    audit = result["items"][0]["sourced_audit"]
    assert audit["calendar_verified"] is False
    assert audit["suspension_sources"] == []
    assert MARKER not in raw
    assert MARKER not in caplog.text
    assert str(tmp_path) not in caplog.text


def test_one_invalid_file_does_not_disable_the_other(observation, configure, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("[]", encoding="utf-8")
    configure(calendar=bad, records=MLPT_RECORD)

    result = research()

    assert result["sourced_reference"]["calendar"]["status"] == "unavailable"
    assert result["sourced_reference"]["event_records"]["status"] == "loaded"
    assert result["items"][0]["sourced_audit"]["zero_volume_flat_bars"][0] == {
        "date": "2026-03-27",
        "status": "suspended",
    }


def test_rejected_and_unavailable_symbols_carry_no_sourced_audit(observation, configure):
    data, _ = observation
    data["_provenance"]["MLPT.JK"]["quote_currency"] = "USD"
    data["BBRI.JK"] = None
    configure(calendar=CALENDAR, records=MLPT_RECORD)

    result = research(codes=("MLPT.JK", "BBRI.JK"))

    assert "sourced_reference" in result
    assert all("sourced_audit" not in item for item in result["items"])


def test_audit_failure_for_one_symbol_is_isolated(observation, configure, monkeypatch, caplog):
    configure(calendar=CALENDAR, records=MLPT_RECORD)

    def broken(*args, **kwargs):
        raise ValueError(MARKER)

    monkeypatch.setattr(idx_research_tool, "audit_series_events", broken)
    with caplog.at_level(logging.WARNING):
        raw = idx_research_tool.IDXResearchTool().execute(codes=["MLPT.JK"], lookback=40, end_date=END)
    item = json.loads(raw)["items"][0]

    assert item["status"] == "ok"
    assert item["sourced_audit"] == {"policy": "idx_sourced_audit_v1", "issue": "audit_failed"}
    assert MARKER not in raw
    assert MARKER not in caplog.text


def test_http_route_returns_the_sourced_fields(observation, configure):
    configure(calendar=CALENDAR, records=MLPT_RECORD)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    with TestClient(app) as client:
        response = client.post("/api/research/idx", json={"codes": ["MLPT.JK"], "lookback": 40, "end_date": END})

    assert response.status_code == 200
    body = response.json()
    assert body["sourced_reference"]["calendar"]["status"] == "loaded"
    assert body["items"][0]["sourced_audit"]["off_calendar_dates"] == ["2026-04-03"]


def test_cli_prints_the_sourced_fields(observation, configure, monkeypatch, capsys):
    configure(calendar=CALENDAR, records=MLPT_RECORD)
    monkeypatch.setattr("sys.argv", ["idx_research_tool", "MLPT.JK", "--lookback", "40", "--end-date", END])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    assert exit_info.value.code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["items"][0]["sourced_audit"]["zero_volume_flat_bars"][0]["status"] == "suspended"


def test_env_fields_are_declared_in_the_config_schema(configure):
    from src.config.accessor import get_env_config

    configure(calendar=CALENDAR, records=MLPT_RECORD)
    data = get_env_config().data

    assert data.vibe_trading_idx_calendar_path == str(CALENDAR)
    assert data.vibe_trading_idx_event_records_path == str(MLPT_RECORD)
    configure()
    assert get_env_config().data.vibe_trading_idx_calendar_path == ""
    assert get_env_config().data.vibe_trading_idx_event_records_path == ""


def test_sessions_helper_matches_the_fixture_window():
    # Guard the synthetic observation: 18 Feb to 24 Apr 2026 avoids no sourced closure except 3 Apr.
    days = _sessions(date(2026, 2, 18), date(2026, 4, 24))
    assert date(2026, 4, 3) not in days
    assert date(2026, 3, 27) in days
    assert days[-1] + timedelta(days=3) == date(2026, 4, 27)


def test_a_home_relative_path_is_expanded(observation, configure, monkeypatch, tmp_path):
    (tmp_path / "calendar.json").write_text(CALENDAR.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    configure(calendar="~/calendar.json")

    assert research()["sourced_reference"]["calendar"]["status"] == "loaded"
