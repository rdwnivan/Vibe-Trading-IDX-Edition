"""Offline audit of vendor daily-bar hazards seen on IDX data (DATA-03).

All dates, calendars, suspensions and prices here are synthetic. The 2030
calendar is a test fixture, not an IDX calendar, and no rule or default is
taken from it.
"""

from datetime import date
import json

import numpy as np
import pandas as pd
import pytest

from src.markets.idx_bar_quality import IDXSuspension, audit_daily_bars
from src.markets.idx_rules import IDXSessionCalendar

SYMBOL = "TEST.JK"
SENTINEL = 999999.9999

# Synthetic coverage 2030-01-07 (Mon) to 2030-01-18 (Fri); 2030-01-10 is a
# fixture holiday, weekends are closed.
SESSIONS = frozenset(date(2030, 1, day) for day in (7, 8, 9, 11, 14, 15, 16, 17, 18))
CALENDAR = IDXSessionCalendar(
    source="synthetic test calendar",
    covered_from=date(2030, 1, 7),
    covered_until=date(2030, 1, 18),
    sessions=SESSIONS,
)


def bars(rows):
    """Build a daily frame from (iso date, close, volume[, open, high, low])."""
    index, data = [], []
    for row in rows:
        stamp, close, volume, *rest = row
        open_, high, low = rest if rest else (close, close, close)
        index.append(pd.Timestamp(stamp))
        data.append({"open": open_, "high": high, "low": low, "close": close, "volume": volume})
    return pd.DataFrame(data, index=pd.DatetimeIndex(index))


def clean_rows():
    return [(day.isoformat(), 1000.0 + day.day, 5000.0, 990.0, 1100.0, 980.0) for day in sorted(SESSIONS)]


def test_clean_bars_on_every_session_have_no_findings():
    report = audit_daily_bars(SYMBOL, bars(clean_rows()), calendar=CALENDAR)

    assert report["calendar_verified"] is True
    assert report["calendar_source"] == "synthetic test calendar"
    assert report["bar_count"] == 9
    for key in (
        "off_calendar_dates",
        "uncovered_dates",
        "missing_session_dates",
        "zero_volume_flat_bars",
        "zero_volume_price_change_dates",
        "traded_during_suspension_dates",
    ):
        assert report[key] == [], key


def test_holiday_row_repeating_last_close_is_off_calendar_not_a_zero_volume_session():
    rows = clean_rows()
    rows.append(("2030-01-10", 1009.0, 0.0))  # repeats the 2030-01-09 close
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["off_calendar_dates"] == ["2030-01-10"]
    assert report["zero_volume_flat_bars"] == []
    assert report["zero_volume_price_change_dates"] == []


def test_weekend_sentinel_rows_are_off_calendar_and_flagged_as_price_change():
    rows = clean_rows()
    rows += [("2030-01-12", SENTINEL, 0.0), ("2030-01-13", SENTINEL, 0.0)]
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["off_calendar_dates"] == ["2030-01-12", "2030-01-13"]
    # Both rows differ from the last traded close (2030-01-11), not only the
    # first: a second sentinel equal to the first is still not a trade price.
    assert report["zero_volume_price_change_dates"] == ["2030-01-12", "2030-01-13"]


def test_sentinel_rows_are_flagged_without_any_calendar():
    rows = clean_rows() + [
        ("2030-01-10", 1009.0, 0.0),
        ("2030-01-12", SENTINEL, 0.0),
        ("2030-01-13", SENTINEL, 0.0),
    ]
    report = audit_daily_bars(SYMBOL, bars(rows))

    assert report["calendar_verified"] is False
    assert report["calendar_source"] is None
    for key in ("off_calendar_dates", "uncovered_dates", "missing_session_dates"):
        assert report[key] is None, key
    assert report["zero_volume_price_change_dates"] == ["2030-01-12", "2030-01-13"]
    # Without a calendar a holiday row repeating the close cannot be told from
    # an untraded or halted session. Sentinel rows are reported once, as a
    # price change, not again as ambiguous sessions.
    assert report["zero_volume_flat_bars"] == [{"date": "2030-01-10", "status": "untraded_or_suspended"}]


def test_zero_volume_session_without_a_suspension_record_stays_ambiguous():
    rows = clean_rows()
    rows[3] = ("2030-01-11", 1009.0, 0.0)  # flat, repeats the 2030-01-09 close
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["zero_volume_flat_bars"] == [{"date": "2030-01-11", "status": "untraded_or_suspended"}]
    assert report["zero_volume_price_change_dates"] == []
    assert report["off_calendar_dates"] == []


def test_supplied_suspension_marks_the_zero_volume_session_as_suspended():
    rows = clean_rows()
    rows[3] = ("2030-01-11", 1009.0, 0.0)
    halt = IDXSuspension(
        symbol=SYMBOL,
        source="synthetic notice",
        first_day=date(2030, 1, 11),
        last_day=date(2030, 1, 11),
    )
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR, suspensions=(halt,))

    assert report["zero_volume_flat_bars"] == [{"date": "2030-01-11", "status": "suspended"}]
    assert report["suspension_sources"] == ["synthetic notice"]


