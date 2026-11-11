"""Local data loader: reads CSV, Parquet, and DuckDB files from user config.

Configuration lives at ``~/.vibe-trading/data-bridge/config.yaml``.
Each entry maps a symbol to a data file with optional column-name overrides,
date format, and (for DuckDB) an SQL query.

Example config::

    sources:
      - symbol: "AAPL.US"
        type: csv
        path: "~/data/aapl_2024.csv"
        columns:
          date: "Date"
          open: "Open"
          high: "High"
          low: "Low"
          close: "Close"
          volume: "Volume"
        date_format: "%Y-%m-%d"

      - symbol: "BTC-USDT"
        type: parquet
        path: "~/data/btc.parquet"

      - symbol: "MYINDEX"
        type: duckdb
        db_path: "~/data/market.duckdb"
        query: "SELECT * FROM prices WHERE ticker = 'MYINDEX'"
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from backtest.loaders.base import cached_loader_fetch, validate_date_range, validate_ohlc
from backtest.loaders.idx_contract import is_idx_share, normalize_idx_volume
from backtest.loaders.registry import register

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path.home() / ".vibe-trading" / "data-bridge"
_CONFIG_PATH = _CONFIG_DIR / "config.yaml"

_DEFAULT_COLUMNS = {
    "date": "date",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
}

# Map the project's bar intervals (see ``backtest.runner._VALID_INTERVALS``) to
# pandas offset aliases used for resampling. All entries are fixed-duration so
# ``pd.Timedelta`` of the alias is well defined.
_RESAMPLE_RULES = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1H": "1h",
    "1h": "1h",
    "4H": "4h",
    "4h": "4h",
    "1D": "1D",
    "1d": "1D",
}

_OHLCV_AGG = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}

# Old local IDX entries can hide defective observations or fabricated volume totals.
# Leave other markets and existing source-revision identities unchanged.
_IDX_CACHE_FIELDS = ("idx_local_volume_v1", "idx_local_dates_v1", "idx_local_prices_v1")


def _sum_idx_volume(values: pd.Series) -> float:
    """A total is unavailable if any observed constituent volume is missing."""
    return normalize_idx_volume(values.sum(min_count=len(values)))


def _resample_to_interval(df: pd.DataFrame, interval: str, symbol: str) -> pd.DataFrame:
    """Resample an OHLCV frame to the requested bar ``interval``.

    Local files can hold any native granularity, so a requested interval the
    file does not already match must be honored explicitly. Previously
    ``interval`` was passed only to the cache key, so requesting e.g. ``4H``
    against hourly data silently returned the file's native bars.

    Coarser-than-source requests are downsampled with the standard OHLCV
    aggregation. A finer-than-source request cannot be fabricated from a file,
    so the source bars are returned unchanged with a warning. Requests that
    already match the source granularity are returned unchanged.
    For IDX, every observed constituent must have volume to report a total.
    This does not establish completeness against an exchange calendar.
    """
    rule = _RESAMPLE_RULES.get(interval)
    if df.empty:
        return df
    if rule is None:
        logger.warning(
            "local loader: unsupported interval %r for %s; returning source bars",
            interval,
            symbol,
        )
        return df

    target = pd.Timedelta(rule)
    if len(df.index) >= 2:
        source = df.index.to_series().diff().dropna().median()
        if pd.notna(source):
            if target < source:
                logger.warning(
                    "local loader: cannot upsample %s source bars to %s for %s; "
                    "returning source bars",
                    source,
                    interval,
                    symbol,
                )
                return df
            if target == source:
                return df

    aggregation = (
        {**_OHLCV_AGG, "volume": _sum_idx_volume} if is_idx_share(symbol) else _OHLCV_AGG
    )
    resampled = df.resample(rule).agg(aggregation)
    resampled = resampled.dropna(subset=["open", "high", "low", "close"])
    resampled.index.name = df.index.name
    return resampled


def _source_cache_identity(entry: dict[str, Any]) -> str:
    """Hash reader settings while excluding unrelated YAML annotations."""
    identity = {
        key: entry.get(key)
        for key in ("type", "path", "db_path", "query", "date_format")
    }
    columns = entry.get("columns")
    identity["columns"] = (
        sorted(
            (str(key), value)
            for key, value in columns.items()
            if isinstance(value, str)
        )
        if isinstance(columns, dict)
        else None
    )
    payload = json.dumps(identity, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_file_revision(entry: dict[str, Any]) -> str:
    # A local source can be corrected or replaced without changing its YAML.
    # Identify filesystem revisions as well as reader declarations so settled
    # cached bars cannot hide the updated file. DuckDB writes may reside in WAL.
    source_type = str(entry.get("type") or "csv").strip().lower()
    source_path = (
        entry.get("db_path") if source_type == "duckdb" else entry.get("path")
    )
    revisions = []
    if isinstance(source_path, str) and source_path.strip():
        reader_path = source_path if source_type == "duckdb" else source_path.strip()
        path = Path(reader_path).expanduser()
        paths = [path, Path(str(path) + ".wal")] if source_type == "duckdb" else [path]
        for file in paths:
            try:
                stat = file.stat()
                revisions.append(
                    (str(file), stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
                )
            except OSError:
                revisions.append((str(file), None))
    payload = json.dumps(revisions).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def _load_config() -> dict[str, Any] | None:
    if not _CONFIG_PATH.exists():
        return None
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Preserve empty/null documents, but do not disguise other falsy YAML
    # values as empty config. Availability and indexing share this boundary.
    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ValueError("local loader: configuration document must be a mapping")
    if "sources" in config and not isinstance(config["sources"], list):
        raise ValueError("local loader: sources must be a list")
    return config


def _normalize_columns(
    df: pd.DataFrame,
    col_map: dict[str, str],
    date_fmt: str | None,
    *,
    idx: bool = False,
) -> pd.DataFrame | None:
    # A DatetimeIndex carries the bar dates (parquet files, and duckdb
    # relations whose query set one). An explicitly mapped date column wins
    # over the index; otherwise the index becomes the date column, whatever
    # date_fmt is configured. Dropping the index on the first path also
    # sidesteps the reset_index crash when index and column share a name.
    if isinstance(df.index, pd.DatetimeIndex):
        if col_map.get("date", "date") in df.columns:
            df = df.reset_index(drop=True)
        else:
            df = df.reset_index()
            col_map = {**col_map, "date": df.columns[0]}
    rename: dict[str, str] = {}
    for std_name, src_name in col_map.items():
        if std_name == "date":
            continue
        if src_name in df.columns:
            rename[src_name] = std_name
    df = df.rename(columns=rename)

    prices = ["open", "high", "low", "close"]
    if not set(prices).issubset(df.columns):
        if idx:
            raise ValueError("IDX prices require all OHLC fields")
        return None

    date_col = col_map.get("date", "date")
    if date_col not in df.columns:
        if idx:
            # Empty observations still need a date schema. DatetimeIndex has
            # already supplied the date column above when one is available.
            raise ValueError("IDX local dates require a date column or DatetimeIndex")
        return None

    if date_fmt:
        parsed_dates = pd.to_datetime(
            df[date_col], format=date_fmt, errors="coerce", utc=True
        )
    else:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce", utc=True)
    if idx and parsed_dates.isna().any():
        # A local row has no padding contract: an undated observation cannot
        # be assigned to a range/bucket or silently discarded as no data.
        # Reject before date filtering can also hide defective OHLC/volume.
        raise ValueError("IDX local dates must be present and parseable with the configured date format")
    # Normalize every input to the loader's UTC-naive index contract. Parsing
    # as UTC first also handles files that span daylight-saving offset changes.
    df["trade_date"] = parsed_dates.dt.tz_convert(None)
    df = df.dropna(subset=["trade_date"])
    df = df.set_index("trade_date").sort_index()

    ohlcv_cols = prices.copy()
    if "volume" in df.columns:
        ohlcv_cols.append("volume")

    df = df[ohlcv_cols]
    if idx and df[prices].map(
        lambda value: pd.api.types.is_bool(value) or pd.api.types.is_complex(value)
    ).any().any():
        raise ValueError("IDX local prices must be real numeric OHLC observations")
    if idx and "volume" in df.columns:
        # Do not let generic coercion turn invalid volume into a missing value.
        df["volume"] = df["volume"].map(normalize_idx_volume)
    for col in ohlcv_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if idx and (
        df[prices].isna().any().any()
        or not df[prices].map(math.isfinite).all().all()
    ):
        # Local dated rows are explicit observations, with no provider-padding
        # contract. Reject even all-null prices before dropna or resampling.
        raise ValueError("IDX local prices must be finite and complete numeric OHLC observations")
    df = df.dropna(subset=prices)
    df = validate_ohlc(df, strategy="raise" if idx else "drop")
    for col in ohlcv_cols:
        df[col] = df[col].astype("float64")

    if "volume" not in df.columns:
        df["volume"] = float("nan") if idx else 0.0

    return df


def _read_csv(
    path: str, col_map: dict[str, str], date_fmt: str | None, *, idx: bool = False,
) -> pd.DataFrame | None:
    df = pd.read_csv(path, dtype=object) if idx else pd.read_csv(path)
    return _normalize_columns(df, col_map, date_fmt, idx=idx)


def _read_parquet(
    path: str, col_map: dict[str, str], date_fmt: str | None, *, idx: bool = False,
) -> pd.DataFrame | None:
    df = pd.read_parquet(path)
    return _normalize_columns(df, col_map, date_fmt, idx=idx)


def _read_duckdb(
    db_path: str, query: str, col_map: dict[str, str], date_fmt: str | None,
    *, idx: bool = False,
) -> pd.DataFrame | None:
    import duckdb

    with duckdb.connect(db_path, read_only=True) as conn:
        df = conn.execute(query).df()
    return _normalize_columns(df, col_map, date_fmt, idx=idx)


_READERS = {
    "csv": _read_csv,
    "parquet": _read_parquet,
    "duckdb": _read_duckdb,
}


@register
class DataLoader:
    """Config-driven local data loader for CSV, Parquet, and DuckDB."""

    name = "local"
    markets = {"us_equity", "a_share", "hk_equity", "id_equity", "crypto", "futures", "forex", "macro", "fund"}
    requires_auth = False

    def __init__(self) -> None:
        self._config: dict[str, Any] | None = None
        self._source_by_symbol: dict[str, dict[str, Any]] = {}

    def is_available(self) -> bool:
        """Check for declared sources; fetch validates their symbol index/readers."""
        config = _load_config()
        if config is None:
            return False
        sources = config.get("sources")
        return isinstance(sources, list) and len(sources) > 0

    def _ensure_config(self) -> None:
        if self._config is not None:
            return
        config = _load_config() or {}
        source_by_symbol: dict[str, dict[str, Any]] = {}
        for position, entry in enumerate(config.get("sources", []), start=1):
            if not isinstance(entry, dict):
                # Unassigned items cannot identify a failing symbol. Report the
                # YAML position without leaking raw values, and keep indexing
                # valid sources for every market instead of poisoning peers.
                logger.warning(
                    "local loader: sources entry %d must be a mapping; skipping unassigned entry",
                    position,
                )
                continue
            symbol = entry.get("symbol", "")
            if not isinstance(symbol, str):
                logger.warning(
                    "local loader: sources entry %d symbol must be a string; skipping unassigned entry",
                    position,
                )
                continue
            symbol = symbol.strip()
            if symbol:
                source_by_symbol[symbol] = entry
        if config.get("sources") and not source_by_symbol:
            # A nonempty declaration with no assignable source is not an empty
            # dataset or an unconfigured request against an otherwise valid index.
            # Publish only successful snapshots so repeated failures retry config.
            raise ValueError("local loader: nonempty sources must define at least one nonblank string symbol")
        self._source_by_symbol = source_by_symbol
        self._config = config

    def fetch(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
        *,
        interval: str = "1D",
        fields: Optional[List[str]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV data for each code from configured local sources.

        Args:
            codes: Symbol list, optionally prefixed with ``local:``.
            start_date: YYYY-MM-DD.
            end_date: YYYY-MM-DD.
            interval: Bar size (all intervals supported if data contains them).
            fields: Ignored.

        Returns:
            Mapping clean_symbol -> OHLCV DataFrame.
        """
        validate_date_range(start_date, end_date)
        self._ensure_config()

        result: Dict[str, pd.DataFrame] = {}
        for code in codes:
            clean = code.split(":", 1)[1] if code.startswith("local:") else code
            entry = self._source_by_symbol.get(clean)
            if entry is None:
                logger.warning("local loader: no config entry for symbol %s", clean)
                continue
            try:
                df = cached_loader_fetch(
                    source=self.name,
                    symbol=clean,
                    timeframe=interval,
                    start_date=start_date,
                    end_date=end_date,
                    # Local symbols are user-defined: the same name can point
                    # to another file/query/schema. Keep settled-data caching,
                    # but key it by reader settings as well as the range.
                    fields=[
                        _source_cache_identity(entry),
                        *(_IDX_CACHE_FIELDS if is_idx_share(clean) else ()),
                    ],
                    source_revision=_source_file_revision(entry),
                    fetch=lambda c=clean: self._fetch_one(
                        c, start_date, end_date, interval
                    ),
                )
                if df is not None and not df.empty:
                    result[clean] = df
            except Exception as exc:
                logger.warning("local loader failed for %s: %s", clean, exc)
                if is_idx_share(clean):
                    raise

        return result

    def _fetch_one(
        self, symbol: str, start_date: str, end_date: str, interval: str = "1D",
    ) -> pd.DataFrame | None:
        entry = self._source_by_symbol.get(symbol)
        if entry is None:
            return None

        idx_options = {"idx": True} if is_idx_share(symbol) else {}

        if idx_options:
            # Validate raw declarations before Path("") can become "." or a
            # missing reader setting can be reported as an empty dataset.
            declared_type = entry.get("type", "csv")
            if not isinstance(declared_type, str) or declared_type.strip().lower() not in _READERS:
                raise ValueError("IDX local source requires a supported type")
            required = ("db_path", "query") if declared_type.strip().lower() == "duckdb" else ("path",)
            for key in required:
                value = entry.get(key)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"IDX local source requires a nonblank string {key}")

        src_type: str = entry.get("type", "csv").strip().lower()
        reader = _READERS.get(src_type)
        if reader is None:
            logger.warning("local loader: unsupported type %r for symbol %s", src_type, symbol)
            return None

        col_map: dict[str, str] = dict(_DEFAULT_COLUMNS)
        user_cols = entry.get("columns")
        if isinstance(user_cols, dict):
            for k, v in user_cols.items():
                if isinstance(v, str):
                    col_map[k] = v

        date_fmt: str | None = None
        user_fmt = entry.get("date_format")
        if isinstance(user_fmt, str) and user_fmt.strip():
            date_fmt = user_fmt.strip()

        if src_type == "duckdb":
            db_path = str(Path(entry.get("db_path", "")).expanduser())
            query = entry.get("query", "").strip()
            if not db_path or not query:
                logger.warning(
                    "local loader: missing db_path or query for duckdb symbol %s", symbol
                )
                return None
            df = _read_duckdb(db_path, query, col_map, date_fmt, **idx_options)
        else:
            path = entry.get("path", "").strip()
            if not path:
                logger.warning("local loader: missing path for symbol %s", symbol)
                return None
            expanded = str(Path(path).expanduser())
            df = reader(expanded, col_map, date_fmt, **idx_options)

        if df is None:
            return None

        start = pd.Timestamp(start_date)
        # Treat ``end_date`` as inclusive of the whole day so intraday bars on
        # the end day survive the filter (a bare midnight bound dropped them,
        # which would defeat any sub-daily ``interval``).
        end = pd.Timestamp(end_date) + pd.Timedelta(days=1)
        # A half-open boundary includes fractional seconds on the end day
        # without admitting the following midnight.
        df = df[(df.index >= start) & (df.index < end)]
        if df.empty:
            return None
        df = _resample_to_interval(df, interval, symbol)
        if df.empty:
            return None
        return df
