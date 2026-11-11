# IDX Phase 2B: local reference import and source discovery

Checked 2026-11-03 (Asia/Jakarta). The importer is implemented; official complete
snapshots, licensing, historical rule coverage and corporate-action calibration
remain open. This does not enable IDX backtests or paper/live orders.

## Local import contract

`src.markets.idx_reference.load_idx_reference(path)` reads a normalized JSON file
and returns source declarations, retrieval time, usage terms, SHA-256 of the exact
file bytes, and the existing registry/calendar/rule primitive. It does not install
the artifact, download data, change a global registry or write runtime state.
Keep authorized exports outside the source tree. The hash identifies bytes; it
does not authenticate the publisher. Structural validation does not certify rights,
completeness, effective dates, board assignment or tradability.

From repository root, validate a synthetic example without network or credentials:

```powershell
$env:PYTHONPATH = "agent"
.venv/idx312/Scripts/python.exe -m src.markets.idx_reference agent/tests/fixtures/idx_reference/instruments.synthetic.json
```

The command returns JSON with `kind`, `records`, `sha256`, and
`validation: structure_only`; invalid input exits 2 without echoing private input.
For field-specific validation errors, use the Python loader locally; do not expose
raw validation errors or file contents through external logs.

All top-level fields are required, with no additional fields accepted:

- `schema_version`: integer `1` (boolean is rejected).
- `kind`: `instruments`, `calendar`, or `regular_rules`.
- `market`, `currency`, `timezone`: exactly `id_equity`, `IDR`, `Asia/Jakarta`.
- `source`: nonempty source reference, ideally document URL and revision.
- `retrieved_at`: ISO datetime with timezone offset; distinct from effective/as-of dates.
- `usage_terms`: nonempty description/reference to the applicable usage permission.
  This is an exporter declaration, not an authorization check.
- `payload`: one of the structures below. Dates use exact `YYYY-MM-DD` format.

For `instruments`, payload contains `as_of` and a nonempty `instruments` list.
Each record requires canonical `symbol` and `name`; `sector`/`industry` are optional
nonempty strings. See the [synthetic example](tests/fixtures/idx_reference/instruments.synthetic.json).
Import requires `.JK`; bare ticker resolution is only allowed later inside the
supplied registry with the exact snapshot date. Duplicate normalized symbols and
unknown fields are rejected. A current snapshot cannot prove historical membership.

For `calendar`, use this **synthetic** payload (the omitted dates below are fictional
closures, not actual IDX calendar claims):

```json
{"covered_from":"2026-11-02","covered_until":"2026-11-08",
 "complete":true,"sessions":["2026-11-02","2026-11-03"]}
```

`sessions` must be nonempty, unique and inside inclusive coverage. `complete: true`
is an explicit exporter assertion: every omitted date inside coverage is closed.
Do not make that assertion from missing OHLCV, partial exports or a holiday list
alone. Dates outside coverage raise. This is a session-date calendar, not intraday
hours, suspensions or a settlement calendar.

For `regular_rules`, use this **synthetic** payload:

```json
{"version":"SYNTHETIC-ONLY","effective_from":"2026-11-02",
 "effective_until":"2026-11-03","lot_shares":10,
 "tick_tiers":[["0","1"],["100","2"]]}
```

Prices/increments require decimal strings; JSON numbers are rejected. The existing
`IDXRegularRules` owns tier ordering, finite amounts, lot size and inclusive effective
coverage. This is only the lot/tick primitive, not a full rulebook. Fees, settlement,
price limits, board exceptions, corporate actions and suspensions remain unmodeled.
Do not use retrieval/observation dates as rule commencement dates.

## Official sources found

These are discovery results, not a completed provider integration or license review.

