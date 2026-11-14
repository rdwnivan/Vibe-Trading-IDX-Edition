import { act, fireEvent, render, screen, within } from "@testing-library/react";
import i18n from "@/i18n";
import { clearAnalysisState } from "@/hooks/useAnalysisState";
import { IDXResearch } from "../IDXResearch";
import type { IDXResearchItem, IDXResearchResponse } from "@/lib/idx-research";

const mock = vi.hoisted(() => ({ getIDXResearch: vi.fn(), searchIDXSymbols: vi.fn() }));
vi.mock("@/lib/api", () => ({ api: mock }));
vi.mock("@/hooks/useChartLifecycle", () => ({ useChartLifecycle: vi.fn() }));

function response(): IDXResearchResponse {
  return {
    ok: true, status: "partial", requested_start_date: "2026-01-01", requested_end_date: "2026-01-30", interval: "1D", lookback: 200,
    items: [{ symbol: "BBCA.JK", status: "ok", provenance: { source: "yahoo", quote_currency: "IDR", adjustment: "unknown", volume_unit: "shares", exchange_timezone: "Asia/Jakarta", retrieved_at: "2026-01-30T12:00:00Z" },
      bars: [{ date: "2026-01-30", open: 100, high: 110, low: 90, close: 105, volume: null }],
      analysis: { latest_close: 105, latest_date: "2026-01-30", read_identity: { dataset_fingerprint: "synthetic", bar_count: 1 },
        indicators: { rsi_14: null, sma_20: null, sma_50: null, sma_200: null, ema_20: null, macd: null, volume: { latest: null, sma_20: null, ratio_20: null, unit: "shares" } } } },
    { symbol: "BBRI.JK", status: "unavailable", reason: "no_data_or_source_failure", provenance: null }],
  };
}

function volumeResponse(): IDXResearchResponse {
  const data = response();
  // Deliberately differs from the one chart row: the UI must read backend metadata.
  data.items[0].volume_coverage = { bar_count: 20, available_bar_count: 19, missing_bar_count: 1, zero_bar_count: 1 };
  return data;
}

it("shows the backend observation fingerprint unchanged without another request", async () => {
  const data = response();
  const fingerprint = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
  data.items[0].analysis!.read_identity.dataset_fingerprint = fingerprint;
  const original = structuredClone(data);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  const label = screen.getByText("Analysis observation fingerprint (SHA-256)");
  expect(label.nextElementSibling).toHaveTextContent(new RegExp(`^${fingerprint}$`));
  expect(screen.getByText(/Interval, dates, closing prices and volumes used by the analysis/)).toBeInTheDocument();
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(data).toEqual(original);
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText(fingerprint)).not.toBeInTheDocument();
  expect(screen.queryByText("Analysis observation fingerprint (SHA-256)")).not.toBeInTheDocument();
});

