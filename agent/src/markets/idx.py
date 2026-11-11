"""Verified IDX reference snapshots, without an invented built-in universe.

Callers import a licensed/official snapshot and explicitly resolve bare tickers
here. General market classification must continue to use _market_hooks.
"""

from dataclasses import dataclass
from datetime import date
import re


@dataclass(frozen=True)
class IDXInstrument:
    """One regular share in a source snapshot (not a historical universe)."""

    symbol: str
    name: str
    source: str
    as_of: date
    sector: str | None = None
    industry: str | None = None

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        if not re.fullmatch(r"[A-Z]{4}\.JK", symbol):
            raise ValueError("IDX regular-share symbols must use the form BBCA.JK")
        if not self.name.strip() or not self.source.strip():
            raise ValueError("IDX instruments require a name and reference-data source")
        if not isinstance(self.as_of, date):
            raise ValueError("IDX instruments require a snapshot date")
        object.__setattr__(self, "symbol", symbol)


class IDXInstrumentRegistry:
    """Explicit IDX-context resolution against a supplied, dated snapshot.

    No I/O, network lookups or global mutation. Absence raises instead of
    guessing a listing. A snapshot cannot establish past index membership,
    listing history, suspension status or present tradability.
    """

    def __init__(self, instruments: list[IDXInstrument]):
        self._instruments: dict[str, IDXInstrument] = {}
        for instrument in instruments:
            if instrument.symbol in self._instruments:
                raise ValueError(f"Duplicate IDX instrument: {instrument.symbol}")
            self._instruments[instrument.symbol] = instrument

    def resolve(self, ticker: str, *, as_of: date) -> IDXInstrument:
        """Resolve a bare/canonical ticker only for the exact snapshot date."""
        symbol = ticker.strip().upper()
        if re.fullmatch(r"[A-Z]{4}", symbol):
            symbol += ".JK"
        instrument = self._instruments.get(symbol)
        if instrument is None:
            raise ValueError(f"IDX instrument is unverified: {ticker!r}")
        if instrument.as_of != as_of:
            raise ValueError(f"IDX snapshot for {symbol} is dated {instrument.as_of}, not {as_of}")
        return instrument
