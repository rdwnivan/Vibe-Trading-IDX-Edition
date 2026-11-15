"""Loader for a caller-supplied, sourced IDX session calendar (DATA-03, RULE-01).

The calendar here is synthetic (January 2030), not an IDX calendar. The loader
ships no calendar and infers no holiday or weekday rule.
"""

from datetime import date
import json

import pytest

from src.markets.idx_calendar_file import SCHEMA, load_session_calendar
from src.markets.idx_rules import IDXSessionCalendar

SESSIONS = ["2030-01-07", "2030-01-08", "2030-01-09", "2030-01-11"]


def document(**changes):
    base = {
        "schema": "idx_session_calendar_v1",
        "source": "synthetic fixture calendar",
        "covered_from": "2030-01-07",
        "covered_until": "2030-01-13",
        "sessions": SESSIONS,
    }
    base.update(changes)
    return base


@pytest.fixture
def write(tmp_path):
    def write(payload, *, raw=False):
        path = tmp_path / "calendar.json"
        path.write_text(payload if raw else json.dumps(payload), encoding="utf-8")
        return path

    return write


def test_valid_file_loads_into_a_session_calendar(write):
    calendar = load_session_calendar(write(document()))

    assert SCHEMA == "idx_session_calendar_v1"
    assert calendar == IDXSessionCalendar(
        source="synthetic fixture calendar",
        covered_from=date(2030, 1, 7),
        covered_until=date(2030, 1, 13),
        sessions=frozenset(date.fromisoformat(day) for day in SESSIONS),
    )
    # Days inside coverage without a session are closed; nothing is inferred.
    assert calendar.is_session(date(2030, 1, 10)) is False
    assert calendar.is_session(date(2030, 1, 11)) is True


def test_coverage_without_sessions_is_allowed(write):
    calendar = load_session_calendar(write(document(sessions=[])))

    assert calendar.sessions == frozenset()


def test_weekend_session_is_kept_because_no_weekday_rule_is_assumed(write):
    calendar = load_session_calendar(write(document(sessions=[*SESSIONS, "2030-01-12"])))

    assert calendar.is_session(date(2030, 1, 12)) is True


@pytest.mark.parametrize(
    "changes",
    [
        {"schema": "idx_session_calendar_v2"},
        {"source": " "},
        {"source": None},
        {"covered_from": "2030-01-14"},
        {"covered_until": "2030/01/13"},
        {"covered_from": "2030-01-07T00:00:00"},
        {"sessions": ["2030-01-06", *SESSIONS]},
        {"sessions": [*SESSIONS, "2030-01-14"]},
        {"sessions": ["2030-01-08", "2030-01-07"]},
        {"sessions": ["2030-01-07", "2030-01-07"]},
        {"sessions": ["2030-01-32"]},
        {"sessions": [20300107]},
        {"sessions": "2030-01-07"},
        {"sessions": None},
    ],
    ids=[
        "unknown-schema",
        "blank-source",
        "null-source",
        "reversed-coverage",
        "slash-date",
        "datetime-coverage",
        "session-before-coverage",
        "session-after-coverage",
        "unsorted-sessions",
        "duplicate-session",
        "impossible-date",
        "numeric-session",
        "sessions-not-list",
        "sessions-null",
    ],
)
def test_invalid_calendar_is_refused(write, changes):
    with pytest.raises(ValueError):
        load_session_calendar(write(document(**changes)))


@pytest.mark.parametrize("missing", ["schema", "source", "covered_from", "covered_until", "sessions"])
def test_every_field_is_required(write, missing):
    payload = document()
    del payload[missing]
    with pytest.raises(ValueError):
        load_session_calendar(write(payload))


def test_unknown_fields_are_refused(write):
    with pytest.raises(ValueError):
        load_session_calendar(write(document(holidays=["2030-01-10"])))


def test_error_names_the_session_index_without_echoing_raw_values(write):
    marker = "SYNTHETIC_PRIVATE_MARKER"
    with pytest.raises(ValueError) as caught:
        load_session_calendar(write(document(sessions=[*SESSIONS[:2], marker])))

    assert "sessions[2]" in str(caught.value)
    assert marker not in str(caught.value)


@pytest.mark.parametrize(
    "raw",
    [
        "{",
        "[]",
        '{"schema": "idx_session_calendar_v1", "schema": "idx_session_calendar_v1"}',
        '{"schema": NaN}',
        "﻿{}",
    ],
    ids=["broken", "list", "duplicate-key", "nan", "bom"],
)
def test_invalid_json_is_refused(write, raw):
    with pytest.raises(ValueError):
        load_session_calendar(write(raw, raw=True))


def test_missing_file_is_refused(tmp_path):
    with pytest.raises(ValueError):
        load_session_calendar(tmp_path / "absent.json")
