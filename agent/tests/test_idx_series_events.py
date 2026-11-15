"""Offline checks for series end, session staleness and ex-date moves (DATA-03).

All dates, calendars, delistings, corporate actions and prices here are
synthetic. The 2030 calendar is a test fixture, not an IDX calendar, and no
rule, default or adjustment is taken from it.
"""

from datetime import date
import json

import numpy as np
import pandas as pd
import pytest

from src.markets.idx_bar_quality import (
    IDXCorporateAction,
    IDXDelisting,
    IDXSuspension,
    audit_series_events,
)
from src.markets.idx_rules import IDXSessionCalendar

SYMBOL = "TEST.JK"

# Synthetic coverage 2030-01-07 (Mon) to 2030-01-18 (Fri); 2030-01-10 is a
# fixture holiday, weekends are closed.
SESSIONS = frozenset(date(2030, 1, day) for day in (7, 8, 9, 11, 14, 15, 16, 17, 18))
CALENDAR = IDXSessionCalendar(
    source="synthetic test calendar",
    covered_from=date(2030, 1, 7),
    covered_until=date(2030, 1, 18),
    sessions=SESSIONS,
)


def bars(rows, adjusted=None):
    """Build a daily frame from (iso date, close, volume); adjusted is a list of adjusted closes."""
    index = [pd.Timestamp(stamp) for stamp, _, _ in rows]
    data = [{"open": c, "high": c, "low": c, "close": c, "volume": v} for _, c, v in rows]
    columns = ["open", "high", "low", "close", "volume"]
    frame = pd.DataFrame(data, index=pd.DatetimeIndex(index), columns=columns)
    if adjusted is not None:
        frame["adjusted_close"] = adjusted
    return frame


def session_rows(until="2030-01-18"):
    return [(day.isoformat(), 1000.0, 5000.0) for day in sorted(SESSIONS) if day.isoformat() <= until]


def delisting(effective_day, symbol=SYMBOL):
    return IDXDelisting(symbol=symbol, source="synthetic delisting notice", effective_day=effective_day)


def dividend(ex_day, symbol=SYMBOL, kind="cash_dividend"):
    return IDXCorporateAction(symbol=symbol, source="synthetic dividend notice", kind=kind, ex_day=ex_day)


# --- Series end and delisting ------------------------------------------------


def test_series_stopping_mid_window_with_a_sourced_delisting_is_delisted():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        delistings=(delisting(date(2030, 1, 15)),),
    )

    end = report["series_end"]
    assert end["status"] == "delisted"
    assert end["last_bar_date"] == "2030-01-14"
    assert end["delisting_effective_date"] == "2030-01-15"
    assert end["sessions_after_last_bar"] == 4
    assert report["delisting_sources"] == ["synthetic delisting notice"]
    assert report["bars_after_delisting_dates"] == []


def test_series_stopping_mid_window_without_a_record_is_ended_or_stale_not_delisted():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
    )

    end = report["series_end"]
    assert end["status"] == "ended_or_stale"
    assert end["sessions_after_last_bar"] == 4
    assert end["delisting_effective_date"] is None
    assert report["delisting_sources"] == []


def test_delisting_is_reported_without_a_calendar_but_session_age_is_not():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        delistings=(delisting(date(2030, 1, 15)),),
    )

    assert report["calendar_verified"] is False
    assert report["series_end"]["status"] == "delisted"
    assert report["series_end"]["sessions_after_last_bar"] is None


def test_delisting_effective_after_as_of_does_not_mark_the_series_delisted():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 15),
        calendar=CALENDAR,
        delistings=(delisting(date(2030, 1, 16)),),
    )

    assert report["series_end"]["status"] == "ended_or_stale"
    assert report["series_end"]["delisting_effective_date"] is None


def test_window_with_no_bars_and_a_delisting_is_delisted_and_nothing_is_filled():
    empty = bars([])
    report = audit_series_events(
        SYMBOL,
        empty,
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        delistings=(delisting(date(2030, 1, 7)),),
    )

    assert report["bar_count"] == 0
    assert report["series_end"]["status"] == "delisted"
    assert report["series_end"]["last_bar_date"] is None
    assert empty.empty


def test_window_with_no_bars_and_no_record_is_no_bars():
    report = audit_series_events(SYMBOL, bars([]), as_of=date(2030, 1, 18), calendar=CALENDAR)

    assert report["series_end"]["status"] == "no_bars"
    assert report["series_end"]["sessions_after_last_bar"] is None


def test_bars_on_or_after_the_delisting_date_are_a_contradiction():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows()),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        delistings=(delisting(date(2030, 1, 17)),),
    )

    assert report["bars_after_delisting_dates"] == ["2030-01-17", "2030-01-18"]
    assert report["series_end"]["status"] == "delisted"


def test_delisting_records_for_other_symbols_are_ignored():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        delistings=(delisting(date(2030, 1, 15), symbol="OTHR.JK"),),
    )

    assert report["series_end"]["status"] == "ended_or_stale"
    assert report["delisting_sources"] == []


