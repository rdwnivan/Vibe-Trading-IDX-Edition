"""Daily IDX data contract shared by the existing Yahoo transports."""

from datetime import datetime, timezone
import math

import pandas as pd

from backtest.engines._market_hooks import _detect_market
from backtest.loaders.base import validate_ohlc

# Earlier entries may have dropped prices or coerced invalid volume to null.
# Both transports must acquire again; cached nulls cannot recover that evidence.
IDX_OBSERVATION_CACHE_FIELDS = ("idx_valid_volume_v3",)


def normalize_idx_volume(value: object) -> float:
    """Keep genuine nulls, rejecting invalid volume before lossy conversion.

    Args:
        value: Raw scalar after the transport/file reader's null parsing.

    Returns:
        Finite nonnegative volume, or NaN for a genuine missing scalar.

    Raises:
        ValueError: Volume is nonnumeric, boolean, complex, negative or nonfinite.
    """
    error = "IDX volume must be numeric, finite and non-negative when available"
    if pd.api.types.is_bool(value) or pd.api.types.is_complex(value):
        raise ValueError(error)
    try:
        if not isinstance(value, str) and pd.isna(value):
            return float("nan")
        volume = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(error) from None
    if not math.isfinite(volume) or volume < 0:
        raise ValueError(error)
    return volume


def normalize_idx_observations(frame: pd.DataFrame) -> pd.DataFrame:
    """Reject incomplete prices without treating wholly absent slots as bars.

    All-null OHLCV slots can arise from provider padding or multi-symbol joins.
    Their omission establishes neither a closure nor a suspension. Validate raw
    volume first, then drop absent slots before price coercion so invalid
    observations cannot become padding.
    Volume may remain missing; invalid values must not become missing values.
    No price or volume is fabricated.
    """
    prices = ["open", "high", "low", "close"]
    if any(column not in frame.columns for column in prices):
        raise ValueError("IDX prices require all OHLC fields")
    observed = frame.copy()
    if "volume" in observed.columns:
        observed["volume"] = observed["volume"].map(normalize_idx_volume)
    observed = observed.dropna(how="all")
    normalized = observed.apply(pd.to_numeric, errors="coerce")
    if normalized[prices].isna().any().any():
        raise ValueError("IDX prices must be complete numeric OHLC observations")
    return normalized


def is_idx_share(code: str) -> bool:
    """Use the canonical classifier rather than introducing another one."""
    return _detect_market(code) == "id_equity"


def validate_idx_interval(codes: list[str], interval: str) -> None:
    """Reject unvalidated intraday/aggregate IDX data before network access."""
    if any(is_idx_share(code) for code in codes) and interval.strip().upper() != "1D":
        raise ValueError("IDX research currently supports daily (1D) bars only")


def stamp_idx_frame(frame: pd.DataFrame, code: str, source: str) -> pd.DataFrame:
    """Record source observation metadata, preserving unknowns explicitly."""
    if not is_idx_share(code) or frame.empty:
        return frame
    validate_ohlc(frame, strategy="raise")
    prices = frame[["open", "high", "low", "close"]]
    if not prices.map(math.isfinite).all().all():
        raise ValueError("IDX prices must be finite and complete")
    volume = frame["volume"].dropna()
    if not volume.map(math.isfinite).all() or (volume < 0).any():
        raise ValueError("IDX volume must be finite and non-negative when available")
    frame.attrs.update(
        market="id_equity",
        exchange="IDX",
        exchange_timezone="Asia/Jakarta",
        interval="1D",
        volume_unit="shares",
        source=source,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        data_as_of=frame.index.max().isoformat(),
        freshness="not_evaluated",
        data_delay="unknown",
        data_quality="incomplete" if frame.isna().any().any() else "provider_reported",
    )
    # Direct chart parsing can omit adjclose and fall back to quote OHLC.
    # Its tuple contract cannot certify that every row was adjusted.
    frame.attrs["adjustment"] = "unknown" if source == "yahoo" else "split_dividend"
    return frame
