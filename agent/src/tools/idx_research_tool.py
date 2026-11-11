"""Bounded personal IDX watchlist research through the existing data pipeline."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
import json
import logging
import math
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from backtest.engines._market_hooks import _detect_market
from backtest.loaders.base import validate_ohlc
from src.agent.tools import BaseTool
from src.market_data import fetch_market_data
from src.tools.technical_indicator_tool import summarize_technical_data_json

logger = logging.getLogger(__name__)
MAX_SYMBOLS = 8
DEFAULT_LOOKBACK = 200
MAX_LOOKBACK = 500
# Personal research alarm only, independent of loader-health availability gates.
# Calendar age cannot establish missing sessions, suspension, or provider delay.
RECENCY_WARNING_DAYS = 14


def _failure(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


class IDXResearchTool(BaseTool):
    """Acquire once, then derive charts and indicators from the same bars."""

    name = "idx_research"
    description = (
        "Personal read-only IDX daily watchlist research. Supply explicit .JK "
        "regular-share symbols (maximum 8). Returns chart OHLCV, existing technical "
        "indicators and actual serving provenance; unavailable symbols remain visible. "
        "Includes calendar-age recency warnings relative to the requested end date. "
        "Reports available, missing and zero-volume counts over the analyzed bars. "
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
                try:
                    json.dumps(provenance, allow_nan=False)
                except (TypeError, ValueError, RecursionError):
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
                    try:
                        json.dumps(diagnostics, allow_nan=False)
                    except (TypeError, ValueError, RecursionError):
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
                frame = frame.sort_index().tail(lookback)
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
                item.update(status="ok", bars=bars, analysis=analysis, recency=recency, volume_coverage=volume_coverage)
            except (ValueError, KeyError, TypeError, OverflowError) as exc:
                logger.warning("IDX research rejected bars for %s (%s; %s)", code, issue_code, type(exc).__name__)
                item.update(reason="invalid_data_or_metadata", quality_issue={"code": issue_code})
            items.append(item)
        available = sum(item["status"] == "ok" for item in items)
        return json.dumps(
            {
                "ok": True,
                "status": "ok" if available == len(items) else "partial" if available else "unavailable",
                "requested_start_date": start.isoformat(),
                "requested_end_date": end.isoformat(),
                "interval": "1D",
                "lookback": lookback,
                "items": items,
                "calendar_completeness": "not_verified",
                "backtest_enabled": False,
            },
            allow_nan=False,
        )


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
