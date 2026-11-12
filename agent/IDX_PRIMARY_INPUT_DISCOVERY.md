# IDX primary-input discovery — 2026-11-05

**New candidate documents were found; no new provider or reference input is
accepted for production.** The user asked us to find the missing primary inputs.
This bounded search follows new publisher routes rather than repeating the
Mendeley CSV/notebook audit, blocked Yahoo terms, or completed BEI catalogue work.
The existing [reference intake](IDX_REFERENCE.md#phase-2b-disposition-and-minimum-handoff)
and [provider handoff](IDX_PROVIDER_RESEARCH.md#minimum-technical-handoff) still apply.

Grounded: PROJECT_STATUS.md, TODO.md, the existing reference/provider findings,
new first-party pages and GitHub repository resources. Blast radius: this note
only. Invariants: no inferred production metadata, upstream permission, complete
calendar, historical universe, or backtest support. Verification: cited resource
identities, explicitly bounded access results, UTF-8/local links and parent-session
inventory/hash/index checks. There is no new runtime surface.

## New public candidates disposition — 2026-11-05

**Two new primary-source routes reviewed; no target OHLCV accepted.** This
follow-up did not reopen the failed IDX page, alternate IDX hosts, hidden
endpoints, old statistics PDFs or the closed Mendeley/Pholenk/TICMI audits.

Grounded: current status/backlog and intake contracts, contributor/security
guidance, `backtest/loaders/local_loader.py:207` (all-OHLC requirement),
`src/market_data.py:457` (declared frame currency), and
`src/tools/idx_research_tool.py:151`/`:296` (currency gate/backtests off), paths
relative to `agent/`. Blast radius: four documentation files. Invariants:
preserve previous changes/index, no inferred declarations, data acceptance,
account/key, purchase, outreach, scraping or access/TLS bypass. Verify: outside-
repo baseline of 3,212 reviewed public files, UTF-8 NUL Git status/inventory,
index copy/hash, source receipts/hashes, local links and `git diff --check`.
There is no changed runtime surface or reproduced code defect.

### Invezgo: useful declarations, authenticated data route

The first-party [Stock Chart dictionary](https://docs.invezgo.com/api-usage/endpoint/market-data/chart-stock/)
explicitly declares all OHLC in Rupiah, executed volume in shares, and trading
dates in WIB. Its timestamp suffix `Z` is expressly not UTC; a future mapping
must preserve the documented session date rather than blindly timezone-convert
it. Today's candle may be realtime. Static September 2024 examples do not
establish BBCA/BBRI coverage for the requested October 26–30, 2026 window.
Board/regular-market scope, all-OHLC adjustment, vintage and revision handling
remain undeclared for a selected original export. These are documentation
declarations, not verified responses or source-declared unknowns.

[API-specific terms](https://docs.invezgo.com/api-usage/terms/) require an account,
active Developer package and valid key, limit ordinary history to two years,
and prohibit redistribution/resale. General terms take precedence on conflict.
The linked [general terms](https://invezgo.com/terms) condition personal saving
on noncommercial use, prohibit bot-like collection and restrict sharing.
Neither public documentation nor a tier description grants this project API
entitlement, upstream rights or permission for the actual export/use. No API,
Try it, registration, key generation or subscription was attempted.

**Disposition:** documented candidate, not executable under this session's
no-account/no-credentials constraints. No original target response was obtained
and no normalization or helper/CLI intake was performed. Reopen only with a
permitted original export and missing declarations/terms, or a newly public
entitled sample. A third-party holder's possession alone does not permit sharing:
the API redistribution restriction must be respected, with permission covering
delivery to this project. No contact was made to seek an exception.

### ERPIW: public page, no available original

The publisher's [IDX Stock Summary](https://erpiw.com/stock/stock-summary/idx)
describes OHLC history but explicitly displays **Not uploaded yet** and says
the stock-summary data has not been uploaded. No dated target export or download
was exposed in the reviewed page. Its links to regulators do not establish
file semantics, rights or coverage. **Disposition:** unavailable input, not a
numeric-quality rejection and not an accepted source. Do not repeat this page
until a concrete dated export appears.

### Concrete stop and opening input

The [one opening package](#one-package-that-reopens-this-route) still applies:
permitted original daily BBCA/BBRI OHLCV for target review October 26–30, 2026
(whole-market originals acceptable), file-bound instrument/venue/board/market,
all-OHLC currency/adjustment, executed-share volume versus queued lots,
session/timezone, vintage/revisions/coverage and applicable acquisition/local-use
terms. We can hash and map it; no user-written JSON is required. Obtain through
a functional normal official export plus its dictionary/terms, a future public
entitled sample, or a holder expressly permitted to deliver the package. The
inspected Invezgo API cannot provide it here without changing the account/key
constraints; ERPIW currently provides no original. Continuing without account or
outreach remains conditional on a genuinely available permitted package, not
merely readable API documentation. Do not repeatedly search these candidates
without a new input or access change.

Four documents updated; runtime code, gates and all broad task acceptance remain
unchanged. DATA-01/02/03, IDX-02, RULE-01 and full RESEARCH-01 stay open. Local
Data Bridge remains unaccepted; MVP Yahoo/yfinance stays read-only, IDX backtests
off, paper/live separate and Index Alpha deferred. No provider integration,
deployment, dependency changes, staging, reset, commit or publication.

QA: `%TEMP%\idx-new-source-review-3fe8287b91`.
`documents/` retains four original public HTML documents; ordinary verified-TLS
GETs all returned HTTP 200. `document-download-receipt.json` records exact URLs,
local request/completion times, selected headers, sizes and SHA-256. These are
documentation receipts, not price-export receipts or source vintage. The web
reader failed on the chart URL, while the ordinary GET succeeded; no browser
identity changes or TLS weakening were used. Extracted text, agent research
synthesis and `intake-review.json` are separately identified. The initial text
printer hit Windows cp1252 UnicodeEncodeError; output was switched to UTF-8 and
extraction completed, without reacquiring sources. `verification.json`,
`evidence-hashes.json` and `session.diff` retain preservation checks. Runtime,
frontend/build and provider tests were not repeated for documentation changes.

## Official manual disposition — 2026-11-05

**The linked primary manual has now been obtained and reviewed. This public
documentation path is complete; it does not qualify an individual-stock OHLCV
input. Stop this route pending the single external package below.** The earlier
failed preview/download observations remain historical evidence, superseded by
the successful individual-file interaction in this increment.

Grounded: current status/backlog, contributor/security/foundation and intake
contracts; `backtest/loaders/local_loader.py:207`, `src/market_data.py:439`,
`src/tools/idx_research_tool.py:151` and `:296`, reference importer
`src/markets/idx_reference.py:75`, API `src/api/idx_research_routes.py:34`, MCP
registration `mcp_server.py:2829`, and metadata-rejection tests
`tests/test_idx_research_quality.py:38` (paths relative to `agent/`).
Blast radius: four documentation files. Invariants: preserve all previous work
and index, currency gate, source-bound declarations and execution rejection;
no invented bars, account, outreach, scraping, TLS/access bypass or dependencies.
Verify: original magic/size/hash/page count, seven-page extraction/render review,
receipts and pre/post public-file hashes, NUL Git inventory/status, index bytes,
UTF-8/local links and `git diff --check`. There is no changed runtime surface.

### Successful acquisition and file identity

From the [officially linked public folder](https://drive.google.com/drive/folders/1-aiZVJwc17tfFOfmyjFH2V2igjttZ7y9),
opening the individual row and dismissing the Drive promotional notice exposed
the seven-page preview. Its **Download** button returned the original local PDF;
Download all was not repeated. The preview's Open in new tab control also exposed
the [individual manual](https://drive.google.com/file/d/1-hJVpCmVmmzQ3wiy6wh3shqWiUafO4MY/view?usp=drive_open).
No login, direct guessed endpoint, certificate override or account authorization
was used. This is a changed successful UI result on the previously unfinished
route, not another audit of the rejected Daily Statistics PDF.

`Manual Guides - IDX Statistical Publication v1.2.pdf`: **981,358 bytes**, `%PDF-`,
**7 pages**, SHA-256
`aab5f6cd9e341c38e6c04fa22c81c14a59d9a6aa974f56212bc16a28283a636c`.
The receipt was recorded at **2026-11-05T02:27:42.362320+00:00** (09:27 WIB).
HTTP status, headers and exact request/completion times were not exposed and
remain null. The listing's 15 February 2023 modification date, copyright 2023
and manual v1.2 are not a price-data vintage or proof of applicability to another
export. The 2026 publication's link establishes the provenance of this guide;
it does not establish unchanged field semantics for every other BEI product.

### What all seven pages establish

- **Page 1:** title, Data Services Division, v1.2 and conditional noncommercial
  citation/use permission with full source and access date. It does not classify
  this project's actual investment research as noncommercial or authorize a
  general feed, redistribution or another product's acquisition method.
- **Page 2:** Trading Summary volume is executed **shares across regular, cash
  and negotiated markets**, not queued bid/offer lots. Previous/Highest/Lowest
  here describe **IHSG**, not stock-level OHLC. These declarations apply to the
  named statistical sections, not automatically to a Stock Summary export.
- **Page 3:** YTD daily averages, foreign transactions, PER/PBV and investor
  composition. These are not daily per-stock bars.
- **Pages 4–5:** top-stock/member rankings; gainers/losers compare closing prices
  across days with corporate-action adjustment mentioned. That limited statement
  cannot declare raw/adjusted treatment of every OHLC field in an absent export.
  Index performance and leader/laggard definitions likewise supply no stock OHLCV.
- **Pages 6–7:** world-index ranking and ISSI aggregates/rankings. ISSI volume
  again covers regular/cash/negotiated trades. No BBCA/BBRI daily OHLCV table or
  new qualifying export route appears in the reviewed manual.

**Decision:** retain the manual as primary documentation; reject its use as the
missing file-bound stock-OHLCV specification. No original target price export
was obtained, so no numeric quality/coverage rejection of such an export is
claimed. Venue/board scope for the selected stocks, all-OHLC currency,
executed-volume semantics for that export, session-date/timezone, all-OHLC
adjustment, vintage/revisions, coverage and applicable file/method/use terms
remain unavailable. These are absent declarations, not source-declared unknowns.
The guide's specific corporate-action statement is preserved in its actual scope.

### One opening package and how to obtain it

The [single opening package](#one-package-that-reopens-this-route) remains precise:
original permitted daily **BBCA/BBRI OHLCV for 26–30 October 2026** (a target
review window, not verified coverage/sessions; intact whole-market originals
are acceptable), plus a dictionary/declaration bound to those files/version,
coverage/vintage/revisions and terms applicable to local retention, calculation
and UI/CLI display. Include the originating download page/method/access time;
we can compute hashes and perform mapping, so user-prepared JSON is unnecessary.
Every OHLC currency/adjustment, venue/board/market, executed shares versus queued
lots and session/timezone declaration must be source-supported. Explicit unknowns
must be attributed to the source and assessed; missing metadata cannot be renamed
unknown to pass intake. Public terms can suffice when their applicability is
demonstrated; a special permission letter is not automatically required.

Obtain that package through the canonical BEI Stock Summary page's normal export
controls **if it becomes functional**, together with its applicable primary
dictionary/terms, or from an authorized holder who already has the originals and
those documents. No request/contact was sent and no user file search is required
to close this increment. The manual itself was obtained **without account or
outreach**. Continuing OHLCV acceptance without account/outreach is possible if
the complete permitted package becomes publicly available or is supplied by an
existing authorized holder; this session has not established such a public route.
Do not reopen the failed page, other daily statistics PDFs, or Pholenk/TICMI
without a new qualifying input or concrete access change.

The normalizer still requires all OHLC and validates observations; it cannot
establish source semantics/rights. Serving provenance carries declared frame
currency; the shared helper still checks `currency_declaration`, then Jakarta,
daily/share-volume/adjustment contracts, and reports `backtest_enabled: false`.
The API/MCP/CLI share that helper. The reference importer is structure-only and
cannot turn this manual into accepted price data. No reproduced code defect,
normalization, helper/CLI run or new runtime test is justified by this document.
DATA-01/02/03, IDX-02, RULE-01 and full RESEARCH-01 remain open; MVP Yahoo/yfinance
is unchanged, local bridge unaccepted, backtests off, paper/live separate and
Index Alpha deferred. Provider integration and deployment were not performed.

New QA: `%TEMP%\idx-manual-review-0fb99aa78f`.
`documents/` retains the original, `document-download-receipt.json` records
provenance and null transport fields, `manual-extracted.txt` and `rendered/`
retain all seven pages, and `intake-review.json` records this agent's decision
(not a publisher declaration). Baseline: 3,212 reviewed public-file hashes,
strict UTF-8 NUL Git inventory/status and index copy/hash. `verification.json`,
`evidence-hashes.json` and `session.diff` record final preservation checks.
No backend/frontend suites, build or provider probe was repeated; no staging,
commit, reset, publish or deployment occurred.

## Official statistics file review — 2026-11-05

**Original official file obtained; rejected for the requested daily per-stock
OHLCV intake.** This is a completed review of a new candidate file, not another
inaccessible-link finding or acceptance of data for the application.

Grounded: current status/backlog, intake owners/contracts reconciled below,
the newly rendered official Statistics page and all nine pages of its selected
PDF. Blast radius: four documentation files. Invariants: preserve prior work
and index, no invented OHLCV/metadata, scraping, account/outreach, TLS bypass or
IDX execution. Verify: pre-edit reviewed-public-file hashes/NUL inventory/status,
index copy, original PDF magic/hash/page count, extracted text plus page renders,
receipts, local links/UTF-8 and `git diff --check`. No changed runtime surface.

### Acquisition through a working public route

The [official Statistics page](https://www.idx.id/en/market-data/statistical-reports/statistics)
displayed daily publication rows and actual download links in the normal browser.
The row for 30 October linked directly to
[IDX Daily Statistics 30 October 2026](https://www.idx.co.id/Media/5hphz3ey/ds_261030.pdf).
That exact rendered link was downloaded with the browser's file-download
capability to `%USERPROFILE%\Downloads\ds_261030.pdf`, then copied intact to QA.
The different `.co.id` file host came from the official link, not an invented
alternate host used to bypass the earlier Stock Summary failure. No undocumented
endpoint, login, CAPTCHA, access-control workaround or upstream code was used.

Original: **1,974,315 bytes**, `%PDF-` magic, **9 pages**, SHA-256
`a36a26c07279977bfdebfc27ab33ba470e24d825df0c42f0d0ae755c3a8a033c`.
The browser exposed the local path but no HTTP status, response headers or exact
request start/completion timestamps; receipt fields remain null. The QA receipt
was recorded at 2026-11-05T02:18:00Z (09:18 WIB), not a publisher data vintage.
The other four daily PDFs in the proposed October 26–30 window were not downloaded
after the first file established the scope mismatch.

### File-bound evidence and rejection

All nine pages were extracted with existing pypdf and rendered with bundled
pypdfium2, then visually inspected as a contact sheet:

- **Page 1:** dated publication, composite-index summary and aggregate trading.
  Its footnote states stock trading totals include regular, cash and negotiated
  markets. These aggregates cannot establish regular-market BBCA/BBRI bars.
- **Page 3:** top-stock volume (million shares), value (billion IDR) and frequency
  rankings include BBCA/BBRI. They have no per-stock OHLC fields. Displayed rounded
  rankings must not be reverse-engineered into exact executed-share observations.
- **Page 4:** market cap/listed-security counts and gainers/losers with previous
  and today prices. Previous/today are not a daily OHLC table.
- **Page 5:** market/instrument trading recapitulation, rather than per-symbol
  OHLCV. Pages 2 and 6–8 contain YTD/investor/index/world/ISSI summaries, likewise
  not the required BBCA/BBRI OHLCV series.
- **Page 9:** publication version v.2.2.0, disclaimer and noncommercial-use
  permission conditional on full source/access-date attribution. This is terms
  evidence bound to the actual publication. It supplies neither missing OHLC
  fields nor entitlement for a different export/feed/redistribution. Actual-use
  applicability remains separate from the numeric rejection.

**Decision:** retain as official publication evidence only; reject as input to
the requested daily per-stock research path. No normalization, reference import,
loader/helper/CLI invocation, production metadata or runtime acceptance occurred.
The missing OHLC fields alone decide the rejection; no inferred all-OHLC IDR,
session timezone, adjustment, revision/vintage or historical coverage can repair
them. The existing source-declaration/currency gates remain unchanged.

### Newly discovered manual route and its limits

Page 9 links to `https://bit.ly/IDXstat-manual`. Normal browser navigation showed
the destination as the public
[Manual Guides folder](https://drive.google.com/drive/folders/1-aiZVJwc17tfFOfmyjFH2V2igjttZ7y9).
Without logging in, its listing showed `Manual Guides - IDX Statistical
Publication v1.2.pdf`, size 958 KB, modified 15 February 2023. The folder was
linked by this official PDF; the listing date is not a data vintage or proof of
manual contents. Preview did not open, and Download all produced no captured
file within 30 seconds. No original guide or interpretation of its contents is
claimed. The web reader could not retrieve the short URL; a separate ordinary
Python GET failed local issuer certificate verification. TLS verification was
not disabled. Normal browser navigation required no warning bypass.

This is a precise public source route for a future changed download result,
not a reason to repeat the same failed controls in this session. Even a statistics
manual would require export-specific binding before applying semantics to Stock
Summary. No contact form or email was submitted. No account or purchase was made.

### Remaining input and preservation

The [single input package below](#one-package-that-reopens-this-route) remains
required: original exact daily per-stock OHLCV plus source-bound semantics,
coverage/vintage/revisions and applicable terms for actual local research use.
No user-prepared JSON is needed. A public authorized export/documentation route
can avoid an account/outreach if available; this publication does not provide
that package. Pholenk/TICMI were not reopened without new qualifying primary
inputs. DATA-01/02/03, IDX-02, RULE-01 and full RESEARCH-01 remain open; backtests
off, paper/live separate, Index Alpha deferred and Yahoo/yfinance MVP unchanged.

New QA: `%TEMP%\idx-statistics-intake-40a7db5844`.
`documents/ds_261030.pdf` retains original bytes; `browser-download-receipt.json`
and `document-download-receipt.json` record the exposed provenance and unknowns.
`pdf-extracted.txt`, `rendered/page-1.png` through `page-9.png`, and
`rendered/all-pages.png` retain the review material. `intake-review.json` and
`failure-record.json` are agent records, not publisher declarations.
`statistics-web-reader.txt` and `evidence-hashes.json` identify further evidence.
Baseline before edits: 3,212 public-file hashes, UTF-8 NUL Git status/inventory
and index copy. Final `verification.json`/`session.diff` record preservation and
document checks. No code/tests/dependencies/frontend changes or runtime-suite
rerun; no provider integration, deployment, staging, commit or publish.

## Official download disposition — 2026-11-05

**Stopped pending one external input package. No official OHLCV export accepted.**
This session pursued the canonical public Stock Summary download route, following
the conditional website permission below. It did not repeat the Mendeley audit,
blocked catalogue/PDF requests, Pholenk tree/history or TICMI restricted pages.

Grounded: current status/backlog, contributor/security/foundation documents,
latest discovery/personal-research notes, reference/provider intake and the
owners below. RTK.md remains absent. Blast radius: four documentation files.
Invariants: preserve prior changes/index; no inferred units, currency, adjustment,
rights or historical completeness; no scraping/access workaround; backtests off.
Verify: outside-repo pre-edit NUL inventory/status, reviewed-public-file hashes,
index copy/hash, evidence receipts, UTF-8/local links, session diff and
`git diff --check`. There is no changed runtime surface.

### Canonical download route and observed failure

The [official Ringkasan Saham page](https://www.idx.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/)
returned only navigation and All Stock/Margin/Short Selling buttons in the web
reader. A normal browser navigation likewise displayed the breadcrumb, an empty
heading and those tabs, with no table, date selector or Download control.
One Menu click left the accessibility tree unchanged. Browser console output
recorded `SyntaxError: Invalid or unexpected token` and
`ChunkLoadError: Loading chunk 5 failed` for `/_nuxt/c8a5bdd.js` at
2026-11-05T02:08:47Z (09:08 WIB). This establishes a failure of this observed
page load, not its underlying cause or global unavailability of BEI downloads.
No direct script request or undocumented data endpoint was used to work around it.

A separate ordinary public GET to the same canonical page returned **HTTP 403**,
17 bytes, retained as an error-response artifact, not a market export. It was
not retried with cookies, changed browser identity, another host or a bypass.
The browser and GET outcomes are different observations; neither proves an
export was obtained. Search results on alternate/test IDX hosts were not used
to bypass the canonical page or as an export-bound specification.

Bounded searches for a Ringkasan Saham download guide and declarations of
opening-price currency, executed-share volume and adjustment did not retrieve a
qualifying source dictionary. Exact queries and the scope of negative results
are retained outside the repo. This is not proof that no such document exists.
No all-OHLC IDR, regular-market-only scope, volume unit, session/timezone,
raw/adjusted policy, source vintage/revisions or coverage was established for a
selected original export. Labels or plausible values cannot supply those facts.
The website terms below are still conditional rights evidence; file/method/use
applicability was not established by this failed download attempt.

### Reconciliation with existing intake owners

Paths below are relative to `agent/`, checked in the current checkout:

- `backtest/loaders/local_loader.py:207` normalizes local columns and validates
  IDX OHLCV; `:440` reads configured files. It does not authenticate an export or
  establish upstream semantics/rights. Its UTC-naive parsing contract needs
  reconciliation to declared session dates before using actual data.
- `src/market_data.py:439` obtains volume units from the serving loader and
  `:457` carries declared frame currency. It does not infer IDR from `.JK`.
- `src/tools/idx_research_tool.py:151` requires declared IDR before Jakarta,
  daily/share-volume/adjustment checks. Explicit source-declared `unknown`
  adjustment is distinct from absence; no adjustment is invented here.
  `:296` reports `backtest_enabled: false`; `:302` owns the module CLI.
  The API route calls that same tool (`src/api/idx_research_routes.py:34`),
  also registered for MCP (`mcp_server.py:2829`).
- `src/markets/idx_reference.py:75` imports declared reference JSON;
  `:105` checks market/currency/timezone and `:178` owns its structure-only CLI.
  Instrument/calendar/rule imports are separate from accepting OHLCV bars.
- `tests/test_idx_research_quality.py:38` exercises metadata-stage rejection;
  `tests/test_idx_reference.py:26` exercises snapshot import. These were read,
  not rerun. No reproduced application defect justifies changing either owner.

Consequently, no production metadata, normalization, loader/helper/CLI run or
new test is justified for this absent official file. This is an acquisition and
source-declaration blocker, not a numeric rejection of an inspected dataset.

### One package that reopens this route

Supply together at a permitted local path outside the repository:

1. **Original official download(s)** for proposed tickers BBCA and BBRI, daily
   window **2026-10-26 through 2026-10-30**, preserving original bytes/filenames.
   This is a requested review scope, not verified session or coverage evidence.
   A daily whole-market file is acceptable: retain it intact and later project
   the named subset. Do not substitute previous close/first trade for Open.
2. **Source-bound dictionary or dated declaration** tied to those files/version:
   venue/instrument and board/market scope; currency for every OHLC field;
   executed volume in shares versus queued bid/offer lots; date-as-session and
   timezone; raw/adjusted treatment for every OHLC field. An explicitly declared
   limitation such as unknown adjustment must remain visible, not be guessed.
3. **Receipt and coverage/revision record:** originating page/download URL,
   actual download method and access time with offset, original SHA-256,
   publication/as-of/retrieval vintage, revision policy and known missing dates
   or excluded instruments. Website retrieval time alone is not price vintage;
   unknowns must be stated by the source and reviewed as limitations.
4. **Applicable terms plus actual-use description:** the file/product terms
   and website terms applicable to this acquisition, with full attribution and
   access date, covering local retention/calculation/UI/CLI display. Personal
   investment research is not automatically classified as noncommercial.
   A separate letter is unnecessary when applicable public terms demonstrably
   cover file, method and actual use; unresolved applicability remains a blocker.

Obtain the package via the normal public Ringkasan Saham download UI once it
works, with its linked official documentation, or from an authorized holder who
can provide the originals and source/permission documents. The user need not
prepare normalized JSON. **An account or outreach is not inherently necessary
if that public route supplies both file and declarations; this session cannot
complete the package without changed external availability or supplied input.**
If the public documentation remains insufficient, a new source declaration is
required; another identical search or a green test run will not provide it.
No account, outreach or purchase was performed or authorized in this session.

On arrival, review the package before mapping, preserve original/normalized
hashes and transformations, then use the existing owners to reconcile values,
metadata and a bounded helper/CLI result. A real metadata gap may then justify
a reproduced fix and distinguishing regression with other-market controls.
Do not reopen Pholenk/TICMI without the new primary inputs already specified
below. Stop this search now; resume only on a new file/declaration or concrete
access change. Full DATA-01/02/03, IDX-02, RULE-01 and RESEARCH-01 stay open.
MVP Yahoo/yfinance remains one-vendor local read-only research; Local Data Bridge
is unaccepted, currency gate unchanged, backtests disabled, paper/live separate
and Index Alpha deferred. No provider integration or deployment occurred.

### Evidence and preservation

New QA directory:
`%TEMP%\idx-official-export-bb4af937a4`.
Before editing: 3,212 reviewed-public-file hashes, UTF-8 NUL Git status/inventory
and an index copy. Prior terms receipt/HTML reconciled successfully to SHA-256
`2c6999bb3e6984901936a1713ef73df9607dff4297b81160b23089ffd8d3a040`.

`document-download-receipt.json` retains the canonical GET's status/URL/times
and selected headers. `documents/official-stock-summary-response.html` is the
17-byte 403 response, SHA-256
`2938e9f1284180959e33ab1718d0793a72ff6e4cdb8108c34dcd14e69446de5c`.
Its extension does not change the recorded `text/plain` response type.
`browser-observation.json` is an agent transcription of returned UI/errors,
not original HTML; the screenshot was inspected in tool output only.
`web-reader-stock-summary.txt` saves the reader result;
`search-scope.json` records queries and bounded negative findings.
`evidence-hashes.json` identifies these evidence files. No market-file receipt
or screenshot-on-disk is claimed. `verification.json` and `session.diff` record
the final document/hash/inventory/index checks. No runtime suites were repeated;
code/tests/dependencies/frontend were untouched. No staging, commit or publish.

## Official website permission evidence — 2026-11-05

**New upstream terms found: conditional noncommercial use of data obtained from
the BEI website has explicit public permission evidence.** This narrows the
previous rights gap for a directly obtained official export. It does not accept
Pholenk, TICMI, a data feed or any CSV for this application.

Grounded: newly read BEI website terms, the prior candidate decisions below,
reference/provider intake contracts and current status/backlog. Blast radius:
four documentation files only. Invariants: no inferred CSV metadata, scraping,
third-party redistribution rights or IDX execution support; preserve all prior
changes/index. Verify: original document receipt/hash, local links/anchors,
UTF-8, session diff and complete public-file inventory/hash/index comparison.
There is no new runtime surface.

### Observed terms and their limits

The official [Syarat Penggunaan](https://www.idx.id/id/syarat-penggunaan)
was readable through the web tool and an ordinary public GET (HTTP 200):

- Clause 6 permits noncommercial use, including quotation, subject to full
  source attribution and access date; it prohibits web scraping/crawling.
  Commercial use/dissemination requires written permission from BEI and/or the
  original owner.
- Clause 2 describes a three-year window for displayed listed-company
  information and directs older information to TICMI under TICMI terms. This
  is not a promise of three years of complete daily OHLCV.
- Clauses 3 and 12 disclaim data guarantees and allow changes to information
  and terms. No effective date or historical applicability interval was observed.
- Clause 8 says a link to BEI does not imply BEI approval or endorsement of
  the referring institution/site.

The page is accepted **as evidence of these conditional website-use terms**.
It is not a general data-feed agreement. The distinction matters: the next
review need not automatically demand a separate permission letter if posted
terms demonstrably cover the actual file, acquisition method and noncommercial
use. Conversely, personal investment research must not silently be classified
as noncommercial for every purpose. Specific product/file terms and the actual
use must be checked; no legal or historical entitlement is inferred here.

### Decisions after the new evidence

**Direct official export: a concrete candidate route for limited review.**
An original file obtained by an ordinary permitted download, with its source
URL/access date and applicable terms, can be evaluated for a bounded local
noncommercial use. This is an intake option, not an accepted dataset. There is
no selected official export in this increment; no market data was downloaded
or parsed. No scraper, undocumented endpoint, access-control workaround or
provider account was used. A file's all-OHLC currency, executed-volume unit,
session/timezone, adjustment, vintage/revisions and scope remain necessary
before the existing loader path can receive production metadata. Missing
metadata must still be obtained from source declarations, not inferred from
these website terms.

**Pholenk: still waiting for file-bound semantics and acquisition/rights
provenance.** The new website terms are relevant upstream evidence, but they
do not establish how the pinned CSV's source files were acquired, which terms
applied then, or the publisher's authority for redistribution under ODbL.
The earlier request for applicable upstream terms/grant can now reference this
specific document; it still requires a traceable connection to the export.
No finding of infringement or blanket prohibition is made.

**TICMI: still waiting for export/specification and applicable entitlement.**
The BEI terms explicitly defer older-company-information access to TICMI's
own terms; they do not grant this project TICMI access. Newly checked public
routes included the TICMIDATA document collection and its linked terms/help:
the collection yielded navigation but no qualifying OHLCV specification;
`term-conditions` was restricted and `pusat-bantuan` returned 403 to the web
reader. The Kampung Pasar Modal FAQ and Kaggle discussion/versions routes were
not accessible through that reader. Targeted issuer/permission/dictionary
searches produced no additional retrieved file-bound declaration. Search
extracts, unrelated education/recruitment terms and other researchers' indexed
permission letters were not adopted as project permission. No blocked route
was retried through an access workaround.

Next progress requires a permitted original export plus its semantic
declarations, or a new publisher-bound declaration. The three candidates are
not interchangeable: website-use permission, publisher redistribution rights
and a TICMI customer entitlement are separate facts. Do not repeat the same
searches or green test suites as progress. DATA-01/02/03, IDX-02, RULE-01 and
full RESEARCH-01 remain open; Local Data Bridge/currency gate and disabled
backtests are unchanged. No provider integration or deployment occurred.

### New receipt and preservation

QA directory:
`%TEMP%\idx-website-terms-de60696324`.
Original `documents/idx-website-terms.html`: 171,540 bytes, SHA-256
`2c6999bb3e6984901936a1713ef73df9607dff4297b81160b23089ffd8d3a040`.
`document-download-receipt.json` preserves the request/completion time, exact
resolved URL, HTTP status and selected headers. Request started
2026-11-05T02:03:54.516148+00:00 (09:03 WIB); retrieval time is not a terms
effective date or a data vintage. The response exposed no Last-Modified value.
Baseline: 3,212 public-file hashes, UTF-8 NUL Git status/inventory and index
copy/hash before edits. `verification.json` and `session.diff` hold the final
checks. Code, tests, dependencies and frontend were untouched; runtime suites
were not repeated. No staging, commit, publish or deployment.

## Follow-up decision — 2026-11-05

**Pholenk: waiting for specific publisher declarations and upstream permission.
TICMI: waiting for a permitted export/specification and applicable entitlement.**
Neither candidate meets the minimum for local personal OHLCV intake. This is a
decision to stop these acquisition paths until the inputs below arrive, not a
finding that either publisher can never supply suitable data. No full CSV was
downloaded, normalized, imported or run through the loader in this follow-up.

Grounded: the pinned publisher tree, README/schema histories, current documents,
new TICMI general terms, prior receipt/JUnit files and local owners
`src/tools/idx_research_tool.py:151` and `src/markets/idx_reference.py:75`.
Blast radius: four documentation files. Invariants: preserve existing work/index,
the IDR currency gate, explicit unknowns and disabled IDX backtests. Verify:
document blob/SHA-256 identities, receipt assertions, local links/anchors, UTF-8,
session diff and baseline inventory/hash/index. No new runtime surface.

### Pholenk: what the additional primary routes establish

The [complete pinned tree](https://api.github.com/repos/Pholenk/IDX-Dataset/git/trees/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b?recursive=1)
contains 2,106 entries and explicitly reports `truncated: false`. There are
983 files under `dataset/stocks/csv/`; this is a file count, not a verified
historical universe, board scope or per-symbol coverage. The tree contains no
Python/notebook/JavaScript/TypeScript conversion source or source-XLSX manifest.
The README gives a general XLSX-to-CSV-to-JSON lineage, without binding input
files, transformation options or correction history to the AADI preview blob.
No such binding was found in the inspected publisher documents.

The [README history](https://api.github.com/repos/Pholenk/IDX-Dataset/commits?path=Readme.md&sha=9bb3b26bd28ab46bc2f3e74a7c03805ce053301b&per_page=100)
returns six entries, latest 12 March 2026. The
[schema history](https://api.github.com/repos/Pholenk/IDX-Dataset/commits?path=dataset-metadata.json&sha=9bb3b26bd28ab46bc2f3e74a7c03805ce053301b&per_page=100)
returns twelve entries. Its
[latest change](https://github.com/Pholenk/IDX-Dataset/commit/57b5809a6b047de5d8d8b06087c6cf351ea3b510)
on 9 April only removes `./` from the preview CSV path. It does not update the
March 9 coverage sentence. Historical patches other than that latest patch were
not audited. Current metadata still says June 1; none of these dates establishes
the upstream observation/retrieval vintage or the preview's last session.

Additional bounded routes: the repository releases collection and all-state
issues collection each returned an empty array; publisher-scoped repository
search `user:Pholenk IDX` returned only this repository. These are observations
at retrieval, not proof that no declaration exists elsewhere. The Kaggle page
identified by schema slug `pholenk/eod-data-indonesia-stock-exchange` provided
no readable lines to the web reader. The connector rejected the tags URL and a
repository-search URL as unsupported; tags were not inspected. No access
restriction was bypassed or upstream code executed.

The pinned schema supports only these bounded semantic findings:

- `Open`, `High`, `Low`, `Close` identify price roles; no all-OHLC currency is
  declared. Venue, plausible magnitudes and turnover ratios cannot supply IDR.
- `Volume` says trading volume without a share/lot unit. `OfferVolume` and
  `BidVolume` explicitly describe queued lots before close. Their unit cannot
  be transferred to executed volume. Separate non-regular fields do not prove
  that the main OHLCV fields cover only the regular market.
- `Date` declares a YYYY-MM-DD string. It does not identify session date versus
  publication date, timezone, or timestamp projection rules.
- No raw/split/dividend adjustment policy or source-revision vintage is
  declared for the selected CSV. `WeightForIndex` describing an adjusted index
  value does not describe OHLC adjustment.
- The schema advertises daily history from January 2020 to March 9, 2026, while
  the previously observed preview contains March 11. Current metadata is June 1.
  Coverage must be reconciled for a selected file/window; none is a calendar or
  proof of completeness. README itself warns of missing dates.
- ODbL section 2.4 separates content rights; section 7.1 disclaims warranties
  including title and non-infringement. The inspected publisher documents supply no applicable
  BEI-content grant for this project's local storage/processing. This is an
  unresolved evidence gap, not a legal conclusion about the publisher.

### Exact inputs that reopen the Pholenk path

A dated publisher declaration or versioned manifest must bind commit
`9bb3b26bd28ab46bc2f3e74a7c03805ce053301b` and the selected CSV blob/hash
(initial candidate: AADI preview `496b998e890479272caa76cefdbd57caadf92424`) to:

1. Original BEI source files/revisions or a traceable source manifest, and the
   conversion/merge/filter/null/correction steps used for that export.
2. Currency of every OHLC field; executed-volume unit independently of queued
   bid/offer lots; venue/instrument/board/market scope; session-date and timezone
   meaning; raw/adjusted treatment of every OHLC field.
3. Selected symbols/date window, known omissions, source retrieval/as-of vintage
   and revision handling. If adjustment/vintage is unknown, the publisher must
   explicitly declare that limitation; it cannot be silently invented here.
4. Applicable upstream terms/grant, effective scope and provenance establishing
   permission to obtain, retain and process these contents for **personal local
   research**, including local UI/CLI display/calculation. ODbL alone is
   insufficient. Cloud/LLM transmission and redistribution are separate scopes,
   not prerequisites requested for this limited evaluation.

The route is a new public publisher manifest/declaration linked from the pinned
repository/Kaggle release, or documents supplied by the user/authorized
representative with the original export at a permitted local path. No outreach
was made. A named subset of at most eight regular shares and a bounded daily
window can start review; a full-market historical package is unnecessary for
that narrow scope. It would still not close full DATA-01/RESEARCH-01 or enable
backtests. On arrival, preserve original bytes/receipt/hash outside the repo,
review rights/semantics, then use the existing intake/loader owners. Stop here
until that input changes; do not repeat this tree/search as progress.

### TICMI: new public document and disposition

The newly inspected [general website terms](https://kampungpasarmodal.com/page/terms-condition)
state ownership of site content and limits on dissemination, and disclaim
responsibility for incompatibility/loss following data updates. They do not
provide an OHLCV data dictionary, an export-specific correction policy, BEI
upstream permission or project entitlement. The HTTP `Last-Modified` value is
14 January 2026; the page declares no observed effective/revision date. That
header is transport metadata, not a contractual commencement date.

Targeted searches for public Stock Summary/OHLC documentation and local-research
terms produced no additional retrievable qualifying specification/grant. The
documentation domain's robots restriction/search extracts are not new evidence
of endpoint semantics; the previously blocked root, Investor Summary, and old
service terms were not re-opened as progress. No authenticated API was called.

**Waiting input:** a public versioned daily-stock specification or a permitted
original export with field dictionary, explicit opening price, all-OHLC currency,
share-volume and regular-market/session/timezone semantics, adjustment, vintage,
revisions and selected coverage; plus applicable dated agreement/permission
covering personal local retention/processing/display. Route: a future public
TICMI document or an export/agreement supplied by the user/authorized holder.
The service terms already recorded below identify a permission route, not a
project grant. No account, contact, subscription or purchase was made. Further
searches stop until a new document or authorized file is available.

### Receipts and local reconciliation

New QA directory:
`%TEMP%\idx-primary-decision-ab6c683ecb`.
`documents/` retains original bytes of the four pinned publisher documents and
new TICMI general terms, all HTTP 200; `document-download-receipt.json` records
URLs, request/completion timestamps, selected headers, sizes and SHA-256.
All four publisher documents also match their expected Git blob identities.
No original CSV is claimed by these document receipts.

Receipt SHA-256:

- `connector-receipt.json`: `b9532611fa23ef1ac78276444303b2b56ff2f2c8302e2080c00f7b4ff6fbe0bd`.
- `followup-connector-receipt.json`: `0b0ea1067bc4d8f103689b1b6d9dc3e917de64f52795ba7fbf28bae641754a39`.
- `document-download-receipt.json`: `7bdd9fe86b53eacdb8215ec50f503c51b831c68106ba697653bae0d2686343df`.

The prior connector receipt hash matches its recorded value. Prior JUnit files
confirm packaging 7 passed, absent-backend 4 passed/3 skipped and startup/auth/SPA
129 passed. Current fixture still uses the existing backend and three offline
pip flags. These are historical tests, not new runs. The backend full suite has
not been repeated after that fixture change. Current research code still requires
declared IDR/Jakarta/daily/share-volume/adjustment metadata, and reports
`backtest_enabled: false`. The reference importer still validates declared
market/currency/timezone; parsing cannot establish rights.

There is no reproduced code defect justifying a code change in this increment.
No production metadata, provider adapter or data acceptance was added. DATA-01/02/03,
IDX-02, RULE-01 and full RESEARCH-01 remain open; MVP Yahoo/yfinance local read-only
research remains accepted separately. Frontend, dependency manifests, trading,
runtime state and index are unchanged. Verification results are in
`verification.json` and `session.diff` in the new QA directory.

## 1. A retrievable alternative export: Pholenk/IDX-Dataset

The publisher [README](https://github.com/Pholenk/IDX-Dataset/blob/main/Readme.md)
describes CSV/JSON derived from BEI spreadsheets, identifies BEI as the original
data owner, and warns that dates can be missing even outside listed holidays.
It declares ODbL for the derived dataset. This is publisher testimony, not a BEI
grant of processing or redistribution rights.

GitHub's public resources resolved `main` to commit
[`9bb3b26bd28ab46bc2f3e74a7c03805ce053301b`](https://github.com/Pholenk/IDX-Dataset/commit/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b),
with commit time 2026-06-01T11:11:51Z. Its
[current metadata](https://github.com/Pholenk/IDX-Dataset/blob/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b/metadata.json)
declares `last_updated: 2026-06-01`. The metadata linked from the README instead
pins an earlier commit and declares `last_updated: 2026-03-09`.
[Publisher metadata](https://github.com/Pholenk/IDX-Dataset/blob/976d334295f39452d8331e4e7da2bbe3d3ebf556/metadata.json).

The [schema document](https://github.com/Pholenk/IDX-Dataset/blob/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b/dataset-metadata.json)
distinguishes stock OHLC from indices that lack opening prices. It describes
date format, stock code/name, remarks, price fields, trading volume, bid/offer
lots and non-regular-market fields. The first five lines of the
[AADI preview](https://github.com/Pholenk/IDX-Dataset/blob/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b/dataset/preview/stocks/csv/AADI.csv)
were read through the GitHub connector; they include OHLC and a 2026-03-11 row.
The schema description still says coverage ends on March 9. Consequently, neither
the old README-linked metadata nor that schema sentence is a reliable upper bound
for the preview. This does not prove the current June 1 envelope date is wrong.
No full CSV audit, reader execution, normalisation or runtime import was performed.

These are concrete source identities returned by the connector, **Git blob SHA-1,
not local SHA-256 transport receipts**:

- `metadata.json` at the README-linked commit: `433e7fc087c3ca36db19fcf661ceebe4ed2ad0b8`.
- `metadata.json` at the resolved current commit: `700c427f830c2c2319228cb92e52b4e870b7bd38`.
- `dataset-metadata.json` on the resolved branch: `0df7b815efb4cb6e93209159dcd0b2d5e3df71cd`.
- AADI preview: `496b998e890479272caa76cefdbd57caadf92424`.
- `licenses/DATA-LICENSE`: `c19565c1f23da21ad45acf2146834ec0908f758c`.

The exact connector responses for current metadata, schema and the five-line
preview are saved outside the repo at
`%TEMP%\idx-primary-packaging-a40765e73b\primary-input-connector-receipt.json`,
SHA-256 `97D8A0FDCA16D705DD85A7F431CE1739C235D0ECBB5389D71F6100FDC6494B08`.
This is a hash of saved decoded-response JSON, not the upstream CSV's original
bytes, an exchange signature or a full-release manifest. All three resources were
re-read at the resolved commit to confirm the file identities above.

**Still missing:** an explicit all-OHLC currency declaration; session-date/timezone
meaning; whether trade volume is shares or lots; raw/adjusted semantics and revision
vintage; complete coverage and transformations; and applicable upstream BEI rights.
The distinction between bid/offer lots and trade volume must not be guessed from
column names. The repository's
[DATA-LICENSE](https://github.com/Pholenk/IDX-Dataset/blob/9bb3b26bd28ab46bc2f3e74a7c03805ce053301b/licenses/DATA-LICENSE)
itself distinguishes database rights from rights over individual contents.
Its presence therefore does not settle the upstream-rights gap.

**Disposition:** a new, retrievable candidate with identifiable files and a schema;
not a substitute for the missing source declarations or authorisation. No code
from the repository was run and no data was copied into project fixtures.

## 2. A first-party permission route: TICMI/TICMIDATA

The readable [TICMI service terms](https://kampungpasarmodal.com/page/S-K-Layanan-Data)
identify general/custom data services and customer download routes. They prohibit
redistributing obtained data to third parties, commercially or non-commercially,
without TICMI permission. This is useful primary permission evidence; it does not
grant this project an account, export, API agreement or permission to pass data
to a server, cloud service or LLM. The page has no observed effective/revision
date, so applicability to a particular TICMIDATA agreement remains to be checked.

A readable [Investor Summary API page](https://doc-api.ticmidata.co.id/e/dp-investor-summary)
documents issuer/start/end-date parameters and an explicit `all` versus `reguler`
market selector, with end-of-day updates. It describes investor summaries, not
an OHLC export. The documentation root returned HTTP 403 to the web reader;
its search-index description of cooperation-agreement credentials is discovery
only. No authenticated endpoint was called and no sample OHLC response was obtained.

**Disposition:** a documented route for obtaining an authorised export and written
scope if the user later chooses it. Availability, pricing, full OHLC schema,
adjustment/vintage, local-storage/processing rights and use in this application
remain unverified. No contact, registration, subscription or purchase was made.

## 3. Search-index-only candidate: lensetek panel descriptor

The indexed [codebook URL](https://github.com/lensetek/idx-panel-data-descriptor/blob/master/data_acquisition/codebook.md)
describes IDR price fields, share volume, Yahoo/yfinance data and a 95-ticker panel;
it also says only complete histories were retained, which would entail a selection
bias requiring disclosure if confirmed. However, opening the repository, codebook
and corresponding public raw URL returned 404. The indexed citation has a Zenodo
DOI placeholder, not a resolvable release identifier. A bounded exact-title/filename
search did not locate a publisher-bound release. **These are unverified indexed
claims, not a retrieved primary release or evidence of rights.** No data was
downloaded and no metadata was adopted.

## 4. Other new routes bounded out

[Asepmology](https://www.asepmology.my.id/) was readable and describes a browser-side
XBRL financial-report converter and corporate-action calendar for research and
education. Its page also displayed a local/offline fallback after failure to reach
IDX. It supplies neither a verified OHLC export nor a complete trading calendar in
this review; a claim to use official feeds does not establish historical coverage.

A newly discovered
[IDX report specification URL](https://www.idxdata3.co.id/IDX%20Reporting%20PSPP/Revitalisasi/Specification%20Document-Report%20Revitalization_PUBLIK%20v1.0.pdf)
returned HTTP 403 to the web reader; the indexed reference to stock-summary files
is discovery only. No access gate was bypassed. Searches for a new KSEI calendar
amendment or an OJK-hosted full copy of the new II-A rule did not provide a new
verified notice chain/full rule text. Previously reviewed KSEI notices were not
re-downloaded or relabelled as new progress.

## What can resume from these findings

For a free public alternative, the Pholenk candidate now has a retrievable schema
and file identities, but still needs the missing declarations and upstream rights
before an original export can be accepted. For an authorised commercial/institutional
route, TICMI's own terms make permission a concrete next input rather than an
assumed consequence of public documentation. The unavailable lensetek release should
not receive implementation effort without a live publisher release.

These findings do not close DATA-01/02/03, IDX-02, RULE-01 or full RESEARCH-01.
The existing local read-only Yahoo/yfinance MVP remains separate. Local Data Bridge
acceptance and its currency gate are unchanged; IDX backtests remain disabled.
No accounts, credentials, outreach, broker action, dependencies, production metadata
or deployment were introduced. No Mendeley audit was repeated.
