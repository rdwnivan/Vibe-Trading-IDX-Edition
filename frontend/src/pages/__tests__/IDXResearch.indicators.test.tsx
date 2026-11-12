import { fireEvent, render, screen } from "@testing-library/react";
import i18n from "@/i18n";
import { clearAnalysisState } from "@/hooks/useAnalysisState";
import { IDXResearch } from "../IDXResearch";

const mock = vi.hoisted(() => ({ getIDXResearch: vi.fn() }));
vi.mock("@/lib/api", () => ({ api: mock }));
vi.mock("@/hooks/useChartLifecycle", () => ({ useChartLifecycle: vi.fn() }));

// Synthetic response: indicator values deliberately cannot be derived from one bar.
function response() {
  return {
    ok: true, status: "partial", requested_start_date: "2026-01-01", requested_end_date: "2026-01-30", interval: "1D", lookback: 200,
    items: [{ symbol: "BBCA.JK", status: "ok", provenance: { source: "yahoo", adjustment: "unknown" },
      bars: [{ date: "2026-01-30", open: 100, high: 110, low: 90, close: 105, volume: 10 }],
      analysis: { latest_close: 105, latest_date: "2026-01-30", read_identity: { dataset_fingerprint: "synthetic", bar_count: 1 },
        indicators: { rsi_14: null, sma_20: null, sma_50: null, sma_200: null, ema_20: null,
          macd: { macd_line: 0.1234, signal_line: -0.0001, histogram: 0 },
          bollinger: { upper: 123.45, middle: 111.25, lower: 99.05 },
          volume: { latest: 10, sma_20: 1234567890.125, ratio_20: null, unit: "shares" } } } },
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

it("shows the received MACD components, Bollinger bands and mean share volume without recalculating or refetching", async () => {
  const data = response();
  const original = structuredClone(data);
  await load(data);

  expect(screen.getByText("MACD").nextElementSibling).toHaveTextContent(/^0.1234$/);
  expect(screen.getByText("MACD signal (IDR)").nextElementSibling).toHaveTextContent(/^-0.0001$/);
  expect(screen.getByText("MACD histogram (IDR)").nextElementSibling).toHaveTextContent(/^0$/);
  expect(screen.getByText("Bollinger upper 20 (IDR)").nextElementSibling).toHaveTextContent(/^123.45$/);
  expect(screen.getByText("Bollinger middle 20 (IDR)").nextElementSibling).toHaveTextContent(/^111.25$/);
  expect(screen.getByText("Bollinger lower 20 (IDR)").nextElementSibling).toHaveTextContent(/^99.05$/);
  expect(screen.getByText("20-bar mean volume (shares)").nextElementSibling).toHaveTextContent(/^1,234,567,890.125$/);
  expect(data).toEqual(original);
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
  expect(screen.getByRole("img")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBRI.JK/ }));
  expect(screen.queryByText("MACD signal (IDR)")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /BBCA.JK/ }));
  expect(screen.getByText("MACD signal (IDR)")).toBeInTheDocument();
  expect(mock.getIDXResearch).toHaveBeenCalledTimes(1);
});

it.each([null, undefined])("marks absent indicator structures %s unavailable and retains the short history chart", async (missing) => {
  const data = response();
  Object.assign(data.items[0].analysis!.indicators, { macd: missing, bollinger: missing, volume: missing });
  await load(data);

  expect(screen.getByText("MACD signal (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("MACD histogram (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("Bollinger upper 20 (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("Bollinger middle 20 (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("Bollinger lower 20 (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("20-bar mean volume (shares)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByRole("img")).toBeInTheDocument();
});

it("keeps missing component values distinct from zero and negative values", async () => {
  const data = response();
  Object.assign(data.items[0].analysis!.indicators, {
    macd: { macd_line: null, signal_line: null, histogram: -12.3456 },
    bollinger: { upper: null, middle: 0, lower: -0.25 },
    volume: { latest: null, sma_20: 0, ratio_20: null, unit: "shares" },
  });
  await load(data);

  expect(screen.getByText("MACD signal (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("MACD histogram (IDR)").nextElementSibling).toHaveTextContent(/^-12.3456$/);
  expect(screen.getByText("Bollinger upper 20 (IDR)").nextElementSibling).toHaveTextContent(/^Unavailable$/);
  expect(screen.getByText("Bollinger middle 20 (IDR)").nextElementSibling).toHaveTextContent(/^0$/);
  expect(screen.getByText("Bollinger lower 20 (IDR)").nextElementSibling).toHaveTextContent(/^-0.25$/);
  expect(screen.getByText("20-bar mean volume (shares)").nextElementSibling).toHaveTextContent(/^0$/);
});

it.each(["en", "id", "tr", "ar", "de", "es", "fa", "ja", "ko", "pt-BR", "zh-CN"])("formats received indicator values and translated labels in %s", async (locale) => {
  await i18n.changeLanguage(locale);
  await load();

  expect(screen.getByText(i18n.t("idxResearch.macdSignal")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(locale, { maximumSignificantDigits: 17 }).format(-0.0001));
  expect(screen.getByText(i18n.t("idxResearch.bollingerUpper")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(locale, { maximumSignificantDigits: 17 }).format(123.45));
  expect(screen.getByText(i18n.t("idxResearch.volumeMean")).nextElementSibling).toHaveTextContent(new Intl.NumberFormat(locale, { maximumSignificantDigits: 17 }).format(1234567890.125));
});
