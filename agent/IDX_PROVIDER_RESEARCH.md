# IDX Phase 2B: provider evidence

Initial research **2026-11-03**, export follow-up **2026-11-04, Asia/Jakarta**.
This is public-document discovery and sample
inspection, not a license grant, provider integration, or authorization to run
backtests. No account was created, provider contacted, subscription purchased or
credential used. Downloads remain in a temporary directory outside the repository;
no exchange data is added to fixtures or installed as runtime reference data.

## Mendeley v5 public registry and code discovery — 2026-11-04

**Registry provenance obtained; market-data provenance remains unresolved.**
This increment follows previously unexamined public metadata and author/institution
code routes. Grounded: current status/backlog and preceding evidence;
`local_loader.py:247–259`, `idx_research_tool.py:151–175` retain normalization and
currency gates. Blast radius: four documents. Invariants: no registry timestamp
promoted to Yahoo retrieval time, invented metadata, notebook execution, account
access or runtime change. Verify: saved-response assertions, source receipts,
UTF-8/local links, session diff/public-file inventory/hashes/index. RTK.md absent.

### Public registry observations

The dataset footer links [API documentation](https://data.mendeley.com/api/docs/)
and [OAI Identify](https://data.mendeley.com/oai?verb=Identify). The former renders
only a loading shell in the web reader. The official
[developer guide](https://dev.mendeley.com/code/datasets_quick_start_guides.html)
requires an OAuth token for its dataset examples; no authenticated API call or
account setup was attempted. OAI is a separate public metadata interface.
Its XML could be read with ordinary PowerShell HTTP after the web reader rejected
the content type. No access-denied response was bypassed.

Using the documented [OAI protocol](https://www.openarchives.org/OAI/openarchivesprotocol.html),
ListMetadataFormats returned `oai_dc`, `oai_datacite` and `datacite`. A bounded
ListIdentifiers query for the issued second returned
`oai:data.mendeley.com/rkpkkd2mhf.5`; this observed identifier, rather than a
guessed identifier, was used in
[GetRecord](https://data.mendeley.com/oai?verb=GetRecord&metadataPrefix=datacite&identifier=oai%3Adata.mendeley.com%2Frkpkkd2mhf.5).
The returned DOI matches v5, with `Issued` and OAI datestamp
**2026-09-30T14:45:31Z**, and the v5 CC BY-NC licence.

DataCite documents [public retrieval without authentication](https://support.datacite.org/docs/rest-api)
and [single-DOI requests](https://support.datacite.org/docs/api-get-doi).
The [v5 DOI response](https://api.datacite.org/dois/10.17632/rkpkkd2mhf.5)
was obtained through ordinary PowerShell HTTP; web-reader access was unavailable.
It records the same issued time, CC BY-NC and the versionless dataset DOI as its
only related identifier. `created`, `registered` and `updated` are all
**2026-09-30T14:45:32Z**; `metadataVersion` is 0. Its abstract repeats the
dataset description, without a file-hash/recipe manifest, full OHLC currency,
Yahoo retrieval time or correction policy.

Following DataCite's [metadata-provenance documentation](https://support.datacite.org/docs/tracking-provenance),
the [DOI activities response](https://api.datacite.org/dois/10.17632/rkpkkd2mhf.5/activities)
contains **one `create` activity**, version 1, at 14:45:32Z; total 1, one page.
These version fields describe DOI metadata, not market-data revisions. Both
registries reflect publisher metadata, not independent price-source validation. The result
does not certify that Yahoo history or dataset files were never corrected.
Neither registry supplies the time at which Yahoo prices were retrieved.

Bounded Crossref follow-up on **2026-11-04 WIB**: the
[article DOI deposit](https://api.crossref.org/works/10.1016/j.dib.2026.113338)
returned HTTP 200 through ordinary PowerShell HTTP after the web reader could
not retrieve it. Its sole `relation` is `is-supplemented-by` the exact Mendeley
v5 URL, `asserted-by: subject`; `update-to`, `updated-by` and `is-update` keys
are absent. This is registry-declared article-to-v5 binding, not file-to-recipe
binding or proof that no correction exists. The two deposited content links
are article text-mining representations, not an additional dataset manifest;
they were not requested. Article licence entries do not establish dataset or
upstream Yahoo entitlement. No OHLC currency/date, transformation or Yahoo
vintage gap is closed. No viable further route emerged from this deposit;
the release-specific publisher/rights input below remains required.

New receipt and decoded response are outside the repo at
`%TEMP%\idx-crossref-evidence-df154f95ef`.
The receipt retains request/completion times, HTTP status, response headers and
SHA-256 of saved UTF-8 decoded text; final redirect URL remains null, and these
times are not Yahoo retrieval times. This follow-up changes only this note;
status/backlog decisions remain unchanged, with no runtime checks or metadata
implementation. Earlier four-document verification totals below remain historical.

### Public code route and decision

The verified article DOI is **10.1016/j.dib.2026.113338**. Searches restricted to
that identity, dataset/notebook identity, author code and institutional records
found no public release manifest. Inspected BINUS AIRDC/BDSRC publication pages
provided no target manifest; this was not a complete archive crawl. A discovered
[coauthor repository](https://github.com/ksnugroho/EmoTweetID) identifies a different
dataset, `10.17632/jzgnjsff9f.3`, so it was excluded. Shared authors are not source
binding. The outside-repo search note records exact scope and the personal-site
502; no unrelated code was run and no outreach was performed.

New evidence is **publisher/registry-declared publication and metadata history**.
Library-derived adjustment/date/volume behavior and inferred all-OHLC IDR retain
their earlier classes; CSV-to-recipe binding, upstream vintage/revision and usage
entitlement remain unknown to this review. No new rights grant was found, and
previously blocked Yahoo terms/help were not requested again without new input.

**No production metadata implementation is justified.** The
[minimum release and rights input](#evidence-classes-and-implementation-decision)
still applies. Exact registry timestamps narrow artifact provenance only. Further
work requires an actual public or authorized manifest/rights record tied to v5,
not another search of the same names or a new Yahoo price vintage. Local Data
Bridge acceptance, DATA-01/02/03, IDX-02 and full RESEARCH-01 stay open; backtest
IDX remains disabled. No loader/helper/cache/tool/CLI or test changed.

QA: `%TEMP%\idx-public-metadata-00af202b71` retains
decoded public XML/JSON, source URL/hash receipts, `registry-findings.json`,
`public-code-findings.md`, baseline/index and verification scripts. Response
files are UTF-8 decoded text, not original transport bytes. HTTP status/headers
and final redirects were not retained and remain null; filesystem save times
are labelled as such, not as Yahoo retrieval times. No old artifacts overwritten.

```powershell
.venv/idx312/Scripts/python.exe -I %TEMP%\idx-public-metadata-00af202b71\inspect_registry.py
.venv/idx312/Scripts/python.exe -I %TEMP%\idx-public-metadata-00af202b71\verify_session.py
git diff --check
```

Saved-response assertions pass for target DOI, matching issued time/licence and
the complete one-page activity result. **266 local links/anchors**, strict UTF-8,
original CSV/README/notebook hashes, identical inventory and `git diff --check`
pass. **3,194 of 3,198 baseline public files remain byte-identical**; only this
note, IDX_PERSONAL_RESEARCH.md, PROJECT_STATUS.md and TODO.md changed. No public
file was added/deleted. Index matches its saved copy, SHA-256
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Existing locale LF→CRLF notices were emitted; those file bytes did not change.
No staging, commit, publish or deployment occurred.
No pytest/Ruff/frontend/build or provider/deployment probe was run: this increment
has no runtime surface.

## Mendeley v5 release comparison and rights follow-up — 2026-11-04

**New public routes examined; production metadata remains held.** This increment
checks release comparison, associated data/correction discovery and licence scope,
rather than repeating the original-file audit or local runtime probes below.
Grounded: project/contributor/security/foundation/reference guidance, prior research,
`local_loader.py:147–166,247–259,398–421,498–511`,
`src/market_data.py:438–468`, `idx_research_tool.py:92–103,151–175`, and existing
`test_idx_local_dates.py:89–99` / research provenance rejection tests.
Blast radius: four documents only. Invariants: no inferred production currency,
changed cache identity, notebook execution, user-state access or acceptance claim.
Verify: UTF-8/local links, session diff, public inventory/hashes and index copy/hash;
no runtime surface. RTK.md remains absent.

### New release evidence and its limits

The [official comparison](https://data.mendeley.com/datasets/compare/rkpkkd2mhf)
opens with version selectors 4 and 5. Its descriptions move from four Excel files
to six CSV files, README and a construction notebook; v4 is dated 8 September,
v5 30 September 2026. It displays CC BY for v4 and CC BY-NC for v5. These are
publisher declarations about packaging, not a file-level transformation log.
README/notebook are newly described; the readable comparison does not establish
their exact addition history. No explanation binds the observed CSV ordering to
the recipe. A workbook-to-CSV conversion is a hypothesis, not verified provenance;
no older workbook was downloaded and the older licence is not applied to v5.

The [article's associated-data section](https://pmc.ncbi.nlm.nih.gov/articles/PMC13694929/#associated-data)
points back to v5 without a separate release manifest in the inspected section.
Its publisher action reaches
[the Elsevier article](https://linkinghub.elsevier.com/retrieve/pii/S235234092600884X),
which the reader could not access (nonretryable). Targeted dataset/recipe searches
for manifest, currency, sort, retrieval and revision, plus article-DOI correction
discovery, found no new binding declaration. This is a bounded negative result,
not proof that a correction or manifest does not exist. No blocked endpoint was
retried through an alternate identity, query variant or account.

### Rights evidence for the intended local use

The full [CC BY-NC 4.0 legal code](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)
was readable. Sections 1(g), 2(a)(1), 4 and 5 distinguish noncommercial copying
and database reuse under rights the licensor controls from warranties of title
or non-infringement, which are disclaimed. The dataset grant therefore remains
relevant to local noncommercial research, but does not itself verify the upstream
rights chain. This is a source review, not a determination that use is prohibited
or that downstream entitlement has been established.

New discovery routes were Yahoo's official
[exchange/provider help](https://help.yahoo.com/kb/SLN2310.html) and
[historical-download help](https://help.yahoo.com/kb/finance-for-web/SLN2311.html).
Search-rendered material flags redistribution restrictions and a subscription
export path; direct full-page opens returned **429**. These are discovery leads,
not reviewed contracts or evidence of a right to use redistributed Mendeley data.
Search surfaced the general and Finance Community terms, warranting one canonical
read of each: both still returned **999**. No cached extract, altered query URL,
different regional contract or subscription was used to resolve that restriction.
The maintainer's personal-research guidance remains distinct from Yahoo permission.
Applicable full upstream terms and their coverage of this downstream local use
remain unresolved; no cloud/LLM/commercial/redistribution grant is inferred.

### Evidence classes and implementation decision

- **Publisher-declared:** v5 packaging/licence, daily trading-date description,
  share volume, close IDR, and the published adjusted-OHLC/local-date recipe.
  These declarations do not authenticate the exact CSV execution path.
- **Library-derived:** the tagged yfinance adjustment algorithm, exchange-local
  daily normalization and missing-volume-to-zero behavior, established in the
  preceding static review. This increment did not rerun that audit.
- **Inferred:** IDR for all OHLC from close IDR and their common unconverted
  projection. Reordering during format conversion remains only a hypothesis.
- **Unknown to this review:** release-to-recipe transformations, captured Yahoo
  currency/timezone response, actual market retrieval vintage and correction
  policy, and applicable upstream-use entitlement. These are not publisher
  declarations of unknown values. Download time/hash are artifact provenance,
  never the Yahoo observation/retrieval timestamp.

**Evidence is insufficient for a production metadata contract on this artifact.**
Existing local normalization emits no authenticated currency declaration; helper
identity/timezone labels do not supply one, and the shared research gate requires
IDR. The module CLI uses the same tool with automatic routing, without a source
switch. No schema, loader/default, helper, cache, research/CLI or tests changed.
Historical 15-series loader/helper and 8+7 CLI results below remain historical.

Minimum input to resume: release-specific publisher evidence identifying the
original CSV/hash or equivalent immutable file identity; recipe version and all
postprocessing (including sorting); explicit currency for O/H/L/C and source-date
semantics; actual upstream retrieval vintage/revision or an explicit publisher
statement that these are unknown; and readable applicable upstream terms or an
authorized rights statement covering local storage/processing of this release.
An honestly unknown vintage can remain unknown in a future bounded contract; do
not invent it or require a fictitious timestamp to pass. Preserve attribution,
licence and uncertainty separately. A new manifest, correction, readable terms
or authorized supplied file is the trigger to resume; repeating old downloads,
the notebook audit or Yahoo price queries would not close these gaps.

Local Data Bridge is still not accepted for research. DATA-01/02/03, IDX-02 and
full RESEARCH-01 stay open; backtest IDX disabled, paper/live separate and Index
Alpha deferred. No pytest/Ruff/frontend/build, provider integration or deployment
was run for these documentation changes.

QA: `%TEMP%\idx-release-evidence-40f850ee1b`.
It retains the new-route findings, baseline status, UTF-8 NUL inventory, public
SHA-256 hashes, index copy and session verification/diff. No original artifacts
or historical QA scripts were overwritten.

```powershell
.venv/idx312/Scripts/python.exe -I %TEMP%\idx-release-evidence-40f850ee1b\verify_session.py
git diff --check
```

Session checks pass: **262 local links/anchors**, strict UTF-8, original
CSV/README/notebook hashes, identical NUL inventory and `git diff --check`.
Of **3,198 baseline public files, 3,194 remain byte-identical**; only
PROJECT_STATUS.md, TODO.md, this note and IDX_PERSONAL_RESEARCH.md changed.
No public file was added/deleted. Index bytes match the saved copy, SHA-256
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Git reports existing LF→CRLF notices for locale files; their bytes remain
unchanged. No staging, commit, publish or deployment occurred.

## Mendeley v5 metadata evidence follow-up — 2026-11-04

**Metadata evidence narrowed; no production metadata or provider acceptance.**
This follow-up resolves several discovery gaps in the earlier audit below. It
uses primary article/construction/library sources, not inferred ticker defaults.
Grounded: status/backlog/contributor/security/reference guidance, prior original
hash, `local_loader.py:207–300,438–511`, `idx_research_tool.py:151–175`, and the
published construction source. Blast radius: four research/status documents.
Invariants: original bytes and runtime rejection remain intact, no invented
currency/source timestamps, no notebook execution, staging or broad task closure.
Verify: static audit, fresh isolated local probes, links/diff/public-file/index.
RTK.md is still absent.

### New source evidence and its scope

The [authors' article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13694929/), Table 2,
declares trading dates and share volume; Fig. 2(c) labels closing prices IDR.
Section 4.2 identifies yfinance 0.2.66/Python 3.13. Its academic-use assertion is
not a downstream entitlement. Dates given for tweets/Stockbit do not establish
market retrieval time. The article licence does not replace the v5 dataset licence.

The normal version-5 public file table exposed the
[construction notebook download](https://data.mendeley.com/public-files/datasets/rkpkkd2mhf/files/1ac69e17-2665-4e00-8aa7-457ad2472b5d/file_downloaded).
Browser Download file succeeded without accounts or access workarounds. Original:
**24,784 bytes**, SHA-256
`11e4abea4ee5fc288cb62fbd652ad7c1209af79c87c027b4d1f6faa5ea18fd0e`.
Local receipt captured after completion at
`2026-11-04T13:19:57.901761+00:00` (20:19:57 WIB). Successful HTTP status,
redirect chain and headers are unavailable from this browser API and remain null.

JSON parsing/source extraction and `ast.parse` only; **no cells were executed**.
All nine code cells have null execution counts and empty saved outputs. Cells
2–3 explicitly describe the market file as `auto_adjust=True`, call
`tk.history(start=START, end=END, auto_adjust=True, actions=False)` for `.JK`
tickers and project that same result's Open/High/Low/Close/Volume. The separate
`auto_adjust=False` request is for P/E inputs, not this market CSV.
`naive_dates` removes timezone preserving local wall dates and normalizes dates;
START is 2022-01-01, exclusive END 2025-01-01. Forward filling occurs later for
the combined output; it is not a step in this market-export recipe.

Tagged [yfinance 0.2.66 adjustment source](https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.66/yfinance/utils.py)
uses the adjusted-close/close ratio on O/H/L and renames adjusted close to close.
This supports a consistent **published adjusted-OHLC recipe**, not an unadjusted
feed or proof of complete corporate actions. With the unconverted projection,
IDR across OHLC is a supported inference from the article's close label, not a
captured response-currency declaration. Keep that distinction in any future mapping.

Tagged [history source](https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.66/yfinance/scrapers/history.py)
normalizes daily exchange-local dates and fills missing volume with zero before
int64 conversion. Thus the **627 CSV zero values** are retained bytes; the
no-imputation statement does not authenticate each as an actual no-trade day.
Dataset calendar filling and upstream null-to-zero handling are different stages.

### Binding limits and disposition

Static comparison finds a concrete reproducibility difference: the published
notebook exports ticker/date order with `%.10g`, while the original CSV is
**date/ticker ordered**. This does not prove price corruption; it means the
notebook is a reconstruction specification rather than a recorded execution that
reproduces these exact bytes. No executed outputs, original Yahoo responses,
currency/timezone metadata, action snapshot, upstream retrieval timestamp or
correction policy bind the recipe to this release. Notebook metadata supplies no
Python/library version beyond the article's declaration. Later Yahoo reruns may
change history; no new Yahoo price calls were made to substitute a new vintage.

The [maintainer guidance](https://ranaroussi.github.io/yfinance/) describes personal
research use and directs users to Yahoo terms; it is not a Yahoo data licence.
The [Yahoo terms cited by the authors](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)
and official Finance terms could not be reviewed through web research (status
999); no access workaround or cached extract was used as a full current contract.
Dataset CC BY-NC and author assertions do not establish independent upstream
redistribution entitlement or cloud/LLM/commercial rights.

**Technical handoff now possible:** document source-declared share volume,
published adjusted-OHLC/date recipe, evidence strength per field, immutable v5
artifact hash and local retrieval receipt. Retain unknown upstream vintage and
inferred OHLC currency explicitly. This is a bounded mapping proposal, not an
invented production JSON schema. Existing `quote_currency`, `volume_unit`,
`exchange_timezone`, `interval` and `adjustment` owners remain the intended seam;
do not populate them from ticker classification or copy local download time into
upstream retrieval provenance. No forced `quote_currency=IDR` was injected to
make this artifact pass the existing research gate.

**Implementation/acceptance remains held** on release-to-recipe provenance,
explicit complete OHLC currency/source semantics and applicable upstream-use
review. Shares and adjustment are no longer wholly missing evidence. Required
next input is a release-specific source manifest/data dictionary or equivalent
publisher evidence that reconciles export ordering/processing and declares the
actual source vintage/unknowns; also review applicable full terms for the intended
local personal use. No account, purchase or provider outreach was attempted.
Calendar/actions/suspension/delisting and broader DATA-01/02/03, IDX-02,
RESEARCH-01 remain open; backtest IDX disabled, paper/live separate, Index Alpha
deferred. No new schema, default metadata, adapter or dependency is installed.

### Fresh verification and artifacts

QA: `%TEMP%\idx-metadata-evidence-e0a3a88dbd`.
Fresh baseline: status and UTF-8 NUL inventory, 3,198 public-file hashes and
index copy/hash. Original CSV hash matches the earlier receipt; all 15 selected
CSV hashes match the original audit. Separate primary-source research is saved
as `primary-findings.md`; only findings are merged here, no notebook data/rows.

Reviewed existing isolated runner/probe was copied to this QA directory. A fresh
run uses allowlisted environment, isolated home/appdata/localappdata/runtime/temp/
cwd and pre-import assertions, disables/stubs dotenv and rejects outside dotenv
reads. Probe socket connect is denied. **15 direct series × 722 bars** pass exact
numeric comparison; real helper JSON returns all 15. CLI **8+7** again returns
**exit 2/unavailable**, every item **currency_declaration**, and
`backtest_enabled: false`. This proves retained rejection, not new source metadata
support. CLI seam remains the previously documented local-only helper/real registry
injection; this is not a clean installed CLI or provider network integration.

```powershell
$qa = '%TEMP%\idx-metadata-evidence-e0a3a88dbd'
.venv/idx312/Scripts/python.exe -I "$qa/static_audit.py"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

No new pytest/Ruff/frontend/build/deployment checks: runtime code/tests are
unchanged. Earlier regression totals are not claimed as fresh runs. The notebook
and source extraction remain outside the repo, with receipt/hash/static audit,
probe outputs/log, baseline/index, session diff and verification.

Final checks: **259 local links/anchors**, UTF-8 and `git diff --check` pass.
Of **3,198 public baseline files, 3,194 remain byte-identical**; only this note,
IDX_PERSONAL_RESEARCH.md, PROJECT_STATUS.md and TODO.md changed. No public file
was added/deleted. Original CSV/README and notebook hashes match their receipts;
the notebook copy matches the browser-saved file. Index before/after remains
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
No staging, commit, publish or deployment occurred.

## Mendeley v5 original-file audit — 2026-11-04

**Original CSV obtained through normal public UI; structural intake passed,
research acceptance remains open.** The version-5
[dataset page](https://data.mendeley.com/datasets/rkpkkd2mhf/5) loaded its file
list in the browser, exposing the
[Stock Market Data.csv download](https://data.mendeley.com/public-files/datasets/rkpkkd2mhf/files/90fecd6b-cd60-4141-88a7-e40fb5633e57/file_downloaded)
and [README download](https://data.mendeley.com/public-files/datasets/rkpkkd2mhf/files/32be9124-b65e-4788-bd00-d7fe35e77f04/file_downloaded).
These are observed public UI links, not guessed internal API routes. Separate
stdlib GETs returned 403. Normal browser Download file controls succeeded without
accounts, credential use, altered TLS, spoofed headers or access-control bypass.
The public API Docs link was readable only as a loading shell in web text view;
no undocumented endpoint was needed. Combined Data.csv and notebooks were not
used or executed. Access succeeded, so the conditional alternative-source search
was not needed.

The page identifies version **5**, publication **30 September 2026**, DOI
`10.17632/rkpkkd2mhf.5`, and **CC BY-NC 4.0**. Its licence panel explicitly
applies attribution/noncommercial terms to associated files and links the
[licence](https://creativecommons.org/licenses/by-nc/4.0/). This is the publisher's
v5 declaration, not an older version's licence or proof of upstream rights.
Citation: Sanjaya, Michael; Setyo Nugroho, Kuncahyo; Martianus Henry, Matthew;
Pardamean, Bens; Intanie Dewi, Vera (2026), dataset title at the linked page,
Mendeley Data, V5, DOI above. No rows are redistributed in this repository.

### Original bytes and transport receipt

Artifacts: `%TEMP%\idx-mendeley-v5-bca783b43b`.
Browser downloads were copied byte-for-byte into `original/`, outside the repo:

- `Stock Market Data.csv`: **920,606 bytes**, SHA-256
  `51c847f70cd310806b90a62dd551779e9ef43480a07714a5189fc884f43aaff6`.
- `README.md`: **4,923 bytes**, SHA-256
  `416b5ce788ccff362a1dfd44d5fc53decb8c7c630e3631a8779ebed0362c7d8e`.

Retrieval completed before **2026-11-04T13:12:52.180004+00:00** (20:12:52 WIB),
the local receipt capture time; exact request/completion timestamps were not
exposed by the browser download API. `download-receipt.json` separates the two
failed direct GETs from successful UI downloads. It records observed download
links, version, paths, sizes and hashes. **Final redirect URL, successful HTTP
status and response headers were not captured**; their fields are null, not an
invented HTTP 200 or a claim that the published link is the final storage URL.
`evidence-notes.md` transcribes the observed v5 licence/file UI; tool snapshots
remain in the chat, not a downloaded page archive. No attempt was made to recover
headers by probing internal endpoints or repeating the blocked request.

### Full-file audit: bytes versus declarations

Stdlib CSV/Decimal audit, without dropping/repairing/imputing any source row:

- Actual schema: `ticker,company_name,date,open,high,low,close,volume`.
- **10,830 rows, 15 tickers, 722 rows each**, **2022-01-03–2024-12-30**.
  Tickers: AUTO, BRMS, BRPT, DSSA, FORU, IMAS, KARW, KONI, MLPT, PANI, PSAB,
  SGER, SRAJ, TOBA, TPIA. BBCA/BBRI are absent. Each ticker has one company name.
- All dates parse as ISO dates; each ticker is ascending and has the same 722
  distinct dates. No duplicate ticker/date pairs, weekend dates, missing fields,
  nonfinite/nonpositive OHLC, OHLC-enclosure violations, or invalid/negative/
  fractional volume were found. This does not prove official-session completeness.
- **627 zero-volume bars** and **462 adjacent identical OHLCV observations** within
  tickers. These are retained observations, not evidence of imputation, holidays,
  suspensions, missing trades or delisting. No null volumes were present.
- README declares dataset times WIB/UTC+7 and dates YYYY-MM-DD; the page/README
  describes daily Yahoo/yfinance market data without imputation. Bytes confirm
  date-only labels, not the authenticity of timezone or absence of upstream
  padding. Tweet `created_at`/session-assignment rules were not applied to OHLCV.
- README warns later dividends/splits can alter historical prices and volumes.
  This is useful adjustment context but does not establish the exact basis of
  every OHLC field in these bytes, library version/options or action snapshot.
  The original market file is not thereby proved to contain unadjusted prices.
- Reviewed v5 page/README do not explicitly declare IDR price currency or shares
  versus lots for volume. Neither field names nor yfinance defaults supply these
  facts. Yahoo derivation is declared; this is not independent vendor confirmation.
  Stock selection used within-period RSI/volume criteria, creating selection bias;
  these 15 stocks are not a point-in-time official universe or membership history.

### Unchanged local loader, JSON and CLI

Grounded: `backtest/loaders/local_loader.py:207–300,381–511`,
`src/market_data.py:438–470`, `src/tools/idx_research_tool.py:151–175` and the
actual bytes. Blast radius: four research/status documents only. Invariants:
no invented metadata, loosened validation, runtime changes or acceptance checks.
Verify: full-file audit, original hashes, isolated probes, links, diff/index.

QA filters each exact ticker into its own derived CSV, preserving all field
strings, original per-ticker order and full history; CSV header/newlines are
reserialized. Each selection has its own SHA-256 in `artifact-audit.json`.
The consolidated file is not mapped to a single symbol: the loader does not
filter `ticker`. Isolated YAML explicitly maps the publisher's IDX context to
`.JK` without changing bare ticker semantics. No metadata declarations are added.

Direct unchanged loader: **15/15 series, 722 bars each**, full 2022–2024 request.
Exact numeric comparison against pandas reading the selected original strings
passes for every OHLCV value and date (dtype-insensitive, no tolerance). The
loader projects OHLCV, casts float64 and uses its existing `trade_date` UTC-naive
index contract. Date-only labels stay unchanged; this is not a verified mapping
of timestamp-bearing source data to Jakarta sessions. Initial QA comparison
failed only because its expected index name was `date`; corrected to existing
`trade_date`, with initial log retained. No application fix was required.

The real helper JSON returns all 15 frames with actual source `local`, no fallback,
`volume_unit: null`, no `quote_currency`, `adjustment: unknown`, and unknown
retrieval/as-of. Its IDX/Asia/Jakarta/1D labels come from existing helper identity
logic, not authenticated artifact metadata. They must not fill source evidence
gaps. In-process CLI probes split the tickers **8+7** to respect the watchlist
limit; all 15 are rejected at **currency_declaration**, both runs exit **2**,
status **unavailable**, `backtest_enabled: false`. Later metadata gates are not
therefore verified. Unlike Aethereal, this file passes acquisition/price checks;
its rejection is metadata-related, not `fetch_failed`.

CLI has no source switch: QA injects `idx_research_tool.fetch_market_data` through
the existing helper with explicit local and a local-only resolver using the real
registry. Actual validation/serialization/exit paths run; this is not a clean
subprocess CLI or production provider integration. Reviewed runner creates an
allowlisted child environment with isolated home/appdata/localappdata/runtime/
temp/cwd, asserts isolation before project imports, disables/stubs dotenv and
denies outside dotenv reads. Socket connect is denied during probes; download
transport is separate. No user config/account state is read or installed.

### Decision and reproducibility

**Earlier disposition (narrowed by metadata evidence follow-up above): insufficient evidence for metadata implementation or provider acceptance.**
Required next inputs: explicit IDR and volume-unit declaration; a reproducible
per-OHLC adjustment contract (or explicit documented unknown and limitations),
market-date semantics tied to this export, source retrieval/revision/correction
policy and intended-use/upstream entitlement review. WIB is now a publisher
declaration, not a wholly absent clue; do not regress to the earlier evidence
state. Noncommercial dataset licensing does not prove commercial, cloud/LLM or
upstream redistribution rights. Calendar/action/suspension/delisting reconciliation
is still absent. Preserve the original and require sourced metadata before using
the existing owners to define a local contract; do not populate production fields
from ticker/library inference. DATA-01/02/03, IDX-02 and RESEARCH-01 remain open;
backtest IDX is disabled, paper/live separate, Index Alpha deferred.

```powershell
$qa = '%TEMP%\idx-mendeley-v5-bca783b43b'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

`audit_csv.py` already ran; it creates selections exclusively and is not an
in-place rerun command. `download_public.py` records the failed direct attempts;
it is not the successful UI route and should not overwrite the combined receipt.
Artifacts include originals, selections, receipt, audit/extra audit, evidence notes,
reviewed isolation runner/probe, initial/final probe logs, JSON/CLI outputs and
baseline/status/inventory/index/final verification. No new pytest, Ruff, full
backend/safety, frontend/build, live provider adapter, deployment or external MCP
checks were run: production code/tests/dependencies are unchanged. These probes
are fresh session evidence; historic test counts above are not reused.
Final verification: **256 local links/anchors**, UTF-8 and `git diff --check`
passed (Git emitted existing locale LF/CRLF notices). **3,194 of 3,198 baseline
public files remain byte-identical**; only PROJECT_STATUS.md, TODO.md,
IDX_PROVIDER_RESEARCH.md and IDX_PERSONAL_RESEARCH.md changed, with no public
file added/deleted. Downloaded copies match the two browser-saved originals.
Index before/after is unchanged:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
No staging, commit, publish or deployment.

## Public local-export search — 2026-11-04

User requested help finding an original permitted OHLCV export before defining
Local Data Bridge metadata. **A downloadable candidate was obtained and tested;
no candidate was accepted for integration.** This follow-up changes documentation
only. It does not install an adapter, invent metadata, or relax validation.

### Downloaded candidate: Aethereal IDX Stock Prices

The [publisher dataset page](https://dataset.aethereal.top/datasets/idx-stock-prices)
offers [CSV](https://dataset.aethereal.top/files/idx-stock-prices.csv) and Parquet
without an account. It declares research/education use, daily IDR prices, share
volume, and a current selection of 120 traded stocks with survivorship bias.
Its dictionary calls `date` the trading day and `adj_close` split/dividend-adjusted.
The [site FAQ](https://dataset.aethereal.top/) distinguishes research datasets
from its enriched CC BY 4.0 datasets; do not transfer the latter licence here.

These are publisher declarations, not proof of upstream redistribution rights.
The reviewed pages do not identify this dataset's upstream vendor or establish
market-date timezone, OHLC adjustment basis, correction policy, regular-board
history, or separate cloud/LLM/redistribution entitlement. Unknowns remain
unknown; do not label this feed independent of Yahoo or stamp Jakarta/raw prices
from an assumption. Download permission is not full provider acceptance.

Actual public GET: **HTTP 200**, CSV content type, **28,730,118 bytes**.
SHA-256: `c97f0554a4a91d57b5c0b9b056ad207487d5384526af5bb3e5279ee2dc1cd95d`.
Request-start receipt: `2026-11-04T08:23:30.054855+00:00` (15:23 WIB).
The server Last-Modified header is recorded separately, not treated as market
observation time or as proof of freshness. The URL is mutable; these findings
apply to these bytes, not every future download.

Stdlib CSV/Decimal audit of the entire file, without correction or imputation:

- Header: `date,ticker,open,high,low,close,adj_close,volume`.
- **518,044 rows, 114 distinct tickers**, dates **2000-06-06–2026-11-03**.
  The observed ticker count differs from the publisher's 120; cause unverified.
- No duplicate ticker/date pairs, malformed ISO dates, nonfinite/missing prices,
  nonpositive prices, or invalid/fractional/negative volumes were found by this
  audit. There are **38,826 zero-volume rows**; no closure/suspension inference.
- **308 rows across 71 tickers violate strict OHLC enclosure**. The smallest
  observed enclosure gap is 0.2439 and largest 1984.4788 in the file's price units;
  all exceed 0.01. Do not dismiss these as machine-epsilon noise or round them
  away. Cause, price accuracy, calendar completeness and actions remain unverified.

The consolidated file must not be mapped directly to one local symbol: the
existing loader does not filter its `ticker` column. QA selected exact BBCA and
BBRI rows into separate files, retaining every original field string and row
order, with no date trimming, price/volume repair or missing-row filling.
This is an explicitly derived selection, not an original single-symbol export.
Bare tickers retain their existing application meaning; the synthetic isolated
configuration explicitly assigns these publisher-identified IDX shares `.JK`.

BBCA selection: **5,522 rows**, 2004-06-08–2026-11-03, SHA-256
`fd253d5da0fa434b72a09e407162db5ba13cc021771e4b3a4f1d02c0898dfefc`.
BBRI: **5,673 rows**, 2003-11-10–2026-11-03, SHA-256
`d27d71d95cf77567c39a6d23c1af89bcd5981751bae4c5a7451db5156ad952d4`.

### Existing-loader and CLI evidence

The direct local-loader request for 2026-10-01–2026-11-03 raises
`5 bar(s) violate OHLC invariants` for BBCA and
`8 bar(s) violate OHLC invariants` for BBRI. The existing normalizer validates
the complete source before filtering (`backtest/loaders/local_loader.py:286,506`),
so narrowing the request does not hide older defective rows. No guard was weakened,
and `adj_close` was not substituted for `close` while keeping a different OHLC basis.

JSON through the real registry/local helper records `fetch_failed` for each.
The existing research CLI emits exit **2**, status **unavailable**,
`backtest_enabled: false`, and the same diagnostics. It does not reach the
currency metadata gate for these rejected series. CLI has no source option:
QA injects `idx_research_tool.fetch_market_data` to the existing helper with
explicit local and a local-only resolver, then uses the real registry.
This is an in-process artifact probe, not a clean subprocess CLI, a new provider
adapter, or verification of Yahoo transport/production integration.

All imports/probes use the project interpreter in an allowlisted child environment
with isolated home/appdata/localappdata/runtime/temp/cwd, assertions before project
imports, dotenv disabled/stubbed, and an audit hook denying external dotenv reads.
The artifact probe denies socket connect; only the separate public download script
accesses the publisher. No user settings, account state, credentials or cache are
read, and no real Data Bridge config is written.

### Academic secondary candidate (earlier session; follow-up above)

[Mendeley version 5](https://data.mendeley.com/datasets/rkpkkd2mhf/5), DOI
`10.17632/rkpkkd2mhf.5`, declares **CC BY-NC 4.0** and Yahoo/yfinance-derived
market data for 15 selected shares in 2022–2024. The description distinguishes
**10,830 raw market rows without imputation** from **5,565 forward-filled rows**
in the combined dataset. Target `Stock Market Data.csv`, not `Combined Data.csv`.
It is not independent Yahoo confirmation or an official universe.
The [version comparison](https://data.mendeley.com/datasets/compare/rkpkkd2mhf)
shows a licence change; do not borrow an older version's CC BY licence for v5.

Publisher metadata was readable through web research, but file links were not
exposed in its text view and a direct public-page request returned HTTP 403.
No bypass was attempted. At that earlier check, actual CSV bytes/hash/quality were **not verified**;
timezone and OHLC adjustment remain unverified. A research dataset licence does
not itself authenticate upstream rights. No notebook was executed or account used.

### Disposition and reproduction

Grounded: current status/backlog, foundation/provider/reference handoff,
contributor/security guidance, loader normalizer/readers/cache, research metadata
gates, and the downloaded bytes. Blast radius: provider research and linked status
only. Invariants: no inferred currency/timezone/adjustment, no fabricated bars,
no production schema/adapter from this candidate, no acceptance checkbox closed.

The verified progress is an actual external CSV and a reproducible failed intake,
not an accepted Local Data Bridge provider. Metadata implementation still requires
documented timezone/date semantics, consistent OHLC adjustment, upstream identity
and applicable usage scope, plus a source revision/correction for the failed rows.
Do not silently drop the failures to create an apparently accepted fixture.
The existing [minimum handoff](#minimum-technical-handoff) remains the intake gate.
DATA-01/02/03, IDX-02 and RESEARCH-01 full acceptance remain open; IDX backtests
stay disabled, paper/live are separate, and Index Alpha remains deferred.

QA: `%TEMP%\idx-local-input-research-rdl8yvgr`.
The original CSV and derived selections remain outside the repository. Artifacts:
`download_public.py`, `download-receipt.json`, `audit_csv.py`,
`artifact-audit.json`, `ohlc-gaps.json`, reviewed `run_tests.py`, `probe_cli.py`,
JSON/CLI outputs, logs, academic findings, baseline hashes/status/inventory/index
copy, and final verification. Public source notebooks/content were not executed.

```powershell
$qa = '%TEMP%\idx-local-input-research-rdl8yvgr'
# download_public.py already ran; it uses exclusive creation to retain the original.
.venv/idx312/Scripts/python.exe -I "$qa/audit_csv.py"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

No production Python/frontend code or dependency changed. No new unit tests,
full backend/safety suite, Ruff/Black, frontend/build, Parquet decoder, external
MCP, Electron or deployment checks were run for this research-only change.
The loader/JSON/CLI probe above is the actual runtime evidence; prior test counts
are not inherited as results for this session. No staging/commit/publish occurred.
Final checks: **253 local links/anchors**, UTF-8 and `git diff --check` passed.
Of **3,198 baseline public files, 3,194 remain byte-identical**; only this note,
IDX_PERSONAL_RESEARCH.md, PROJECT_STATUS.md and TODO.md changed. No files were
added to or removed from the public inventory, and all production/test code is
unchanged. Index SHA-256 before/after:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.

## Public delivery and product evidence

[IDX Data Services](https://www.idx.id/en/products/idx-data-services/) lists direct
and redistributor EoD products, Data Reference, and separate display/non-display
uses. Data Reference includes financial statements, corporate actions and
disclosures. Listed local redistributors include Antara, IQ Plus, RTI Infokom and
IDX Solusi Teknologi Informasi. Listing verifies an access route, not which vendor
offers a suitable historical API or which rights a prospective subscriber receives.
The page announces catalogue and terms changes effective **1 January 2027**.

The ordinary public HTML exposes download links omitted by the browser text
extractor. Public samples were retrieved using those links, without undocumented
APIs or access-control workarounds:

- [Equity EoD sample ZIP](https://www.idx.id/media/8422/idx-equity-eod.zip):
  29,934,637 bytes; SHA-256
  `893cdd353947970cceb8a880fc48d626a84a101bd6bec5e754ea8706d92aa01b`.
  Archive entries include quotation, board, transaction, first-transaction and
  index files. Inspected `Stock Quotation/SQ200217.TXT` is dated 17 February 2020.
- [Equity EoD Professional sample ZIP](https://www.idx.id/media/9655/idx-equity-eod-professional.zip):
  1,296,593 bytes; SHA-256
  `a5685900149adc0365a61ce532646423c37c4be335354081b4864fa60ab8b16b`.
  Contains main/development-board quotation files with January-February 2021
  filenames. Inspected `List of Securities Quotation Main Board/MB210104.txt`
  explicitly dates itself 4 January 2021. Its header includes code/name,
  previous/high/low/close/change, volume/value/frequency, index and bid/offer;
  it has no opening-price field. These observations concern these sample files,
  not a contractual current schema or historical-coverage guarantee.

Samples do not establish volume units, adjustment policy, timestamp semantics,
point-in-time corporate actions, missing/suspended/delisted instruments, revision
policy or current board coverage. Do not infer those facts from column names or
derive an opening price from previous close. No sample is a current universe.

## Contract evidence and date boundaries

[BEI notice S-07014/BEI.LDT/11-2020, 27 November 2020](https://www.idxdata3.co.id/Pengumuman/SIGNED_1410257_1927-S-07014-BEI.LDT-11-2020-%2827-11-20%29---Pelanggan-Data-BEI---Peralihan-Media-Distribusi-IDX-Equity-EoD.pdf)
states that legacy public EoD distribution ended on 4 January 2021 and obtaining
that product requires an agreement and subscription. Historical public URLs are
not evidence of permission to continue downloading a feed.

[General Terms v0.3, last modified 1 January 2024](https://www.idx.id/media/vaupc3md/20240215_final-general-term-of-use-version-0-3-2024-efektif-1-january-2024-2.pdf)
is the terms document linked in the ordinary license section on the check date:

- Article 1.1 prioritizes the application and amendments, then the license
  agreement, then effective general terms. Public terms alone cannot prove rights.
- Articles 2.1.2-2.1.3 distinguish internal non-display analysis from public display
  and distinguish group from non-group access. Article 3.1.2(a)(1)(c)(ii) identifies
  algorithmic trading as category 1 and investment/portfolio/risk/quantitative
  analysis as category 2. This suggests questions for this project's license
  scope; it does not classify or authorize the intended deployment.
- Article 3.1.1(a)(2) says technical specifications and registration procedures are
  supplied on request. Article 3.1.1(e)(10) requires a display license to become a
  redistributor. Article 9.7(c) requires prior written consent for historical
  database use after termination.

The official page also links the
[2026 catalogue](https://www.idx.id/media/rzfl4wzy/20260513_idx-data-services-catalogue-pricelist-non-ab-2026.pdf).
The linked PDF was retrieved (21,028,838 bytes, 42 pages; SHA-256
`57fb27132030e4383555eeb9a947b701beeb8365f46edd8d209bb4ef1b94401b`).
The web extractor again rejected its size. Follow-up used the existing
`pypdfium2` package for bounded, page-by-page text extraction and PNG rendering;
the SHA-256 matches the earlier download. This avoids the previous stalled
whole-document extraction without changing access methods. Relevant complete
pages were read, and rendered pages checked for table alignment, labels and
footnotes. Page references below give **PDF page / printed page**, both one-based:

- **7/5 and 18/16:** direct and indirect EoD Professional descriptions omit opening
  price; Basic also omits high/low. These products cannot be presumed sufficient
  for OHLCV backtests. The catalogue corroborates the sample limitation, without
  establishing a production schema.
- **25/23:** Data Reference includes filings, actions and suspension/unsuspension
  reports. Product scope does not establish point-in-time history or revision
  semantics.
- **27/25:** non-display category 2 covers investment/portfolio/risk/quantitative
  analysis; its distribution column has a cross. The delayed/EoD redistributor
  fee footnote does not grant free data access or override subscription rights.
- **34/32 and 36/34:** subscription involves an agreement and connection
  coordination; direct licensees require an NSP leased line. Public catalogue
  access does not provide a public production API.

These are observations from the [official catalogue](https://www.idx.id/media/rzfl4wzy/20260513_idx-data-services-catalogue-pricelist-non-ab-2026.pdf),
not entitlement or a quote. No applicable total cost, signed terms, historical
coverage, units, adjustments or LLM/cloud rights have been established.

Future documents are separately linked:
[2027 catalogue](https://www.idx.id/media/zmopzq1r/idx-data-services-catalogue-pricelist-2027_compressed.pdf)
and [terms effective 1 January 2027](https://www.idx.id/media/0j2ap3ru/idx-data-general-terms-of-use-1-januari-2027.pdf).
These links were discovered; their contents were not reviewed. Do not apply future
terms to a 2026 run or assume the 2024 document governs an eventual subscription
without checking its signed documents and later amendments.

## Inputs still required before acceptance

Obtain the provider's current technical specification and an authorized sample
with daily OHLCV units/adjustments and historical coverage; instrument/board/listing
history; corporate-action announcement, ex, record and payment dates and revision
semantics. Reconcile these to the importer and the chosen backtest interval.

Obtain written entitlement covering the intended personal or organization use,
local storage/caching and retention, server/cloud processing, transmission to LLM
services, internal calculation, UI/report display, derived outputs and any
redistribution. Public product listings do not resolve these rights. There is no
licensed provider in this workspace, no verified production API contract, and no
evidence supporting provider acceptance or enabling IDX backtests.

## Minimum technical handoff

For a provider evaluation to resume, first identify the intended date range,
regular-share/board universe and deployment (local research, server/cloud,
LLM processing, display or redistribution). Then obtain from an authorized source:

- A versioned production specification/data dictionary and permitted delivery
  method (file export is sufficient to start; an API is not mandatory), with
  field types, instrument identifiers, board/session coverage, timestamps,
  IDR price/turnover units, share-versus-lot volume, null/status semantics,
  adjustments, corrections and available history. An API additionally needs
  documented authentication, pagination and rate limits; credentials stay private.
- A sample permitted for local validation, with actual opening/high/low/close/volume
  fields for the proposed daily OHLCV path. Require an explicit explanation for
  absent opening prices; previous close or first transaction is not an accepted
  substitute. The catalogue and old samples do not prove a current product can
  supply these fields. If it cannot, record the narrower supported use and keep
  OHLCV/backtest acceptance open.
- For historical acceptance, dated listing/board changes, suspensions/resumptions
  and corporate actions with announcement/publication and effective dates,
  revision/availability semantics and coverage gaps. The sample and coverage
  statement must allow reconciliation of normal, missing, suspended, action and
  delisted cases; no event values are invented when absent.
- Written entitlement for the selected use and delivery, including the storage,
  retention and processing/display scopes listed above, applicable documents and
  effective dates. Unknown rights remain unresolved; catalogue access is not a grant.

These inputs start evaluation; they do not select a provider or enable an engine.
An authorized representative can supply documents/export files without granting
account access. No purchase, provider outreach or account authorization is needed
for the local preparation completed here. Reference import intake is documented
in [the reference handoff](IDX_REFERENCE.md#phase-2b-disposition-and-minimum-handoff).

Verification: official page and linked sample downloads succeeded in the earlier
research sessions; sample archive
entries and selected text headers were inspected without executing contents.
`data.idx.co.id` FAQ/catalogue direct reads returned HTTP 403; cached search
extracts and older catalogues were not used as current contract evidence.

## New Index Alpha documentation evidence

Checked **2026-11-03, Asia/Jakarta**. Public documentation now provides a concrete
evaluation route; this is new technical evidence, not an accepted provider.

- The [endpoint reference](https://indexalpha.id/id/docs/endpoints) documents daily
  `GET /stocks/ohlcv`, alongside broker/foreign-flow endpoints. It distinguishes
  unadjusted `idx` prices from Yahoo-derived `yfinance` prices, with optional
  dividend adjustment on the latter. Missing dates are omitted. These are provider
  descriptions and response examples; no actual market response was retrieved.
- The public [Swagger page](https://api.indexalpha.id/docs) explicitly links its
  [OpenAPI schema](https://api.indexalpha.id/openapi.json), retrieved without
  authentication. Version `0.1.0` declares HTTP Bearer authentication for OHLCV,
  required date/OHLCV fields and integer price/volume types. Reconcile those types
  with adjusted-price precision before implementation. Its enumerated paths do
  not include an instrument-master, calendar or corporate-action endpoint; this
  observation is limited to this published schema. It has no `info.license` field.
- [Authentication](https://indexalpha.id/id/docs/authentication) supplies the base
  URL and Bearer-token convention. The [quick start](https://indexalpha.id/id/docs/quickstart)
  requires Google sign-in to provision an account/key. The
  [pricing page](https://indexalpha.id/id/pricing) advertises a Free plan with five
  daily requests; payment is therefore not a prerequisite to the advertised trial.
  No account, OAuth authorization, token, trial call or purchase was performed.

This permits specification review and planning an authorized probe. It does not
supply the dated instrument export required for reference import. The reviewed
pages/schema do not establish this project's storage, cloud/LLM, display or
redistribution entitlement, OHLCV units/timezone/board coverage, revision policy,
historical actions or completeness. Broker-summary units must not be transferred
to OHLCV by assumption. Obtain applicable terms and an authorized sample before
adapter acceptance; keep RULE-01, DATA-01 and RESEARCH-01 open and IDX execution
disabled. No code or runtime surface changed in this research increment.

## User-operated Playground response observation

Observed **2026-11-03, Asia/Jakarta**, after the user signed in and submitted
requests in the [Playground](https://indexalpha.id/playground). The earlier
documentation-only observations above precede this account-access evidence.
The agent did not reveal/copy the token or submit another request.

The first visible response was broker-summary JSON: `success: true`, `error: null`,
90 records with 90 distinct broker codes. It was not the intended OHLCV probe.
The subsequent visible response was OHLCV JSON: `success: true`, `error: null`,
20 records with `date`, `open`, `high`, `low`, `close`, and `volume`.
At inspection the form showed ticker `BBCA`, requested interval 2026-01-01 through
2026-01-31, source `IDX (as-traded)` and dividend adjustment `No`. Returned dates
were unique and ascending, spanning 2026-01-02 through 2026-01-30, inside that
interval. All OHLCV numbers were finite, volumes nonnegative, and each bar's
high/low enclosed open/close. The form interval differs from the October window
prepared earlier; do not report this as an October probe. The response itself
does not echo ticker, source or requested interval; those are observed form state,
not independently captured HTTP request provenance. No HTTP status/headers were
captured. Raw rows and credentials are not copied into the repository.

This verifies a user-operated response at the provider UI, not application-loader
integration, completeness against an official calendar, independent price accuracy,
currency/volume units, timezone or usage entitlement. An account and successful
response do not resolve storage/cloud/LLM/display/redistribution rights. Obtain
those terms and a permitted original artifact before accepting an adapter or
reference import. RULE-01, DATA-01 and RESEARCH-01 remain open; backtests stay
disabled. This increment changes documentation only; tests/Ruff were not rerun.

## EODHD free-plan probe and Yahoo comparison — 2026-11-13

**Why this candidate.** A search for providers not yet evaluated found EODHD
(eodhd.com) listing the Jakarta exchange as `JK` (MIC XIDX) with
[924 active IDR tickers](https://eodhd.com/exchange/JK). Twelve Data also lists
XIDX instruments, but its [pricing page](https://twelvedata.com/pricing) does not
say whether IDX is in the free plan or how deep daily history goes, so it stays a
fallback candidate. Two open-source IDX sources were rejected without use:
[NeaByteLab IDX-API](https://gh.hhj520.top/NeaByteLab/IDX-API) reads the exchange
website, which the BEI site terms forbid scraping, and
[saham-mcp](https://glama.ai/mcp/servers/baguskto/saham-mcp) relies on a GitHub
dataset with no stated licence.

**Published terms read (not a signed agreement).**

- [Pricing](https://eodhd.com/pricing): personal plans. The free Sandbox has 1 year
  of history and 20 calls per day. Historian costs $19.99 per month and gives
  "30+ yrs" of end-of-day data with 100,000 calls per day. Commercial plans are
  separate and were not read.
- [Historical EOD API](https://eodhd.com/financial-apis/api-for-historical-data-and-volumes):
  - `/api/eod/{SYMBOL}` returns date, open, high, low, close, adjusted_close and
    volume.
  - OHLC is unadjusted, "as they printed on the tape that day".
  - Volume is in shares and split-adjusted only.
  - `adjusted_close` covers splits and dividends and is recomputed, so past values
    change when new dividends arrive.
  - Delisted tickers keep their history. Non-US history depth varies by market,
    and no JK start date is stated.
- [Terms](https://eodhd.com/financial-apis/terms-conditions): non-professional
  users may "store, manipulate, and analyze the data for private, non-commercial
  purposes". Redistribution and "displaying" are prohibited. The data "is not
  necessarily real-time nor accurate", and EODHD gives no warranties. Use with LLM
  services and caching are not addressed.

**Probe.** The user created a free account and saved the token in the gitignored
`agent/.env` as `EODHD_API_KEY`. The token was read from that file by a scratch
script and never printed or committed. One request per symbol, with
`from=2025-11-01`, returned HTTP 200 `application/json`. The free plan clipped
the history to one year. The JSON files stay outside the repository, which the
terms allow for private use.

| Symbol | Bytes | Rows | First | Last | SHA-256 |
|---|---|---|---|---|---|
| BBCA.JK | 27,547 | 240 | 2025-11-13 | 2026-11-13 | `6354320873f10468e90be28af60913cb3fbceb419ba4a67024a97dbab255de49` |
| BBRI.JK | 27,196 | 240 | 2025-11-13 | 2026-11-13 | `6fdd118113c481b994f382b27efcf2e7842a07ff9780137a30f5186ae5ce155e` |

**Comparison with Yahoo.** yfinance 1.5.2 `history(auto_adjust=False)` over the
same dates. Yahoo timestamps were converted to Asia/Jakarta session dates.

| Check | BBCA.JK | BBRI.JK |
|---|---|---|
| Session dates | 240 = 240, identical sets | 240 = 240, identical sets |
| High, low, close | identical on all 240 | identical on all 240 |
| Open | identical except 2026-09-02 (EODHD 6,675, Yahoo 6,650) | identical on all 240 |
| Volume equal | 24 of 240 | 222 of 240 |
| Volume difference | median 5 shares, 90th percentile 19, max 7,601,998 (2026-09-02) | max 60,323,500 (2026-10-16, EODHD lower) |
| Volumes divisible by 100 | EODHD 27 of 240, Yahoo 240 of 240 | both 240 of 240 |
| Zero-volume bars | none in either | none in either |
| `adjusted_close`/close | 0.9451–1.0000 | 0.9052–1.0000 |

Yahoo reported dividends on the same window (BBCA: 55, 281, 20 and 25 IDR; BBRI:
137 and 209 IDR), consistent with EODHD's falling adjustment ratio. Splits were
not observed in this window, so split handling is untested.

**What this shows.** On this window two vendors agree on session dates and on
almost every price. EODHD's BBCA volumes are mostly not round lots while Yahoo's
always are, which suggests a different aggregation such as odd lots or another
market segment. Nothing read establishes the cause. Where the two disagree, for
example BBCA on 2026-09-02, neither can be called correct without an official BEI
figure. Agreement between two vendors is not independent proof, because they may
share an upstream source.

**Disposition.** EODHD is a usable second source for cross-checking Yahoo in
personal research, and the paid personal plan could extend history. It does not
satisfy DATA-01: there is no accuracy warranty, the volume definition is
unexplained, JK history depth is unknown, LLM use is not addressed, and display
is prohibited. No adapter, loader, fallback-chain entry or env-schema key was
added. DATA-01 stays open, and IDX backtests stay refused.

### EODHD volume gap analysis — 2026-11-13

**Inputs.** The two saved EODHD files above, with the same SHA-256 hashes, and a
fresh yfinance 1.5.2 fetch of the same window: `history(auto_adjust=False)` daily
and `interval="60m"`, saved as CSV outside the repository. The daily Yahoo CSVs
hash to `61115fc928f14b5952e55119111fb94d206a79a9e7785a561154fb7b742dd1cf` (BBCA)
and `d032d05c1877e43f1b20ba93f2883b52edf461d001544203ca82c602078e9f55` (BBRI).
No new EODHD request was made. The scratch scripts sit in the session
scratchpad under `%TEMP%`.

**Small gaps are lot rounding, not added odd lots.**

- On BBCA, 223 of the 240 day gaps are under 100 shares, from −62 to +44. Their
  signs are balanced: EODHD is higher on 102 days, lower on 97, and equal on 24.
  If EODHD added odd lots, it would always be the higher figure.
- Yahoo equals EODHD rounded to the nearest 100 shares on 222 of 240 BBCA days.
  It equals EODHD rounded down on only 126.
- On BBRI, EODHD volume is always a multiple of 100, and 222 of 240 days match
  Yahoo exactly.

So EODHD carries a share-level figure for BBCA but lot multiples for BBRI, and
Yahoo publishes lot-rounded figures. Why the BBCA figure is not a lot multiple
(odd-lot trades or something else) is still unproven, but it does not explain
the difference between the two vendors.

**Large gaps fall on the same dates in both stocks.**

- A gap of at least 10,000 shares occurred on 11 BBCA dates and 13 BBRI dates.
  Ten dates are shared: 2026-02-23, 03-11, 04-07, 05-07, 05-29, 06-11, 07-08,
  07-17, 09-02 and 10-05.
- On every shared date EODHD is higher, by 0.01% to 7.5%. The largest gaps are
  on 2026-09-02: +7.53% for BBCA and +3.99% for BBRI.
- The one large gap in the other direction is BBRI on 2026-10-16, where EODHD is
  4.81% (60.3 million shares) lower. It is a BBRI-only date.
- The gaps are not explained by a shift of one day: on the five largest BBCA
  gaps, Yahoo's figures for the neighbouring days do not match EODHD.

A shared date set points to a difference in what each vendor captured for those
trading days, such as a late or corrected print, or trades from another market
segment, rather than a per-stock rule. The data cannot tell which vendor is
right. BBCA's 2026-09-02 open (EODHD 6,675, Yahoo 6,650) differs on the day with
the largest gap.

**Yahoo intraday bars do not reconcile either daily total.** On all 240 days for
both stocks, the sum of Yahoo 60m volumes equals neither vendor's daily volume.
On the gap dates the sum is 49–93% of the daily figure. Both daily totals
therefore include volume outside the hourly bars, for example the closing
auction or non-regular segments, so intraday data cannot settle the gap.

**Disposition.** The volume definition is still unexplained, and an official
figure is needed. The narrowest next input is a BEI publication giving
per-stock volume, split by market, for one shared gap date (2026-09-02) and the
reversed date (2026-10-16). The IDX Daily Statistics PDF downloaded normally on
2026-11-05, but whether it lists BBCA and BBRI volume by market has not been
checked, and fetching it needs the user's approval. Until then, research use
should treat volume from either vendor as approximate to within the observed
gaps (up to 7.5% on the dates seen) and should not mix the two sources in one
series. DATA-01 stays open. No code, loader or fallback entry changed, and IDX
backtests stay refused.

### Official BEI check of the volume gap — 2026-11-13

**Files.** With the user's approval, two IDX Daily Statistics PDFs were taken
from the links on the
[official Statistics page](https://www.idx.id/en/market-data/statistical-reports/statistics).
A plain `curl` GET returned HTTP 403 with an HTML body, which was deleted and
not retried with altered headers. The same links returned HTTP 200
`application/pdf` in the normal browser, and the browser saved the files. Both
are publication v.2.2.0, 9 pages, and stay outside the repository.

| Trading day | Link | Bytes | Last-Modified | SHA-256 |
|---|---|---|---|---|
| 2026-09-02 | [ds_260902.pdf](https://www.idx.co.id/Media/3dkhm2hn/ds_260902.pdf) | 1,985,442 | 2026-09-02 10:29:15 GMT | `349147b189cb3cb87735d30be8359a52066851b2898b108493bf12dddd554a6e` |
| 2026-10-16 | [ds_261016.pdf](https://www.idx.co.id/Media/bndpqsus/ds_261016.pdf) | 1,971,217 | 2026-10-16 11:19:17 GMT | `08e80f11ec5fb466e6a34e430f9cc7bc60f756efe458c0dae1bf6d9b9d4c3608` |

**What the publication gives.** Page 3 ranks the top ten stocks by volume
(million shares), value (billion IDR) and frequency. The footnote on page 1 says
volume, value and frequency are "total trading in regular, cash, and negotiate
markets". These figures are therefore all-market totals, rounded to 1 million
shares or 1 billion IDR. There is no regular-market split per stock. The
[Stock Summary page](https://www.idx.id/en/market-data/trading-summary/stock-summary)
still renders only its tabs, with no table, in the browser.

**16 October 2026** (both stocks are in the top-ten volume table):

| Stock | BEI all-market | EODHD | Yahoo |
|---|---|---|---|
| BBCA | 1,258 M | 1,241.098 M (−16.9 M) | 1,241.098 M (−16.9 M) |
| BBRI | 1,217 M | 1,193.916 M (−23.1 M) | 1,254.240 M (**+37.2 M**) |

- On BBCA the two vendors agree with each other, but both are 1.3% below the
  official all-market total. A vendor daily volume is therefore not the BEI
  all-market total. A regular-market-only figure would fit this, but nothing
  read establishes it.
- Yahoo's BBRI volume is 37.2 million shares (3.1%) above the official total
  for all markets combined. No market segment can explain that, so Yahoo
  over-counted BBRI on this day. EODHD sits below the total, as both vendors do
  for BBCA.

**2 September 2026** (neither stock is in the top-ten volume table, so only
value can be checked). BBCA's official value is IDR 723 billion and BBRI's is
726 billion. With EODHD's volume, these values imply average prices of 6,661
(BBCA) and 3,403 (BBRI), at or inside the day's high-low range. With Yahoo's
volume they imply 7,163 and 3,538, which is 6.5% and 4.1% above the day's high.
Because the official value also includes negotiated trades, which can be priced
outside the regular range, this does not prove Yahoo wrong. It does favour
EODHD.

**Disposition.**

- On the two dates checked, EODHD is consistent with BEI publications, and
  Yahoo is shown to be wrong once (BBRI, 16 October).
- Neither vendor's daily volume is the BEI all-market total. What it measures
  (probably the regular market) still needs a BEI regular-market figure per
  stock.
- Two dates do not make EODHD verified. Yahoo volume should not be treated as
  exact, and the two vendors should not be mixed in one series.
- DATA-01 stays open. No code, loader or fallback entry changed, and IDX
  backtests stay refused.

### Monthly regular-market reconciliation against BEI — 2026-11-13

**Source.** BEI's Digital Statistic report
[Table of Stock Trading](https://www.idx.id/en/market-data/statistical-reports/digital-statistic/monthly/trading-summary/table-of-stock-trading)
gives each stock's monthly **Regular Market** and **Total Market** volume (in
thousands of shares, one decimal), value and frequency. The page loads ten rows
at a time from its own endpoint, `/primary/DigitalStatistic/GetApiDataPaginated`
with `urlName=LINK_TABLE_STOCK_TRADING`, which accepts a `search` parameter.
Four single lookups were made through that endpoint from the open page: BBCA and
BBRI for September and October 2026. All returned HTTP 200 JSON. This is the
request the page itself makes, not a crawl, and nothing was saved to a file. The
BEI site terms prohibit scraping and crawling, so this route should stay limited
to occasional single lookups.

| Stock, month | BEI regular | BEI total | EODHD sum (22 days) | Yahoo sum (22 days) |
|---|---|---|---|---|
| BBCA 2026-09 | 2,716,745,900 | 3,443,015,261 | 2,716,745,929 (+29) | 2,709,138,100 (−7,607,800) |
| BBRI 2026-09 | 4,009,458,000 | 4,255,057,128 | 4,009,458,000 (0) | 4,001,254,900 (−8,203,100) |
| BBCA 2026-10 | 7,220,911,100 | 7,950,214,655 | 7,220,911,237 (+137) | 7,220,900,900 (−10,200) |
| BBRI 2026-10 | 7,613,796,900 | 7,877,248,628 | 7,613,796,900 (0) | 7,674,104,600 (+60,307,700) |

BEI and both vendors count 22 trading days in each month.

**Findings.**

- **Vendor daily volume is regular-market volume.** Summed over a month, EODHD
  equals BEI's regular-market volume exactly for BBRI. For BBCA it is within
  29 and 137 shares, which is BEI's rounding to hundreds of shares. Both
  vendors fall 3–21% below BEI's total-market volume, which also counts
  negotiated and cash-market trades. This settles the open question from the
  official check above.
- **Yahoo's large gaps are Yahoo errors.** Yahoo's monthly shortfalls and
  excess match its daily gaps to EODHD on the same dates:
  - BBCA September: −7,607,800 against −7,601,998 on 2026-09-02.
  - BBRI September: −8,203,100, mainly −8,193,900 on 2026-09-02.
  - BBRI October: +60,307,700 against +60,323,500 on 2026-10-16.

  BEI's monthly figure agrees with EODHD in all three cases. The small BBCA
  gaps are Yahoo's rounding to whole lots, as found earlier.
- **Scope.** This covers 2 stocks and 2 months (88 of the 480 stock-days
  compared). EODHD matched BEI on every stock-month checked; that is
  evidence, not a warranty over all symbols and dates.

**Disposition.** For daily IDX volume, EODHD reproduces BEI regular-market
totals on every stock-month checked, and Yahoo does not. In personal research,
EODHD can serve as the volume reference and Yahoo as a fallback, with Yahoo's
lot rounding and occasional missed or doubled days stated. The volume part of
DATA-01 is answered for these samples. DATA-01 as a whole stays open, because
these items are still unresolved:

- EODHD's accuracy disclaimer and its display and redistribution limits;
- unknown JK history depth;
- untested split adjustment;
- corporate-action vintages;
- LLM-use terms.

No loader, fallback entry or env key was added, and IDX backtests stay
refused.

### EODHD split handling, history depth and holiday rows — 2026-11-14

**Cases.** Two `.JK` stocks split during the free plan's one-year window. The
issuer disclosure of **RAJA** (Rukun Raharja, 9 June 2026; file 323,696 bytes,
SHA-256 `4a581ce38b25db59d92481016bd02b6fe5fb56fd574dd43acf3298909170031a`,
read with `pypdf`) sets a 1:5 split, nominal Rp25 to Rp5, with a *tentative*
schedule: last trading at the old nominal on 13 July 2026 and first trading at
the new nominal on **16 July 2026**. **MLPT** (Multipolar Technology) split
1:25; its date was taken from the vendor data below, not from an issuer
document.

**Requests.** Five EODHD calls with the user's free token, read from the
gitignored `agent/.env` by a scratch script that never printed it. Responses
stay outside the repository, as the terms allow for private use.

| Call | Status | Bytes | Rows | SHA-256 |
|---|---|---|---|---|
| `/api/eod/RAJA.JK?from=2025-11-01` | 200 | 28,315 | 253 | `7bf213c212ce4f61f8216e3c00b7f308fbfb7880cfeb19edc13d38f81235e0c7` |
| `/api/splits/RAJA.JK` | 200 | 103 | 2 | `b04285d19d82a10481110febc923a4f885168a82d7951632b899d2ddb121fba4` |
| `/api/eod/MLPT.JK?from=2025-11-01` | 200 | 28,595 | 253 | `76569ab51025fe637f9058746b9d7ad6d8ee1ef55eb89dbd3d45ef9cfcf508d7` |
| `/api/splits/MLPT.JK` | 200 | 53 | 1 | `314fc3c16a9a6de7a47d42b134235e4536bc38a6526e564dafd896ca4afe9fa0` |
| `/api/eod/BBCA.JK?from=2025-11-01` | 200 | 27,431 | 239 | `38711d9ee99878e7f72968171fc92d8eb577439ff598acf25953b1edee4e1e4b` |

**Split handling.**

- The **splits endpoint works on the free plan and is not clipped to one
  year**: RAJA returns 2016-06-07 (4:1) and **2026-07-16 (5:1)**; MLPT returns
  **2026-07-21 (25:1)**. RAJA's date matches the issuer's first day at the new
  nominal.
- **OHLC is unadjusted**, as documented. On the split day RAJA's close moves
  from 4,600 to 875, and MLPT's from 25,950 to 1,300. `adjusted_close` divides
  pre-split closes by exactly the ratio (`adjusted_close`/close = 0.2 and 0.04
  on the days just before the split, lower further back because of dividends).
- **Volume is split-adjusted**, as documented, so pre-split price × volume
  overstates traded value by the split ratio. Checked against BEI's monthly
  Table of Stock Trading (two single lookups from the open page, June 2026,
  regular market, 20 days): RAJA BEI 700,637,600 shares, EODHD sum 3,503,002,000
  = 5 × 700,600,400; MLPT BEI 1,038,600, EODHD 25,955,000 = 25 × 1,038,200.
  The remainders (−37,200 and −400 shares) were not explained.
- **Yahoo** (yfinance 1.5.2, `auto_adjust=False`) reports the same split dates
  and ratios, but its OHLC is already split-adjusted. On every pre-split day
  the EODHD close is exactly 5× (RAJA, 154 days) or 25× (MLPT, 156 days) the
  Yahoo close; after the split all 85 and 82 closes are equal. Daily volume is
  identical on every common day.

**Holiday rows: a data-quality hazard.** RAJA and MLPT each have 14 extra rows,
on exactly the 14 BEI holidays in the window (Peng-00149/BEI.POP/08-2025 for
late 2025, Peng-00171/BEI.POP/09-2025 for 2026), all with volume 0:

- 25 and 26 December 2025, 31 December 2025, 1 January 2026 and 16 January 2026
  carry a **sentinel price of 999,999.9999** in open, high, low and close (and
  `adjusted_close` 986,699.92 for RAJA);
- the other nine (1, 14, 15, 27, 28 May; 1 and 16 June; 17 and 25 August 2026)
  repeat the previous close with volume 0.

BBCA.JK over the same window has 239 rows, exactly the BEI sessions, and the
BBCA/BBRI probe of 2026-11-13 had none either. So the behaviour differs by
symbol, and nothing in the response marks these rows. Yahoo has no such rows
for either stock. Both vendors have one zero-volume, flat row for MLPT on
2026-03-27, a normal trading day; whether MLPT was suspended or simply had no
trade was not checked. A loader using EODHD would have to drop rows on dates
outside the BEI calendar and reject zero-volume sentinel prices, or a single
row could break returns, highs and position sizing.

**History depth.** Still unknown. Every `eod` response carries "Data is limited
by one year as you have free subscription", and EODHD publishes no JK start
date. The splits endpoint returning a 2016 event shows that corporate-action
history goes back further, not that prices do. Measuring price depth needs the
paid plan, which needs the user's purchase approval.

**Disposition.** Split handling is now tested on two cases. EODHD and Yahoo
agree on split dates and ratios; EODHD keeps raw prices with adjusted volume,
and Yahoo adjusts both. The holiday rows with sentinel prices are a new
reason not to use EODHD without calendar filtering. DATA-01 stays open for the
terms (accuracy disclaimer, no display or redistribution, LLM use not
addressed), JK price-history depth and corporate-action vintages. No loader,
fallback entry or env key was added, and IDX backtests stay refused.

### MLPT zero-volume row on 27 March 2026: a suspension — 2026-11-14

**Question.** Both EODHD and Yahoo carry one zero-volume, flat row for MLPT.JK
on Friday 27 March 2026, a normal BEI trading day (previous section).

**BEI lookup.** One visit to BEI's announcements page
(`idx.co.id/id/berita/pengumuman/`) in the built-in browser returned **HTTP
503**: a maintenance page saying the site is being developed and is
temporarily unavailable. It was not retried. The BEI announcement itself, and
its number, were therefore not read.

**News reports.** Two reports, which quote BEI but cite no announcement number:

- [Pasardana, 27 March 2026](https://pasardana.id/news/2026/3/27/bei-hentikan-sementara-perdagangan-saham-mlpt-3):
  BEI halted trading in MLPT **in all markets from session I on 27 March
  2026** until further notice. MLPT had closed at Rp14,450 on 26 March, down
  7.07% on the day. The article gives no official reason.
- [Pasardana, 30 March 2026](https://pasardana.id/news/2026/3/30/bei-buka-suspensi-perdagangan-saham-mlpt):
  trading reopened in the **Regular and Cash Markets from session I on 30
  March 2026**, per a written BEI statement dated 27 March.

**Result.** The zero-volume row is a full-day suspension, not a day without
trades, on the evidence of news reports; it is not yet confirmed from BEI's own
announcement. Both vendors fill the suspended day with the previous close and
volume 0, and nothing in either response marks it. A loader cannot tell a
suspension from an untraded day from vendor bars alone: it would need BEI's
suspension announcements as a separate, dated source. This is a further
reason, alongside the holiday rows, to keep a suspension record (RULE-01,
DATA-03) apart from the price series. No loader, fixture or code was added.
