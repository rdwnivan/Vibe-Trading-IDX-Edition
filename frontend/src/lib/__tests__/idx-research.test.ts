import { formatIDXRetrievedAt, formatIDXSourceAsOf, getIDXBarAudit, getIDXRecency, getIDXSourcedAudit, getIDXSourcedReference, getIDXVolumeCoverage } from "../idx-research";

function barAudit(dates: unknown = ["2026-01-12", "2026-01-13"]) {
  return { policy: "idx_daily_bar_audit_v1", calendar_verified: false, zero_volume_price_change_dates: dates };
}

it.each([[[]], [["2026-01-12"]], [["2026-01-12", "2026-01-13"]]])("accepts a backend bar audit with dates %j unchanged", (dates) => {
  const value = barAudit(dates);
  expect(getIDXBarAudit(value)).toBe(value);
});

it.each([undefined, null, true, "2026-01-12", [], [["2026-01-12"]]])("keeps unsupported bar audit container %j unavailable", (value) => {
  expect(getIDXBarAudit(value)).toBeNull();
});

it.each([
  { ...barAudit(), policy: "idx_daily_bar_audit_v2" },
  { ...barAudit(), calendar_verified: true },
  { policy: "idx_daily_bar_audit_v1", calendar_verified: false },
  barAudit(null),
  barAudit("2026-01-12"),
  barAudit(["2026-01-12", "2026-02-30"]),
  barAudit(["2026-01-12", "2026-1-13"]),
  barAudit(["2026-01-12T00:00:00Z"]),
  barAudit(["2026-01-12", 20260113]),
])("marks the whole bar audit unavailable instead of filtering it: %j", (value) => {
  expect(getIDXBarAudit(value)).toBeNull();
});

function volumeCoverage() {
  return { bar_count: 20, available_bar_count: 19, missing_bar_count: 1, zero_bar_count: 1 };
}

it.each([undefined, null, true, 20, "private-value", [], [20, 19, 1, 1]])("keeps unsupported volume coverage container %j unavailable", (value) => {
  expect(getIDXVolumeCoverage(value)).toBeNull();
});

describe.each(["bar_count", "available_bar_count", "missing_bar_count", "zero_bar_count"])("volume coverage %s", (field) => {
  it.each([undefined, null, true, "19", -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])("keeps invalid count %s unavailable without discarding valid neighbors", (value) => {
    expect(getIDXVolumeCoverage({ ...volumeCoverage(), [field]: value })).toEqual({ ...volumeCoverage(), [field]: undefined });
  });
});

it.each([
  { bar_count: 20, available_bar_count: 19, missing_bar_count: 5, zero_bar_count: 1 },
  { bar_count: 20, available_bar_count: 19, missing_bar_count: 0, zero_bar_count: 1 },
  { bar_count: 20, available_bar_count: 21 },
  { bar_count: 20, missing_bar_count: 21 },
  { bar_count: 20, zero_bar_count: 21 },
  { available_bar_count: 0, zero_bar_count: 1 },
])("keeps contradictory known volume counts %j unavailable", (value) => {
  expect(getIDXVolumeCoverage(value)).toBeNull();
});

it.each([
  { bar_count: 20, available_bar_count: 0, missing_bar_count: 20, zero_bar_count: 0 },
  { bar_count: 20, available_bar_count: 20, missing_bar_count: 0, zero_bar_count: 20 },
  { bar_count: Number.MAX_SAFE_INTEGER, available_bar_count: Number.MAX_SAFE_INTEGER - 1, missing_bar_count: 1, zero_bar_count: 0 },
])("preserves consistent volume counts %j without mutation", (value) => {
  const original = structuredClone(value);
  expect(getIDXVolumeCoverage(value)).toEqual(original);
  expect(value).toEqual(original);
});

