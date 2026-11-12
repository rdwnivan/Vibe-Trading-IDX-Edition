import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "@/lib/api";
import type { IDXBar, IDXResearchResponse, IDXSymbolSearchResponse } from "@/lib/idx-research";
import { formatIDXRetrievedAt, formatIDXSourceAsOf, getIDXRecency, getIDXVolumeCoverage } from "@/lib/idx-research";
import { useAnalysisState } from "@/hooks/useAnalysisState";
import { useChartLifecycle } from "@/hooks/useChartLifecycle";
import { getChartTheme } from "@/lib/chart-theme";

// Presentation only: validation and the first failing stage belong to the backend.
const qualityStageKeys = {
  instrument_identity: "idxResearch.qualityStages.instrument_identity",
  currency_declaration: "idxResearch.qualityStages.currency_declaration",
  session_timezone: "idxResearch.qualityStages.session_timezone",
  daily_interval: "idxResearch.qualityStages.daily_interval",
  share_volume_unit: "idxResearch.qualityStages.share_volume_unit",
  adjustment_declaration: "idxResearch.qualityStages.adjustment_declaration",
  unique_bar_dates: "idxResearch.qualityStages.unique_bar_dates",
  local_session_dates: "idxResearch.qualityStages.local_session_dates",
  requested_date_window: "idxResearch.qualityStages.requested_date_window",
  price_values: "idxResearch.qualityStages.price_values",
  volume_values: "idxResearch.qualityStages.volume_values",
  indicator_calculation: "idxResearch.qualityStages.indicator_calculation",
} as const;

const attemptReasonKeys = {
  no_data: "idxResearch.attemptNoData",
  fetch_failed: "idxResearch.attemptFailed",
  source_unavailable: "idxResearch.attemptUnavailable",
} as const;

// Show only known source identifiers, never arbitrary server text.
const attemptSources = new Set(["yahoo", "yfinance", "local"]);

function SourceAttempts({ value, fallback = false }: { value: unknown; fallback?: boolean }) {
  const { t } = useTranslation();
  const attempts = Array.isArray(value) ? value : [];
  const title = t(fallback ? "idxResearch.fallbackAttempts" : "idxResearch.sourceAttempts");
  return <div role="group" aria-label={title} className="mt-4 min-w-0 border-t pt-4">
    <h3 className="font-medium">{title}</h3>
    {attempts.length ? <ol className="mt-2 list-inside list-decimal space-y-2 break-words">{attempts.map((attempt, index) => {
      const source = typeof attempt?.source === "string" && attemptSources.has(attempt.source) ? attempt.source : t("idxResearch.unknown");
      const reasonKey = typeof attempt?.reason === "string" && Object.prototype.hasOwnProperty.call(attemptReasonKeys, attempt.reason)
        ? attemptReasonKeys[attempt.reason as keyof typeof attemptReasonKeys] : "idxResearch.attemptUnknown";
      return <li key={index}>{source} · {t(reasonKey)}</li>;
    })}</ol> : <p className="mt-2 text-muted-foreground">{t("idxResearch.attemptsUnknown")}</p>}
    <p className="mt-3 text-xs text-muted-foreground">{t(fallback ? "idxResearch.fallbackAttemptsScope" : "idxResearch.attemptsScope")}</p>
  </div>;
}

function CloseChart({ bars, label }: { bars: IDXBar[]; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useChartLifecycle(ref, () => {
    const theme = getChartTheme();
    return {
      animation: false,
      tooltip: { trigger: "axis", renderMode: "richText" },
      grid: { left: 12, right: 16, top: 20, bottom: 40, containLabel: true },
      xAxis: { type: "category", data: bars.map((bar) => bar.date), axisLabel: { color: theme.textColor } },
      yAxis: { type: "value", scale: true, axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridColor } } },
      series: [{ name: label, type: "line", showSymbol: bars.length === 1, connectNulls: false, data: bars.map((bar) => bar.close) }],
    };
  }, [bars, label]);
  return <div ref={ref} role="img" aria-label={label} className="h-72 w-full" />;
}