- [BEI daftar saham](https://www.idx.id/id/data-pasar/data-saham/daftar-saham)
  offers an Unduh control; the accessible response still shows dynamic loading.
  A complete current export has not been retrieved or reconciled. Use the official
  export to establish listing/board scope before calling a registry complete.
- [KSEI registered shares](https://web.ksei.co.id/services/registered-securities/shares?setLocale=id-ID)
  exposes codes and issuer names, including BBCA and BBRI. It can cross-check identity;
  registration is not proof of exchange tradability, board status or historical membership.
  Its nominal-value column is not a lot size. No universe is copied into fixtures.
- [KSEI PENG-0002/DIR/KSEI/0126, 8 January 2026](https://web.ksei.co.id/files/1767843003_Penyesuaian_Pengumuman_Hari_Libur_dan_Cuti_Bersama_PT_KSEI_Ta....pdf)
  references BEI Peng-00171/BEI.POP/09-2025 and lists 22 weekday closures. KSEI allows
  subsequent adjustments and specifies limited settlement services on 31 December.
  It is evidence for calendar reconciliation, not a guarantee of complete trading
  or settlement coverage through today. Check later amendments before import.
- [BEI holiday calendar](https://www.idx.co.id/id/tentang-bei/jadwal-libur-bursa)
  was discoverable but direct retrieval returned HTTP 403 in this session. No access
  control bypass or undocumented API was used. National holidays/BI calendars are
  not substituted for verified BEI session dates.
- [IDX Data Services](https://www.idx.id/en/products/idx-data-services/)
  documents subscription-based EoD products and Data Reference for statements,
  corporate actions and disclosures, with direct and redistributor access paths.
  The page announces catalogue/terms changes effective 1 January 2027. Actual API
  schemas, history, units, entitlements and permitted deployment use still need
  confirmation; no current price or license grant is inferred from public access.
- [BEI trading mechanism](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan)
  remains the discovery entry for current rule references. A current web description
  cannot establish all historical effective intervals required for backtesting.

Practical next inputs: authorized BEI instrument export with as-of/revision;
official calendar plus amendments for the requested coverage; dated decrees;
provider sample/schema covering raw versus adjusted OHLCV, volume units and actions;
and terms for the intended personal/server/redistribution use. No purchase, account
authorization or message to a provider was performed.

## Follow-up evidence: instruments, calendars and rule history

Checked again **2026-11-03, Asia/Jakarta**. Ordinary public HTTP reads and the
official download UI were attempted; no undocumented API, login, alternate test
host or access-control bypass was used. Search results from `testing`/`block`
hosts and third-party copies are not accepted as production reference artifacts.

### Instrument export

The [production list page](https://www.idx.id/id/data-pasar/data-saham/daftar-saham)
returned HTTP 200 through PowerShell `Invoke-WebRequest`. Its public HTML contains
962 `{Code:...}` records in the embedded table data, including code, issuer name,
listing date, shares and listing board. This is an observation of that response,
not a certified total or historical universe. The text extractor shows loading;
the browser UI rendered empty filters/table and clicking **Unduh** did not yield
a verified export. Embedded `downloadData` was empty. No XLSX/CSV export was
obtained, and no records were installed or copied into fixtures.

The HTML has no verified snapshot revision/as-of declaration or usage grant for
this project. Listing date and current board cannot reconstruct delisting,
renaming, suspension or historical board membership. The importer currently
accepts symbol/name and optional sector/industry, not listing/board histories;
retain an authorized original export outside the repository before deciding how
to represent those fields. Do not silently discard them to claim full support.

### Calendar revision chain

The [KSEI operational schedule index](https://web.ksei.co.id/services/schedule-c-best-instruction)
currently links its 2026 holiday item to the January adjustment below. Two official
three-page documents were read, including their page-3 date lists:

- [PENG-0005/DIR/KSEI/1025, 1 October 2025](https://web.ksei.co.id/files/Pengumuman_Hari_Libur_dan_Cuti_Bersama_PT_KSEI_Tahun_2026.pdf):
  initial KSEI notice referring to BEI Peng-00171/BEI.POP/09-2025 of 23 September 2025.
- [PENG-0002/DIR/KSEI/0126, 8 January 2026](https://web.ksei.co.id/files/1767843003_Penyesuaian_Pengumuman_Hari_Libur_dan_Cuti_Bersama_PT_KSEI_Ta....pdf):
  same BEI reference and same 22 listed weekday closures. Its operating-services
  clause instead refers to KSEI-8073/DIR/1225 and subsequent applicable changes.
  This is not evidence of a change in exchange session dates between the two lists.

Both permit later adjustment and distinguish limited year-end settlement
operations. The index linking January's PDF does not prove that no later notice
exists. Targeted official-domain searches did not establish an exhaustive
amendment register through the check date. A full BEI source document and complete
amendment reconciliation remain missing; `complete: true` is not justified.

[KSEI-1000/DIR/0226, 13 February 2026](https://web.ksei.co.id/files/Penyesuaian_Jadwal_Kegiatan_Operasional_C-BEST_dan_S-INVEST_Ramadhan_Tah....pdf)
separately adjusts C-BEST/S-INVEST cutoffs for Ramadan. It does not establish BEI
equity trading sessions or add exchange closures. Keep settlement operations,
trading sessions and instrument suspensions separate.

The [BEI calendar page](https://www.idx.id/id/tentang-bei/jadwal-libur-bursa)
now returned HTTP 200 via ordinary PowerShell retrieval, while the web reader
could not retrieve it. Its embedded content was an empty HTML body, without a
verified calendar download. This updates the earlier HTTP-403 observation; it
does not establish calendar completeness or an absence of amendments.

### Official rule-document register

The correct discovery pages are [Peraturan BEI](https://www.idx.id/id/peraturan/peraturan-bei)
(Peraturan Perdagangan tab) and [Keputusan Direksi](https://www.idx.id/id/peraturan/keputusan-direksi).
Both returned HTTP 200, and their public embedded data identifies these attachments:

- II-A **Kep-00158/BEI/10-2026**, equity trading:
  [signed attachment](https://www.idx.co.id/Media/stumk2gi/signed_peraturan_nomor_ii_a_tentang_perdagangan_efek_bersifat_ekuitas-261020.pdf).
- II-X **Kep-00140/BEI/09-2026**, special-monitoring board:
  [signed attachment](https://www.idx.co.id/Media/0dfb0coz/signed_peraturan_ii_x_perdagangan_ebe_pada_papan_pemantauan_khusus.pdf).
- **Kep-00138/BEI/09-2026**, trading guidelines:
  [signed attachment](https://www.idx.co.id/Media/5gapo3t3/signed_sk_perubahan_pedoman_perdagangan_bei.pdf).
- **Kep-00002/BEI/04-2025**, emergency continuity guidelines:
  [listed attachment](https://www.idx.co.id/Media/il0h5rov/signed_sk_perubahan_panduan_kelangsungan_perdagangan_kondisi_darurat.pdf).
- **Kep-00060/BEI/09-2025**, revocation of BEJ II-A:
  [listed attachment](https://www.idx.co.id/Media/yoopbeb2/signed_sk_pencabutan_peraturan_bej_nomor_ii_a_tentang_perdagangan_efek.pdf).

The first three exact attachment URLs returned HTTP 403 to ordinary PowerShell
requests; the web reader also failed on them and returned 403 for the emergency
guideline. The revocation attachment was discovered, not read. Document bodies,
commencement/revocation clauses and historical effective intervals therefore
remain unverified. A filename, decree month or current-page reference is not a
commencement date. In particular, a revocation of **BEJ** II-A must not be assumed
to revoke the current **BEI** II-A without reading its scope.

The current [trading mechanism page](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan)
still cites the October 2026 II-A; it is a current observation only. Searches did
not recover an authoritative full 2016/2023/2025 II-A revision chain. No historical
lot/tick JSON was created. Full texts and intervening amendments, effective dates,
board exceptions, limits, fees/taxes, settlement, suspensions and actions are still
required before simulation acceptance.

### Additional public-access checks, 2026-11-03

The KSEI operational index was checked again: its 2026 item still resolves to
the January notice. The public [today's announcements page](https://web.ksei.co.id/todays-announcements)
exposes date/filter controls but no complete amendment register in the readable
response. Targeted official-domain searches did not establish a complete revision
chain. This negative search result does not certify that no later amendment exists.
The BEI calendar page again returned HTTP 200 via ordinary PowerShell retrieval,
but its embedded page data was `data:[{}]`, with no verified calendar attachment.

The public BEI rule register also identifies three supporting documents:

- I-L **Kep-00077/BEI/05-2023**, suspensions:
  [attachment](https://www.idx.co.id/Media/hnenqs11/peraturan_nomor_i_l_suspensi_efek.pdf).
- I-I **Kep-00044/BEI/04-2024**, share splits and consolidations:
  [attachment](https://www.idx.co.id/Media/ca1ailjr/signed_peraturan_i_i_pemecahan_saham_dan_penggabungan_saham_oleh_perusahaan_tercatat_yang_menerbitkan_ebe.pdf).
- I-N **Kep-00054/BEI/05-2024**, delisting/relisting:
  [attachment](https://www.idx.co.id/Media/bmzg55k1/peraturan_i_n_pembatalan_pencatatan_delisting_dan_pencatatan_kembali_relisting.pdf).

All three exact attachments returned HTTP 403 to ordinary `Invoke-WebRequest`,
as did rechecks of II-A, II-X and the trading guidelines above. Their contents,
commencement clauses and amendments remain unverified. These references expand
the discovery register only; they cannot supply instrument events or historical
rule coverage. Requests stopped at the access restriction.

Official-domain search results also exposed differing II-A references on older
production paths/query variants. The older `.co.id/id/produk/mekanisme-dan-jam-perdagangan`
path returned 403 when read directly. Search extracts are not accepted as archived
decrees or evidence of a verified effective interval; no historical rules were
created from them.

### Provider handoff update

[Provider research](IDX_PROVIDER_RESEARCH.md) records official downloadable EoD
samples, hashes, observed schema limitations, inspected 2026 catalogue pages,
linked future 2027 documents, contract
clauses and unresolved access rights. Public sample retrieval is verified;
production entitlement, provider integration and coverage acceptance are not.

Next work can start from the exact links above: obtain readable signed rules and
the complete amendment chain; obtain the dated instrument export and retain board
history; reconcile the BEI calendar; obtain technical specifications and written
entitlement for the intended processing/display. External evidence remains the
blocker for RULE-01, DATA-01 and RESEARCH-01; their acceptance is not checked off.

## Phase 2B disposition and minimum handoff

Local reassessment **2026-11-03, Asia/Jakarta**, using the evidence already recorded
above and in [provider research](IDX_PROVIDER_RESEARCH.md). No new public-source
request was made: catalogue inspection, sample headers and exact-URL access failures
have no new input warranting repetition. This reassessment adds an intake procedure,
not new official evidence or acceptance of a provider.

The independently actionable work is complete for this increment: map evidence
gaps to the existing import contract, define minimum external inputs and distinguish
structural validation from market acceptance. There is no justified production
adapter/schema change before an authorized export and specification exist. This is
not completion of Phase 2B as a whole; open task criteria remain in
[TODO.md](../TODO.md).

### Minimum input to resume one reference import

One authorized instrument snapshot is sufficient to resume a **limited local
instrument import review**; it need not wait for a provider subscription or the full
historical rulebook. Supply these together, through a permitted local file location:

- The original BEI export or authorized provider export, with issuer code/name,
  instrument class and board scope, as-of date, source/revision and permission to
  use it for this project. Retain original listing/board/status fields. An HTML
  record count, retrieval timestamp or KSEI registration list does not establish
  these facts.
- Its coverage declaration: whole selected universe or an explicitly named subset,
  excluded classes/boards and known omissions. A subset may be structurally
  validated but cannot close the complete-universe acceptance requirement.
- A normalization mapping to schema v1: canonical four-letter `.JK` symbol, name,
  optional sector/industry, envelope source, offset-aware retrieval timestamp and
  usage-terms reference. Bare source codes require documented IDX context. Keep
  the mapping and original hash outside the source tree alongside the original.
  Do not put board/listing fields into unsupported JSON keys or silently discard
  them: document any projection separately and leave history unsupported until
  its owning model is designed from the real source.

The original export plus metadata/permission is enough to begin normalization;
the user does not have to prepare JSON or provide credentials. Record a SHA-256
for both original and normalized bytes and the transformation used. Neither hash
authenticates the publisher. No export is currently available, so this procedure
has not been executed against official data.

### Additional inputs for calendar and rules

These can arrive independently; do not synthesize one from another:

- **Calendar:** the intended inclusive date range; readable BEI base notice and
  all applicable amendments through a stated cutoff, or an authorized complete
  session export with revision/completeness evidence. Reconcile the supplied
  sessions to every notice. Only then may the exporter assert `complete: true`.
  KSEI settlement cutoffs and price gaps cannot supply missing trading dates.
- **Rules:** readable official full texts and annexes for the requested interval,
  including applicable preceding/replacement versions and commencement/revocation
  clauses. Start with the [discovered rule register](#official-rule-document-register)
  and [supporting documents](#additional-public-access-checks-2026-11-03).
  Record clause/page, effective interval, instrument/board scope, units and
  exceptions. Import only verified lot/tick values into `regular_rules`; retain
  settlement, fees/taxes, limits, suspensions and action evidence separately.
  A lot/tick import cannot close full-rulebook acceptance.

### Receipt and acceptance procedure

1. Keep original artifacts, permission documents and mappings outside the source
   tree. Record source, revision, retrieval time, coverage, usage scope and hashes;
   exclude account identifiers and credentials from reviewable summaries.
2. Review rights and semantic coverage before normalization. If absent or unclear,
   record the missing input and stop that acceptance path. Successful JSON parsing
   cannot resolve it.
3. Validate a normalized file with the existing module command in the
   [local import contract](#local-import-contract). Reconcile instrument counts,
   exclusions and duplicate identities against the original; calendar sessions
   against the complete notice chain; rule boundaries against effective clauses.
   Capture counts/hash/`structure_only` and validation outcome, without publishing
   licensed rows. Invalid input must remain rejected; fix the mapping from source
   evidence rather than insert plausible values.
4. Report structural validation, source/permission review, coverage reconciliation
   and runtime integration as separate outcomes. The CLI does not install a
   reference or connect it to tool/UI/backtest consumers. Future integration needs
   its own implementation and tests at those surfaces.
5. Leave IDX backtests disabled. Even accepted reference imports and OHLCV rights
   would still require the full historical action/rule model and BT-01/BT-02
   implementation and verification before execution support can be claimed.

Code evidence checked locally: `src/markets/idx_reference.py:75` loads bytes;
`:114`, `:132`, `:146` define the three supported payloads; `:178` owns CLI output.
`src/markets/idx.py:49` restricts resolution to the snapshot date.
`src/markets/idx_rules.py:52` and `:92` reject uncovered rule/calendar dates.
`backtest/runner.py:1765` and `backtest/engines/composite.py:32` retain execution
rejection (paths relative to `agent/`). Importer callers found are the module CLI
and its tests; there is no automatic application installation path.

Resume source retrieval only when a new official accessible attachment, supplied
authorized file, documented access route or changed access result provides a reason.
Do not repeat blocked PDF requests or the completed catalogue inspection as progress.
For provider inputs, use the [technical handoff](IDX_PROVIDER_RESEARCH.md#minimum-technical-handoff)
instead of assuming that a reference import supplies market bars or entitlement.

## Verification

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_reference.py agent/tests/test_idx_foundation.py -q --disable-socket
.venv/idx312/Scripts/python.exe -m ruff check agent/src/markets/idx_reference.py agent/tests/test_idx_reference.py
```

Tests use synthetic artifacts only. No official calendar/universe is bundled as a
default. Pending acceptance remains in [TODO.md](../TODO.md).

Previous importer session result: 435 tests passed across the importer and the foundation/classifier,
registry, currency, Yahoo/yfinance and shared-data suites listed in
[PROJECT_STATUS.md](../PROJECT_STATUS.md). Ruff lint and format checks passed for
the new Python files. Black was unavailable (`No module named black`); no package
was installed. The module command accepted the synthetic example (one record,
`structure_only`) and rejected a missing path. Full backend/frontend, safety and
network-provider probes were not repeated for this read-only import increment.

Follow-up research session: documentation only, no new runtime surface. The two
test modules above passed **102 tests** (one anyio/pytest deprecation warning);
the Ruff command passed. Local links/whitespace in the five changed Markdown files
and `git diff --check` passed. The 22 existing uncommitted code/fixture files kept
their hashes. Full regression, safety, frontend, licensed-provider integration
and deployment were not rerun. Official source downloads and access failures are
reported separately above and in the provider note.

Catalogue/access follow-up (same date): **102 passed, 1 warning** on the same two
test modules; Ruff lint and format checks passed on importer/test files. All
52 local links (including anchors) and whitespace across the five updated documents
passed validation; `git diff --check` passed. SHA-256 comparison confirmed that all
22 pre-existing uncommitted code/fixture files were unchanged. This increment
changes only those five documents and has no new runtime surface. The historical
435-test run was not repeated; full backend/frontend, safety, licensed-provider
integration and deployment were not run. No official snapshot was imported.

Local disposition increment (2026-11-03): no runtime surface, source retrieval or
new official evidence. Five documents changed; Python-project link/anchor and
whitespace validation passed (**64 local links, 0 issues**), and `git diff --check`
passed. SHA-256 comparison against the start of this increment confirmed all 22
pre-existing code/fixture files and both README files unchanged; no files were
added or removed. The 102/435-test runs and Ruff were not repeated for these prose
changes. Full backend/frontend, safety, licensed-provider integration and deployment
were not run. No staging, commit, authorized-data import or backtest activation
occurred. The completed local item is P2B-PREP; external acceptance tasks stay open.