def test_two_delisting_records_for_one_symbol_are_refused():
    with pytest.raises(ValueError):
        audit_series_events(
            SYMBOL,
            bars(session_rows()),
            as_of=date(2030, 1, 18),
            delistings=(delisting(date(2030, 1, 15)), delisting(date(2030, 1, 16))),
        )


def test_series_end_is_not_judged_without_as_of():
    report = audit_series_events(SYMBOL, bars(session_rows()), calendar=CALENDAR)

    assert report["series_end"] is None


def test_as_of_before_the_last_bar_is_refused():
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, bars(session_rows()), as_of=date(2030, 1, 15), calendar=CALENDAR)


@pytest.mark.parametrize("as_of", ["2030-01-18", pd.Timestamp("2030-01-18")])
def test_as_of_must_be_a_calendar_date(as_of):
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, bars(session_rows()), as_of=as_of)


# --- Session-based staleness -------------------------------------------------


def test_last_bar_on_the_latest_session_is_current():
    # 2030-01-19/20 are a weekend; age counts sessions, not calendar days.
    report = audit_series_events(SYMBOL, bars(session_rows()), as_of=date(2030, 1, 18), calendar=CALENDAR)

    assert report["series_end"]["status"] == "current"
    assert report["series_end"]["sessions_after_last_bar"] == 0


def test_session_age_skips_weekends_and_calendar_holidays():
    # Last bar Wed 2030-01-09; Thu 2030-01-10 is a fixture holiday, so the
    # sessions after it up to Mon 2030-01-14 are 01-11 and 01-14.
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-09")),
        as_of=date(2030, 1, 14),
        calendar=CALENDAR,
    )

    assert report["series_end"]["sessions_after_last_bar"] == 2
    assert report["series_end"]["status"] == "ended_or_stale"


def test_as_of_on_a_closed_day_after_the_last_session_is_current():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-09")),
        as_of=date(2030, 1, 10),
        calendar=CALENDAR,
    )

    assert report["series_end"]["sessions_after_last_bar"] == 0
    assert report["series_end"]["status"] == "current"


def test_session_age_is_none_without_a_calendar():
    report = audit_series_events(SYMBOL, bars(session_rows(until="2030-01-09")), as_of=date(2030, 1, 14))

    assert report["series_end"]["status"] == "unverified"
    assert report["series_end"]["sessions_after_last_bar"] is None


def test_session_age_is_none_when_as_of_is_outside_calendar_coverage():
    report = audit_series_events(
        SYMBOL,
        bars(session_rows()),
        as_of=date(2030, 1, 21),
        calendar=CALENDAR,
    )

    assert report["series_end"]["status"] == "uncovered"
    assert report["series_end"]["sessions_after_last_bar"] is None


def test_missing_sessions_all_inside_a_supplied_suspension_are_suspended_not_stale():
    halt = IDXSuspension(
        symbol=SYMBOL,
        source="synthetic notice",
        first_day=date(2030, 1, 15),
        last_day=date(2030, 1, 31),
    )
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        suspensions=(halt,),
    )

    assert report["series_end"]["status"] == "suspended"
    assert report["series_end"]["sessions_after_last_bar"] == 4


def test_suspension_covering_only_part_of_the_gap_stays_ended_or_stale():
    halt = IDXSuspension(
        symbol=SYMBOL,
        source="synthetic notice",
        first_day=date(2030, 1, 15),
        last_day=date(2030, 1, 16),
    )
    report = audit_series_events(
        SYMBOL,
        bars(session_rows(until="2030-01-14")),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        suspensions=(halt,),
    )

    assert report["series_end"]["status"] == "ended_or_stale"


# --- Ex-date moves -----------------------------------------------------------


def test_raw_series_shows_the_ex_date_drop_and_adjusted_close_factor_changes():
    rows = [("2030-01-14", 1000.0, 5000.0), ("2030-01-15", 950.0, 5000.0), ("2030-01-16", 950.0, 5000.0)]
    frame = bars(rows, adjusted=[950.0, 950.0, 950.0])
    before = frame.copy(deep=True)
    report = audit_series_events(SYMBOL, frame, corporate_actions=(dividend(date(2030, 1, 15)),))

    assert report["adjusted_close_supplied"] is True
    assert report["corporate_action_sources"] == ["synthetic dividend notice"]
    [move] = report["ex_date_moves"]
    assert move["ex_date"] == "2030-01-15"
    assert move["kind"] == "cash_dividend"
    assert move["bar_present"] is True
    assert move["previous_bar_date"] == "2030-01-14"
    assert move["previous_close"] == 1000.0
    assert move["close"] == 950.0
    assert move["close_ratio"] == pytest.approx(0.95)
    assert move["previous_adjustment_factor"] == pytest.approx(0.95)
    assert move["adjustment_factor"] == pytest.approx(1.0)
    pd.testing.assert_frame_equal(frame, before)