function ObservationTable({ bars, symbol }: { bars: IDXBar[]; symbol: string }) {
  const { t, i18n } = useTranslation();
  // Locale formatting only: retain the response values, including adjusted prices.
  const numbers = new Intl.NumberFormat(i18n.language, { maximumSignificantDigits: 17 });
  const value = (number: number | null) => number === null ? t("idxResearch.unknown") : numbers.format(number);
  return <details className="min-w-0 border-t py-3">
    <summary className="cursor-pointer rounded-sm py-2 text-sm font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring">{t("idxResearch.observations")}</summary>
    <p className="my-3 text-xs text-muted-foreground">{t("idxResearch.observationsScope")}</p>
    {bars.length ? <div role="region" aria-label={t("idxResearch.observations")} tabIndex={0} className="max-h-80 w-full overflow-auto rounded-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring">
      <table className="w-full whitespace-nowrap text-sm tabular-nums">
        <caption className="sr-only">{symbol} · {t("idxResearch.observations")}</caption>
        <thead className="sticky top-0 bg-background"><tr>
          {(["observationDate", "observationOpen", "observationHigh", "observationLow", "observationClose", "observationVolume"] as const).map((key) => <th key={key} scope="col" className="border-b px-3 py-2 text-end first:text-start">{t(`idxResearch.${key}`)}</th>)}
        </tr></thead>
        <tbody>{bars.map((bar) => <tr key={bar.date} className="border-b last:border-0">
          <th scope="row" className="px-3 py-2 text-start font-normal"><bdi>{bar.date}</bdi></th>
          {[bar.open, bar.high, bar.low, bar.close, bar.volume].map((number, index) => <td key={index} className="px-3 py-2 text-end">{value(number)}</td>)}
        </tr>)}</tbody>
      </table>
    </div> : <p className="text-sm text-muted-foreground">{t("idxResearch.unknown")}</p>}
  </details>;
}

