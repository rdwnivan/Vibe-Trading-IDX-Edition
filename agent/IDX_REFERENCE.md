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

### II-A Kep-00158/BEI/10-2026 read, 2026-11-12

Access change: the same II-A attachment URL now returns HTTP 200 to an ordinary
browser session (no CAPTCHA or challenge). A non-browser `curl` request still
receives HTTP 403 with an HTML body; no header spoofing was used to get around
it. Receipt from the in-browser fetch: `application/pdf`, **1,495,566 bytes**,
`Last-Modified: Mon, 19 Oct 2026 23:50:08 GMT`, SHA-256
`a33125be8c418e7ec0443cdf3c2e012fa66b1b993f72168cafccb6487dc05736`, 29 pages.
Text was extracted in the browser with pdf.js 4.4.168 and read for the clauses
below. The PDF bytes and extracted text were **not** saved to disk or committed.
A later check must re-download the file and compare it against this hash.

Decree (pages 1–3):

- Issued **20 October 2026**, in force **20 October 2026**, effective from that
  date. It restates the full II-A annex as one unit and **revokes
  Kep-00157/BEI/10-2026 (19 October 2026)**. Existing implementing provisions stay
  in force where they do not conflict with it.
- OJK approvals cited: S-259/PM.01/2026 (17 September 2026; II-A and II-O
  changes), S-135/D.04/2026 (18 October 2026) and S-136/D.04/2026 (19 October
  2026; temporary lower auto-rejection adjustment).
- **Transition:** the percentage auto-rejection limits in annex VI.7.1.1 are
  **not applied until 31 December 2026**. Until then a transitional, asymmetric
  schedule applies (decree item 3). Price ranges are reference-price bands:

| Reference-price band | Upper limit | Lower limit |
|---|---|---|
| Rp1–Rp10 | +Rp1 | −Rp1 |
| Rp11–Rp14 | +35% | −Rp1 |
| Rp15–Rp200 | +35% | −7% |
| >Rp200–Rp5,000 | +25% | −7% |
| >Rp5,000 | +20% | −7% |

  Orders below the Rp1 minimum price (VI.6) are also auto-rejected.

Annex clauses used for the rulebook contract (scope: equity securities on the
Regular and Cash markets unless stated otherwise):

- **Currency and day:** a price is an amount in rupiah (I.11). An exchange day
  is Monday to Friday, except national holidays and days declared exchange
  holidays (I.16). The holiday list itself is not in this document.
- **Settlement:** Regular market **T+2** (I.29); Cash market **T+0** (I.30).
- **Round lot:** trading must be in round lots or multiples; **1 round lot = 100
  shares** (VI.4.1–VI.4.2).
- **Tick size** by previous close (VI.5.2): <Rp200 → Rp1 (max step Rp10);
  Rp200–<Rp500 → Rp2 (Rp20); Rp500–<Rp2,000 → Rp5 (Rp50); Rp2,000–<Rp5,000 →
  Rp10 (Rp100); ≥Rp5,000 → Rp25 (Rp250). The maximum step does not apply to
  warrants (VI.5.3). Tick and step change in real time with the order price's
  band (VI.5.4), and a step may not exceed the auto-rejection limit (VI.5.5).
- **Minimum price:** Rp1 (VI.6).
- **Permanent auto-rejection** (VI.7.1.1, deferred to after 31 December 2026 by
  the decree): ±Rp1 for Rp1–Rp10; ±35% for Rp11–Rp200; ±25% for >Rp200–Rp5,000;
  ±20% for >Rp5,000. Warrants have their own schedule (VI.7.1.2–VI.7.1.3).
- **Volume rejection:** an order larger than **50,000 lots or 5% of listed
  shares, whichever is smaller** (VI.7.2).
- **Reference price** (VI.7.3): previous close; theoretical post-corporate-action
  price; IPO price on first trading day; or appraised fair value.
  Auto-rejection does not apply to rights (HMETD) except the minimum price (VI.7.4).
- **Regular-market sessions** in JATS time (IV.1–IV.2):
  - Monday–Thursday: pre-opening 08:45:00–08:59:59 (matching 08:58:00–08:59:59);
    session I 09:00:00–12:00:00; session II 13:30:00–15:49:59; pre-closing
    15:50:00–16:01:59 (random closing 15:58:00–15:59:59, matching
    16:00:00–16:01:59); post-closing 16:02:00–16:15:00 at the closing price.
  - Friday: same, except session I ends 11:30:00 and session II starts 14:00:00.
  - Cash market: session I only (Mon–Thu to 12:00:00, Fri to 11:30:00).
  - Negotiated market: session II ends 16:30:00.

Limits of this evidence: it fixes the regime **from 20 October 2026** only. The
text of the revoked Kep-00157 and every earlier II-A version, so the rules for
any earlier simulation date, are still unread. JATS time is not stated as WIB in
the clauses read. Holidays, special-monitoring board rules (II-X), trading
guidelines, fees/taxes, suspensions and corporate-action handling stay open. No
rulebook JSON or default `IDXRegularRules` instance was added; backtests remain
refused.

### II-X and trading guideline read, 2026-11-12

Both attachments now return HTTP 200 to the same browser session and were read
with the same in-browser method; neither file was saved to disk.

**II-X Kep-00140/BEI/09-2026**, special-monitoring board: `application/pdf`,
1,155,373 bytes, `Last-Modified: Fri, 25 Sep 2026 15:15:28 GMT`, SHA-256
`9421501e43920b04fed6148956ef7b73b8e0cb911e5da503f6718ab5930fb509`, 13 pages.

- Issued 25 September 2026, in force **28 September 2026**; amends and replaces
  the annex of Kep-00316/BEI/11-2023 (in force 1 December 2023). The new
  non-cancellation period in its call-auction sessions starts only when the PSPP
  trading-system upgrade goes live, as later announced by the exchange.
- Everything follows II-A except (II.1): the board trades by **periodic call
  auction** on Regular (T+2) and Cash (T+0) call-auction markets plus the
  negotiated market; minimum price Rp1; auto-rejection **±Rp1 for Rp1–Rp10 and
  ±10% above Rp10**; no maximum price step; the closing price is the **last
  traded price** (II.1.9).
- Regular call-auction sessions (II.1.7): Monday–Thursday five sessions starting
  09:00, 10:00, 11:00, 14:00 and 15:00, each with order entry to xx:55:00, a
  random end between xx:53:00 and xx:55:00 and price formation by xx:59:59
  (session V by 16:00:00); post-closing 16:01:00–16:15:00 at the last price.
  Friday has four sessions (09:00, 10:00–11:25, 14:00, 15:00) and the same
  post-closing. The Cash call-auction market runs the morning sessions only.
- Which listed companies are placed on the board is a listing rule (I-X), not
  read here. A `.JK` ticker does not reveal board placement.

**Trading guideline Kep-00138/BEI/09-2026**: `application/pdf`, 2,374,343 bytes,
`Last-Modified: Fri, 25 Sep 2026 15:16:00 GMT`, SHA-256
`55157e7f5eeb3d42ebff811b6661b3b9ab7f0c2621868c3db13619d0dd57db92`, 89 pages.
Only the decree, the table of contents and section IV were read.

- Issued 25 September 2026, in force 28 September 2026; revokes the guideline
  in Kep-00096/BEI/12-2022 (28 December 2022). Its recitals cite II-A
  **Kep-00136/BEI/09-2026 (21 September 2026)** and say that change adjusted the
  minimum tradable price and the auto-rejection percentages. The values before
  that change are not stated in the parts read and must not be inferred.
- **II-A version chain observed:** Kep-00136 (21 September 2026) → Kep-00157
  (19 October 2026) → Kep-00158 (20 October 2026, in force). Only Kep-00158 has
  been read. Rules for simulation dates before 20 October 2026 stay unverified.
- **Corporate actions (section IV):** covers cash, stock and interim dividends,
  rights issues, bonus shares, stock split, reverse split and merger-delisting.
  The exchange sets the trading period, adjusts the reference price and/or
  suspends market segments per security.
  - Cum/ex relative to the recording date (RD): Regular and Negotiated markets
    cum until RD−2, ex from RD−1; Cash market cum through RD, ex from RD+1.
    Selling during the ex period does not forfeit the entitlement.
  - On the Regular-market ex date, Regular and Negotiated prices are reset to the
    exchange's **theoretical post-action price** computed from the company's
    ratio. Cash-market prices are reset only at the Cash ex date. Formulas are
    set per security and action type; none are given in this section.
- Neither document ties JATS time to WIB in the parts read.

