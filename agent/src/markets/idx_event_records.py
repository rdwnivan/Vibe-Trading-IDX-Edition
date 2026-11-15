"""Load caller-supplied, sourced IDX event records from a JSON file.

The file holds suspensions, delistings and corporate actions that the caller
has taken from dated sources. This module only parses and validates it into
the records used by ``idx_bar_quality``; it ships no records, fills no gaps
and infers nothing from prices. Errors name the group and entry index but
never echo raw values from the file.

Format (``schema`` is required; each group is optional and defaults to none)::

    {
      "schema": "idx_event_records_v1",
      "suspensions": [{"symbol": "XXXX.JK", "source": "...", "first_day": "YYYY-MM-DD", "last_day": "YYYY-MM-DD"}],
      "delistings": [{"symbol": "XXXX.JK", "source": "...", "effective_day": "YYYY-MM-DD"}],
      "corporate_actions": [{"symbol": "XXXX.JK", "source": "...", "kind": "cash_dividend", "ex_day": "YYYY-MM-DD"}]
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re
from typing import Any, Callable

from src.markets.idx_bar_quality import IDXCorporateAction, IDXDelisting, IDXSuspension

SCHEMA = "idx_event_records_v1"
_ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class IDXEventRecords:
    suspensions: tuple[IDXSuspension, ...]
    delistings: tuple[IDXDelisting, ...]
    corporate_actions: tuple[IDXCorporateAction, ...]


def _day(value: Any) -> date:
    if not isinstance(value, str) or not _ISO_DAY.match(value):
        raise ValueError("dates must be YYYY-MM-DD strings")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("date is not a calendar date") from None


def _suspension(entry: dict[str, Any]) -> IDXSuspension:
    return IDXSuspension(
        symbol=entry["symbol"],
        source=entry["source"],
        first_day=_day(entry["first_day"]),
        last_day=_day(entry["last_day"]),
    )


def _delisting(entry: dict[str, Any]) -> IDXDelisting:
    return IDXDelisting(symbol=entry["symbol"], source=entry["source"], effective_day=_day(entry["effective_day"]))


def _corporate_action(entry: dict[str, Any]) -> IDXCorporateAction:
    return IDXCorporateAction(
        symbol=entry["symbol"], source=entry["source"], kind=entry["kind"], ex_day=_day(entry["ex_day"])
    )


_GROUPS: dict[str, tuple[frozenset[str], Callable[[dict[str, Any]], Any]]] = {
    "suspensions": (frozenset({"symbol", "source", "first_day", "last_day"}), _suspension),
    "delistings": (frozenset({"symbol", "source", "effective_day"}), _delisting),
    "corporate_actions": (frozenset({"symbol", "source", "kind", "ex_day"}), _corporate_action),
}


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("Event-record file has a duplicate JSON key")
    return dict(pairs)


def _refuse_constant(_: str) -> Any:
    raise ValueError("Event-record file contains a non-finite number")


def _read(path: Path) -> Any:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise ValueError("Event-record file cannot be read as UTF-8") from None
    try:
        return json.loads(text, object_pairs_hook=_unique_keys, parse_constant=_refuse_constant)
    except json.JSONDecodeError:
        raise ValueError("Event-record file is not valid JSON") from None


def _load_group(name: str, entries: Any) -> tuple[Any, ...]:
    fields, build = _GROUPS[name]
    if not isinstance(entries, list):
        raise ValueError(f"{name} must be a list")
    records = []
    for index, entry in enumerate(entries):
        where = f"{name}[{index}]"
        if not isinstance(entry, dict) or set(entry) != fields:
            raise ValueError(f"{where} must have exactly the fields {', '.join(sorted(fields))}")
        try:
            record = build(entry)
        except ValueError as exc:
            # Record and date errors are fixed messages; they carry no raw value.
            raise ValueError(f"{where} is invalid: {exc}") from None
        if record in records:
            raise ValueError(f"{where} duplicates an earlier record")
        records.append(record)
    return tuple(records)


def load_event_records(path: str | Path) -> IDXEventRecords:
    """Parse one event-record file; refuse the whole file on any invalid entry."""
    document = _read(Path(path))
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise ValueError(f"Event-record file must be an object with schema {SCHEMA}")
    unknown = set(document) - {"schema", *_GROUPS}
    if unknown:
        raise ValueError("Event-record file has unknown top-level keys")
    groups = {name: _load_group(name, document[name]) if name in document else () for name in _GROUPS}
    symbols = [item.symbol for item in groups["delistings"]]
    if len(symbols) != len(set(symbols)):
        raise ValueError("delistings has more than one record for a symbol")
    return IDXEventRecords(**groups)