export function IDXResearch() {
  const { t, i18n } = useTranslation();
  const [draft, setDraft] = useAnalysisState("idx-research", { codes: "BBCA.JK, BBRI.JK, TLKM.JK", lookback: 200, endDate: "" });
  const [result, setResult] = useState<IDXResearchResponse | null>(null);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const generation = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState<IDXSymbolSearchResponse | null>(null);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState(false);
  const searchGeneration = useRef(0);
  const searchController = useRef<AbortController | null>(null);
  useEffect(() => () => {
    generation.current += 1; controller.current?.abort();
    searchGeneration.current += 1; searchController.current?.abort();
  }, []);
  const codes = draft.codes.split(/[,;\s]+/).filter(Boolean).map((code) => code.toUpperCase());
  const valid = codes.length > 0 && codes.length <= 8 && new Set(codes).size === codes.length && codes.every((code) => /^[A-Z]{4}\.JK$/.test(code));
  const format = (value: number | null | undefined) => value == null ? t("idxResearch.unknown") : new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 2 }).format(value);
  // Preserve the backend's indicator precision, including small MACD components.
  const formatIndicator = (value: number | null | undefined) => value == null ? t("idxResearch.unknown") : new Intl.NumberFormat(i18n.language, { maximumSignificantDigits: 17 }).format(value);
  // Missing/invalid counts stay unavailable; chart rows do not replace analysis metadata.
  const formatBarCount = (value: unknown) => typeof value === "number" && Number.isSafeInteger(value) && value > 0
    ? new Intl.NumberFormat(i18n.language).format(value) : t("idxResearch.unknown");
  const item = result?.items.find((entry) => entry.symbol === selected);
  const indicators = item?.analysis?.indicators;
  const provenance = item?.provenance;
  const recency = getIDXRecency(item?.recency);
  const volumeCoverage = getIDXVolumeCoverage(item?.volume_coverage);
  // Backend hexdigest only; do not derive identity from chart rows or normalize it.
  const rawFingerprint = item?.analysis?.read_identity?.dataset_fingerprint;
  const fingerprint = typeof rawFingerprint === "string" && rawFingerprint.length === 64 && /^[a-f0-9]+$/.test(rawFingerprint)
    ? rawFingerprint : t("idxResearch.unknown");
  const qualityCode = item?.quality_issue?.code;
  const qualityStageKey = qualityCode && Object.prototype.hasOwnProperty.call(qualityStageKeys, qualityCode)
    ? qualityStageKeys[qualityCode as keyof typeof qualityStageKeys] : null;

  function changeQuery(value: string) {
    searchGeneration.current += 1;
    searchController.current?.abort();
    setQuery(value);
    setSearchResult(null);
    setSearchError(false);
    setSearching(false);
  }

  async function search() {
    if (!query.trim()) return;
    searchController.current?.abort();
    const pending = new AbortController();
    searchController.current = pending;
    const current = ++searchGeneration.current;
    setSearching(true); setSearchError(false); setSearchResult(null);
    try {
      const response = await api.searchIDXSymbols(query.trim(), pending.signal);
      if (searchGeneration.current !== current) return;
      if (!response.ok || response.data.sources.yahoo !== "ok") setSearchError(true);
      else setSearchResult(response);
    } catch {
      if (searchGeneration.current === current && !pending.signal.aborted) setSearchError(true);
    } finally {
      if (searchGeneration.current === current) setSearching(false);
    }
  }

  function edit(update: Partial<typeof draft>) {
    generation.current += 1;
    controller.current?.abort();
    setLoading(false);
    setError(null);
    setResult(null);
    setDraft((previous) => ({ ...previous, ...update }));
  }

  async function load() {
    if (!valid) return;
    controller.current?.abort();
    const pending = new AbortController();
    controller.current = pending;
    const current = ++generation.current;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.getIDXResearch({ codes, lookback: draft.lookback, ...(draft.endDate ? { end_date: draft.endDate } : {}) }, pending.signal);
      if (generation.current !== current) return;
      setResult(response);
      setSelected(response.items.find((entry) => entry.status === "ok")?.symbol ?? response.items[0]?.symbol ?? "");
    } catch (failure) {
      if (generation.current === current && !pending.signal.aborted) setError(failure instanceof Error ? failure.message : t("idxResearch.failed"));
    } finally {
      if (generation.current === current) setLoading(false);
    }
  }

  return <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 sm:p-6">
    <header><h1 className="text-2xl font-semibold">{t("idxResearch.title")}</h1><p className="mt-2 text-sm text-muted-foreground">{t("idxResearch.intro")}</p></header>
    <section className="rounded-xl border p-4" aria-label={t("idxResearch.searchLabel")}>
      <form onSubmit={(event) => { event.preventDefault(); void search(); }} className="flex flex-wrap items-end gap-3">
        <div className="min-w-0 flex-1"><label htmlFor="idx-search" className="text-sm font-medium">{t("idxResearch.searchLabel")}</label><input id="idx-search" value={query} maxLength={120} onChange={(event) => changeQuery(event.target.value)} aria-describedby="idx-search-hint" className="mt-2 min-h-11 w-full rounded-md border bg-background px-3 text-base" /></div>
        <button type="submit" disabled={!query.trim() || searching} className="min-h-11 rounded-md border px-4 text-sm disabled:opacity-50">{t(searching ? "idxResearch.searching" : "idxResearch.search")}</button>
      </form>
      <p id="idx-search-hint" className="mt-2 text-xs text-muted-foreground">{t("idxResearch.searchHint")}</p>
      <div aria-live="polite">
        {searchError && <p role="alert" className="mt-3 text-sm text-destructive">{t("idxResearch.searchFailed")}</p>}
        {searchResult && searchResult.data.candidates.length === 0 && <p className="mt-3 text-sm">{t("idxResearch.searchEmpty")}</p>}
        {searchResult && <ul className="mt-3 divide-y">{searchResult.data.candidates.map((candidate) => {
          const added = codes.includes(candidate.symbol);
          const supported = /^[A-Z]{4}\.JK$/.test(candidate.symbol) && candidate.venue === "IDX" && candidate.currency === "IDR";
          return supported && <li key={candidate.symbol} className="flex items-center justify-between gap-3 py-2">
            <div className="min-w-0 break-words text-sm"><span className="font-medium">{candidate.symbol}</span> · {candidate.name}<span className="block text-xs text-muted-foreground">{candidate.venue} · {candidate.currency} · {candidate.source}</span></div>
            <button type="button" disabled={added || codes.length >= 8 || (codes.length > 0 && !valid)} onClick={() => edit({ codes: [...codes, candidate.symbol].join(", ") })} aria-label={`${t(added ? "idxResearch.added" : "idxResearch.add")} ${candidate.symbol}`} className="min-h-11 shrink-0 rounded-md border px-3 text-sm disabled:opacity-50">{t(added ? "idxResearch.added" : "idxResearch.add")}</button>
          </li>;
        })}</ul>}
      </div>
    </section>
    <form onSubmit={(event) => { event.preventDefault(); void load(); }} className="flex flex-col gap-4 rounded-xl border p-4">
      <div><label htmlFor="idx-codes" className="text-sm font-medium">{t("idxResearch.watchlist")}</label><input id="idx-codes" value={draft.codes} onChange={(event) => edit({ codes: event.target.value })} maxLength={120} aria-describedby="idx-codes-hint" className="mt-2 min-h-11 w-full rounded-md border bg-background px-3 text-base" /><p id="idx-codes-hint" className="mt-2 text-xs text-muted-foreground">{t("idxResearch.hint")}</p></div>
      <div className="flex flex-wrap items-end gap-4">
        <div><label htmlFor="idx-lookback" className="block text-sm">{t("idxResearch.lookback")}</label><select id="idx-lookback" value={draft.lookback} onChange={(event) => edit({ lookback: Number(event.target.value) })} className="mt-2 min-h-11 rounded-md border bg-background px-3">{[60, 200, 500].map((count) => <option key={count} value={count}>{count}</option>)}</select></div>
        <div><label htmlFor="idx-end" className="block text-sm">{t("idxResearch.endDate")}</label><input id="idx-end" type="date" value={draft.endDate} onChange={(event) => edit({ endDate: event.target.value })} className="mt-2 min-h-11 rounded-md border bg-background px-3 text-base" /></div>
        <button type="submit" disabled={!valid || loading} className="min-h-11 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground disabled:opacity-50">{t(loading ? "idxResearch.loading" : "idxResearch.load")}</button>
      </div>
    </form>
    {error && <p role="alert" className="rounded-lg border border-destructive p-4 text-sm text-destructive">{error}</p>}
    <div aria-live="polite">{loading ? <p className="text-sm text-muted-foreground">{t("idxResearch.loading")}</p> : !result && !error ? <p className="text-sm text-muted-foreground">{t("idxResearch.empty")}</p> : null}</div>
    {result && <>
      <p className="text-xs text-muted-foreground">{result.requested_start_date} — {result.requested_end_date} · 1D · {t("idxResearch.snapshot")}</p>
      {result.status !== "ok" && <p role="status" className="text-sm">{t("idxResearch.partial")}</p>}
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3" aria-label={t("idxResearch.watchlist")}>
        {result.items.map((entry) => {
          const entryRecency = getIDXRecency(entry.recency);
          return <button key={entry.symbol} type="button" aria-pressed={selected === entry.symbol} onClick={() => setSelected(entry.symbol)} className={`min-h-20 rounded-xl border p-4 text-start ${selected === entry.symbol ? "border-primary bg-primary/5" : "hover:bg-muted"}`}><span className="block text-sm font-medium">{entry.symbol}</span><span className="mt-1 block text-lg tabular-nums">{entry.status === "ok" ? `IDR ${format(entry.analysis?.latest_close)}` : t("idxResearch.unavailable")}</span><span className="text-xs text-muted-foreground">{entry.analysis?.latest_date ?? "—"}</span>{entry.status === "ok" && entryRecency?.status === "warning" && <span className="mt-2 block text-xs font-semibold">{t("idxResearch.recencyWarning", { days: format(entryRecency.warning_after_calendar_days) })}</span>}</button>;
        })}
      </div>
      {item?.status === "unavailable" && <div role="status" className="rounded-xl border p-4 text-sm">
        <p>{t(item.reason === "invalid_data_or_metadata" ? "idxResearch.invalidData" : "idxResearch.noData")}</p>
        {item.reason === "no_data_or_source_failure" && <SourceAttempts value={item.diagnostics?.attempts} />}
        {item.reason === "invalid_data_or_metadata" && <>
          <p className="mt-3 font-medium">{qualityStageKey ? t("idxResearch.qualityStage", { stage: t(qualityStageKey) }) : t("idxResearch.qualityUnknown")}</p>
          <p className="mt-2 text-xs text-muted-foreground">{t("idxResearch.qualityScope")}</p>
        </>}
      </div>}
      {item?.status === "ok" && <section className="min-w-0 rounded-xl border p-4" aria-label={item.symbol}>
        <h2 className="text-lg font-semibold">{item.symbol} · IDR</h2>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          {[[t("idxResearch.analyzedBars"), formatBarCount(item.analysis?.read_identity?.bar_count)], [t("idxResearch.requestedBars"), formatBarCount(result.lookback)]].map(([label, value]) => <div key={label}><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 tabular-nums">{value}</dd></div>)}
        </dl>
        <p className="mt-3 text-xs text-muted-foreground">{t("idxResearch.coverageScope")}</p>
        <dl className="mt-3 min-w-0 text-sm">
          <dt className="text-xs text-muted-foreground">{t("idxResearch.fingerprint")}</dt>
          <dd dir="ltr" className="mt-1 select-text font-mono [overflow-wrap:anywhere]">{fingerprint}</dd>
        </dl>
        <p className="mt-2 text-xs text-muted-foreground">{t("idxResearch.fingerprintScope")}</p>
        <div role="group" aria-label={t("idxResearch.volumeCoverage")} className="mt-4 border-t pt-4 text-sm">
          <h3 className="font-medium">{t("idxResearch.volumeCoverage")}</h3>
          <dl className="mt-3 grid gap-3 sm:grid-cols-4">
            {[[t("idxResearch.volumeBars"), format(volumeCoverage?.bar_count)], [t("idxResearch.volumeAvailable"), format(volumeCoverage?.available_bar_count)], [t("idxResearch.volumeMissing"), format(volumeCoverage?.missing_bar_count)], [t("idxResearch.volumeZero"), format(volumeCoverage?.zero_bar_count)]].map(([label, value]) => <div key={label}><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 tabular-nums">{value}</dd></div>)}
          </dl>
          <p className="mt-3 text-xs text-muted-foreground">{t("idxResearch.volumeCoverageScope")}</p>
        </div>
        <div role="status" className="mt-4 border-y py-3 text-sm">
          <h3 className="font-medium">{t("idxResearch.recencyTitle")}</h3>
          {recency ? <>
            <p className={`mt-1 ${recency.status === "warning" ? "font-semibold" : "text-muted-foreground"}`}>{t(recency.status === "warning" ? "idxResearch.recencyWarning" : "idxResearch.recencyWithin", { days: format(recency.warning_after_calendar_days) })}</p>
            <dl className="mt-3 grid gap-3 sm:grid-cols-3">
              {[[t("idxResearch.recencyAge"), t("idxResearch.recencyDays", { days: format(recency.age_calendar_days) })], [t("idxResearch.recencyLastBar"), recency.last_bar_date], [t("idxResearch.recencyReference"), recency.reference_date]].map(([label, value]) => <div key={label}><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 tabular-nums">{value}</dd></div>)}
            </dl>
            <p className="mt-3 text-xs text-muted-foreground">{t("idxResearch.recencyScope")}</p>
          </> : <p className="mt-1 text-muted-foreground">{t("idxResearch.recencyUnknown")}</p>}
        </div>
        <p className="mt-1 text-xs text-muted-foreground">{t("idxResearch.closeChart")}</p>
        <CloseChart bars={item.bars ?? []} label={`${item.symbol} · ${t("idxResearch.closeChart")} · IDR`} />
        <ObservationTable key={item.symbol} bars={item.bars ?? []} symbol={item.symbol} />
        <dl className="grid grid-cols-2 gap-4 border-t py-4 sm:grid-cols-4">
          {[["RSI 14", indicators?.rsi_14], ["SMA 20", indicators?.sma_20], ["SMA 50", indicators?.sma_50], ["SMA 200", indicators?.sma_200], ["EMA 20", indicators?.ema_20], ["MACD", indicators?.macd?.macd_line], [t("idxResearch.macdSignal"), indicators?.macd?.signal_line], [t("idxResearch.macdHistogram"), indicators?.macd?.histogram], [t("idxResearch.bollingerUpper"), indicators?.bollinger?.upper], [t("idxResearch.bollingerMiddle"), indicators?.bollinger?.middle], [t("idxResearch.bollingerLower"), indicators?.bollinger?.lower], [t("idxResearch.volume"), indicators?.volume?.latest], [t("idxResearch.volumeMean"), indicators?.volume?.sma_20], [t("idxResearch.volumeRatio"), indicators?.volume?.ratio_20]].map(([label, value]) => <div key={String(label)} className="min-w-0 [overflow-wrap:anywhere]"><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 font-medium tabular-nums">{formatIndicator(value as number | null | undefined)}</dd></div>)}
        </dl>
        <p className="text-xs text-muted-foreground">{t("idxResearch.insufficient")}</p>
        <dl className="mt-4 grid gap-3 border-t pt-4 text-sm sm:grid-cols-2">
          {[[t("idxResearch.source"), provenance?.source], [t("idxResearch.adjustment"), provenance?.adjustment], [t("idxResearch.volumeUnit"), provenance?.volume_unit], [t("idxResearch.timezone"), provenance?.exchange_timezone], [t("idxResearch.retrieved"), formatIDXRetrievedAt(provenance?.retrieved_at, i18n.language)], [t("idxResearch.sourceAsOf"), formatIDXSourceAsOf(provenance?.data_as_of)], [t("idxResearch.asOf"), item.analysis?.latest_date]].map(([label, value]) => <div key={label}><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 break-words">{value ?? t("idxResearch.unknown")}</dd></div>)}
        </dl>
        <p className="mt-3 text-xs text-muted-foreground">{t("idxResearch.timeScope")}</p>
        {provenance?.fallback_used === true && <>
          <p className="mt-3 text-xs">{t("idxResearch.fallback")}</p>
          <SourceAttempts value={provenance.attempts} fallback />
        </>}
      </section>}
    </>}
    <footer className="border-t pt-4 text-xs leading-relaxed text-muted-foreground">{t("idxResearch.limits")}</footer>
  </div>;
}