def test_suspension_records_for_other_symbols_are_ignored():
    rows = clean_rows()
    rows[3] = ("2030-01-11", 1009.0, 0.0)
    other = IDXSuspension(
        symbol="OTHR.JK",
        source="synthetic notice",
        first_day=date(2030, 1, 11),
        last_day=date(2030, 1, 11),
    )
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR, suspensions=(other,))

    assert report["zero_volume_flat_bars"] == [{"date": "2030-01-11", "status": "untraded_or_suspended"}]
    assert report["suspension_sources"] == []


def test_positive_volume_inside_a_supplied_suspension_is_a_contradiction():
    halt = IDXSuspension(
        symbol=SYMBOL,
        source="synthetic notice",
        first_day=date(2030, 1, 14),
        last_day=date(2030, 1, 15),
    )
    report = audit_daily_bars(SYMBOL, bars(clean_rows()), calendar=CALENDAR, suspensions=(halt,))

    assert report["traded_during_suspension_dates"] == ["2030-01-14", "2030-01-15"]


def test_missing_session_is_reported_and_no_bar_is_invented():
    rows = [row for row in clean_rows() if row[0] != "2030-01-15"]
    frame = bars(rows)
    before = frame.copy(deep=True)
    report = audit_daily_bars(SYMBOL, frame, calendar=CALENDAR)

    assert report["missing_session_dates"] == ["2030-01-15"]
    assert report["bar_count"] == 8
    pd.testing.assert_frame_equal(frame, before)


def test_missing_sessions_are_only_counted_between_the_first_and_last_bar():
    rows = [row for row in clean_rows() if "2030-01-08" <= row[0] <= "2030-01-16"]
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["missing_session_dates"] == []


def test_bars_outside_calendar_coverage_are_unknown_not_errors():
    rows = clean_rows() + [("2030-01-21", 1100.0, 5000.0)]
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["uncovered_dates"] == ["2030-01-21"]
    assert report["off_calendar_dates"] == []


def test_missing_volume_is_not_treated_as_zero():
    rows = clean_rows()
    rows[3] = ("2030-01-11", SENTINEL, np.nan)
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["zero_volume_flat_bars"] == []
    assert report["zero_volume_price_change_dates"] == []


def test_zero_volume_bar_before_any_trade_cannot_be_judged_for_price_change():
    rows = [("2030-01-07", 1000.0, 0.0)] + clean_rows()[1:]
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["zero_volume_price_change_dates"] == []
    assert report["zero_volume_flat_bars"] == [{"date": "2030-01-07", "status": "untraded_or_suspended"}]


def test_zero_volume_bar_with_a_range_is_a_price_change_even_if_close_repeats():
    rows = clean_rows()
    rows[3] = ("2030-01-11", 1009.0, 0.0, 1009.0, 1050.0, 1009.0)
    report = audit_daily_bars(SYMBOL, bars(rows), calendar=CALENDAR)

    assert report["zero_volume_price_change_dates"] == ["2030-01-11"]
    assert report["zero_volume_flat_bars"] == []


def test_report_is_strict_json_and_input_order_does_not_matter():
    rows = clean_rows() + [("2030-01-12", SENTINEL, 0.0)]
    shuffled = bars(list(reversed(rows)))
    report = audit_daily_bars(SYMBOL, shuffled, calendar=CALENDAR)

    json.dumps(report, allow_nan=False)
    assert report["policy"] == "idx_daily_bar_audit_v1"
    assert report["zero_volume_price_change_dates"] == ["2030-01-12"]


@pytest.mark.parametrize("symbol", ["AAPL", "600000.SH", "TEST", "", None])
def test_non_idx_symbols_are_rejected(symbol):
    with pytest.raises(ValueError):
        audit_daily_bars(symbol, bars(clean_rows()))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda frame: frame.reset_index(drop=True),
        lambda frame: pd.concat([frame, frame.iloc[[0]]]),
        lambda frame: frame.tz_localize("Asia/Jakarta"),
        lambda frame: frame.set_axis(frame.index + pd.Timedelta(hours=9)),
        lambda frame: frame.drop(columns=["volume"]),
        lambda frame: frame.drop(columns=["close"]),
    ],
    ids=[
        "not-dated",
        "duplicate-date",
        "tz-aware",
        "intraday",
        "no-volume",
        "no-close",
    ],
)
def test_malformed_frames_are_rejected(mutate):
    with pytest.raises(ValueError):
        audit_daily_bars(SYMBOL, mutate(bars(clean_rows())))


def test_calendar_and_suspension_types_are_enforced():
    with pytest.raises(ValueError):
        audit_daily_bars(SYMBOL, bars(clean_rows()), calendar={"sessions": []})
    with pytest.raises(ValueError):
        audit_daily_bars(SYMBOL, bars(clean_rows()), suspensions=[("TEST.JK", "x")])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"symbol": "AAPL"},
        {"symbol": "TEST"},
        {"source": "  "},
        {"first_day": date(2030, 1, 12), "last_day": date(2030, 1, 11)},
        {"first_day": pd.Timestamp("2030-01-11")},
        {"last_day": "2030-01-11"},
    ],
)
def test_suspension_record_requires_idx_symbol_source_and_ordered_dates(kwargs):
    fields = {
        "symbol": SYMBOL,
        "source": "synthetic notice",
        "first_day": date(2030, 1, 11),
        "last_day": date(2030, 1, 11),
    }
    fields.update(kwargs)
    with pytest.raises(ValueError):
        IDXSuspension(**fields)