def test_already_adjusted_series_shows_no_ex_date_drop_and_is_reported_as_is():
    rows = [("2030-01-14", 950.0, 5000.0), ("2030-01-15", 950.0, 5000.0)]
    report = audit_series_events(SYMBOL, bars(rows), corporate_actions=(dividend(date(2030, 1, 15)),))

    [move] = report["ex_date_moves"]
    assert move["close_ratio"] == pytest.approx(1.0)
    assert report["adjusted_close_supplied"] is False
    assert move["previous_adjustment_factor"] is None
    assert move["adjustment_factor"] is None


def test_price_jumps_are_not_reported_without_a_corporate_action_record():
    rows = [("2030-01-14", 1000.0, 5000.0), ("2030-01-15", 200.0, 5000.0)]
    report = audit_series_events(SYMBOL, bars(rows))

    assert report["ex_date_moves"] == []
    assert report["corporate_action_sources"] == []


def test_ex_date_without_a_bar_is_reported_as_missing_not_filled():
    rows = [("2030-01-14", 1000.0, 5000.0), ("2030-01-16", 950.0, 5000.0)]
    report = audit_series_events(SYMBOL, bars(rows), corporate_actions=(dividend(date(2030, 1, 15)),))

    [move] = report["ex_date_moves"]
    assert move["bar_present"] is False
    assert move["close"] is None
    assert move["close_ratio"] is None
    assert report["bar_count"] == 2


def test_ex_date_on_the_first_bar_has_no_previous_close():
    rows = [("2030-01-15", 950.0, 5000.0)]
    report = audit_series_events(SYMBOL, bars(rows), corporate_actions=(dividend(date(2030, 1, 15)),))

    [move] = report["ex_date_moves"]
    assert move["previous_bar_date"] is None
    assert move["previous_close"] is None
    assert move["close_ratio"] is None


def test_actions_for_other_symbols_are_ignored_and_moves_are_date_ordered():
    rows = [("2030-01-14", 1000.0, 5000.0), ("2030-01-15", 950.0, 5000.0), ("2030-01-16", 190.0, 5000.0)]
    actions = (
        dividend(date(2030, 1, 16), kind="split"),
        dividend(date(2030, 1, 15)),
        dividend(date(2030, 1, 15), symbol="OTHR.JK"),
    )
    report = audit_series_events(SYMBOL, bars(rows), corporate_actions=actions)

    assert [(m["ex_date"], m["kind"]) for m in report["ex_date_moves"]] == [
        ("2030-01-15", "cash_dividend"),
        ("2030-01-16", "split"),
    ]


def test_report_is_strict_json_with_missing_prices():
    rows = [("2030-01-14", np.nan, 5000.0), ("2030-01-15", 950.0, 5000.0)]
    report = audit_series_events(
        SYMBOL,
        bars(rows, adjusted=[np.nan, 950.0]),
        as_of=date(2030, 1, 18),
        calendar=CALENDAR,
        corporate_actions=(dividend(date(2030, 1, 15)),),
    )

    json.dumps(report, allow_nan=False)
    assert report["policy"] == "idx_series_event_audit_v1"
    [move] = report["ex_date_moves"]
    assert move["previous_close"] is None
    assert move["close_ratio"] is None
    assert move["previous_adjustment_factor"] is None


# --- Input validation --------------------------------------------------------


@pytest.mark.parametrize("symbol", ["AAPL", "TEST", "", None])
def test_non_idx_symbols_are_rejected(symbol):
    with pytest.raises(ValueError):
        audit_series_events(symbol, bars(session_rows()))


def test_record_containers_and_calendar_type_are_enforced():
    frame = bars(session_rows())
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, frame, delistings=[delisting(date(2030, 1, 15))])
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, frame, corporate_actions=(("TEST.JK", "2030-01-15"),))
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, frame, calendar={"sessions": []})


def test_duplicate_adjusted_close_columns_are_rejected():
    frame = bars(session_rows(), adjusted=[1000.0] * 9)
    frame = pd.concat([frame, frame[["adjusted_close"]]], axis=1)
    with pytest.raises(ValueError):
        audit_series_events(SYMBOL, frame)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"symbol": "AAPL"},
        {"source": " "},
        {"effective_day": pd.Timestamp("2030-01-15")},
        {"effective_day": "2030-01-15"},
    ],
)
def test_delisting_record_requires_idx_symbol_source_and_date(kwargs):
    fields = {"symbol": SYMBOL, "source": "synthetic notice", "effective_day": date(2030, 1, 15)}
    fields.update(kwargs)
    with pytest.raises(ValueError):
        IDXDelisting(**fields)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"symbol": "600000.SH"},
        {"source": ""},
        {"kind": "dividend"},
        {"kind": ""},
        {"ex_day": pd.Timestamp("2030-01-15")},
    ],
)
def test_corporate_action_record_requires_idx_symbol_source_known_kind_and_date(kwargs):
    fields = {"symbol": SYMBOL, "source": "synthetic notice", "kind": "cash_dividend", "ex_day": date(2030, 1, 15)}
    fields.update(kwargs)
    with pytest.raises(ValueError):
        IDXCorporateAction(**fields)
