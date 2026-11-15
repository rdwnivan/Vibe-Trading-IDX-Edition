"""Read-only audit of vendor daily bars for IDX data-quality hazards.

Vendors have been seen to emit zero-volume rows on exchange holidays, some
with a placeholder price, and to fill a full-day trading halt with the prior
close and zero volume, without marking either. This module reports such bars;
it never drops, repairs or fills them.

A second audit reports where a series ends (delisted only from a supplied
record, otherwise ended or stale), its age in calendar sessions, and prices
around supplied corporate-action ex dates, without adjusting any price.

Calendars, suspensions, delistings and corporate actions must be supplied by
the caller from dated sources. Nothing here holds or infers an IDX calendar,
holiday, suspension, delisting or corporate action. Without a calendar,
calendar checks are reported as not run (``None``), not as clean.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from backtest.engines._market_hooks import _detect_market
from src.markets.idx_rules import IDXSessionCalendar

POLICY = "idx_daily_bar_audit_v1"
_COLUMNS = ("open", "high", "low", "close", "volume")


def _require_idx_symbol(symbol: Any) -> None:
    if not isinstance(symbol, str) or _detect_market(symbol) != "id_equity":
        raise ValueError("A canonical IDX symbol (XXXX.JK) is required")


@dataclass(frozen=True)
class IDXSuspension:
    """One sourced full-day trading halt, inclusive at both ends."""

    symbol: str
    source: str
    first_day: date
    last_day: date

    def __post_init__(self) -> None:
        _require_idx_symbol(self.symbol)
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("A suspension record requires its source")
        # pd.Timestamp subclasses datetime, which subclasses date; require plain dates.
        if type(self.first_day) is not date or type(self.last_day) is not date:
            raise ValueError("Suspension days must be calendar dates")
        if self.last_day < self.first_day:
            raise ValueError("Suspension interval is reversed")

    def covers(self, day: date) -> bool:
        return self.first_day <= day <= self.last_day


@dataclass(frozen=True)
class IDXDelisting:
    """One sourced delisting; ``effective_day`` is the first day the stock is no longer listed."""

    symbol: str
    source: str
    effective_day: date

    def __post_init__(self) -> None:
        _require_idx_symbol(self.symbol)
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("A delisting record requires its source")
        if type(self.effective_day) is not date:
            raise ValueError("Delisting day must be a calendar date")


# Labels for supplied records only. They carry no ratio, amount or adjustment rule.
CORPORATE_ACTION_KINDS = frozenset(
    {"cash_dividend", "stock_dividend", "bonus_shares", "split", "reverse_split", "rights_issue"}
)


@dataclass(frozen=True)
class IDXCorporateAction:
    """One sourced corporate action with its ex date (first day trading without the entitlement)."""

    symbol: str
    source: str
    kind: str
    ex_day: date

    def __post_init__(self) -> None:
        _require_idx_symbol(self.symbol)
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("A corporate-action record requires its source")
        if self.kind not in CORPORATE_ACTION_KINDS:
            raise ValueError("Unknown corporate-action kind")
        if type(self.ex_day) is not date:
            raise ValueError("Ex date must be a calendar date")


def _validated_frame(frame: Any) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("Dated daily bars are required")
    if frame.index.hasnans or frame.index.has_duplicates:
        raise ValueError("Bar dates must be unique")
    if frame.index.tz is not None or not frame.index.equals(frame.index.normalize()):
        raise ValueError("Bars must carry normalized local session dates")
    if isinstance(frame.columns, pd.MultiIndex) or any(frame.columns.tolist().count(c) != 1 for c in _COLUMNS):
        raise ValueError("One open, high, low, close and volume column is required")
    return frame.sort_index()


def audit_daily_bars(
    symbol: str,
    frame: pd.DataFrame,
    *,
    calendar: IDXSessionCalendar | None = None,
    suspensions: tuple[IDXSuspension, ...] = (),
) -> dict[str, Any]:
    """Report holiday rows, placeholder prices, ambiguous zero-volume days and gaps.

    Findings, all as ISO dates in ascending order:

    - ``off_calendar_dates``: bars on dates the calendar marks closed.
    - ``uncovered_dates``: bars outside the calendar's coverage (unknown).
    - ``missing_session_dates``: sessions between the first and last bar with
      no bar.
    - ``zero_volume_flat_bars``: flat zero-volume bars not already off the
      calendar, with ``status`` ``suspended`` when a supplied record covers
      the day and ``untraded_or_suspended`` otherwise.
    - ``zero_volume_price_change_dates``: zero-volume bars whose prices are
      not all equal to the last positive-volume close. With no trade there is
      no new trade price. Prices are compared exactly; a bar before any traded
      bar is not judged. Raw (unadjusted) series can also show this on an
      untraded corporate-action date, so it is a finding, not a verdict.
    - ``traded_during_suspension_dates``: positive volume inside a supplied
      suspension.

    Missing volume (NaN) is unknown, never zero. The input frame is not
    modified. Calendar-dependent findings are ``None`` without a calendar.
    """
    _require_idx_symbol(symbol)
    bars = _validated_frame(frame)
    if calendar is not None and not isinstance(calendar, IDXSessionCalendar):
        raise ValueError("calendar must be an IDXSessionCalendar")
    if not isinstance(suspensions, tuple) or any(not isinstance(item, IDXSuspension) for item in suspensions):
        raise ValueError("suspensions must be a tuple of IDXSuspension records")
    halts = [item for item in suspensions if item.symbol == symbol]

    off_calendar: list[str] = []
    uncovered: list[str] = []
    flat_zero: list[dict[str, str]] = []
    price_change: list[str] = []
    traded_halted: list[str] = []
    last_traded_close: float | None = None

    for stamp, row in bars.iterrows():
        day = stamp.date()
        iso = day.isoformat()
        volume = row["volume"]
        prices = [row[column] for column in ("open", "high", "low", "close")]
        halted = any(item.covers(day) for item in halts)

        closed = False
        if calendar is not None:
            if not calendar.covered_from <= day <= calendar.covered_until:
                uncovered.append(iso)
            elif not calendar.is_session(day):
                off_calendar.append(iso)
                closed = True

        if pd.isna(volume):
            continue
        if volume > 0:
            if halted:
                traded_halted.append(iso)
            last_traded_close = row["close"]
            continue
        if volume != 0:
            continue
        if last_traded_close is not None and any(price != last_traded_close for price in prices):
            price_change.append(iso)
        elif not closed and len(set(prices)) == 1:
            flat_zero.append(
                {
                    "date": iso,
                    "status": "suspended" if halted else "untraded_or_suspended",
                }
            )

    missing: list[str] | None = None
    if calendar is not None:
        missing = []
        if not bars.empty:
            present = {stamp.date() for stamp in bars.index}
            first, last = bars.index[0].date(), bars.index[-1].date()
            missing = sorted(
                day.isoformat() for day in calendar.sessions if first <= day <= last and day not in present
            )

    return {
        "policy": POLICY,
        "symbol": symbol,
        "bar_count": len(bars),
        "calendar_verified": calendar is not None,
        "calendar_source": calendar.source if calendar is not None else None,
        "suspension_sources": sorted({item.source for item in halts}),
        "off_calendar_dates": off_calendar if calendar is not None else None,
        "uncovered_dates": uncovered if calendar is not None else None,
        "missing_session_dates": missing,
        "zero_volume_flat_bars": flat_zero,
        "zero_volume_price_change_dates": price_change,
        "traded_during_suspension_dates": traded_halted,
    }


SERIES_EVENT_POLICY = "idx_series_event_audit_v1"


def _price(value: Any) -> float | None:
    """A finite price as float, else None (missing is unknown, never zero)."""
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return number if np.isfinite(number) else None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    ratio = numerator / denominator
    return ratio if np.isfinite(ratio) else None


def _symbol_records(records: Any, record_type: type, name: str, symbol: str) -> list[Any]:
    if not isinstance(records, tuple) or any(not isinstance(item, record_type) for item in records):
        raise ValueError(f"{name} must be a tuple of {record_type.__name__} records")
    return [item for item in records if item.symbol == symbol]


def _series_end(
    bars: pd.DataFrame,
    as_of: date,
    calendar: IDXSessionCalendar | None,
    halts: list[IDXSuspension],
    delisting: IDXDelisting | None,
) -> dict[str, Any]:
    last_bar = bars.index[-1].date() if not bars.empty else None
    if last_bar is not None and as_of < last_bar:
        raise ValueError("as_of precedes the last bar")
    delisted = delisting is not None and delisting.effective_day <= as_of

    sessions_after: int | None = None
    gap: list[date] = []
    covered = False
    if calendar is not None and last_bar is not None:
        covered = calendar.covered_from <= last_bar and as_of <= calendar.covered_until
        if covered:
            gap = sorted(day for day in calendar.sessions if last_bar < day <= as_of)
            sessions_after = len(gap)

    if delisted:
        status = "delisted"
    elif last_bar is None:
        status = "no_bars"
    elif calendar is None:
        status = "unverified"
    elif not covered:
        status = "uncovered"
    elif not gap:
        status = "current"
    elif all(any(item.covers(day) for item in halts) for day in gap):
        status = "suspended"
    else:
        status = "ended_or_stale"

    return {
        "as_of": as_of.isoformat(),
        "last_bar_date": last_bar.isoformat() if last_bar is not None else None,
        "status": status,
        "sessions_after_last_bar": sessions_after,
        "delisting_effective_date": delisting.effective_day.isoformat() if delisted else None,
    }


def _ex_date_move(bars: pd.DataFrame, action: IDXCorporateAction, adjusted: bool) -> dict[str, Any]:
    stamp = pd.Timestamp(action.ex_day)
    earlier = bars.loc[bars.index < stamp]
    previous = earlier.iloc[-1] if not earlier.empty else None
    current = bars.loc[stamp] if stamp in bars.index else None

    previous_close = _price(previous["close"]) if previous is not None else None
    close = _price(current["close"]) if current is not None else None
    previous_factor = factor = None
    if adjusted:
        if previous is not None:
            previous_factor = _ratio(_price(previous["adjusted_close"]), previous_close)
        if current is not None:
            factor = _ratio(_price(current["adjusted_close"]), close)
    return {
        "ex_date": action.ex_day.isoformat(),
        "kind": action.kind,
        "source": action.source,
        "bar_present": current is not None,
        "previous_bar_date": earlier.index[-1].date().isoformat() if previous is not None else None,
        "previous_close": previous_close,
        "close": close,
        "close_ratio": _ratio(close, previous_close),
        "previous_adjustment_factor": previous_factor,
        "adjustment_factor": factor,
    }


def audit_series_events(
    symbol: str,
    frame: pd.DataFrame,
    *,
    as_of: date | None = None,
    calendar: IDXSessionCalendar | None = None,
    suspensions: tuple[IDXSuspension, ...] = (),
    delistings: tuple[IDXDelisting, ...] = (),
    corporate_actions: tuple[IDXCorporateAction, ...] = (),
) -> dict[str, Any]:
    """Report where a series ends, its age in sessions and prices around supplied ex dates.

    Findings:

    - ``series_end`` (``None`` without ``as_of``): the last bar, the number of
      calendar sessions after it up to ``as_of`` (``None`` without a calendar
      or outside its coverage) and a ``status``:
      ``delisted`` only from a supplied record effective on or before
      ``as_of``; ``no_bars``; ``unverified`` (no calendar); ``uncovered``;
      ``current`` (no session missed); ``suspended`` (every missed session
      inside a supplied suspension); otherwise ``ended_or_stale``, because
      bars alone cannot tell a series that ended from stale data.
    - ``bars_after_delisting_dates``: bars on or after a supplied delisting.
    - ``ex_date_moves``: one entry per supplied corporate action, with the
      previous and ex-date closes, their ratio and, when an
      ``adjusted_close`` column is present, ``adjusted_close``/``close`` on
      both bars. Raw series show the jump; adjusted ones do not. No ratio is
      compared with an expected entitlement and no price is adjusted.

    Nothing is filled, dropped or modified, and no calendar, delisting or
    corporate-action list is built in.
    """
    _require_idx_symbol(symbol)
    bars = _validated_frame(frame)
    adjusted = "adjusted_close" in bars.columns
    if adjusted and bars.columns.tolist().count("adjusted_close") != 1:
        raise ValueError("At most one adjusted_close column is allowed")
    if as_of is not None and type(as_of) is not date:
        raise ValueError("as_of must be a calendar date")
    if calendar is not None and not isinstance(calendar, IDXSessionCalendar):
        raise ValueError("calendar must be an IDXSessionCalendar")
    halts = _symbol_records(suspensions, IDXSuspension, "suspensions", symbol)
    removals = _symbol_records(delistings, IDXDelisting, "delistings", symbol)
    actions = _symbol_records(corporate_actions, IDXCorporateAction, "corporate_actions", symbol)
    if len(removals) > 1:
        raise ValueError("More than one delisting record for the symbol")
    delisting = removals[0] if removals else None

    after_delisting: list[str] = []
    if delisting is not None:
        after_delisting = [stamp.date().isoformat() for stamp in bars.index if stamp.date() >= delisting.effective_day]

    return {
        "policy": SERIES_EVENT_POLICY,
        "symbol": symbol,
        "bar_count": len(bars),
        "calendar_verified": calendar is not None,
        "calendar_source": calendar.source if calendar is not None else None,
        "suspension_sources": sorted({item.source for item in halts}),
        "delisting_sources": [delisting.source] if delisting is not None else [],
        "corporate_action_sources": sorted({item.source for item in actions}),
        "adjusted_close_supplied": adjusted,
        "series_end": _series_end(bars, as_of, calendar, halts, delisting) if as_of is not None else None,
        "bars_after_delisting_dates": after_delisting,
        "ex_date_moves": [
            _ex_date_move(bars, action, adjusted) for action in sorted(actions, key=lambda item: item.ex_day)
        ],
    }
