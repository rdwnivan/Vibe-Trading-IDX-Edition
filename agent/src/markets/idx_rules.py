"""Versioned, explicitly supplied Regular Market rules; no implicit defaults.

These reference primitives do not enable an execution engine. A complete
historical rulebook also needs price limits, board exceptions, fees/taxes,
settlement, suspensions and corporate actions before simulation can run.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class IDXRegularRules:
    """One sourced effective interval, inclusive at both ends.

    Tick tiers are (inclusive lower price, increment), in IDR. The reference
    price is the prior session close, not the requested order price. Callers
    supply independently verified dates; an observation date is insufficient.
    """

    version: str
    source: str
    effective_from: date
    effective_until: date
    lot_shares: int
    tick_tiers: tuple[tuple[Decimal, Decimal], ...]

    def __post_init__(self) -> None:
        if not self.version.strip() or not self.source.strip():
            raise ValueError("Rule version and official source are required")
        if type(self.effective_from) is not date or type(self.effective_until) is not date:
            raise ValueError("Rule coverage requires calendar dates")
        if self.effective_until < self.effective_from:
            raise ValueError("Rule effective interval is reversed")
        if type(self.lot_shares) is not int or self.lot_shares <= 0:
            raise ValueError("Lot size must be a positive integer number of shares")
        if not isinstance(self.tick_tiers, tuple) or not self.tick_tiers:
            raise ValueError("Tick tiers must be a nonempty immutable tuple")
        if any(not isinstance(tier, tuple) or len(tier) != 2 for tier in self.tick_tiers):
            raise ValueError("Each tick tier must be an immutable pair")
        prior = None
        for lower, tick in self.tick_tiers:
            if not isinstance(lower, Decimal) or not isinstance(tick, Decimal):
                raise ValueError("Tick tiers require Decimal IDR amounts")
            if not lower.is_finite() or not tick.is_finite() or tick <= 0:
                raise ValueError("Tick tiers must have finite prices and positive increments")
            if (prior is None and lower != 0) or (prior is not None and lower <= prior):
                raise ValueError("Tick tiers must start at zero and increase strictly")
            prior = lower

    def tick_size(self, previous_close: Decimal, *, session_date: date) -> Decimal:
        """Select the daily tick tier without guessing outside rule coverage."""
        if not self.effective_from <= session_date <= self.effective_until:
            raise ValueError("IDX session is outside this rule version's effective interval")
        if not isinstance(previous_close, Decimal) or not previous_close.is_finite() or previous_close <= 0:
            raise ValueError("Previous close must be a positive finite Decimal in IDR")
        return next(tick for lower, tick in reversed(self.tick_tiers) if previous_close >= lower)

    def shares_from_lots(self, lots: int) -> int:
        """Convert explicit lot units without rounding fractional orders."""
        if type(lots) is not int or lots < 0:
            raise ValueError("Lots must be a non-negative integer")
        return lots * self.lot_shares


@dataclass(frozen=True)
class IDXSessionCalendar:
    """Complete, supplied session dates for a bounded official calendar.

    Missing days inside coverage are closed; outside coverage is unknown and
    raises. It never infers holidays or suspensions from missing price bars.
    """

    source: str
    covered_from: date
    covered_until: date
    sessions: frozenset[date]

    def __post_init__(self) -> None:
        if type(self.covered_from) is not date or type(self.covered_until) is not date:
            raise ValueError("Calendar coverage requires calendar dates")
        if not self.source.strip() or self.covered_until < self.covered_from:
            raise ValueError("Calendar requires a source and valid coverage")
        if not isinstance(self.sessions, frozenset):
            raise ValueError("Calendar sessions must be an immutable frozenset")
        if any(type(day) is not date for day in self.sessions):
            raise ValueError("Calendar sessions require calendar dates")
        if any(not self.covered_from <= day <= self.covered_until for day in self.sessions):
            raise ValueError("Calendar sessions extend outside declared coverage")

    def is_session(self, day: date) -> bool:
        """Return known session status; refuse an uncovered date."""
        if not self.covered_from <= day <= self.covered_until:
            raise ValueError("IDX date is outside verified calendar coverage")
        return day in self.sessions
