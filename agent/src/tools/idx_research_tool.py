"""Bounded personal IDX watchlist research through the existing data pipeline."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
import json
import logging
import math
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from backtest.engines._market_hooks import _detect_market
from backtest.loaders.base import validate_ohlc
from src.agent.tools import BaseTool
from src.config.accessor import get_env_config
from src.market_data import fetch_market_data
from src.markets.idx_bar_quality import audit_daily_bars, audit_series_events
from src.markets.idx_calendar_file import load_session_calendar
from src.markets.idx_event_records import IDXEventRecords, load_event_records
from src.markets.idx_rules import IDXSessionCalendar
from src.tools.technical_indicator_tool import summarize_technical_data_json

logger = logging.getLogger(__name__)
MAX_SYMBOLS = 8
DEFAULT_LOOKBACK = 200
MAX_LOOKBACK = 500
# Personal research alarm only, independent of loader-health availability gates.
# Calendar age cannot establish missing sessions, suspension, or provider delay.
RECENCY_WARNING_DAYS = 14
# Acquisition metadata is a few levels deep. Bound nesting explicitly: from
# Python 3.14 the C JSON encoder checks the real stack, so deep containers
# no longer raise RecursionError and cannot be relied on to fail.
MAX_METADATA_DEPTH = 64


def _exceeds_depth(value: Any, limit: int = MAX_METADATA_DEPTH) -> bool:
    """Return True when dict/list/tuple nesting exceeds ``limit`` (iterative, cycle-safe)."""
    stack = [(value, 1)]
    seen: set[int] = set()
    while stack:
        current, depth = stack.pop()
        if not isinstance(current, (dict, list, tuple)):
            continue
        if depth > limit:
            return True
        if id(current) in seen:
            continue  # cycles are rejected by json.dumps itself
        seen.add(id(current))
        children = current.values() if isinstance(current, dict) else current
        stack.extend((child, depth + 1) for child in children)
    return False


def _is_json_metadata(value: Any) -> bool:
    """True when ``value`` is bounded, strict JSON (no NaN/Infinity, cycles or foreign types)."""
    if _exceeds_depth(value):
        return False
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        return False
    return True


def _failure(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


SOURCED_REFERENCE_POLICY = "idx_sourced_reference_v1"
SOURCED_AUDIT_POLICY = "idx_sourced_audit_v1"
_UNAVAILABLE = {"status": "unavailable", "issue": "unreadable_or_invalid"}


def _load_sourced_reference() -> tuple[dict[str, Any] | None, IDXSessionCalendar | None, IDXEventRecords | None]:
    """Load the opt-in calendar and event-record files named by env.

    Returns ``(None, None, None)`` when neither is configured, so the response
    is unchanged. A file that cannot be read or validated degrades to
    ``unavailable`` on its own; neither its path nor its content is echoed.
    """
    data = get_env_config().data
    calendar_path = data.vibe_trading_idx_calendar_path.strip()
    records_path = data.vibe_trading_idx_event_records_path.strip()
    if not calendar_path and not records_path:
        return None, None, None

    calendar: IDXSessionCalendar | None = None
    calendar_state: dict[str, Any] = {"status": "not_configured"}
    if calendar_path:
        try:
            calendar = load_session_calendar(Path(calendar_path).expanduser())
        except (ValueError, OSError) as exc:
            logger.warning("IDX research sourced calendar unavailable (%s)", type(exc).__name__)
            calendar_state = dict(_UNAVAILABLE)
        else:
            calendar_state = {
                "status": "loaded",
                "source": calendar.source,
                "covered_from": calendar.covered_from.isoformat(),
                "covered_until": calendar.covered_until.isoformat(),
            }

    records: IDXEventRecords | None = None
    records_state: dict[str, Any] = {"status": "not_configured"}
    if records_path:
        try:
            records = load_event_records(Path(records_path).expanduser())
        except (ValueError, OSError) as exc:
            logger.warning("IDX research sourced event records unavailable (%s)", type(exc).__name__)
            records_state = dict(_UNAVAILABLE)
        else:
            records_state = {
                "status": "loaded",
                "suspension_count": len(records.suspensions),
                "delisting_count": len(records.delistings),
                "corporate_action_count": len(records.corporate_actions),
            }

    reference = {"policy": SOURCED_REFERENCE_POLICY, "calendar": calendar_state, "event_records": records_state}
    return reference, calendar, records


def _sourced_audit(
    code: str,
    frame: pd.DataFrame,
    window_start: str,
    end: date,
    calendar: IDXSessionCalendar | None,
    records: IDXEventRecords | None,
) -> dict[str, Any]:
    """Calendar, suspension, series-end and ex-date findings from supplied files, inside the window."""
    suspensions = records.suspensions if records is not None else ()
    daily = audit_daily_bars(code, frame, calendar=calendar, suspensions=suspensions)
    events = audit_series_events(
        code,
        frame,
        as_of=end,
        calendar=calendar,
        suspensions=suspensions,
        delistings=records.delistings if records is not None else (),
        corporate_actions=records.corporate_actions if records is not None else (),
    )

    def windowed(days: list[str] | None) -> list[str] | None:
        return None if days is None else [day for day in days if day >= window_start]

    return {
        "policy": SOURCED_AUDIT_POLICY,
        "calendar_verified": calendar is not None,
        "off_calendar_dates": windowed(daily["off_calendar_dates"]),
        "uncovered_dates": windowed(daily["uncovered_dates"]),
        "missing_session_dates": windowed(daily["missing_session_dates"]),
        "zero_volume_flat_bars": [bar for bar in daily["zero_volume_flat_bars"] if bar["date"] >= window_start],
        "traded_during_suspension_dates": windowed(daily["traded_during_suspension_dates"]),
        "suspension_sources": daily["suspension_sources"],
        "series_end": events["series_end"],
        "bars_after_delisting_dates": windowed(events["bars_after_delisting_dates"]),
        "delisting_sources": events["delisting_sources"],
        "ex_date_moves": [move for move in events["ex_date_moves"] if move["ex_date"] >= window_start],
    }


class IDXResearchTool(BaseTool):
    """Acquire once, then derive charts and indicators from the same bars."""

    name = "idx_research"
    description = (
        "Personal read-only IDX daily watchlist research. Supply explicit .JK "
        "regular-share symbols (maximum 8). Returns chart OHLCV, existing technical "
        "indicators and actual serving provenance; unavailable symbols remain visible. "
        "Includes calendar-age recency warnings relative to the requested end date. "
        "Reports available, missing and zero-volume counts over the analyzed bars, "
        "and lists zero-volume bars whose price differs from the last traded close. "
        "When the operator configures sourced calendar or event-record files, also "
        "reports calendar findings, suspensions, series end in sessions and ex-date moves. "
        "Not an official instrument universe, calendar or backtest."
    )
    parameters = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "codes": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_SYMBOLS},
            "lookback": {"type": "integer", "minimum": 20, "maximum": MAX_LOOKBACK, "default": DEFAULT_LOOKBACK},
            "end_date": {"type": "string", "description": "YYYY-MM-DD; defaults to Jakarta today"},
        },
        "required": ["codes"],
    }
    is_readonly = True
    repeatable = True

    def execute(self, **kwargs: Any) -> str:
        """Return a bounded watchlist with per-symbol failures and no invented bars."""
        codes = kwargs.get("codes")
        if not isinstance(codes, list) or not 1 <= len(codes) <= MAX_SYMBOLS:
            return _failure(f"codes must contain 1–{MAX_SYMBOLS} explicit .JK symbols")
        if any(not isinstance(code, str) for code in codes):
            return _failure("every code must be a string")
        codes = [code.strip().upper() for code in codes]
        try:
            if any(_detect_market(code) != "id_equity" or code.startswith("LOCAL:") for code in codes):
                return _failure("use explicit regular-share .JK symbols, for example BBCA.JK")
        except ValueError:
            return _failure("unsupported IDX symbol; use regular-share .JK symbols")
        if len(set(codes)) != len(codes):
            return _failure("duplicate symbols are not allowed")
        lookback = kwargs.get("lookback", DEFAULT_LOOKBACK)
        if type(lookback) is not int or not 20 <= lookback <= MAX_LOOKBACK:
            return _failure(f"lookback must be an integer from 20 to {MAX_LOOKBACK}")
        raw_end = kwargs.get("end_date")
        try:
            end = date.fromisoformat(raw_end) if raw_end is not None else datetime.now(ZoneInfo("Asia/Jakarta")).date()
            if raw_end is not None and end.isoformat() != raw_end:
                return _failure("end_date must use YYYY-MM-DD")
        except (TypeError, ValueError):
            return _failure("end_date must use YYYY-MM-DD")
        try:
            start = end - timedelta(days=lookback * 2)
        except OverflowError:
            return _failure("end_date is too early for the requested lookback")
        try:
            data = fetch_market_data(
                codes=codes,
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                source="auto",
                interval="1D",
                max_rows=0,
                include_provenance=True,
                as_frames=True,
            )
            if not isinstance(data, dict):
                raise TypeError("market data acquisition must return an object")
        except Exception as exc:
            logger.warning("IDX research acquisition failed (%s)", type(exc).__name__)
            return _failure("market data acquisition failed; retry later or check loader configuration")

        # Opt-in sourced files are read once per request; without env the
        # response carries no new field and bar_audit v1 is unchanged.
        sourced_reference, sourced_calendar, sourced_records = _load_sourced_reference()

        items = []
        provenance_by_code = data.get("_provenance")
        for code in codes:
            # Malformed/missing declarations are rejected by the existing
            # per-symbol currency gate, never repaired from frame attributes.
            provenance = provenance_by_code.get(code) if isinstance(provenance_by_code, dict) else None
            if not isinstance(provenance, dict):
                provenance = None
            else:
                # Provenance is returned even for unavailable symbols and is
                # also embedded in the indicator read identity. Reject a broken
                # declaration before either path can poison watchlist JSON.
                if not _is_json_metadata(provenance):
                    logger.warning("IDX research invalid acquisition provenance for %s", code)
                    provenance = None
            frame = data.get(code)
            item: dict[str, Any] = {"symbol": code, "status": "unavailable", "provenance": provenance}
            if not isinstance(frame, pd.DataFrame) or frame.empty:
                # Diagnostics are optional acquisition metadata. Malformed
                # containers/entries must not discard healthy watchlist peers
                # or pass arbitrary non-object values into the JSON response.
                diagnostics_by_code = data.get("_diagnostics")
                diagnostics = diagnostics_by_code.get(code) if isinstance(diagnostics_by_code, dict) else None
                if (diagnostics_by_code is not None and not isinstance(diagnostics_by_code, dict)) or (
                    diagnostics is not None and not isinstance(diagnostics, dict)
                ):
                    logger.warning("IDX research invalid acquisition diagnostics for %s", code)
                    diagnostics = None
                elif diagnostics is not None:
                    # An object can still contain non-JSON values, nonfinite
                    # numbers or cycles. Isolate optional metadata failure here
                    # before serializing the whole watchlist; never stringify
                    # arbitrary values or expose serializer exception messages.
                    if not _is_json_metadata(diagnostics):
                        logger.warning("IDX research invalid acquisition diagnostics for %s", code)
                        diagnostics = None
                item.update(reason="no_data_or_source_failure", diagnostics=diagnostics)
                items.append(item)
                continue
            try:
                # Stable stage codes only: never expose provider values or raw
                # exception messages in validation diagnostics or warning logs.
                issue_code = "currency_declaration"
                if not isinstance(provenance, dict) or provenance.get("quote_currency") != "IDR":
                    raise ValueError("declared IDR currency is required")
                issue_code = "instrument_identity"
                # Older observations may omit these optional declarations, but
                # a present value must agree with the requested instrument.
                # Never repair a conflicting identity or borrow another symbol.
                for field, expected in (("symbol", code), ("market", _detect_market(code)), ("exchange", "IDX")):
                    if field in provenance and provenance[field] != expected:
                        raise ValueError("declared instrument identity must match the request")
                issue_code = "session_timezone"
                if provenance.get("exchange_timezone") != "Asia/Jakarta":
                    raise ValueError("Jakarta session-date metadata is required")
                issue_code = "daily_interval"
                if provenance.get("interval") != "1D":
                    raise ValueError("daily interval metadata is required")
                issue_code = "share_volume_unit"
                if provenance.get("volume_unit") != "shares":
                    raise ValueError("declared share-volume units are required")
                # Unknown is an explicit declaration, unlike missing metadata.
                # Keep the serving label; never infer or apply corporate actions.
                issue_code = "adjustment_declaration"
                adjustment = provenance.get("adjustment")
                if not isinstance(adjustment, str) or not adjustment.strip():
                    raise ValueError("declared price adjustment is required")
                issue_code = "unique_bar_dates"
                if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.hasnans or frame.index.has_duplicates:
                    raise ValueError("unique dated bars are required")
                issue_code = "local_session_dates"
                if frame.index.tz is not None or not frame.index.equals(frame.index.normalize()):
                    raise ValueError("normalized local session dates are required")
                issue_code = "requested_date_window"
                if frame.index.min().date() < start or frame.index.max().date() > end:
                    raise ValueError("bars must lie inside the requested interval")
                # Reject a defective observation before applying the display limit;
                # otherwise older invalid bars disappear without a quality failure.
                issue_code = "price_values"
                # Each required label must select exactly one Series. Do not
                # flatten a provider's symbol levels or pick a duplicate column.
                if isinstance(frame.columns, pd.MultiIndex) or any(
                    frame.columns.tolist().count(column) != 1 for column in ("open", "high", "low", "close")
                ):
                    raise ValueError("unique flat price columns are required")
                # Python/numpy booleans are finite, but are not observations.
                # Numpy complex scalars may silently discard their imaginary
                # part in comparisons/float conversion; reject before either.
                if (
                    not frame[["open", "high", "low", "close"]]
                    .map(
                        lambda value: (
                            not pd.api.types.is_bool(value)
                            and not pd.api.types.is_complex(value)
                            and math.isfinite(value)
                        )
                    )
                    .all()
                    .all()
                ):
                    raise ValueError("prices must be finite and complete")
                validate_ohlc(frame, strategy="raise")
                issue_code = "volume_values"
                if frame.columns.tolist().count("volume") != 1:
                    raise ValueError("one volume column is required")
                if (
                    not frame["volume"]
                    .dropna()
                    .map(
                        lambda value: (
                            not pd.api.types.is_bool(value)
                            and not pd.api.types.is_complex(value)
                            and math.isfinite(value)
                            and value >= 0
                        )
                    )
                    .all()
                ):
                    raise ValueError("available volume must be finite and nonnegative")
                # Audit the whole validated observation so a window-start bar
                # is judged against the last traded close before the window.
                # Report only; vendor placeholder prices stay in the bars and
                # indicators. No calendar is supplied, so none is checked.
                audit = audit_daily_bars(code, frame)
                validated = frame
                frame = frame.sort_index().tail(lookback)
                window_start = frame.index[0].date().isoformat()
                bar_audit = {
                    "policy": audit["policy"],
                    "calendar_verified": False,
                    "zero_volume_price_change_dates": [
                        day for day in audit["zero_volume_price_change_dates"] if day >= window_start
                    ],
                }
                if bar_audit["zero_volume_price_change_dates"]:
                    logger.warning(
                        "IDX research %s zero-volume price change on %d bars",
                        code,
                        len(bar_audit["zero_volume_price_change_dates"]),
                    )
                bars = [
                    {
                        "date": stamp.date().isoformat(),
                        **{
                            key: None if pd.isna(row[key]) else float(row[key])
                            for key in ("open", "high", "low", "close", "volume")
                        },
                    }
                    for stamp, row in frame.iterrows()
                ]
                observed = {code: frame, "_provenance": {code: provenance}}
                issue_code = "indicator_calculation"
                analysis = json.loads(
                    summarize_technical_data_json(
                        observed,
                        code,
                        "1D",
                        lookback,
                        end.isoformat(),
                        pinned_boundary=raw_end is not None,
                    )
                )
                if not analysis["ok"]:
                    raise ValueError("indicator calculation unavailable")
                # Finite observations can still overflow indicator arithmetic.
                # Validate nested results inside this symbol's failure boundary;
                # null remains valid, and no computed value is replaced or clamped.
                json.dumps(analysis, allow_nan=False)
                # Count the exact chart/analysis window, not the acquisition
                # budget or inferred exchange sessions. Zero is observed volume.
                available_volumes = [bar["volume"] for bar in bars if bar["volume"] is not None]
                volume_coverage = {
                    "bar_count": len(bars),
                    "available_bar_count": len(available_volumes),
                    "missing_bar_count": len(bars) - len(available_volumes),
                    "zero_bar_count": sum(volume == 0 for volume in available_volumes),
                }
                last_bar = frame.index[-1].date()
                age_days = (end - last_bar).days
                old_observation = age_days > RECENCY_WARNING_DAYS
                recency = {
                    "policy": "calendar_age_warning_v1",
                    "reference_date": end.isoformat(),
                    "last_bar_date": last_bar.isoformat(),
                    "age_calendar_days": age_days,
                    "warning_after_calendar_days": RECENCY_WARNING_DAYS,
                    "status": "warning" if old_observation else "within_window",
                    "calendar_verified": False,
                }
                if old_observation:
                    logger.warning("IDX research old observation for %s (%s calendar days)", code, age_days)
                if sourced_reference is not None:
                    try:
                        item["sourced_audit"] = _sourced_audit(
                            code, validated, window_start, end, sourced_calendar, sourced_records
                        )
                    except (ValueError, KeyError, TypeError) as exc:
                        logger.warning("IDX research sourced audit failed for %s (%s)", code, type(exc).__name__)
                        item["sourced_audit"] = {"policy": SOURCED_AUDIT_POLICY, "issue": "audit_failed"}
                item.update(
                    status="ok",
                    bars=bars,
                    analysis=analysis,
                    recency=recency,
                    volume_coverage=volume_coverage,
                    bar_audit=bar_audit,
                )
            except (ValueError, KeyError, TypeError, OverflowError) as exc:
                logger.warning("IDX research rejected bars for %s (%s; %s)", code, issue_code, type(exc).__name__)
                item.update(reason="invalid_data_or_metadata", quality_issue={"code": issue_code})
            items.append(item)
        available = sum(item["status"] == "ok" for item in items)
        response: dict[str, Any] = {
            "ok": True,
            "status": "ok" if available == len(items) else "partial" if available else "unavailable",
            "requested_start_date": start.isoformat(),
            "requested_end_date": end.isoformat(),
            "interval": "1D",
            "lookback": lookback,
            "items": items,
            "calendar_completeness": "not_verified",
            "backtest_enabled": False,
        }
        if sourced_reference is not None:
            response["sourced_reference"] = sourced_reference
        return json.dumps(response, allow_nan=False)


def main() -> None:
    """Run personal research without onboarding or an LLM account."""
    parser = argparse.ArgumentParser(description=IDXResearchTool.description)
    parser.add_argument("codes", nargs="+")
    parser.add_argument("--lookback", type=int, default=DEFAULT_LOOKBACK)
    parser.add_argument("--end-date")
    args = parser.parse_args()
    result = IDXResearchTool().execute(codes=args.codes, lookback=args.lookback, end_date=args.end_date)
    print(result)
    parsed = json.loads(result)
    raise SystemExit(0 if parsed.get("ok") and parsed.get("status") == "ok" else 2)


if __name__ == "__main__":
    main()