Calendar recheck: the [BEI holiday page](https://www.idx.id/id/tentang-bei/jadwal-libur-bursa)
loads in the browser but shows only its heading and the site clock, with no date
list. This is the same state as before, not an access change, and was not
pursued further.

### I-X, I-L and I-I read; II-A register check, 2026-11-12

The [Peraturan BEI](https://www.idx.id/id/peraturan/peraturan-bei) register
(Peraturan Pencatatan tab) lists these three attachments. The I-L and I-I URLs
match those recorded under the 2026-11-03 checks below:

- I-X **Kep-00139/BEI/09-2026**, placement on the special-monitoring board:
  [signed attachment](https://www.idx.co.id/Media/uw4lipoa/signed_peraturan_i_x_penempatan_pencatatan_ebe_pada_papan_pemantauan_khusus.pdf).
- I-L **Kep-00077/BEI/05-2023**, suspensions (URL above).
- I-I **Kep-00044/BEI/04-2024**, stock split and reverse split (URL above).

All three now return HTTP 200 to the browser session; ordinary `curl` without
header changes still gets HTTP 403 `text/html` for each. They were read with the
same in-browser method as II-A (fetch on the PDF's own page, pdf.js 4.4.168 from
cdnjs). No PDF bytes or extracted text were saved to disk or committed.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| I-X Kep-00139 | 1,022,101 | Fri, 25 Sep 2026 15:15:07 GMT | 7 | `e49cae1ad76c231385cd19bd391376ae97bda533a62de4345dd9d73b15d7cbe3` |
| I-L Kep-00077 | 556,258 | Wed, 31 May 2023 12:53:57 GMT | 8 | `c1948ad050ba36f7a379c829eb953a404f2c76e8069b64c672ec0aa90896c342` |
| I-I Kep-00044 | 1,396,687 | Mon, 15 Jun 2026 04:57:30 GMT | 17 | `c1334cf876203293da5fef344c87ff43a4cd6151b1940097459413c6b0c71dd1` |

All three are `application/pdf`. The I-I `Last-Modified` is two years after its
decree date; the decree and annex read carry only the April 2024 dates, so this
timestamp does not show an amendment, and none was found in the register.

**I-X Kep-00139/BEI/09-2026**, special-monitoring board placement:

- Issued 25 September 2026, in force **28 September 2026**. It revokes I-X in
  Kep-00035/BEI/06-2025 (3 June 2025; the annex header gives in force 4 June
  2025). OJK approval S-285/PM.01/2026 (24 September 2026) covers both I-X and
  II-X. Clause V.5 (lifting a suspension for a corporate action) starts only once
  a separate exchange circular is issued.
- The exchange announces placement on or removal from the board at least one
  exchange day before it takes effect (II.3) and may add a special notation to the
  company code (II.4–II.5). The exchange may change the criteria parameters by
  directors' decree with OJK approval (II.8).
- Placement criteria (III.1), any one of: disclaimer opinion on the latest audited
  statements (III.1.2); no revenue or no change in revenue versus the prior report
  (III.1.3); minerals/coal companies, or holding companies of such, with no core
  revenue by the end of the fourth financial year after listing (III.1.4); negative
  equity on the latest statements (III.1.5); a PKPU, bankruptcy or annulment
  petition against the company (III.1.8) or a material subsidiary (III.1.9) judged
  material by the exchange; other conditions set with OJK approval (III.1.11).
  III.1.1, III.1.6, III.1.7 and III.1.10 read "Dihapus" (deleted). What they said
  before deletion is not in this text and must not be reconstructed.
- Exit (IV.1–IV.3): once the condition no longer holds, or revenue is booked for
  III.1.4, on the date in the exchange announcement; the company returns to its
  previous listing board. The exchange may keep a company on the board on
  substance (IV.4).
- Suspension (V.1–V.4): after **more than one consecutive year** on the board, a
  company meeting III.1.2–III.1.5, III.1.8 or III.1.9 is suspended on all markets;
  under III.1.11 it may be suspended on markets the exchange or OJK sets. The
  suspension is lifted on exit unless another rule supports it.
- Simulation consequence: placement depends on financial-statement and court
  facts plus dated exchange announcements. Neither a ticker nor price data
  reveals it, so a board flag needs an announcement-dated event history. The
  criteria before 28 September 2026 (Kep-00035 and earlier) are unread.

**I-L Kep-00077/BEI/05-2023**, suspension of securities:

- Issued and in force **31 May 2023**. It revokes circular SE-008/BEJ/08-2004
  (27 August 2004). OJK approval S-112/PM.01/2023 (13 May 2023). No later
  amendment is listed in the register; that is not proof that none exists.
- The exchange may suspend trading on all markets or on a given market for a set
  period (II.1). Detailed explanations are delegated to an exchange circular
  (II.3), which was not read.
- Conditions (III.1): two consecutive disclaimer opinions or one adverse opinion
  (III.1.1); a company or material subsidiary files its own bankruptcy or PKPU
  petition (III.1.2); a bankruptcy ruling (III.1.3); missing, incomplete or wrong
  material disclosure (III.1.4); going-concern doubt (III.1.5); planned delisting
  (III.1.6); a rule breach carrying a suspension sanction (III.1.7); an OJK order
  (III.1.8); other conditions the exchange decides (III.1.9).
- Scope (III.2): III.1.1–III.1.5 suspend on all markets; delisting, sanctions,
  OJK orders and III.1.9 use the market set under those rules or by OJK or the
  exchange.
- Lifting (III.3–III.9): case by case, at the exchange's discretion
  ("dapat mempertimbangkan"). It can be partial: for example, the negotiated
  market can be reopened first after a disclaimer or a PKPU (III.3.1, III.4.1).
- The rule sets **no fixed suspension length** and no price or volume trigger.
- Simulation consequence: suspensions are discretionary, per market and open-ended.
  They can only come from a dated exchange suspension/lifting history, never from
  a rule formula or from missing bars.
- I-L does not address trading halts for unusual market activity (UMA); where
  such halts are governed was not checked.

**I-I Kep-00044/BEI/04-2024**, stock split and reverse split:

- Issued and in force **1 April 2024**. It revokes I-A provisions II.15
  (Annex I) and V.4, VI.2.1 and VI.3.1 (Annex II) of Kep-00101/BEI/12-2021 and
  prevails over other exchange rules on splits. Applications for in-principle
  approval filed before 1 April 2024 must also comply. It follows POJK
  15/POJK.04/2022; OJK approval S-68/PM.01/2024 (14 March 2024).
- Trading of post-split or post-reverse-split shares follows II-A's
  corporate-action trading provisions (II.7). Split execution price at least
  **Rp100** (II.8). Before applying, the 25-exchange-day average Regular-market
  close multiplied by the split ratio must be at least Rp100 (III.1). A suspended
  stock instead uses the average of daily highs over the last 12 months (III.2).
  The split ratio must not create odd lots (III.5).
- Exchange timing: in-principle decision within 9 exchange days (IV.3, VI.3);
  listing decision within 3 exchange days (IV.9, VI.10); an announcement of the
  additional listing and the **price adjustment** at least one exchange day before
  the effective date (IV.11.2, VI.12).
- Reverse split: the company appoints one buyer for odd lots (V.1) at the higher
  of the price at the reverse split or the price during the odd-lot buying period
  (V.2). The recording date for odd-lot holders is one exchange day after the
  effective date (VI.6).
- The application forms (annexes I-I.1–I-I.4) list separate dates for the last
  trade at the old nominal value on all markets, the first Regular/Negotiated
  trade at the new value and the first Cash-market trade at the new value.
- No price-adjustment formula is given; the exchange announces the adjusted price.
  Simulation consequence: adjustment factors need the announced ratio and dates
  per event. The odd-lot buyback is a cash event outside exchange matching. Rules
  before 1 April 2024 (I-A Kep-00101/BEI/12-2021 provisions) are unread.

**II-A Kep-00136 and Kep-00157 search:** the
[Keputusan Direksi](https://www.idx.id/id/peraturan/keputusan-direksi) register
filter, checked by first confirming it finds Kep-00138, returns no rows for
`00136`, `00157` or `00158`. In the Peraturan BEI register, all three tabs
return nothing for `00136`. The only II-A entry is Kep-00158/BEI/10-2026. The
`00157` hit is **II-H Kep-00157/BEI/10-2024**, a different document with the
same sequence number in another year, not the II-A Kep-00157/BEI/10-2026 that
Kep-00158 revokes. The site-wide search for each full number returns only
unrelated fuzzy matches. Neither text is publicly listed, so nothing about their
content is recorded. Rules for simulation dates before 20 October 2026 depend on
obtaining them, or the versions before them, another way.

Limits of this evidence: each document fixes its own regime from its stated
in-force date only. Prior I-X versions, the I-L and I-X implementing circulars,
I-A before 2024, POJK 15/POJK.04/2022, the I-N delisting rule, II-A Kep-00136
and Kep-00157, holidays, JATS–WIB mapping, fees and taxes stay open. No rulebook
JSON, `IDXRegularRules` default or code change was made; backtests stay refused.

### Fees, JATS time and I-N read, 2026-11-12

Same browser method and access state as the section above: HTTP 200 in the
browser, `curl` without header changes HTTP 403 `text/html`. Nothing was saved
to disk or committed.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| Kep-00120/BEI/08-2026 (joint BEI/KPEI/KSEI) | 1,061,693 | Fri, 14 Aug 2026 15:03:55 GMT | 7 | `a4a98ab4df4b3920d338607531317593200b0dbdc627f7ddb854a824770b7c27` |
| I-N Kep-00054/BEI/05-2024 | 1,682,750 | Mon, 06 May 2024 13:10:53 GMT | 17 | `a2af2c4079ba8f71e1c67672de570dab89fb8ed0803a46ae264d8892838fd1e1` |

II-A Kep-00158 and guideline Kep-00138 were downloaded again. Both SHA-256
values match the ones recorded above, so the files are unchanged.

**Fee register search.** Keputusan Direksi filters for `Biaya`, `Transaksi Bursa`,
`Levy` and `Pungutan`, plus `Biaya` and `Pungutan` across all three Peraturan BEI
tabs, find no decree that sets a Regular-market base fee. They find only fee
reliefs and exemptions: Negotiated-market relief (Kep-00120), liquidity providers
(Kep-00125, Kep-00053) and ETFs (Kep-00089, Kep-00094, Kep-00098). The base
exchange fee is set in II-A itself.

**II-A Kep-00158 chapter XI (transaction fees):**

- The exchange member pays the exchange **0.018% of each transaction's value** on
  the Regular and Cash markets, excluding clearing and settlement (XI.1.1). The
  Negotiated-market fee follows an exchange decree (XI.1.2). The member pays a
  monthly minimum of Rp20,000,000 (XI.1.3), which is a member-level charge, not a
  per-trade cost.
- VAT and other taxes are added and collected through the exchange (XI.2). No
  VAT rate is stated.
- XI.3–XI.7 cover the member's monthly payment, late fines and suspension of the
  member. These do not apply to a simulated investor.
- This is the exchange's charge to the member. What a broker charges a client is
  a separate commercial term and is not set here.

**Kep-00120/BEI/08-2026** (joint decree with KEP-081/DIR/KPEI/0826 and
KEP-0045/DIR/KSEI/0826), Negotiated-market fee relief:

- Issued and in force **14 August 2026**. It revokes the joint decree
  Kep-00052/BEI/08-2020 (18 August 2020).
- Negotiated-market cost is **0.03%** of transaction value: exchange 0.018%,
  KPEI clearing 0.009%, KSEI settlement 0.003% (item 1). Relief of 10–25% applies
  per transaction of at least Rp250 billion, when the price is at or above the
  Regular-market lower auto-rejection limit (item 2).
- Its recitals cite the sources for the clearing and settlement parts. KPEI II-5
  (KEP-031/DIR/KPEI/0626, 15 June 2026) X.1.2 sets **0.009% for the Negotiated
  market**. KSEI VI-A (KEP-0017/DIR/KSEI/0422, 26 April 2022) 4.6.1 sets
  **0.003% of the cumulative monthly transaction value** for equity settlement.
  Neither KPEI nor KSEI rule was read. The Regular-market KPEI clearing fee is
  not stated in anything read and must not be assumed from the Negotiated figure.
- **Conflicting reference to an earlier II-A:** the recitals cite II-A as the
  annex of **Kep-00003/BEI/04-2025 (8 April 2025)**. The Peraturan BEI register,
  however, lists Kep-00003/BEI/04-2025 as **II-Q**, on liquidity-provider
  activity, in the Peraturan Perdagangan tab. No II-A entry under that number
  appears in any tab. Either one decree covered both rules, or one of the two
  sources is wrong. Neither the II-Q attachment nor any 2025 II-A text was read,
  so this is not resolved. Kep-00003 is **not** added to the II-A version chain.
  *Resolved later the same day:* BEI used the number twice; see
  [the II-A version chain follow-up](#ii-a-version-chain-trading-halts-and-share-sale-tax-2026-11-12).
- Its deadlines are written as "pukul 17:00 WIB" (items 6 and 9). These are
  administrative deadlines in a different document. They do not define JATS time.

**JATS time.** II-A I.40 defines JATS time only as "the time shown on JATS".
A text search of all 89 pages of guideline Kep-00138 (143,599 extracted
characters, no blank pages) finds no `WIB`, `UTC`, `GMT` or "zona waktu". The
BEI website clock shows WIB. No rule read ties session times to WIB/UTC+7, so an
`Asia/Jakarta` session clock stays a modelling assumption.

Wording difference: guideline Kep-00138 says the random close falls between
**15:58:00 and 16:00:00**, while II-A Kep-00158 IV.1 gives 15:58:00–15:59:59. The
guideline came into force before the current II-A, and which wording governs was
not resolved. A daily-bar simulation is not affected.

**I-N Kep-00054/BEI/05-2024**, delisting and relisting:

- Issued and in force **6 May 2024**. It revokes BEJ I-I Kep-308/BEJ/07-2004
  (19 July 2004) and BES I.A.7 SK-023/LGL/BES/XI/2004 (25 November 2004). OJK
  approval S-89/PM.01/2024 (7 April 2024). For voluntary delistings already
  suspended before 6 May 2024, the delisting fee is 2× the last annual listing
  fee instead of 5× (decree item 2).
- Grounds (III.1): the company's request, an OJK order, or an exchange decision.
  The exchange can decide when there is a significant adverse condition without
  adequate recovery (III.1.3.1), when listing requirements are no longer met
  (III.1.3.2), or after **at least 24 months of suspension** on the Regular and
  Cash markets or all markets (III.1.3.3).
- Voluntary delisting (III.3): listed at least 5 years, fee 5× the last annual
  listing fee. The exchange suspends the shares on all markets once the plan is
  disclosed (III.3.2.3). Delisting follows within 14 working days of the OJK
  letter, and the exchange announces it at least one exchange day before the
  effective date.
- Exchange-decided delisting (III.5): after **6 consecutive months** of
  suspension, the exchange announces potential delisting and repeats the notice
  every June and December (III.5.3). A delisting decision is final, and the public
  is told by the start of session I on the next exchange day (III.5.4.1–III.5.4.2).
  The company must disclose its buyback plan within 30 days, and delisting takes
  effect **6 months after that period** (III.5.4.3–III.5.4.4), on the next exchange
  day if that is a holiday (III.5.4.6). OJK can set another date (III.5.4.5).
- The exchange may temporarily lift a suspension on the Negotiated market only
  (II.8). Relisting is possible no earlier than 6 months after delisting, under the
  same company code (V.2, V.4).
- Simulation consequence: a delisted stock's last tradable day and any buyback
  exit come from dated announcements. A survivorship-safe universe needs those
  events. Long runs of missing bars cannot stand in for them.

Limits of this evidence: the Regular-market KPEI clearing fee, the KSEI and KPEI
rules, the VAT rate, the final income tax on share sales (a government tax rule,
not an exchange rule) and broker commission stay unread. Earlier II-A versions,
including whether Kep-00003/BEI/04-2025 contains one, the official holiday list
and the JATS–WIB mapping also stay open. No rulebook JSON, `IDXRegularRules` default or code change was made;
backtests stay refused.

### II-Q Kep-00003 and KSEI VI-A read; KPEI not reached, 2026-11-12

Same in-browser method; no file was saved to disk or committed.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| BEI II-Q Kep-00003/BEI/04-2025 | 1,009,054 | Wed, 30 Apr 2025 17:28:38 GMT | 8 | `134c9d9b4d6d638a119744653b72037d74bfae7a0d6de4aa0517ba1c7cd66932` |
| KSEI KEP-0017/DIR/KSEI/0422 (decree) | 63,856 | Tue, 26 Apr 2022 07:46:55 GMT | 3 | `e78c859264b6fde8577dab288b8ef8f7527efb3324872b3e2d97b62456bf4e89` |
| KSEI VI-A annex to KEP-0017 | 274,294 | Tue, 26 Apr 2022 07:47:31 GMT | 10 | `ea18c8940b5953cf5d490c91e2036af50505bf82910de767ea05f32eff30addf` |
| KSEI fee list "Daftar Biaya Layanan Jasa" | 441,769 | Wed, 05 Oct 2022 10:00:52 GMT | 10 | `71b71340b0860374c73ff4a79cc112c0dd1210580f1cb82bb658f2cbe83d9c12` |

The II-Q URL is
[signed attachment](https://www.idx.co.id/Media/4cmfnb3n/signed_peraturan_nomor_ii-q_tentang_kegiatan_liquidity_provider_saham_di_bursa.pdf)
(`curl` 403, browser 200). The KSEI files come from the
[Peraturan KSEI](https://web.ksei.co.id/regulations/csd-regulation) and
[fee](https://web.ksei.co.id/regulations/services_fee) pages; the VI-A annex
also returns HTTP 200 to plain `curl`.

**II-Q Kep-00003/BEI/04-2025 resolves its identity, not the II-A citation.**

- The decree covers only II-Q, on liquidity-provider activity. It was issued
  **30 April 2025** and in force **8 May 2025**; clause IV.4 waits for a later
  exchange announcement. It neither enacts nor amends II-A. Its only II-A
  reference (II.1) says that liquidity-provider quotes follow II-A on trading,
  settlement, surveillance, fees and halts.
- Kep-00120's recital, "II-A … Kep-00003/BEI/04-2025 dated 8 April 2025", shares
  this document's number but not its rule or date. *Corrected later the same
  day:* BEI's own sources show that the number was used twice, once for an II-A
  amendment dated 8 April 2025. See
  [the next follow-up](#ii-a-version-chain-trading-halts-and-share-sale-tax-2026-11-12).
- Incidentally, its recitals cite an earlier I-X version, **Kep-00076/BEI/06-2024
  (20 June 2024)**, with liquidity-provider exit routes in IV.1.4–IV.1.5. That
  version is unread. Kep-00035/BEI/06-2025, which the current I-X revokes, came
  later.

**KSEI VI-A (KEP-0017/DIR/KSEI/0422)**, settlement fee:

- Issued and effective **26 April 2022**, with OJK approval S-373/PM.21/2022
  (19 April 2022). The BI-FAST withdrawal fee applies from 1 May 2022. It revokes
  fee items 1.5, 2.1.4 and 3.6.4 of the KSEI central-custody rule
  (KEP-0013/DIR/KSEI/0612). This is the version Kep-00120 cites.
- **4.6.1:** the settlement fee for exchange transactions in equity securities,
  including structured warrants and exchange-traded fund units, is **0.003% of the
  cumulative monthly value of exchange transactions**. Debt securities pay 20% of
  the exchange fee instead (4.6.2). The fee is charged to the exchange member and
  collected through the exchange (4.6.3). It is not limited to the Negotiated
  market.
- The fee list repeats 0.003% (item 13). The fee page, however, says the list is
  based on VI-A **Kep-0005/DIR/KSEI/0121**, while the register gives KEP-0017 as
  the current VI-A. The list itself carries no decree number or date, so the label
  conflict stays open. It does not change the 0.003% figure. The register shows no
  VI-A amendment after KEP-0017; that is not proof that none exists.

**KPEI not reached.** Navigating the built-in browser to `www.kpei.co.id` was
refused ("denied or failed"). It was not retried and no other route was tried.
KPEI II-5 (KEP-031/DIR/KPEI/0626) and its **Regular-market clearing fee** stay
unread. The 0.009% figure that Kep-00120 cites is for the Negotiated market only.

Cost picture so far, for a member's equity trade on the Regular market: exchange
0.018% per transaction (II-A XI.1.1) plus KSEI settlement 0.003% of monthly
cumulative value (VI-A 4.6.1), plus a KPEI clearing fee that is still unknown,
plus VAT at an unstated rate. These are exchange, clearing and depository
charges billed to the member. Whether and how a broker passes them to a client
is a commercial term. The final income tax on share sales is a government rule
and still unread. No fee model is defined from this partial picture.

### KPEI retry and II-A Kep-00055/BEI/03-2023 read, 2026-11-12

**KPEI is unreachable from this network, not refused.** After the user allowed
the site, the built-in browser still failed on both `www.kpei.co.id` and
`kpei.co.id`. Plain `curl` explains why: `www.kpei.co.id` does not resolve
(curl exit 6; `nslookup` times out), and `kpei.co.id` resolves to
202.155.72.168 but the connection times out (curl exit 28). `www.idx.id`
answers normally from the same machine. KPEI II-5 therefore stays unread.

A web search limited to official domains returned KPEI's
[equity page](https://www.kpei.co.id/page/ekuitas) and
[equity rules page](https://www.kpei.co.id/regulation/peraturan-ekuitas). The
search engine's summary said the equity page lists a Regular-market clearing fee
of **0.009%** per transaction with a monthly minimum of Rp10,000,000. Neither
page was opened, so this is a **search-snippet claim, not evidence**. It is
recorded only as a pointer for the next KPEI read and is not used anywhere.

**II-A Kep-00055/BEI/03-2023**, found through the same search, read in the
browser:
[signed attachment](https://idx.co.id/Media/y0vjxqur/signed_peraturan_ii_a_perdagangan_efek_bersifat_ekuitas.pdf)
(`curl` 403, browser 200). The current Peraturan BEI register does not list it;
it is an older file still served on the official domain.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| II-A Kep-00055/BEI/03-2023 | 771,686 | Thu, 30 Mar 2023 13:13:23 GMT | 30 | `c62046378cfa889a0ffabcfd92cef87d399a3b6e0e34d68b5ca83fe40ea363c8` |

Decree:

- Issued 30 March 2023, in force **3 April 2023**. It sets the II-A annex and
  **revokes II-A Kep-00061/BEI/07-2021** (23 July 2021, in force 26 July 2021).
  The annex header reads "Kep-00061/BEI/07-2021 … amended by Kep-00055/BEI/03-2023".
  OJK approvals cited: S-1153/PM.21/2020 (16 November 2020) and S-52/PM.01/2023
  (29 March 2023).
- Context: it ends the COVID-19 relaxations (POJK 7/POJK.04/2021 as amended,
  expiring 31 March 2023). It restores the trading hours in IV.2–IV.4 and the
  V.12 reporting deadline from its in-force date.
- **Auto-rejection was normalised in stages** (decree item 4). The upper limits
  were already +35% (Rp50–Rp200), +25% (>Rp200–Rp5,000) and +20% (>Rp5,000).
  The lower limit changed by period:

| Period | Lower limit |
|---|---|
| 3 April – 31 May 2023 | −7% |
| 5 June – 1 September 2023 | −15% |
| From 4 September 2023 | symmetric, per annex VI.7.1.2 (−35/−25/−20%) |

  The decree does not cover 1–4 June 2023, and nothing is assumed for it.
- Reference-price provisions VI.7.3 and VI.9.1–VI.9.2 wait for a later exchange
  date (item 5). Until then the reference price is the previous close, the
  theoretical post-corporate-action price, the IPO price, or an appraised fair
  value.

Annex clauses (Regular and Cash markets) that differ from or match Kep-00158:

- **Minimum price Rp50** for shares (VI.6.1) and Rp1 for rights (HMETD,
  VI.6.2). VI.6.3 sets Rp1 for one more class, which was cut off in the extract
  read. Kep-00158 has Rp1 for shares, and the bands below Rp50 that Kep-00158
  defines do not exist here.
- Round lot 100 (VI.4.1–VI.4.2), the same as Kep-00158.
- Tick sizes Rp1/2/5/10/25 with maximum steps Rp10/20/50/100/250 at the
  200/500/2,000/5,000 previous-close breaks (VI.5.2), the same as Kep-00158.
- Volume rejection above 50,000 lots or 5% of listed shares, whichever is
  smaller (VI.7.2), the same as Kep-00158.
- Settlement: Regular T+2 (I.27); Cash same day (I.28).
- Sessions follow JATS time (IV.1). Mon–Thu: pre-opening 08:45:00–08:59:00, with
  price formation 08:59:01–08:59:59; session I 09:00:00–12:00:00; session II
  13:30:00–15:49:59; pre-closing order entry 15:50:00–16:00:00, with a random
  close between 15:58:00 and 16:00:00 and price formation 16:00:01–16:00:59;
  post-closing 16:01:00–16:15:00. Friday: session I ends 11:30:00 and session II
  starts 14:00:00. These pre-opening and pre-closing boundaries differ from
  Kep-00158 IV.1–IV.2.
- Exchange fee **0.018%** per transaction on Regular and Cash, excluding
  clearing and settlement (XI.1.1), the same as Kep-00158.

Version chain now evidenced by read documents: Kep-00061/BEI/07-2021 (in force
26 July 2021; annex not read separately) → **Kep-00055/BEI/03-2023 (in force
3 April 2023)** → … → Kep-00136 (21 September 2026, unread) → Kep-00157
(19 October 2026, unread) → Kep-00158 (in force 20 October 2026). Whether any
version came between Kep-00055 and Kep-00136, and so **when the Kep-00055 regime
ended**, is not shown. Kep-00055 values therefore apply from 3 April 2023 only
up to an end date that is still unknown. They must not be extended to later dates
or backfilled before 3 April 2023.

Limits of this evidence: the KPEI clearing fee, the end of the Kep-00055
interval, the texts of Kep-00136 and Kep-00157, the VAT rate, the final income
tax on share sales, the holiday list and the JATS–WIB mapping stay open. No
rulebook JSON, `IDXRegularRules` default or code change was made; backtests stay
refused.

### II-A version chain, trading halts and share-sale tax, 2026-11-12

These leads came from web searches limited to official domains. Every document
below was opened and read in the browser; search summaries are not used as
evidence. Nothing was saved to disk or committed. The `idx.co.id` files return
HTTP 403 to plain `curl` and 200 in the browser; the JDIH BPK file returns 200 to
both.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| II-A Kep-00061/BEI/07-2021 | 615,993 | Fri, 23 Jul 2021 12:46:30 GMT | 32 | `46301c47ca438db434b5247228274ee918611a40c6864070a53e94e083d060f6` |
| IDXbell newsletter, edition 27 (January 2025) | 6,268,404 | Thu, 23 Jan 2025 08:21:41 GMT | 22 | `93e79bd39667dd57202dd6aa04f470d4640faaf846a2fdb2ff13b736280212c2` |
| BEI governance report 2025 | 7,010,018 | Thu, 30 Apr 2026 09:41:27 GMT | 88 | `ea7cb5033e7256c758c5fcbb3b369d192bf5f4d3871757d1bfdf649c02f2c1ad` |
| Emergency trading-continuity guideline Kep-00002/BEI/04-2025 | 781,838 | Mon, 07 Apr 2025 23:44:27 GMT | 8 | `59b34aecf2358cbf6c947c5c5ff4f213c9cece7baad0631cd0acf4dc8858f83a` |
| I-X Kep-00076/BEI/06-2024 | 815,719 | Thu, 20 Jun 2024 14:31:25 GMT | 10 | `aafc7a2837ad310077b6dfd1119631429c8aa5aa3cc26d850d29baea9595fade` |
| PP 41/1994 (JDIH BPK) | 36,705 | Mon, 04 Dec 2017 07:16:44 GMT | 7 | `7feda5bbae40f475605001e84c256eb8ee9fc4202f0d8b6048700ce66cb2ed5b` |
| PP 14/1997 (JDIH BPK) | 39,682 | Wed, 29 Nov 2017 01:55:40 GMT | 8 | `1c97d344d0308c2ff8d843111bb3d13b90114c5b65c4fcd1b9ec7c18de86538c` |

URLs: [II-A Kep-00061](https://www.idx.co.id/media/10022/peraturan_ii_a_perdagangan_efek_bersifat_ekuitas.pdf),
[IDXbell 27](https://www.idx.co.id/Media/y5agatkd/idxbell-edisi-27-januari-2025.pdf),
[governance report 2025](https://www.idx.co.id/media/bpgni45v/laporan-tata-kelola-bei-tahun-2025.pdf),
[Kep-00002 guideline](https://www.idx.co.id/Media/il0h5rov/signed_sk_perubahan_panduan_kelangsungan_perdagangan_kondisi_darurat.pdf),
[I-X Kep-00076](https://www.idx.co.id/Media/gkbivhjb/peraturan_i_x_penempatan_pencatatan_ebe_pada_papan_pemantauan_khusus_signed.pdf),
[PP 41/1994](https://peraturan.bpk.go.id/Details/57263/pp-no-41-tahun-1994),
[PP 14/1997](https://peraturan.bpk.go.id/Details/56237/pp-no-14-tahun-1997).

**Correction: Kep-00003/BEI/04-2025 is two documents.** The governance report
(p. 25) lists both "II-A … Kep-00003/BEI/04-2025 dated 8 April 2025" and "II-Q …
Kep-00003/BEI/04-2025 dated 30 April 2025". The signed Kep-00002 guideline cites
II-A as "Kep-00003/BEI/04-2025 dated 8 April 2025 on the amendment of II-A", the
same citation as Kep-00120. Three BEI sources therefore agree that an **II-A
amendment numbered Kep-00003 and dated 8 April 2025** exists, alongside the II-Q
decree with the same number. Its signed text was not found; a search turned up
only an unsigned "konsep bersih" draft, which is not used. The earlier note that
the Kep-00120 citation "does not match" is withdrawn.

**II-A versions now evidenced**, by in-force date:

| Version | In force | Evidence | Text read |
|---|---|---|---|
| Kep-00025/BEI/03-2020 | 12 March 2020 (date given; in-force date not shown) | Kep-00108 recital and revocation | no |
| Kep-00108/BEI/12-2020 | 7 December 2020 (issued 4 December 2020) | signed decree | yes, decree and annex ([read later](#vat-basis-ii-a-kep-00108-and-i-x-kep-00315-read-2026-11-12)) |
| Kep-00061/BEI/07-2021 | 26 July 2021 | signed decree | yes, decree |
| Kep-00055/BEI/03-2023 | 3 April 2023 | signed decree | yes |
| Kep-00196/BEI/12-2024 | 9 December 2024 (issued 6 December 2024) | IDXbell newsletter; Peng-00251/BEI.POP/12-2024 ([read later](#bei-calendar-amendments-ii-a-context-and-vat-exemptions-2026-11-12)) | no |
| Kep-00003/BEI/04-2025 | 8 April 2025 (date given; in-force date not shown) | governance report, Kep-00002, Kep-00120 | no |
| Kep-00136/BEI/09-2026 | 21 September 2026 (date given) | Kep-00138 recital | no |
| Kep-00157/BEI/10-2026 | 19 October 2026 (date given) | Kep-00158 decree | no |
| Kep-00158/BEI/10-2026 | 20 October 2026 | signed decree | yes |

The regime of Kep-00055 therefore ended no later than 9 December 2024. Whether
another version came between 3 April 2023 and 9 December 2024 is not shown. The
newsletter says only that Kep-00196 widened the pre-opening session from LQ45
stocks to all stocks on the Main, Development and New Economy boards. Its other
contents and the 8 April 2025 changes are unread and must not be guessed. The
date of the 8 April 2025 version matches the emergency auto-rejection change
below, but its values were not read.

**Kep-00061/BEI/07-2021**, decree items read:

- Issued 23 July 2021, in force 26 July 2021; revokes II-A Kep-00108/BEI/12-2020
  (4 December 2020).
- Trading hours in the annex (IV.2–IV.4) were deferred. Two temporary schedules
  applied instead, Monday to Friday alike:
  - 26 July – 3 December 2021: pre-opening 08:45:00–08:55:00, session I
    09:00:00–11:30:00, session II 13:30:00–14:49:59, pre-closing 14:50:00–15:00:00,
    post-closing 15:05:00–15:15:00.
  - From 6 December 2021 "until set later by the exchange": pre-opening to
    08:59:00, the same sessions, random close 14:58:00–15:00:00, post-closing
    15:01:00–15:15:00.
  - Kep-00055 restored the annex hours from 3 April 2023. The days 4–5 December
    2021 were a weekend.
- Market orders took effect on 6 December 2021.
- Auto-rejection in the annex (VI.7.1.2) was deferred. A temporary
  **asymmetric** schedule applied instead: +35/+25/+20% upper and **−7% lower**
  for every price band. This is consistent with the 3 April – 31 May 2023 stage
  of Kep-00055. Minimum share price Rp50 (VI.6.1).
- Decree item 3b sets a reporting deadline of "16:00:00 WIB". That is an
  administrative deadline, as in Kep-00120, and does not define JATS time.

**Emergency trading-continuity guideline Kep-00002/BEI/04-2025:**

- Issued and in force **8 April 2025**, on an OJK order (S-28/D.04/2025, 7 April
  2025) to adjust trading-halt limits and auto-rejection. It revokes the
  guideline in Kep-00024/BEI/03-2020 (10 March 2020). It is listed in the current
  Keputusan Direksi register. No later version was found; that is not proof that
  none exists.
- A trading halt keeps open orders in JATS, which members may withdraw. A trading
  suspend withdraws them all automatically (III.1). A halt can become a suspend
  for the rest of the day (III.2).
- **Index-drop thresholds (III.3.8):** if the composite index (IHSG) falls more
  than **8%**, trading halts for 30 minutes. A further fall past **15%** brings
  another 30-minute halt. A further fall past **20%** suspends trading to the end
  of the session, or longer with OJK approval or order. The base the percentage
  is measured from is not defined in the text read.
- Other triggers (III.3.1–III.3.7) are operational: disasters, JATS faults, more
  than 30 members disconnected or members holding more than 60% market share,
  power, and clearing or settlement failures.
- Simulation consequence: market-wide halts are dated events. They can be
  reconstructed from announcements or intraday data, not from daily bars. The
  thresholds before 8 April 2025 (Kep-00024/2020) are unread.

**I-X Kep-00076/BEI/06-2024**, special-monitoring placement (an earlier version):

- Issued 20 June 2024, in force 21 June 2024; revokes I-X Kep-00315/BEI/11-2023
  (1 December 2023). Free-float criteria phase in on 2 July 2024 (Main and
  Development boards) and 31 October 2025 (Acceleration board). The
  liquidity-provider exit routes wait for the liquidity-provider rules (II-Q, in
  force 8 May 2025).
- Placement criteria in this version include **III.1.1**: over the last 3 months,
  an average price below **Rp51**, average daily value below Rp5,000,000 **and**
  average daily volume below 10,000 shares. Other criteria are **III.1.6** (no
  longer meets continued-listing requirements, apart from free float) and
  **III.1.7** (average daily value below Rp5,000,000 and volume below 10,000
  shares over 3 months). These carry the numbers of three items that Kep-00139
  marks "Dihapus". Kep-00035 may have renumbered the criteria, so the numbers
  are not proof that these are the deleted texts.
- What Kep-00035/BEI/06-2025, the version between Kep-00076 and Kep-00139, said
  is unread. So it is not known whether these criteria still applied from 4 June
  2025 to 27 September 2026. They are evidenced only from 21 June 2024 until an
  unknown date no later than 4 June 2025.

**Final income tax on share sales (PP 41/1994 as amended by PP 14/1997):**

- PP 41/1994 was enacted 23 December 1994 and **applies from 1 January 1995**
  (Art. 5). Income from selling shares on the exchange bears a **final** income
  tax (Art. 1(1)). The exchange operator collects it on every sale, pays it
  monthly and reports it (Art. 2). Its explanatory note includes the parallel
  exchange. Because the tax is final, it is neither combined with other income
  nor credited in the annual return.
- PP 14/1997 (in force 29 May 1997, on promulgation) replaces Art. 1(2): the tax
  is **0.1% of the gross sale value** of every share sale. Founder shares instead
  bear a one-off additional 0.5% of the share value: the year-end 1996 closing
  price, or the IPO price for listings after 1 January 1997 (Art. 1A, 2A). A
  founder may opt for normal income tax instead (Art. 3A). The original
  founder-share surcharge of 5% of each sale (PP 41/1994 Art. 1(2)b) was replaced.
- JDIH BPK lists PP 41/1994 as "Berlaku" (in force), amended only by PP 14/1997.
  The implementing Minister of Finance decree and any later change through income
  tax law amendments were not checked.
- Simulation consequence: a **sell-side 0.1% of gross proceeds**, charged whether
  the trade gains or loses. It applies to ordinary shares on the exchange. The
  founder surcharge is not a per-trade cost.

**Still unverified:** the VAT rate on exchange fees (not checked), the KPEI
clearing fee, broker commission, and the texts of II-A Kep-00108, Kep-00196,
Kep-00003 (8 April 2025), Kep-00136 and Kep-00157. I-X Kep-00315 and Kep-00035,
the official holiday list and the JATS–WIB mapping are also unread. No rulebook
JSON, `IDXRegularRules` default, fee model or code change was made; backtests
stay refused.

### VAT basis, II-A Kep-00108 and I-X Kep-00315 read, 2026-11-12

Leads came from web searches limited to official domains; each document below
was opened and read. Search summaries are not used as evidence. Text was
extracted in the browser with pdf.js 4.4.168 from cdnjs, except UU 42/2009: the
built-in browser refused `peraturan.bpk.go.id` this time, so that file was
fetched with plain `curl` into `%TEMP%` and read with the project's `pypdf`.
Nothing was saved to the repository. The two `idx.co.id` files return HTTP 403
`text/html` to plain `curl` and 200 in the browser.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| II-A Kep-00108/BEI/12-2020 | 676,694 | Fri, 04 Dec 2020 07:49:28 GMT | 32 | `659b7a2ff2aaa3336439cc41abe3ef5832e312b93dec77788b617183a15474cd` |
| I-X Kep-00315/BEI/11-2023 | 835,485 | Fri, 01 Dec 2023 07:51:55 GMT | 10 | `b12a82be7017eb3a9b53ce12b7c7288ddecd16e7d4ba838c9b121850759b2676` |
| BEI announcement Peng-SPT-00003/BEI.PP1/06-2025 et al. | 773,295 | Mon, 23 Jun 2025 11:20:55 GMT | 4 | `565bfd2be8cb55bcf6aafade07ef457c9b415ad845a697beb0a71aec43eff2e2` |
| OJK/SRO joint press release SP 21/DHMS/OJK/III/2020 | 145,784 | Mon, 23 Mar 2020 01:52:22 GMT | 2 | `5b40a1d062dc7573eab0c0be269121ff159fbb6f1ee1968e732728401e3aac40` |
| UU 7/2021 (HPP), JDIH Kemenkeu | 10,263,030 | Fri, 10 Nov 2023 09:56:38 GMT | 224 | `4e4be3e276bf327e6e9e8a4a031838f572feb4014c2476f6cea0d9a54dd38d5b` |
| PMK 131/2024, JDIH Kemenkeu | 398,305 | Wed, 01 Jan 2025 04:46:01 GMT | 6 | `bd2b45907407c6640a6313500adb87c5a95854d79df3b53c1f5064ace71305cd` |
| UU 42/2009, JDIH BPK | 263,002 | Tue, 05 Sep 2017 04:53:44 GMT | 73 | `17bb1512014f0eda9364f84baa33d0439633ac1cdd48801c134d105e6b58d444` |

All seven returned HTTP 200 `application/pdf` to the fetch that was hashed.
URLs: [II-A Kep-00108](https://www.idx.co.id/media/9410/perubahan_peraturan_ii_a_perdagangan_efek_bersifat_ekuitas.pdf),
[I-X Kep-00315](https://www.idx.co.id/Media/hqydaod4/peraturan_i_x_penempatan_pencatatan_ebe_pada_papan_pemantauan_khusus011223.pdf),
[June 2025 announcement](https://idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_EREP/202506/293cdf91c4_bae7069f6b.pdf),
[OJK/SRO press release](https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Documents/Pages/Siaran-Pers-Bersama-OJK-dan-SRO-Jaga-Keberlangsungan-Aktivitas-Perdagangan-Bursa-Efek-yang-Teratur/SPB%20-%20OJK%20dan%20SRO%20Jaga%20Keberlangsungan%20Aktivitas%20Perdagangan%20Bursa%20Efek%20yang%20Teratur.pdf),
[UU 7/2021](https://jdih.kemenkeu.go.id/api/download/a9faab97-aca7-4f87-9fdc-faa8123d1454/7TAHUN2021UU.pdf),
[PMK 131/2024](https://jdih.kemenkeu.go.id/api/download/ad276b82-94bd-4197-b409-af33e2842cd6/2024pmkeuangan131.pdf)
([JDIH BPK entry](https://peraturan.bpk.go.id/Details/311485/pmk-no-131-tahun-2024)),
[UU 42/2009](https://peraturan.bpk.go.id/Details/38787/uu-no-42-tahun-2009).

**VAT on exchange, clearing and depository fees.** II-A XI.2 (both Kep-00108 and
Kep-00158) adds VAT to the exchange fee and has the exchange collect it, without
a rate. The rate comes from the VAT law (UU 8/1983 as amended):

| Period | Statutory rate | Tax base for an ordinary taxable service | Effective share of the fee | Source |
|---|---|---|---|---|
| 1 April 2010 – 31 March 2022 | 10% | the fee | 10% | UU 42/2009 art. I item 8 (Pasal 7(1)); in force 1 April 2010 (Pasal II) |
| 1 April 2022 – 31 December 2024 | 11% | the fee | 11% | UU 7/2021 Pasal 4 item 2 (Pasal 7(1)a); VAT chapter in force 1 April 2022 (Pasal 17(2)) |
| From 1 January 2025 | 12% | "other value" of **11/12** of the fee | 11% | UU 7/2021 Pasal 7(1)b ("no later than 1 January 2025"); PMK 131/2024 Art. 3(2)–(3), in force 1 January 2025 (Art. 6) |

- PMK 131/2024 keeps the full 12% on the sale price only for luxury goods that
  bear sales tax on luxury goods (Art. 2). Every other taxable good and **every
  taxable service** uses the 11/12 base (Art. 3(1)). Businesses already on a
  separate "other value" or fixed-amount scheme are excluded (Art. 4). JDIH BPK
  lists PMK 131/2024 as "Berlaku" with no amending or revoking regulation shown;
  that is not proof that none exists.
- Exchange, clearing and depository services are not in the VAT-exempt lists
  read. UU 42/2009 Pasal 4A(3)d left "financial services" outside VAT, and its
  explanation limits these to deposit taking, lending and placement, finance
  leasing, factoring, credit cards, consumer finance, pawn lending and
  guarantees. UU 7/2021 removed that item from Pasal 4A(3) and moved "financial
  services" to the Pasal 16B(1a)j facility, with the same list in its
  explanation. Neither list names exchange, clearing or custody services, and
  II-A XI.2 treats the exchange fee as subject to VAT. The implementing
  government regulation for Pasal 16B was not read.
- Simulation consequence: the VAT on the exchange fee is **0.018% × 10%, 11% or
  11%** of transaction value in the three periods above. The 2025 figure equals
  12% × 11/12. Whether VAT is charged on the KSEI and KPEI fees, and how a broker
  passes any of it to a client, was not read and is not assumed.
- Not checked: whether UU 6/2023 (Cipta Kerja) changed Pasal 7 after UU 7/2021,
  how the exchange's own invoices apply the 11/12 base, and any VAT rule before
  1 April 2010. (UU 6/2023 and PP 49/2022 were read later; see
  [VAT exemption and the UU 6/2023 check](#bei-calendar-amendments-ii-a-context-and-vat-exemptions-2026-11-12).)

**II-A Kep-00108/BEI/12-2020** (decree file with the directors' names; the file
name has no "signed" marker):

- Issued **4 December 2020**, in force **7 December 2020**. It revokes II-A
  **Kep-00025/BEI/03-2020** (12 March 2020), items 1–2 of Kep-00031/BEI/03-2020
  (26 March 2020, trading-hour change) and Kep-00063/BEI/09-2020 (2 September
  2020, reference prices) (decree item 8). OJK approval S-1153/PM.21/2020
  (16 November 2020). Kep-00025 becomes the earliest version now evidenced; its
  text is unread.
- Annex hours IV.2–IV.4 and market orders were set to start **26 July 2021**
  (items 2a, 4). Until then a temporary Monday–Friday schedule applied: pre-opening
  08:45:00–08:55:00, session I 09:00:00–11:30:00, session II 13:30:00–14:49:59,
  pre-closing 14:50:00–15:00:00, post-closing 15:05:00–15:15:00 (item 2b).
  Kep-00061 replaced Kep-00108 on 26 July 2021 and deferred the annex hours
  again, so the Kep-00108 annex hours never applied.
- Annex auto-rejection VI.7.1.2 (symmetric ±35/25/20%) was deferred. The
  temporary limits were **+35/+25/+20% upper and −7% lower** for the Rp50–200,
  >Rp200–5,000 and >Rp5,000 bands (item 5). The reference-price clauses VI.7.3
  and VI.9 were also deferred; the reference was the previous price, theoretical
  post-action price, IPO price or appraised value (item 6).
- Annex values: round lot 100 (VI.4.2); tick Rp1/2/5/10/25 with maximum steps
  Rp10/20/50/100/250 at the 200/500/2,000/5,000 previous-price breaks
  (VI.5.2.1–VI.5.2.5); minimum price **Rp50** for shares, Rp1 for rights and
  warrants (VI.6); volume rejection above 50,000 lots or 5% of listed shares
  (VI.7.2); Regular T+2, Cash T+0 (VI.12.3–VI.12.4); cum Regular ends RD−2, Cash
  on RD (VIII.1); exchange fee **0.018%** per transaction on Regular and Cash,
  excluding clearing and settlement, with a Rp20,000,000 monthly member minimum
  (XI.1.1, XI.1.3); VAT added (XI.2). Pre-opening was for LQ45 stocks and others
  the exchange chose (VI.8.2).
- Simulation consequence: from 7 December 2020 to 25 July 2021 the values above
  apply, with the temporary hours and the −7% lower limit. The earlier
  Kep-00061 note (−7%, Rp50) is consistent with this. What applied before
  7 December 2020 is in Kep-00025 and is unread.

**II-A Kep-00196/BEI/12-2024 and Kep-00003/BEI/04-2025 (II-A): no signed file
found.** Searches limited to `idx.co.id` and `idx.id` returned only secondary
references and drafts:

- Pre-opening list announcement Peng-00251/BEI.POP/12-2024 and the IDXbell
  newsletter cite Kep-00196 dated 6 December 2024; neither was read this time.
  A search summary also said the trading-hours page cites Kep-00196. The current
  English trading-hours page, opened today, cites only Kep-00158, so that summary
  reflects an older copy.
- An unsigned "konsep bersih" draft of II-A
  ([`0hebzfh0`](https://www.idx.co.id/Media/0hebzfh0/konsep_bersih_perubahan_peraturan_nomor_ii_a_terdampak_pspp.pdf))
  and a June 2023 change matrix
  ([`5wabxbxi`](https://idx.co.id/Media/5wabxbxi/20230622_matriks_perubahan_peraturan_ii-a_perdagangan_ebe.pdf))
  exist. They are drafts, were not opened, and are not evidence.
- The values of both versions therefore stay unread. The II-A rows for
  Kep-00196 and Kep-00003 in the version table are unchanged.

**I-X Kep-00315/BEI/11-2023**, special-monitoring placement:

- Issued **1 December 2023**, in force **4 December 2023**. It revokes I-X
  **Kep-00081/BEI/05-2023** (5 June 2023) (decree item 7). OJK approvals
  S-21/PM.21/2023 (4 January 2023) and S-267/PM.01/2023 (28 November 2023, phase II
  full call auction transition). Trading on the board follows the transition in
  II-X Kep-00316/BEI/11-2023 (items 2–3).
- Placement criteria (III.1), any one is enough:

| Item | Criterion |
|---|---|
| III.1.1 | 6-month average price below **Rp51** on the Regular and/or periodic-call-auction market (not for Acceleration-board shares, III.2) |
| III.1.2 | disclaimer opinion on the latest audited statements |
| III.1.3 | no revenue, or no change in revenue, against the previous statements |
| III.1.4 | mining company (or its holding) with no core revenue by the end of the 4th financial year after listing |
| III.1.5 | negative equity in the latest statements |
| III.1.6 | no longer meets continued-listing rules I-A (Main, Development) or I-V (Acceleration) |
| III.1.7 | 6-month average daily value below Rp5,000,000 **and** volume below 10,000 shares |
| III.1.8–III.1.9 | PKPU, bankruptcy or cancellation of a composition filed against the company or a material subsidiary |
| III.1.10 | trading halted for more than 1 exchange day because of trading activity |
| III.1.11 | other conditions set by the exchange with OJK approval or order |

- The 6-month windows of III.1.1 and III.1.7 are evaluated each **May and
  November** (III.3). III.1.6 started on 31 January 2024 for I-A and starts on
  31 October 2025 for I-V (item 4).
- Exit (IV.1) needs the condition to end, revenue recorded for III.1.4, liquidity
  or a liquidity provider for III.1.7, 30 calendar days on the board for
  III.1.10, and a share price of **at least Rp50** (IV.1.6). Placement and exit
  are announced at least 1 exchange day ahead (II.3); the exchange may keep a
  company on the board on substance (IV.4).
- Suspension (V): mandatory after more than 1 consecutive year for III.1.2–1.6,
  1.8 and 1.9 (V.1); discretionary for III.1.1, 1.7 and 1.11 (V.2). It covers all
  markets for 1.2–1.5, 1.8 and 1.9, Regular and Cash only for 1.1, 1.6 and 1.7
  (V.3). The V.1 suspension did not apply to companies whose only criterion is
  negative equity until **8 June 2026** (item 5); the year counts from the date a
  company was first placed (item 6).
- Interval: in force 4 December 2023 until Kep-00076 replaced it on 21 June 2024.
  Kep-00076 III.1.1 uses a 3-month window together with value and volume tests,
  so the criteria changed between versions and Kep-00315 values must not be
  used after 20 June 2024.

**I-X Kep-00035/BEI/06-2025: no rule file found.** Searches returned no
attachment. A BEI suspension announcement of 23 June 2025 (hashed above) cites
Kep-00035 and restates three points: the V.1 year counts from 21 June 2024 for
companies already on the board under Kep-00076; V.1 covers III.1.2–1.6, 1.8 and
1.9; and the negative-equity exemption runs to **30 June 2026**. This is the
exchange's own summary, not the rule text, and gives no placement thresholds. A
search summary dated Kep-00035 to 3 June 2025 from the governance report; that
page was not re-read, so the date stays unverified. The announcement's list of
48 companies is not reproduced here.

**Trading halt before 8 April 2025: Kep-00024/BEI/03-2020 not found.** No copy
turned up on `idx.co.id`, `idx.id` or `ojk.go.id`. The OJK/SRO joint press
release of 23 March 2020 lists, among COVID-19 measures, "a 30-minute trading
halt when IHSG falls 5%" (item 8). It does not cite Kep-00024 or give any second
tier. A search summary claimed further 10% and 15% tiers from an OJK letter
S-274/PM.21/2020 and an older Kep-00366/BEI/05-2012; neither was opened, so
those tiers are not recorded. The thresholds in force from 10 March 2020 to
7 April 2025 therefore stay unproven beyond the single 5% statement.

**KPEI II-5:** no local PDF path was given, so the KPEI step was skipped and the
KPEI site was not tried again.

**Still open after this read:** the KPEI Regular-market clearing fee, broker
commission, the texts of II-A Kep-00025, Kep-00196, Kep-00003 (8 April 2025),
Kep-00136 and Kep-00157, I-X Kep-00081 and Kep-00035, the 2020 halt guideline,
the VAT points listed above, the official holiday list and the JATS–WIB mapping.
No rulebook JSON, `IDXRegularRules` default, fee model or code change was made;
backtests stay refused.

### BEI holiday calendars 2024 to 2027, 2026-11-12

Leads came from web searches limited to official domains; each file below was
opened and read. The BEI files were read in the browser with pdf.js 4.4.168. The
built-in browser refused `web.ksei.co.id` this time, so the two KSEI files were
fetched with plain `curl` (HTTP 200) into `%TEMP%` and read with `pypdf`. Nothing
was saved to the repository.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| BEI Peng-00233/BEI.POP/11-2024, 2024 calendar change | 420,277 | Tue, 12 Nov 2024 04:19:00 GMT | 3 | `22c6255c03fe6bd72b0ef940f34761810dadf5c35df60cf328e43e7ebf5d034d` |
| BEI Peng-00213/BEI.POP/10-2024, 2025 calendar | 394,023 | Wed, 16 Oct 2024 15:35:39 GMT | 3 | `84cfc174e5eab9257e9f93ce36bb41c76e67a3d8cb99cc9b4a80c76c26638b43` |
| KSEI PENG-0004/DIR/KSEI/0825, 2025 change | 1,009,963 | Mon, 11 Aug 2025 08:04:26 GMT | 3 | `c29c466e48ed8eb968876e51b99076a23c91d79e6f9cc8f7c646986ff9b50f21` |
| KSEI PENG-0007/DIR/KSEI/1225, 2025 second change | 1,086,708 | Tue, 16 Dec 2025 01:52:24 GMT | 4 | `80996292bd2230b5dfd2354d57a121749740d0e2a7a224cffb36558beaa0b413` |
| BEI Peng-00171/BEI.POP/09-2025, 2026 calendar | 364,914 | Tue, 23 Sep 2025 02:19:21 GMT | 3 | `5273a6f5724a5ac7f17027bdfcc8205ff8491e8299a6c0230347c59332e25324` |
| BEI Peng-00169/BEI.POP/09-2026, 2027 calendar | 624,261 | Wed, 16 Sep 2026 11:27:55 GMT | 3 | `2175f76d80d4645db8844dffbb93a8d88627b1dcf8429d91ab1d5959f78ceab7` |
| BEI Peng-00171/BEI.POP/09-2026, 2027 label correction | 787,875 | Thu, 17 Sep 2026 15:42:17 GMT | 3 | `cd4e16986e53cb2d8ef2a243e7f74ad1bfced1721310f5a7934c4f3ab088938e` |

URLs: [Peng-00233](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Libur%20Bursa%20Peng-00233-No.%20Peng-00233BEI.POP11-2024.pdf),
[Peng-00213](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Peng-00213-No.%20Peng-00213BEI.POP10-2024.pdf),
[KSEI PENG-0004](https://web.ksei.co.id/files/Pengumuman_Perubahan_Hari_Libur_dan_Cuti_Bersama_PT_KSEI_Tahun_2025.pdf),
[KSEI PENG-0007](https://web.ksei.co.id/files/Pengumuman_Perubahan_Kedua_Hari_Libur_dan_Cuti_Bersama_PT_KSEI_Tahun_2025.pdf),
[Peng-00171/2025](https://idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Peng-00171%20Libur%20Bursa%202026-No.%20Peng-00171BEI.POP09-2025.pdf),
[Peng-00169](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Libur%20Bursa%20Peng-00169%20ID-No.%20Peng-00169BEI.POP09-2026.pdf),
[Peng-00171/2026](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Penyesuaian%20Kalender%20Bursa%20Peng-00171%20ID-No.%20Peng-00171BEI.POP09-2026.pdf).

**What a BEI calendar is.** Each yearly notice says the calendar fixes the days on
which **both trading and settlement** of securities at the exchange do not take
place (item 1). It is based on the joint ministerial decree on national holidays
and collective leave for that year. BEI may change it if Bank Indonesia changes
its clearing calendar or the government changes holidays (item 2). It lists only
weekday closures; holidays on Saturday or Sunday are named in a note and left out.

**Weekday closures, by year** (dates are day-month):

| Year | Source in force | Closures | Trading days | Dates |
|---|---|---|---|---|
| 2024 | Peng-00233 (11 November 2024), revising Peng-00030/BEI.POP/02-2024 | 25 | 237 | 01-01; 08-02, 09-02, 14-02 (general election); 11-03, 12-03, 29-03; 08-04 to 12-04, 15-04; 01-05, 09-05, 10-05, 23-05, 24-05; 17-06, 18-06; 16-09; 27-11 (regional elections); 25-12, 26-12, 31-12 |
| 2025 | Peng-00213 (16 October 2024), plus 18 August per KSEI (below) | 24 + 1 | 237 as published | 01-01, 27-01, 28-01, 29-01; 28-03, 31-03; 01-04 to 04-04, 07-04, 18-04; 01-05, 12-05, 13-05, 29-05, 30-05; 06-06, 09-06, 27-06; (18-08); 05-09; 25-12, 26-12, 31-12 |
| 2026 | Peng-00171/BEI.POP/09-2025 (23 September 2025) | 22 | 239 | 01-01, 16-01; 16-02, 17-02; 18-03, 19-03, 20-03, 23-03, 24-03; 03-04; 01-05, 14-05, 15-05, 27-05, 28-05; 01-06, 16-06; 17-08, 25-08; 24-12, 25-12, 31-12 |
| 2027 | Peng-00169/BEI.POP/09-2026 (16 September 2026), label corrected by Peng-00171/BEI.POP/09-2026 | 20 | 241 | 01-01, 05-01; 05-02; 08-03 to 12-03, 15-03, 25-03, 26-03; 06-05, 17-05 to 20-05; 01-06; 17-08; 24-12, 31-12 |

- **Arithmetic check.** For each year, all listed dates fall on weekdays, and
  weekdays minus closures reproduce both the stated annual total and every
  monthly "Hari Bursa" figure in the attachment. With 18 August added, 2025 has
  236 trading days; no BEI document stating 236 was read.
- **2024:** Peng-00233 adds 27 November 2024 for the regional elections, citing
  OJK letter S-240/PM.122/2024 (7 November 2024), and sets 31 December 2024 as a
  holiday, "revising" Peng-00030 (5 February 2024). Peng-00030 and the original
  2024 notice were not read, so the calendar in force before 11 November 2024
  (in particular for 31 December) is not shown. A backtest that replays decisions
  as of a past date needs those earlier versions; a calendar of what actually
  happened can use Peng-00233.
- **2025:** KSEI PENG-0004/DIR/KSEI/0825 (8 August 2025) cites BEI
  **Peng-00149/BEI.POP/08-2025** (8 August 2025, "Perubahan Kalender Libur Bursa
  Tahun 2025") and adds **18 August 2025** (collective leave for Independence
  Day) to KSEI's closures. KSEI PENG-0007/DIR/KSEI/1225 (15 December 2025) keeps
  the same 25 dates and limits 31 December 2025 settlement to government bonds,
  bonds traded through SPPA/PLTE and Bank Indonesia securities. Peng-00149 itself
  was **not found** on `idx.co.id`. The 18 August closure is therefore evidenced
  by KSEI's citation of a BEI notice, not by the BEI text. The KSEI list for 2025
  otherwise matches Peng-00213 date for date.
- **2026:** no BEI change notice for 2026 was found. KSEI's operational index
  still links its 2026 holiday item to PENG-0002/DIR/KSEI/0126, whose 22 dates
  match Peng-00171/BEI.POP/09-2025 (see
  [Calendar revision chain](#calendar-revision-chain)). Not finding a change is
  not proof that none exists; the year is not over.
- **2027:** the correction changes only one description ("Kenaikan Yesus Kristus
  (Paskah)" becomes "Kenaikan Yesus Kristus") and keeps every date. It names a new
  BEI page, `https://www.idx.co.id/id/berita/jadwal-libur-bursa`. That page and the
  older `tentang-bei` page both rendered empty in the browser today, without
  dates or attachments. KSEI's index now links a separate KSEI 2027 holiday
  notice, which was not read.
- Notice numbers repeat across years: Peng-00171 is the 2026 calendar
  (09-2025) and also the 2027 correction (09-2026). Cite number and month-year
  together.

**Simulation consequence.** For 2024, 2026 and 2027, the session-date calendar
can be the weekdays minus the closures above, as last published. For 2025 it
needs the extra 18 August closure, whose BEI text is still unread. Each year can
still change by later notice, so coverage should end at the last notice read and
be marked revisable. Years before 2024 are not covered: no BEI calendar for 2023
or earlier was found in this pass. Trading sessions, half days and instrument
suspensions are separate from this list. Per the notices, settlement does not
run on these days either, so T+2 counts the same exchange days; KSEI's limited
31 December bond settlement does not apply to equities.

Limits of this evidence: the BEI texts of Peng-00030/BEI.POP/02-2024, the
original 2024 notice and Peng-00149/BEI.POP/08-2025, all calendars before 2024,
and any change to 2026 or 2027 after the notices read. No calendar artifact,
`complete: true` flag, rulebook JSON or code change was made; backtests stay
refused. (Peng-00030 and Peng-00149 were found and read later; see
[the next section](#bei-calendar-amendments-ii-a-context-and-vat-exemptions-2026-11-12).)

### BEI calendar amendments, II-A context and VAT exemptions, 2026-11-12

**How the BEI files were found.** The `idx.co.id` announcement pages render
their list from a JSON endpoint, `/primary/NewsAnnouncement/GetAllAnnouncement`
(parameters `keywords`, `dateFrom`, `dateTo`, `pageNumber`, `pageSize`, `lang`).
Called from a page on `idx.co.id` in the built-in browser, it returned HTTP 200
JSON with each notice's number, date and attachment URLs. Searches for "Kalender
Libur Bursa", "Libur Bursa" and "Perubahan Kalender" over 2018–2026 returned the
calendar notices already read plus Peng-00030/BEI.POP/02-2024 and
Peng-00149/BEI.POP/08-2025. Web searches limited to official domains found
neither. PDFs were then fetched on their own page and read with pdf.js 4.4.168
from cdnjs. Peng-00030 is published only as a zip; the zip was fetched from an
`idx.co.id` page and opened in memory with JSZip 3.10.1 from cdnjs. Plain `curl`
was not used for `idx.co.id`. The two JDIH BPK files were fetched with plain
`curl` (HTTP 200) into `%TEMP%` and read with the project's `pypdf`. Nothing was
saved to the repository, and the temporary files were deleted.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| BEI Peng-00030/BEI.POP/02-2024, zip as published | 260,047 | Mon, 05 Feb 2024 12:18:40 GMT | – | `feafdae5874bd58f52b7d947e74f54b4f87938ac997540228806fba1ef2961fb` |
| PDF inside that zip | 372,966 | (zip entry dated 6 February 2024) | 3 | `a70dc3184b4ed8646b4dea814c402a5fc01b64631576562890444f06f1b9ff5a` |
| BEI Peng-00149/BEI.POP/08-2025, 2025 calendar change | 431,390 | Fri, 08 Aug 2025 09:45:34 GMT | 3 | `c0f59975d73c136e954b0c10508d483832f15029b91d91d056bfaf5e3e31192c` |
| BEI Peng-00251/BEI.POP/12-2024, pre-opening list | 729,167 | Sat, 07 Dec 2024 12:21:09 GMT | 18 | `00878713b9d310861b33c4b161571f1ec6d64cbebc475d3056b644da73ff80fc` |
| IDXbell newsletter, edition 27 (re-read) | 6,268,404 | Thu, 23 Jan 2025 08:21:41 GMT | 22 | `93e79bd39667dd57202dd6aa04f470d4640faaf846a2fdb2ff13b736280212c2` |
| PP 49/2022, JDIH BPK | 8,092,351 | Thu, 15 Dec 2022 02:37:45 GMT | 78 | `5b262aef226ce5d2cb7d19aae419aafbcc57582b06ef0809bcdc8af74234e2c5` |
| UU 6/2023, JDIH BPK | 85,354,383 | Sat, 01 Apr 2023 05:09:08 GMT | 1,127 | `de73c84f11d4e721a4c0e66cadadac7f698941ec8adff5934e70f32dc885fdae` |

The zip returned `application/x-zip-compressed`; every other file returned HTTP
200 `application/pdf`. The IDXbell hash matches the earlier record.
URLs: [Peng-00030 zip](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Peng-00030_BEI.POP_02-2024-ID.zip),
[Peng-00149](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/Libur%20Bursa%20Peng-00149-No.%20Peng-00149BEI.POP08-2025.pdf),
[Peng-00251](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/Exchange/PreOp%20Peng-00251-No.%20Peng-00251BEI.POP12-2024.pdf),
[IDXbell 27](https://www.idx.co.id/Media/y5agatkd/idxbell-edisi-27-januari-2025.pdf),
[PP 49/2022](https://peraturan.bpk.go.id/Details/232943/pp-no-49-tahun-2022),
[UU 6/2023](https://peraturan.bpk.go.id/Details/246523/uu-no-6-tahun-2023).

**Calendar change notices, weekday closures** (dates are day-month):

| Year | Notice | Change | Closures | Trading days | Dates |
|---|---|---|---|---|---|
| 2024 | Peng-00030/BEI.POP/02-2024 (5 February 2024) | adds 14-02 (general election) | 23 | 239 | 01-01; 08-02, 09-02, 14-02; 11-03, 12-03, 29-03; 08-04 to 12-04, 15-04; 01-05, 09-05, 10-05, 23-05, 24-05; 17-06, 18-06; 16-09; 25-12, 26-12 |
| 2025 | Peng-00149/BEI.POP/08-2025 (8 August 2025) | adds 18-08 (collective leave, Independence Day) | 25 | 236 | Peng-00213/BEI.POP/10-2024 dates plus 18-08 |

- **Arithmetic check.** In both attachments every listed date is a weekday, and
  weekdays minus closures reproduce every monthly "Hari Bursa" figure and the
  annual total (2024: 22/18/18/16/18/18/23/22/20/23/21/20 = 239; 2025:
  19/20/19/16/17/18/23/20/21/23/20/20 = 236).
- **Peng-00030/BEI.POP/02-2024.** Cites UU 7/2017 Pasal 167(3) (voting on a
  national holiday), KPU regulation 3/2022 and decree 21/2022, and OJK letter
  S-33/PM.122/2024 (5 February 2024). It sets 14 February 2024 as an exchange
  holiday and attaches the full revised list. It does **not** cite the number or
  date of the original 2024 calendar. It may be readjusted for Bank Indonesia
  clearing changes or government holiday changes. Peng-00233/BEI.POP/11-2024
  later adds 27 November and 31 December (25 closures, 237 days); its other 23
  dates match Peng-00030 date for date.
- **Peng-00149/BEI.POP/08-2025.** Cites the amended joint ministerial decree
  (Minister of Religious Affairs 933/2025, Manpower 1/2025, Administrative
  Reform 3/2025, amending 1017/2024, 2/2024, 2/2024). Item 1 sets 18 August 2025
  as an exchange holiday, "revising" Peng-00213/BEI.POP/10-2024. Item 2 allows
  further adjustment. Its attachment lists the 24 Peng-00213 dates plus 18
  August, with 236 trading days. This is the BEI text that the KSEI notices
  PENG-0004/DIR/KSEI/0825 and PENG-0007/DIR/KSEI/1225 cited; the 18 August
  closure is now evidenced directly.
- **Version chains now read.** 2024: original notice (not found) →
  Peng-00030 (5 February 2024) → Peng-00233 (11 November 2024). 2025:
  Peng-00213 (16 October 2024) → Peng-00149 (8 August 2025). The index also
  lists Peng-00029/BEI.POP/02-2024, Peng-00234/BEI.POP/11-2024 and
  Peng-00150/BEI.POP/08-2025, which change the debt-securities and sukuk
  operating calendar. They were not read and do not set equity holidays.

**Calendars 2020 to 2023 and the original 2024 notice: not found.**

- The announcement index has no item dated before 3 July 2023. For 2019–2022 it
  returned 0 items even with an empty keyword, and for 2023 it returned 42,067
  items, the earliest dated 3 July 2023. A 2023 calendar would have been
  published in late 2022, so it is outside the index. From 3 July 2023 to
  4 February 2024 the index returned no BEI item with "Libur" or "Kalender" in
  its title. The original 2024 calendar is therefore also not found. The
  index's coverage of BEI's own notices in late 2023 is sparse; this is not
  evidence that no such notice exists.
- Searches limited to `idx.co.id` and `idx.id` returned only prospectuses that
  define "Hari Bursa".
- KSEI: the operating index links only the 2025, 2026 and 2027 holiday notices.
  Probing the same file-name pattern for 2020–2024 returned 404 or 500, and the
  KSEI news archive returned HTTP 500 after page 3. No KSEI notice citing a BEI
  calendar number for 2020–2024 was found, so no indirect evidence either.
- Leads, **not verified**: news-site search summaries say the 2022 calendar was
  revised in April 2022 to add 29 April and 4–6 May, and that the 2023 calendar
  listed 18 closures and 242 trading days, later revised to add 28 and 30 June
  2023. No BEI document was opened for either, so no date for 2020–2023 is
  recorded here.

**II-A Kep-00196/BEI/12-2024 context.** Neither document is the rule text; the
II-A version table keeps "Text read: no" for Kep-00196.

- **Peng-00251/BEI.POP/12-2024** (7 December 2024, signed by the heads of the
  trading-regulation and research divisions). It cites provision **VI.8.1** of
  Kep-00196/BEI/12-2024 of 6 December 2024 (amending II-A): pre-opening trades
  all shares listed on the Main, New Economy and Development boards. It lists
  the shares in the pre-opening session from **9 December 2024**; the annex
  numbers 685 shares. Its footnote says the list changes when a share leaves or
  enters the special-monitoring board.
- **IDXbell edition 27, page 12.** Says the exchange issued updated II-A and II-P
  on Friday 6 December 2024, effective Monday 9 December 2024, under
  **Kep-00196/BEI/12-2024** (equity trading) and **Kep-00197/BEI/12-2024**
  (structured warrants). The only II-A change it describes is pre-opening
  widened from LQ45 stocks to all stocks on the Main, Development and New
  Economy boards, to improve price discovery at the open. Its page-9 timeline
  labels the 9 December 2024 item "expansion of pre-opening shares, warrant AR,
  AR and MPM SW". It gives no values for those, and they are not inferred.
- Simulation consequence: from 9 December 2024 every share on the three boards
  could trade in pre-opening, and the list depends on special-monitoring
  placement. IDXbell describes the earlier scope as LQ45 stocks; Kep-00108
  VI.8.2 (read earlier) said LQ45 and others the exchange chose. The scope under
  Kep-00055 was not checked. Kep-00196's other values (hours, auto-rejection,
  tick, lot) remain unread.

**VAT exemption and the UU 6/2023 check.**

- **PP 49/2022** (set and promulgated 12 December 2022, in force on promulgation,
  Pasal 38). Pasal 10 lists the strategic taxable services exempted from VAT;
  "jasa keuangan" is item **d** and "jasa asuransi" item e. **Pasal 14** limits
  the exempt financial services to five kinds: (a) taking deposits, savings and
  similar funds; (b) placing, borrowing or lending funds; (c) financing (finance
  leases with option, factoring, credit cards, consumer finance, including
  sharia); (d) pawn and fiduciary lending; (e) guarantees. The explanation
  defines only the item (c) financing types. Neither the article nor the
  explanation mentions exchange, clearing, settlement or custody services; the
  words bursa, kliring, kustodian and efek do not appear in the extracted text.
  So exchange, KPEI and KSEI services are not in the exempt list. PP 49/2022
  revokes PP 146/2000, PP 81/2015, PP 40/2015 and PP 50/2019 (Pasal 37); JDIH
  BPK shows it as "Berlaku".
- **UU 6/2023** (enacting Perppu 2/2022 on job creation; signed and promulgated
  31 March 2023, in force on promulgation). Its annex lists UU 8/1983 among the
  laws it changes (Pasal 105 item g). **Pasal 112** of the annex amends only two
  provisions of the VAT law: Pasal 1A (item 1, what counts as a delivery of
  taxable goods) and Pasal 13 (item 2, tax invoices). **Pasal 7 (rate) is not
  amended.** The extracted text has no other amendment of UU 8/1983. The JDIH
  BPK page lists the laws that later amended or partly revoked UU 6/2023, and
  none of them is a tax law. So the rate chain recorded in
  [the VAT section](#vat-basis-ii-a-kep-00108-and-i-x-kep-00315-read-2026-11-12)
  (10%, 11%, 12% on an 11/12 base) is unchanged by UU 6/2023.
- Not checked: UU 4/2023 (financial sector) and any later tax law for a change to
  Pasal 7 or Pasal 4A; VAT on KSEI and KPEI fees as actually invoiced; broker
  pass-through.

**Simulation consequence.** For 2025 the calendar is now read from BEI itself:
weekdays minus the 25 closures of Peng-00149, which gives 236 days. For 2024, a
replay as of a date between 5 February and 10 November 2024 would use the 23
Peng-00030 closures. Without the original notice, dates before 5 February 2024
are not shown. In particular, before Peng-00030 was issued, nothing read shows
whether 14 February was a holiday. Years before 2024 have no read calendar, so a
session calendar for 2020–2023 cannot be built from this evidence. VAT on the
exchange fee stays 0.018% × 10%/11%/11% by period, with no exemption.

Limits of this evidence: no BEI calendar for 2020–2023 and no original 2024
notice; no change to 2026 or 2027 after the notices read; the Kep-00196 rule
text; KPEI fees; UU 4/2023. No calendar artifact, `complete: true` flag,
rulebook JSON, fee model or code change was made; backtests stay refused.

### UU 4/2023 read; Kep-00196 and 2026 calendar recheck, 2026-11-13

**UU 4/2023** (financial-sector development and strengthening, "P2SK"). The JDIH
BPK page shows it as "Berlaku", in force 12 January 2023, and amended by
**UU 4/2026** (below). The signed PDF was fetched with plain `curl` (HTTP 200)
into `%TEMP%`, with the user's approval for the 81.8 MB download, read with the
project's `pypdf` and deleted; nothing was saved to the repository.

| Document | Bytes | `Last-Modified` | Pages | SHA-256 |
|---|---|---|---|---|
| UU 4/2023, JDIH BPK download 295189 | 81,823,248 | Mon, 16 Jan 2023 01:42:40 GMT | 819 | `2be1b1e49af7c729fc2b09c16fcd94da0c601f70b9b6066e81e6b56d980b0e12` |

- The PDF is a scan with an OCR text layer; every page yielded text, but OCR
  errors (for example `2OLl` for 2011) mean a search can miss a spelling. Searches
  covered "Pertambahan", "PPN", "Pasal 4A", "Barang Mewah", "Pajak" and OCR
  variants of "1983".
- The statutes it amends ("Beberapa ketentuan dalam Undang-Undang Nomor …
  diubah") are all financial-sector laws: crisis prevention (UU 9/2016), LPS
  (UU 24/2004), OJK (UU 21/2011), Bank Indonesia (UU 23/1999), currency
  (UU 7/2011), banking (UU 7/1992), Islamic banking (UU 21/2008), **capital
  markets (UU 8/1995)**, insurance (UU 40/2014), social security (UU 40/2004)
  and microfinance (UU 1/2013). **The VAT law (UU 8/1983) is not among them**,
  and no text amends its Pasal 7 (rate) or Pasal 4A.
- Its tax provisions only point to tax law. For example, **Pasal 307** lets the
  government grant tax treatment or incentives for certain financial services
  "berdasarkan ketentuan peraturan perundang-undangan di bidang perpajakan". The
  elucidation names UU 7/2021 as the separate tax-sector reform.
- **UU 4/2026** (amending UU 4/2023): set, promulgated and in force
  **17 June 2026**, status "Berlaku" on JDIH BPK. Its abstract lists LPS status
  and governance, OJK supervision of mineral and strategic-commodity exchanges,
  **demutualisation of BEI**, financial-sector investigation and restorative
  justice, and the commodity exchanges. The abstract mentions no tax change. The
  text was then read too (next point).
- **UU 4/2026 text**, read the same way after a second approved download and then
  deleted:

  | Document | Bytes | `Last-Modified` | Pages | SHA-256 |
  |---|---|---|---|---|
  | UU 4/2026, JDIH BPK download 413875 | 13,974,767 | Mon, 22 Jun 2026 13:01:26 GMT | 207 | `dab7d3f02b6b4755c4f64eb3859ea6d717559465fc7947b0f10d0cb79a884483` |

  - Article I amends only UU 4/2023. Its other amendment points are UU 4/2023's
    own articles, among them the capital-markets article (Pasal 22). Article II
    holds transitional dates, and the law is in force on promulgation.
  - Capital markets (items 63–68, amending UU 8/1995 through UU 4/2023
    Pasal 22): **Pasal 8** makes the exchange a limited company whose
    shareholders may be individuals or Indonesian legal entities, members or not
    (demutualisation; details left to an OJK regulation). Pasal 8A is deleted.
    New **Pasal 8B** lets the Ministry of Finance, Bank Indonesia and BPI
    Danantara hold exchange shares while keeping the exchange independent.
    Pasal 100A and new 100E cover OJK's choice not to proceed to investigation,
    and Pasal 101 is deleted. **None of these items sets lots, ticks, price
    limits, hours, settlement, fees or holidays.**
  - Items 69–70 insert a new Pasal 39A on margin transfer for transactions in
    financial markets (initial margin as collateral). That passage was not read
    beyond its opening, and it sets no BEI equity trading value.
  - Tax: the text has no VAT, UU 8/1983 or Pasal 4A reference. Tax appears only
    in these places: an LPS or OJK levy that "bukan merupakan objek pajak
    penghasilan" (corporate income tax, effective for 2027 levies under
    Article II item 3); special-debt instruments that cannot be a tax basis; and
    special tax treatment for an Indonesian international financial centre,
    left to a separate law.

**Simulation consequence.** The VAT rate chain on the exchange fee recorded in
[the VAT section](#vat-basis-ii-a-kep-00108-and-i-x-kep-00315-read-2026-11-12)
stays as it was: neither UU 4/2023 nor UU 4/2026 changes it. BEI demutualisation
is governance and does not by itself change any trading rule read here.

**II-A Kep-00196/BEI/12-2024: still no rule text.** The `idx.co.id` announcement
index (`/primary/NewsAnnouncement/GetAllAnnouncement`, called from an
`idx.co.id` page in the built-in browser) returned no notice for the keywords
"Kep-00196", "Pra-pembukaan", "Pre-opening", "Peraturan Nomor II-A", "Perubahan
Peraturan" or "Perdagangan Efek Bersifat Ekuitas" between 1 November 2024 and
31 January 2025. "II-A" matched only issuer filings. Rule changes are evidently
not published through that index, so the version-table row stays "Text read: no".

**2026 calendar recheck.** Over 1 January to 13 November 2026, "Libur Bursa"
and "Kalender" returned only Peng-00169 and Peng-00171/BEI.POP/09-2026 (2027,
already read) and Peng-00170 and Peng-00172/BEI.POP/09-2026. The last two are
calendars for EBUS (the debt-securities market), are out of scope for equities,
and were not read. "Cuti Bersama", "Hari Bursa" and "Perubahan Kalender"
returned nothing. So the index holds **no amendment to the 2026 equity calendar**
issued during 2026 up to today. That is an absence in one index, not proof that
no change exists.

Limits of this evidence: the UU 4/2026 margin-transfer article in full; tax laws
after UU 7/2021 other than UU 6/2023, UU 4/2023 and UU 4/2026; the Kep-00196 text; BEI calendars for 2020–2023 and the
original 2024 notice; KPEI fees. No code, rulebook JSON, calendar artifact or fee
model changed; backtests stay refused.

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
