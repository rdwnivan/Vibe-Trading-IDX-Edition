import { fireEvent, render, screen, within } from "@testing-library/react";
import i18n from "@/i18n";
import { clearAnalysisState } from "@/hooks/useAnalysisState";
import type { IDXBar, IDXResearchResponse } from "@/lib/idx-research";
import { IDXResearch } from "../IDXResearch";

const mock = vi.hoisted(() => ({ getIDXResearch: vi.fn() }));
vi.mock("@/lib/api", () => ({ api: mock }));
vi.mock("@/hooks/useChartLifecycle", () => ({ useChartLifecycle: vi.fn() }));

function response(): IDXResearchResponse {
  return {
    ok: true, status: "partial", requested_start_date: "2026-01-01", requested_end_date: "2026-01-30", interval: "1D", lookback: 200,
    items: [{ symbol: "BBCA.JK", status: "ok", provenance: { source: "yahoo", adjustment: "unknown", volume_unit: "shares" },
      bars: [
        { date: "2026-01-28", open: 100.123456789, high: 110.5, low: 90.25, close: 105.75, volume: 0 },
        { date: "2026-01-30", open: 200, high: 220, low: 180, close: 210, volume: null },
      ],
      analysis: { latest_close: 210, latest_date: "2026-01-30", read_identity: { dataset_fingerprint: "synthetic", bar_count: 2 },
        indicators: { rsi_14: null, sma_20: null, sma_50: null, sma_200: null, ema_20: null, macd: null, volume: { latest: null, sma_20: null, ratio_20: null, unit: "shares" } } } },
    { symbol: "BBRI.JK", status: "unavailable", reason: "no_data_or_source_failure", provenance: null }],
  };
}

beforeEach(async () => {
  clearAnalysisState("idx-research");
  mock.getIDXResearch.mockReset();
  await i18n.changeLanguage("en");
});

async function load(data = response()) {
  mock.getIDXResearch.mockResolvedValue(data);
  render(<IDXResearch />);
  fireEvent.click(screen.getByRole("button", { name: i18n.t("idxResearch.load") }));
  await screen.findByRole("img");
}

function openObservations() {
  fireEvent.click(screen.getByText(i18n.t("idxResearch.observations"), { selector: "summary" }));
  expect(screen.getByText(i18n.t("idxResearch.observations"), { selector: "summary" }).parentElement).toHaveAttribute("open");
  return screen.getByRole("table", { name: `BBCA.JK · ${i18n.t("idxResearch.observations")}` });
}

it("reveals the response OHLCV values, keeping date gaps, zero volume and missing volume distinct", async () => {
  const data = response();
  const original = structuredClone(data);
  await load(data);
  expect(screen.getByText("Daily OHLCV observations", { selector: "summary" }).parentElement).not.toHaveAttribute("open");

  const table = openObservations();
  const rows = within(table).getAllByRole("row");
  expect(rows).toHaveLength(3);
  expect(within(rows[1]).getByRole("rowheader")).toHaveTextContent("2026-01-28");
  expect(within(rows[1]).getAllByRole("cell").map((cell) => cell.textContent)).toEqual(["100.123456789", "110.5", "90.25", "105.75", "0"]);
  expect(within(rows[2]).getByRole("rowheader")).toHaveTextContent("2026-01-30");
  expect(within(rows[2]).getAllByRole("cell").map((cell) => cell.textContent)).toEqual(["200", "220", "180", "210", "Unavailable"]);
  expect(table).not.toHaveTextContent("2026-01-29");
  expect(data).toEqual(original);
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(screen.getByRole("img")).toBeInTheDocument();
  expect(screen.getByText("RSI 14")).toBeInTheDocument();
});

it("provides scoped headers and a named, focusable scroll region", async () => {
  await load();
  const table = openObservations();

  expect(within(table).getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
    "Session date", "Open (IDR)", "High (IDR)", "Low (IDR)", "Close (IDR)", "Volume (shares)",
  ]);
  expect(within(table).getAllByRole("columnheader").every((header) => header.getAttribute("scope") === "col")).toBe(true);
  const region = screen.getByRole("region", { name: "Daily OHLCV observations" });
  expect(region).toHaveAttribute("tabindex", "0");
  expect(region).toHaveClass("overflow-auto", "max-h-80");
  expect(screen.getByText(/using the reported price adjustment/)).toBeInTheDocument();
});

it("uses the native disclosure and hides observations for unavailable symbols", async () => {
  await load();
  openObservations();
  fireEvent.click(screen.getByText("Daily OHLCV observations", { selector: "summary" }));
  expect(screen.getByText("Daily OHLCV observations", { selector: "summary" }).parentElement).not.toHaveAttribute("open");
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText("Daily OHLCV observations", { selector: "summary" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByText("Daily OHLCV observations", { selector: "summary" }).parentElement).not.toHaveAttribute("open");
  expect(openObservations()).toBeInTheDocument();
});

it.each([undefined, []])("keeps missing or empty bars %s visibly unavailable without inventing a table", async (bars) => {
  const data = response();
  data.items[0].bars = bars;
  await load(data);
  const summary = screen.getByText("Daily OHLCV observations", { selector: "summary" });
  fireEvent.click(summary);

  expect(within(summary.parentElement!).getByText("Unavailable")).toBeInTheDocument();
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(screen.getByRole("img")).toBeInTheDocument();
});

it("displays all 500 received bars inside the bounded scroll region", async () => {
  const data = response();
  data.items[0].bars = Array.from({ length: 500 }, (_, index): IDXBar => ({
    date: new Date(Date.UTC(2024, 0, index + 1)).toISOString().slice(0, 10),
    open: 100, high: 110, low: 90, close: 105, volume: index,
  }));
  await load(data);

  const table = openObservations();
  expect(within(table).getAllByRole("row")).toHaveLength(501);
  expect(within(table).getAllByRole("rowheader")[499]).toHaveTextContent("2025-05-14");
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("localizes the table and large numbers in %s", async (language) => {
  await i18n.changeLanguage(language);
  const data = response();
  data.items[0].bars![0].volume = 1234567890123;
  await load(data);

  const table = openObservations();
  expect(within(table).getByRole("columnheader", { name: i18n.t("idxResearch.observationVolume") })).toBeInTheDocument();
  expect(within(table).getByText(new Intl.NumberFormat(language).format(1234567890123))).toBeInTheDocument();
  expect(within(table).getByText(i18n.t("idxResearch.unknown"))).toBeInTheDocument();
  expect(within(table).getByRole("rowheader", { name: "2026-01-28" })).toBeInTheDocument();
  expect(table).not.toHaveTextContent("idxResearch.");
});
