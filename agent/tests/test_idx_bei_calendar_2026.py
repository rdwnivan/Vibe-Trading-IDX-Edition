"""The sourced BEI 2026 session calendar as an ``idx_session_calendar_v1`` file.

Closures come from BEI Peng-00171/BEI.POP/09-2025 (23 September 2025), matched
by KSEI PENG-0002/DIR/KSEI/0126; an exchange day is Monday to Friday except
those closures (II-A Kep-00158/BEI/10-2026, I.16). See IDX_REFERENCE.md. The
file is a test fixture that nothing loads automatically.
"""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.markets.idx_bar_quality import audit_daily_bars
from src.markets.idx_calendar_file import load_session_calendar
from src.markets.idx_event_records import load_event_records

FIXTURES = Path(__file__).parent / "fixtures"
CALENDAR = FIXTURES / "idx_calendar" / "bei_sessions_2026.json"
MLPT_RECORD = FIXTURES / "idx_event_records" / "mlpt_2026-03_suspension.json"

# The 22 weekday closures listed by Peng-00171/BEI.POP/09-2025.
CLOSURES_2026 = {
    date(2026, month, day)
    for month, day in [
        (1, 1),
        (1, 16),
        (2, 16),
        (2, 17),
        (3, 18),
        (3, 19),
        (3, 20),
        (3, 23),
        (3, 24),
        (4, 3),
        (5, 1),
        (5, 14),
        (5, 15),
        (5, 27),
        (5, 28),
        (6, 1),
        (6, 16),
        (8, 17),
        (8, 25),
        (12, 24),
        (12, 25),
        (12, 31),
    ]
}

# The 14 holiday rows EODHD served for RAJA/MLPT (IDX_PROVIDER_RESEARCH.md,
# "EODHD split handling ..."): 11 fall in 2026, 3 in late 2025.
EODHD_HOLIDAYS_2026 = [
    date(2026, 1, 1),
    date(2026, 1, 16),
    date(2026, 5, 1),
    date(2026, 5, 14),
    date(2026, 5, 15),
    date(2026, 5, 27),
    date(2026, 5, 28),
    date(2026, 6, 1),
    date(2026, 6, 16),
    date(2026, 8, 17),
    date(2026, 8, 25),
]
EODHD_HOLIDAYS_2025 = [date(2025, 12, 25), date(2025, 12, 26), date(2025, 12, 31)]


def _year_days():
    day = date(2026, 1, 1)
    while day.year == 2026:
        yield day
        day += timedelta(days=1)


def test_file_loads_and_covers_the_whole_of_2026():
    calendar = load_session_calendar(CALENDAR)

    assert calendar.covered_from == date(2026, 1, 1)
    assert calendar.covered_until == date(2026, 12, 31)
    assert len(calendar.sessions) == 239


def test_source_names_the_holiday_notice_and_the_weekday_rule():
    source = load_session_calendar(CALENDAR).source

    assert "Peng-00171/BEI.POP/09-2025" in source
    assert "PENG-0002/DIR/KSEI/0126" in source
    assert "Kep-00158/BEI/10-2026" in source
    assert "I.16" in source


def test_sessions_are_exactly_the_weekdays_minus_the_listed_closures():
    calendar = load_session_calendar(CALENDAR)
    weekdays = {day for day in _year_days() if day.weekday() < 5}

    assert CLOSURES_2026 <= weekdays
    assert calendar.sessions == frozenset(weekdays - CLOSURES_2026)


def test_eodhd_holiday_rows_in_2026_fall_on_closed_days():
    calendar = load_session_calendar(CALENDAR)

    assert [day for day in EODHD_HOLIDAYS_2026 if calendar.is_session(day)] == []


def test_eodhd_holiday_rows_in_2025_are_outside_coverage_not_sessions():
    calendar = load_session_calendar(CALENDAR)
    frame = _flat_bars([*EODHD_HOLIDAYS_2025, *EODHD_HOLIDAYS_2026])

    audit = audit_daily_bars("RAJA.JK", frame, calendar=calendar)

    assert audit["uncovered_dates"] == [day.isoformat() for day in EODHD_HOLIDAYS_2025]
    assert audit["off_calendar_dates"] == [day.isoformat() for day in EODHD_HOLIDAYS_2026]


def test_27_march_2026_is_a_session_and_the_mlpt_halt_is_reported_as_suspended():
    calendar = load_session_calendar(CALENDAR)
    assert calendar.is_session(date(2026, 3, 27))

    frame = pd.DataFrame(
        {
            "open": [100.0, 100.0, 101.0],
            "high": [100.0, 100.0, 101.0],
            "low": [100.0, 100.0, 101.0],
            "close": [100.0, 100.0, 101.0],
            "volume": [1000.0, 0.0, 1200.0],
        },
        index=pd.DatetimeIndex(["2026-03-26", "2026-03-27", "2026-03-30"]),
    )
    audit = audit_daily_bars(
        "MLPT.JK",
        frame,
        calendar=calendar,
        suspensions=load_event_records(MLPT_RECORD).suspensions,
    )

    assert audit["off_calendar_dates"] == []
    assert audit["missing_session_dates"] == []
    assert audit["zero_volume_flat_bars"] == [{"date": "2026-03-27", "status": "suspended"}]


def _flat_bars(days):
    days = sorted(days)
    values = [100.0] * len(days)
    return pd.DataFrame(
        {"open": values, "high": values, "low": values, "close": values, "volume": [0.0] * len(days)},
        index=pd.DatetimeIndex([pd.Timestamp(day) for day in days]),
    )