it("keeps a zero total unavailable without borrowing neighbors", () => {
  expect(getIDXVolumeCoverage({ bar_count: 0, available_bar_count: 0, missing_bar_count: 0, zero_bar_count: 0 }))
    .toEqual({ bar_count: undefined, available_bar_count: 0, missing_bar_count: 0, zero_bar_count: 0 });
});

function recency() {
  return {
    policy: "calendar_age_warning_v1", status: "warning", calendar_verified: false,
    reference_date: "2026-01-30", last_bar_date: "2026-01-15",
    age_calendar_days: 15, warning_after_calendar_days: 14,
  };
}

it.each([undefined, null, true, 1, "private-value", [], {}])("keeps unsupported recency container %s unavailable", (value) => {
  expect(getIDXRecency(value)).toBeNull();
});

describe.each(["age_calendar_days", "warning_after_calendar_days"])("recency %s", (field) => {
  it.each([undefined, null, true, "14", -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])("rejects invalid count %s", (value) => {
    expect(getIDXRecency({ ...recency(), [field]: value })).toBeNull();
  });

  it("accepts zero without deriving a different backend verdict", () => {
    const value = { ...recency(), [field]: 0 };
    expect(getIDXRecency(value)).toEqual(value);
  });
});

describe.each(["reference_date", "last_bar_date"])("recency %s", (field) => {
  it.each([undefined, null, true, 20260130, "private-date", "2026-02-30", "2026-02-29", "2026-01-30T00:00:00Z", "2026-01-30T00:00:00"])("rejects unsupported session date %s", (value) => {
    expect(getIDXRecency({ ...recency(), [field]: value })).toBeNull();
  });

  it("accepts a real leap day without timezone conversion", () => {
    const value = { ...recency(), [field]: "2024-02-29" };
    expect(getIDXRecency(value)).toEqual(value);
  });
});

it.each(["warning", "within_window"])("retains backend %s verdict and counts even when they differ from chart metadata", (status) => {
  const value = { ...recency(), status, extra: "ignored" };
  expect(getIDXRecency(value)).toEqual(value);
});

it.each([
  "2026-01-30T18:05:06Z",
  "2026-01-30T13:05:06-05:00",
  "2026-01-31T01:05:06.000000+07:00",
])("shows the same instant in WIB across date boundaries: %s", (timestamp) => {
  expect(formatIDXRetrievedAt(timestamp, "id")).toBe("31/01/2026, 01.05.06 WIB");
});

it.each([undefined, "", "private-invalid-time", "2026-01-30", "2026-01-30T18:05:06", "2026-02-30T18:05:06Z", "2026-01-30T24:00:00Z", "2026-01-30T18:60:06Z"])("marks missing or ambiguous retrieval metadata unavailable: %s", (timestamp) => {
  expect(formatIDXRetrievedAt(timestamp, "en")).toBeNull();
});

it.each(["2026-01-30", "2026-01-30T00:00:00", "2026-01-30T00:00:00.000000"])("keeps the source session date without timezone conversion: %s", (date) => {
  expect(formatIDXSourceAsOf(date)).toBe("2026-01-30");
});

it.each([undefined, "", "2026-02-30", "2026-01-30T12:00:00", "2026-01-30T00:00:00Z", "private-invalid-date"])("marks unsupported source date metadata unavailable: %s", (date) => {
  expect(formatIDXSourceAsOf(date)).toBeNull();
});

it("accepts a real leap day while rejecting a nonexistent one", () => {
  expect(formatIDXSourceAsOf("2024-02-29T00:00:00")).toBe("2024-02-29");
  expect(formatIDXSourceAsOf("2026-02-29T00:00:00")).toBeNull();
});

