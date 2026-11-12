// A session date is a calendar label, never an instant in the browser timezone.
function validSessionDate(value: string): boolean {
  const parsed = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

/** Current daily loaders stamp a local date or a timezone-free midnight. */
export function formatIDXSourceAsOf(value: string | undefined): string | null {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}(?:T00:00:00(?:\.0+)?)?$/.test(value)) return null;
  const day = value.slice(0, 10);
  return validSessionDate(day) ? day : null;
}

/** Unknown/invalid metadata stays visibly unavailable; never assume a zone. */
export function formatIDXRetrievedAt(value: string | undefined, locale: string): string | null {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return null;
  const instant = new Date(value);
  if (!validSessionDate(value.slice(0, 10)) || !Number.isFinite(instant.getTime()) || value.slice(11, 13) === "24") return null;
  return `${new Intl.DateTimeFormat(locale, {
    timeZone: "Asia/Jakarta", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).format(instant)} WIB`;
}

/** Presentation gate only: unknown diagnostics stay visibly unavailable.
 * The backend owns age, threshold and verdict; do not recompute them here.
 */
export function getIDXRecency(value: unknown): NonNullable<IDXResearchItem["recency"]> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const fields = value as Record<string, unknown>;
  const validCount = (count: unknown) => typeof count === "number" && Number.isSafeInteger(count) && count >= 0;
  const validDate = (day: unknown) => typeof day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(day) && validSessionDate(day);
  if (fields.policy !== "calendar_age_warning_v1" || fields.calendar_verified !== false
    || (fields.status !== "warning" && fields.status !== "within_window")
    || !validCount(fields.age_calendar_days) || !validCount(fields.warning_after_calendar_days)
    || !validDate(fields.last_bar_date) || !validDate(fields.reference_date)) return null;
  return value as NonNullable<IDXResearchItem["recency"]>;
}

/** Presentation only: contradictory counts are unavailable, never repaired from bars.
 * Preserve valid neighbors of missing/invalid fields without inferring a count.
 */
export function getIDXVolumeCoverage(value: unknown): Partial<NonNullable<IDXResearchItem["volume_coverage"]>> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const fields = value as Record<string, unknown>;
  const count = (value: unknown): number | undefined => typeof value === "number" && Number.isSafeInteger(value) && value >= 0 ? value : undefined;
  const total = count(fields.bar_count);
  const available = count(fields.available_bar_count);
  const missing = count(fields.missing_bar_count);
  const zero = count(fields.zero_bar_count);
  const bars = total === 0 ? undefined : total;
  if ((bars !== undefined && ((available !== undefined && available > bars)
    || (missing !== undefined && missing > bars) || (zero !== undefined && zero > bars)))
    || (available !== undefined && zero !== undefined && zero > available)
    || (bars !== undefined && available !== undefined && missing !== undefined && available !== bars - missing)) return null;
  return { bar_count: bars, available_bar_count: available, missing_bar_count: missing, zero_bar_count: zero };
}

export interface IDXSymbolSearchResponse {
  ok: boolean;
  data: {
    query: string;
    candidates: { symbol: string; name: string | null; venue: "IDX"; currency: "IDR"; source: string }[];
    sources: { yahoo: string };
  };
}

export interface IDXBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
}

export interface IDXResearchItem {
  symbol: string;
  status: "ok" | "unavailable";
  reason?: string;
  diagnostics?: { attempts?: { source: string; reason: string }[] | null; recovery?: string } | null;
  quality_issue?: { code: string } | null;
  volume_coverage?: {
    bar_count: number;
    available_bar_count: number;
    missing_bar_count: number;
    zero_bar_count: number;
  } | null;
  recency?: {
    policy: "calendar_age_warning_v1";
    reference_date: string;
    last_bar_date: string;
    age_calendar_days: number;
    warning_after_calendar_days: number;
    status: "warning" | "within_window";
    calendar_verified: false;
  } | null;
  provenance: {
    source?: string;
    quote_currency?: string;
    adjustment?: string;
    exchange_timezone?: string;
    volume_unit?: string;
    retrieved_at?: string;
    data_as_of?: string;
    freshness?: string;
    fallback_used?: boolean;
    attempts?: { source: string; reason: string }[] | null;
  } | null;
  bars?: IDXBar[];
  analysis?: {
    latest_close: number;
    latest_date: string;
    read_identity: { dataset_fingerprint: string; bar_count: number };
    indicators: {
      rsi_14: number | null;
      sma_20: number | null;
      sma_50: number | null;
      sma_200: number | null;
      ema_20: number | null;
      macd: { macd_line: number | null; signal_line: number | null; histogram: number | null } | null;
      bollinger?: { upper: number | null; middle: number | null; lower: number | null } | null;
      volume: { latest: number | null; sma_20: number | null; ratio_20: number | null; unit: string | null };
    };
  };
}

export interface IDXResearchResponse {
  ok: boolean;
  status: "ok" | "partial" | "unavailable";
  requested_start_date: string;
  requested_end_date: string;
  interval: string;
  lookback: number;
  items: IDXResearchItem[];
}