it.each([undefined, null, "", "private-fingerprint", "a".repeat(63), "a".repeat(65), "g".repeat(64), "A".repeat(64), ` ${"a".repeat(64)}`, `${"a".repeat(64)}\n`, 123, true, {}, [], ["a".repeat(64)]].map((value) => ({ value })))(
  "keeps malformed fingerprint %j unavailable while retaining chart and indicators", async ({ value: fingerprint }) => {
    const data = response();
    data.items[0].analysis!.read_identity.dataset_fingerprint = fingerprint as string;
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
    await screen.findByRole("img");
    expect(screen.getByText("Analysis observation fingerprint (SHA-256)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
    expect(screen.getByText("RSI 14")).toBeInTheDocument();
    expect(screen.queryByText("private-fingerprint")).not.toBeInTheDocument();
  },
);

it.each([undefined, null, {}, [], "private-identity"].map((value) => ({ value })))("keeps missing or malformed read identity %j unavailable", async ({ value: identity }) => {
  const data = response();
  data.items[0].analysis!.read_identity = identity as never;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  expect(screen.getByText("Analysis observation fingerprint (SHA-256)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
});

it.each(["id", "en", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("renders fingerprint copy in locale %s", async (locale) => {
  await i18n.changeLanguage(locale);
  const data = response();
  data.items[0].analysis!.read_identity.dataset_fingerprint = "a".repeat(64);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  await screen.findByRole("img");
  expect(screen.getByText(i18n.t("idxResearch.fingerprint")).nextElementSibling).toHaveTextContent(/^a{64}$/);
  expect(screen.getByText(i18n.t("idxResearch.fingerprintScope"))).not.toHaveTextContent("idxResearch.");
});

it("shows failed attempts before successful fallback in backend order", async () => {
  const data = response();
  Object.assign(data.items[0].provenance!, { source: "local", fallback_used: true, attempts: [
    { source: "yfinance", reason: "no_data" }, { source: "yahoo", reason: "fetch_failed" },
  ] });
  // Diagnostics belong to the unavailable path and must not override provenance.
  data.items[0].diagnostics = { attempts: [{ source: "local", reason: "source_unavailable" }] };
  const original = structuredClone(data);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  const group = screen.getByRole("group", { name: "Attempts before fallback data" });
  expect(within(group).getAllByRole("listitem").map((row) => row.textContent)).toEqual([
    "yfinance · No bars returned for this range", "yahoo · Data request failed",
  ]);
  expect(within(group).getByText(/Yahoo and yfinance are transports for one vendor/)).toBeInTheDocument();
  expect(screen.getByRole("img")).toBeInTheDocument();
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(data).toEqual(original);
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByRole("group", { name: "Attempts before fallback data" })).not.toBeInTheDocument();
  expect(screen.getByRole("group", { name: "Source attempts" })).toBeInTheDocument();
});

it.each([undefined, null, [], "private-raw", {}, 0])(
  "marks unavailable fallback attempt metadata neutral: %j", async (attempts) => {
    const data = response();
    Object.assign(data.items[0].provenance!, { fallback_used: true, attempts });
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
    await screen.findByRole("img");
    const group = screen.getByRole("group", { name: "Attempts before fallback data" });
    expect(within(group).getByText("Source attempt details unavailable")).toBeInTheDocument();
    expect(within(group).queryByRole("list")).not.toBeInTheDocument();
    expect(group).not.toHaveTextContent("private-raw");
  },
);

it("does not expose unknown fallback attempt values", async () => {
  const data = response();
  Object.assign(data.items[0].provenance!, { fallback_used: true, attempts: [
    null, ["private-entry"], { source: "private-source", reason: "private-reason" },
    { source: "yahoo", reason: "toString" }, { source: {}, reason: [] },
  ] });
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  const group = screen.getByRole("group", { name: "Attempts before fallback data" });
  expect(within(group).getAllByRole("listitem")).toHaveLength(5);
  expect(within(group).getAllByText(/Attempt outcome unavailable/)).toHaveLength(5);
  expect(group).not.toHaveTextContent(/private-|toString|object Object/);
});

it.each([undefined, false, "true", 1])("requires explicit fallback flag: %j", async (fallback_used) => {
  const data = response();
  Object.assign(data.items[0].provenance!, { fallback_used, attempts: [{ source: "yahoo", reason: "fetch_failed" }] });
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  expect(screen.queryByRole("group", { name: "Attempts before fallback data" })).not.toBeInTheDocument();
});

it.each(["id", "en", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])(
  "renders translated fallback attempts in %s", async (locale) => {
    await i18n.changeLanguage(locale);
    const data = response();
    Object.assign(data.items[0].provenance!, { fallback_used: true, attempts: [{ source: "yahoo", reason: "fetch_failed" }] });
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
    await screen.findByRole("img");
    const group = screen.getByRole("group", { name: i18n.t("idxResearch.fallbackAttempts") });
    expect(group).toHaveTextContent(i18n.t("idxResearch.attemptFailed"));
    expect(group).toHaveTextContent(i18n.t("idxResearch.fallbackAttemptsScope"));
    expect(group).not.toHaveTextContent("idxResearch.");
  },
);

it.each([
  { bar_count: 20, available_bar_count: 19, missing_bar_count: 5, zero_bar_count: 1 },
  { bar_count: 20, available_bar_count: 19, missing_bar_count: 0, zero_bar_count: 1 },
  { bar_count: 20, available_bar_count: 21, missing_bar_count: 0, zero_bar_count: 1 },
  { bar_count: 20, available_bar_count: 19, missing_bar_count: 1, zero_bar_count: 20 },
])("marks contradictory volume coverage unavailable while preserving research: %j", async (coverage) => {
  const data = volumeResponse();
  data.items[0].volume_coverage = coverage;
  const original = structuredClone(data);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(group).getAllByText("Unavailable")).toHaveLength(4);
  expect(screen.getByRole("img")).toBeInTheDocument();
  expect(screen.getByText("RSI 14")).toBeInTheDocument();
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(data).toEqual(original);
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByRole("group", { name: "Volume coverage" })).not.toBeInTheDocument();
});

it("displays backend volume counts without deriving them from chart rows or lookback", async () => {
  mock.getIDXResearch.mockResolvedValue(volumeResponse());
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const coverage = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(coverage).getByText("Bars in volume window").nextElementSibling).toHaveTextContent(/^20$/);
  expect(within(coverage).getByText("Volume available").nextElementSibling).toHaveTextContent(/^19$/);
  expect(within(coverage).getByText("Volume missing").nextElementSibling).toHaveTextContent(/^1$/);
  expect(within(coverage).getByText("Zero volume").nextElementSibling).toHaveTextContent(/^1$/);
  expect(within(coverage).getByText(/Zero volume is included in available volume/)).toBeInTheDocument();
  expect(within(coverage).getByText(/do not verify exchange-session completeness or liquidity/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByRole("group", { name: "Volume coverage" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByRole("group", { name: "Volume coverage" })).toBeInTheDocument();
});

it.each([
  ["all missing", 0, 20, 0],
  ["all zero", 20, 0, 20],
  ["all positive", 20, 0, 0],
])("preserves zero counts for %s volume", async (_scenario, available, missing, zero) => {
  const data = volumeResponse();
  data.items[0].volume_coverage = { bar_count: 20, available_bar_count: available, missing_bar_count: missing, zero_bar_count: zero };
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const coverage = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(coverage).getByText("Volume available").nextElementSibling).toHaveTextContent(new RegExp(`^${available}$`));
  expect(within(coverage).getByText("Volume missing").nextElementSibling).toHaveTextContent(new RegExp(`^${missing}$`));
  expect(within(coverage).getByText("Zero volume").nextElementSibling).toHaveTextContent(new RegExp(`^${zero}$`));
});

it("warns about zero-volume bars whose price differs from the last traded close", async () => {
  const data = volumeResponse();
  data.items[0].bar_audit = { policy: "idx_daily_bar_audit_v1", calendar_verified: false, zero_volume_price_change_dates: ["2026-01-12", "2026-01-13"] };
  const original = structuredClone(data);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  const warning = within(group).getByText(/Zero-volume bars with a price different from the last traded close/);
  expect(warning).toHaveTextContent("(2): 2026-01-12, 2026-01-13.");
  expect(warning).toHaveClass("font-semibold");
  expect(within(group).getByText(/holiday rows and suspensions are not checked/)).toBeInTheDocument();
  // The chart and indicators are kept; the warning does not remove research.
  expect(screen.getByRole("img")).toBeInTheDocument();
  expect(screen.getByText("RSI 14")).toBeInTheDocument();
  expect(data).toEqual(original);
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText(/Zero-volume bars with a price different/)).not.toBeInTheDocument();
});

it("states a clean zero-volume price check without warning styling", async () => {
  const data = volumeResponse();
  data.items[0].bar_audit = { policy: "idx_daily_bar_audit_v1", calendar_verified: false, zero_volume_price_change_dates: [] };
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  const clean = within(group).getByText("No zero-volume bar carries a price different from the last traded close.");
  expect(clean).not.toHaveClass("font-semibold");
});

it.each([undefined, null, { policy: "idx_daily_bar_audit_v1", calendar_verified: false, zero_volume_price_change_dates: ["2026-02-30"] }])(
  "marks an absent or malformed bar audit %j unavailable, not clean", async (audit) => {
    const data = volumeResponse();
    data.items[0].bar_audit = audit as IDXResearchItem["bar_audit"];
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
    const group = await screen.findByRole("group", { name: "Volume coverage" });
    expect(within(group).getByText("Zero-volume price check unavailable.")).toBeInTheDocument();
    expect(within(group).queryByText(/No zero-volume bar carries/)).not.toBeInTheDocument();
    expect(within(group).queryByText("2026-02-30", { exact: false })).not.toBeInTheDocument();
  },
);

it("shows the zero-volume price warning in Indonesian", async () => {
  const data = volumeResponse();
  data.items[0].bar_audit = { policy: "idx_daily_bar_audit_v1", calendar_verified: false, zero_volume_price_change_dates: ["2026-01-12"] };
  mock.getIDXResearch.mockResolvedValue(data);
  await act(async () => { await i18n.changeLanguage("id"); });
  try {
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
    const group = await screen.findByRole("group", { name: i18n.t("idxResearch.volumeCoverage") });
    expect(within(group).getByText(/bar bervolume nol memiliki harga yang berbeda/)).toHaveTextContent("2026-01-12");
    expect(group).not.toHaveTextContent("idxResearch.");
  } finally {
    await act(async () => { await i18n.changeLanguage("en"); });
  }
});

it.each([undefined, null])("marks absent volume coverage %s unavailable while retaining the chart", async (coverage) => {
  const data = response();
  data.items[0].volume_coverage = coverage;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(group).getAllByText("Unavailable")).toHaveLength(4);
  expect(screen.getByRole("img")).toBeInTheDocument();
});

it.each([undefined, null, -1, 1.5, NaN, Infinity, "19", true, Number.MAX_SAFE_INTEGER + 1])("marks invalid volume count %s unavailable without replacing valid neighbors", async (count) => {
  const data = volumeResponse();
  data.items[0].volume_coverage!.available_bar_count = count as number;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(group).getByText("Volume available").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(within(group).getByText("Volume missing").nextElementSibling).toHaveTextContent(/^1$/);
  expect(screen.getByRole("img")).toBeInTheDocument();
});

it("marks a zero total unavailable rather than borrowing the analyzed count", async () => {
  const data = volumeResponse();
  data.items[0].volume_coverage!.bar_count = 0;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const group = await screen.findByRole("group", { name: "Volume coverage" });
  expect(within(group).getByText("Bars in volume window").nextElementSibling).toHaveTextContent(/^Unavailable$/);
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("renders localized volume coverage and large counts in %s", async (language) => {
  await i18n.changeLanguage(language);
  const data = volumeResponse();
  data.items[0].volume_coverage = { bar_count: 1234567, available_bar_count: 1234566, missing_bar_count: 1, zero_bar_count: 0 };
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  const group = await screen.findByRole("group", { name: i18n.t("idxResearch.volumeCoverage") });
  expect(within(group).getByText(i18n.t("idxResearch.volumeBars")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(language).format(1234567));
  expect(within(group).getByText(i18n.t("idxResearch.volumeZero")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(language).format(0));
  expect(within(group).getByText(i18n.t("idxResearch.volumeCoverageScope"))).toBeInTheDocument();
  expect(group).not.toHaveTextContent(/idxResearch\./);
});

it("distinguishes analyzed bars from the response lookback without claiming complete sessions", async () => {
  const data = response();
  data.lookback = 60;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText("Analyzed bars").nextElementSibling).toHaveTextContent(/^1$/);
  expect(within(detail).getByText("Requested bar limit").nextElementSibling).toHaveTextContent(/^60$/);
  expect(within(detail).getByText(/Counts do not verify exchange-session completeness/)).toBeInTheDocument();
  expect(within(detail).getByRole("img")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText("Analyzed bars")).not.toBeInTheDocument();
});

it.each([undefined, 0, -1, 1.5, NaN, Infinity, "60"])("marks invalid analyzed count %s unavailable without counting chart rows", async (count) => {
  const data = response();
  data.items[0].analysis!.read_identity.bar_count = count as number;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText("Analyzed bars").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(within(detail).getByRole("img")).toBeInTheDocument();
});

it("keeps missing read identity unavailable while preserving valid indicators", async () => {
  const data = response();
  delete (data.items[0].analysis as Partial<NonNullable<IDXResearchItem["analysis"]>>).read_identity;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText("Analyzed bars").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(within(detail).getByText("RSI 14")).toBeInTheDocument();
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("renders localized observation counts in %s", async (language) => {
  await i18n.changeLanguage(language);
  mock.getIDXResearch.mockResolvedValue(response());
  render(<IDXResearch />);
  fireEvent.click(await screen.findByRole("button", { name: i18n.t("idxResearch.load") }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText(i18n.t("idxResearch.analyzedBars")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(language).format(1));
  expect(within(detail).getByText(i18n.t("idxResearch.requestedBars")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(language).format(200));
  expect(within(detail).getByText(i18n.t("idxResearch.coverageScope"))).toBeInTheDocument();
  expect(detail).not.toHaveTextContent(/idxResearch\.(analyzedBars|requestedBars|coverageScope)/);
});

it("distinguishes retrieval in WIB, source as-of and the last analyzed session", async () => {
  const data = response();
  data.items[0].provenance!.retrieved_at = "2026-01-30T18:05:06Z";
  data.items[0].provenance!.data_as_of = "2026-01-29T00:00:00";
  mock.getIDXResearch.mockResolvedValue(data);
  await i18n.changeLanguage("id");
  render(<IDXResearch />);
  fireEvent.click(await screen.findByRole("button", { name: "Ambil data harian" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  const retrieved = within(detail).getByText("Diambil (Asia/Jakarta)").nextElementSibling;
  expect(retrieved).toHaveTextContent("31/01/2026, 01.05.06 WIB");
  expect(within(detail).getByText("Tanggal as-of sumber").nextElementSibling).toHaveTextContent("2026-01-29");
  expect(within(detail).getByText("Sesi terakhir teramati").nextElementSibling).toHaveTextContent("2026-01-30");
  expect(within(detail).getByText(/Waktu pengambilan bukan waktu transaksi/)).toBeInTheDocument();
});

it("keeps the chart available when time metadata cannot be interpreted", async () => {
  const data = response();
  data.items[0].provenance!.retrieved_at = "2026-01-30T18:05:06";
  data.items[0].provenance!.data_as_of = "2026-02-30T00:00:00";
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText("Retrieved (Asia/Jakarta)").nextElementSibling).toHaveTextContent("Unavailable");
  expect(within(detail).getByText("Source as-of date").nextElementSibling).toHaveTextContent("Unavailable");
  expect(within(detail).getByRole("img")).toBeInTheDocument();
  expect(detail).not.toHaveTextContent(/Invalid Date|2026-02-30|18:05:06/);
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("renders time provenance in %s", async (language) => {
  await i18n.changeLanguage(language);
  const data = response();
  data.items[0].provenance!.data_as_of = "2026-01-30T00:00:00";
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(await screen.findByRole("button", { name: i18n.t("idxResearch.load") }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText(i18n.t("idxResearch.sourceAsOf")).nextElementSibling).toHaveTextContent("2026-01-30");
  expect(within(detail).getByText(i18n.t("idxResearch.retrieved")).nextElementSibling).toHaveTextContent(/WIB$/);
  expect(within(detail).getByText(i18n.t("idxResearch.timeScope"))).toBeInTheDocument();
  expect(detail).not.toHaveTextContent(/idxResearch\.(sourceAsOf|timeScope)|Invalid Date/);
});

function agedResponse(status: "warning" | "within_window", age = 15): IDXResearchResponse {
  const data = response();
  data.items[0].recency = {
    policy: "calendar_age_warning_v1", reference_date: "2026-02-14", last_bar_date: "2026-01-30",
    age_calendar_days: age, warning_after_calendar_days: 14, status, calendar_verified: false,
  };
  data.requested_end_date = "2026-02-14";
  return data;
}

function rejectedResponse(code?: string): IDXResearchResponse {
  const data = response();
  data.items[1].reason = "invalid_data_or_metadata";
  if (code !== undefined) data.items[1].quality_issue = { code };
  return data;
}

it.each([
  ["en", "Instrument identity declaration"],
  ["id", "Deklarasi identitas instrumen"],
  ["tr", "Enstrüman kimliği beyanı"],
  ["ar", "إقرار هوية الأداة المالية"],
  ["de", "Deklaration der Instrumentenidentität"],
  ["es", "Declaración de identidad del instrumento"],
  ["fa", "اظهار هویت ابزار مالی"],
  ["ja", "銘柄識別情報の宣言"],
  ["ko", "종목 식별 정보 선언"],
  ["pt-BR", "Declaração de identidade do instrumento"],
  ["zh-CN", "标的身份声明"],
])("explains instrument identity rejection in %s without changing the response or fetching again", async (language, label) => {
  await i18n.changeLanguage(language);
  const data = rejectedResponse("instrument_identity");
  const original = structuredClone(data);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  await screen.findByRole("img", { name: /BBCA.JK/ });
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText(i18n.t("idxResearch.qualityStage", { stage: label }))).toBeInTheDocument();
  expect(screen.getByText(i18n.t("idxResearch.qualityScope"))).toBeInTheDocument();
  expect(screen.queryByText(i18n.t("idxResearch.qualityUnknown"))).not.toBeInTheDocument();
  expect(screen.queryByText(/instrument_identity|idxResearch\.quality/)).not.toBeInTheDocument();
  expect(screen.queryByRole("img")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByRole("img", { name: /BBCA.JK/ })).toBeInTheDocument();
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(data).toEqual(original);
});

it.each([
  ["currency_declaration", "Currency declaration"],
  ["session_timezone", "Session timezone"],
  ["daily_interval", "Daily interval"],
  ["share_volume_unit", "Share-volume unit"],
  ["adjustment_declaration", "Price adjustment declaration"],
  ["unique_bar_dates", "Unique bar dates"],
  ["local_session_dates", "Local session dates"],
  ["requested_date_window", "Requested date window"],
  ["price_values", "Price values"],
  ["volume_values", "Volume values"],
  ["indicator_calculation", "Indicator calculation"],
])("explains rejected %s observations while preserving the healthy symbol", async (code, label) => {
  mock.getIDXResearch.mockResolvedValue(rejectedResponse(code));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  expect(await screen.findByRole("img", { name: /BBCA.JK/ })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText(`Failed validation stage: ${label}`)).toBeInTheDocument();
  expect(screen.getByText(/Only the first failed stage is reported/)).toBeInTheDocument();
  expect(screen.queryByRole("img")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByRole("img", { name: /BBCA.JK/ })).toBeInTheDocument();
  expect(screen.queryByText(/Failed validation stage:/)).not.toBeInTheDocument();
});

it.each([undefined, "future_stage_private_detail", "__proto__", "toString"])("safely labels missing or unknown stage %s", async (code) => {
  mock.getIDXResearch.mockResolvedValue(rejectedResponse(code));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText("Validation stage unavailable.")).toBeInTheDocument();
  expect(screen.getByText(/Bars were rejected/)).toBeInTheDocument();
  expect(screen.queryByText(/future_stage_private_detail|__proto__|toString|idxResearch\.quality/)).not.toBeInTheDocument();
});

it("does not invent a validation issue for empty or failed acquisition", async () => {
  mock.getIDXResearch.mockResolvedValue(response());
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText(/No usable bars/)).toBeInTheDocument();
  expect(screen.queryByText(/Validation stage unavailable|Failed validation stage|Only the first failed/)).not.toBeInTheDocument();
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("renders a localized rejection stage in %s", async (language) => {
  await i18n.changeLanguage(language);
  mock.getIDXResearch.mockResolvedValue(rejectedResponse("adjustment_declaration"));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText(i18n.t("idxResearch.qualityStage", { stage: i18n.t("idxResearch.qualityStages.adjustment_declaration") }))).toBeInTheDocument();
  expect(screen.getByText(i18n.t("idxResearch.qualityScope"))).toBeInTheDocument();
  expect(screen.queryByText(/idxResearch\.quality|adjustment_declaration/)).not.toBeInTheDocument();
});

it("keeps old observations available and shows the backend age and dates beside the chart", async () => {
  mock.getIDXResearch.mockResolvedValue(agedResponse("warning"));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const chart = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(chart).getByText("Warning: observation age exceeds 14 calendar days.")).toBeInTheDocument();
  expect(within(chart).getByText("15 calendar days")).toBeInTheDocument();
  const status = within(chart).getByRole("status");
  expect(within(status).getByText("2026-01-30")).toBeInTheDocument();
  expect(within(status).getByText("2026-02-14")).toBeInTheDocument();
  expect(within(chart).getByRole("img")).toBeInTheDocument();
  expect(within(chart).getByText("yahoo")).toBeInTheDocument();
  expect(within(chart).getByText(/does not verify exchange sessions/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /BBCA.JK/ })).toHaveTextContent("Warning: observation age exceeds 14 calendar days.");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText("15 calendar days")).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "Observation age" })).not.toBeInTheDocument();
});

it.each([0, 14])("shows backend within-window status at age %i without claiming fresh data", async (age) => {
  mock.getIDXResearch.mockResolvedValue(agedResponse("within_window", age));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const status = within(await screen.findByRole("region", { name: "BBCA.JK" })).getByRole("status");
  expect(within(status).getByText(`${age} calendar days`)).toBeInTheDocument();
  expect(within(status).getByText("Within the 14 calendar-day observation window.")).toBeInTheDocument();
  expect(screen.queryByText(/Warning: observation age/)).not.toBeInTheDocument();
});

it("uses backend status and threshold rather than deriving its own calendar policy", async () => {
  const data = agedResponse("warning", 3);
  data.items[0].recency!.warning_after_calendar_days = 2;
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const chart = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(chart).getByText("Warning: observation age exceeds 2 calendar days.")).toBeInTheDocument();
});

it.each([
  ["unknown status", { status: "private-unknown-status" }],
  ["missing status", { status: undefined }],
  ["unknown policy", { policy: "private-unknown-policy" }],
  ["invalid age", { age_calendar_days: -1 }],
  ["invalid threshold", { warning_after_calendar_days: "private-threshold" }],
  ["invalid date", { last_bar_date: "private-date" }],
  ["impossible date", { reference_date: "2026-02-30" }],
  ["different calendar scope", { calendar_verified: true }],
])("keeps %s recency neutral on cards and detail without hiding the chart", async (_name, fields) => {
  const data = agedResponse("warning");
  Object.assign(data.items[0].recency!, fields);
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText("Observation age unavailable.")).toBeInTheDocument();
  expect(screen.queryByText(/Warning: observation age/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Within the .* observation window/)).not.toBeInTheDocument();
  expect(detail).not.toHaveTextContent(/private-/);
  expect(within(detail).getByRole("img")).toBeInTheDocument();
  expect(within(detail).getByText("RSI 14")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText("Observation age unavailable.")).not.toBeInTheDocument();
});

it("labels observation age unavailable for responses without recency", async () => {
  mock.getIDXResearch.mockResolvedValue(response());
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  expect(await screen.findByText("Observation age unavailable.")).toBeInTheDocument();
  expect(screen.queryByText(/Within the .* observation window/)).not.toBeInTheDocument();
  expect(screen.getByRole("img")).toBeInTheDocument();
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("localizes unsupported recency in %s without displaying a verdict", async (language) => {
  await i18n.changeLanguage(language);
  const data = agedResponse("warning");
  Object.assign(data.items[0].recency!, { status: "private-unknown-status" });
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  const detail = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(detail).getByText(i18n.t("idxResearch.recencyUnknown"))).toBeInTheDocument();
  expect(detail).not.toHaveTextContent(/private-|idxResearch\./);
  expect(within(detail).getByRole("img")).toBeInTheDocument();
});

it("renders observation warnings and their scope in Indonesian", async () => {
  await i18n.changeLanguage("id");
  mock.getIDXResearch.mockResolvedValue(agedResponse("warning"));
  render(<IDXResearch />);
  fireEvent.click(await screen.findByRole("button", { name: "Ambil data harian" }));
  const chart = await screen.findByRole("region", { name: "BBCA.JK" });
  expect(within(chart).getByRole("heading", { name: "Usia observasi" })).toBeInTheDocument();
  expect(within(chart).getByText("15 hari kalender")).toBeInTheDocument();
  expect(within(chart).getByText("Peringatan: usia observasi melebihi 14 hari kalender.")).toBeInTheDocument();
  expect(within(chart).getByText(/Ini tidak memverifikasi sesi bursa/)).toBeInTheDocument();
});

beforeEach(async () => { clearAnalysisState("idx-research"); mock.getIDXResearch.mockReset(); mock.searchIDXSymbols.mockReset(); await i18n.changeLanguage("en"); });

it.each([
  ["ar", "أبحاث IDX", "ابحث عن رمز في IDX", "بحث عن الرموز", "لم يُعثر على أسهم IDX مدعومة. جرّب اسماً أو رمزاً آخر."],
  ["de", "IDX-Recherche", "IDX-Symbol finden", "Symbole suchen", "Keine unterstützten IDX-Aktien gefunden. Versuchen Sie einen anderen Namen oder ein anderes Kürzel."],
  ["es", "Investigación IDX", "Buscar un símbolo de IDX", "Buscar símbolos", "No se encontraron acciones de IDX compatibles. Pruebe con otro nombre o ticker."],
  ["fa", "پژوهش IDX", "یافتن نماد IDX", "جستجوی نمادها", "هیچ سهم پشتیبانی‌شده‌ای از IDX یافت نشد. نام یا نماد دیگری را امتحان کنید."],
  ["ja", "IDX リサーチ", "IDX 銘柄コードを探す", "銘柄コードを検索", "対応する IDX 株式が見つかりません。別の名称または銘柄コードをお試しください。"],
  ["ko", "IDX 리서치", "IDX 종목 코드 찾기", "종목 코드 검색", "지원되는 IDX 주식을 찾지 못했습니다. 다른 이름이나 종목 코드로 검색하세요."],
  ["pt-BR", "Pesquisa IDX", "Encontrar um símbolo IDX", "Buscar símbolos", "Nenhuma ação IDX compatível foi encontrada. Tente outro nome ou ticker."],
  ["zh-CN", "IDX 研究", "查找 IDX 代码", "搜索代码", "未找到受支持的 IDX 股票。请尝试其他名称或代码。"],
])("renders %s research and empty symbol search in the selected language", async (code, title, label, search, empty) => {
  await i18n.changeLanguage(code);
  mock.searchIDXSymbols.mockResolvedValue({ ok: true, data: { candidates: [], sources: { yahoo: "ok" } } });
  render(<IDXResearch />);
  expect(await screen.findByRole("heading", { name: title })).toBeInTheDocument();
  fireEvent.change(screen.getByRole("textbox", { name: label }), { target: { value: "missing" } });
  fireEvent.click(screen.getByRole("button", { name: search }));
  expect(await screen.findByText(empty)).toBeInTheDocument();
  expect(mock.getIDXResearch).not.toHaveBeenCalled();
});

it("fetches only on request and displays source, missing indicators and unavailable symbols", async () => {
  mock.getIDXResearch.mockResolvedValue(response());
  render(<IDXResearch />);
  expect(mock.getIDXResearch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  expect(await screen.findByRole("img", { name: /BBCA.JK/ })).toBeInTheDocument();
  expect(screen.getByText("yahoo")).toBeInTheDocument();
  expect(screen.getByText("unknown", { exact: true })).toBeInTheDocument();
  expect(screen.getByText("shares")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText(/No usable bars/)).toBeInTheDocument();
  expect(screen.queryByRole("img")).not.toBeInTheDocument();
});

it("rejects bare, duplicate and unsupported symbols without requesting data", () => {
  render(<IDXResearch />);
  for (const codes of ["BBCA", "BBCA.JK,bbca.jk", "BBCA-W.JK", "AAPL.US"]) {
    fireEvent.change(screen.getByRole("textbox", { name: "Watchlist" }), { target: { value: codes } });
    expect(screen.getByRole("button", { name: "Fetch daily data" })).toBeDisabled();
  }
  expect(mock.getIDXResearch).not.toHaveBeenCalled();
});

it("ignores a pending result after the watchlist is edited", async () => {
  let resolve!: (value: IDXResearchResponse) => void;
  mock.getIDXResearch.mockImplementation(() => new Promise((done) => { resolve = done; }));
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  const signal = mock.getIDXResearch.mock.calls[0][1] as AbortSignal;
  fireEvent.change(screen.getByRole("textbox", { name: "Watchlist" }), { target: { value: "TLKM.JK" } });
  expect(signal.aborted).toBe(true);
  await act(async () => resolve(response()));
  expect(screen.queryByRole("img")).not.toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Watchlist" })).toHaveValue("TLKM.JK");
});

it("shows request failure and retains only watchlist settings on return", async () => {
  mock.getIDXResearch.mockRejectedValue(new Error("Source unavailable"));
  const page = render(<IDXResearch />);
  fireEvent.change(screen.getByRole("textbox", { name: "Watchlist" }), { target: { value: "TLKM.JK" } });
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Source unavailable");
  page.unmount(); render(<IDXResearch />);
  expect(screen.getByRole("textbox", { name: "Watchlist" })).toHaveValue("TLKM.JK");
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
});

function searchResponse(symbol = "ASII.JK") {
  return { ok: true, data: { query: "astra", candidates: [{ symbol, name: "Synthetic Astra", venue: "IDX", currency: "IDR", source: "yahoo" }], sources: { yahoo: "ok" } } };
}

function searchFor(query = "astra") {
  fireEvent.change(screen.getByRole("textbox", { name: "Find an IDX symbol" }), { target: { value: query } });
  fireEvent.click(screen.getByRole("button", { name: "Search symbols" }));
}

it("requires explicit selection and adds only a canonical IDX symbol without fetching prices", async () => {
  mock.searchIDXSymbols.mockResolvedValue(searchResponse());
  render(<IDXResearch />);
  searchFor();
  const add = await screen.findByRole("button", { name: "Add ASII.JK" });
  expect(screen.getByRole("textbox", { name: "Watchlist" })).toHaveValue("BBCA.JK, BBRI.JK, TLKM.JK");
  expect(screen.getByText("IDX · IDR · yahoo")).toBeInTheDocument();
  fireEvent.click(add);
  expect(screen.getByRole("textbox", { name: "Watchlist" })).toHaveValue("BBCA.JK, BBRI.JK, TLKM.JK, ASII.JK");
  expect(screen.getByRole("button", { name: "Added ASII.JK" })).toBeDisabled();
  expect(mock.getIDXResearch).not.toHaveBeenCalled();
});

it("prevents adding beyond eight or into an invalid watchlist", async () => {
  mock.searchIDXSymbols.mockResolvedValue(searchResponse());
  render(<IDXResearch />);
  searchFor();
  const add = await screen.findByRole("button", { name: "Add ASII.JK" });
  fireEvent.change(screen.getByRole("textbox", { name: "Watchlist" }), { target: { value: "BBCA.JK, BBRI.JK, TLKM.JK, ANTM.JK, INCO.JK, BBNI.JK, BMRI.JK, UNTR.JK" } });
  expect(add).toBeDisabled();
  fireEvent.change(screen.getByRole("textbox", { name: "Watchlist" }), { target: { value: "BBCA" } });
  expect(add).toBeDisabled();
});

it("displays empty search separately from a Yahoo failure", async () => {
  mock.searchIDXSymbols.mockResolvedValueOnce({ ok: true, data: { candidates: [], sources: { yahoo: "ok" } } });
  render(<IDXResearch />);
  searchFor("missing");
  expect(await screen.findByText(/No supported IDX shares/)).toBeInTheDocument();
  mock.searchIDXSymbols.mockResolvedValueOnce({ ok: true, data: { candidates: [], sources: { yahoo: "Synthetic outage" } } });
  searchFor("bank");
  expect(await screen.findByRole("alert")).toHaveTextContent("Yahoo symbol search is unavailable");
  expect(screen.queryByText(/No supported IDX shares/)).not.toBeInTheDocument();
});

it("shows transport failure and permits a retry", async () => {
  mock.searchIDXSymbols.mockRejectedValueOnce(new Error("offline"));
  render(<IDXResearch />);
  searchFor();
  expect(await screen.findByRole("alert")).toHaveTextContent("Yahoo symbol search is unavailable");
  mock.searchIDXSymbols.mockResolvedValueOnce(searchResponse());
  fireEvent.click(screen.getByRole("button", { name: "Search symbols" }));
  expect(await screen.findByRole("button", { name: "Add ASII.JK" })).toBeEnabled();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it("aborts and ignores an older search even when it completes after the new query", async () => {
  let resolve!: (value: ReturnType<typeof searchResponse>) => void;
  mock.searchIDXSymbols.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  render(<IDXResearch />);
  searchFor();
  const signal = mock.searchIDXSymbols.mock.calls[0][1] as AbortSignal;
  mock.searchIDXSymbols.mockResolvedValueOnce(searchResponse("BBNI.JK"));
  searchFor("bank");
  expect(signal.aborted).toBe(true);
  expect(await screen.findByRole("button", { name: "Add BBNI.JK" })).toBeInTheDocument();
  await act(async () => resolve(searchResponse()));
  expect(screen.queryByRole("button", { name: "Add ASII.JK" })).not.toBeInTheDocument();
});

it("aborts pending symbol search on unmount", () => {
  mock.searchIDXSymbols.mockImplementation(() => new Promise(() => {}));
  const page = render(<IDXResearch />);
  searchFor();
  const signal = mock.searchIDXSymbols.mock.calls[0][1] as AbortSignal;
  page.unmount();
  expect(signal.aborted).toBe(true);
});

it("does not offer malformed symbols or conflicting venues returned by a server", async () => {
  mock.searchIDXSymbols.mockResolvedValueOnce(searchResponse("BBCA-W.JK"));
  render(<IDXResearch />);
  searchFor();
  await act(async () => {});
  expect(screen.queryByRole("button", { name: /Add .*JK/ })).not.toBeInTheDocument();
});


it("shows source attempts in backend order only for acquisition failures", async () => {
  const data = response();
  data.items[1].diagnostics = { attempts: [
    { source: "yfinance", reason: "no_data" },
    { source: "yahoo", reason: "fetch_failed" },
    { source: "local", reason: "source_unavailable" },
  ] };
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  expect(screen.queryByRole("group", { name: "Source attempts" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  const group = screen.getByRole("group", { name: "Source attempts" });
  expect(within(group).getAllByRole("listitem").map((row) => row.textContent)).toEqual([
    "yfinance · No bars returned for this range",
    "yahoo · Data request failed",
    "local · Source unavailable; check configuration or optional dependencies",
  ]);
  expect(within(group).getByText(/do not establish suspension, delisting or a complete trading calendar/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByRole("img")).toBeInTheDocument();
  expect(screen.queryByRole("group", { name: "Source attempts" })).not.toBeInTheDocument();
});

it.each([undefined, null, {}, { attempts: [] }, { attempts: null }, { attempts: "private-raw" }])(
  "marks absent or malformed source attempts unavailable: %j", async (diagnostics) => {
    const data = response();
    data.items[1].diagnostics = diagnostics as IDXResearchItem["diagnostics"];
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
    await screen.findByRole("img");
    fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
    const group = screen.getByRole("group", { name: "Source attempts" });
    expect(within(group).getByText("Source attempt details unavailable")).toBeInTheDocument();
    expect(within(group).queryByRole("list")).not.toBeInTheDocument();
    expect(group).not.toHaveTextContent("private-raw");
  },
);

it("keeps unknown source attempts neutral without exposing raw values or recovery text", async () => {
  const data = response();
  data.items[1].diagnostics = { attempts: [
    null, { source: "private-source", reason: "private-reason" },
    { source: "yahoo", reason: "toString" },
  ], recovery: "private-recovery" } as unknown as IDXResearchItem["diagnostics"];
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  const group = screen.getByRole("group", { name: "Source attempts" });
  expect(within(group).getAllByRole("listitem")).toHaveLength(3);
  expect(within(group).getAllByText(/Attempt outcome unavailable/)).toHaveLength(3);
  expect(group).not.toHaveTextContent("private-");
  expect(group).not.toHaveTextContent("toString");
});

it.each(["id", "en", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])(
  "renders translated acquisition diagnostics in %s", async (locale) => {
    await i18n.changeLanguage(locale);
    const data = response();
    data.items[1].diagnostics = { attempts: [{ source: "yahoo", reason: "fetch_failed" }] };
    mock.getIDXResearch.mockResolvedValue(data);
    render(<IDXResearch />);
    fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
    await screen.findByRole("img");
    fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
    const group = screen.getByRole("group", { name: i18n.t("idxResearch.sourceAttempts") });
    expect(group).toHaveTextContent(i18n.t("idxResearch.attemptFailed"));
    expect(group).not.toHaveTextContent("idxResearch.");
  },
);


it("keeps validation rejection separate from acquisition attempts", async () => {
  const data = rejectedResponse("price_values");
  data.items[1].diagnostics = { attempts: [{ source: "yahoo", reason: "fetch_failed" }] };
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: "Fetch daily data" }));
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.getByText("Failed validation stage: Price values")).toBeInTheDocument();
  expect(screen.queryByRole("group", { name: "Source attempts" })).not.toBeInTheDocument();
});
