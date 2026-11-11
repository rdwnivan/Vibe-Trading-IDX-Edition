import { formatIDXRetrievedAt, formatIDXSourceAsOf, getIDXRecency, getIDXVolumeCoverage } from "../idx-research";

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
