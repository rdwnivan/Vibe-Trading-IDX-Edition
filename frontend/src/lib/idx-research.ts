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

/** Presentation gate only: the backend owns the audit and its verdicts.
 * Any malformed field makes the whole finding unavailable; never filter or
 * repair dates here, since a partial list would understate the warning.
 */
export function getIDXBarAudit(value: unknown): NonNullable<IDXResearchItem["bar_audit"]> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const fields = value as Record<string, unknown>;
  const dates = fields.zero_volume_price_change_dates;
  if (fields.policy !== "idx_daily_bar_audit_v1" || fields.calendar_verified !== false || !Array.isArray(dates)
    || !dates.every((day) => typeof day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(day) && validSessionDate(day))) return null;
  return value as NonNullable<IDXResearchItem["bar_audit"]>;
}

const SOURCED_SERIES_STATUSES = ["delisted", "no_bars", "unverified", "uncovered", "current", "suspended", "ended_or_stale"] as const;
const SOURCED_ACTION_KINDS = ["cash_dividend", "stock_dividend", "bonus_shares", "split", "reverse_split", "rights_issue"] as const;
const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === "object" && value !== null && !Array.isArray(value);
const isSessionDate = (day: unknown): day is string => typeof day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(day) && validSessionDate(day);
const isCount = (count: unknown) => typeof count === "number" && Number.isSafeInteger(count) && count >= 0;
const isDateList = (days: unknown) => Array.isArray(days) && days.every(isSessionDate);
const isPrice = (price: unknown) => price === null || (typeof price === "number" && Number.isFinite(price));

/** Presentation gate only: status of the operator's sourced files as the backend reports it. */
export function getIDXSourcedReference(value: unknown): NonNullable<IDXResearchResponse["sourced_reference"]> | null {
  if (!isRecord(value) || value.policy !== "idx_sourced_reference_v1") return null;
  const unloaded = (state: Record<string, unknown>) => state.status === "not_configured"
    || (state.status === "unavailable" && state.issue === "unreadable_or_invalid");
  const calendar = value.calendar;
  const records = value.event_records;
  if (!isRecord(calendar) || !(unloaded(calendar) || (calendar.status === "loaded" && typeof calendar.source === "string"
    && calendar.source.trim() !== "" && isSessionDate(calendar.covered_from) && isSessionDate(calendar.covered_until)))) return null;
  if (!isRecord(records) || !(unloaded(records) || (records.status === "loaded" && isCount(records.suspension_count)
    && isCount(records.delisting_count) && isCount(records.corporate_action_count)))) return null;
  return value as NonNullable<IDXResearchResponse["sourced_reference"]>;
}

/** Presentation gate only: the backend owns every sourced finding and verdict.
 * Any malformed field makes the whole audit unavailable; never filter or repair it here.
 */
export function getIDXSourcedAudit(value: unknown): NonNullable<IDXResearchItem["sourced_audit"]> | null {
  if (!isRecord(value) || value.policy !== "idx_sourced_audit_v1" || typeof value.calendar_verified !== "boolean") return null;
  const calendarList = (days: unknown) => value.calendar_verified ? isDateList(days) : days === null;
  if (!calendarList(value.off_calendar_dates) || !calendarList(value.uncovered_dates) || !calendarList(value.missing_session_dates)) return null;
  const flat = value.zero_volume_flat_bars;
  if (!Array.isArray(flat) || !flat.every((bar) => isRecord(bar) && isSessionDate(bar.date)
    && (bar.status === "suspended" || bar.status === "untraded_or_suspended"))) return null;
  if (!isDateList(value.traded_during_suspension_dates) || !isDateList(value.bars_after_delisting_dates)) return null;
  const sources = (list: unknown) => Array.isArray(list) && list.every((item) => typeof item === "string");
  if (!sources(value.suspension_sources) || !sources(value.delisting_sources)) return null;
  const end = value.series_end;
  if (!isRecord(end) || !isSessionDate(end.as_of) || !(end.last_bar_date === null || isSessionDate(end.last_bar_date))
    || !(SOURCED_SERIES_STATUSES as readonly unknown[]).includes(end.status)
    || !(end.sessions_after_last_bar === null || isCount(end.sessions_after_last_bar))
    || !(end.delisting_effective_date === null || isSessionDate(end.delisting_effective_date))) return null;
  const moves = value.ex_date_moves;
  if (!Array.isArray(moves) || !moves.every((move) => isRecord(move) && isSessionDate(move.ex_date)
    && (SOURCED_ACTION_KINDS as readonly unknown[]).includes(move.kind) && typeof move.bar_present === "boolean"
    && isPrice(move.previous_close) && isPrice(move.close))) return null;
  return value as NonNullable<IDXResearchItem["sourced_audit"]>;
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
  bar_audit?: {
    policy: "idx_daily_bar_audit_v1";
    calendar_verified: false;
    zero_volume_price_change_dates: string[];
  } | null;
  sourced_audit?: {
    policy: "idx_sourced_audit_v1";
    calendar_verified: boolean;
    off_calendar_dates: string[] | null;
    uncovered_dates: string[] | null;
    missing_session_dates: string[] | null;
    zero_volume_flat_bars: { date: string; status: "suspended" | "untraded_or_suspended" }[];
    traded_during_suspension_dates: string[];
    suspension_sources: string[];
    series_end: {
      as_of: string;
      last_bar_date: string | null;
      status: (typeof SOURCED_SERIES_STATUSES)[number];
      sessions_after_last_bar: number | null;
      delisting_effective_date: string | null;
    };
    bars_after_delisting_dates: string[];
    delisting_sources: string[];
    ex_date_moves: {
      ex_date: string;
      kind: (typeof SOURCED_ACTION_KINDS)[number];
      source: string;
      bar_present: boolean;
      previous_bar_date: string | null;
      previous_close: number | null;
      close: number | null;
      close_ratio: number | null;
      previous_adjustment_factor: number | null;
      adjustment_factor: number | null;
    }[];
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
  sourced_reference?: {
    policy: "idx_sourced_reference_v1";
    calendar:
      | { status: "loaded"; source: string; covered_from: string; covered_until: string }
      | { status: "not_configured" }
      | { status: "unavailable"; issue: "unreadable_or_invalid" };
    event_records:
      | { status: "loaded"; suspension_count: number; delisting_count: number; corporate_action_count: number }
      | { status: "not_configured" }
      | { status: "unavailable"; issue: "unreadable_or_invalid" };
  };
}
