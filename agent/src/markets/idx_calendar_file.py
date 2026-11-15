"""Load a caller-supplied, sourced IDX session calendar from a JSON file.

The file lists every session inside a bounded coverage window, taken by the
caller from a dated source; days inside coverage that are not listed are
closed. This module only parses and validates the file into
``IDXSessionCalendar``. It ships no calendar and assumes no weekday, holiday
or half-day rule. Errors never echo raw values from the file.

Format (every field is required)::

    {
      "schema": "idx_session_calendar_v1",
      "source": "...",
      "covered_from": "YYYY-MM-DD",
      "covered_until": "YYYY-MM-DD",
      "sessions": ["YYYY-MM-DD", ...]
    }

``sessions`` must be strictly ascending, so a repeated or misplaced date is
refused instead of silently merged.
"""

from __future__ import annotations

from pathlib import Path

from src.markets.idx_event_records import parse_iso_day, read_strict_json
from src.markets.idx_rules import IDXSessionCalendar

SCHEMA = "idx_session_calendar_v1"
_FIELDS = frozenset({"schema", "source", "covered_from", "covered_until", "sessions"})


def load_session_calendar(path: str | Path) -> IDXSessionCalendar:
    """Parse one calendar file; refuse it on any invalid or missing field."""
    document = read_strict_json(Path(path))
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise ValueError(f"Calendar file must be an object with schema {SCHEMA}")
    if set(document) != _FIELDS:
        raise ValueError(f"Calendar file must have exactly the fields {', '.join(sorted(_FIELDS))}")
    if not isinstance(document["source"], str):
        raise ValueError("Calendar source must be a string")
    try:
        covered_from = parse_iso_day(document["covered_from"])
        covered_until = parse_iso_day(document["covered_until"])
    except ValueError as exc:
        raise ValueError(f"Calendar coverage is invalid: {exc}") from None

    entries = document["sessions"]
    if not isinstance(entries, list):
        raise ValueError("Calendar sessions must be a list")
    sessions = []
    for index, entry in enumerate(entries):
        try:
            day = parse_iso_day(entry)
        except ValueError as exc:
            raise ValueError(f"sessions[{index}] is invalid: {exc}") from None
        if sessions and day <= sessions[-1]:
            raise ValueError(f"sessions[{index}] is not after the previous session")
        sessions.append(day)

    # IDXSessionCalendar checks the source, coverage order and session bounds.
    return IDXSessionCalendar(
        source=document["source"],
        covered_from=covered_from,
        covered_until=covered_until,
        sessions=frozenset(sessions),
    )
