"""Read-only import of explicitly supplied IDX reference JSON snapshots.

Validation proves structure, not authenticity, licensing or market coverage.
No download, persistence, global registry mutation or execution enablement.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from src.markets.idx import IDXInstrument, IDXInstrumentRegistry
from src.markets.idx_rules import IDXRegularRules, IDXSessionCalendar


def _object(value: Any, required: set[str], optional: set[str] | None = None) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    if required - value.keys() or value.keys() - required - (optional or set()):
        raise ValueError("Snapshot has missing or unsupported fields")
    return value


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Snapshot text fields must be nonempty strings")
    return value.strip()


def _date(value: Any) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Snapshot dates must use YYYY-MM-DD")
    return date.fromisoformat(value)


def _list(value: Any) -> list:
    if not isinstance(value, list) or not value:
        raise ValueError("Snapshot collections must be nonempty lists")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field in snapshot")
        result[key] = value
    return result


@dataclass(frozen=True)
class IDXReferenceSnapshot:
    """Validated local artifact and its source declarations.

    The SHA-256 identifies exact imported bytes; it is not an official signature.
    Source/terms declarations are supplied by the exporter, never certified here.
    """

    kind: str
    source: str
    retrieved_at: datetime
    usage_terms: str
    sha256: str
    data: IDXInstrumentRegistry | IDXSessionCalendar | IDXRegularRules
    record_count: int


def load_idx_reference(path: str | Path) -> IDXReferenceSnapshot:
    """Load a version-1 artifact, refusing ambiguity and invalid coverage.

    Args:
        path: Local normalized JSON exported from an authorized source.

    Returns:
        Source declarations and existing IDX domain objects, without side effects.

    Raises:
        ValueError: Invalid schema, dates, units, duplicates or domain values.
        OSError: The supplied file cannot be read.
    """
    raw = Path(path).read_bytes()
    root = _object(
        json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object),
        {
            "schema_version",
            "kind",
            "market",
            "currency",
            "timezone",
            "source",
            "retrieved_at",
            "usage_terms",
            "payload",
        },
    )
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise ValueError("Unsupported IDX reference schema_version")
    if (root["market"], root["currency"], root["timezone"]) != ("id_equity", "IDR", "Asia/Jakarta"):
        raise ValueError("IDX reference requires id_equity, IDR and Asia/Jakarta")
    source = _text(root["source"])
    terms = _text(root["usage_terms"])
    retrieved = datetime.fromisoformat(_text(root["retrieved_at"]))
    if retrieved.tzinfo is None or retrieved.utcoffset() is None:
        raise ValueError("retrieved_at must include a timezone offset")
    kind = root["kind"]
    payload = root["payload"]
    if kind == "instruments":
        payload = _object(payload, {"as_of", "instruments"})
        as_of = _date(payload["as_of"])
        instruments = []
        for row in _list(payload["instruments"]):
            row = _object(row, {"symbol", "name"}, {"sector", "industry"})
            instruments.append(
                IDXInstrument(
                    symbol=_text(row["symbol"]),
                    name=_text(row["name"]),
                    source=source,
                    as_of=as_of,
                    sector=_text(row["sector"]) if "sector" in row else None,
                    industry=_text(row["industry"]) if "industry" in row else None,
                )
            )
        data = IDXInstrumentRegistry(instruments)
        count = len(instruments)
    elif kind == "calendar":
        payload = _object(payload, {"covered_from", "covered_until", "sessions", "complete"})
        if payload["complete"] is not True:
            raise ValueError("Calendar must declare complete session coverage")
        sessions = [_date(day) for day in _list(payload["sessions"])]
        if len(set(sessions)) != len(sessions):
            raise ValueError("Duplicate calendar session")
        data = IDXSessionCalendar(
            source=source,
            covered_from=_date(payload["covered_from"]),
            covered_until=_date(payload["covered_until"]),
            sessions=frozenset(sessions),
        )
        count = len(sessions)
    elif kind == "regular_rules":
        payload = _object(payload, {"version", "effective_from", "effective_until", "lot_shares", "tick_tiers"})
        tiers = []
        for tier in _list(payload["tick_tiers"]):
            if not isinstance(tier, list) or len(tier) != 2:
                raise ValueError("Tick tiers require pairs of decimal strings")
            try:
                tiers.append((Decimal(_text(tier[0])), Decimal(_text(tier[1]))))
            except InvalidOperation as exc:
                raise ValueError("Tick tiers require decimal strings") from exc
        data = IDXRegularRules(
            version=_text(payload["version"]),
            source=source,
            effective_from=_date(payload["effective_from"]),
            effective_until=_date(payload["effective_until"]),
            lot_shares=payload["lot_shares"],
            tick_tiers=tuple(tiers),
        )
        count = 1
    else:
        raise ValueError("Unsupported IDX reference kind")
    return IDXReferenceSnapshot(
        kind=kind,
        source=source,
        retrieved_at=retrieved,
        usage_terms=terms,
        sha256=hashlib.sha256(raw).hexdigest(),
        data=data,
        record_count=count,
    )


def main(argv: list[str] | None = None) -> int:
    """Validate a local artifact and print counts/hash without dumping records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Authorized normalized IDX JSON snapshot")
    args = parser.parse_args(argv)
    try:
        snapshot = load_idx_reference(args.path)
    except (OSError, ValueError, UnicodeError):
        # Do not echo input records, private paths or raw source declarations.
        parser.exit(2, "Invalid IDX reference snapshot; check file access and documented schema.\n")
    print(
        json.dumps(
            {
                "kind": snapshot.kind,
                "records": snapshot.record_count,
                "sha256": snapshot.sha256,
                "validation": "structure_only",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