describe("sourced reference gates", () => {
  function reference() {
    return {
      policy: "idx_sourced_reference_v1",
      calendar: { status: "loaded", source: "BEI Peng-00171/BEI.POP/09-2025", covered_from: "2026-01-01", covered_until: "2026-12-31" },
      event_records: { status: "loaded", suspension_count: 1, delisting_count: 0, corporate_action_count: 0 },
    };
  }

  function audit() {
    return {
      policy: "idx_sourced_audit_v1",
      calendar_verified: true,
      off_calendar_dates: ["2026-04-03"],
      uncovered_dates: [],
      missing_session_dates: [],
      zero_volume_flat_bars: [{ date: "2026-03-27", status: "suspended" }],
      traded_during_suspension_dates: [],
      suspension_sources: ["BEI Peng-SPT-00097/BEI.WAS/03-2026"],
      series_end: { as_of: "2026-04-30", last_bar_date: "2026-04-24", status: "ended_or_stale", sessions_after_last_bar: 4, delisting_effective_date: null },
      bars_after_delisting_dates: [],
      delisting_sources: [],
      ex_date_moves: [{ ex_date: "2026-04-15", kind: "cash_dividend", source: "s", bar_present: true, previous_bar_date: "2026-04-13", previous_close: 105, close: 100, close_ratio: 0.95, previous_adjustment_factor: null, adjustment_factor: null }],
    };
  }

  it("accepts a valid sourced reference unchanged", () => {
    const value = reference();
    expect(getIDXSourcedReference(value)).toBe(value);
    const absent = { ...reference(), calendar: { status: "not_configured" }, event_records: { status: "unavailable", issue: "unreadable_or_invalid" } };
    expect(getIDXSourcedReference(absent)).toBe(absent);
  });

  it.each([
    undefined, null, [], "x",
    { ...reference(), policy: "idx_sourced_reference_v2" },
    { ...reference(), calendar: { status: "loaded", source: "", covered_from: "2026-01-01", covered_until: "2026-12-31" } },
    { ...reference(), calendar: { status: "loaded", source: "s", covered_from: "2026-02-30", covered_until: "2026-12-31" } },
    { ...reference(), calendar: { status: "unknown" } },
    { ...reference(), event_records: { status: "loaded", suspension_count: -1, delisting_count: 0, corporate_action_count: 0 } },
    { ...reference(), event_records: { status: "loaded", suspension_count: 1.5, delisting_count: 0, corporate_action_count: 0 } },
  ])("marks malformed sourced reference %j unavailable", (value) => {
    expect(getIDXSourcedReference(value)).toBeNull();
  });

  it("accepts a valid sourced audit unchanged, including unknown calendar findings", () => {
    const value = audit();
    expect(getIDXSourcedAudit(value)).toBe(value);
    const noCalendar = { ...audit(), calendar_verified: false, off_calendar_dates: null, uncovered_dates: null, missing_session_dates: null,
      series_end: { ...audit().series_end, status: "unverified", sessions_after_last_bar: null } };
    expect(getIDXSourcedAudit(noCalendar)).toBe(noCalendar);
  });

  it.each([
    undefined, null, [],
    { policy: "idx_sourced_audit_v1", issue: "audit_failed" },
    { ...audit(), policy: "idx_sourced_audit_v2" },
    { ...audit(), off_calendar_dates: null },
    { ...audit(), calendar_verified: false },
    { ...audit(), missing_session_dates: ["2026-13-01"] },
    { ...audit(), zero_volume_flat_bars: [{ date: "2026-03-27", status: "halted" }] },
    { ...audit(), series_end: { ...audit().series_end, status: "gone" } },
    { ...audit(), series_end: { ...audit().series_end, sessions_after_last_bar: -1 } },
    { ...audit(), ex_date_moves: [{ ...audit().ex_date_moves[0], kind: "spinoff" }] },
    { ...audit(), ex_date_moves: [{ ...audit().ex_date_moves[0], close: "100" }] },
    { ...audit(), suspension_sources: [1] },
  ])("marks the whole sourced audit unavailable instead of filtering it: %j", (value) => {
    expect(getIDXSourcedAudit(value)).toBeNull();
  });
});
