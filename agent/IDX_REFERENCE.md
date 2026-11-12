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
