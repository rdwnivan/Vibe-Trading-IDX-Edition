"""Read-only audit of vendor daily bars for IDX data-quality hazards.

Vendors have been seen to emit zero-volume rows on exchange holidays, some
with a placeholder price, and to fill a full-day trading halt with the prior
close and zero volume, without marking either. This module reports such bars;
it never drops, repairs or fills them.

Calendars and suspensions must be supplied by the caller from dated sources.
Nothing here holds or infers an IDX calendar, holiday or suspension. Without a
calendar, calendar checks are reported as not run (``None``), not as clean.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

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
