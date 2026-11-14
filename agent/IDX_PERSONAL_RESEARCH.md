# Riset pribadi IDX melalui Yahoo/yfinance

## Paket lokal terbaru — 2026-11-11

**Wheel dan sdist baru tersedia, memuat profil IDX serta skill terbaru.**
Source, runtime logic, dependency manifest, versi `0.1.18` dan frontend tidak
berubah. Paket dibangun dari snapshot checkout publik yang belum di-commit;
bukan build yang hanya merepresentasikan commit HEAD. Seluruh perubahan lama
dipertahankan. Artefak deployment lama tidak ditimpa.

Grounded: `../setup.py:21,37` memiliki build wheel dengan UI dan sdist;
`../pyproject.toml:106,118` memiliki console entry points dan package data.
`tests/test_frontend_distribution.py`, runner/guard/verifier QA lama dibaca
sebelum adaptasi. Blast radius: artefak di luar repo dan tiga dokumen status.
Invariants: byte source/index sebelumnya, owner tool/client/registry, raw/null,
auth, currency gate, batas data dan penundaan LLM tetap. Verify: build produksi,
regresi targeted, wheel/sdist roundtrip, hash source/UI/skill, local install,
CLI serta API/MCP in-memory dari package terpasang dan integritas baseline.

### Artefak dan metode build

QA baru: `%TEMP%\idx-package-refresh-mmio_v47`.
Baseline sebelum edit: **3.219 file publik**, inventory/status Git UTF-8 NUL,
salinan/hash index dan salinan tiga dokumen. Snapshot hanya file publik dari
inventory Git; dotenv nyata, state akun, secret dan cache OAuth tidak disalin.
Backend setuptools existing disalin dari QA sebelumnya; **579 file cocok hash**
dengan receipt sebelum dipakai. Verifier akhir awalnya juga menuntut byte cache
backend tetap sama; 136 `.pyc` existing ternyata dikompilasi ulang oleh child
fixture packaging. `backend-after-run.json` membuktikan hanya cache itu berubah,
tanpa file baru atau perubahan kode/metadata backend; verifier akhir memisahkan
cache dari kode/metadata yang tetap wajib cocok hash. `node_modules` existing
dipakai melalui junction
QA untuk tes/build frontend; tidak ada `npm ci`, unduhan atau instalasi dependency.
Venv baru memakai pip bawaan Python; hanya wheel aplikasi dipasang `--no-deps`.

Wheel langsung `wheels/vibe_trading_ai-0.1.18-py3-none-any.whl`:
**18.176.618 byte**, SHA-256
`c29002afcae0c10340c008688674093fc00445aeb251846920f8c14cc01f50aa`.
`sdists/vibe_trading_ai-0.1.18.tar.gz` juga dibangun, lalu wheel dibuat ulang dari
sdist tanpa Node atau provisioning. Kedua wheel masing-masing memuat **1.662
file source yang cocok hash**, **143 aset UI cocok** dengan build produksi baru,
dan **91 skill**, termasuk `src/skills/idx-research/SKILL.md`. Profil/tool/client
terbaru hadir dan cocok snapshot. Hash arsip wheel roundtrip berbeda; tidak
mengklaim build reproducible byte-for-byte. Receipt `wheel-verification.json`
memuat hash kedua wheel, sdist dan tiap aset.

Instalasi bersifat terisolasi dengan **dependency existing dipakai ulang**
melalui path eksplisit; bukan instalasi dependency bersih atau bukti lock baru.
Environment child memakai allowlist OS, identitas sintetis dan home/runtime/temp
QA; guard Python menolak dotenv eksternal serta DNS/socket eksternal. Ini bukan
sandbox OS untuk native code. Konfigurasi/cache/index pip dinonaktifkan dan tiap
pip wheel/install memakai `--no-index --no-build-isolation --no-deps`.

### Verifikasi baru dan kegagalan QA yang dipertahankan

- Frontend penuh **1.231 passed, 95 file**, 563,77 detik; build produksi exit 0.
  Warning existing configLoader Vite, chunk besar, plugin timing dan beberapa
  log skenario React/error-boundary tetap tercatat; tidak ada failure tes.
- Seleksi backend packaging/profil/skill/Yahoo/startup/auth/SPA/scheduler:
  **233 passed, 2 warnings**, 530,75 detik, tanpa skip. Warning existing adalah
  anyio/pytest CallSpec2 dan Starlette/httpx; tidak memasang dependency pengganti.
- Run backend awal melewati deadline luar QA **600 detik** setelah satu marker
  `F`; detail failure belum tercetak saat abort. Penyebab marker tersebut tidak
  dipastikan. Empat kasus bantuan entry point diulang **4 passed** tanpa perubahan
  fixture/assertion; seluruh seleksi kemudian diulang dengan deadline luar
  1.800 detik dan lulus. Log awal `targeted-tests.log` dan receipt di `attempts/`
  dipertahankan; hasil run tidak lengkap tidak dihitung sebagai run lulus.
- Instalasi wheel lokal exit 0; `pip check`: **No broken requirements found**.
  CLI `--version` memberi `vibe-trading 0.1.18`; serve help, console MCP help
  dan module CLI riset help exit 0. Probe asal modul API/CLI/MCP/profil/Yahoo
  memastikan semuanya dari `venv/Lib/site-packages`, bukan source checkout.
- Probe MCP help awal gagal `ModuleNotFoundError: No module named 'pywintypes'`:
  `PYTHONPATH` tidak memproses extra paths dari `pywin32.pth`. File bootstrap
  existing dibaca; environment QA diperbaiki memakai path win32/lib/pythonwin
  existing dan DLL directory lokal proses. Probe diulang lulus, tanpa mengubah
  produk, memasang dependency atau mengubah konfigurasi Windows. Log awal
  disimpan di `attempts/`, sebab/cakupan di `pywin32-bootstrap-receipt.json`.
- Probe paket terpasang memakai assembler/serve adapter/auth/SPA asli dengan
  `uvicorn.run` hanya ditangkap, tanpa listener/lifespan. Empat route UI `/`,
  `/research/idx`, `/correlation`, `/runs/qa-package` memberi 200 dan index sesuai;
  **142 aset tambahan** diperiksa byte-nya. Missing/wrong key 401, Host/Origin
  asing 403. Ini ASGI in-memory dan tes render, bukan browser atau startup
  lifespan/preflight nyata yang baru.
- API IDX dengan boundary chart sintetis memberi BBCA.JK **20 bar**, IDR,
  close 144, SMA20 134,5, volume terakhir null dan satu akuisisi fixture.
  MCP in-memory memakai registry existing tanpa shell: profil BBRI.JK mempertahankan
  raw `0.18742001`, null periode/publikasi dan `historical_use="not_supported"`;
  boolean numerik ditolak dan kontrol US tetap lulus. Skill IDX terpasang dapat
  dimuat lengkap. Angka fixture bukan observasi provider baru atau kalibrasi ROE.

Perintah dari root, artefak/log ada di QA tersebut:

```text
.venv/idx312/Scripts/python.exe <QA>/workflow.py frontend
.venv/idx312/Scripts/python.exe <QA>/workflow.py build
.venv/idx312/Scripts/python.exe <QA>/diagnose.py
.venv/idx312/Scripts/python.exe <QA>/workflow.py tests
.venv/idx312/Scripts/python.exe <QA>/workflow.py probe
.venv/idx312/Scripts/python.exe <QA>/verify_final.py
```

Runner menyimpan argv/cwd/exit per command. `targeted.xml`, log frontend,
`installed-probe.json`, `backend-receipt.json`, `process-audit.jsonl`,
`session.diff` dan `verification.json` memisahkan hasil, batas dan integritas.
Repository hanya memperbarui panduan ini, `../PROJECT_STATUS.md` dan `../TODO.md`;
tidak ada permukaan runtime baru dari perubahan dokumentasi tersebut.

Tidak menjalankan full backend/safety, Ruff, browser baru, startup lifespan,
provider nyata, MCP jaringan/stdio eksternal, uji LLM nyata, Electron atau deployment.
**LLM tetap ditunda pengguna karena biaya token**. ROE tetap terblokir; raw unit,
periode, scope, formula, sampling/annualization, dataset version dan update/as-of
provider belum terbukti. Revenue/EPS/saham tidak dilanjutkan. RESEARCH-01/02/03
serta DATA/RULE/RELEASE penuh tetap terbuka. Hak display/redistribusi/remote/publik
belum diterima; MVP lokal delapan saham reguler .JK/harian IDR tetap, Local Data
Bridge belum diterima, backtest IDX nonaktif dan paper/live terpisah. Tidak ada
akun/login/credential/config sistem, order, listener eksternal, staging, reset,
commit atau publish. Dependency/config environment proyek dan artefak QA lama tidak diubah.

## Pembuktian ROE BBRI — 2026-11-11

**Disposisi: pembuktian `financials.returnOnEquity` BBRI.JK masih terblokir;
nilai dan metadata runtime tidak diubah.** Satu field ini belum diterima hanya
karena bukti issuer bertambah. Revenue bank, EPS dan saham belum dilanjutkan:
urutan penerimaan bergantung pada penyelesaian ROE, dan basis provider masih
unknown. Tidak mengambil ulang profil, mengulang lane Yahoo/BCA yang ditolak,
atau menganggap selisih angka sebagai bug shaper. LLM nyata tetap ditunda oleh
pengguna karena biaya token.

Grounded: `src/tools/stock_profile_tool.py:42,59,87,102` mengambil raw tanpa
rescale; `:452-454` mempertahankan null periode/publikasi dan history unsupported.
`backtest/loaders/yahoo_client.py:323,368` mengambil hasil quoteSummary pertama.
Tes `tests/test_idx_stock_profile.py:47,252` memisahkan retrieval/publikasi dan
menjaga pasar lain; registry, wrapper MCP, skill IDX serta capture/QA sebelumnya
dibaca. `RTK.md` tetap tidak ditemukan di root, tidak dibuat pengganti.
Blast radius: tiga dokumen status/backlog/panduan saja. Invariants: nilai raw,
unknown/null, seluruh perubahan terdahulu, index dan gate/batas pasar tetap.
Verify: comparator Decimal offline pada capture berhash, sumber primer dengan
halaman/cakupan, baseline file publik, inventory/status NUL, byte index,
UTF-8/tautan dan diff. Tidak ada permukaan runtime baru.

### Follow-up upstream dan batas pencarian publik

Kelanjutan **2026-11-11 WIB** memeriksa satu petunjuk upstream baru tanpa
mengambil profil ulang. Indeks [bantuan resmi Yahoo SLN37694](https://help.yahoo.com/kb/SLN37694.html)
menyebut migrasi dataset tab Financials ke Morningstar dan penyesuaian script
sebelum 9 November 2026. Ini **petunjuk indeks saja**: halaman yang sebelumnya
ditolak tidak dibuka ulang atau diakses lewat alias region/cache/archive.
Tidak membuktikan tanggal revisi halaman, update field BBRI, versi dataset
capture atau bahwa `quoteSummary.financialData.returnOnEquity` ikut migrasi.

Bukti primer baru yang benar-benar dibaca:

- [Glossary Morningstar Stock Grades](https://admainnew.morningstar.com/webhelp/glossary_definitions/indexes/stkstockgrades.htm),
  bagian Return on Equity %, menjelaskan net income tahunan dibagi net worth
  akhir tahun, lalu dikali 100. Cakupannya surface stock-grades yang didokumentasikan;
  versi/tanggal efektif dan pemetaan ke field Yahoo tidak diberikan.
- [Artikel edukasi Morningstar, 15 Juni 2015](https://www.morningstar.in/posts/33439/what-is-return-on-invested-capital.aspx),
  bagian Other profitability measures, menjelaskan net income dibagi rata-rata
  total common equity periode terkait. Ini artikel edukasi dengan scope berbeda,
  bukan spesifikasi feed yang memetakan field Yahoo.
- [Glossary 10-Yr Financials Morningstar](https://admainnew.morningstar.com/webhelp/glossary_definitions/indexes/stkfinancials.htm)
  memuat heading Return on Equity tanpa formula pada teks hasil ekstraksi.
  [Disclosures newsletter](https://newsletters.morningstar.com/msi-disclosures)
  hanya mengembalikan shell yang memerlukan JavaScript; cuplikan indeks tentang
  rata-rata ekuitas/estimasi analis tidak dianggap halaman terverifikasi.

Perbedaan cakupan sumber tersebut bukan bug. Nama vendor Morningstar saja
tidak memilih denominator, common/total equity, persen/fraksi, TTM, scope
konsolidasian, sampling/annualization, atau update/as-of Yahoo. Tidak ada
atribusi vendor/metodologi baru pada runtime. Riset issuer terdelegasi juga
menuntaskan query baru ROE B/S/monthly/annualized/rata-rata ekuitas pada domain
BRI, tanpa menemukan definisi yang dibutuhkan atau membuka ulang bukti lama.

**Disposisi:** pencarian publik increment ini ditutup menunggu input baru yang
memenuhi gap. Jangan mengulang query/lane yang sama hanya karena ada instruksi
melanjutkan. Pembuka spesifik adalah pemetaan **field + produk/versi dataset +
snapshot** provider, disertai definisi unit/periode/scope/formula/update, serta
definisi issuer dan observasi pada basis sama. Notice migrasi, glossary umum,
raw/fmt saja atau snapshot baru tidak cukup. ROE tetap belum selesai; urutan
revenue/EPS/saham tidak dilewati dan task penuh tidak dicentang.

QA baru di luar repo: `%TEMP%\idx-roe-upstream-8ff31c9010`.
Script QA sebelumnya dibaca; baseline sebelum edit berisi 3.180 hash publik,
inventory/status Git UTF-8 NUL, salinan/hash index dan salinan dokumen terdampak.
`checkpoint.txt`, `upstream-evidence.md`, receipt issuer, `source-acceptance.json`
dan `evidence.log` memisahkan halaman terbaca, cuplikan indeks dan mapping unknown.
`run_check.py evidence check_evidence.py` melalui interpreter existing memeriksa
hash/nilai capture lama, null/history, hash receipt dan ledger penerimaan
offline; **exit 0**, tanpa network/import produk. `verify_final.py` memeriksa
baseline/index/UTF-8/tautan/diff; hasil pada `verification.json`/`session.diff`.
Ini dokumentasi tanpa permukaan runtime, bukan integrasi provider atau tes
runtime baru. Pytest/Ruff, backend/safety penuh, frontend/build, packaging,
MCP eksternal, LLM dan deployment tidak dijalankan. LLM tetap ditunda pengguna;
hak data tambahan belum diterima. Tidak ada dependency/config/secret, order,
listener, staging/reset/commit/publish atau proses QA berkelanjutan.

### Deklarasi provider, interpretasi nama dan kalibrasi issuer

**Deklarasi yang tersimpan:** envelope lama membawa `returnOnEquity=0.18742001`,
identitas BBRI.JK/IDX equity, currency kuotasi/laporan IDR dan retrieval
`2026-11-11T00:35:59.961411+00:00`. Ini output tool, bukan sel Yahoo asli dengan
raw/fmt. Unit field, periode, consolidated/bank-only, numerator, denominator,
sampling rata-rata, annualization dan waktu pembaruan field belum terbukti.
Currency IDR bukan unit ROE; retrieval bukan update/publikasi per metrik.

**Interpretasi nama:** nama returnOnEquity merupakan petunjuk kandidat rasio
profitabilitas, bukan kontrak persen/fraksi, TTM, MRQ, ekuitas rata-rata atau
scope issuer. Dua hipotesis skala diuji offline saja. Jika raw dianggap fraksi,
hasil aritmetikanya 18,742001%; jika dianggap angka persen, 0,18742001%.
Keduanya tidak sama dengan tampilan issuer 9M26 19,2%/18,1%, juga di luar
setengah digit terakhir bila diasumsikan pembulatan terdekat. Konvensi rounding
issuer itu sendiri belum diaudit. Perbandingan negatif ini tidak memilih unit,
periode atau denominator yang benar dan tidak membuktikan provider salah.

**Kalibrasi independen:** belum ada pasangan provider/issuer dengan basis sama.
Angka Juni di bawah juga tidak menjadi kandidat pengganti angka September atau
Yahoo hanya karena berdekatan. `financial_period` dan `publication_time` tetap
null; `historical_use="not_supported"` dipertahankan. Tidak menambahkan metadata
baru, membagi/mengalikan raw produk, atau menulis regresi produk untuk dugaan.

### Bukti primer baru dan batasnya

Akses **2026-11-11 WIB**, riset issuer didelegasikan menurut skill research:

- [Publikasi keuangan BRI Juni 2026](https://www.ir-bri.com/misc/QR/2026/BRI-Lapkeu-Q2-2026-Eng.pdf),
  16 halaman, **PDF p11**: tabel rasio as of 30 Juni 2026/2025 memakai persen.
  ROE(3) Juni 2026 **22,59%**, denominator rata-rata total ekuitas Tier 1;
  ROE(4) **18,50%**, denominator rata-rata total ekuitas. Kedua footnote memakai
  laba setelah pajak sebagai numerator. Tabel itu tidak melabeli scope ROE
  secara eksplisit; sampling rata-rata dan annualization tidak dijelaskan di
  footnote tersebut. Tidak memindahkan definisi Juni ke ROE B/S 9M26.
- [Statement interim lengkap September 2026](https://www.ir-bri.com/newsroom/LF_30_Sep_2026_released.pdf),
  **427 halaman**, adalah dokumen baru berbeda dari URL statement lama yang
  gagal. Sampul mengidentifikasi konsolidasian/sembilan bulan sampai 30 September
  2026. Pencarian ekstraksi `Return on Equity`, `annualized`, `disetahunkan`
  tidak menemukan formula ROE yang dibutuhkan; ini bukan pembuktian ketiadaan
  formula di semua gambar/halaman. Dokumen menjadi input tersedia untuk tahap
  berikutnya, tanpa kalibrasi revenue/EPS/saham pada sesi ini.
- [Publikasi Maret 2025](https://www.ir-bri.com/misc/QR/2025/BRI-Lapkeu-Q1-2025-Eng.pdf),
  PDF p10, memberi corroboration historis dua denominator tersebut; tetap bukan
  bukti definisi September 2026. Presentasi Q3 existing diperiksa lagi untuk
  rumus; bukti monthly/persen/scope sebelumnya tidak diklaim sebagai temuan baru.
- [Listing resmi 2026](https://www.ir-bri.com/financials.html/year/2026)
  mengarah ke dokumen publikasi ringkas Q3 **berbeda**, melalui link aktual:
  [BRI-Lapkeu-Q3-2026-Eng.pdf](https://ir-bri.com/misc/QR/2026/BRI-Lapkeu-Q3-2026-Eng.pdf).
  Klik tracker gagal non-retryable dan target PDF inaccessible; kode HTTP PDF
  asal tidak tersedia. Lane baru ini langsung dihentikan, tanpa direct retry,
  mengganti host/region atau bypass. PDF tersebut tidak diklaim sudah dibaca.
  Release 09 Nov 2026 pada listing tetap deklaratif, bukan update Yahoo.

Discovery terarah definisi ROE pada domain help/developer Yahoo tidak menemukan
kontrak field yang dapat dipakai. Hasil berita sindikasi di finance.yahoo.com
menjelaskan formula penerbit lain, sehingga ditolak sebagai deklarasi provider.
Tidak membuka ulang halaman Yahoo 429 atau endpoint profil. Receipt merinci
query dan akses; tidak mencari provider pengganti atau mengulang audit aturan IDX.

### Blocker minimum dan QA

Input pembuka harus mencakup (1) deklarasi/provider evidence untuk field Yahoo
yang mengikat raw/fmt, unit, periode, scope, numerator/denominator, sampling,
annualization serta update/as-of pada observasi tersimpan; (2) definisi issuer
ROE B/S untuk periode/scope yang sama beserta observasi pembentuknya. Raw/fmt
tersanitasi saja dapat membantu unit, tetapi belum cukup membuktikan formula
atau waktu update. Definisi umum ROE, maxAge, tanggal listing dan snapshot baru
saja tidak memenuhi paket ini. Jika provider ternyata memakai horizon lain,
kalibrasi harus memakai laporan horizon tersebut, bukan memaksakan 9M26.

QA: `%TEMP%\idx-roe-proof-bd4f341fc3`.
Script baseline/runner/verifier/comparator lama dibaca sebelum adaptasi. Sebelum
edit: **3.180 hash file publik**, inventory/status Git UTF-8 NUL, salinan/hash
index dan salinan file terdampak. `checkpoint.txt`, `issuer-evidence.md`,
`external-receipt.json`, `check_roe.py`, `issuer-comparison.json` serta `roe.log`
memisahkan observasi, hipotesis dan unknown. Comparator stdlib tanpa network
memeriksa hash capture, raw/retrieval, null/history, delapan perbandingan dua
hipotesis skala dan ketidakcukupan basis; **exit 0**. Ini QA bukti, bukan tes
runtime atau penerimaan semantik provider. Perintah dari root:

```text
.venv/idx312/Scripts/python.exe <QA>/run_check.py roe <QA>/check_roe.py
.venv/idx312/Scripts/python.exe <QA>/verify_final.py
git diff --check
```

Pytest/Ruff, backend/safety penuh, frontend/build, packaging/wheel, external
MCP, LLM dan deployment tidak dijalankan pada sesi dokumentasi ini; **91 tes
lama bukan run baru**. Tidak ada akuisisi Yahoo/integrasi provider baru, akun,
secret/config, dependency, order, listener, staging/reset/commit/publish.
RESEARCH-01/02/03 penuh dan DATA/RULE/RELEASE tetap terbuka. Izin data tambahan
display/redistribusi/remote/publik belum diterima; MVP lokal maksimum delapan
saham reguler .JK/harian IDR tetap, UI fundamental tidak dibuat. Local Data
Bridge belum diterima, backtest IDX nonaktif, paper/live terpisah dan Index
Alpha ditunda. Integritas akhir lulus: hanya tiga dokumen tersebut berubah,
**3.177 file publik lain identik**, inventory/status Git UTF-8 NUL dan byte
index identik, **236 tautan/anchor lokal**, UTF-8 dan `git diff --check` lulus.
Index SHA-256 tetap
`4b8f7506e2b8d5e925201c8541ffe3addeac5a4d35d07e4f92b344799e759a6c`.
Hasil dicatat dalam `verification.json` dan `session.diff`; comparator/verifier
foreground serta subtask riset selesai, tanpa proses QA/listener berkelanjutan.

## Pencocokan issuer BRI — 2026-11-11

**Bukti issuer memberi unit dan scope yang eksplisit; belum mengkalibrasi
field Yahoo.** Kelanjutan ini mengerjakan gap laporan issuer dari audit
sebelumnya, tanpa mengambil ulang dua profil atau mengulang akses Yahoo 429.
Riset primer didelegasikan menurut skill research; draft dan receipt berada
di luar repo. Pengguna tetap menunda LLM berbayar. Tidak ada bug shaper baru
yang direproduksi atau perubahan runtime berdasarkan kemiripan angka.

Grounded: `src/tools/stock_profile_tool.py:42,87,197,448` mempertahankan raw
terpilih dan currency listing/laporan, tetapi tidak memiliki unit/periode per
field; `backtest/loaders/yahoo_client.py:375` hanya mengambil hasil pertama.
Kontrak `publication_time=null` dan `historical_use=not_supported` serta tes
retrieval-vs-publikasi dibaca ulang. Snapshot sekarang dibandingkan dengan
artefak QA lama, bukan dianggap payload Yahoo yang masih menyimpan fmt.
Blast radius: tiga dokumen status/backlog/panduan. Invariants: tidak menyamakan
periode/scope/denominator, tidak mengubah nilai atau metadata provider,
mempertahankan seluruh perubahan/index/gate dan batas riset lokal.
Verify: sumber primer per halaman, comparator Decimal offline, UTF-8/tautan,
diff serta hash baseline/inventory/status/byte index.

### Bukti primer dan batas pencocokan

Akses **2026-11-11 WIB**, [presentasi resmi Q3 2026 BRI](https://www.ir-bri.com/misc/PS/2026/Q3-2026-FU-Presentation.pdf),
89 halaman, nomor PDF sama dengan slide:

- Halaman 16/19: nominal konsolidasian **Rp Bn**. 9M26 equity 345.685;
  interest income 162.794, expense (44.939), NII 117.855;
  net profit 48.158, PATMI 47.689.
- Halaman 57/59: ROE B/S 9M26 konsolidasian **19,2%**, bank-only **18,1%**;
  laba bank-only 40.692 Rp Bn. Halaman 24 menyebut perubahan perhitungan rasio
  konsolidasian quarterly ke monthly sejak Januari 2024 dan penyesuaian histori.
  Rumus denominator, EPS dan saham belum terbukti dari halaman yang diperiksa.

`issuer-comparison.json` memeriksa konversi unit issuer, identitas NII dan
perbedaan scope; data ditranskripsi manual dari halaman primer. Raw ROE Yahoo
`0.18742001` tidak cocok dengan kedua ROE issuer, baik angka persen maupun
persen dibagi 100. Ini menolak penyamaan otomatis; bukan bukti raw Yahoo salah.
Tidak memetakan `totalRevenue` ke interest income/NII, atau memakai laba/equity
akhir periode sebagai denominator ROE tanpa definisi. Basis/horizon Yahoo
masih unknown. Tidak ada formula, faktor skala atau perbaikan runtime yang
diturunkan dari hipotesis tersebut.

[Financial Reports 2026](https://www.ir-bri.com/financials.html/year/2026)
dan [Corporate Presentations 2026](https://www.ir-bri.com/slides.html/year/2026)
menampilkan **09 Nov 2026** untuk item Q3 terkait. Ini tanggal release yang
dinyatakan listing sekarang, bukan waktu intraday/first-publication atau
riwayat revisi. Tanggal mendahului retrieval Yahoo 11 Nov tidak membuktikan
Yahoo memakai laporan itu. Tidak dipindahkan ke `publication_time` provider.
Periode issuer 9M26 tidak mengisi `financial_period` Yahoo atau membuktikan TTM.

[Listing keuangan BCA](https://www.bca.co.id/id/tentang-bca/Hubungan-Investor/laporan-presentasi/Laporan-Keuangan)
memuat laporan September 2026, tetapi rendered text tidak memberi link PDF;
satu permintaan HTML standar mendapat **403**, lalu lane dihentikan tanpa
retry/bypass. [PDF statement BRI dari listing](https://ir-bri.com/misc/QR/2026/Q3-2026.pdf)
tidak dapat diakses oleh web tool tanpa kode HTTP; tidak diklaim berhasil
dibaca. Presentasi berhasil diekstrak, screenshot halaman 57 diminta dan
screenshot halaman 19 timeout; tidak mengklaim seluruh tabel terverifikasi
visual. Angka sekunder/cuplikan pencarian tidak dipakai untuk mengganti laporan.

### Hasil, QA dan tindak lanjut yang masih dibutuhkan

Terbukti pada **tabel issuer yang dibaca saja**: unit nominal, pemisahan scope,
label periode dan persen ROE. Terbukti pada listing: tanggal release deklaratif.
Belum terbukti: unit raw Yahoo per field, rasio-versus-persen provider, EPS
basic/diluted dan adjustment split, weighted-average versus outstanding shares,
float resmi, forecast basis, definisi revenue/cash/debt bank, denominator ROE,
per-field publication/as-of serta revision history. Bukti issuer tidak menjadi
izin display/redistribusi/remote/publik atas data Yahoo atau laporan issuer.

Input berikutnya kini lebih spesifik: definisi dan periode `returnOnEquity`
Yahoo beserta raw/fmt terpilih; rekonsiliasi `totalRevenue` ke komponen laporan
yang benar; catatan EPS dan saham dalam statement yang dapat diakses; lalu
tanggal ketersediaan dan versi setiap observasi untuk histori. Jangan mengulang
lane Yahoo/BCA yang ditolak tanpa input/kondisi baru. Jika laporan primer
tersedia dari pengguna, review unit/scope/periode sebelum normalisasi apa pun.
RESEARCH-01/02/03 penuh serta DATA/RULE/RELEASE tetap terbuka; owner input
eksternal pending triage. Batas MVP maksimum delapan saham reguler `.JK`,
harian IDR tetap berlaku.

QA: `%TEMP%\idx-issuer-calibration-1acfd1c75d`.
Script QA lama dibaca sebelum adaptasi; baseline **3.180 file publik**,
inventory/status UTF-8 NUL, salinan/hash index serta tiga dokumen diambil
sebelum edit. `checkpoint.txt`, `issuer-evidence.md`, `compare_issuer.py`,
`issuer-comparison.json`, `comparison.log`, `session.diff` dan
`verification.json` menyimpan scope, sumber/halaman, aritmetika dan integritas.
Comparator memakai angka Decimal/integer tanpa network, menjalankan assertion
unit/NII/scope/ROE serta mempertahankan null/history pada capture; **exit 0**:

```text
.venv/idx312/Scripts/python.exe <QA>/run_check.py comparison <QA>/compare_issuer.py
.venv/idx312/Scripts/python.exe <QA>/verify_final.py
git diff --check
```

Tidak ada permukaan runtime baru. Pytest/Ruff, full backend/safety,
frontend/build, packaging/wheel, external MCP, LLM dan deployment tidak diulang
karena hanya dokumentasi yang berubah; 91 tes sesi sebelumnya bukan hasil run
sesi ini. Tidak ada akun, credential, dependency, order, listener, konfigurasi,
staging/reset/commit/publish. UI fundamental tidak dibangun, Local Data Bridge
belum diterima, backtest IDX nonaktif, paper/live terpisah, Index Alpha ditunda.
Integritas akhir lulus: hanya tiga dokumen tersebut berubah; **3.177 file
publik lainnya identik**, inventory/status Git UTF-8 NUL dan byte index identik,
**234 tautan/anchor lokal**, UTF-8 dan `git diff --check` lulus. Index SHA-256
`4b8f7506e2b8d5e925201c8541ffe3addeac5a4d35d07e4f92b344799e759a6c`.
Comparator/verifier foreground dan subtask riset selesai; tidak ada proses QA
atau listener berkelanjutan. Tidak menghentikan service pengguna.

## Audit semantik dan metadata profil — 2026-11-11

**Peta 56 field dan batas metadata diverifikasi offline; unit provider belum
dikalibrasi independen.** Tidak ada bug runtime baru yang terbukti, sehingga
source, tes dan skill tidak diubah. Pengguna tetap menunda panggilan LLM nyata
karena biaya token. Audit ini tidak menerima RESEARCH-02/03 penuh.

Grounded: `src/tools/stock_profile_tool.py:42,57,62,87,109,143,161,178`
memilih/meratakan enam section; `backtest/loaders/yahoo_client.py:323,375`
mengembalikan `quoteSummary.result[0]` tanpa rescale atau normalisasi sel.
Registry `src/tools/__init__.py:35,77,171` menemukan tool existing; wrapper
`mcp_server.py:2489,2513` memanggil registry yang sama. Referensi yfinance,
skill `idx-research`, preset fundamental/credit/management dan seluruh caller
yang ditemukan diperiksa: mereka tidak menambahkan metadata unit/periode yang
hilang dari envelope. `src/skills/data-routing/SKILL.md` masih memberi ringkasan
profil sebagai US; deskripsi tool/ref profil dan skill IDX sudah lebih luas.
Ini ketidaksinkronan panduan existing di luar slice semantik, bukan bukti routing
IDX gagal. Tidak menjalankan preset/swarm/LLM.

Blast radius: tiga dokumen ini, status dan backlog. Invariants: seluruh
pekerjaan sebelumnya/index, classifier/provider owner, null/presisi nilai,
currency gate, backtest nonaktif serta batas lokal/read-only tetap dipertahankan.
Verify: audit sintetis boundary client/registry, aritmetika capture terdahulu,
empat modul pytest targeted, UTF-8/tautan/diff dan seluruh hash publik/Git/index.

### Apa yang benar-benar dibawa dan dibuang

Client mengembalikan modul hasil pertama; metadata HTTP luar, error envelope
dan hasil tambahan bukan bagian return. Client tidak menambahkan unit/periode.
Tool meminta `price` plus modul section terpilih, bukan seluruh modul keuangan.
Output section berisi **56 nama field** (14 + 13 + 14 + 5 + 4 + 6); ini jumlah
nama dalam schema baris, bukan jumlah observasi atau jaminan coverage provider.
Inventaris dari AST dan assertion terhadap registry ada di `semantics-audit.json`.

- `key_stats` ← `defaultKeyStatistics`: semua 14 field dipilih dengan nama
  sama dan `_raw`. Kelompok nominal: `enterpriseValue`; EPS: `trailingEps`,
  `forwardEps`; kandidat multiple: `enterpriseToEbitda`, `enterpriseToRevenue`,
  `forwardPE`, `pegRatio`, `priceToBook`; kandidat rasio/fraksi: `profitMargins`,
  `heldPercentInsiders`, `heldPercentInstitutions`; ukuran saham: `sharesOutstanding`,
  `floatShares`; `beta` merupakan statistik tersendiri, bukan persentase.
- `financials` ← `financialData`: semua 13 field dipilih dengan nama sama
  dan `_raw`. Harga/target: `currentPrice`, `targetMeanPrice`, `targetHighPrice`,
  `targetLowPrice`; nominal: `totalRevenue`, `totalCash`, `totalDebt`; kandidat
  rasio/growth: `revenueGrowth`, `grossMargins`, `operatingMargins`,
  `returnOnEquity`; jumlah: `numberOfAnalystOpinions`; teks: `recommendationKey`.
- `earnings_trend` ← `earningsTrend.trend[]`: `period` disalin langsung;
  `end_date` ← `endDate` langsung; `growth` ← `growth.raw` bila berupa object.
  `eps_avg/eps_low/eps_high/eps_analysts` ←
  `earningsEstimate.avg/low/high/numberOfAnalysts`; `revenue_avg` ←
  `revenueEstimate.avg`; `eps_trend_current/eps_trend_7d_ago/eps_trend_30d_ago/eps_trend_90d_ago`
  ← `epsTrend.current/7daysAgo/30daysAgo/90daysAgo`;
  `eps_revisions_up_30d/eps_revisions_down_30d` ←
  `epsRevisions.upLast30days/downLast30days`. Selain dua label awal, semuanya
  memakai `_raw`. Nama 7/30/90 hari menyatakan label lookback provider, bukan
  timestamp observasi yang diaudit atau arsip point-in-time.
- `institution_ownership` ← `institutionOwnership.ownershipList[]`:
  `organization` langsung; `report_date/pct_held/position/value` ←
  `reportDate/pctHeld/position/value`, melalui `_raw`.
- `insider_holders` ← `insiderHolders.holders[]`: `name/relation` langsung;
  `latest_transaction` ← `latestTransDate` **langsung**, tanpa `_raw`;
  `position` ← `positionDirect` melalui `_raw`, bukan total direct+indirect.
- `recommendation_trend` ← `recommendationTrend.trend[]`: `period` langsung;
  `strong_buy/buy/hold/sell/strong_sell` ← `strongBuy/buy/hold/sell/strongSell`
  langsung, tanpa `_raw`.

Kelompok di atas adalah **interpretasi nama field untuk menentukan kebutuhan
bukti**, bukan deklarasi unit yang diterima. Nominal belum otomatis IDR satuan,
EPS belum terbukti IDR/saham dengan basis laporan tertentu, jumlah belum
terbukti integer/kelengkapan populasi, dan saham/posisi belum menjadi lot.
Tidak menyamakan `floatShares` dengan definisi free float resmi BEI atau
`heldPercentInsiders` dengan kepemilikan pengendali resmi.

`_raw` mengambil hanya anggota `raw` pada object; `fmt`, `longFmt` dan anggota
lain dibuang, object tanpa `raw` menjadi null. Scalar dipertahankan persis;
tidak ada kali/bagi 100, 1.000 atau satu juta. Tidak semua field memakai `_raw`:
fixture `latestTransDate` berbentuk object tetap object pada `latest_transaction`.
Ini hasil sintetis, bukan klaim payload insider IDX nyata; dua capture lama
insider-nya kosong. Tanggal output belum memiliki normalisasi schema seragam.

Metadata modul/sel yang tidak dipilih tidak masuk envelope, termasuk jika
disediakan: `maxAge`, `lastFiscalYearEnd`, `mostRecentQuarter`, currency di
subobject estimasi/holder, `regularMarketTime`, timezone dan field publikasi
yang tidak dipilih. Kehilangan field tersebut dibuktikan dengan sentinel
sintetis; **keberadaan nama-nama itu dalam respons nyata belum terbukti oleh
capture lama**. `maxAge` juga bukan tanggal publikasi. List dipotong sebelum
shaping pada 25 entri, entri nonobject dilewati, tanpa tanda jumlah total atau
truncation; list kosong tidak membuktikan tidak ada holder/analis.

`listing` mempertahankan `symbol`, `exchange`, `exchange_name` (prioritas
`fullExchangeName`, lalu `exchangeName`), `quote_type`, `currency`, serta
`underlying_symbol` bila ada dan `financial_currency` dari `financialData` bila
ada. IDX mengisi financial currency yang tidak ada menjadi null. Meminta hanya
`key_stats` tidak otomatis mengambil `financialData`: financial currency null
dapat berarti modul itu tidak diminta. Quote currency IDR bukan metadata unit
universal untuk EV, EPS, estimasi atau nilai kepemilikan.

### Bukti angka, semantik dan waktu

Capture publik lama menyimpan **output tool**, bukan sel raw Yahoo beserta
`fmt/longFmt`. Jadi informasi yang dibuang shaper tidak dapat direkonstruksi.
`provider-probe.json` lama ber-SHA-256
`fb88f978bb53477b6b8c1bb3e7c1b23aea4833dd8237b876122d33d310edd4ad`.
Audit menghitung dengan `Decimal(str(value))` di luar runtime produk:

- EV/revenue BBCA = 5,012621476..., BBRI = 2,902334825..., dekat multiple
  provider 5,013 dan 2,902. Ini konsistensi aritmetika dua field pada vendor
  yang sama; tidak membuktikan unit absolut (skala bersama dapat saling hapus),
  definisi EV bank, periode revenue atau ketepatan akuntansi issuer.
- `forwardPE × forwardEps` BBCA = 4.818,71013744 versus currentPrice 5.300
  (−9,08094%); BBRI = 2.950,725847095 versus 2.820 (+4,63567%). Tidak ada
  bukti keduanya harus memakai harga, horizon forecast, basis EPS atau waktu
  pembaruan yang sama. Tidak mengoreksi PE/EPS atau menganggap ini bug shaper.
- Holder `value = position × currentPrice` persis untuk kedua capture;
  posisi 11.522/25.610 bersamaan dengan `pct_held=0.0`. Itu bukan bukti posisi
  nol, persentase presisi penuh, denominasi nilai atau harga pada report date.
  Jangan menghitung histori nilai holder dari harga snapshot.
- Jumlah lima kategori recommendation periode `0m` = 26/23, sedangkan
  `numberOfAnalystOpinions` = 25/22. Populasi/tanggal pembaruan belum terikat;
  jangan memakai satu field sebagai denominator field lain secara otomatis.
- `revenueGrowth` BBRI = 2,035; nilai di atas satu tidak boleh otomatis ditolak
  atau dipotong ke rentang 0–1. Mengubahnya menjadi 203,5% memerlukan konfirmasi
  konvensi skala provider, periode pembanding dan definisi revenue bank.
  Hal sama berlaku untuk margin, ROE, growth estimasi dan held-percent.

Belum ada cross-check laporan issuer/rumus/periode yang independen. Deklarasi
listing/financialCurrency IDR pada dua capture tetap terbukti pada scope lama;
seluruh unit field, rasio-versus-persen, EPS basis, TTM/MRQ/forecast year,
adjustment split dan kecocokan metrik bank masih unresolved. Nol `grossMargins`
dipertahankan sebagai observasi provider, bukan hasil kalibrasi.

`retrieved_at` adalah waktu tool membungkus hasil, bukan timestamp per metrik;
bahkan replay offline menghasilkan waktu ini. `report_date` holder 2025-03-31/
2026-09-30 adalah tanggal referensi holder; `end_date` 2026-12-31 dst adalah
horizon estimasi. `latest_transaction` adalah label transaksi, `0m/-1m` label
periode recommendation. Tidak satu pun membuktikan tanggal laporan aktual atau
waktu pertama informasi tersedia bagi publik. `financial_period` dan
`publication_time` tetap null, `historical_use="not_supported"`; perubahan
`end_date` harga riset tidak menjadikan profil historis.

### Riset primer terbatas dan blocker

Gap sebelum browsing: konvensi raw/fmt, skala nominal dan periode field tidak
tersimpan pada capture. Pada **2026-11-11 WIB**, pencarian web primer Yahoo
menemukan halaman statistik BBCA dan bantuan financial statements; cuplikan
indeks memberi label persen/TTM/MRQ dan halaman laporan lain memberi label
ribuan. Ini hanya petunjuk lintas halaman/waktu, bukan kontrak quoteSummary,
dan label ribuan pada tabel laporan tidak boleh dipindahkan ke financialData.
Tidak mengadopsi angka cuplikan sebagai kalibrasi.

Akses langsung [statistik BBCA](https://finance.yahoo.com/quote/BBCA.JK/key-statistics/)
dan [bantuan financial statements](https://help.yahoo.com/kb/finance-for-web/financial-statements-yahoo-finance-changing-sln37694.html)
mengembalikan **HTTP 429** melalui web tool. Dua halaman lain dalam batch yang
sama (analysis/holders) tidak dapat diakses; tool tidak memberi kode HTTP.
Jalur Yahoo dihentikan setelah hasil batch, tanpa bypass, retry, pergantian
region, login atau probe quoteSummary. `external-receipt.json` mencatat scope
dan status tanpa cookie/crumb/header/raw body. Tidak mengulang audit sumber
resmi lama atau mencari provider pengganti.

Input minimum berikutnya: dokumentasi provider yang dapat diakses atau satu
capture **sanitasi sel terpilih** yang mempertahankan raw/fmt/longFmt, currency,
label periode dan waktu retrieval untuk field yang belum jelas; tanpa body HTTP
atau auth. Untuk kalibrasi independen diperlukan laporan issuer berizin dengan
unit, consolidated/standalone, basis EPS/split, akhir periode dan waktu
publikasi yang dapat dicocokkan. Historis membutuhkan versi/as-of dan waktu
ketersediaan setiap observasi, bukan snapshot baru saja. Hak display/redistribusi/
remote/publik tetap memerlukan input hak tersendiri. Jangan mengulang akses
yang ditolak tanpa kondisi/input baru.

### QA dan disposisi

QA baru: `%TEMP%\idx-profile-semantics-fa982fc57e`.
Script baseline/runner/verifier lama dibaca sebelum adaptasi. Baseline menyimpan
3.180 hash file publik, inventory/status Git UTF-8 NUL, salinan/hash byte index
serta salinan tiga dokumen sebelum edit. `checkpoint.txt` mencatat bukti/scope.
Environment child memakai allowlist OS dan runtime/home disposable. Audit awal
gagal karena pemilihan AST menangkap dict kosong internal, lalu script QA
diperbaiki memilih dict nonkosong; tidak ada kegagalan produk atau red regression
yang diklaim dari kesalahan auditor tersebut.

`audit_semantics.py` memeriksa 56 field, client tanpa rescale, registry existing
tanpa shell, nonmutasi payload, pemisahan IDR/USD sintetis, metadata yang dibuang,
tanggal yang tidak disimpulkan dan aritmetika dua capture. Sel sentinel bukan
data provider nyata. Tes empat modul memakai boundary provider fixture dan MCP
in-memory, bukan listener atau panggilan LLM. Perintah interpreter existing
melalui `<QA>/run_check.py`:

```text
.venv/idx312/Scripts/python.exe <QA>/run_check.py audit-corrected <QA>/audit_semantics.py
.venv/idx312/Scripts/python.exe <QA>/run_check.py targeted -m pytest
  agent/tests/test_idx_stock_profile.py agent/tests/test_stock_profile_tool.py
  agent/tests/test_idx_research_skill.py agent/tests/test_yahoo_client.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short --junitxml=<QA>/targeted.xml
git diff --check
```

Audit terkoreksi exit 0; empat modul **91 passed/1 warning** (anyio memakai
alias pytest yang deprecated), tanpa failure/error/skip. Tidak ada tes baru:
perubahan hanya dokumentasi, bukan perilaku. Log auditor awal tetap disimpan
untuk transparansi. `semantics-audit.json`, `external-receipt.json`,
`targeted.xml/log` dan `verification.json` merekam hasil serta batas klaim.
Integritas akhir: hanya `PROJECT_STATUS.md`, `TODO.md` dan panduan ini berubah
relatif baseline sesi; **3.177 file publik lainnya identik**, inventory/status
Git UTF-8 NUL identik, **232 tautan/anchor lokal**, UTF-8 dan `git diff --check`
lulus. Byte index identik dengan SHA-256
`4b8f7506e2b8d5e925201c8541ffe3addeac5a4d35d07e4f92b344799e759a6c`.
`session.diff`, salinan baseline dan hash artefak mendukung review. Proses
audit/pytest/verifier foreground selesai; tidak ada listener atau proses QA
berkelanjutan. Pemeriksaan tidak menghentikan service pengguna.
Tidak ada perubahan runtime sehingga tidak ada permukaan runtime baru;
audit/tes hanya memverifikasi kontrak existing. Tidak menjalankan full backend/
safety, frontend test/build, packaging/wheel, external MCP, broker/order,
Linux/WSL/Docker atau deployment. Tidak memasang dependency, membaca credential,
mengubah konfigurasi, reset/staging/commit/publish. UI fundamental tidak dibuat,
Local Data Bridge belum diterima, Index Alpha ditunda dan paper/live terpisah.
Implementasi metadata baru dan penerimaan fundamental penuh tetap menunggu
bukti; pekerjaan offline yang berguna dituntaskan pada scope audit ini.

## Validasi tipe angka profil — 2026-11-11

**Bug tipe angka diperbaiki tanpa biaya LLM atau akuisisi provider baru.**
Pengguna secara eksplisit menunda uji LLM nyata karena biaya token. Discovery
read-only menemukan executable Claude CLI, tetapi keberadaan binary tidak
membuktikan login, entitlement atau izin biaya; tidak memanggil auth/login,
membaca cache akun maupun menjalankannya sebagai model aplikasi. Bagian LLM
tetap ditunda sesuai keputusan pengguna, bukan task yang dianggap lulus.

Grounded: shaper `_raw`/`_pick` dan shaper enam section di
`src/tools/stock_profile_tool.py` memproyeksikan nilai tanpa memeriksa tipe
numerik. `json.dumps(..., allow_nan=False)` menolak nonfinite tetapi menerima
boolean/string/list/object JSON. Reproduksi sintetis melalui `execute` memberi
`ok=true`, `forwardPE=true` dan `totalRevenue="not-a-number"`. Tool yang sama
dimiliki registry existing untuk agent dan wrapper MCP; tidak perlu classifier,
adapter atau skema frontend baru. Blast radius: guard tipe IDX pada enam section,
17 kasus regresi tambahan dan dokumentasi. Invariants: null/unavailable, nol,
angka negatif yang sah, field teks/tanggal, currency/pasar lain, transport,
seluruh pekerjaan sebelumnya dan gate trading. Verify: red/green pytest,
MCP in-memory, replay capture offline, Ruff dan integritas Git/hash/link.

Guard `_validate_idx_numeric_values` memeriksa output shaper existing sebelum
serialisasi; field nonteks wajib `int`/`float` atau null. Boolean, string
(termasuk string yang tampak numerik), list dan object ditolak, tanpa coercion
atau mengubah angka. Field label/tanggal yang diproyeksikan shaper tetap
dikecualikan dari pemeriksaan numerik. Strict JSON tetap menolak nonfinite.
Kegagalan menghasilkan `{"ok": false, "error": "invalid IDX profile values"}`
dan warning jenis exception tanpa nilai provider. Tidak memperketat pasar lain,
menambah aturan rasio/count, mengarang unit atau mengaudit seluruh schema mentah;
struktur baris yang dilewati shaper dan metadata teks tetap kontrak existing.

QA baru: `%TEMP%\idx-profile-types-c57d31fbcc`.
Script baseline/runner/verifier sebelumnya dibaca. Sebelum edit: **3.180 hash
publik**, inventory/status Git UTF-8 NUL, salinan/hash index serta salinan file
yang disentuh. `checkpoint.txt` dan `reproduce.log` merekam bukti serta scope.
Child memakai allowlist environment dan HOME/USERPROFILE/AppData/runtime
disposable, tanpa credential atau state akun pengguna.

Regresi awal **12 failed/45 passed/1 warning**: enam tipe cacat pada PE,
boolean di lima section lain, serta kegagalan melalui MCP. Assertion pembeda:
respons `ok=true` diterima sementara yang diharapkan `ok=false`. Sesudah fix,
empat modul targeted **91 passed/1 warning**, tanpa failure/skip. Dari 17 kasus
tambahan, lima kontrol mempertahankan null/nol/angka bertanda dan kontrak AS;
12 kasus memperlihatkan kegagalan sebelum fix. Kontrol US/HK/UK/Argentina/Brazil,
skill discovery/load, client Yahoo, MCP sehat dan MCP penolakan tercakup.
Warning existing anyio/pytest alias tetap diungkapkan. Ruff pada source/tes
terkait **All checks passed!**.

`capture-replay.json` menggunakan dua envelope publik dari QA probe sebelumnya,
bukan network baru. Enam section tersimpan masing-masing lolos guard numerik.
Input boundary untuk `key_stats`/`financials` direkonstruksi dari output shaper
sebelumnya (nama field sama), lalu dipanggil melalui registry nyata: nilai dua
section dan listing identik untuk BBCA/BBRI. Raw HTTP tidak disimpan pada probe
lama, sehingga ini replay nilai, bukan replay payload Yahoo asli atau integrasi
provider baru. Metadata retrieval baru pada replay bukan retrieval jaringan.

Perintah actual, `.venv/idx312/Scripts/python.exe` dari root lewat runner QA:

```text
<QA>/reproduce.py
-m pytest agent/tests/test_idx_stock_profile.py -q --allow-hosts=127.0.0.1,::1
  --tb=line --junitxml=<QA>/red.xml
-m pytest agent/tests/test_idx_stock_profile.py agent/tests/test_stock_profile_tool.py
  agent/tests/test_idx_research_skill.py agent/tests/test_yahoo_client.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short --junitxml=<QA>/targeted.xml
-m ruff check agent/src/tools/stock_profile_tool.py agent/tests/test_idx_stock_profile.py
<QA>/replay_capture.py
git diff --check
```

Proses foreground reproduce/red/green/lint/replay selesai; red exit 1 sesuai
reproduksi, green/lint/replay exit 0. Tidak ada listener atau child berkelanjutan.
Tidak mengulang backend/safety penuh, frontend test/build, packaging atau
deployment karena jalur tersebut tidak diubah. Tidak ada paid LLM, provider
probe, dependency, secret/config, broker/order, staging/commit/reset/publish.
Tujuh file berubah dari baseline sesi: source/tes profil, dua README,
PROJECT_STATUS, TODO dan panduan ini. `verification.json`, `session.diff`,
inventory/status before/after, byte index dan evidence hashes merekam verifikasi.

Unit per field, tanggal publikasi/periode, kecocokan metrik bank, fundamental
historis/events dan hak tambahan masih memerlukan bukti. RESEARCH-01/02/03,
DATA/RULE/RELEASE penuh tetap terbuka; tidak mengulang pencarian sumber lama
tanpa input baru. UI fundamental tidak dibangun, wheel lama belum memuat
increment ini, Local Data Bridge belum diterima, backtest IDX nonaktif,
paper/live terpisah dan Index Alpha ditunda. Owner pekerjaan eksternal tetap
pending triage; uji LLM menunggu pengguna membuka kembali bagian yang ditunda.

## Probe profil Yahoo nyata — 2026-11-11

**Retrieval snapshot BBCA.JK dan BBRI.JK berhasil pada source checkout Windows.**
Probe memanggil `StockProfileTool.execute` dengan seluruh section default melalui
`yahoo_client.get_quote_summary`; tidak menambah adapter atau mengambil ulang
OHLCV. Tidak ada bug aplikasi yang direproduksi, sehingga kode/tes tidak diedit.

Grounded: `stock_profile_tool.py:271,354,390` memiliki klasifikasi, validasi
parameter dan akuisisi; `yahoo_client.py:323,348` memiliki quoteSummary/handshake;
`src/tools/__init__.py:35,171` menemukan tool yang dipakai agent dan
`mcp_server.py:2489` merutekan wrapper ke registry yang sama. Skill bundled dan
dua modul regresi IDX dibaca beserta shaper dan kontrol lintas pasar.
Blast radius: tiga dokumen status/backlog/panduan saja. Invariants: seluruh
perubahan sebelum sesi, index, classifier/routing, currency gate, shell opt-in,
mandate/kill switch/read-only, backtest nonaktif dan batas data lokal.
Verify: probe tool existing, inspeksi capture offline, empat modul pytest,
UTF-8/tautan/diff serta seluruh hash publik/inventory/index baseline.

### Receipt provider dan coverage

QA baru: `%TEMP%\idx-profile-live-f3aec82041`.
Script capture, runner dan verifier QA sebelumnya dibaca sebelum adaptasi.
Baseline sebelum edit memuat **3.180 hash file publik**, status/inventory UTF-8
NUL, salinan/hash index dan salinan tiga dokumen. Environment child memakai
allowlist OS, HOME/USERPROFILE/AppData/runtime disposable; tidak mewarisi
credential/proxy pengguna. TLS dan throttle existing dipertahankan.

Empat GET actual: `fc.yahoo.com` **404**, endpoint crumb **200**, quoteSummary
BBCA.JK **200**, quoteSummary BBRI.JK **200**. Client existing memakai cookie
response handshake pertama; 404 itu tidak mencegah dua profil berhasil.
Tidak ada 401/403/429. Guard QA menghentikan lane sebelum retry 401 bawaan
client jika penolakan tersebut muncul; tidak mengubah retry produksi, host,
TLS atau melakukan bypass. Cookie/crumb/header/query/raw HTTP body tidak
disimpan; `provider-probe.json` menyimpan status/path dan envelope tool publik.
Session HTTP ditutup dan proses probe sudah selesai.

Kedua respons `ok=true`, `market=idx`, sumber aktual **yahoo**,
symbol sesuai permintaan, venue **JKT / Jakarta**, quote type **EQUITY**,
currency kuotasi **IDR** dan financial currency **IDR**. Waktu retrieval:
BBCA **2026-11-11 00:35:58.858544 UTC (07:35:58.858544 WIB)**;
BBRI **00:35:59.961411 UTC (07:35:59.961411 WIB)**. Ini waktu pengambilan,
bukan waktu publikasi laporan, perdagangan terakhir atau jaminan freshness.

Coverage identik pada dua capture:

- Key stats: **13/14** field terisi; `enterpriseToEbitda` null. Tersedia
  `enterpriseValue`, `enterpriseToRevenue`, `forwardPE`, `trailingEps`,
  `forwardEps`, `pegRatio`, `priceToBook`, `profitMargins`, `beta`,
  `sharesOutstanding`, `floatShares`, `heldPercentInsiders`,
  `heldPercentInstitutions`.
- Financials: **13/13** field terisi: `currentPrice`, `targetMeanPrice`,
  `targetHighPrice`, `targetLowPrice`, `recommendationKey`,
  `numberOfAnalystOpinions`, `totalRevenue`, `revenueGrowth`, `grossMargins`,
  `operatingMargins`, `returnOnEquity`, `totalCash`, `totalDebt`.
  `grossMargins=0.0` adalah nilai yang dikembalikan, bukan bukti kecocokan
  metrik tersebut bagi akuntansi bank dan tidak diubah menjadi unavailable.
- Earnings trend: **4 baris** (`0q`, `+1q`, `0y`, `+1y`), end date berturut
  **2026-12-31, 2027-03-31, 2026-12-31, 2027-12-31**. Ini horizon estimasi
  provider, bukan periode laporan aktual atau tanggal publikasi.
- Institution ownership: **1 baris** masing-masing; `report_date` epoch yang
  dikembalikan setara **2025-03-31 UTC** untuk BBCA dan **2026-09-30 UTC**
  untuk BBRI. Tanggal pelaporan holder bukan waktu retrieval/publikasi;
  snapshot tidak membuktikan daftar pemegang lengkap atau terkini.
- Insider holders: **0 baris**, tetap unavailable. Recommendation trend:
  **4 baris** masing-masing, period `0m`, `-1m`, `-2m`, `-3m`.

Currency di atas dideklarasikan pada level listing/financialData. Tool tidak
memberi metadata unit per field; denominasi/basis harga-target/EPS, multiple,
rasio versus persen, skala nominal dan saham/posisi belum dikalibrasi independen.
Tidak membuat multiple, konversi FX atau klaim lot dari angka tersebut.
Interval, volume, timezone pasar dan adjustment OHLCV tidak disediakan profil;
tidak diturunkan dari waktu retrieval. `financial_period`/`publication_time`
tetap null dan `historical_use=not_supported`. Dividen/corporate events,
histori laporan, sektor dan foreign flow tidak dibuktikan oleh probe ini.
`capture-review.json` mencatat coverage, horizon/tanggal dan keterbatasan unit;
`review_capture.py` memeriksa dua envelope tersimpan tanpa akuisisi ulang.

### LLM, regresi dan disposisi

Pemeriksaan struktur saja: `LANGCHAIN_PROVIDER`, `LANGCHAIN_MODEL_NAME`,
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`,
`GOOGLE_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_BASE_URL`,
`OLLAMA_BASE_URL`, `VIBE_TRADING_HOME` tidak ada di environment sesi.
Ketiga kandidat dotenv aplikasi (`~/.vibe-trading/.env`, `agent/.env`, CWD
`.env`) dan tiga kandidat config `agent.json/yaml/yml` di runtime home standar
tidak ditemukan. `llm-availability.json` berisi nama/boolean keberadaan saja;
tidak membaca nilai secret, cache OAuth atau state akun. Ini bukan audit seluruh
instalasi LLM di komputer. Tidak ada runtime aplikasi terkonfigurasi yang dapat
diidentifikasi dalam batas tersebut; **analisis LLM nyata belum dijalankan**.
Langkah pembuka: runtime aplikasi existing dengan provider/model dan otorisasi
penggunaan/biaya yang jelas. Sesudah tersedia, jalankan satu skenario
`idx-research` Bahasa Indonesia, periksa angka terhadap observasi tool,
currency/tanggal, unavailable dan pemisahan fakta/interpretasi. Tidak membuat
akun, membaca/memindahkan credential, atau memakai autentikasi Codex desktop
sebagai konfigurasi aplikasi ini.

Perintah actual, interpreter `.venv/idx312/Scripts/python.exe` dari root melalui
`<QA>/run_check.py` (allowlist environment dan home terisolasi):

```text
<QA>/probe_profile.py
<QA>/review_capture.py
-m pytest agent/tests/test_idx_stock_profile.py agent/tests/test_stock_profile_tool.py
  agent/tests/test_idx_research_skill.py agent/tests/test_yahoo_client.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short --junitxml=<QA>/targeted.xml
git diff --check
```

Targeted **74 passed/1 warning** (anyio memakai alias pytest yang deprecated),
tanpa failure/skip; profil/skill melalui MCP in-memory, registry nyata dan
boundary provider fixture tercakup. Ini tes offline dengan koneksi dibatasi
loopback, bukan LLM atau MCP eksternal. Capture nyata dua ticker lolos review
offline; tidak mengambil data lagi melalui MCP. Tidak mengulang suite backend
atau safety penuh, Ruff (kode tidak berubah), frontend test/build, packaging,
Linux/WSL/Docker atau deployment. Tidak ada listener dibuat. Semua child QA
selesai; tidak ada service pengguna dihentikan atau konfigurasi sistem diubah.

Hanya status/backlog/panduan ini diperbarui; snapshot dua ticker berhasil tidak
menerima fundamental historis, hak display/redistribusi/remote/publik atau
menutup RESEARCH-01/02/03, DATA/RULE/RELEASE penuh. Wheel QA lama tetap belum
memuat increment profil/skill source. UI fundamental tidak dibangun, Local Data
Bridge belum diterima, backtest IDX nonaktif, paper/live terpisah dan Index
Alpha ditunda. Tidak ada dependency, akun, order, reset, staging, commit atau
publish. `verification.json`, `session.diff`, inventory/status before/after dan
evidence hashes menyimpan hasil pemeriksaan akhir; index diperiksa byte-for-byte
dan seluruh file publik baseline di luar tiga dokumen harus tetap sama.

Hasil integritas akhir: **3.177 file publik baseline lainnya identik**, inventory
dan status Git identik dengan baseline, **228 tautan/anchor lokal**, UTF-8 dan
`git diff --check` lulus. Byte index identik dengan SHA-256
`4b8f7506e2b8d5e925201c8541ffe3addeac5a4d35d07e4f92b344799e759a6c`.
Tiga dokumen tidak memiliki permukaan runtime baru; proses probe/review/pytest
foreground selesai dengan exit 0, tanpa listener atau proses QA berkelanjutan.

## Research local — 2026-11-11

**Kontrak profil IDX dan metode riset lokal tersedia pada source checkout.**
Scope lanjutan ini memajukan RESEARCH-02/03 memakai tool/registry/provider client
existing, tanpa sumber, akun atau dependency baru. Penerimaan MVP harga lokal
tidak diperluas menjadi penerimaan fundamental Yahoo IDX nyata.

Grounded: `stock_profile_tool.py:271` mengembalikan `us` untuk `.JK` dan
`execute` belum menguji listing yang dikembalikan provider. Caller agent melalui
`src.tools.build_registry` dan wrapper MCP `get_stock_profile` memakai tool sama;
SkillsLoader/LoadSkillTool menemukan panduan bundled dari source/package data.
Classifier tetap `_market_hooks._detect_market`; transport/rate limit tetap
`yahoo_client.get_quote_summary`, bukan HTTP client baru. Blast radius: tool
profil, konstanta alias venue provider dan konsumennya di pencarian, docstring
MCP, skill/method, dua modul regresi baru dan dokumentasi. Invariants: arti bare
ticker/pasar lain, auth, shell opt-in, gate mandate/kill switch/read-only,
currency gate, backtest IDX nonaktif dan seluruh perubahan sebelumnya.
Verify: regresi red/green offline, MCP in-memory, manifest/skill discovery,
kontrol lintas pasar, gate keselamatan, lint dan integritas Git/hash/link.

### Perilaku dan penggunaan

Pada agent/CLI interaktif atau klien MCP, muat:

```text
load_skill(name="idx-research")
```

Metode berbahasa Indonesia menggunakan `idx_research` untuk satu observasi
watchlist harian IDR beserta indikator existing, identitas/fingerprint, sumber
aktual, usia observasi, volume hilang/nol dan hasil parsial. Kueri ambigu tetap
memerlukan pilihan pengguna; tidak ada universe resmi baru yang dibuat.
Untuk konteks profil, tool existing menerima:

```text
get_stock_profile(ticker="BBCA.JK", sections=["key_stats", "financials"])
```

Jalur IDX menormalisasi case/whitespace dan memakai classifier pasar existing.
Instrumen `.JK` tidak didukung dan `local:` ditolak sebelum fetch. Setelah fetch,
provider wajib mendeklarasikan symbol yang sama, equity pada alias venue IDX,
dan currency kuotasi IDR. Alias Yahoo `JKT`/`IDX` sekarang dimiliki
`yahoo_client.IDX_EQUITY_EXCHANGES`, dibaca oleh pencarian dan profil; bukan
classifier paralel atau master instrumen. Bare `BBCA` tetap `us`; kontrol US/HK/
UK/Argentina/Brazil mempertahankan kontrak existing.

`listing.financial_currency` tetap terpisah dari IDR kuotasi, termasuk bila
provider melaporkan USD; tidak ada konversi atau penyamaan unit. Bila tidak ada
deklarasi, nilainya null. Angka hilang tetap null dan list unavailable tetap
kosong, bukan nol buatan. Mata uang/periode seluruh field belum dikalibrasi.
Provenance tambahan untuk IDX menyatakan `retrieved_at` UTC,
`financial_period: null`, `publication_time: null`,
`historical_use: "not_supported"`. Retrieval tidak membuktikan waktu publikasi;
snapshot tidak boleh menjadi input fundamental point-in-time historis.

Acquisition error IDX hanya mencatat jenis exception dan memberi error
tersanitasi, tanpa URL/crumb mentah. Listing/module cacat dan nilai yang gagal
strict JSON/nonfinite memberi envelope gagal. Ini bukan audit ulang seluruh
shaper/endpoint pasar lain. Skill mengarahkan field/dividen/events/foreign flow
yang belum tersedia menjadi unavailable, serta memisahkan observasi dari
interpretasi; tidak menghasilkan order atau perhitungan finansial baru.

### Bukti eksekusi dan batas

QA baru: `%TEMP%\idx-research-profile-ec974b66da`.
Baseline checkout sekarang sebelum edit: **3.216 hash publik**, inventory/status
Git UTF-8 NUL, salinan/hash index dan salinan file yang disentuh. Script capture/
verification QA sebelumnya dibaca sebelum adaptasi; tidak ada artefak lama
ditimpa. HOME/USERPROFILE/AppData/runtime child diset ke direktori QA baru dan
environment child memakai allowlist. Tidak membaca dotenv nyata, credential
atau state akun. Semua payload profil adalah fixture sintetis.

Red profil **29 failed/7 passed** mencakup `.JK` berlabel US, identitas/currency
asing diterima, bentuk instrumen tidak didukung mencapai fetch, raw error
provider bocor, missing metadata dan exception pada respons cacat. Skill yang
belum ada memberi **3 failed**. Runner awal untuk log skill menemui
`UnicodeEncodeError` saat mencetak teks Unicode ke terminal cp1252; XML/log tes
tetap utuh dan runner UTF-8 baru dipakai sesudahnya. Ini masalah harness,
bukan failure produk tambahan.

Fokus awal **49 passed/1 warning**. Regresi 12 modul **1.162 passed/5 warnings**:
profil, skill/discovery/manifest, Yahoo client, pencarian IDX/lintas pasar,
identity parity, skill allowlist/reference dan permukaan MCP. Profil diakses
melalui sesi MCP in-memory dengan registry nyata dan boundary provider fixture;
tidak menyalakan listener. Gate order/mandate/kill switch/read-only/SSE ticket
**137 passed/2 warnings**. Ruff lint pada enam file Python terkait lulus.
Warning existing anyio/Starlette tidak disembunyikan. Tiga kontrol pencarian
existing mencoba koneksi eksternal yang ditolak pytest socket allowlist;
hasil tersebut bukan integrasi provider atau bukti nol percobaan jaringan.
Ketiga kontrol itu dijalankan ulang dengan `--disable-socket` dan guard QA:
**3 passed/4 warnings**, kali ini pytest menolak `getaddrinfo` sebelum DNS.
Tidak mengubah tes kontrol lama atau menganggap fallback itu sebagai provider
berhasil. Uji permukaan akhir **2 passed/1 warning** membuktikan profil melalui
registry nyata serta skill melalui `load_skill`, keduanya pada sesi MCP
in-memory tanpa LLM/listener. Lint akhir sesudah format tes juga lulus.

Perintah memakai `.venv/idx312/Scripts/python.exe` dari root, melalui runner
environment terisolasi di QA:

```text
-m pytest agent/tests/test_idx_stock_profile.py -q --disable-socket --tb=line
-m pytest agent/tests/test_idx_research_skill.py -q --disable-socket --tb=line
-m pytest agent/tests/test_idx_stock_profile.py agent/tests/test_stock_profile_tool.py
  agent/tests/test_idx_research_skill.py agent/tests/test_idx_symbol_search.py
  agent/tests/test_symbol_search_tool.py agent/tests/test_yahoo_client.py
  agent/tests/test_distribution_skill_manifest.py agent/tests/test_skills.py
  agent/tests/test_load_skill_allowlist.py agent/tests/test_skill_reference_links.py
  agent/tests/test_market_identity_parity.py agent/tests/test_mcp_new_tools.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short
-m pytest agent/tests/test_sdk_order_gate.py agent/tests/test_mandate_enforcement.py
  agent/tests/test_killswitch_blocks_orders.py agent/tests/test_readonly_default.py
  agent/tests/test_sse_ticket_and_headers.py -q --allow-hosts=127.0.0.1,::1 --tb=short
-m ruff check agent/src/tools/stock_profile_tool.py agent/src/tools/symbol_search_tool.py
  agent/backtest/loaders/yahoo_client.py agent/mcp_server.py
  agent/tests/test_idx_stock_profile.py agent/tests/test_idx_research_skill.py
```

`red.xml`, `skill-red.xml`, `focused.xml`, `regression.xml`, `safety.xml`,
`surface.xml`, `search-controls.xml` dan
lognya merekam run aktual. Source/hash terkini, `verification.json`,
`session.diff`, inventory/status NUL dan byte index diverifikasi oleh
`verify_session.py`; artefak tersimpan di luar repo. Manifest bundled menjadi
91 skill; tidak membangun/memasang wheel baru. Wheel QA deployment lama belum
mengandung increment ini. Hanya tes baru diformat, tanpa reformat luas source.

Pada run kontrak offline ini belum dijalankan: profil Yahoo IDX nyata (probe
lanjutan tercatat pada bagian di atas), penerimaan/kalibrasi fundamental dan
corporate events, jawaban agent dengan LLM nyata, backend penuh, build/test
frontend (tidak ada perubahan UI), Linux/proxy/TLS atau deployment. Hak data
tetap riset pribadi lokal; remote/publik belum diterima. RESEARCH-01/02/03 penuh,
DATA/RULE dan RELEASE-01 tetap terbuka, Local Data Bridge belum diterima,
backtest IDX nonaktif dan paper/live terpisah. Tidak ada broker order, akun,
dependency baru, staging, commit, reset, publish atau service pengguna diubah.

## Deployment follow-up — 2026-11-11

**Verifikasi Linux terblokir karena lingkungan belum tersedia; backup/restore
Windows sintetis dibuktikan terpisah.** Tidak ada perubahan kode produk atau
aktivasi deployment. Empat dokumen diperbarui: status, backlog, panduan deployment
dan catatan ini. RTK.md tetap tidak ditemukan; tidak dibuat penggantinya.

Grounded: template unit/environment/proxy, `src/api/server_cli.py:12`,
`src/api/security.py:166`/`:403`/`:473`, `src/config/paths.py:13`,
`src/api/helpers.py:32`, resolver UI `src/api/frontend.py:6`,
`src/api/sessions_routes.py:443`/`:854` dan `src/session/service.py:275`.
Konsumen browser `frontend/src/lib/api.ts:17`, `apiAuth.ts` dan `useSSE.ts`
memisahkan request biasa tanpa replay otomatis dari reconnect stream berticket.
Blast radius: dokumentasi saja. Invariants: seluruh kode/pekerjaan sebelumnya,
index, gate auth/mandate/kill switch/read-only/shell opt-in dan batas pasar tetap.
Verify: discovery read-only, ekspresi pre-start, snapshot stopped/restore/API,
hash seluruh baseline publik, inventory/status NUL, byte index, tautan/UTF-8/diff.

### Lingkungan dan kontrak deployment

`wsl.exe --list --verbose` exit **1** dan `wsl.exe --status` exit **50**:
`The Windows Subsystem for Linux is not installed.` Docker/Podman/Nginx/
`systemd-analyze`/Multipass/Lima tidak ditemukan melalui PATH; executable
Docker/Podman tidak ada pada dua lokasi instalasi umum yang dicatat di receipt.
Tidak ada service runtime terkait yang ditemukan pada discovery service.
Tidak ada guest/container milik pengguna yang dibuka atau diubah, instalasi,
aktivasi service, perubahan konfigurasi sistem, unduhan dependency/image atau
resource berbayar. Temuan ini membuktikan jalur lokal yang dicek tidak tersedia;
bukan inventaris seluruh host remote milik pengguna.

Unit tetap mengikat backend 127.0.0.1:8899, satu proses, HOME di
`/var/lib/vibe-trading` dan VIBE_TRADING_HOME di subdirektori `runtime`.
Settings dotenv di HOME/.vibe-trading berbeda dari structured runtime; keduanya
termasuk scope backup. API_AUTH_KEY bersama bukan isolasi tenant atau jaminan
seluruh API read-only. Launcher lokal tanpa key masih mengizinkan mode developer;
kewajiban key deployment ada pada **ExecStartPre unit**, bukan klaim launcher
menolak semua startup tanpa key. Ekspresi dari unit aktual diuji dengan
absent/kosong/whitespace → **exit 1**, sintetis → **exit 0**, tanpa mencetak key.
Ini bukan `systemd-analyze verify` atau eksekusi unit Linux.

Proxy menimpa Host/forwarding, memakai `$uri` tanpa query untuk access log,
mematikan buffering/cache/retry upstream dan menolak shutdown exact path.
Itu hasil pembacaan konfigurasi, bukan bukti runtime Nginx. Karena Host upstream
ditimpa, Host asli asing perlu gate virtual host penolak dan pengujian di proxy;
guard backend tidak membuktikannya. Template listen 80/443 harus diadaptasi pada
salinan QA ke 127.0.0.1/port tinggi sebelum eksekusi lokal.

### Backup dan restore yang benar-benar dijalankan

QA baru di luar repo:
`%TEMP%\idx-deployment-followup-30822d55de`.
Sebelum edit disimpan 3.177 hash publik ditambah 39 hash kode publik supplemental
(nama `src/memory`, `src/live/runtime` dan modul credential adalah kode, bukan
state/secret), total **3.216**, inventory/status Git UTF-8 NUL dan salinan index.
Script `verify_session.py` dan `smoke_installed.py` QA sebelumnya dibaca dahulu;
artefak lama tidak ditimpa. Wheel lama diikat ulang ke SHA-256 manifest asli dan
seluruh member Python dengan counterpart source sekarang cocok byte; diekstrak
ke direktori QA baru, tanpa install/build. Runtime memakai interpreter proyek
existing, bukan provisioning venv bersih atau dependency Linux.

Perintah dari root, dengan `<QA>` direktori di atas:

```text
.venv/idx312/Scripts/python.exe <QA>/inspect_environment.py
.venv/idx312/Scripts/python.exe <QA>/check_prestart.py
.venv/idx312/Scripts/python.exe <QA>/backup_restore_v4.py
.venv/idx312/Scripts/python.exe <QA>/verify_followup.py
```

Harness menjalankan paket dari luar checkout dengan HOME/USERPROFILE/AppData/
runtime disposable, environment allowlist dan guard DNS/socket Python loopback
yang diadaptasi dari QA lama. Guard ini bukan sandbox jaringan OS; preflight
eksternal yang ditolak bukan integrasi provider. Tidak ada dotenv nyata,
credential atau state akun dibaca. API membuat sesi sintetis **201** melalui
SessionService; child memakai SessionStore existing untuk menulis satu pesan
sintetis tanpa LLM. GET sesi/pesan/list **200**, tanpa key **401**.

Proses pertama dihentikan melalui shutdown lokal berautentikasi **200**, exit
**15**, port **51136 tertutup** sebelum snapshot. ZIP stopped snapshot berisi
**11 file**, sumber tidak berubah selama salinan, lalu diekstrak ke home kedua;
seluruh hash file cocok **sebelum** startup restore. API proses kedua membuktikan
ID/title dan isi pesan sama, sesi/pesan/list **200**, tanpa key **401**.
Shutdown lokal **200**, exit **15**, port **51552 tertutup**. Key sintetis tidak
ada pada kedua log final. Tidak menguji ticket pada run ini; sanitasi ticket
melalui proxy masih terbuka.

Backup sintetis `restore-attempt-4/synthetic-stopped-backup.zip`, SHA-256:
`9f29f87ce97d86bbc9c5121247fa8da766bea56bc99412b1d56f93e3386b3978`.
Direktori HOME/.vibe-trading termasuk tetapi **kosong**: bukan bukti pemulihan
Settings/secret produksi. Snapshot sintetis ini tidak menguji enkripsi/retensi,
power loss, backup concurrent, permissions/ownership Linux, semua jenis state,
atau shutdown finalizer graceful. Tidak ada state asli yang disalin/dipulihkan.

Percobaan harness dipertahankan: v1 gagal `FileNotFoundError [WinError 2]`
karena interpreter temporer lama hilang, sebelum proses server dibuat; v2 gagal
`AssertionError: startup deadline exceeded` pada batas 75 detik; v3 mencapai API
tetapi gagal `assert record['port_closed']` karena pemeriksaan terlalu cepat
setelah terminate. Probe cleanup berikutnya mendapat connection refused;
run final menunggu penutupan port dan memakai shutdown berautentikasi.
Port percobaan **54274/64199** juga dicek kembali tertutup. Ini koreksi harness,
tanpa reproduksi bug produk atau perubahan runtime. v4 **exit 0**, bukan klaim
semua percobaan lulus. Tidak mengulang suite penuh, regresi Windows lama,
build/test frontend atau provisioning dependency.

### Gate tersisa dan artefak

Prasyarat minimum: lingkungan Linux disposable **sudah tersedia** dengan runtime
dan dependency aplikasi untuk Linux, Nginx, systemd-analyze dan alat sertifikat
existing. Tidak memasang atau menarik image otomatis. Perlu salinan konfigurasi
QA loopback, CA/sertifikat sintetis SAN yang cocok dan trust store khusus QA,
tanpa TLS bypass. Belum dijalankan: `systemd-analyze verify`, `nginx -t`, startup
native Linux, UI/deep links/auth/Host/Origin/forwarding/shutdown **melalui proxy**,
TLS, SSE deterministik streaming/buffering/cancel/timeout, tanpa retry write dan
tanpa key/ticket pada log proxy; backup/restore Linux juga belum dibuktikan.

Receipt `environment-checks.json`, `prestart-checks.json`, source binding
`restore-attempt-2/current-package-binding.json`, `restore-attempt-4/backup-restore.json`,
`backup-manifest.json` di subdirektori yang sama, log final serta script v1–v4
menyimpan bukti. `verification.json`, `session.diff`, `current-reviewed-files.json`
dan `evidence-hashes.json` merekonsiliasi perubahan sesi ke baseline/source saat
ini; `index-before` dan inventory/status NUL mempertahankan bukti Git.

Hak data tetap riset pribadi lokal Yahoo/yfinance; remote/display/redistribusi/
publik belum diterima. Local Data Bridge/currency gate, backtest IDX nonaktif,
paper/live terpisah dan Index Alpha ditunda. DEPLOY-PREP-01 tetap selesai hanya
sebagai persiapan; RELEASE-01 dan deployment aktual **belum selesai**. Tidak ada
akun, broker order, staging, commit, reset, publish atau listener publik.

## Deployment local — 2026-11-05

**Persiapan satu operator dan QA paket lokal selesai; deployment publik belum
dilakukan.** Scope ini mengerjakan kode/config/package tanpa akun atau input
provider baru. Shared key mengautorisasi satu operator, bukan identitas atau
isolasi pengguna. [Panduan dan template](../deployment/single-operator/README.md).

Grounded: status/backlog, panduan kontribusi/keamanan, pemilik auth di
`src/api/security.py:383`/`:403`, launcher `src/api/server_cli.py:15`, distribusi
`setup.py`, path state `src/config/paths.py`, serta tes auth/bind/packaging.
Blast radius: dua pemilik runtime, dua modul tes, dua README, status/backlog,
catatan ini dan empat file template. Invariants: key-first auth, Host/origin,
shell opt-in, mandate/kill switch/read-only, state di luar source, perubahan
sebelumnya/index tetap; tanpa listener eksternal, secret nyata atau order.
Verify: regresi red/green, wheel offline, real HTTP dua startup/restart,
persistensi sesi sintetis, hash aset/UI/code dan integritas Git.

### Bug yang direproduksi dan diperbaiki

Enam tes baru gagal pada kode awal: port Origin nonnumerik/out-of-range
menimbulkan ValueError tak tertangani; Origin loopback dengan port cacat melewati
penolakan origin; kedua varian backend `--dev` men-spawn Vite `0.0.0.0`.
Parser kini memvalidasi port sebelum menerima loopback atau membandingkan host,
sehingga guard memberi 403 terstruktur. Launcher memakai Vite `127.0.0.1`
untuk backend loopback maupun explicit remote. API bind existing tetap kompatibel.
Red akhir **6 failed/77 deselected**; bukan klaim kegagalan seluruh suite.

Perintah dari root memakai `.venv/idx312/Scripts/python.exe -m pytest`:

```text
agent/tests/test_security_auth_api.py agent/tests/test_serve_bind.py
  -k "malformed_origin_port or dev_frontend_stays" -q --allow-hosts=127.0.0.1,::1 --tb=line

agent/tests/test_security_auth_api.py agent/tests/test_serve_bind.py
agent/tests/test_api_entrypoints.py agent/tests/test_auth_precedence.py
agent/tests/test_sse_ticket_and_headers.py agent/tests/test_readonly_default.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short

agent/tests/test_frontend_distribution.py agent/tests/test_sdk_order_gate.py
agent/tests/test_mandate_enforcement.py agent/tests/test_killswitch_blocks_orders.py
  -q --allow-hosts=127.0.0.1,::1 --tb=short
```

Regresi pertama **128 passed/2 warnings**; packaging/safety **117 passed/1
warning**. Tes packaging memakai backend setuptools yang telah tersedia lewat
PYTHONPATH fixture dan pip no-index/no-build-isolation/no-deps; dependency tidak
diunduh. Warning existing anyio/Starlette tercatat. Ruff lint empat file lulus.
`ruff format --check` tetap gagal pada **empat file baseline maupun current**;
rekonstruksi baseline diverifikasi ke SHA-256 pra-edit. Perbedaan format existing
tidak ditimpa dengan reformat luas atas pekerjaan lama. Ini bukan klaim format
bersih. Tes regresi dan HTTP menjadi verifikasi perilaku; tidak ada reviewer
independen untuk audit deployment menyeluruh.

### Wheel baru dan uji HTTP terisolasi

QA baru: `%TEMP%\idx-deployment-local-70d48e18ca`.
Baseline sebelum edit: 3.212 hash file publik, inventory/status Git UTF-8 NUL
dan salinan/hash index. Script QA lama dibaca sebelum adaptasi; artefak lama
tidak ditimpa. Salinan publik di luar repo tidak membawa dotenv/state privat.
**262 file sumber frontend** sama dengan sesi DEV-PACK-01; **143 aset build**
dipakai kembali dan dibandingkan byte/hash di wheel. Tidak ada build/test UI baru.

Wheel `vibe_trading_ai-0.1.18-py3-none-any.whl`, **18.171.687 bytes**, SHA-256
`26eaafc717d0e64fabf1ee2ad26f3c6f82c0f5897b763d4bf26f4843726bf739`.
Build: `python -m pip wheel --no-index --no-build-isolation --no-deps` pada
salinan; backend existing dari QA DEV-PACK-01. Install:
`python -m pip install --no-index --no-deps --target <QA>/installed-pip <wheel>`.
Ini target install dengan dependency dari clean-venv terverifikasi sebelumnya,
**bukan provisioning dependency/venv bersih baru**. `pip check`: No broken
requirements found. Import API/security/CLI/UI berasal dari target wheel,
tanpa PYTHONPATH source. Home/appdata/runtime sementara dan key khusus QA
sintetis; tidak ada akun/credential pengguna. Guard DNS/socket Python membatasi
ke loopback, bukan sandbox jaringan OS. Preflight provider eksternal ditolak
guard; bukan bukti integrasi provider.

Dua startup `python -m cli serve --host 127.0.0.1 --port <sementara>` dari luar
checkout membuktikan:

- UI `/`, `/research/idx`, `/correlation`, `/runs/deployment-qa` dan aset: **200**;
  CSP, nosniff dan frame denial ada pada respons.
- API riset tanpa/salah key **401**; key valid mencapai validasi body **422**,
  tanpa memanggil data provider. Origin port cacat/cross-site dan Host asing **403**.
- Header proxy sintetis Host domain/forwarded IP/HTTPS: tanpa key **401**,
  key valid **422**. Ini menguji app/Uvicorn, bukan Nginx/TLS sebenarnya.
- `/health` **200**, `/ready` **503** tanpa LLM. Sesi sintetis dibuat **201**,
  lalu sesudah stop/start terbaca **200** dengan title sama di VIBE_TRADING_HOME.
- `/system/shutdown` lokal **200**, kedua proses exit 15 dan kedua port tertutup.
  Windows SIGTERM ini tidak membuktikan semua finalizer shutdown graceful atau
  backup/restore. Endpoint itu ditolak pada template proxy, belum diuji di Nginx.

Unit pre-start expression diuji dengan key absent/blank/whitespace (exit **1**)
dan key sintetis (exit **0**) tanpa mencetak key. Nginx/systemd/Docker tidak
tersedia di QA ini; validasi sintaks dan eksekusi native, sertifikat/TLS,
proxy SSE, image/lock Linux, retensi/restore backup dan host tujuan belum diuji.
Template hanya persiapan dan tidak diaktifkan. Audit ini tidak menerima hak
display remote/publik atau menutup RELEASE-01/DATA/RULE/RESEARCH penuh.

`red.xml`, `regression.xml`, `packaging-safety.xml`, `http-checks.json`,
`installed-origins.log`, `pip-check.log`, `prestart-checks.json`,
`format-comparison.json`, `package.json` dan log server menyimpan hasil aktual.
`verification.json`/`session.diff` merekonsiliasi hanya perubahan sesi ini;
bundle review wheel/template di luar repo tidak berisi state QA atau secret.
Tanpa dependency baru, staging, commit, reset, publish atau deployment.

## Follow-up kandidat publik baru — 2026-11-05

Dokumentasi primer Invezgo Stock Chart memberi deklarasi seluruh OHLC Rupiah,
volume lembar dan sesi WIB, dengan peringatan bahwa suffix `Z` bukan UTC.
Terms API memerlukan akun/paket Developer/key dan melarang distribusi ulang.
Sampel dokumentasi bukan original BBCA/BBRI target 26–30 Oktober 2026;
adjustment, board/market, vintage/revisi dan hak penggunaan terikat file belum
terpenuhi. Halaman OHLC ERPIW menyatakan data belum diunggah.
[Sumber primer, keputusan dan paket pembuka](IDX_PRIMARY_INPUT_DISCOVERY.md#new-public-candidates-disposition--2026-11-05).

Pencarian terbatas ini selesai tanpa penerimaan data. Jalur Invezgo tidak dapat
dieksekusi dalam batas tanpa akun/key; jalur ERPIW belum menyediakan original.
Review berikutnya membutuhkan paket original berizin beserta deklarasi/terms,
melalui ekspor resmi normal bila berfungsi, sampel publik berizin baru atau
pemegang yang secara eksplisit boleh membagikannya. Tidak meminta pengguna
menyusun JSON, membuka akun, membeli atau menghubungi provider. Tidak mengulang
halaman BEI gagal atau kandidat lama. Local Data Bridge/currency gate tetap;
backtest nonaktif, paper/live terpisah dan Index Alpha ditunda.

QA baru: `%TEMP%\idx-new-source-review-3fe8287b91`.
Empat HTML primer asli beserta receipt HTTP 200, ekstraksi dan SHA-256 disimpan
di luar repo; timestamp akuisisi dokumen bukan vintage harga. Baseline 3.212
file publik, status/inventory Git UTF-8 NUL dan index disimpan sebelum edit.
Hanya empat dokumen diperbarui. Tanpa perubahan kode, API/data request,
normalisasi, helper/CLI intake, tes runtime/frontend/build, integrasi provider,
deployment, dependency baru, staging, commit, reset atau publish.

## Pemeriksaan panduan primer BEI — 2026-11-05

Manual v1.2 yang ditautkan publikasi resmi kini **berhasil diunduh tanpa login**
melalui tombol Download preview individual Drive: 981.358 bytes, tujuh halaman.
Semua halaman diekstrak, dirender dan diperiksa. Volume ringkasan dinyatakan
sebagai saham yang ditransaksikan di pasar reguler/tunai/negosiasi; keterangan
adjustment gainers/losers terbatas pada perbandingan harga antarhari. Manual
tidak menyediakan OHLCV BBCA/BBRI atau deklarasi seluruh OHLC terikat ekspor.
[Hash/receipt, bukti halaman dan keputusan](IDX_PRIMARY_INPUT_DISCOVERY.md#official-manual-disposition--2026-11-05).

Jalur dokumentasi ini selesai, **penerimaan OHLCV dihentikan menunggu satu paket**:
file asli BBCA/BBRI untuk target review 26–30 Oktober 2026 (whole-market boleh),
deklarasi sumber terikat file untuk identitas/venue/board/market, currency dan
adjustment semua OHLC, volume saham versus lot antrean, sesi/timezone,
coverage/vintage/revisi serta terms yang mencakup metode dan penggunaan lokal
aktual. Peroleh lewat ekspor resmi normal bila kembali berfungsi beserta
dokumennya, atau paket dari pemegang berizin; JSON buatan pengguna tidak diperlukan.
Review bisa lanjut tanpa akun/outreach jika paket lengkap itu tersedia; manual
publik ini sendiri belum membuktikan jalur OHLCV lengkap. Penggunaan pribadi
tidak otomatis nonkomersial; surat khusus tidak otomatis wajib jika terms publik
terbukti berlaku. Tidak mengulang halaman 403 atau audit PDF statistik sebelumnya.

QA: `%TEMP%\idx-manual-review-0fb99aa78f`, berisi
original, receipt (status/header/timestamp request tidak diekspos: null), ekstraksi,
render, keputusan dan verifikasi. Baseline 3.212 file publik, inventory/status
UTF-8 NUL dan index disimpan sebelum edit. Empat dokumen saja diperbarui;
tanpa permukaan runtime baru, normalisasi atau helper/CLI/provider probe.
Tes backend/frontend/build tidak diulang. Currency gate, Local Data Bridge
belum diterima, task penuh terbuka, backtest nonaktif, paper/live terpisah dan
Index Alpha ditunda tetap berlaku. Tidak ada integrasi provider, deployment,
staging, commit, reset atau publish; perubahan sebelumnya dipertahankan.

## Pemeriksaan file statistik resmi — 2026-11-05

Jalur alternatif memberi file asli baru: PDF IDX Daily Statistics 30 Oktober
2026, 1.974.315 bytes/9 halaman, diunduh tanpa akun lewat tautan halaman Statistik
BEI. Seluruh halaman diekstrak dan dirender memakai dependency existing/bundled.
**Ditolak untuk intake OHLCV harian BBCA/BBRI**: peringkat volume/nilai/frekuensi,
harga previous/today pada gainers/losers serta ringkasan indeks/agregat tidak
menyediakan Open/High/Low/Close lengkap per saham. Tidak ada bar dinormalisasi.
[Receipt/hash, bukti halaman dan keputusan](IDX_PRIMARY_INPUT_DISCOVERY.md#official-statistics-file-review--2026-11-05).

Lampiran halaman 9 memberi terms publikasi nonkomersial bersyarat dan tautan
manual ke folder Google Drive publik tanpa login. Listing manual v1.2 terbaca;
preview/unduhan belum berhasil, sehingga isi manual tidak dipakai sebagai
deklarasi data. Kegagalan sertifikat GET lokal dan timeout unduhan browser
dicatat, tanpa melemahkan TLS atau mengotorisasi akun. Tidak mengunduh empat
laporan harian lain setelah file pertama gagal memenuhi scope OHLCV.

QA baru: `%TEMP%\idx-statistics-intake-40a7db5844`.
File asli, receipt dengan status/header HTTP yang tidak diekspos ditandai null,
ekstraksi, render, review dan hash bukti tersimpan di luar repo. Baseline sebelum
edit: 3.212 hash publik, status/inventory Git UTF-8 NUL dan salinan index.
Hasil akhir: `verification.json`/`session.diff`. Hanya empat dokumen diperbarui;
tanpa permukaan runtime baru, tes backend/frontend/build tidak diulang.
Implementasi, integrasi provider dan deployment tidak berubah; penerimaan data
OHLCV, Local Data Bridge dan task penuh tetap terbuka. MVP Yahoo/yfinance tetap
read-only lokal; backtest nonaktif, paper/live terpisah dan Index Alpha ditunda.
Perubahan lama dipertahankan, tanpa staging/commit/publish.

## Disposisi unduhan resmi — 2026-11-05

Satu jalur penerimaan ekspor BEI ditelusuri dan **dihentikan menunggu paket
input eksternal**. Halaman Ringkasan Saham kanonik hanya menampilkan kerangka,
tanpa tabel, tanggal atau tombol unduhan; browser mencatat SyntaxError dan
ChunkLoadError aset JavaScript. GET publik biasa terpisah mendapat HTTP 403;
tidak ada retry, host alternatif atau endpoint tersembunyi yang digunakan.
[Bukti, batas sebab kegagalan dan paket minimum](IDX_PRIMARY_INPUT_DISCOVERY.md#official-download-disposition--2026-11-05).
Belum ada file pasar untuk diuji kualitasnya. Tidak mengisi metadata dari label
kolom atau hasil indeks pencarian. Currency gate tetap menolak local tanpa IDR.

Paket pembuka dipersempit ke file asli BBCA/BBRI dalam window 26–30 Oktober 2026,
deklarasi terikat file untuk seluruh OHLC/volume/sesi/board/adjustment,
vintage/revisi/cakupan, receipt dan terms yang berlaku untuk penggunaan aktual.
Pengguna tidak perlu menyiapkan JSON. Unduhan publik normal dan dokumentasinya
dapat menghindari akun/outreach jika tersedia; sesi ini belum dapat memperoleh
keduanya. Izin nonkomersial tidak otomatis mencakup semua riset investasi pribadi.
Surat khusus bukan prasyarat otomatis bila terms publik terbukti mencakupnya.

QA baru di luar repo:
`%TEMP%\idx-official-export-bb4af937a4`.
Baseline sebelum edit memuat 3.212 hash file publik yang sebelumnya direview,
status/inventory UTF-8 NUL dan salinan index. Receipt/hash respons 403, transkripsi
observasi browser dan scope pencarian disimpan terpisah; bukan receipt dataset.
Hash HTML terms terdahulu cocok. Hasil akhir ada di `verification.json` dan
`session.diff`. Perubahan sesi hanya empat dokumen, tanpa permukaan runtime baru;
tes backend/frontend/build tidak diulang. Tidak ada implementasi metadata,
penerimaan data, integrasi provider atau deployment. DATA-01/02/03, IDX-02,
RULE-01 dan RESEARCH-01 penuh tetap terbuka; MVP read-only Yahoo/yfinance,
backtest nonaktif, paper/live terpisah serta penundaan Index Alpha tetap.
Seluruh perubahan lama dipertahankan; tanpa staging, commit atau publish.

## Ketentuan penggunaan website BEI — 2026-11-05

Ditemukan dan dibaca dokumen primer baru: ketentuan website BEI memberi izin
penggunaan nonkomersial bersyarat atribusi sumber/tanggal akses dan melarang
scraping/crawling. [Klausa, interpretasi terbatas dan keputusan kandidat](IDX_PRIMARY_INPUT_DISCOVERY.md#official-website-permission-evidence--2026-11-05).
Ini mempersempit gap izin bagi ekspor langsung yang metode/file/penggunaannya
terbukti tercakup; tidak otomatis memerlukan surat khusus. Tidak membuktikan
hak distribusi Pholenk, entitlement TICMI atau semantik OHLCV. Klasifikasi
penggunaan aktual dan ketentuan produk/file tetap perlu diperiksa.

HTML asli HTTP 200, receipt request/completion/header dan SHA-256 berada di
`%TEMP%\idx-website-terms-de60696324`.
Tidak mengunduh file pasar, mengulang audit CSV atau mengisi metadata. Jalur
publik tambahan TICMI/Kaggle belum memberi spesifikasi yang memenuhi intake;
akses restricted/403 tidak dilewati. Tidak ada outreach, akun atau pembelian.

Empat dokumen saja diubah; baseline sebelum edit memuat 3.212 hash publik,
status/inventory UTF-8 NUL dan salinan/hash index. Hasil pemeriksaan akhir di
`verification.json`/`session.diff` QA baru. Tidak ada permukaan runtime baru;
Verifikasi lulus: 205 tautan/anchor lokal, UTF-8, receipt/hash HTML dan
`git diff --check`. Sebanyak 3.208 file baseline lain identik, tanpa file
baru/hilang; inventory/status dan byte index tetap identik (SHA-256 index
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`).
backend/frontend test/build tidak diulang. Belum ada penerimaan data, integrasi
provider atau deployment. Currency gate, Local Data Bridge belum diterima,
backtest nonaktif dan semua task penerimaan penuh tetap. Tanpa staging/commit.

## Keputusan kandidat primer — 2026-11-05

Pholenk dan TICMI kini memiliki keputusan **menunggu input spesifik** beserta
jalur pembukanya di [catatan discovery](IDX_PRIMARY_INPUT_DISCOVERY.md#follow-up-decision--2026-11-05).
Pohon Pholenk lengkap (2.106 entri/983 CSV saham), riwayat README/schema,
rilis/issues kosong dan pencarian repo penerbit diperiksa. Patch schema terakhir
hanya memperbaiki path; tidak mengikat CSV ke recipe/sumber atau memenuhi
currency/unit/sesi/adjustment/vintage/rights. Halaman ketentuan umum TICMI baru
terbaca, tetapi belum memberi kontrak OHLCV atau entitlement proyek. Pencarian
terarah dihentikan sampai input yang disebutkan tersedia; tidak mengulang audit
Mendeley, Lensetek 404 atau katalog/PDF BEI yang sudah dibatasi.

Dokumen asli dan receipt baru disimpan di luar repo:
`%TEMP%\idx-primary-decision-ab6c683ecb`.
Empat dokumen Pholenk HTTP 200 cocok dengan blob commit yang dipatok; halaman
umum TICMI HTTP 200 memiliki hash/timestamp tersendiri. Tidak ada CSV diunduh
atau intake loader baru karena review hak/semantik belum memenuhi minimum.
Satu subset/window pribadi dapat direview setelah deklarasi dan izin tersedia;
tidak perlu menunggu paket historis seluruh pasar untuk review terbatas itu.

Receipt discovery sebelumnya dan tiga JUnit packaging/absent-backend/startup
direkonsiliasi dengan kode fixture serta gate riset/importer saat ini. Hasil
7 passed, 4 passed/3 skipped dan 129 passed tetap **historis**, bukan run baru.
Suite penuh belum diulang setelah perubahan fixture packaging; sesi ini tidak
mengubah kode yang membenarkan pengulangan. Tidak ada permukaan runtime baru.

Perubahan sesi hanya empat dokumen: status, backlog, catatan ini dan discovery.
Baseline baru memuat 3.212 hash publik, status/inventory Git UTF-8 NUL dan
salinan index. Verifikasi dokumen, diff sesi, hash/inventory/index serta batas
pemeriksaan disimpan dalam `verification.json`/`session.diff` QA baru.
Pemeriksaan akhir lulus: 202 tautan/anchor lokal, UTF-8, lima receipt unduhan
dan `git diff --check` (warning LF/CRLF existing tercatat di log). Sebanyak
3.208 file baseline lain identik, tanpa file baru/hilang; inventory/status Git
identik dan index byte-identik dengan SHA-256
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Local Data Bridge belum diterima; gate currency tetap menolak; backtest IDX
nonaktif, paper/live terpisah dan Index Alpha ditunda. DATA-01/02/03, IDX-02,
RULE-01 dan RESEARCH-01 penuh tetap terbuka; BASE-02 bukan baseline pra-IDX.
Tanpa dependency, dotenv/state akun, outreach, akun, pembelian, staging, commit,
publikasi atau deployment. Frontend test/build dan suite hijau tidak diulang.

## Packaging offline dan input primer baru — 2026-11-05

**Gap eksekusi tiga tes packaging ditutup pada fixture offline:**
modul `test_frontend_distribution.py` **7 passed, 1 warning**, 30,49 detik;
regresi startup/auth/SPA terpisah **129 passed, 2 warnings**, 103,97 detik.
Dengan backend tidak tersedia, kontrol terpisah **4 passed, 3 skipped,
1 warning**, sebelum pembuatan builder. Angka ini tidak dijumlahkan dengan
hasil suite penuh historis di bawah.

Grounded: fixture `build_python`, helper `build_wheel`, install editable,
`setup.py`, manifest dan receipt packaging/full-backend sebelumnya. Fixture
lama membuang PIP_NO_INDEX milik parent dan membiarkan pip build isolation
memprovision dependency. Satu regresi boundary subprocess membuktikan command
lama kekurangan `--no-index` dan `--no-build-isolation` (**1 failed sebelum
fix**, tanpa menjalankan pip). Helper/fixture tes kini memakai environment
allowlist bersama, mematikan konfigurasi/cache/index pip serta user site,
mempertahankan home/appdata/identitas sintetis, dan memakai flag
`--no-index --no-build-isolation --no-deps` pada wheel maupun editable install.
Backend setuptools harus sudah tersedia; absent menghasilkan skip eksplisit,
bukan unduhan otomatis. Venv builder memakai pip bawaan Python. Assertion
wheel/aset, hilangnya source, remediasi build UI dan editable tetap dipertahankan.
`setup.py`, MANIFEST, backend produk, frontend dan dependency manifest tidak diubah.

Python proyek tetap `.venv/idx312/Scripts/python.exe`, versi 3.12.13. Untuk bukti
eksekusi ini, **579 file backend setuptools 84.2.1 yang telah tersedia** di QA
DEV-PACK-01 disalin ke QA baru dan diverifikasi SHA-256; tidak memasang atau
mengunduh dependency baru. Venv/instalasi fixture hanya berada di QA baru:
`%TEMP%\idx-primary-packaging-a40765e73b`.
Source publik, runtime/home/USERPROFILE/APPDATA/LOCALAPPDATA/temp/cwd terisolasi
sebelum import proyek; getpass memakai `qa-user`, tanpa secret/config akun asli.
Dotenv di luar QA ditolak, template berasal dari snapshot dan fixture sintetis.

Guard audit baru mendecode argv native Windows, termasuk Popen executable=None,
dan menolak pip wheel/install yang tidak membawa ketiga flag offline. Jalur
guard Python diwariskan ke subprocess, termasuk builder dan probe paket terpasang.
Audit seluruh run tes sesi ini: **23 spawn, 27 startup guard Python**, tiga
operasi pip (**wheel, wheel, install**) dengan flag offline, seluruh home/cwd
startup tercatat di QA, **nol percobaan DNS/socket eksternal teramati**.
Backend yang disalin tetap cocok dengan receipt. Ini bukti Python/child fixture,
bukan sandbox jaringan OS atau jaminan untuk native code/proses arbitrer.
Pencarian web primer dijalankan terpisah dari run tes offline ini.

Regresi 129 tes mencakup file/modul/CLI entry point, bind, SPA deep link,
auth precedence/security, preflight dan pemilik scheduler lifespan memakai
fixture. Tidak mengubah auth/assembler/lifespan/scheduler; tidak memakai broker
nyata atau server externally reachable. Warning adalah deprecation anyio/pytest
dan Starlette/httpx existing. Ruff lint dan format file tes lulus.

Perintah aktual dari root proyek:

```powershell
$qa = '%TEMP%/idx-primary-packaging-a40765e73b'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" packaging "$qa/checkout/agent/tests/test_frontend_distribution.py" --allow-hosts=127.0.0.1,::1 -v --tb=short --junitxml="$qa/packaging.xml"
.venv/idx312/Scripts/python.exe "$qa/run_without_backend.py" missing-backend "$qa/checkout/agent/tests/test_frontend_distribution.py" --allow-hosts=127.0.0.1,::1 -v --tb=short --junitxml="$qa/missing-backend.xml"
.venv/idx312/Scripts/python.exe -m ruff check agent/tests/test_frontend_distribution.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_frontend_distribution.py
git diff --check
```

`startup-regression.xml` memuat seleksi tujuh modul/129 tes; `red.xml`,
`packaging.xml`, `missing-backend.xml`, log, `test-summary.json`, audit dan
`existing-backend-receipt.json` menyimpan bukti masing-masing. Baseline baru
memuat 3.211 hash publik, inventory/status NUL UTF-8 dan salinan/hash index.
Baca runner sebelum penggunaan ulang dan buat direktori QA baru.
Contributor guide kini menjelaskan prasyarat backend dan batas tes offline.

Atas permintaan pengguna, pencarian **jalur primer baru** menghasilkan
[metadata/schema/preview Pholenk serta ketentuan layanan TICMI](IDX_PRIMARY_INPUT_DISCOVERY.md).
Receipt GitHub dipatok ke commit; tanggal metadata lama/schema dibedakan dari
metadata current, dan lisensi database tidak dianggap izin data hulu. Lensetek
hanya search-index karena repository/raw 404; tidak diimplementasikan. Tidak
mengulang audit CSV/notebook Mendeley atau terms yang sebelumnya terblokir.
Belum ada input yang memenuhi seluruh deklarasi OHLCV/tanggal/vintage/rights,
atau rantai kalender/rulebook lengkap. Tidak ada outreach, akun atau pembelian.

MVP pribadi tetap diterima; Local Data Bridge/currency gate, DATA-01/02/03,
IDX-02, RULE-01 dan RESEARCH-01 penuh tetap terbuka. Backtest IDX nonaktif,
paper/live terpisah dan Index Alpha ditunda. BASE-02 tetap bukan baseline
pra-IDX. BASE-03 sudah memiliki keputusan tracking menurut CONTRIBUTING.md
(AGENTS lokal/untracked), tetapi referensi RTK.md tetap tidak ditemukan.
Tidak mengulang suite penuh/backend, frontend test/build, provider nyata,
Electron atau deployment pada follow-up ini. Tidak ada staging/commit/publish.

Pemeriksaan akhir: **200 tautan/anchor lokal**, UTF-8 dan `git diff --check`
lulus. **3.206 dari 3.211 file baseline** tetap identik; lima file existing
berubah dan satu catatan riset baru ditambahkan. Seluruh runtime produk,
manifest/dependency dan fixture data baseline tetap utuh. Index identik dengan
salinan baseline, SHA-256
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Daftar file, diff sesi dan receipt ada di `verification.json`/`session.diff` QA.

## Verifikasi backend Windows — 2026-11-05

**Suite penuh pascakoreksi lulus pada seleksi backend contributor guide:**
**22.213 passed, 231 skipped, 3 deselected, 28 warnings**, exit 0,
**1.244,93 detik**. Regresi terpisah **1.507 passed, 31 skipped, 2 warnings**
pada 57 modul, 134,91 detik. Angka run berbeda tidak dijumlahkan sebagai tes unik.
Ini memverifikasi checkout sekarang, bukan baseline sebelum implementasi IDX.

Grounded: AGENTS/status/backlog/contributor/security/fondasi dan receipt sesi
2026-11-04 dicocokkan dengan kode. RTK.md tetap absent. Baseline baru menyimpan
status Git dan inventory UTF-8 NUL, SHA-256 **3.211 file publik**, salinan/hash
index dan snapshot source publik melalui daftar path yang telah direview.
Tidak membaca dotenv nyata, konfigurasi pengguna atau state akun. QA historis
tidak ditimpa; artefak sesi baru berada di:
`%TEMP%\idx-backend-full-b52f0e0adf`.

### Kegagalan awal, reproduksi dan koreksi

- Run pertama sesi ini: **22.206 passed, 4 failed, 231 skipped, 28 warnings**,
  1.635,34 detik. Satu failure aplikasi terjadi pada
  `test_a_completed_run_leaves_a_queryable_record`: record tetap `running`.
  Traceback membuktikan **WinError 5 pada `BackgroundTaskStore` `os.replace`**,
  dipanggil melalui `BackgroundManager._persist`. Kasus asli lulus saat sendiri;
  bukan alasan mengabaikan kegagalan pada run penuh.
- Penulis atomik existing di `src/tools/background_store.py` kini memakai
  `src.atomic_file.replace_with_retry`, sama dengan store yang sudah dikoreksi.
  Batas tetap **6 percobaan**, khusus WinError **5/32**, backoff
  **25/50/100/200/400 ms**. Enam kasus baru menyuntikkan kegagalan di boundary OS:
  record terminal dapat dibaca setelah contention sementara; exhaustion/error
  lain mempertahankan byte record lama, membersihkan temp dan melempar objek
  error asli. Red sebelum fix **4 failed/2 passed**; modul setelah fix
  **30 passed/2 skipped/1 warning**. Kasus manager asli juga lulus dalam run penuh
  final. Fsync, format record, recovery, kepemilikan dan gate order tidak berubah.
  Cleanup saat error dan chmod setelah commit tetap best effort existing;
  verifikasi ini tidak membuktikan privasi ACL Windows.
- Tiga failure lain berasal dari **kesalahan seleksi harness**: `--deselect`
  absolut tidak cocok dengan node ID relatif Windows. Tes packaging sempat
  membuat venv QA dan menjalankan child pip build isolation; audit merekam DNS
  eksternal yang ditolak. Tidak ada perubahan dependency proyek. Keberhasilan
  packaging offline tidak diklaim. Runner final memakai hook collection yang
  mencocokkan nama file/tes aktual dan menolak run penuh bila jumlah pengecualian
  bukan tepat tiga. Collection final **22.434/22.437 item, 3 deselected**, exit 0;
  tiga kasus provisioning tidak dieksekusi pada run final.

### Isolasi dan cakupan bukti offline

Python **3.12.13** proyek menjalankan snapshot di `corrected/checkout` dengan
home, USERPROFILE, APPDATA, LOCALAPPDATA, runtime, temp dan cwd QA **sebelum
import proyek**. Environment berasal dari allowlist dasar OS, tanpa meneruskan
secret; `getpass.getuser()` dibuktikan memakai `qa-user`. Sandbox conftest tetap
menjadi pemilik redirect runtime per tes. Template `.env.example` hanya berasal
dari snapshot publik; dotenv sintetis tes boleh di dalam QA, akses dotenv di
luar QA ditolak.

Pytest-socket membatasi host ke `127.0.0.1,::1` untuk asyncio Windows. Audit
tambahan menolak connect/bind non-loopback dan DNS eksternal, sambil membolehkan
parsing IP literal tanpa DNS jaringan. Probe harness membuktikan penolakan
connect, bind publik, DNS dan dotenv eksternal, serta startup guard child Python
dengan environment minimal. Tidak ada server externally reachable yang diizinkan.

Audit run penuh final mencatat **196 spawn**, **182 startup guard Python**,
**17 DNS ditolak**; semua startup tercatat memakai home/cwd di dalam QA dan semua
environment spawn tercatat membawa jalur guard. Pada Windows, 164 event Popen
melaporkan executable `None`, 32 `cmd.exe`; argv disimpan sebagai hash dan
fixture subprocess terkait ditinjau. Jumlah startup bukan klaim satu guard per
native child: shell/command native dan ekstensi C tidak otomatis dilindungi
socket guard Python. **Ini bukan sandbox jaringan OS atau bukti bahwa seluruh
child process arbitrer offline.** Tes provisioning dipisahkan, dan tidak ada
provisioning packaging pada run final. Tidak mengubah firewall/privilege,
Developer Mode, dependency, auth, assembler, lifespan atau startup scheduler.

**231 skip** tetap bukan hasil lulus: mencakup 10 collection skip, kemampuan
symlink/mode/POSIX/timezone/Unix yang tidak tersedia, extra opsional seperti
statsmodels/arch/adapter, prasyarat panel faktor sintetis, dan tes opt-in yang
memerlukan token/jaringan atau baseline manual. Alasan per kasus ada di
`corrected/full-summary.json` dan JUnit. Warning 28 tetap dicatat pada log,
termasuk deprecation dependency serta warning numerik/parsing fixture. Tidak
memasang extra atau melonggarkan assertion untuk menghilangkannya.

### Perintah, receipt dan status

Perintah run penuh (dari root proyek; runner menyiapkan environment terisolasi):

```powershell
$qa = '%TEMP%/idx-backend-full-b52f0e0adf/corrected'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" full "$qa/checkout/agent/tests" --ignore="$qa/checkout/agent/tests/e2e_backtest" --ignore="$qa/checkout/agent/tests/test_e2e_harness_v2.py" --allow-hosts=127.0.0.1,::1 -v --tb=short --junitxml="$qa/full.xml"
.venv/idx312/Scripts/python.exe "$qa/run_targeted.py"
.venv/idx312/Scripts/python.exe "$qa/lint_final.py"
git diff --check
```

Baca script sebelum memakai ulang dan buat direktori QA baru agar receipt ini
tidak tertimpa. `corrected/test-modules.json` memuat seleksi 57 modul termasuk
kontrol pasar/routing/config, policy shell, store dan gate order/mandate/
kill-switch/read-only. `red.xml`, `green.xml`, `targeted.xml`, `full.xml` beserta
log dan summary menyimpan bukti terpisah. `source-hashes.json` dan
`audit-summary.json` membuktikan **3.211 file snapshot tetap identik dengan
checkout yang diuji** setelah suite selesai; tidak ada source publik snapshot
yang dimutasi tes. Ruff **47 file Python** pada gabungan perubahan sebelumnya
dan sesi ini lulus. Baseline/index, diff sesi dan verifikasi dokumen disimpan
pada direktori induk QA.

Pemeriksaan akhir: **192 tautan/anchor lokal**, UTF-8 dan `git diff --check`
lulus. **3.206 dari 3.211 file baseline publik** identik; hanya store background,
tesnya, dokumen ini, PROJECT_STATUS.md dan TODO.md berubah. Inventory identik,
tanpa file publik baru. Seluruh **3.208 file snapshot selain tiga dokumen status**
tetap cocok dengan source yang diuji. Index identik dengan salinan baseline,
SHA-256 `4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`;
receipt akhir ada di `final-verification.json`. Tiga pembaruan dokumen tidak
memiliki permukaan runtime dan diperiksa melalui tautan/hash/diff.

MVP Yahoo/yfinance tetap riset pribadi lokal read-only UI/CLI, watchlist manual
maksimum delapan saham reguler `.JK`, harian IDR; keduanya satu vendor.
Local Data Bridge belum diterima dan currency gate tetap menolak. BASE-02,
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka, backtest IDX nonaktif,
paper/live terpisah, Index Alpha ditunda. Tidak ada riset Mendeley baru tanpa
input primer. Provider nyata, frontend test/build, packaging integrasi final,
Electron dan deployment tidak diuji pada sesi ini. Tanpa staging, commit,
publish, akun/otorisasi, kredensial atau order broker nyata.

## Verifikasi backend Windows — 2026-11-04

**Koreksi terverifikasi pada 57 modul; bukan klaim suite penuh pascakoreksi.**
Pengguna memilih verifikasi backend offline sambil menunggu bukti eksternal
Mendeley. Acceptance MVP pribadi tetap terpisah dari penerimaan Local Data Bridge,
baseline pra-IDX, backtest dan deployment.

Grounded: backlog/status/contributor/security, `DataConfig`, registry/accessor/
Settings, kebijakan tool, store Swarm/Task/live JobStore, pemanggil dan tes terkait.
Baseline menyimpan status Git dan inventory UTF-8 NUL, 3.207 hash file publik,
salinan index, serta snapshot source publik. Tes memakai Python 3.12.13 proyek,
salinan checkout dan home/appdata/localappdata/runtime/temp/cwd sementara;
dotenv nyata, konfigurasi pengguna dan state akun tidak dipakai. Koneksi pytest
dibatasi ke loopback untuk asyncio Windows; audit tambahan menolak koneksi dan
DNS eksternal, dengan parsing IP literal lokal tetap diperbolehkan.

Perubahan yang dibuktikan:

- `DataConfig` menambah string kosong default untuk
  `MARKET_DATA_ORDER_ID_EQUITY`. Regresi alias/serialisasi awal: **1 failed IDX,
  1 passed AS**. Registry tetap memiliki default/permutation/hot-apply; tidak ada
  chain baru atau deklarasi currency yang diisi dari classifier.
- `src.atomic_file` memiliki retry penggantian file WinError **5/32**, maksimal
  **6 percobaan**, dengan backoff **25/50/100/200/400 ms**. SwarmStore memakai
  primitive yang sama dengan TaskStore (termasuk dependency resolution) dan live
  JobStore. Error lain dan exhaustion tetap dilempar; log hanya memuat kode dan
  nomor percobaan. Pemilik tetap menangani temp/fsync/cleanup, tanpa perubahan
  scheduler lifecycle, mandate atau semantik order. **4 regresi deterministik
  awal gagal**; regresi store/native concurrency/gate kemudian **232 passed,
  3 skipped**. Tidak ada order atau akun broker nyata.
- Kebijakan tool mempertahankan pemeriksaan ulang command Python di Windows
  melalui bentuk argv terkutip yang kanonik. Hanya bentuk yang cocok persis
  setelah decode/render yang memakai parser native; input lain tetap melalui
  lexer dan gate existing. **5 regresi round-trip awal gagal**. Probe shell
  sintetis juga membuktikan kutip literal bersama metakarakter tertentu dapat
  ditafsirkan ulang `cmd.exe`; bentuk tersebut kini ditolak dengan arahan memakai
  file `.py`. Operator yang ditambahkan sesudah command tetap ditolak. Ini tetap
  filter kenyamanan, bukan sandbox Python atau pengganti gate live.
- Tes memakai pembacaan UTF-8 eksplisit dan fixture subprocess yang sesuai
  Windows. Symlink setup hanya skip pada WinError 1314; error lain tetap gagal.
  Host-timezone dan TCP diuji, sedangkan variasi POSIX/Unix yang tidak tersedia
  diberi alasan skip. Extra `statsmodels` tidak dipasang; regresi OU yang
  memerlukannya ditandai unavailable melalui skip modul.
- **8 fixture paper market/5m** dipulihkan dari CRLF ke LF **hanya setelah**
  setiap hasil LF cocok dengan SHA-256 manifest existing. Manifest dan nilai
  data tidak diubah. `.gitattributes` mematok EOL untuk dua jalur fixture tersebut.
  Inventaris SKILL/docstring MCP dan tujuh README kini sesuai **85 tool MCP**
  dan **119 tool agent keyless**, diverifikasi terhadap registrasi aktual.

Hasil eksekusi, tidak dijumlahkan sebagai tes unik:

- Collection awal: **22.390 tes**, exit 0. Run awal dengan stub dotenv dihentikan
  karena menghalangi fixture dotenv sintetis; bukan hasil kegagalan aplikasi.
  Harness kemudian dikoreksi untuk identitas pengguna sintetis, scope template
  dotenv di dalam QA, dan parsing IP literal tanpa DNS jaringan.
- Run luas pada snapshot sebelum koreksi terakhir: **22.110 passed, 71 failed,
  227 skipped, 28 warnings**, 1.439,41 detik. Sebanyak **35 failure** berasal dari
  inventaris README yang tertinggal. Tiga tes packaging bertanda integration
  membuat venv dan menjalankan pip build isolation; akses jaringan child pip
  tidak direkam, sehingga keberhasilannya **tidak diklaim sebagai bukti offline**.
  Tidak ada manifest/version dependency proyek yang diubah.
- Regresi gabungan sesudah koreksi: **1.501 passed, 31 skipped, 2 warnings**,
  **57 modul**, 146,45 detik. Mencakup seluruh modul gagal pada run luas,
  seluruh modul tes yang diubah, kontrol konfigurasi/routing/pasar, store serta
  order/mandate/kill-switch/read-only. Packaging integrasi tidak dipilih kembali.
  Satu perapian import tes WebSocket setelahnya diperiksa terpisah; Ruff seluruh
  Python yang berubah lulus. Dua warning utama adalah deprecation anyio/pytest
  dan Starlette/httpx existing.
- **31 skip**: 25 symlink WinError 1314, 1 symlink existing dengan alasan privilege,
  1 mode izin POSIX (bukan verifikasi ACL Windows), 2 perubahan timezone via
  `tzset`, 1 Unix server Windows, dan 1 collection skip extra stats. Assertion
  confinement tanpa symlink serta timestamp host/TCP tetap berjalan. Tidak ada
  bukti native symlink, ACL Windows, non-UTC POSIX atau statistik extra dari skip.

Rujukan parser: [CommandLineToArgvW/LocalFree](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-commandlinetoargvw)
dan [konversi argumen Windows Python](https://docs.python.org/3/library/subprocess.html#converting-an-argument-sequence-to-a-string-on-windows).
Artefak di luar repo:
`%TEMP%\idx-backend-offline-ffe4da21e0`.
`combined/test-modules.json` menyimpan seleksi 57 modul; runner `run_tests.py`
memakai `--allow-hosts=127.0.0.1,::1 -v --tb=short` dan JUnit. Log/XML/summary
run luas, red-before-fix, regresi gabungan, receipt EOL dan baseline/index
dipertahankan. Baca script dan buat QA baru sebelum mengulang agar log historis
tidak tertimpa. Perintah lint: interpreter proyek `-m ruff check` terhadap daftar
Python pada `changed-public-files.json`; pemeriksaan akhir memakai
`verify_session.py` dan `git diff --check`.

Suite penuh tidak diulang setelah koreksi terakhir. Tidak ada probe provider,
frontend test/build baru, deployment, staging atau commit. Metadata Mendeley dan
hak hulu tetap menunggu input eksternal; DATA-01/02/03, IDX-02, RESEARCH-01 penuh
tetap terbuka, backtest IDX nonaktif dan paper/live tetap jalur terpisah.

Pemeriksaan akhir: **375 tautan/anchor lokal**, UTF-8, Ruff dan
`git diff --check` lulus. **3.145 dari 3.207 file baseline publik** tetap identik;
62 berubah dan empat file baru ditambahkan, total 66 file sesi termasuk delapan
normalisasi EOL fixture. Inventory tidak memiliki perubahan tak terduga. Index
identik dengan salinan baseline, SHA-256
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Follow-up import WebSocket: **2 passed, 1 skipped**, tanpa perubahan runtime.

## Ringkasan riset sumber sebelumnya

**Follow-up registry/kode publik, 2026-11-04:** OAI/DataCite v5 berhasil dibaca;
waktu publikasi dan satu aktivitas pembuatan metadata tidak membuktikan waktu
retrieval atau koreksi Yahoo. Pencarian repo/institusi belum memberi manifest
target. Metadata produksi tetap belum layak diimplementasikan; Local Data Bridge
belum diterima riset. Tidak ada tes/probe runtime baru atau task luas ditutup.
[Receipt registry dan blocker yang tersisa](IDX_PROVIDER_RESEARCH.md#mendeley-v5-public-registry-and-code-discovery--2026-11-04).

**Follow-up rilis/hak, 2026-11-04:** perbandingan publik v4→v5 memberi bukti
perubahan deskripsi paket, belum pengikatan recipe ke urutan CSV rilis. Associated
data/koreksi belum memberi manifest baru. CC BY-NC terbaca dan terbatas pada hak
pemberi lisensi; hak hulu untuk pemrosesan lokal belum terverifikasi. Bantuan Yahoo
baru hanya discovery karena full read 429; terms tetap 999. Currency seluruh OHLC
masih inferensi, vintage/revisi unknown dalam review. Tidak ada metadata produksi,
probe atau tes runtime baru; Local Data Bridge tetap belum diterima riset.
[Kelas bukti, keputusan dan input minimum](IDX_PROVIDER_RESEARCH.md#mendeley-v5-release-comparison-and-rights-follow-up--2026-11-04).
Hasil runtime pada ringkasan sebelumnya berikut adalah historis.

**Follow-up metadata, 2026-11-04:** artikel primer mendeklarasikan saham dan
close IDR; notebook v5 membuktikan recipe `auto_adjust=True` dan tanggal lokal
secara statis, tanpa dieksekusi. Bukti bukan lagi hanya README. Proyeksi currency
seluruh OHLC masih inferensi; urutan rilis CSV berbeda dari recipe, source vintage
serta review hak hulu belum memadai. Probe baru seluruh 15 seri lulus loader/helper,
CLI 8+7 tetap ditolak currency_declaration, exit 2/unavailable. Kontrak produksi
belum diimplementasikan dan task luas tidak dicentang.
[Handoff metadata dan blocker yang dipersempit](IDX_PROVIDER_RESEARCH.md#mendeley-v5-metadata-evidence-follow-up--2026-11-04).

**Input local sebelumnya, 2026-11-04:** pencarian ekspor publik kini mempunyai
CSV asli yang diunduh dan diaudit, tetapi kandidat Aethereal gagal invariant
OHLC pada seri BBCA/BBRI dan metadata wajib belum lengkap. Follow-up Mendeley v5 kini memperoleh CSV asli 920.606 bytes: 10.830 baris,
15 ticker × 722, tanpa pelanggaran OHLC/duplikasi, 627 volume nol. Loader dan
helper menerima seluruh seri; CLI 8+7 menolak pada currency_declaration,
exit 2/unavailable, backtest_enabled false. README menyatakan WIB, tetapi IDR,
unit volume dan basis adjustment belum memadai untuk kontrak. Lihat
[audit Mendeley, seam injeksi, isolasi dan blocker](IDX_PROVIDER_RESEARCH.md#mendeley-v5-original-file-audit--2026-11-04), serta
[receipt, audit nyata dan keputusan penerimaan](IDX_PROVIDER_RESEARCH.md#public-local-export-search--2026-11-04).
Tidak ada implementasi metadata dari asumsi atau perubahan kode runtime;
Local Data Bridge tetap belum diterima riset dan task luas tetap terbuka.

## DATA-03 — Peringatan harga saat volume nol di riset

Slice **2026-11-14, Asia/Jakarta**, lanjutan [audit bar harian vendor](#data-03--audit-bar-harian-vendor).

**Backend.** [idx_research_tool.py](src/tools/idx_research_tool.py) memanggil
`audit_daily_bars(code, frame)` pada seluruh observasi yang sudah lolos
validasi, sebelum dipotong ke `lookback`. Bar pertama jendela dinilai terhadap
close bertransaksi terakhir sebelum jendela. Item sehat mendapat field baru:

```json
"bar_audit": {"policy": "idx_daily_bar_audit_v1", "calendar_verified": false, "zero_volume_price_change_dates": ["2026-09-11"]}
```

Hanya tanggal di dalam jendela analisis yang dikembalikan. Bar, grafik dan
indikator tidak diubah, jadi harga pengganti vendor tetap memengaruhi
indikator. Bila ada temuan, log mencatat jumlah bar tanpa nilai harga. Item
yang ditolak atau tidak tersedia tidak punya `bar_audit`. Field
`volume_coverage` tidak diubah, sehingga tes yang membandingkan dict persis
tetap berlaku. API, MCP dan CLI memakai tool yang sama. Deskripsi tool dan
[skill idx-research](src/skills/idx-research/SKILL.md) menyebut field ini,
termasuk bahwa kalender tidak diperiksa.

**UI.** Panel "Cakupan volume" di `/research/idx` menampilkan satu baris:
peringatan tebal dengan jumlah dan tanggal, kalimat bersih bila daftar kosong,
atau "tidak tersedia" bila field absen atau cacat. Gate presentasi
`getIDXBarAudit` menolak seluruh field bila ada satu tanggal yang tidak valid,
tanpa menyaring daftar. Di bawahnya ada keterangan bahwa baris hari libur dan
suspensi tidak diperiksa tanpa kalender terverifikasi. Teks ditambahkan di 11
locale (en, id, tr, ar, de, es, fa, ja, ko, pt-BR, zh-CN).

**Verifikasi.**

- [Tes backend](tests/test_idx_research_bar_audit.py): 10 kasus dengan data
  sintetis. Sebelum tool disambungkan, 7 dari 8 kasus pertama gagal; yang
  lulus adalah kasus simbol ditolak yang memang tidak punya field.
- Seluruh `agent/tests/test_idx*.py` plus `test_market_detection.py` dan
  `test_registry.py`: **1.082 passed** (`--allow-hosts=127.0.0.1,::1`).
- `test_mcp_new_tools.py` dan `test_research_artifact_store.py`: 68 passed.
- Ruff lint dan format lulus pada file Python yang diubah.
- Frontend: tes gate dan render baru ditulis setelah implementasi, jadi tidak
  ada run merah yang tercatat. `npm run test:run` **1.363 passed** (103 file),
  termasuk paritas locale/interpolasi. `npm run build` lulus.
- Suite backend penuh dan probe provider nyata tidak dijalankan. DATA-03 penuh
  tetap terbuka.

## DATA-03 — Audit bar harian vendor

Slice **2026-11-14, Asia/Jakarta**. Pemicunya temuan EODHD/Yahoo yang dicatat
di [riset provider](IDX_PROVIDER_RESEARCH.md#eodhd-split-handling-history-depth-and-holiday-rows--2026-11-14):
baris bervolume nol pada hari libur BEI, sebagian berharga sentinel
999.999,9999, dan hari suspensi MLPT yang
[diisi close sebelumnya](IDX_PROVIDER_RESEARCH.md#mlpt-zero-volume-row-on-27-march-2026-a-suspension--2026-11-14).
Semua bar itu lolos invariant OHLC yang ada, karena bar datar tetap valid.

**Implementasi.** [idx_bar_quality.py](src/markets/idx_bar_quality.py)
menambah `audit_daily_bars(symbol, frame, calendar=None, suspensions=())` dan
record `IDXSuspension` (simbol IDX, sumber, hari pertama dan terakhir,
inklusif). Fungsi ini hanya melaporkan. Ia tidak membuang, memperbaiki atau
mengisi bar, dan tidak mengubah frame input. Temuan berupa daftar tanggal ISO:

| Field | Arti |
|---|---|
| `off_calendar_dates` | bar pada tanggal yang ditandai tutup oleh kalender yang diberikan |
| `uncovered_dates` | bar di luar cakupan kalender, status tidak diketahui (bukan error) |
| `missing_session_dates` | sesi di antara bar pertama dan terakhir tanpa bar; tidak ada bar yang dibuat |
| `zero_volume_flat_bars` | bar datar bervolume nol di luar daftar off-calendar; `status` `suspended` bila record suspensi yang diberikan mencakup hari itu, selain itu `untraded_or_suspended` |
| `zero_volume_price_change_dates` | volume nol, tetapi ada harga OHLC yang berbeda dari close terakhir bervolume positif (tanpa transaksi tidak ada harga baru) |
| `traded_during_suspension_dates` | volume positif di dalam suspensi yang diberikan |

Batasnya:

- Kalender wajib berupa `IDXSessionCalendar` yang disuplai pemanggil. Tidak
  ada kalender, hari libur atau suspensi default. Tanpa kalender, tiga temuan
  kalender bernilai `None` (tidak diperiksa), bukan daftar kosong.
- Record suspensi untuk simbol lain diabaikan; sumbernya ikut di
  `suspension_sources`.
- Volume NaN tetap tidak diketahui, bukan nol. Bar bervolume nol sebelum bar
  bertransaksi pertama tidak dinilai untuk perubahan harga.
- Harga dibandingkan persis, tanpa toleransi. Seri mentah juga bisa berubah
  harga tanpa transaksi pada tanggal aksi korporasi, jadi temuan ini bukan
  vonis.
- Sentinel berurutan sama-sama tertangkap karena pembandingnya close terakhir
  bervolume positif, bukan bar sebelumnya.

**Belum tersambung ke permukaan mana pun.** Tool `idx_research`, API, MCP, CLI
dan UI tidak memanggilnya. Tes `volume_coverage` yang ada membandingkan dict
secara persis, dan belum ada kalender bersumber untuk diberikan. Menyambungkan
temuan tanpa kalender (`zero_volume_price_change_dates`) ke tool riset dan UI
adalah slice terpisah.

**Verifikasi.** [Tes](tests/test_idx_bar_quality.py) memakai kalender,
suspensi dan harga sintetis tahun 2030, bukan data IDX. Run awal gagal saat
koleksi karena modul belum ada. Satu tes awal kemudian diperbaiki: baris
sentinel dilaporkan sekali, sebagai perubahan harga, bukan juga sebagai sesi
ambigu. Hasil akhir:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_bar_quality.py agent/tests/test_idx_foundation.py agent/tests/test_idx_reference.py -q --disable-socket   # 135 passed (33 baru)
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py -q --allow-hosts=127.0.0.1,::1   # 160 passed
.venv/idx312/Scripts/python.exe -m ruff check agent/src/markets/idx_bar_quality.py agent/tests/test_idx_bar_quality.py   # lulus
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/markets/idx_bar_quality.py agent/tests/test_idx_bar_quality.py   # lulus
```

Tes riset dengan `--disable-socket` menghasilkan 13 kegagalan HTTP, karena
asyncio Windows butuh socket loopback. Dengan `--allow-hosts` semuanya lulus.
Black tanpa konfigurasi memakai lebar 88 dan menolak file IDX yang sudah ada
(`idx_rules.py`, `idx_research_tool.py`) maupun file baru. Proyek memakai
`line-length = 120` milik Ruff, jadi file baru mengikuti `ruff format`. Suite
penuh, frontend dan probe provider tidak dijalankan. DATA-03 penuh tetap
terbuka: delisting, dividen, data basi berbasis sesi dan kalender bersumber
belum ada.

## DATA-03 — List tanpa mapping Local Data Bridge

Audit subset **2026-11-04, Asia/Jakarta**. Grounded: status/backlog,
contributor/security, fondasi/reference/provider, `_load_config`, availability,
indeks/fetch/readers, registry, runner, helper akuisisi, tool/CLI dan tes existing
dicocokkan. RTK.md tetap absent. Sebelum fix, pemilik indeks
`backtest/loaders/local_loader.py:348–373` melewati entri tanpa identitas lalu
mempublikasikan indeks kosong. Availability `:340–346` hanya memeriksa list
nonempty; fetch `:400–404` melewati simbol tanpa mapping. Registry
`registry.py:654–655` karena itu memilih loader, helper
`src/market_data.py:385–399` menerima omission sebagai `no_data`. Runner
`backtest/runner.py:1940–1946` sudah menolak hasil local tidak lengkap.

Blast radius: validasi agregat pada pemilik indeks existing, lintas pasar;
tidak menambah classifier, validator surface, registry atau state persisten.
Invariant: guard root/container, skip item/simbol invalid dengan warning tanpa
nilai mentah, string numerik/strip/case/last-wins, peer sehat, schema
tanggal/OHLC/volume, nol/null, harga asli, provenance, revision/cache dan larangan
fallback jaringan explicit-local. Verify: tes red/green, 48 modul offline,
Ruff, JSON/CLI sintetis, tautan/diff dan hash baseline/index.

### Audit sebelum fix dan keputusan kontrak

`audit-before.json` merekam sepuluh bentuk melalui availability, resolver asli,
direct fetch pertama/ulang dan helper resolved/direct. Seluruhnya memakai
YAML/CSV sintetis, tanpa konfigurasi pengguna:

- Key sources absent/list kosong: availability false, resolver
  NoAvailableSourceError; direct `{}`, helper resolved `source_unavailable`,
  helper direct `no_data`. File absent juga dipertahankan oleh regresi baru.
- List seluruh item bukan mapping, seluruh symbol non-string, atau seluruh
  symbol absent/blank: availability true, resolver memilih local, kedua direct
  fetch `{}`, kedua helper `no_data`. Warning item/simbol salah tipe terlihat;
  absent/blank tetap dilewati tanpa warning per entri seperti existing.
- List campuran invalid dan peer IDX/AS: peer tetap berdata. Indeks valid tetapi
  simbol diminta tidak dikonfigurasi: omission/`no_data` dengan warning simbol.
- Sumber berschema lengkap tanpa bar: `no_data`; reader/schema gagal pada simbol
  IDX yang terpetakan: exception direct dan `fetch_failed` melalui helper.

Hipotesis diurutkan: penolakan agregat indeks kosong belum ada; helper menelan
exception; cache menyamarkan kegagalan. Direct fetch sebelum cache sudah `{}`,
sedangkan exception reader menjadi `fetch_failed`: bukti mendukung yang pertama.

**Satu gap dipilih: list nonempty tanpa satu pun simbol yang dapat diindeks.**
`_ensure_config` kini membangun indeks lokal sementara dengan aturan existing,
lalu menolak indeks kosong dengan ValueError:
`local loader: nonempty sources must define at least one nonblank string symbol`.
Error tidak menyalin nilai/path konfigurasi. Config/indeks instance baru
dipublikasikan sesudah guard, agar gagal pertama/ulang tetap menolak dan instance
yang sama dapat pulih setelah YAML dikoreksi. Tidak menebak simbol atau mengubah
angka menjadi ticker.

Keputusan kompatibilitas disengaja: list seluruh absent/blank ikut ditolak
secara agregat. Skip per entri absent/blank dalam list campuran tidak berubah.
List kosong/absent tetap valid kosong existing. Simbol yang tidak dikonfigurasi
di dalam indeks valid tetap omission/`no_data`; tidak mengubah seluruh omission
menjadi kegagalan. Indexability hanya mensyaratkan simbol string nonblank,
bukan membuktikan reader, venue, metadata atau bar tersedia.

Availability tetap pemeriksaan deklarasi nonempty, sehingga kedua jalur helper
resolved/direct kini mencatat **`fetch_failed`**, bukan `source_unavailable`,
untuk gap ini. Docstring menjelaskan batas itu. Exception spesifik keluar dari
loader dan tercatat oleh error logger helper existing. Tidak menambah reason
publik baru. List tanpa identitas tidak dapat mengisolasi simbol/peer; penolakan
ini berlaku untuk seluruh konfigurasi tersebut, bukan klaim isolasi global.

### Regresi, cache dan verifikasi

QA: `%TEMP%\idx-local-unmapped-qxi0qaq4`.
Sebelum edit: status Git dan inventaris UTF-8 NUL-delimited, SHA-256 **3.197
file publik**, salinan/hash index dan loader. Nama dotenv/token/secret
dikecualikan dari pembacaan. Hash index diverifikasi ulang dan cocok dengan
handoff. Runner/checker historis dibaca sebelum disalin dan disesuaikan; venv
existing bukan instalasi bersih. Environment allowlist, home/appdata/localappdata/
runtime/temp/cwd terisolasi, assertions sebelum import proyek, dotenv
disabled/stub dan audit hook menolak dotenv di luar QA. Direktori legacy state
di source diperiksa absent. Pytest memakai home tambahan di TEMP QA. Socket
dinonaktifkan; regresi HTTP/asyncio Windows hanya mengizinkan loopback. Probe
menolak connect, tanpa server eksternal atau provider.

Regresi awal **18 failed, 5 passed, 1 warning**: `Failed: DID NOT RAISE
ValueError`, dan helper menghasilkan `no_data` ketika yang diharapkan
`fetch_failed`. Setelah fix **23 passed, 1 warning**. Modul baru menguji empat
kelompok list tanpa mapping × IDX/AS, retry/koreksi instance, helper
resolved/direct tanpa fallback, absent/empty, kontrol indeks valid dengan peer,
unconfigured/empty/reader/schema serta cache IDX/AS. Satu tes coercion existing
ditambah peer valid: tetap memastikan angka tidak menjadi ticker, sementara
penolakan agregat diuji oleh modul baru. Assertion omission tidak dilemahkan.

Tes cache mengisi cache positif IDX/AS, mengganti YAML menjadi seluruh invalid,
memastikan ValueError dan daftar/byte cache tetap, lalu memperbaiki YAML pada
instance gagal dan melarang CSV I/O. Frame dari cache tetap identik. Instance
yang sudah sukses tetap snapshot existing, bukan hot reload. Validasi mendahului
cache; identity deklarasi, revision file/WAL dan token cache tidak berubah.
Tidak ada cache pengguna yang dibaca atau dihapus.

Perintah aktual dari root; runner meneruskan `-c <repo>/pyproject.toml`:

```powershell
$qa = '%TEMP%\idx-local-unmapped-qxi0qaq4'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --audit
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_local_loader_unmapped_sources.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_unmapped_sources.py agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_local_loader_unmapped_sources.py agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

Audit sebelum fix disimpan; menjalankan ulang audit menilai kode saat ini.
Gabungan **48 modul: 1.526 passed, 3 skipped, 7 warnings** (70,09 detik).
Skip: tiga pembacaan Parquet membutuhkan pandas engine opsional. Warning:
anyio/pytest, Starlette/httpx deprecation dan arithmetic ekstrem fixture.
Ruff lint tiga file serta format kedua tes lulus; loader tidak diformat ulang
luas. Black tidak dijalankan (sebelumnya tidak tersedia); tidak memasang dependency.

Probe JSON existing dan entry point CLI riset lulus **20 kombinasi**: sepuluh
fixture (absent key, list kosong, non-mapping, non-string, absent/blank,
unconfigured, valid empty, reader gagal, schema gagal, mixed peers) × resolver
asli/direct loader. Perbedaan absent/empty tetap existing; all-unmapped dan
reader/schema gagal `fetch_failed`; unconfigured/valid empty `no_data`.
Peer IDX/AS close **105**, volume **0/null**, provenance local tanpa currency
buatan. Seluruh CLI exit **2**, status **unavailable**, backtest_enabled
**false**. Peer berdata ditolak pada `currency_declaration`.
CLI tidak memiliki opsi source: seam `idx_research_tool.fetch_market_data`
diarahkan ke helper local, resolver hanya mengizinkan local lalu memakai registry
asli. Validasi/serialisasi/exit CLI existing tetap berjalan. Ini probe in-process,
bukan subprocess CLI bersih, provider nyata, HTTP server atau aplikasi packaged.
Log probe tidak mengandung marker mentah sintetis.

Local belum diterima riset. Metadata IDR/timezone/interval/unit volume/adjustment/
provenance, timestamp/UTC/tanggal sesi/epoch/format/bounds/bucket dan decoder
Parquet nyata tetap perlu ekspor berizin sesuai [reference](IDX_REFERENCE.md) dan
[provider](IDX_PROVIDER_RESEARCH.md). YAML syntax dan kebijakan duplikasi baru
tidak disentuh. DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka;
backtest IDX nonaktif, paper/live terpisah, Index Alpha ditunda. Backend/safety
penuh, frontend/build, provider nyata, MCP eksternal, Electron dan deployment
tidak diverifikasi. Assembler/auth/lifespan/scheduler/runtime/trading tetap.
Tanpa dependency, staging, commit, publish atau deployment.

File sesi: loader, tes entri existing, tes unmapped baru, README.md,
README_id.md, PROJECT_STATUS.md, TODO.md dan dokumen ini. Artefak QA menyimpan
baseline/status/inventaris, index/loader sebelum edit, audit, runner/daftar modul,
red/green/regression/probe/Ruff logs, JSON/CLI, diff sesi dan verification.json.
Pemeriksaan akhir: **248 tautan lokal/anchor**, UTF-8, konsistensi status/backlog
dan `git diff --check` lulus. **3.190 dari 3.197 file baseline identik**, tujuh
file baseline diubah dan satu tes baru; tidak ada baseline hilang. Pekerjaan lama
di file lain tetap identik. Index sebelum/sesudah sama:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Warning LF/CRLF dari file frontend existing tercatat, tanpa perubahan byte file itu.

## DATA-03 — Container sources Local Data Bridge

Subset **2026-11-04, Asia/Jakarta**, setelah follow-up dokumen top-level.
Grounded: status/backlog dibandingkan dengan `_load_config`
(`backtest/loaders/local_loader.py:191–203` sebelum fix), availability `:338–344`,
indeks `:346–378`, fetch/cache `:402–436`, registry availability
(`registry.py:624,654`), runner local-prefixed (`runner.py:1940–1942`), helper
(`src/market_data.py:347–355,385–399`), tool/CLI dan tes existing. Panduan kontribusi,
keamanan, fondasi serta batas reference/provider tetap berlaku; RTK.md absent.
Blast radius: validasi container pada pemilik pembacaan `_load_config` saja.
Invariant: absent/empty, list valid lintas pasar, guard item/simbol, strip/case/
last-wins/string numerik, schema tanggal/OHLC/volume, harga asli/nol/null,
provenance/revision/cache dan larangan fallback jaringan explicit-local.
Verify: modul 51 kasus baru, 47 modul regresi offline, Ruff, JSON/CLI sintetis,
dokumen/diff dan baseline/index SHA-256.

### Reproduksi dan keputusan

`audit-before.json` di QA merekam 12 bentuk `sources` melalui availability,
direct fetch, resolver asli serta helper resolved/direct. Null, boolean, integer
atau float: availability false, direct fetch TypeError. String kosong/nonempty
atau mapping kosong/nonempty: availability false, direct fetch `{}`; helper direct
menyebut `no_data`. Guard item existing melewati karakter/key mapping sebagai
item tanpa identitas. List kosong: unavailable/direct `{}`; list nonempty dengan
item tanpa mapping/simbol: tersedia namun omission/no_data dengan warning.

Gap dipilih: **key `sources` yang hadir tetapi nilainya bukan list**. Satu guard
di `_load_config` sesudah guard root mapping menolak dengan ValueError
`local loader: sources must be a list`, tanpa nilai, path atau repr mentah.
Tidak menambah validator di registry/helper/UI dan tidak mengubah kebijakan
reader/simbol. Null eksplisit kini ditolak; key absent, list kosong, dokumen
kosong/null dan file absent tetap existing. Ini keputusan kompatibilitas yang
disengaja: null container tidak disamakan dengan list kosong. Semua pasar memakai
guard struktur bersama; list valid pasar lain tetap didukung.

Regresi sebelum fix **44 failed, 7 passed**; contoh `TypeError: 'NoneType' object
is not iterable`, `Failed: DID NOT RAISE ValueError` untuk mapping/string, dan
NoAvailableSourceError pada resolver yang seharusnya mengungkap error spesifik.
**51 kasus baru**: 13 nilai non-list × availability/fetch/resolver (39), tiga
kontrol absent/empty list, dua pemanggilan berulang/koreksi instance, dua cache
IDX/AS, empat helper resolved/direct serta satu kontrol list campuran sehat/
kosong/item invalid. Null, dua boolean, integer/float/NaN, string kosong/marker,
mapping kosong/marker dan tanggal YAML melewati safe_dump/load nyata.
Sesudah fix **51 passed, 1 warning** (1,89 detik).

Guard berjalan sebelum assignment `_config`; tes memanggil instance invalid dua
kali lalu mengoreksinya menjadi list sehat IDX/AS. Tidak ada config/indeks parsial.
Instance yang sudah sukses tetap memakai snapshot existing, bukan hot reload.
Cache tidak membutuhkan token baru: pada instance baru guard mendahului lookup.
Tes mengisi positive cache IDX/AS, mengganti container menjadi mapping, memeriksa
penolakan serta daftar/byte cache utuh, mengembalikan YAML lalu melarang CSV I/O.
Frame tetap identik dari cache; source revision/identity tidak diubah dan cache
pengguna tidak dihapus.

### Perintah dan hasil aktual

QA: `%TEMP%\idx-local-sources-le45bbp0`.
Sebelum edit: status dan inventaris Git UTF-8 NUL-delimited, hash **3.196 file
publik**, salinan index dan loader. Nama dotenv/token/secret dikecualikan dari
pembacaan. Hash index diverifikasi ulang terhadap sesi sebelumnya. Runner/probe
existing diperiksa; venv bukan instalasi bersih. Environment allowlist,
home/appdata/localappdata/runtime/temp/cwd terisolasi, assertions sebelum import,
state legacy source absent, dotenv disabled/stub dan audit hook yang menolak
dotenv di luar QA. Pytest home tambahan berada di TEMP QA. Tes offline dengan
pytest-socket, hanya loopback untuk HTTP/asyncio Windows; probe menolak connect.

```powershell
$qa = '%TEMP%\idx-local-sources-le45bbp0'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --audit
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_local_loader_sources_shape.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_sources_shape.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_local_loader_sources_shape.py
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

Audit di atas dibuat sebelum fix; menjalankan ulang menilai kode saat ini.
Regresi **47 modul: 1.503 passed, 3 skipped, 7 warnings** (51,97 detik), termasuk
seluruh kontrol local sebelumnya, root dokumen, IDX/routing dan pasar lain.
Tiga skip membutuhkan pandas Parquet engine opsional; decoder nyata belum diuji.
Warning anyio/Starlette deprecation dan arithmetic ekstrem fixture tetap terlihat.
Ruff lint dan format tes lulus; loader tidak diformat ulang luas. Black tidak
tersedia pada run sebelumnya dan tidak dijalankan ulang; dependency tidak dipasang.

Probe JSON existing dan CLI entry point menguji null, boolean false, mapping
marker dan string marker × resolver asli/direct-loader (delapan kombinasi).
Resolver `source_unavailable`; direct helper `fetch_failed`; CLI exit **2**,
status **unavailable**, `backtest_enabled: false`. Schema diagnostik publik tetap
alasan umum existing. Exception spesifik tersedia pada loader dan log fetch;
jalur resolver tetap memakai logger DEBUG existing. Tidak ada marker mentah.
Probe pertama gagal assertion log karena handler QA hanya menangkap logger
local-loader, sementara error fetch dicatat helper `src.market_data`. Handler
QA ditambah pada logger helper lalu probe lulus; kode produksi tidak diubah.
`probe-initial.log` menyimpan kegagalan harness tersebut.

Probe kontrol list yang dapat dipetakan tetap menguji empat simbol non-string,
lima reader cacat, dua peer sehat dan file kosong: reader `fetch_failed`, valid
empty `no_data`, peer close **105**, volume null/0 serta provenance local.
CLI menolak peer berdata pada `currency_declaration`, tanpa metadata buatan.
Guard global tidak dapat menyelamatkan peer dari container non-list: tidak ada
struktur daftar entri yang dapat dipercaya. Explicit-local tetap tanpa jaringan.
CLI tidak punya opsi source: seam `idx_research_tool.fetch_market_data` diinjeksi
ke helper local dengan resolver dibatasi local lalu registry asli. Validasi,
serialisasi dan exit tetap existing; ini probe in-process sintetis, bukan CLI
subprocess bersih, HTTP server, provider nyata atau Electron packaged app.

Diagnostik simbol tanpa mapping/all-invalid tetap omission/no_data dengan warning;
YAML syntax dan kebijakan duplikasi baru tidak disentuh. Metadata IDR/timezone/
interval/unit volume/adjustment/provenance, timestamp/UTC/epoch/format/bounds/
bucket dan decoder Parquet nyata tetap memerlukan ekspor berizin; lihat
[handoff referensi](IDX_REFERENCE.md) dan [provider](IDX_PROVIDER_RESEARCH.md).
Local belum diterima riset; DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap
terbuka. Backtest IDX nonaktif; paper/live terpisah, Index Alpha ditunda.
Backend/safety penuh, provider nyata, frontend/build, MCP eksternal, Electron dan
deployment tidak dijalankan. Assembler/auth/lifespan/scheduler/runtime/trading dan
dependency tetap. Tidak ada staging/commit/publish/deployment.

Pemeriksaan akhir: **242 tautan lokal/anchor**, UTF-8, konsistensi status/backlog
serta `git diff --check` lulus. **3.190 dari 3.196 file baseline identik**;
enam file diperluas dan satu tes baru, tanpa baseline hilang. File sesi: loader,
`tests/test_local_loader_sources_shape.py`, README.md, README_id.md,
PROJECT_STATUS.md, TODO.md dan dokumen ini. Modul tes/top-level dari sesi sebelumnya
serta seluruh file lain tetap identik. Index awal/akhir tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Baseline/status/inventaris UTF-8 NUL, salinan index/loader, audit, runner/daftar
modul, red/green/regression/probe/Ruff logs, JSON, session diff dan
`verification.json` disimpan di QA. Tidak ada staging atau commit.

## DATA-03 — Dokumen top-level Local Data Bridge

Audit **2026-11-04, Asia/Jakarta**, fixture YAML/CSV sintetis, tanpa config pengguna.
Grounded: status/backlog, contributor/security, foundation/reference/provider,
loader/readers, registry, helper akuisisi, runner, tool/CLI, cache serta tes dibaca.
Sebelum fix `backtest/loaders/local_loader.py:191–196` memakai
`yaml.safe_load(...) or {}`. Availability `:331–337` memanggil `.get`, indeks
`:339–371` melakukan hal sama sebelum fetch/cache `:395–417`. Registry
`:624`/`:654` tidak menangkap exception availability; runner local-prefixed
`:1940–1942` memakai registry asli. Helper `src/market_data.py:347–355` mencatat
resolver gagal sebagai `source_unavailable`, `:385–392` mencatat exception fetch
sebagai `fetch_failed`, omission `:395–399` menjadi `no_data`. Tool riset dan CLI
mengonsumsi helper existing; tidak membuat validator pada surface tersebut.

Blast radius: hanya bentuk dokumen pada `_load_config`, pemilik pembacaan bersama.
Invariant: mapping valid lintas pasar, null/empty/absent, indeks/duplikat/strip/case,
reader/schema tanggal/OHLC/volume, harga asli/nol/null, provenance/revision/cache,
serta explicit-local tanpa jaringan. Verify: 49 kasus baru, 46 modul regresi,
Ruff, JSON/CLI sintetis, tautan/diff dan hash baseline/index.

### Matriks audit sebelum fix

`audit-before.json` merekam 20 fixture melalui load, availability, direct fetch,
resolver dan helper. Hasil aktual memperbarui dugaan handoff lama:

- File absent: load None; dokumen kosong/null, mapping kosong dan mapping tanpa
  sources: unavailable; direct fetch `{}`. `sources: []` juga sama.
- Root false/0/string kosong/list kosong dilebur menjadi `{}`: cacat dapat tampak
  sebagai konfigurasi kosong. Root string, integer/float atau list nonempty lolos
  dari load lalu memicu AttributeError pada availability/direct/resolver.
- `sources: null`/false: availability false, direct fetch TypeError. Mapping
  kosong/nonempty dan scalar string: availability false, direct fetch omission
  `{}` dengan warning item bukan mapping dari guard terbaru. Jadi mapping
  nonempty tidak lagi selalu AttributeError seperti audit historis.
- List sources nonempty tersedia; entry IDX dengan path blank menjadi
  `fetch_failed`. Probe list valid menguji peer sehat dan file valid kosong.
- Helper dengan resolver asli merangkum semua bentuk unavailable di atas sebagai
  `source_unavailable`; alasan publik itu belum membedakan config cacat dari
  file absent. Direct loader melewati availability dan memiliki hasil berbeda.

### Gap dipilih dan kompatibilitas

Satu subset diperbaiki: **dokumen top-level scalar/list**. Setelah safe_load,
None tetap `{}` untuk YAML kosong/null; file absent tetap None. Semua nilai lain
harus dict, atau ValueError `local loader: configuration document must be a mapping`.
Tidak mengutip nilai, path, tipe repr atau payload private. Falsy non-null kini
menolak, perubahan kompatibilitas yang disengaja agar cacat tidak menjadi empty.
Mapping valid pasar mana pun tidak berubah. Tidak memvalidasi nested `sources`,
field baru, YAML syntax, metadata, duplikat atau ticker melalui guard tambahan.

Regresi awal **40 failed, 9 passed**; contoh `Failed: DID NOT RAISE ValueError`
untuk false dan `AttributeError: 'bool' object has no attribute 'get'` untuk true.
**49 tes baru**: 12 scalar/list/tanggal YAML × availability/fetch/resolver,
tujuh kontrol dokumen kosong/mapping, absent, koreksi pada instance sama,
cache IDX/AS dan dua jalur helper. Hasil akhir **49 passed, 1 warning**.
Run antara setelah fix: **2 failed, 47 passed**, `(None, <Day>)` pada equality
frekuensi index fixture satu bar yang diresample lalu dibaca cache. Fixture
menjadi dua bar harian nol/null seperti kontrol existing; assertion frame tetap
utuh. Tidak mengubah kode/cache untuk kasus metadata frekuensi existing itu.

Penolakan terjadi sebelum assignment `_config`; instance gagal dapat membaca
config yang dikoreksi. In-memory config pada instance yang sudah sukses tetap
snapshot existing, bukan hot reload. Cache positif tidak dapat melewati guard
pada instance baru: tes mengisi cache, mengganti root menjadi list kosong,
membuktikan ValueError dan byte/daftar file tetap, mengembalikan YAML semula lalu
melarang CSV reader. Frame IDX/AS tetap sama dari cache. Tanpa token baru,
perubahan identity/revision atau penghapusan cache pengguna.

### Verifikasi dan surface probe

QA: `%TEMP%\idx-local-root-w7buco4m`.
Baseline sebelum edit: status/inventaris UTF-8 NUL-delimited, SHA-256 **3.195 file
publik**, salinan index/loader/tes. Nama dotenv/token/secret tidak dibaca.
Runner/probe historis diperiksa sebelum dipakai ulang; venv existing bukan clean
install. Environment allowlist; home, appdata/localappdata, runtime, temp dan cwd
terisolasi. Assertions sebelum import, dotenv disabled/stub, audit hook menolak
pembacaan dotenv di luar QA, direktori state legacy source diperiksa absent.
Pytest memakai sandbox home tambahan di TEMP QA; socket dinonaktifkan, loopback
hanya untuk HTTP/asyncio Windows. Probe menolak socket connect.

Perintah aktual dari root (manifest `-c <repo>/pyproject.toml` lewat runner):

```powershell
$qa = '%TEMP%\idx-local-root-w7buco4m'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --audit
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_local_loader_document.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_document.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_local_loader_document.py
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

`audit-before.json` dibuat sebelum fix; menjalankan ulang audit menilai kode saat
ini. Regresi **46 modul: 1.452 passed, 3 skipped, 7 warnings** (58,03 detik).
Tiga skip membutuhkan pandas Parquet engine opsional; decoder nyata belum teruji.
Warning anyio/Starlette deprecation dan arithmetic ekstrem fixture tetap tampak.
Ruff lint/format tes lulus, loader tidak diformat ulang luas. Black tidak tersedia
(`No module named black`); dependency tidak dipasang/diubah.

JSON existing dan entry point CLI riset diuji dengan tiga root cacat (false,
list kosong, string marker), masing-masing resolver asli dan direct-loader:
resolver `source_unavailable`, direct-loader `fetch_failed`; CLI exit **2**,
status **unavailable**, `backtest_enabled: false`. Error spesifik tersedia pada
exception loader (dan log fetch), tetapi schema diagnostik publik tetap alasan
umum existing. Tidak menjanjikan kode publik baru atau log warning pada jalur
resolver yang logger existing-nya DEBUG. Tidak ada nilai marker pada log.
Dokumen global cacat tidak dapat memetakan peer; seluruh simbol ditolak.

Probe list valid memakai empat simbol non-string sebelum lima reader cacat,
dua peer sehat dan satu file kosong. Lima reader `fetch_failed`, empty berschema
valid `no_data`; peer close **105**, volume null/0 dan provenance local tetap
tersedia. CLI tetap menolak peer berdata pada `currency_declaration`, tanpa
metadata IDR buatan. Resolver dibatasi local lalu registry asli; CLI tidak punya
opsi source, sehingga seam `idx_research_tool.fetch_market_data` diinjeksi menuju
helper local. Validasi/serialisasi/exit CLI tetap existing. Ini probe in-process,
bukan subprocess CLI bersih, HTTP server, provider nyata atau aplikasi packaged.

Container `sources` salah bentuk, simbol tanpa mapping/all-invalid sebagai no_data,
YAML syntax dan kebijakan duplikasi baru tetap memerlukan slice/keputusan terpisah.
Metadata IDR/timezone/interval/unit volume/adjustment/provenance, timestamp/UTC/
epoch/format/bounds/bucket dan decoder Parquet nyata memerlukan ekspor berizin;
lihat [handoff referensi](IDX_REFERENCE.md) dan [provider](IDX_PROVIDER_RESEARCH.md).
Local belum diterima untuk riset; DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh
terbuka. Backtest IDX nonaktif, paper/live terpisah, Index Alpha ditunda.
Backend/safety penuh, frontend/build, MCP eksternal, provider nyata, Electron dan
deployment tidak dijalankan. Assembler/auth/lifespan/scheduler/runtime/trading
serta dependency tidak diubah. Tanpa staging/commit/publish/deployment.

Pemeriksaan akhir: **236 tautan lokal/anchor**, UTF-8, konsistensi status/backlog
serta `git diff --check` lulus. **3.189 dari 3.195 file baseline identik**;
enam diperluas dan satu file tes baru, tanpa file baseline hilang. File sesi:
loader, `tests/test_local_loader_document.py`, README.md, README_id.md,
PROJECT_STATUS.md, TODO.md dan dokumen ini. Semua pekerjaan sebelumnya di file
lain tetap identik. SHA-256 index sebelum/sesudah sama:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Baseline/status/inventaris NUL UTF-8, salinan index, audit, runner/daftar modul,
red/green/regression/probe logs, JSON, session diff dan `verification.json`
disimpan di QA di atas. Tidak ada staging atau commit.

## DATA-03 — Simbol non-string Local Data Bridge

Follow-up **2026-11-04, Asia/Jakarta** menutup satu gap audit struktur di bawah.
Sebelum edit, `backtest/loaders/local_loader.py:354` langsung memanggil
`entry.get("symbol", "").strip()`. Guard item bukan mapping pada `:344–353`
belum melindungi mapping dengan nilai symbol null, boolean, angka, list,
mapping atau tanggal YAML. Kesalahan terjadi sebelum pemilihan entri/cache
(`fetch` pada `:380–410`), sehingga konfigurasi satu simbol tanpa identitas
valid menggagalkan simbol sehat dan dapat meninggalkan indeks parsial pada
instance yang sama. `src/market_data.py:477–480` sudah memisahkan akuisisi IDX
per simbol; membaca seluruh konfigurasi pada setiap instance tetap merambatkan
kegagalan indeks itu menjadi `fetch_failed` pada peer.

Grounded: snapshot status/backlog dicocokkan dengan loader, callers registry,
runner/helper, identity/revision/cache dan tes existing. Blast radius: guard
tipe simbol di `_ensure_config`, pemilik indeks yang sudah menangani entri
tanpa mapping. Invariant: tidak ada coercion simbol, strip/case-sensitive
lookup/duplikat terakhir/string numerik serta absent/blank tetap sama; semua
entri valid lintas pasar, reader/schema tanggal/OHLC/volume, harga asli,
nol/null, provenance dan larangan fallback jaringan local tetap terjaga.
Verify: modul entri, 45 modul regresi, Ruff, JSON/CLI sintetis, pemeriksaan
tautan/diff serta hash file/index. RTK.md tetap tidak ditemukan di root.

Sebelum fix **36 failed, 30 passed** pada modul entri, termasuk 28 kasus
existing. Contoh error `AttributeError: 'NoneType' object has no attribute
'strip'`. Sebanyak **38 kasus baru** meliputi 11 nilai non-string × tiga
posisi entri (sebelum/di antara/setelah peer IDX dan AS), isolasi helper,
positive cache, larangan coercion angka ke ticker, penerimaan string numerik,
serta case-sensitive lookup. Null, dua boolean, integer, float, NaN, list
kosong/berisi marker, mapping kosong/berisi marker dan `datetime.date`
melewati YAML safe dump/load nyata. CSV sintetis memakai harga close 105,
volume nol dan null; tidak ada metadata atau harga produksi yang diasumsikan.

Pemilik indeks kini memeriksa nilai symbol sebelum `.strip()`. Nilai bukan
string dilewati dengan warning `local loader: sources entry N symbol must be
a string; skipping unassigned entry`, N mulai 1, tanpa nilai mentah. Ini
memperluas degradasi entri tanpa identitas existing: seluruh pasar dapat
memuat entri validnya, bukan menentukan pasar dari nilai salah tipe. Tidak
mengubah angka menjadi string, menebak ticker dari list/mapping, atau
menormalisasi case baru. String `"600519"` tetap diterima; angka `600519`
tidak menjadi entri untuk permintaan string tersebut. Simbol absent memakai
default string kosong existing, blank dilewati existing, dan entri string
duplikat tetap memilih yang terakhir setelah strip.

Cache tetap memakai identity deklarasi, kontrak IDX dan file/WAL revision
existing, tanpa token baru atau penghapusan entry. Guard indeks berjalan
sebelum lookup cache: cacat ini sebelumnya menghalangi pembacaan, bukan
menyimpan bar salah. Tes mengisi cache sehat, menyisipkan `symbol: null`,
melarang reader I/O lalu membuktikan warning tetap muncul, frame identik,
daftar file serta seluruh byte cache tetap utuh. Pemanggilan berulang pada
instance yang sama mempertahankan kedua peer, tanpa indeks parsial.

Top-level/`sources` salah bentuk, YAML syntax error dan kebijakan duplikasi
baru tetap di luar subset. Availability masih memeriksa list nonempty;
simbol tanpa mapping tetap omission/no_data existing. Jika seluruh entri
memiliki simbol non-string, warning memperlihatkan kerusakan tetapi diagnostik
per simbol belum membedakannya dari simbol tidak dikonfigurasi. Ini bukan
klaim bahwa seluruh konfigurasi cacat menjadi `fetch_failed`. Reader cacat
untuk simbol IDX valid tetap `fetch_failed`, sumber valid kosong tetap
`no_data`, dan peer sehat tetap memperoleh data/provenance local.

### Verifikasi simbol non-string

Artefak QA: `%TEMP%\idx-local-symbol-o1r19efr`.
Sebelum edit, status Git UTF-8/NUL-delimited, hash **3.195 file publik**,
salinan index, loader dan modul tes disimpan. Nama dotenv/token/secret
dikecualikan. Hash index awal kembali cocok dengan sesi sebelumnya.
Runner/probe historis dibaca sebelum disalin; interpreter proyek existing,
bukan instalasi bersih. Sebelum import proyek: environment allowlist,
home/appdata/localappdata/runtime/temp/cwd terisolasi, assertions direktori
legacy source absent, dotenv disabled/stub dan audit hook menolak dotenv di
luar QA. Pytest memakai sandbox home tambahan di TEMP terisolasi. Probe
menolak socket connect; tes offline memakai pytest-socket dan hanya mengizinkan
loopback untuk HTTP/asyncio Windows pada regresi gabungan.

Perintah aktual dari root; runner meneruskan manifest `-c <repo>/pyproject.toml`:

```powershell
$qa = '%TEMP%\idx-local-symbol-o1r19efr'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_local_loader_source_entries.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

Modul entri **66 passed, 1 warning** (8,08 detik); regresi 45 modul **1.403
passed, 3 skipped, 7 warnings** (53,18 detik). Tiga skip tetap pembacaan Parquet
yang memerlukan engine pandas opsional; decoder nyata belum dibuktikan. Warning
anyio/Starlette deprecation serta arithmetic ekstrem fixture tetap terlihat.
Ruff lint loader/tes dan format tes lulus; loader tidak diformat ulang luas.
Black tidak tersedia (`No module named black`); dependency tidak dipasang/diubah.

Probe JSON akuisisi dan CLI riset memakai YAML/CSV sintetis: empat mapping
simbol non-string (null, integer, list marker, mapping marker) sebelum delapan
entri valid bentuk mapping menghasilkan warning nomor 1–4 tanpa marker mentah.
Resolver hanya mengizinkan local kemudian memakai registry asli. Seam akuisisi
CLI diarahkan ke local karena CLI riset tidak memiliki opsi source; validasi,
serialisasi dan exit entry point CLI tetap existing. Lima deklarasi reader
cacat tetap `fetch_failed`; GGRM berschema valid tanpa bar `no_data`; BBRI
volume hilang null, TLKM nol 0, keduanya close 105 dan provenance local tanpa
currency buatan. CLI exit **2**, status **unavailable**, backtest_enabled
**false**; peer berdata tetap ditolak pada `currency_declaration`. File DuckDB
yang tidak boleh dibuka tidak dibuat. Tidak ada fallback jaringan/provider nyata.

Local belum diterima untuk riset. Metadata IDR/timezone/interval/unit volume/
adjustment/provenance dan semantik timestamp/bucket tetap memerlukan ekspor
asli berizin sesuai [handoff referensi](IDX_REFERENCE.md) dan
[provider](IDX_PROVIDER_RESEARCH.md). DATA-01/02/03, IDX-02 dan RESEARCH-01
penuh tetap terbuka; backtest IDX nonaktif, Index Alpha ditunda. Backend/safety
penuh, frontend/build, MCP eksternal, Electron packaged app dan deployment
tidak dijalankan. Assembler/auth/lifespan/scheduler, trading serta dependency
tidak berubah. Tidak ada staging, commit, publish atau deployment.

Pemeriksaan akhir: **230 tautan lokal/anchor** pada lima dokumen yang diubah,
UTF-8, konsistensi status/backlog dan `git diff --check` lulus. Git hanya
memberi warning konversi LF/CRLF pada file working tree existing. Dari **3.195
file publik baseline**, **3.188 identik**, tujuh diperluas; tidak ada file
tambahan/hilang. File sesi: loader, `tests/test_local_loader_source_entries.py`,
README.md, README_id.md, PROJECT_STATUS.md, TODO.md dan dokumen ini. Perubahan
lama termasuk frontend/packaging tetap identik terhadap baseline sesi.
Hash index sebelum/sesudah tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Status/hash baseline, salinan index/loader/tes, runner/probe, daftar modul,
log red/green/regression/probe/Ruff/Black, diff tes dan `verification.json`
tersimpan di direktori QA di atas. Tidak ada staging/commit.

## DATA-03 — Isolasi entri YAML Local Data Bridge

Audit subset **2026-11-04, Asia/Jakarta**, terhadap source existing; tidak ada
input provider baru. Sebelum edit, `backtest/loaders/local_loader.py:191–196`
memuat `yaml.safe_load(...) or {}`; `:331–337` hanya memeriksa bahwa `sources`
adalah list nonempty untuk availability. `_ensure_config` pada `:339–347`
mengindeks seluruh list dan memanggil `entry.get(...).strip()` tanpa guard.
Satu item bukan mapping menghentikan indeks, termasuk sebelum entri sehat.
Karena `_config` sudah terisi, pemanggilan kedua pada instance yang sama juga
dapat memakai indeks parsial tanpa mencoba menyelesaikannya.

Grounded: loader, normalizer/readers, identity/revision/cache, registry
`get_loader_cls_with_fallback` (`:632–669`), runner `_fetch_all_data`
(`:1933–1957`), helper akuisisi, tool/CLI dan tes local/routing dibaca.
`src/market_data.py:477–480` sudah mengambil IDX per simbol, tetapi setiap
instance tetap membaca seluruh YAML. Exception menjadi `fetch_failed` pada
`:385–392`, omission menjadi `no_data` pada `:395–399`. Ini menjelaskan mengapa
isolasi helper saja tidak menyelamatkan peer sehat. Blast radius: loop indeks
bersama `_ensure_config`, tanpa mengubah routing/reader/perhitungan. Invariant:
entri valid lintas pasar, last-wins setelah strip, case-sensitive lookup,
harga asli, volume nol/null, schema tanggal/OHLC/volume, provenance, revision
dan larangan fallback jaringan local eksplisit. Verify: modul tes baru, enam
modul local, 45 modul regresi, Ruff dan JSON/CLI sintetis terisolasi.

Hasil audit struktur sebelum fix (`audit-before.json` di QA):

- Top-level list/string nonempty: `AttributeError` pada availability dan indeks.
  Nilai falsy termasuk YAML null dilebur menjadi `{}`; availability false.
- `sources: null`: availability false, direct indexing `TypeError`.
  `sources` mapping nonempty: availability false, direct indexing `AttributeError`.
  Tidak mengubah perbedaan resolver versus direct fetch pada subset ini.
- List berisi item null/non-mapping: availability true, indexing gagal.
  Inilah gap yang dipilih. Null, boolean, integer, float, string dan list
  direproduksi dengan fixture YAML/CSV sintetis nyata, sebelum/di antara/setelah
  dua entri valid IDX dan AS. Sebelum fix **23 failed, 5 passed**; contoh error
  `AttributeError: 'NoneType' object has no attribute 'get'`, serta helper
  melaporkan peer/empty sebagai kegagalan akuisisi.
- Mapping dengan simbol absent/blank diabaikan existing. Simbol non-string
  seperti null gagal pada `.strip()` dan masih dapat menggagalkan peer.
  Duplikat dipilih terakhir setelah outer strip; lookup tetap case-sensitive.
  Tidak memperkenalkan normalisasi/penolakan duplikat baru. Lima tes kontrol
  awal mengunci duplikat IDX/AS dan simbol absent/blank yang sudah lulus.

Perbaikan pada pemilik indeks existing: setiap item bukan `dict` dilewati
dengan warning `local loader: sources entry N must be a mapping; skipping
unassigned entry` (N mulai 1). YAML mapping dari safe loader memang berupa dict.
Tidak mencatat nilai mentah atau menganggap item scalar/list memiliki identitas
simbol. Degradasi terbatas pada item tanpa mapping dalam list yang sedang dibaca;
entri mapping tetap menjalankan kontrak lama. Semua pasar berbagi guard ini
agar item tanpa identitas tidak menghalangi entri valid pasar mana pun; kebijakan
reader/normalisasi pasar lain tidak berubah. Warning muncul sekali per item per
inisialisasi loader, termasuk saat data sehat diambil dari cache. Helper IDX
membuat instance per simbol sehingga warning dapat berulang antarsimbol.

Ini bukan validator YAML lengkap. Pada audit ini top-level/`sources` salah bentuk,
simbol non-string, YAML syntax error dan keputusan duplikasi memerlukan slice
terpisah; simbol non-string kemudian ditutup oleh follow-up di atas.
Simbol yang tidak memiliki mapping tetap memakai omission/no_data existing;
jika seluruh item tidak dapat dipetakan, warning menunjukkan kerusakan tetapi
diagnostik per simbol belum dapat membedakannya dari simbol tidak dikonfigurasi.
Tidak mengklaim semua konfigurasi cacat kini memiliki `fetch_failed`.
Entri IDX yang memiliki simbol tetapi reader cacat tetap `fetch_failed`, sumber
berschema valid tanpa bar tetap `no_data`, dan peer berdata tetap dimuat.

Cache tidak memerlukan token baru: `_ensure_config` berjalan sebelum cache
lookup, sehingga cacat struktur ini sebelumnya mencegah pembacaan cache positif,
bukan menyimpan bar cacat. Tes mengisi cache sehat, menyisipkan null sebelum
entri valid, melarang reader I/O, lalu membuktikan frame identik, warning tetap
muncul, daftar file dan semua byte cache tetap utuh. Identity deklarasi, token
IDX existing, file/WAL revision dan kebijakan None/empty tetap sama; regresi
revision/schema ikut dijalankan. Cache pengguna tidak dibaca/dihapus.

### Verifikasi isolasi entri

Artefak: `%TEMP%\idx-local-structure-ggockd1m`.
Sebelum edit: status Git, inventaris NUL-delimited UTF-8 (`core.quotepath=false`),
SHA-256 3.194 file publik, salinan/hash index dan loader disimpan. Nama
dotenv/token/secret dikecualikan. Runner historis diperiksa sebelum disalin;
interpreter proyek existing, bukan instalasi bersih. Environment allowlist,
home/appdata/localappdata/runtime/temp/cwd sementara dan dotenv stubs dipasang
sebelum import proyek. Run regresi/probe juga memeriksa tidak adanya direktori
legacy sessions/runs/uploads/.swarm/runs di source; audit hook menolak pembacaan
dotenv di luar QA. Pytest memindah home lagi ke sandbox di TEMP terisolasi.
Probe memblokir socket connect; tes offline memakai pytest-socket.

Perintah aktual dari root (runner meneruskan `-c <repo>/pyproject.toml`):

```powershell
$qa = '%TEMP%\idx-local-structure-ggockd1m'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --audit
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_local_loader_source_entries.py" -q --disable-socket --tb=short
$local = 'test_local_loader_source_entries.py','test_idx_local_source_config.py','test_idx_local_date_schema.py','test_idx_local_dates.py','test_idx_local_prices.py','test_idx_local_volume.py' | ForEach-Object { "$PWD/agent/tests/$_" }
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @local -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_local_loader_source_entries.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_local_loader_source_entries.py
git diff --check
```

Hasil **28 tes baru lulus**, enam modul local **304 passed, 2 warnings**;
regresi 45 modul **1.365 passed, 3 skipped, 7 warnings**, 37,75 detik. Tiga skip
adalah pembacaan Parquet yang memerlukan engine pandas opsional; decoder Parquet
nyata belum diverifikasi. Warning deprecation anyio/Starlette dan arithmetic
ekstrem fixture tetap terlihat. Ruff lint loader/tes dan format tes lulus;
loader tidak diformat ulang luas. Black tidak tersedia (`No module named black`);
dependency tidak diubah/dipasang.

Probe surface memakai JSON akuisisi existing dan entry point CLI riset existing.
Resolver memverifikasi source hanya local lalu memakai registry asli; seam
akuisisi CLI diarahkan ke local karena CLI riset tidak menyediakan opsi source.
YAML menyisipkan null, string marker dan list sebelum delapan entri mapping.
Ketiganya menghasilkan warning nomor 1/2/3 tanpa marker mentah. Lima reader
cacat tetap `fetch_failed`; GGRM valid kosong `no_data`; BBRI volume hilang
tetap null dan TLKM nol tetap 0, harga close tetap 105 serta provenance local
tanpa metadata IDR buatan. CLI exit **2**, status **unavailable**,
`backtest_enabled: false`: lima gagal akuisisi, satu kosong dan dua berdata
ditolak pada `currency_declaration`. File DuckDB yang tidak boleh dibuka tetap
tidak dibuat. Tidak ada network fallback atau provider nyata.

DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka; backtest IDX nonaktif,
Index Alpha ditunda. Metadata IDR/timezone/interval/unit/adjustment/provenance
local dan semantik timestamp/bucket tetap memerlukan ekspor asli berizin serta
[handoff referensi](IDX_REFERENCE.md) dan [provider](IDX_PROVIDER_RESEARCH.md).
Backend/safety penuh, frontend/build, MCP eksternal, Electron packaged app dan
deployment tidak dijalankan. Assembler/auth/lifespan/scheduler, trading serta
dependency tidak berubah. Tanpa staging, commit, publish atau deployment.

Pemeriksaan akhir: **224 tautan lokal/anchor** valid pada lima dokumen yang
diubah, UTF-8 dan `git diff --check` lulus (Git hanya memberi warning konversi
LF/CRLF pada file working tree existing). Dari **3.194 file publik baseline**,
**3.188 identik**, enam berubah dan satu tes baru; tidak ada file baseline
hilang. File sesi hanya loader, `tests/test_local_loader_source_entries.py`,
README.md, README_id.md, PROJECT_STATUS.md, TODO.md dan dokumen ini.
Hash index sebelum/sesudah identik:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Perubahan lama termasuk frontend/packaging dipertahankan. Baseline, audit,
runner, daftar modul, log red/green/targeted/regression/probe serta
`verification.json` disimpan di QA. Verifikasi integritas/dokumen:

```powershell
.venv/idx312/Scripts/python.exe -I "$qa/check_session.py"
git diff --check
```

## DATA-03 — Konfigurasi sumber Local Data Bridge

Subset **2026-11-04, Asia/Jakarta** menutup gap konfigurasi reader yang tercatat
pada audit schema tanggal. Sebelum edit, `_fetch_one` pada
`backtest/loaders/local_loader.py:419–421, 437–442, 446–449` mengembalikan None
untuk type tidak didukung atau setting wajib kosong. Helper
`src/market_data.py:388–390` kemudian merekam no_data. Selain itu, db_path kosong
diproses melalui `Path("")` menjadi `.` sebelum pengecekan kosong; tipe nilai
salah dapat memicu AttributeError/TypeError alih-alih error konfigurasi spesifik.

Grounded: loader fetch, seluruh reader, normalizer, resampling, identity/revision
cache, registry, runner, helper per simbol dan tool/CLI serta tes terkait dibaca.
Blast radius: validasi deklarasi reader di `_fetch_one`, khusus IDX. Invariant:
pasar lain mempertahankan omission/log existing; tidak mengubah schema kolom,
timestamp/bucket, metadata, harga atau volume; nol/null, peer/provenance dan
larangan fallback jaringan dari local eksplisit tetap berlaku. Verify: modul
baru `tests/test_idx_local_source_config.py`, lima modul local IDX, regresi
44 modul, Ruff dan JSON/CLI sintetis dengan runtime terisolasi.

Regresi awal **47 failed, 14 passed**. Type unsupported dan field blank/absent
tidak melempar (`DID NOT RAISE ValueError`), tipe salah menghasilkan exception
Python generik, db_path kosong mencapai reader pada probe I/O, dan helper
menghasilkan no_data ketika diharapkan fetch_failed. Log red tersimpan di QA.

Validasi kini memeriksa deklarasi mentah sebelum memilih reader atau membentuk
Path: type yang hadir wajib string dan cocok dengan registry `_READERS` existing
setelah strip/lower. Jika type tidak ditulis, default CSV tetap berlaku.
CSV/Parquet mewajibkan path string nonblank; DuckDB mewajibkan db_path dan query
string nonblank. Null, boolean, angka, list dan mapping ditolak. Pesan ValueError
menyebut type atau nama field tetap, tanpa menyalin nilai konfigurasi. Fetch
mencatat warning lalu meneruskan exception IDX; helper tetap merekam fetch_failed
dan mengisolasi simbol. Non-IDX tidak mendapat policy baru.

Tidak menormalisasi ulang db_path yang valid atau membatasi SQL baru; reader
DuckDB existing tetap read-only. Validasi bukan sertifikasi keberadaan file,
izin akses, kebenaran SQL, schema hasil atau seluruh YAML. YAML global malformed,
entri duplikat dan kebijakan simbol yang tidak dikonfigurasi belum diaudit penuh;
simbol tanpa entri tetap no_data existing. File valid tanpa bar/rentang kosong
tetap no_data. Ketiga reader mempertahankan harga dan nol/null tanpa menambah
metadata IDR/Jakarta/unit saham/adjustment.

Cache tidak memerlukan token baru: identity existing sudah memasukkan type,
path/db_path/query, columns dan date_format; None/empty tidak disimpan.
Deklarasi cacat pada kasus ini sebelumnya gagal atau kosong, bukan hasil positif.
Tes mengisi cache valid, mengubah path menjadi blank, membuktikan error serta
byte dan daftar file cache tidak berubah, lalu memulihkan deklarasi dan membaca
cache positif tanpa reader I/O. Source revision/file/WAL existing tidak berubah;
cache pengguna tidak dihapus. Kontrol revision dan schema existing ikut regresi.

### Verifikasi konfigurasi sumber local

Artefak QA: `%TEMP%\idx-local-config-75b1796d`.
Status, hash file publik, salinan index Git dan loader disimpan sebelum edit.
Inventaris memakai `core.quotepath=false` sehingga path non-ASCII juga dihash;
nama dotenv/token/secret dikecualikan. Runner sesi schema tanggal dibaca ulang
dan disalin: interpreter proyek existing, bukan instalasi bersih. Environment
allowlist tanpa kredensial serta assertions home/appdata/localappdata/runtime/
temp/cwd sementara berjalan sebelum import proyek; dotenv dinonaktifkan dan
distub. Pytest membuat home sandbox di TEMP terisolasi. Probe memblokir socket
connect dan memakai YAML/CSV sintetis; tidak membaca dotenv atau state akun.

```powershell
$qa = '%TEMP%\idx-local-config-75b1796d'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_local_source_config.py" -q --disable-socket --tb=short
$local = 'test_idx_local_source_config.py','test_idx_local_date_schema.py','test_idx_local_dates.py','test_idx_local_prices.py','test_idx_local_volume.py' | ForEach-Object { "$PWD/agent/tests/$_" }
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @local -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_source_config.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_local_source_config.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_source_config.py
git diff --check
```

Hasil: **61 tes baru** lulus, lima modul local IDX **276 passed, 2 warnings**;
regresi 44 modul **1.337 passed, 3 skipped, 7 warnings** (64,57 detik).
Skip membutuhkan engine Parquet opsional; tes baru memakai stub decoder Parquet,
CSV/DuckDB sintetis nyata. Decoder Parquet tidak diverifikasi. Warning berasal
dari deprecation anyio/Starlette dan fixture arithmetic ekstrem. Ruff lint dan
format tes baru lulus; loader tidak diformat ulang luas. Black tidak tersedia
(`No module named black`); tidak ada dependency ditambah/diubah.

Surface JSON: BBCA type unsupported, BMRI path blank, ASII path Parquet absent,
ANTM db_path blank dan INDF query absent → fetch_failed. File DuckDB fixture
yang tidak boleh dibuka tetap tidak dibuat. GGRM berschema valid tanpa bar →
no_data; BBRI volume hilang → null; TLKM nol → 0. Peer berdata mempertahankan
provenance local. CLI existing dengan delapan simbol menghasilkan exit **2**,
status **unavailable**, backtest_enabled **false**; lima simbol cacat gagal
akuisisi, satu kosong, dua berdata ditolak pada currency_declaration.

Implementasi dan tes subset terbukti; penerimaan local/provider tetap belum.
Timestamp/bucket dan metadata memerlukan ekspor asli berizin sesuai handoff
[reference](IDX_REFERENCE.md) dan [provider](IDX_PROVIDER_RESEARCH.md).
DATA-01/02/03, IDX-02, RESEARCH-01 penuh tetap terbuka; backtest IDX nonaktif
dan Index Alpha ditunda. Backend/safety penuh, provider nyata, frontend, MCP
eksternal, Electron packaged app dan deployment tidak diuji. Tanpa perubahan
assembler/auth/lifespan/scheduler, dependency atau trading; tanpa staging,
commit, publish atau deployment. File sesi: loader, satu tes baru, kedua README,
PROJECT_STATUS, TODO dan dokumen ini; pekerjaan sebelumnya dipertahankan.

Pemeriksaan akhir: **218 tautan lokal/anchor**, UTF-8, konsistensi status/backlog
dan `git diff --check` lulus. Dari **3.193 file publik baseline**, **3.187 identik**,
enam diperluas dan satu tes baru ditambahkan; tidak ada file baseline hilang.
Hash index Git sebelum/sesudah tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Baseline, daftar modul, log red/green/targeted/regression/probe dan
`verification.json` berada di direktori QA di atas. Tidak ada staging/commit.

## DATA-03 — Schema tanggal Local Data Bridge

Catatan lanjutan: gap konfigurasi type/path/query yang disebut pada audit
historis di bawah ditutup oleh [increment konfigurasi sumber](#data-03--konfigurasi-sumber-local-data-bridge).
Batas timestamp/bucket dan metadata pada audit tersebut tetap berlaku.

Subset **2026-11-04, Asia/Jakarta** menutup kolom tanggal absent yang sebelumnya
tampak sebagai sumber kosong. Bukti sebelum edit: normalizer
`backtest/loaders/local_loader.py:208–215` memakai DatetimeIndex sebagai sumber
tanggal bila kolom yang dipetakan tidak ada; `:231–233` mengembalikan None bila
keduanya tidak tersedia. Ketiga reader bertemu pada normalizer ini; `_fetch_one`
meneruskan None dan helper `src/market_data.py:388–390` merekam no_data.
Harga/volume yang valid tidak dapat memberi tanggal pada observasi tersebut.

Grounded: normalizer, ketiga reader, fetch/cache/source revision, resampler,
registry dan pemanggil helper/riset/CLI beserta tes diperiksa. Blast radius:
satu guard schema pada normalizer local IDX. Invariant: pasar lain tetap
return-None; DatetimeIndex, mapping dan date_format existing tetap berlaku;
tidak membuat tanggal, harga, volume atau metadata; volume nol/null, provenance,
isolasi simbol dan explicit-local tanpa fallback jaringan tetap terjaga.
Verify: modul baru `tests/test_idx_local_date_schema.py`, empat modul local IDX,
regresi 43 modul, Ruff serta probe surface JSON/CLI dengan fixture sintetis.

Regresi awal **18 failed, 17 passed**: kasus absent/mapping salah/cache tidak
melempar (`DID NOT RAISE ValueError`); helper memberi
`{'source': 'local', 'reason': 'no_data'}` ketika diharapkan fetch_failed.
Guard baru menolak schema IDX tanpa kolom tanggal atau DatetimeIndex, juga
pada frame nol bar dengan OHLC lengkap. Tidak meminjam kolom tanggal yang tidak
dipetakan. Empty dengan schema tanggal/OHLC valid tetap no_data. DatetimeIndex
tetap menyediakan tanggal ketika kolom absent, termasuk mapping ke kolom absent;
kolom eksplisit yang tersedia tetap mengalahkan index. Ini mempertahankan
precedence existing, bukan definisi schema produksi baru.

### Audit timestamp dan bucket yang belum diterima

Audit sintetis pada **pandas 2.3.3**, disimpan sebagai `timestamp-audit.json`:

- `date_format` string nonblank diteruskan ke pandas setelah strip; tanpa format
  digunakan inference. `%d/%m/%Y` menerima `01/09/2026`, mismatch ISO ditolak.
  Campuran date-only dan ISO datetime tanpa format ditolak pada fixture ini;
  `ISO8601` eksplisit menerima keduanya. Ini hasil versi parser terpasang,
  bukan daftar format ekspor yang disertifikasi.
- `mixed` juga diteruskan, bukan pola strptime yang dibatasi. Fixture
  `02/09/2026` menjadi **9 Februari**, bukan 2 September. Tidak ada deklarasi
  day-first atau schema provider yang membenarkan menebak arti input tersebut.
- Pada normalizer in-memory, angka `1788220800000000000` tanpa unit menjadi
  `2026-09-01` melalui default nanosecond pandas, sedangkan teks angka yang sama
  ditolak. CSV IDX membaca object; tipe Parquet/DuckDB dapat berbeda. Kontrak
  unit epoch dan bentuk timestamp lintas reader tetap membutuhkan ekspor asli.
- Naive `2026-09-01T06:59:59` tetap UTC-naive pada jam itu; aware
  `2026-09-01T06:59:59+07:00` menjadi `2026-08-31 23:59:59`.
  `utc=True` lalu `tz_convert(None)` tidak membuktikan tanggal sesi Jakarta.
- Filter tetap `start <= timestamp < end + 1 hari`, sebelum resampling. Probe
  end-day nanosecond mempertahankan `23:59:59.999999999`, menolak midnight
  berikutnya; hasil 1m berlabel `23:59`. Probe +07 di pergantian hari menghasilkan
  bucket `16:00` UTC-naive, tanpa memindahkannya ke kalender sesi Jakarta.
- Resampling memakai median jarak timestamp. Jarak cocok mempertahankan jam
  asal (dua bar harian `12:30` tetap `12:30`); request lebih halus mempertahankan
  source bars dengan warning. Downsample dua bar `12:30/13:30` ke harian berlabel
  midnight, dan `01:30/02:30` ke 4H berlabel `00:00`, memakai default pandas.
  Asal, label dan batas bucket belum dikalibrasi terhadap kontrak ekspor/sesi.
- Schema OHLC/date yang tidak lengkap kini gagal untuk IDX; invalid parsed dates
  dan OHLC/volume tetap ditolak sebelum filter. Konfigurasi sumber seperti type
  tidak didukung atau path/query absent masih dapat memberi None/no_data melalui
  cabang existing `_fetch_one`; ini gap konfigurasi terpisah, tidak ditutup oleh
  guard tanggal. Kelengkapan sesi, duplikasi timestamp dan seluruh bentuk schema
  provider tidak disertifikasi oleh increment ini.

Tidak ada perubahan parser, timezone, filter atau bucket. Local masih tidak
mendeklarasikan metadata wajib IDR/Jakarta/unit saham/adjustment sehingga fitur
riset menolaknya pada currency_declaration. Penerimaan semantik memerlukan
ekspor asli berizin dengan sumber, tanggal/revisi, cakupan dan arti field;
input minimum [reference](IDX_REFERENCE.md) dan [provider](IDX_PROVIDER_RESEARCH.md)
tetap berlaku. DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka;
backtest IDX nonaktif dan Index Alpha ditunda.

### Cache dan verifikasi schema tanggal

Token cache baru **tidak diperlukan** untuk kegagalan ini: sebelumnya normalizer
menghasilkan None, dan `loader_cache_put` (`base.py:635–636`) tidak menyimpan None
atau frame kosong. Identity menyertakan mapping/date_format, revision menyertakan
stat file/WAL; keduanya tidak berubah. Tes membuktikan cache positif pada file
valid tidak menyembunyikan penggantian file berschema cacat; entry cache valid
lama tetap ada. File cacat tidak menghasilkan negative cache, dan file yang
dikoreksi langsung dapat dibaca. Ini memakai kontrak revision existing, bukan
jaminan terhadap penggantian byte yang sengaja mempertahankan seluruh stat.

Artefak QA: `%TEMP%\idx-local-schema-4e64c389`.
Baseline status Git, SHA-256 file publik, salinan index dan loader sebelum edit
disimpan sebelum perubahan. Runner historis dibaca dan disalin ke direktori QA
baru, memakai interpreter proyek existing; ini bukan instalasi bersih. Environment
allowlist tanpa kredensial dan assertions home/appdata/localappdata/runtime/temp/
cwd sementara berjalan sebelum import proyek; dotenv dinonaktifkan dan distub.
Pytest menempatkan home sandbox di TEMP tersebut. Tidak membaca dotenv atau
state akun pengguna. Probe JSON/CLI juga memblokir socket connect.

```powershell
$qa = '%TEMP%\idx-local-schema-4e64c389'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_local_date_schema.py" -q --disable-socket --tb=short
# Run akhir empat modul local IDX:
$local = 'test_idx_local_date_schema.py','test_idx_local_dates.py','test_idx_local_prices.py','test_idx_local_volume.py' | ForEach-Object { "$PWD/agent/tests/$_" }
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @local -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --disable-socket --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --audit
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_date_schema.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_local_date_schema.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_date_schema.py
git diff --check
```

Hasil: **35 tes baru** lulus; run akhir empat modul **215 passed, 2 warnings**.
Regresi 43 modul **1.276 passed, 3 skipped, 7 warnings** (38,48 detik).
Tiga skip memerlukan engine Parquet opsional; tes baru memakai stub read_parquet,
CSV dan DuckDB file sintetis nyata. Decoder Parquet tidak diverifikasi.
Warning berasal dari deprecation anyio/Starlette dan fixture arithmetic ekstrem.
Ruff lint lulus; format tes sempat gagal satu layout dict, diperbaiki lalu check
lulus. Black tidak tersedia (`No module named black`), tanpa instalasi dependency.

Probe JSON via YAML/CSV asli: BBCA tanggal absent dan BMRI tanggal tidak dipetakan
→ fetch_failed, ASII empty berschema → no_data, BBRI volume hilang → null,
TLKM volume nol → 0. Peer berdata mempertahankan provenance local. CLI existing
exit **2**, status **unavailable**, backtest_enabled **false**; dua peer berdata
ditolak pada currency_declaration. Implementasi dan tes subset terbukti,
integrasi provider dan penerimaan local belum. Backend/safety penuh, frontend,
provider nyata, MCP eksternal, Electron packaged app dan deployment tidak diuji.
Tanpa perubahan dependency/trading/assembler/auth/lifespan/scheduler, staging,
commit atau publish. File sesi: loader, tes baru, kedua README, status, backlog
dan dokumen ini; pekerjaan sebelumnya dipertahankan.

Pemeriksaan dokumen: **211 tautan lokal/anchor**, UTF-8, konsistensi status/backlog
dan `git diff --check` lulus. Baseline SHA-256 mencakup **2.924 path publik**:
**2.918 identik**, enam file diperluas, satu modul tes ditambahkan, tidak ada
file baseline hilang. Inventaris hash awal mengecualikan nama sensitif dan
**268 path non-ASCII yang di-quote Git**; hash sebelum/sesudah tidak diklaim
untuk path tersebut. Checker integritas awal gagal karena membandingkan daftar
Git quoted terhadap path existing, lalu disesuaikan dengan cakupan baseline;
tidak ada perubahan aplikasi untuk masalah harness tersebut.
Hash index Git awal/akhir identik dengan catatan sesi sebelumnya:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
`verification.json`, status, daftar modul serta red/green/regression/probe/audit
logs berada di direktori QA di atas. Tanpa staging atau commit.

## DATA-03 — OHLC Local Data Bridge

Catatan lanjutan: gap kolom tanggal absent pada catatan historis ini telah
ditutup pada [increment schema tanggal](#data-03--schema-tanggal-local-data-bridge);
hasil run historis serta batas UTC/bucket dan metadata tetap berlaku.

Subset lokal **2026-11-04, Asia/Jakarta** menutup normalisasi OHLC yang dapat
menghilangkan cacat pada local IDX. Bukti sebelum edit:
`backtest/loaders/local_loader.py:254–259` melakukan coercion, dropna dan
`validate_ohlc` dengan default drop sebelum filter/resampling; `:221–223`
mengembalikan None untuk field harga hilang. Validator base menguji
struktur/positivitas, bukan kelengkapan/finite. Regresi sintetis awal
**101 failed, 13 passed**: cacat diterima (`DID NOT RAISE ValueError`), field
hilang menjadi data kosong, cache lama menyajikan seri pendek dan simbol cacat
tidak memperoleh diagnostik kegagalan. Log lengkap ada pada artefak QA.

Grounded: normalizer dan ketiga reader, seluruh pemanggilnya, loader fetch,
resampling, cache/source revision, runner/registry, helper akuisisi dan tool/CLI
riset dicocokkan dengan tes local/IDX. Blast radius: cabang normalizer local IDX
dan fields cache-nya. Invariant: tidak membuat harga, tanggal, volume atau
metadata; volume nol/null, source revision, peer/provenance dan explicit-local
tanpa fallback jaringan dipertahankan; pasar lain tetap memakai kebijakan
normalisasi/cache existing. Tidak ada perubahan jalur trading.

Normalizer local kini menolak field OHLC hilang dan harga mentah boolean/kompleks
sebelum coercion. Setelah numeric conversion, harga missing atau nonfinite
menolak seri sebelum dropna. Invariant tetap dimiliki `validate_ohlc` existing,
dipanggil dengan strategy raise untuk IDX dan drop untuk pasar lain. Tidak
memakai `stamp_idx_frame` karena helper itu juga mendeklarasikan metadata yang
belum tersedia dari ekspor local. Guard volume `normalize_idx_volume` tetap
dipakai tanpa perubahan; helper/cache Yahoo/yfinance tidak berubah.

Setiap bar local bertanggal merupakan observasi eksplisit: OHLC all-null
menolak seri, termasuk jika volumenya null. Kontrak padding/join provider
Yahoo tidak dipinjam untuk file local yang tidak memilikinya. String harga
numerik valid tetap diterima; CSV tetap tunduk pada null parsing pandas,
Parquet/DuckDB pada tipe/null reader. Ini bukan validasi byte mentah atau
sertifikasi schema provider. File kosong **dengan schema OHLC/date** tetap
no_data; field harga hilang menjadi fetch_failed, termasuk pada frame kosong
yang schema-nya tidak memenuhi kontrak. Kolom tanggal yang absen masih menjadi
return-None existing; bukan gap yang ditutup pada increment OHLC ini.

Validasi dilakukan pada seluruh file sebelum filter rentang dan resampling.
Bar cacat di luar rentang permintaan tetap menolak file; tidak ada harga
pengganti atau pembuangan bar yang membuat agregat tampak sehat. Hal ini tidak
mendeteksi bar yang tidak pernah ada dalam file atau membuktikan kelengkapan
sesi, libur, suspensi atau corporate actions. Konversi UTC-naive, filter
half-open dan bucket pandas tetap existing; metadata ekspor nyata diperlukan
untuk menentukan tanggal sesi Jakarta, bukan ditebak dari ticker.

Identitas cache menambah **`idx_local_prices_v1`** setelah token volume/tanggal
existing. Tes menanam cache kontrak tanggal sebelumnya yang sehat di atas file
dengan high hilang; fetch baru menolak dan entry lama tetap tersedia. Cache
valid baru dapat dibaca tanpa akuisisi ulang. Source revision file/schema
tetap berlaku; cache pengguna tidak dihapus. Exception diteruskan melalui log
existing ke helper sebagai fetch_failed; helper tetap mengisolasi IDX per
simbol, sementara pemanggilan loader langsung dengan batch dapat melempar.

### Verifikasi OHLC local

Artefak QA: `%TEMP%\idx-local-prices-ca19c7b0`.
Status, SHA-256 seluruh file perubahan, index Git dan salinan loader sebelum
edit disimpan di sana. Runner yang diperiksa memakai interpreter proyek
existing; environment allowlist tanpa kredensial, home/appdata/localappdata/
temp/runtime/cwd sementara, dotenv disabled/stub dan assertions isolasi sebelum
import proyek. Pytest memasang home sandbox di TEMP terisolasi. Tidak ada
state/.env pengguna nyata yang dibaca; ini bukan instalasi bersih baru.

```powershell
$qa = '%TEMP%\idx-local-prices-ca19c7b0'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_local_prices.py" "$PWD/agent/tests/test_idx_local_dates.py" "$PWD/agent/tests/test_idx_local_volume.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_prices.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_local_prices.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_prices.py
git diff --check
```

Hasil: **114 tes baru**, gabungan tiga modul local IDX **180 passed, 2 warnings**
dengan socket disabled. Regresi 42 modul **1.241 passed, 3 skipped, 7 warnings**
(33,83 detik); daftar modul melanjutkan 40 modul tanggal local plus modul harga
baru dan validator OHLC existing. Tiga skip memerlukan engine Parquet opsional;
tes harga baru memakai stub `pd.read_parquet`, sedangkan CSV dan DuckDB memakai
file sintetis nyata. Decoder Parquet belum diverifikasi. Warning regresi
berasal dari deprecation anyio/Starlette dan fixture arithmetic ekstrem.
Ruff lint dan format tes baru lulus; loader tidak diformat ulang secara luas.
Black tidak tersedia (`No module named black`); tidak ada dependency dipasang.

Probe surface JSON melalui YAML/CSV sintetis asli, dengan socket connect
diblokir: BBCA high parsial dan BMRI field open hilang → fetch_failed;
ASII file kosong → no_data; BBRI volume hilang → null; TLKM nol → 0.
Peer sehat tetap memiliki provenance local. CLI existing menghasilkan exit
**2**, status unavailable, backtest false; BBCA/BMRI gagal akuisisi, ASII
kosong, BBRI/TLKM ditolak pada currency_declaration. Implementasi serta tes
subset terbukti; integrasi provider berizin, penerimaan local dan deployment
tidak dibuktikan oleh fixture. DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap
terbuka. Input minimum pada handoff reference/provider tetap diperlukan.

Tujuh file sesi: loader local, tes baru `agent/tests/test_idx_local_prices.py`,
kedua README, PROJECT_STATUS, TODO dan dokumen ini. Tanpa perubahan frontend,
dependency, assembler/auth/lifespan/scheduler, trading, staging, commit,
publikasi atau deployment. Provider nyata, backend/safety penuh, frontend
test/build, MCP eksternal dan Electron packaged app tidak dijalankan.

Pemeriksaan akhir: **205 tautan lokal/anchor**, konsistensi status/backlog dan
`git diff --check` lulus. Dari 78 file baseline, **72 mempertahankan SHA-256**;
enam diperluas dan satu tes baru ditambahkan, tanpa file baseline hilang.
Hash index Git awal/akhir tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Log, daftar modul dan ringkasan integritas berada di direktori QA di atas.

## DATA-03 — Tanggal Local Data Bridge

Catatan lanjutan: gap OHLC yang dicatat pada audit historis di bawah telah
ditutup pada [increment OHLC local](#data-03--ohlc-local-data-bridge) di atas;
hasil run dan batas semantik timestamp sesi tanggal tetap berlaku.

Subset lokal **2026-11-04, Asia/Jakarta** menutup pembuangan tanggal cacat pada
normalizer local IDX. Audit sebelum edit: `backtest/loaders/local_loader.py:232–240`
memakai `pd.to_datetime(errors="coerce", utc=True)` lalu membuang `NaT` sebelum
guard volume/OHLC, filter rentang dan resampling. Fixture sintetis awal
**19 failed, 9 passed**: `DID NOT RAISE ValueError` pada tanggal invalid/null,
format salah, DatetimeIndex NaT dan cache lama; diagnostik simbol cacat juga
hilang (`KeyError: 'BBCA.JK'`) karena seri pendek dikembalikan sebagai sukses.

Grounded: tiga reader existing, seluruh pemanggil normalizer/resampler, loader
fetch/cache, runner local, registry, helper akuisisi, tool/CLI riset dan tes
local/routing diperiksa. Blast radius: satu guard pada normalizer local IDX dan
fields identitas cache IDX. Invariant: tidak membuat tanggal/harga/volume,
pasar lain mempertahankan drop policy dan cache existing, volume nol/null tetap
berbeda, source revision/provenance serta explicit-local tanpa fallback
jaringan dipertahankan. Isolasi peer tetap dimiliki helper bersama.

Guard pada `backtest/loaders/local_loader.py:237` kini menolak seri bila hasil
parsing tanggal mengandung NaT, sebelum bar dibuang. Cakupannya adalah bar yang
mencapai parsing tanggal pada schema OHLC/date existing: null, teks invalid,
tanggal kalender invalid, di luar rentang timestamp pandas dan mismatch format
yang menghasilkan NaT. Ini bukan parser/schema ekspor baru atau validator semua
bentuk timestamp. Kolom tanggal tidak tersedia atau schema OHLC tidak lengkap
masih mengikuti return-None existing dan menjadi gap terpisah. File kosong
**dengan schema** tetap kosong; file tanpa schema tidak disertifikasi.
Karena seluruh file dinormalisasi sebelum filter, tanggal yang tidak bisa
ditempatkan dalam rentang menolak file meskipun sebagian bar lain berada di
luar permintaan. Bar yang valid tetapi seluruhnya di luar rentang tetap no_data.
Tidak ada kontrak padding local yang membenarkan pembuangan bar tanpa tanggal.

Cache IDX kini memakai identity file/schema existing ditambah
`idx_local_volume_v1` dan **`idx_local_dates_v1`**. Tes menanam cache kontrak
volume sebelumnya yang tampak sehat di atas file bertanggal rusak; akuisisi
baru menolak file dan entry lama tetap utuh. Source revision tidak berubah.
Roundtrip cache valid serta perubahan sumber diuji oleh modul local existing;
cache pengguna tidak dihapus. Error diteruskan melalui warning existing ke
helper sebagai fetch_failed; pemanggilan loader batch langsung masih dapat
melempar, sedangkan helper mengisolasi peer per simbol.

### Audit tanggal, batas dan OHLC yang tersisa

- Parsing aware/naive tetap memakai UTC, kemudian `tz_convert(None)`; tanggal
  naive diperlakukan sebagai UTC existing, bukan diklaim sebagai waktu Jakarta.
  Filter `start <= timestamp < end + 1 hari` berada di `:437–445`; resampling
  `:123–141` memakai median jarak dan bucket UTC-naive pandas. Tes kontrol IDX/US
  dekat pergantian hari mengunci perilaku existing, bukan menerima semantiknya
  untuk ekspor IDX. Offset +07 dapat berpindah tanggal UTC; belum ada metadata
  yang membenarkan perubahan ke Jakarta atau tanggal sesi.
- OHLC nonnumerik/parsial menjadi NaN lalu dibuang di `:256–258`; invariant
  memakai `validate_ohlc` default drop di `:259`. Probe sintetis terpisah
  membuktikan masing-masing dua bar menjadi satu pada ketiga kasus. Tidak ada
  pemeriksaan finite khusus pada normalizer local; validator base memeriksa
  struktur/positivitas, bukan kelengkapan finite. Cast float64 bukan sertifikasi.
- Resampling `first/max/min/last` dan drop bucket tanpa OHLC dapat menyamarkan
  bar yang telah dibuang. Guard tanggal baru melindungi cacat tanggal; OHLC
  dengan tanggal valid masih pekerjaan berikutnya. Tidak ada inferensi bahwa
  bar tidak teramati merupakan libur/suspensi atau bahwa file lengkap terhadap
  kalender. Tidak ada metadata IDR/Jakarta/satuan/adjustment yang ditambahkan.

### Verifikasi tanggal local

Artefak QA: `%TEMP%\idx-local-ohlc-f6b7aa2f`.
Baseline status, SHA-256 file perubahan dan index disimpan sebelum edit.
Runner QA yang diperiksa ulang memakai interpreter proyek existing, environment
allowlist tanpa kredensial, home/appdata/localappdata/temp/runtime/cwd sementara,
dotenv disabled/stub sebelum import. Assertions membuktikan isolasi sebelum
modul proyek diimpor; pytest memasang home sandbox-nya di TEMP terisolasi.
Ini bukan instalasi bersih. Tidak ada state/.env pengguna yang dibaca.

```powershell
$qa = '%TEMP%\idx-local-ohlc-f6b7aa2f'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_local_dates.py" "$PWD/agent/tests/test_idx_local_volume.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_dates.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_local_dates.py
.venv/idx312/Scripts/python.exe -m black --check agent/backtest/loaders/local_loader.py agent/tests/test_idx_local_dates.py
git diff --check
```

Hasil: **28 tes baru**, tanggal+volume **66 passed, 2 warnings** dengan socket
disabled; regresi **1.121 passed, 3 skipped, 7 warnings** pada 40 modul (31,71
detik). Daftar modul QA melanjutkan 39 modul volume local sebelumnya plus
modul tanggal baru. Tiga skip existing memerlukan engine Parquet opsional;
tes tanggal baru memakai stub batas `pd.read_parquet`, sedangkan CSV/DuckDB
memakai file sintetis nyata. Ini tidak memverifikasi decoder Parquet. Warning
berasal dari anyio/Starlette deprecation dan fixture arithmetic ekstrem.
Ruff lint dan format tes baru lulus; loader tidak diformat ulang secara luas.
Black gagal dijalankan: `No module named black`; dependency tidak dipasang.

Probe surface JSON membaca YAML/CSV sintetis melalui reader asli dan memblokir
network connect: BBCA tanggal invalid → fetch_failed, ASII kosong → no_data,
BBRI volume hilang → null, TLKM nol → 0. Peer tetap memiliki provenance local.
CLI existing menghasilkan exit **2**, status unavailable dan backtest false;
BBCA gagal akuisisi, ASII kosong, BBRI/TLKM ditolak pada currency_declaration.
Karena itu implementasi/tes subset terbukti, tetapi penerimaan local/provider
dan metadata tetap belum terpenuhi. DATA-01/02/03, IDX-02, RESEARCH-01 penuh
tetap terbuka; handoff ekspor/reference/provider existing tetap berlaku.

File sesi: loader local, tes baru `agent/tests/test_idx_local_dates.py`, kedua
README, PROJECT_STATUS, TODO dan dokumen ini. Tidak ada perubahan dependency,
frontend, trading, assembler/auth/lifespan/scheduler, staging, commit atau
deployment. Provider nyata, backend/safety penuh, frontend test/build, MCP
eksternal dan Electron packaged app tidak diverifikasi pada increment ini.

Pemeriksaan akhir: **202 tautan lokal/anchor**, konsistensi status/backlog dan
`git diff --check` lulus. Dari 77 file baseline, **71 mempertahankan SHA-256**,
enam diperluas dan satu tes baru ditambahkan; tidak ada file baseline hilang.
Hash index awal/akhir tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Log, daftar modul, probe, baseline dan ringkasan `verification.json` berada
di direktori QA di atas. Tidak ada staging atau commit.

## DATA-03 — Volume Local Data Bridge

Subset lokal **2026-11-04, Asia/Jakarta** menutup hilangnya perbedaan volume
nol/null pada Local Data Bridge IDX. Bukti sebelum edit:
`backtest/loaders/local_loader.py:239` mengisi kolom absent dengan nol;
`:131` memakai agregasi `sum` yang mengabaikan null, sehingga seluruh volume
hilang menjadi nol dan volume parsial menjadi total. `:232,236` melakukan
coercion/cast sebelum guard volume IDX. Tiga reader existing semuanya berujung
pada normalizer tersebut. Regresi awal **21 failed, 7 passed** menunjukkan
nilai volume yang salah, nilai invalid yang diterima dan cache lama yang
menyembunyikan cacat; tidak ada sumber pasar nyata yang dibaca.

Grounded: reader CSV/Parquet/DuckDB, normalizer, resampler, get/put cache dengan
source revision, seluruh pemanggil dan tes local/routing dibaca sebelum edit.
Blast radius: cabang local IDX, reuse validator volume kontrak bersama dan
identitas cache local IDX. Invariant: tanpa harga/volume pengganti, nol/null
terpisah, pasar lain tetap pada kebijakan existing, explicit local tidak
fallback jaringan, helper tetap mengisolasi simbol/provenance, tidak menebak
metadata atau mengaktifkan IDX backtest/paper/live.

Kolom volume absent kini menjadi NaN khusus IDX. Setiap nilai volume yang
tersedia diperiksa sebelum coercion dengan `normalize_idx_volume` pada
`idx_contract.py`; helper scalar sebelumnya privat kini diekspos agar tiga
transport/file-reader tidak menyalin validator. Kontrak dan cache Yahoo/yfinance
tidak berubah. Boolean, kompleks, nonnumeric, negatif/nonfinite dan overflow
yang sampai ke guard ditolak dengan pesan tetap; string angka valid diterima.
CSV IDX dibaca dengan dtype object untuk menghindari inferensi angka/boolean
sebelum guard. Konvensi null parser pandas existing tetap berlaku: token yang
sudah dibaca sebagai missing tidak dapat dibedakan lagi dari null. Parquet dan
DuckDB juga tunduk pada tipe/null yang dikembalikan pembacanya. Tidak ada klaim
validasi byte mentah seluruh format atau schema produksi provider baru.

Resampling IDX memakai `sum(min_count=len(values))`: total volume hanya tersedia
jika semua **bar penyusun yang teramati** memiliki volume. Nol lengkap tetap
nol; missing pada satu hari tidak mengubah total hari lain. Hasil agregasi yang
overflow ditolak. Bucket tanpa OHLC tetap dilewati; tidak dibuat bar, harga atau
volume untuk mengisi hari kosong. Ini tidak mendeteksi bar yang tidak pernah
ada dalam file, membuktikan kalender lengkap, atau menyimpulkan suspensi/libur.
Pemilihan bucket/timezone dan normalisasi OHLC/tanggal generic local belum
diubah; bagian itu tetap memerlukan kontrak metadata/ekspor yang nyata.

Cache memakai fields identity file/schema existing ditambah
`idx_local_volume_v1` khusus IDX. Cache lama dengan nol/total parsial harus
diakuisisi ulang; tes memastikan entry lama tetap ada dan cache baru dapat
dipakai tanpa membaca ulang file. Source revision tetap menjaga perubahan file.
Pasar lain mempertahankan key dan kebijakan normalisasi/resampling existing.

Exception local IDX kini diteruskan setelah warning existing, sehingga helper
memberi diagnostik `fetch_failed` dan mengisolasi simbol. Pemanggilan langsung
loader dengan batch IDX dapat melempar exception; isolasi peer berada pada
`src.market_data.fetch_market_data`, sama seperti dua transport Yahoo.
Jalur explicit local tetap hanya mencoba local. Metadata IDR, satuan saham,
Jakarta, adjustment dan provenance sumber ekspor belum dideklarasikan loader;
feature riset tetap menolak hasil local pada `currency_declaration`. Perbaikan
volume tidak membuat sumber tersebut diterima. Konvensi logging/source-empty
generic dan pembuangan OHLC/tanggal cacat yang tidak disentuh masih perlu audit
terpisah; tidak ada klaim audit seluruh loader selesai.

### Verifikasi local volume

Artefak QA: `%TEMP%\idx-local-volume-41f95aa1`.
Baseline status/hash seluruh file perubahan dan index disimpan sebelum edit.
Runner memakai interpreter proyek existing, environment allowlist tanpa
kredensial, home/appdata/localappdata/temp/runtime/cwd sementara dan dotenv
disabled/stub sebelum import proyek. Assertions membuktikan isolasi; pytest
kemudian memasang sandbox home-nya sendiri di TEMP terisolasi. CSV/DuckDB nyata
pada tmp_path; jalur Parquet baru memakai stub batas `pd.read_parquet`, karena
engine file opsional tidak tersedia. Itu pengujian jalur normalisasi, bukan
sertifikasi decoder Parquet.

```powershell
$qa = '%TEMP%\idx-local-volume-41f95aa1'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_local_volume.py" "$PWD/agent/tests/test_idx_volume_observations.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --allow-hosts=127.0.0.1,::1 --tb=short -rs
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/local_loader.py agent/backtest/loaders/idx_contract.py agent/tests/test_idx_local_volume.py agent/tests/test_idx_volume_observations.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/backtest/loaders/idx_contract.py agent/tests/test_idx_local_volume.py agent/tests/test_idx_volume_observations.py
git diff --check
```

Tes dua modul **91 passed, 2 warnings** dengan socket disabled, termasuk **38
tes baru**. Regresi 39 modul **1.093 passed, 3 skipped, 7 warnings, 26,23 detik**;
daftar modul pada artefak melanjutkan 38 modul sesi volume Yahoo, ditambah modul
local baru. Tiga skip existing membutuhkan engine opsional pyarrow; warning
adalah deprecation anyio/Starlette dan arithmetic ekstrem fixture, termasuk satu
overflow agregat baru yang memang ditolak. Ruff lint dan format tiga file
kontrak/tes lulus; local_loader existing tidak diformat ulang secara luas.
Black tidak tersedia pada runtime existing; dependency tidak ditambah.

Run pertama setelah fix **1 failed, 27 passed**: assertion roundtrip cache
membandingkan freq indeks (`None` versus `Day`), padahal kontrak cache existing
tidak menyimpan freq. Assertion disesuaikan dengan kontrol cache existing
(`check_freq=False`), tetap membandingkan tanggal, nilai dan null. Assertion
audit local pada tes sesi volume Yahoo juga diperbarui: absent kini missing,
bukan nol, sementara gate metadata tetap wajib menolak. Tidak ada gate gagal
yang disisihkan.

Probe terpisah membaca config YAML/CSV sintetis melalui reader asli; socket
connect diblokir dan resolver hanya menyediakan local. Surface JSON akuisisi
menunjukkan BBCA invalid → `fetch_failed`, BBRI parsial → volume `null`, TLKM
nol → `0`, ASII lengkap → `600`; peer/provenance local tetap tersedia. CLI
riset existing menghasilkan exit **2**, `unavailable`: BBCA gagal akuisisi,
ketiga simbol lain ditolak pada `currency_declaration`, backtest false.
Tidak ada metadata IDR/Jakarta/saham/adjustment yang ditambahkan secara buatan.

DATA-01/02/03, IDX-02, RESEARCH-01 penuh tetap terbuka. Local masih memerlukan
kontrak ekspor/metadata dan verifikasi timestamp/OHLC, satuan/adjustment serta
hak pemakaian; kalibrasi provider independen, referensi resmi, kalender dan
histori kejadian tetap membutuhkan input minimum pada handoff existing.
Tanpa akses provider, perubahan dependency/frontend, assembler/auth/lifespan/
scheduler, staging, commit, publikasi atau deployment. Backend/safety penuh,
frontend test/build, MCP eksternal dan Electron packaged app tidak dijalankan.

Pemeriksaan akhir: **200 tautan file lokal/anchor** pada lima dokumen dan
`git diff --check` lulus. Dari 76 file baseline perubahan sebelumnya, **68
mempertahankan SHA-256**, delapan diperluas dan satu tes baru ditambahkan.
Sembilan file sesi: `agent/backtest/loaders/local_loader.py`,
`agent/backtest/loaders/idx_contract.py`, `agent/tests/test_idx_local_volume.py`,
`agent/tests/test_idx_volume_observations.py`, `README.md`, `README_id.md`,
`PROJECT_STATUS.md`, `TODO.md`, dan dokumen ini. Hash index Git awal/akhir:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Tidak ada file baseline hilang, staging atau commit; log dan hash tetap berada
di temporary QA sesi ini.

## DATA-03 — Volume mentah sebelum coercion

Subset lokal **2026-11-04, Asia/Jakarta** menutup penyamaran volume invalid
sebagai volume hilang pada dua transport Yahoo. Sebelum edit,
`backtest/loaders/idx_contract.py:29` melakukan `to_numeric(errors="coerce")`
pada seluruh OHLCV; `yahoo_client.py:272` memakai `_to_float` yang mengubah
teks invalid menjadi `None`. Validasi volume berikutnya melewati null.
Boolean dapat menjadi 0/1 dan kompleks NumPy dapat kehilangan bagian imajiner.
Regresi awal **25 failed, 26 passed** mereproduksi `DID NOT RAISE ValueError`,
`OverflowError: int too large to convert to float`, fallback yang tidak berjalan,
dan watchlist yang salah berstatus `ok` alih-alih `partial`.

Grounded: pemanggil parser hanya `get_chart`, dipakai loader Yahoo dan tes;
normalizer IDX dipakai kedua loader existing. `yfinance_loader.py:232,343,397`
memakai normalizer, identitas cache bersama dan stamping. Helper
`src/market_data.py:376,387,479` mempertahankan chain, diagnostik `fetch_failed`
dan isolasi simbol. Blast radius: kontrak volume IDX, preservasi nilai pada
parser strict/pembentukan frame Yahoo dan identitas cache. Invariant: tanpa
volume/harga pengganti, null berbeda dari nol, input tidak dimutasi, pasar lain
tetap berperilaku existing, metadata IDR/Jakarta/daily/saham/adjustment dan
provenance fallback dipertahankan, backtest IDX tetap nonaktif.

`idx_contract.py:16,46` sekarang memvalidasi volume sebelum coercion maupun
pembuangan slot kosong. Null asli (`None`, NaN numerik, `pd.NA`) tetap missing;
nol serta string angka valid diterima. Teks invalid/kosong/`"NaN"`, boolean
Python/NumPy, kompleks (termasuk bagian imajiner nol dan complex-NaN), negatif,
nonfinite dan overflow menolak seri dengan pesan tetap tanpa nilai mentah.
Tidak ada konversi saham ke lot atau penambahan syarat integer. Presisi output
tetap mengikuti kontrak float loader existing. Parser strict
`yahoo_client.py:273` mempertahankan volume mentah; `yahoo_loader.py:175`
memakai dtype object khusus IDX agar inferensi pandas tidak overflow sebelum
guard. Default parser/caller dan normalisasi/cache pasar lain tetap sama.

Cache kedua transport memakai `("idx_valid_volume_v3",)` dari satu pemilik.
Cache v2 dapat menyimpan null hasil coercion; data itu tidak cukup untuk
revalidasi. Kedua transport mengakuisisi ulang jika hanya cache lama tersedia,
tanpa menghapusnya. Tes membuktikan v2 tetap dapat dibaca secara eksplisit dan
cache baru mempertahankan null/nol, attrs serta retrieval time.

### Audit Local Data Bridge

`local_loader.py:232,236,239` memakai coercion generik, konversi float, lalu
mengisi **kolom** volume absent dengan nol. Null yang sudah berada dalam kolom
tetap null; teks invalid dapat menjadi null. Tidak ada guard volume khusus pada
jalur itu: negatif/nonfinite dapat bertahan, boolean menjadi angka, dan cast
kompleks berisiko menghilangkan informasi. Resampling volume memakai `sum`
dan belum mendeklarasikan kontrak missing volume IDX. Ini gap terbuka, bukan
adapter produksi yang sudah diterima.

Fixture CSV sementara membuktikan `DataLoader.markets` mengiklankan `id_equity`,
hasilnya memiliki volume nol buatan untuk kolom absent, serta tidak memiliki
attrs quote_currency/volume_unit. Melalui routing dan tool riset asli dengan
resolver sintetis local-only, simbol tetap unavailable dengan
`reason: invalid_data_or_metadata`, `quality_issue.code: currency_declaration`.
Tidak ada schema/metadata provider yang ditebak atau loader local yang diubah.
Dukungan local penuh tetap memerlukan kontrak ekspor/satuan/metadata yang nyata.

### Verifikasi volume

Artefak QA: `%TEMP%\idx-volume-337b8123`.
Runner baru memakai interpreter proyek existing, environment allowlist tanpa
kredensial warisan, cwd/home/appdata/localappdata/temp/runtime sementara, cache
default off serta dotenv disabled/stub sebelum import proyek. Assertion sebelum
import membuktikan path isolasi; fixture suite kemudian memasang sandbox home
sendiri di TEMP terisolasi. Cache/CSV fixture hanya memakai tmp_path.

```powershell
$qa = '%TEMP%\idx-volume-337b8123'
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" "$PWD/agent/tests/test_idx_volume_observations.py" -q --disable-socket --tb=short
$mods = Get-Content "$qa/regression-modules.txt"
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" @mods -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe "$qa/run_tests.py" --probe
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/idx_contract.py agent/backtest/loaders/yahoo_client.py agent/backtest/loaders/yahoo_loader.py agent/tests/test_idx_volume_observations.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/backtest/loaders/idx_contract.py agent/tests/test_idx_volume_observations.py
git diff --check
```

Modul baru **53 passed, 1 warning** dengan socket disabled; regresi **1.055
passed, 3 skipped, 6 warnings, 25,87 detik**. Daftar 38 modul pada artefak
mencakup 30 modul follow-up OHLC sebelumnya, modul volume baru serta tujuh
modul local loader/routing/cache/revision. Tiga skip Parquet membutuhkan engine
opsional pyarrow; dependency tidak ditambah. Warning final adalah deprecation
anyio/Starlette dan arithmetic ekstrem fixture existing. Ruff lint dan format
dua file baru/kontrak lulus. Black tidak tersedia (`No module named black`);
file transport existing tidak diformat ulang secara luas.

Run perbaikan pertama masih gagal satu kasus overflow saat membentuk DataFrame;
dtype object di batas Yahoo menutupnya. Regresi luas awal **1 failed, 1.054
passed, 3 skipped** menemukan kesalahan fixture resolver local: patch nama fungsi
tidak mengganti argumen default terikat sehingga test memakai transport sintetis
dari fixture sebelumnya, dan satu percobaan koneksi diblokir pytest-socket.
Injeksi `loader_resolver` eksplisit melalui helper asli memperbaiki fixture;
run final tidak memiliki warning koneksi. Probe pertama juga salah meneruskan
`--probe` ke pytest; dispatch runner diperbaiki dan run final lulus.

CLI sintetis, kedua vendor transport di-stub dan socket connect diblokir,
menghasilkan exit **2**, `partial`, BBCA unavailable dan BBRI sehat **20 bar**.
Volume invalid pada bar paling awal tetap ditolak sebelum tail 20 bar; peer
melaporkan 19 volume tersedia, 1 hilang dan 1 nol, backtest false. Kegagalan kedua
transport tercatat `fetch_failed`. Ini bukti permukaan CLI lokal dengan fixture,
bukan probe/integrasi provider nyata atau konfirmasi vendor independen.

DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. SDK yfinance dapat
mentransformasi respons sebelum adapter; opsi SDK tidak diubah dan hasil ini
berlaku pada nilai yang sampai ke seam adapter. Kalibrasi volume independen,
schema local, referensi/kalender/histori kejadian dan entitlement tetap memerlukan
input nyata berizin pada handoff existing. Tidak ada perubahan frontend,
dependency, backtest/paper/live, assembler/auth/lifespan/scheduler; frontend
test/build, backend/safety penuh, MCP eksternal, Electron packaged app serta
deployment tidak dijalankan. Tanpa staging, commit atau publikasi.

Pemeriksaan akhir: **198 tautan lokal/anchor** pada lima dokumen dan
`git diff --check` lulus. Checker anchor QA sempat tidak mengenali empat anchor
HTML eksplisit pada README Indonesia; dukungan `<a id>` ditambahkan, tanpa
perubahan tautan produk. Dari 75 file baseline perubahan lama, **67 tetap
memiliki SHA-256 yang sama**; delapan diperluas, satu tes baru ditambahkan.
Sembilan file sesi: `agent/backtest/loaders/idx_contract.py`,
`agent/backtest/loaders/yahoo_client.py`, `agent/backtest/loaders/yahoo_loader.py`,
`agent/tests/test_idx_volume_observations.py`, `README.md`, `README_id.md`,
`PROJECT_STATUS.md`, `TODO.md` dan dokumen ini. Baseline status/hash dan log
tersimpan pada artefak QA. Hash index Git awal/akhir tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.

## DATA-03 — OHLC tidak lengkap dan isolasi simbol

Follow-up lokal **2026-11-04, Asia/Jakarta** melanjutkan subset invariant OHLC
di bawah. Bukti sebelum edit: `yfinance_loader._normalize_frame` mengubah nilai
non-numerik menjadi null lalu membuang bar; `yahoo_client._parse_chart` melewati
OHLC null sebelum loader melihatnya; `_rows_to_frame` juga membuang harga null.
Sebanyak **23 dari 27 tes awal gagal** dengan `DID NOT RAISE ValueError` atau
provenance/fallback yang salah; empat kontrol existing lulus.

Grounded: jalur `get_chart` → `_parse_chart` → `_rows_to_frame` dan
`DataLoader.fetch` → `_normalize_frame`, seluruh pemanggil produksi serta tes
Yahoo/yfinance dan kontrak IDX dibaca sebelum edit. Blast radius: parser strict
opt-in, normalisasi serta cache kedua loader, dan akuisisi helper khusus IDX.
Invariant: satu classifier/routing owner, tidak ada harga buatan, IDR/Jakarta/
daily/saham dan adjustment tetap eksplisit, volume nol berbeda dari null,
provenance fallback tetap terlihat, pasar lain tetap batch, IDX backtest nonaktif.
Verifikasi: pytest fixture offline pada modul baru/transport/shared data, diikuti
CLI dengan kedua provider sintetis dan network connect diblokir.

`idx_contract.normalize_idx_observations` sekarang memiliki kontrak bersama:
slot OHLCV seluruhnya null dilewati **sebelum** coercion. Setiap slot lainnya
harus memiliki seluruh field OHLC yang dapat dibaca numerik. Semua harga berupa
string invalid tidak boleh berubah menjadi padding; harga seluruhnya hilang
dengan volume nol yang teramati juga ditolak. String angka valid tetap diterima;
volume null tidak diisi nol. Slot kosong tidak membuktikan libur, suspensi atau
delisting. Field harga hilang ditolak; respons tanpa observasi tetap kosong.

`yahoo_client.get_chart(..., strict_ohlc=True)` menjaga kegagalan null/non-numerik
di parser; hanya loader IDX yang mengaktifkannya. Caller lain mempertahankan
default. Kedua loader memakai identitas cache bersama
`("idx_complete_ohlc_v2",)`; cache lama `None` maupun kontrak yfinance v1 tidak
digunakan. File cache lama tidak dihapus. Roundtrip cache baru mempertahankan
nilai dan attrs/retrieval; pasar lain tetap memakai identitas existing.

Probe CLI awal dengan BBCA cacat dan BBRI sehat mengungkap bahwa loader yang
melempar exception untuk BBCA menggagalkan seluruh batch; hasil yang diharapkan
partial tidak tercapai. Regresi tambahan mereproduksi `KeyError: 'BBRI.JK'`.
Pemilik routing `src.market_data.fetch_market_data` kini menjalankan chain
existing per simbol untuk grup IDX. Batching pasar lain, urutan sumber, batas
upaya dan larangan fallback jaringan dari local eksplisit tetap dipertahankan.
Ini menambah panggilan terpisah pada multi-simbol IDX; watchlist pribadi tetap
dibatasi delapan simbol. API/agent/MCP/CLI memakai helper yang sama.

### Verifikasi follow-up

Artefak lokal: `%TEMP%\idx-partial-ohlc-758b1f66`.
Runner menyiapkan cwd/home/appdata/localappdata/runtime/temp terisolasi di sana,
environment minimum tanpa kredensial warisan, cache default off dan dotenv
dinonaktifkan sebelum import proyek. Cache tes hanya pada `tmp_path`.

```powershell
$qa = '%TEMP%\idx-partial-ohlc-758b1f66\run_tests.py'
.venv/idx312/Scripts/python.exe $qa "$PWD/agent/tests/test_idx_incomplete_prices.py" -q --disable-socket
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/idx_contract.py agent/backtest/loaders/yahoo_client.py agent/backtest/loaders/yahoo_loader.py agent/backtest/loaders/yfinance_loader.py agent/src/market_data.py agent/tests/test_idx_incomplete_prices.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/backtest/loaders/idx_contract.py agent/tests/test_idx_incomplete_prices.py
.venv/idx312/Scripts/python.exe %TEMP%\idx-partial-ohlc-758b1f66\run_probe.py
git diff --check
```

Run gabungan akhir: **915 passed, 6 warnings, 23,92 detik**, runner yang sama
dengan `-q --allow-hosts=127.0.0.1,::1 --tb=short`. Sebanyak 30 modul:
`test_idx_incomplete_prices`, `test_idx_yfinance_quality`, `test_idx_foundation`,
`test_idx_reference`, `test_idx_research`, `test_idx_research_quality`,
`test_idx_research_provenance`, `test_idx_research_diagnostics`, `test_idx_symbol_search`,
`test_yahoo_loader`, `test_yahoo_client`, `test_market_data`,
`test_market_data_serving_source`, `test_market_data_tool`,
`test_get_market_data_unresolved`, `test_get_market_data_provenance`,
`test_mcp_new_tools`, `test_market_identity_parity`, `test_market_detection`,
`test_registry`, `test_composite_currency_guard`, serta sembilan
`test_yfinance*.py` pada `agent/tests/`. **39 tes baru** mencakup nonmutasi,
missing field, null/non-numerik, semua-slot kosong, string angka, cache, fallback,
isolasi peer sehat dan kontrol batching US. Log akhir `regression-final.log`.

Ruff lulus. Probe CLI independen menghasilkan exit **2**, status **partial**,
BBCA.JK unavailable, BBRI.JK sehat **20 bar**, `backtest_enabled: false`.
Kegagalan awal tes HTTP dengan `--disable-socket` adalah `SocketBlockedError`
pada socket internal event loop Windows; run loopback final lulus. Assertion
regresi peer sempat memakai akses frame pada output default berupa list;
tes diperbaiki dengan meminta `as_frames=True`. FutureWarning assignment fixture
None juga diperbaiki; enam warning akhir adalah deprecation anyio/Starlette
dan arithmetic ekstrem fixture existing. Tidak ada gate gagal yang disisihkan.

[Dokumentasi primer yfinance.download](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)
dibaca lagi pada **2026-11-04 WIB** untuk pertanyaan spesifik `keepna`/`repair`;
SDK terpasang `scrapers/history.py:523–530` dikonfirmasi menghapus bar yang seluruh
nilai datanya null/zero pada default. Opsi SDK tidak diubah; guard ini berlaku
untuk observasi yang sampai ke adapter, bukan jaminan mempertahankan setiap
slot respons Yahoo mentah atau kelengkapan sesi. Tidak ada aturan BEI baru
diterapkan, riset katalog/403 diulang, probe harga jaringan atau data resmi diimpor.
Input minimum referensi/provider pada peta gap di bawah tetap diperlukan;
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. Frontend/test/build,
backend/safety penuh, MCP eksternal, broker dan deployment tidak dijalankan.

Pemeriksaan akhir: modul baru **39 passed** dengan `--disable-socket`; Ruff,
177 tautan file lokal pada lima dokumen, anchor baru serta `git diff --check`
lulus. Sebanyak 64 dari 73 file perubahan lama pada baseline mempertahankan
SHA-256. Sembilan file baseline diperluas, satu file tracked yang awalnya bersih
(`yahoo_client.py`) diubah, dan satu file tes ditambahkan: total 11 file sesi ini.
Daftarnya: `agent/backtest/loaders/{idx_contract,yahoo_client,yahoo_loader,yfinance_loader}.py`,
`agent/src/market_data.py`, `agent/tests/test_idx_incomplete_prices.py`, dua README,
`PROJECT_STATUS.md`, `TODO.md`, dan dokumen ini. Hash index Git awal/akhir tetap
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Tidak ada staging atau commit; baseline dan log disimpan di temporary sesi.

## DATA-03 — Validasi OHLC yfinance sebelum pembuangan bar

Selesai subset lokal **2026-11-04, Asia/Jakarta**. Normalisasi yfinance sebelumnya
memanggil `validate_ohlc` dengan kebijakan default `drop`. Bar dengan high/low
bertentangan, open/close di luar rentang atau harga nonpositif dibuang sebelum
`stamp_idx_frame` memeriksa seri. Seri yang sudah kehilangan bar kemudian dapat
dilaporkan sehat. Kini IDX memakai kebijakan `raise`; helper akuisisi bersama
mempertahankan kegagalan melalui `fetch_failed` dan fallback existing.

Grounded: `backtest/loaders/yfinance_loader.py:197,241,370` serta
`backtest/loaders/idx_contract.py:23` dan `src/market_data.py:368,385` (relatif
`agent/`). Pemanggil normalizer produksi hanya `DataLoader.fetch`; helper bersama
melayani tool riset yang dipakai API/agent/MCP/CLI. Blast radius: normalisasi dan
identitas cache yfinance IDX. Invariant: nonmutasi input, IDR/Jakarta/harian/saham,
volume nol berbeda dari null, provenance dan kegagalan terlihat, perilaku serta
cache pasar lain tetap sama, backtest IDX tetap ditolak.

Cache lama tidak dapat membuktikan bar apa yang telah dibuang. Karena itu, get/put
IDX memakai identitas `fields=["idx_strict_ohlc_v1"]` yang sama; cache lama tidak
dihapus dan pasar lain tetap memakai `fields=None`. Fetch IDX pertama sesudah
perubahan memerlukan akuisisi baru bila hanya cache lama tersedia. Cache baru
mempertahankan bar, provenance dan retrieval time tanpa mengunduh lagi.

### Peta gap penerimaan sesi ini

- **DATA-01:** penerimaan MVP pribadi dan probe historis tetap berlaku dalam
  batasnya. Coverage luas, kalibrasi volume independen, adjustment/aksi historis
  dan hak penggunaan yang lebih luas belum terbukti. Sampel/spesifikasi produksi
  serta entitlement yang sesuai deployment diperlukan untuk evaluasi berizin.
- **DATA-02:** registry, fallback, provenance dan larangan fallback jaringan dari
  local eksplisit sudah diuji. Local Data Bridge mengiklankan IDX tetapi belum
  mendeklarasikan kontrak IDX lengkap; normalizer generiknya dapat mengisi volume
  hilang dengan nol. Tool riset menolak metadata tidak memadai. Dukungan local
  penuh membutuhkan kontrak ekspor nyata dan regresi pada seam itu; sesi ini
  tidak membuat schema adapter baru atau menganggap local sebagai sumber diterima.
- **DATA-03:** guard kualitas dan fixture sintetis sudah luas; sesi ini menutup
  kehilangan bar struktural pada normalisasi yfinance dan cache-nya. Fixture
  dapat membuktikan penolakan/fallback, bukan bahwa gap harga berarti suspensi,
  delisting atau aksi korporasi. Rekonsiliasi kejadian nyata tetap memerlukan
  bukti bertanggal dan hak penggunaan. Drop bar OHLC null/non-numerik yang sudah
  ada pada adapter tidak diubah oleh subset ini; ini bukan audit seluruh parsing.
- **IDX-02:** IDR, Jakarta, daily, saham dan adjustment tersedia pada Yahoo paths;
  lintas local/import/artefak serta kalender/rulebook historis belum lengkap.
  Perubahan ini tidak menetapkan aturan lot, sesi, biaya atau settlement.
- **RESEARCH-01:** pencarian Yahoo dan importer snapshot bertanggal tersedia;
  belum ada universe resmi yang diimpor atau tersambung ke konsumen. Satu ekspor
  instrumen asli bertanggal, sumber/revisi, cakupan/exclusions dan izin yang
  memadai cukup untuk mulai review subset sesuai [handoff referensi](IDX_REFERENCE.md#phase-2b-disposition-and-minimum-handoff).
  Histori listing/board harus dipertahankan terpisah dari schema snapshot existing.

Kalender membutuhkan notice BEI dan amendment lengkap untuk interval pilihan;
aturan membutuhkan teks lengkap beserta commencement/revocation dan cakupan
instrumen/papan. Provider membutuhkan data dictionary, sampel OHLCV/kejadian
yang boleh divalidasi serta izin storage/retensi/proses/display yang relevan;
[minimum handoff provider](IDX_PROVIDER_RESEARCH.md#minimum-technical-handoff)
tetap berlaku. Tidak ada input tersebut yang diganti dengan data buatan.
Index Alpha tetap ditunda; tidak mengulang katalog atau URL yang sudah 403.

### Sumber primer dan verifikasi

Observasi **2026-11-04 WIB** pada [dokumentasi resmi yfinance.download](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html):
`end` eksklusif dan `auto_adjust` menyesuaikan OHLC; `keepna` dan `repair`
merupakan opsi terpisah. Ini dokumentasi API saat observasi, tanpa tanggal
efektif aturan BEI. Pemanggilan lokal `_download_history` tetap menetapkan
`auto_adjust=True`; kontrak tanggal akhir adapter tidak diubah. Dokumentasi ini
tidak membuktikan unit/akurasi/kelengkapan data IDX atau entitlement. Tidak ada
fakta aturan BEI baru yang diterapkan dan tidak ada probe harga jaringan.

Runtime `.venv/idx312/Scripts/python.exe` memakai runner temporary
`%TEMP%\idx-data-validation-f8824aff\run_tests.py`:
cwd/home/appdata/localappdata/temp/runtime di luar checkout, environment minimum
tanpa kredensial warisan, dotenv dinonaktifkan sebelum import pytest, dan cache
default nonaktif. Tes cache menyalakan cache hanya pada `tmp_path`. Pytest
conftest mengisolasi home lagi sebelum collection. Tidak ada server eksternal
atau akun yang diakses. Perintah dari root (runner menerima argumen pytest):

```powershell
$qa = '%TEMP%\idx-data-validation-f8824aff\run_tests.py'
.venv/idx312/Scripts/python.exe $qa "$PWD/agent/tests/test_idx_yfinance_quality.py" -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/backtest/loaders/yfinance_loader.py agent/tests/test_idx_yfinance_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_yfinance_quality.py
git diff --check
```

Awal: **9 failed, 2 passed**; delapan failure membuktikan cacat, satu lainnya
adalah assertion hint frekuensi pandas yang memang tidak disimpan Parquet.
Assertion roundtrip diperbaiki untuk memeriksa tanggal/nilai/dtype/attrs tanpa
hint frekuensi. Akhir **13 passed** termasuk dua kontrol tambahan cache AAPL
lama dan HTTP in-process. HTTP 200/status `unavailable`, item tanpa bars dengan
alasan `no_data_or_source_failure` dan upaya yfinance `fetch_failed`; backtest false.

Regresi gabungan **785 passed, 6 warnings, 23,21 detik** dengan runner/flags yang
sama: `test_idx_yfinance_quality`, `test_idx_foundation`, `test_idx_reference`,
`test_idx_research`, `test_idx_research_quality`, `test_idx_research_provenance`,
`test_idx_research_diagnostics`, `test_idx_symbol_search`, `test_yahoo_loader`,
`test_market_data`, `test_market_data_serving_source`, `test_market_identity_parity`,
`test_market_detection`, `test_registry`, `test_composite_currency_guard`, dan
seluruh 9 file `test_yfinance*.py` pada `agent/tests/`. Log serta baseline hash
berada di directory temporary yang sama. Ruff lint dan format tes lulus.
Warnings: deprecation anyio/Starlette serta overflow/invalid arithmetic fixture
ekstrem existing. Frontend tidak disentuh; test/build/frontend browser, backend
dan safety penuh, CLI/MCP eksternal, provider nyata serta deployment tidak diulang.
Semua task penerimaan luas tetap terbuka; tidak ada staging atau commit.
Hash SHA-256 index Git awal/akhir sama:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Perbandingan hash baseline menunjukkan hanya enam file existing yang berubah
pada sesi ini (loader, dua README, dokumen ini, status dan TODO), ditambah satu
file tes baru. Perubahan sebelumnya pada file lain tetap utuh.

Handoff **2026-11-03, Asia/Jakarta**. Pengguna memilih melanjutkan MVP riset
pribadi dengan jalur existing; integrasi Index Alpha ditunda. Ini bukan penutupan
Fase 2B atau penerimaan provider untuk deployment umum.

## Penerimaan MVP pribadi — 2026-11-04

**Diterima secara teknis untuk riset pribadi lokal dalam scope berikut.**
Keputusan ini memakai implementasi working tree saat ini dan bukti 3–4 November
2026 WIB; bukan baseline regresi sebelum perubahan IDX, penerimaan seluruh IDX,
jaminan ketersediaan Yahoo, atau verifikasi deployment.

Pengguna sasaran adalah pemilik watchlist manual maksimum delapan saham reguler
empat huruf `.JK`, data harian IDR, melalui UI dan CLI tanpa akun LLM.
Yahoo HTTP menjadi pilihan default; yfinance adalah transport alternatif vendor
yang sama. Tidak ada paket berbayar atau provider baru. Penggunaan mengikuti
batas personal yang telah dicatat di bagian [batas](#batas-yang-tetap-berlaku).
Benchmark MVP adalah skenario fungsi di bawah, bukan return strategi atau
rekonsiliasi terhadap bursa. Bentuk ticker dan deklarasi Yahoo tidak membuktikan
status papan reguler, listing atau suspensi terkini; pengguna memilih instrumen
yang sesuai. Universe resmi lengkap bukan prasyarat watchlist terbatas ini.

Kriteria penerimaan yang dapat diulang:

1. **Input dan pemilihan:** UI menerima 1–8 simbol `.JK` unik; menolak ticker
   tanpa venue, duplikasi dan bentuk instrumen di luar scope sebelum akuisisi.
   Pencarian menampilkan kandidat IDX/IDR dan membutuhkan pemilihan eksplisit.
   Hasil kosong tetap terlihat; pengguna dapat memasukkan `.JK` secara manual.
2. **Akuisisi nyata:** CLI berhasil pada delapan ticker terbaru dan dua kelompok
   historis 200/500 bar di bawah; yfinance benar-benar menjadi sumber aktual pada
   tiga ticker di dua periode. Setiap hasil wajib melewati gate harian IDR,
   tanggal sesi Jakarta, OHLCV dan provenance existing. Batas bar bukan janji
   kelengkapan sesi. Nol dan data hilang tidak diganti angka buatan.
3. **Alur UI:** fetch manual → pilih simbol → chart/indikator → buka OHLCV
   memakai satu hasil akuisisi; sumber, adjustment, retrieval/as-of, usia data
   dan jumlah observasi ditampilkan. Desktop/mobile id berfungsi tanpa overflow.
   Sebelas locale tetap melewati tes frontend; tidak semuanya diuji browser nyata.
4. **Kegagalan:** hasil parsial mempertahankan simbol sehat; akuisisi kosong,
   kegagalan sumber, metadata invalid dan indikator tidak tersedia tetap eksplisit.
   CLI keluar 0 hanya untuk semua simbol tersedia, 2 untuk input/hasil gagal atau
   parsial. Kasus kegagalan diperiksa dengan fixture sintetis existing, bukan
   dengan sengaja membebani atau memutus provider publik.
5. **Batas riset:** endpoint memakai dependency auth existing; tool/CLI tidak
   mengaktifkan backtest, paper atau live. Regresi batas auth, pasar lain,
   currency, penolakan backtest dan safety lulus. Tidak ada order broker.

### Bukti provider dan alur pengguna

Lima subprocess CLI terisolasi pada **2026-11-03 sekitar 19:21–19:22 WIB**
menghasilkan **22 hasil simbol/periode, semuanya status ok dan exit 0**:

- Yahoo, lookback 60, end `2026-11-02`: BBCA, BBRI, TLKM, ASII, ANTM, ICBP,
  UNVR dan GOTO (semua `.JK`); masing-masing 60 bar `2026-08-07`–`2026-11-02`.
  Rentang akuisisi `2026-07-05`–`2026-11-02`.
- Yahoo, lookback 200, end `2025-12-31`: BBCA/TLKM/ANTM/GOTO; masing-masing
  200 bar `2025-02-26`–`2025-12-30`. Akuisisi `2024-11-26`–`2025-12-31`.
- Yahoo, lookback 500, end `2024-12-31`: BBRI/ASII/ICBP/UNVR; masing-masing
  500 bar `2022-11-29`–`2024-12-30`. Akuisisi `2022-04-06`–`2024-12-31`.
  UNVR mempunyai satu bar volume nol yang tetap diterima sebagai observasi nol.
- yfinance, BBCA/TLKM/ANTM, lookback 60/end `2026-11-02` dan
  200/end `2025-12-31`: masing-masing 60/200 bar dengan tanggal seperti kelompok
  Yahoo di atas. Override existing `MARKET_DATA_ORDER_ID_EQUITY=yfinance,yahoo,local`
  dipasang hanya pada subprocess; provenance memastikan sumber **yfinance**,
  bukan keberhasilan fallback Yahoo yang salah dilabeli sebagai uji yfinance.

Semua hasil menyatakan IDR, Asia/Jakarta, 1D, unit provider `shares`, tanpa
konversi mata uang. Adjustment Yahoo `unknown`, yfinance `split_dividend`;
delay tetap `unknown`, freshness provider `not_evaluated`. Ini bukti bahwa
adapter menerima dan menyajikan data, bukan kalibrasi harga/volume independen,
kalender resmi, kelengkapan aksi korporasi atau hak redistribusi.

Browser Chromium headless pada **2026-11-04 sekitar 01:13 WIB** menggunakan
build produksi, route `register_idx_research_routes` dan adapter/provider nyata
di server QA loopback sementara. Desktop 1280: delapan ticker di atas × 60 bar,
HTTP 200/status ok; pilih GOTO dan buka 60 bar OHLCV tanpa akuisisi tambahan.
Mobile 390: UNVR/end `2024-12-31`, HTTP 200/status ok, tabel 500 bar.
Masing-masing satu request riset; page error kosong dan scrollWidth sama dengan
innerWidth (1280/390). Input bare ticker/duplikat menonaktifkan fetch.
Harness mengizinkan auth khusus QA dan tidak menjalankan lifespan API penuh;
auth produksi diperiksa oleh regresi, bukan oleh browser ini. Server ditutup.

Pencarian Yahoo mempunyai keterbatasan yang benar-benar terlihat: `ANTM` pernah
memberi kandidat IDX kosong dengan `sources.yahoo=ok`; `ANTM.JK` pernah memberi
satu kandidat yang berhasil ditambahkan lewat UI, dan panggilan lain kosong.
Recheck adapter mentah `ANTM` mengembalikan ANTM.JK/JKT/EQUITY. Respons awal
mentah tidak direkam, sehingga penyebab variasi belum dapat dipastikan dan
tidak dinyatakan sebagai bug filter aplikasi. Pesan kosong dan input manual
memungkinkan riset berlanjut; pencarian bukan bukti instrumen tidak terdaftar.
Tidak ada bug aplikasi yang berhasil direproduksi untuk diperbaiki sesi ini.

Home, runtime, appdata/cache dan cwd probe berada di temporary
`idx-mvp-acceptance-d5i_qyxk`, di luar repository; subprocess memakai environment
minimum tanpa kredensial warisan dan cache data aplikasi nonaktif. yfinance
dapat menyimpan cookie publiknya sendiri di appdata sementara. Tidak membaca
konfigurasi rahasia. JSON pasar, log, script QA dan screenshot tetap lokal di
temporary tersebut; tidak ditambahkan sebagai fixture distribusi.

### Verifikasi dan keputusan berhenti

Peta implementasi yang dicocokkan sebelum pembaruan dokumen: batas input dan
akuisisi pada `src/tools/idx_research_tool.py:59,89`, gate kualitas `:151`,
observasi/indikator `:229,240`, usia `:269`, CLI/exit `:302`; delivery HTTP pada
`src/api/idx_research_routes.py:24`; UI pada
`frontend/src/pages/IDXResearch.tsx:110,139,167,265` (path frontend relatif root).
Tidak ada perubahan runtime/dependency sesi ini. Invariant: perilaku pasar lain,
penolakan execution IDX, pekerjaan lama dan index Git dipertahankan.

Dari root dengan `.venv/idx312/Scripts/python.exe -m pytest`, flags
`-q --allow-hosts=127.0.0.1,::1`:

- **719 passed**, 15 modul: `test_idx_research`, `test_idx_research_diagnostics`,
  `test_idx_research_provenance`, `test_idx_research_quality`, `test_idx_symbol_search`,
  `test_idx_foundation`, `test_yahoo_loader`, `test_yfinance_declared_currency`,
  `test_market_data`, `test_market_data_serving_source`, `test_market_identity_parity`,
  `test_market_detection`, `test_registry`, `test_composite_currency_guard`,
  `test_mcp_new_tools` (semuanya `agent/tests/<nama>.py`).
- **121 passed**, empat modul safety: `test_sdk_order_gate`,
  `test_mandate_enforcement`, `test_killswitch_blocks_orders`, `test_readonly_default`.
- Dari `frontend/`: `npm run test:run -- --maxWorkers=2` → **1231 passed,
  95 file**, 173,76 detik; `npm run build` → lulus. Warning configLoader/chunk
  existing, deprecation anyio/Starlette, serta overflow numerik yang memang
  dipicu fixture penolakan tercatat; tidak ada dependency yang diubah.

Percobaan browser awal gagal pada harness: lokasi binary browser terisolasi
belum diarahkan, selector `summary` ambigu, lalu `theme-boot.js` tersaji sebagai
HTML. Ketiganya diperbaiki di script temporary; hasil browser akhir di atas
berasal dari run ulang yang lulus. Ekspektasi kandidat pencarian yang selalu
ada juga dilepas agar keadaan provider kosong diuji sebagaimana adanya.

MVP berhenti pada penerimaan terbatas ini, tanpa mencari tambahan slice UI
atau hardening tak berbatas. **DATA-01/02/03, IDX-02, UI-01 penuh dan RESEARCH-01
tetap terbuka** sesuai scope task asal. Universe resmi/historis, fundamental,
screener, laporan analis, penjadwalan, provider berbayar, install bersih/packaging
dan deployment adalah perluasan. RULE-01 serta BT-01/02/03 tetap tahap terpisah;
backtest IDX nonaktif, paper/live tidak tersedia. Backend penuh, MCP eksternal,
startup/auth aplikasi penuh dan deployment tidak dijalankan. Tidak ada staging,
commit, reset, akun, pembelian atau order broker.

Verifikasi dokumen: 125 tautan lokal dan 75 anchor pada tiga dokumen yang
diubah lulus, UTF-8 strict/whitespace dan `git diff --check` lulus. Perbandingan
hash terhadap awal sesi memastikan hanya `PROJECT_STATUS.md`, `TODO.md` dan
file ini berubah; file kerja lain serta hash index Git tetap sama. Tidak ada
file nonignored baru/hilang. Dokumen ini tidak menambahkan permukaan runtime.

## Startup aplikasi dan auth nyata — 2026-11-04

**Lulus untuk jalur startup resmi dan riset IDX lokal**, melengkapi batas
startup/auth yang belum diperiksa pada penerimaan MVP-A01 di atas. Tidak ada
override route, auth dependency, lifespan atau provider pada pemeriksaan ini.
Ini bukan verifikasi chat/agent LLM, instalasi bersih atau deployment.

Working tree dipetakan dan di-hash sebelum pekerjaan. Kode saat ini beserta
build frontend disalin ke `idx-full-startup-g2_j12es/project` di temporary;
hanya source nonignored yang dipilih, tanpa `.env`, kredensial atau direktori
runtime lama. Ini penting karena startup asli menjalankan migrasi state lama
dan pencarian dotenv (`src/config/migrate.py:122`, `src/providers/llm.py:1310`).
Interpreter tetap `.venv/idx312/Scripts/python.exe` milik proyek. Setiap proses
memakai home/appdata/runtime sementara terpisah dan environment minimum;
`PYTHONPATH` menunjuk `project/agent` hasil salinan, cache data nonaktif,
scheduler dan channel auto-start nonaktif melalui konfigurasi existing.

Perintah startup sesungguhnya dari direktori salinan:

```powershell
<interpreter-proyek> -m cli serve --host 127.0.0.1 --port <port-sementara>
```

Ini jalur console entry `vibe-trading serve`, melalui `cli/_legacy.py:256` →
`api_server.serve_main` → `src/api/server_cli.py:14`. Assembler/lifespan asli,
preflight, static mount `SPAStaticFiles`, middleware Host/CORS/security, serta
dependency `require_auth` dipakai. Dua proses pada **sekitar 02:56 WIB**:

- **Loopback tanpa key:** startup 27,84 detik; `/health` 200. Chromium desktop
  id 1280 membuka deep link `/research/idx` dari static mount produksi asli.
- **Key sintetis khusus QA:** startup 10,39 detik; `/health` 200. API riset tanpa
  key/salah key dan `/openapi.json` tanpa key ditolak **401**. Nilai sintetis
  yang sama dipasang melalui storage auth frontend existing; Chromium mobile
  id 390 berhasil mengakses riset. Tidak ada token nyata dibaca atau ditulis.
- Pada kedua mode, POST cross-site dan request dengan Host tak tepercaya
  ditolak **403** sebelum akuisisi. Probe penolakan tidak memerlukan broker.
- Browser kedua mode mengambil BBCA.JK/BBRI.JK/TLKM.JK, lookback 60 dan end
  `2026-11-02`: HTTP 200/status ok, sumber aktual **yahoo**, IDR, masing-masing
  60 bar `2026-08-07`–`2026-11-02`. Memilih TLKM dan membuka 60 bar OHLCV
  tidak menambah akuisisi: **satu POST riset per skenario**. Chart tampil,
  page error kosong; scrollWidth == innerWidth masing-masing 1280/390.
- `/system/shutdown` asli memberi 200; proses selesai dan kedua port diperiksa
  sudah tertutup. Pada Windows endpoint memakai penghentian proses; hasil ini
  tidak membuktikan seluruh finalizer lifespan mendapat graceful shutdown.

**Mode degradasi yang tetap terlihat:** `/ready` memberi **503** pada kedua
mode karena model/akun LLM tidak dikonfigurasi. Preflight menampilkan
`Critical check failed - agent cannot start without a working LLM provider`,
tetapi startup HTTP selesai dan riset IDX langsung tetap berfungsi. Ini tidak
menyatakan chat/agent LLM siap. Preflight OKX gagal dengan
`SSLCertVerificationError: unable to get local issuer certificate`; yfinance
dilaporkan reachable. SSL tidak dinonaktifkan dan konfigurasi trust mesin tidak
diubah; kegagalan OKX di luar jalur Yahoo riset ini.

Percobaan awal menjalankan `python agent/api_server.py` secara langsung
menghasilkan `RuntimeError: register_runs_routes: api_server module not in
sys.modules; ensure api_server is imported before calling this function`.
Kode dieksekusi sebagai `__main__`, sementara registrasi mencari modul
`api_server`/`agent.api_server` (`src/api/runs_routes.py:853`). Jalur resmi CLI
dan jalur desktop yang mengimpor modul berfungsi. Saat pemeriksaan awal jalur langsung belum
diperbaiki; **DEV-START-01** saat itu dicatat sebagai pekerjaan opsional terpisah,
bukan penghalang MVP melalui command yang didokumentasikan.

### Regresi startup dan isolasi tes

Run awal enam modul menghasilkan **119 passed, 1 failed**:
`test_get_run_code_rejects_dot_run_id` menerima `200`, expected `{400, 404}`.
Urutan tes mount frontend → tes keamanan tersebut menghasilkan **1 passed,
1 failed**; tes keamanan sendiri **1 passed**. Penyebabnya helper startup
memasang root static mount ke `api_server.app` global dan meninggalkannya
untuk tes berikutnya; URL `/runs/../code` dinormalisasi menjadi `/code`, lalu
menerima HTML SPA. Bukan bukti pembacaan source di luar direktori run.

Perbaikan hanya di `agent/tests/test_serve_bind.py`: fixture autouse memberikan
salinan daftar route per tes dan monkeypatch memulihkan daftar awal. Docstring
helper juga dikoreksi: static mount memang berjalan sebelum uvicorn stub.
Assertion keamanan tidak diubah. Tidak ada kode runtime/provider/frontend,
rumus, konfigurasi pengguna atau dependency yang berubah.

Perintah dari root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_serve_bind.py agent/tests/test_preflight.py agent/tests/test_scheduling_lifespan_owner.py agent/tests/test_spa_deep_link.py agent/tests/test_security_auth_api.py agent/tests/test_auth_precedence.py -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/tests/test_serve_bind.py
```

Hasil akhir **120 passed**, 8,86 detik, Ruff lulus; warning deprecation
anyio/Starlette tetap ada. Backend penuh, safety order penuh, frontend suite/build
tidak diulang karena hanya isolasi tes dan dokumen berubah. Bukti frontend,
safety dan provider lebih luas pada MVP-A01 tetap hasil sesi sebelumnya,
bukan baseline pra-IDX. JSON pasar, screenshot, salinan source dan log tetap
di temporary, bukan fixture distribusi. Tidak ada staging, commit, deployment,
akun, pembelian, order atau akses konfigurasi rahasia pengguna.

## Perilaku yang tersedia

- Halaman `/research/idx`, menu **Riset IDX**, memakai daftar awal BBCA.JK,
  BBRI.JK dan TLKM.JK sebagai pilihan pribadi, bukan master instrumen resmi.
- Maksimum delapan simbol saham empat huruf `.JK` yang unik; input tanpa venue,
  waran, pasar lain dan duplikasi ditolak sebelum pengambilan data.
- Fetch manual, interval 1D, hingga 60/200/500 observasi di UI. Tanggal akhir
  opsional memakai hari Jakarta. Rentang akuisisi dua hari kalender per bar
  merupakan anggaran pengambilan, bukan jaminan jumlah sesi atau kelengkapan.
- Satu pengambilan melalui `src.market_data.fetch_market_data` memasok chart
  penutupan, OHLCV, fingerprint dan perhitungan indikator existing. Rumus RSI,
  MACD, Bollinger, SMA/EMA dan statistik volume tidak disalin ke UI.
- Watchlist dan pengaturan tersimpan sebagai draft tab menggunakan hook existing.
  Hasil berada di memori halaman; tidak ada polling atau refresh otomatis.
  Kebijakan cache loader existing tetap berlaku bila dikonfigurasi pengguna.
- Sumber aktual, adjustment, IDR, timezone sesi, unit volume, waktu pengambilan
  dan tanggal bar terakhir tampil. `unknown` tetap unknown; tidak diberi label
  real-time. Nilai volume/indikator yang tidak tersedia tetap null.
- Simbol gagal tetap ditampilkan; respons membedakan hasil lengkap, parsial dan
  tidak tersedia. HTTP memakai auth dependency existing dan worker thread.
  Untuk simbol tanpa data, container/entry diagnostik akuisisi non-object menjadi
  null dengan warning tersanitasi; metadata absent/null tetap unknown.
  Object diagnostik yang gagal serialisasi JSON juga menjadi null, termasuk
  angka nonfinite, nilai non-JSON, siklus dan nesting berlebihan.
  Perubahan input membatalkan konsumsi respons UI lama; ini tidak menjamin
  pembatalan worker/provider request yang sudah berjalan di server.
- Object provenance yang gagal serialisasi JSON strict menjadi null dengan
  warning tersanitasi sebelum analisis. Simbol berdata ditolak melalui gate
  metadata existing; simbol kosong tetap memakai alasan kegagalan akuisisi.
  Provenance valid dan hasil simbol sehat tetap dipertahankan.
- Frame observasi wajib memiliki kolom datar dengan tepat satu field untuk setiap
  open/high/low/close/volume. Kolom bertingkat ditolak pada tahap harga; duplikat
  harga/volume ditolak pada tahap masing-masing tanpa memilih atau meratakan kolom.
  Kolom tambahan yang tidak dipakai tidak mengubah penerimaan observasi.
- Deklarasi provenance `symbol`, `market` dan `exchange` yang hadir wajib cocok
  persis dengan instrumen permintaan. Field absen tetap kompatibel; deklarasi
  null/invalid/bertentangan ditolak melalui `instrument_identity`, tanpa perbaikan
  identitas atau peminjaman data simbol lain.
- JSON API/agent/MCP/CLI menyertakan diagnostik `recency` per simbol yang tersedia:
  usia bar terakhir terhadap tanggal akhir permintaan, dengan peringatan setelah
  14 hari kalender. Data valid tetap tersedia. Watchlist kini menampilkan warning,
  usia, bar terakhir dan tanggal acuan; field yang hilang ditandai belum tersedia.
- Panel simbol sehat juga menampilkan cakupan volume dari `volume_coverage`:
  jumlah bar aktual, volume tersedia, hilang dan nol. Nol termasuk tersedia;
  hitungan hilang/invalid ditandai tidak tersedia tanpa menghitung ulang chart.
- Simbol sehat dengan `fallback_used: true` menampilkan upaya gagal sebelumnya
  dari `provenance.attempts`, sesuai urutan backend. Nilai asing/hilang ditandai
  tidak tersedia; Yahoo/yfinance tetap dua transport satu vendor. Panel ini
  tidak menambahkan percobaan sumber, request, atau verifikasi independen.
- Disclosure **Observasi OHLCV harian** menampilkan bar respons yang sama dengan
  chart: tanggal sesi, pembukaan/tertinggi/terendah/penutupan dalam IDR dan volume
  saham. Volume nol tetap nol, null ditandai tidak tersedia. Tabel dapat dibuka
  lewat keyboard dan digulir di dalam panel, termasuk pada mobile.
- Panel simbol sehat menampilkan fingerprint SHA-256 backend untuk interval, tanggal,
  close dan volume analisis. Metadata hilang/malformed ditandai tidak tersedia;
  fingerprint bukan hash seluruh OHLCV atau bukti autentisitas provider.
- Panel indikator menampilkan sinyal/histogram MACD, Bollinger atas/tengah/bawah
  20 bar dalam IDR dan rata-rata volume 20 bar dalam saham dari respons existing.
  Format locale mempertahankan presisi indikator; nol/negatif tetap nilai,
  sedangkan komponen atau struktur yang null/hilang tetap tidak tersedia.

Tool agent dan MCP bernama `idx_research`, menggunakan schema kelas yang sama.
MCP memakainya melalui mirror existing dan tool tetap read-only. Endpoint UI
adalah `POST /api/research/idx`, body `codes`, `lookback`, `end_date` opsional.
Tidak ada opsi order atau pengaktifan engine pada permukaan ini.

## Menjalankan tanpa akun LLM

Dari root repository, melalui interpreter proyek:

```powershell
$env:PYTHONPATH = "agent"
.venv/idx312/Scripts/python.exe -m src.tools.idx_research_tool BBCA.JK BBRI.JK TLKM.JK --lookback 60 --end-date 2026-10-30
```

Perintah mengakses sumber data sesuai routing/config existing; keluar 0 hanya
untuk seluruh simbol tersedia dan 2 untuk input gagal/hasil parsial/tidak tersedia.
JSON mengandung bar pasar: jangan commit output atau memakai data sebagai fixture
distribusi tanpa izin. Jangan membaca token untuk menjalankan fitur ini.

## Batas yang tetap berlaku

Yahoo dan yfinance adalah dua transport satu vendor. Routing auto existing
Yahoo → yfinance → local beserta konfigurasi urutan sumber dipertahankan.
Unit/provider-reported metadata belum merupakan validasi independen data bursa.
Sumber yang tidak menyatakan IDR atau bar yang tidak memenuhi kontrak ditolak.
Tidak ada master instrumen lengkap, kalender resmi, histori suspensi/delisting,
aksi korporasi point-in-time atau model fee/rulebook baru.

Gunakan untuk riset pribadi sesuai ketentuan sumber. Dokumentasi
[yfinance](https://ranaroussi.github.io/yfinance/) menyebut tujuan riset/edukasi
dan penggunaan personal API Yahoo; hak atas data tetap mengikuti ketentuan Yahoo.
Ini bukan pemberian hak redistribusi, display publik atau pemrosesan LLM/cloud.
RULE-01, DATA-01 dan RESEARCH-01 tetap terbuka. Backtest IDX tetap ditolak oleh
runner/composite; paper/live IDX tidak diaktifkan.

## Bukti verifikasi sesi ini

- Regresi 13 modul data/IDX/indikator: **499 passed**, termasuk 18 tes awal fitur.
  Setelah tambahan batas tanggal dan exposure MCP, run fitur + MCP:
  **50 passed** (19 fitur, 31 MCP). Semua tes memakai runtime sandbox proyek;
  koneksi dibatasi ke loopback. Warning anyio/pytest dan Starlette bersifat
  deprecation. Tes indikator existing `test_invalid_lookback_clamped` sempat
  mencoba jaringan eksternal yang diblokir pytest-socket; bukan probe provider.
- Frontend `npm run test:run`: **92 file, 850 passed**. Setelah perbaikan encoding
  teks dan landmark halaman, tes page/navigation/i18n: **54 passed**.
- `npm run build` akhir berhasil (Vite 6,73 detik), dengan warning chunk >500 kB
  existing. Ruff pada tool/helper/route/tes baru lulus. `git diff --check` lulus.
- Browser lokal dengan adapter Yahoo sintetis: chart/indikator, hasil parsial,
  sumber/as-of dan locale Indonesia tampil; viewport desktop 1280 dan mobile
  390 diperiksa. Pada mobile `innerWidth == scrollWidth == 390`. Angka di
  pemeriksaan browser adalah sintetis, bukan kutipan harga aktual.
- **Probe jaringan terpisah melalui CLI baru:** subprocess dengan environment
  minimum tanpa kredensial warisan, home/runtime sementara, cwd di luar repo dan
  cache nonaktif. BBCA.JK, BBRI.JK, TLKM.JK semuanya `status=ok`, masing-masing
  **60 bar**, 2026-08-06 sampai 2026-10-30; rentang diminta 2026-07-02 sampai
  2026-10-30. Sumber aktual `yahoo`, IDR, unit provider `shares`, adjustment
  `unknown`. Retrieval 2026-11-03 sekitar 04:57 WIB. Ringkasan/hash dataset ada
  di direktori temporary `idx-personal-probe-wesmuu08`, bukan raw rows di repo.
  Ini membuktikan eksekusi CLI/data acquisition, bukan kalender, akurasi harga
  independen, corporate actions atau entitlement umum.
- Full backend, safety suite dan deployment tidak diulang. Tidak ada akun,
  token, order broker, pembelian, staging atau commit. Server QA loopback
  sementara memakai data sintetis dan bukan deployment aplikasi.

Perintah regresi fitur/MCP:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/src/tools/technical_indicator_tool.py agent/src/api/idx_research_routes.py agent/tests/test_idx_research.py
```

## Titik lanjut

Slice DATA-03 bentuk provenance kini menolak container/entry non-object tanpa
menggugurkan tool, HTTP atau CLI; kontrak dan bukti ada di bagian akhir dokumen.
DATA-03 penuh tetap terbuka.

Slice DATA-03 penolakan nilai kompleks kini tersedia; lihat
[kontrak dan bukti](#data-03--penolakan-nilai-kompleks). DATA-03 penuh tetap terbuka.

Slice UI-01 kelengkapan panel indikator kini tersedia; lihat
[kontrak dan bukti](#ui-01--kelengkapan-panel-indikator). UI-01 penuh tetap terbuka.

Slice DATA-03 cakupan volume observasi kini tersedia di JSON tool bersama;
lihat [kontrak dan bukti](#data-03--cakupan-volume-observasi). UI kini menampilkan
ringkasan tersebut; lihat [cakupan volume](#ui-01--cakupan-volume). DATA-03 penuh tetap terbuka.

Slice DATA-03 batas numerik indikator kini tersedia; lihat
[kontrak dan bukti](#data-03--batas-numerik-indikator). DATA-03 penuh tetap terbuka.

Slice DATA-03 tipe numerik observasi kini tersedia; lihat
[kontrak dan bukti](#data-03--tipe-numerik-observasi). DATA-03 penuh tetap terbuka.

Slice UI-01 cakupan observasi kini tersedia; lihat
[kontrak dan bukti](#ui-01--cakupan-observasi). Slice UI-01 penuh serta DATA-03,
RULE-01, DATA-01 dan RESEARCH-01 tetap terbuka.

Slice DATA-03 deklarasi adjustment dan fixture aksi sintetis kini tersedia;
lihat [bukti dan batasnya](#data-03--deklarasi-adjustment-dan-fixture-aksi-sintetis).
Kalibrasi aksi korporasi nyata tetap membutuhkan data pembanding/event berizin.

Periksa working tree sebelum mengedit: fondasi IDX dan perubahan sebelumnya belum
di-commit. Jangan reset/overwrite. Pemilik backlog tetap [TODO.md](../TODO.md).
MVP-R01 adalah slice watchlist manual yang sudah diuji; MVP-R02 kini menambahkan
pencarian simbol pada watchlist melalui seam `search_symbol` existing, tanpa
mengklaim universe resmi. MVP-I18N melengkapi terjemahan teks fitur dan navigasi
pada ar/de/es/fa/ja/ko/pt-BR/zh-CN, termasuk pencarian simbol; en/id/tr dipertahankan.
Tidak perlu mengulang riset
Index Alpha, katalog lama atau PDF 403 untuk mengerjakan slice riset pribadi.


## MVP-R02 — pencarian watchlist pribadi

Halaman memiliki form pencarian manual nama/ticker. Pencarian tidak menambah
simbol atau mengambil harga secara otomatis; pengguna memilih tombol Tambah.
Hanya kandidat saham reguler empat huruf `.JK`, exchange Yahoo JKT/IDX, yang
tersedia untuk dipilih. Venue IDX dan currency identitas IDR diturunkan melalui
pemilik klasifikasi existing; ini bukan verifikasi quote currency observasi
harga (loader tetap memvalidasi IDR secara terpisah). Bare ticker tetap memiliki
arti pasar existing di luar pemilihan kandidat ini. Maksimum delapan simbol unik;
watchlist yang invalid perlu diperbaiki sebelum menambah kandidat.

Tool `search_symbol` mendapat opsi `market="idx"` (default tetap `all`). Scope
tersebut hanya memakai transport pencarian Yahoo existing, tanpa membaca profil
connector akun, memanggil Eastmoney/SEC, atau memakai fallback vendor lain.
API halaman `GET /api/research/idx/symbols?query=...` memakai auth dependency dan
worker thread existing; kueri dibatasi 120 karakter dan maksimum 20 kandidat.
Hasil kosong dibedakan dari status kegagalan/unsupported query Yahoo. Perubahan
kueri dan unmount membatalkan konsumsi respons lama, termasuk saat provider
mengabaikan abort. Worker yang sudah berjalan di server belum tentu berhenti.

Terjemahan fitur kini tersedia di seluruh locale existing melalui MVP-I18N,
dengan key parity tetap terjaga. Kandidat Yahoo bukan master resmi, universe
historis, ataupun bukti tradability. Index Alpha tetap ditunda.

Verifikasi MVP-R02 (fixture sintetis, koneksi hanya loopback):

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_symbol_search.py agent/tests/test_symbol_search_tool.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_market_identity_parity.py -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/symbol_search_tool.py agent/src/api/idx_research_routes.py agent/mcp_server.py agent/tests/test_idx_symbol_search.py agent/tests/test_mcp_new_tools.py
cd frontend
npm run test:run -- src/lib/__tests__/api.test.ts src/pages/__tests__/IDXResearch.test.tsx
npm run test:run
npm run build
```

Backend **234 passed**; frontend penuh **858 passed** (92 file), termasuk
halaman/klien **23 passed**; build dan Ruff lulus. Wrapper MCP `search_symbol`
meneruskan scope opsional dan mempertahankan argumen default existing.
Tes endpoint menjalankan tool/normalisasi existing dengan batas Yahoo dipalsukan;
tes halaman merender komponen dan menguji pemilihan serta respons tertunda.
Run awal frontend menemukan ekspektasi tes header yang belum mencantumkan
Content-Type existing; ekspektasi diperbaiki tanpa mengubah helper HTTP.
Warning existing: deprecation pytest/Starlette, query tes umum yang mencoba
koneksi eksternal diblokir pytest-socket, konfigurasi Vite native dan ukuran chunk.
Probe Yahoo nyata, browser desktop/mobile, full backend/safety suite dan deployment
tidak diulang pada MVP-R02. Tidak ada token, akun, order, staging atau commit.

## MVP-I18N — terjemahan Riset IDX

Sebanyak **312 teks** (39 per locale) diterjemahkan pada ar/de/es/fa/ja/ko/pt-BR/
zh-CN: seluruh blok `idxResearch`, termasuk pencarian simbol, serta deskripsi,
petunjuk dan judul navigasi. Locale en/id/tr dipertahankan. Tidak ada perubahan
alur provider, akun, aturan pasar, indikator atau eksekusi.

Verifikasi dari `frontend/`:

```powershell
npm run test:run -- src/i18n/__tests__/i18n.test.ts src/pages/__tests__/IDXResearch.test.tsx src/components/layout/__tests__/Navigation.test.tsx
npm run test:run
npm run build
```

Tes terkait **77 passed**: key/interpolation parity, pencegahan teks Inggris
tersalin, navigasi dan halaman IDX. Delapan kasus merender halaman dengan locale
yang dipilih dan menjalankan pencarian kosong memakai provider sintetis. Kasus
baru awalnya gagal dengan `Unable to find an accessible element with the role
"heading"` karena assertion mendahului lazy loading; tes diperbaiki untuk menunggu
judul terjemahan tampil, tanpa mengubah runtime i18n. Build lulus dengan warning
ukuran chunk existing. Nilai JSON di luar fitur IDX pada delapan locale cocok
dengan HEAD, dan pemeriksaan marker mojibake lulus. Run akhir frontend penuh
**874 passed** (92 file), `git diff --check` lulus. Warning Vite configLoader
existing tetap muncul pada Vitest; tidak ada kegagalan tersisa.

Backend/Ruff, probe Yahoo nyata, browser desktop/mobile dan deployment tidak
diulang untuk perubahan terjemahan ini. RULE-01/DATA-01/RESEARCH-01 tetap terbuka;
backtest IDX tetap nonaktif dan Index Alpha ditunda. Tidak ada token, akun,
order broker, staging atau commit.

## DATA-03 — validasi observasi riset pribadi

Slice lokal DATA-03 memvalidasi seluruh frame yang diterima tool sebelum
`sort_index().tail(lookback)`. Harga nonpositif, OHLC tidak konsisten, harga
NaN/infinity atau volume tersedia yang negatif/infinity menolak observasi
tersebut, termasuk bar di luar tail tampilan. Metadata interval harus `1D`
dan unit volume harus `shares`; unit hilang/lot tidak ditebak atau dikonversi.
Penolakan memakai status `unavailable`, reason `invalid_data_or_metadata`
dan warning tersanitasi existing; simbol sehat tetap menghasilkan hasil parsial.
API, agent/MCP dan CLI memakai pemilik validasi yang sama.

Fixture Python sintetis di `tests/test_idx_research_quality.py` berisi 15 kasus,
tanpa bar provider nyata. Volume nol tetap nol, volume null tetap null, gap
tanggal tidak diisi atau diberi arti suspensi, dan frame akuisisi tidak dimutasi.
Adjustment `unknown`, freshness `not_evaluated` dan kalender `not_verified`
tetap dinyatakan demikian pada provenance loader. Diagnostik usia riset terpisah
tersedia pada slice berikutnya. Validasi ini hanya mencakup frame yang diterima;
tidak membuktikan kelengkapan bar yang sudah disaring provider/loader sebelumnya.
Kalibrasi split/dividen, suspensi/delisting, kalender resmi dan freshness policy
belum tersedia, sehingga DATA-03 penuh tetap terbuka.

Perintah dari root repository:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/tests/test_idx_research_quality.py
git diff --check
```

Hasil: **497 passed** (14 modul), Ruff lint/format tes dan whitespace lulus.
Sebelum perbaikan, 11 dari 12 kasus awal gagal: `assert 'ok' == 'unavailable'`
atau `assert 'ok' == 'partial'`; kontrol gap/null sudah lulus. Setelah perbaikan,
run riset/kualitas/MCP awal **64 passed**; tiga kontrol tambahan ikut run 497.
Endpoint sintetis mengembalikan HTTP 200/status partial dengan BBCA unavailable
dan BBRI ok (20 bar), tanpa mengubah kontrak HTTP. Pemeriksaan format awal
menemukan file tes baru belum terformat; Ruff format memperbaikinya.

Warning existing: deprecation anyio/pytest dan Starlette, serta percobaan
koneksi eksternal oleh `test_invalid_lookback_clamped` yang diblokir
pytest-socket. Ini bukan probe Yahoo nyata. Tidak ada perubahan frontend;
frontend/build, full backend/safety, browser, provider nyata dan deployment
tidak diulang. Index Alpha tetap ditunda, backtest IDX tetap nonaktif dan
RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Tidak ada token, akun, order,
staging atau commit.

## DATA-03 — diagnostik usia observasi

Tool bersama kini menambahkan `recency` pada simbol yang lolos validasi dan
perhitungan indikator. Kebijakan lokal `calendar_age_warning_v1` menghitung
`age_calendar_days` dari bar terakhir aktual terhadap `requested_end_date`,
bukan waktu retrieval/cache atau metadata as-of. Tanggal akhir eksplisit menjadi
acuan request historis; default tetap hari Jakarta. `last_bar_date`,
`reference_date` dan `warning_after_calendar_days` disertakan agar dapat diaudit.

Usia **lebih dari 14 hari kalender** menghasilkan `status: warning` dan log
warning tersanitasi. Usia 0–14 hari menghasilkan `within_window`, bukan klaim
fresh/real-time. Ini ambang alarm pribadi, bukan aturan BEI atau bukti missing
session, suspensi, delisting, delay maupun kelengkapan kalender. `calendar_verified`
tetap false; freshness provenance loader tetap `not_evaluated`. Ambang diagnostik
ini terpisah dari gate availability pada loader-health.

Data valid beserta indikator tetap tersedia dan exit CLI tetap 0 jika semua
simbol tersedia, meskipun ada warning usia. Field JSON ini diteruskan melalui API,
agent/MCP dan CLI; pada slice backend ini UI belum menampilkannya. Follow-up UI-01 di bawah menambahkan tampilan tersebut. Simbol unavailable tidak mendapat
usia buatan; bar sesudah end date tetap ditolak. Tidak ada pengisian gap, perubahan
angka indikator, mutasi frame/provenance, provider baru atau aktivasi backtest.

Sepuluh kasus sintetis ditambahkan ke `test_idx_research_quality.py`: batas 0/14/15
hari, request historis, retrieval/as-of yang tidak menyegarkan bar lama, clock di
pergantian tanggal Jakarta, empty/invalid/future bars, HTTP parsial dan output CLI.
Run sebelum implementasi: **7 failed, 18 passed**, kegagalan `KeyError: 'recency'`.
Sesudah implementasi: fitur/kualitas/MCP **77 passed**; Ruff lint serta format
kedua file kode/tes lulus. Perintah regresi 14 modul sama dengan slice sebelumnya.
Run akhir 14 modul: **507 passed**, termasuk **25 kasus kualitas**. Warning
existing anyio/Starlette dan koneksi tes indikator yang diblokir pytest-socket
tetap muncul. `git diff --check` lulus. Berkas yang diubah pada slice ini:
`src/tools/idx_research_tool.py`, `tests/test_idx_research_quality.py`, handoff ini,
serta `PROJECT_STATUS.md`, `TODO.md`, `README.md` dan `README_id.md` di root.
Pemeriksaan **126 tautan lokal/anchor** pada enam dokumen terkait lulus,
termasuk anchor HTML eksplisit pada README Indonesia.

Full backend/safety, frontend/build, browser, probe Yahoo nyata dan deployment
tidak diulang. DATA-03 penuh dan RULE-01/DATA-01/RESEARCH-01 tetap terbuka;
Index Alpha ditunda dan backtest IDX tetap nonaktif. Tidak ada token, akun,
order broker, staging atau commit.


## UI-01 — usia observasi pada watchlist

Slice lokal 2026-11-03 meneruskan `recency` backend ke halaman Riset IDX.
Peringatan terlihat di tombol simbol sekalipun simbol lain sedang dipilih.
Detail menampilkan usia kalender, tanggal bar terakhir, tanggal akhir permintaan,
serta status/ambang dari backend. UI tidak menghitung ulang usia memakai clock
browser atau menetapkan ambang sendiri. Status dalam rentang bukan klaim data
fresh/real-time; keterangan menyebut sesi bursa dan suspensi belum diverifikasi.

Chart, indikator dan provenance tetap tersedia ketika usia memberi warning.
Respons lama tanpa `recency` menampilkan usia belum tersedia; simbol unavailable
tidak diberi usia buatan. Sembilan key baru diterjemahkan pada seluruh 11 locale,
termasuk Indonesia, tanpa mengganti teks existing atau memperluas provider.
Tipe frontend memakai field opsional agar respons tanpa diagnostik tetap terbaca.

Bukti kode: `frontend/src/lib/idx-research.ts` memodelkan kontrak,
`frontend/src/pages/IDXResearch.tsx` menampilkan status backend, dan
`frontend/src/pages/__tests__/IDXResearch.test.tsx` menambah enam kasus rendering.
Semua path frontend pada paragraf ini relatif terhadap root repository.
Tes mencakup usia 0/14/15, tanggal historis dari backend, ambang alternatif,
chart/provenance tetap tersedia, pergantian ke unavailable, field hilang dan
locale Indonesia. Key/interpolation parity dan pencegahan teks Inggris tersalin
juga lulus melalui tes i18n existing.

Perintah dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Hasil: targeted **88 passed**, frontend penuh **880 passed** (92 file), build
lulus. Warning Vite configLoader native dan chunk >500 kB existing tetap muncul.
Tidak ada kegagalan tes tersisa. `git diff --check` lulus.

Browser memakai build produksi dan route/tool backend existing di server QA
loopback sementara dengan `VIBE_TRADING_HOME` sementara. Hanya batas akuisisi
diganti frame sintetis: BBCA 15 hari, BBRI 0 hari, TLKM unavailable. HTTP 200
menghasilkan warning, hasil parsial, chart dan metadata. Locale Indonesia,
pergantian simbol dan status dalam rentang diperiksa langsung. Desktop 1280
serta mobile 390 mempunyai `innerWidth == scrollWidth`; teks membungkus tanpa
overflow horizontal. Shell QA minimal tidak menyediakan sesi percakapan sehingga
banner kegagalan sesi tampil; ini keterbatasan harness, bukan hasil endpoint riset.
Screenshot sementara tersedia di direktori `idx-recency-ui-b4ibaolv` di temp OS.
Server QA dan tab browser sudah ditutup; port 18973 tidak lagi listening.
Pemeriksaan **128 tautan lokal/anchor** pada enam dokumen terkait lulus.

Berkas slice: tiga file frontend kode/tes di atas, 11 JSON locale,
`PROJECT_STATUS.md`, `TODO.md`, `README.md`, `README_id.md` dan handoff ini.
Backend/Ruff/full safety dan probe Yahoo nyata tidak diulang; deployment tidak
diverifikasi. UI-01 penuh dan DATA-03 penuh tetap terbuka bersama RULE-01,
DATA-01 dan RESEARCH-01. Index Alpha ditunda, backtest IDX nonaktif. Perubahan
sebelumnya dipertahankan; tidak ada token, akun, order broker, staging atau commit.

## DATA-03 — deklarasi adjustment dan fixture aksi sintetis

Slice lokal 2026-11-03 mewajibkan `provenance.adjustment` berupa teks nonkosong
sebelum menghitung indikator. Metadata hilang, null, kosong/whitespace atau
nonteks menghasilkan `unavailable`/`invalid_data_or_metadata` serta warning
tersanitasi existing. Tidak ada chart, indikator atau usia buatan pada simbol
yang ditolak; simbol sehat tetap tersedia dalam hasil parsial HTTP 200.

`unknown` eksplisit tetap diterima. Label sumber dipertahankan persis, tanpa
menebak adjustment dari nama provider. Pemeriksaan ini memvalidasi deklarasi,
bukan daftar enum atau kebenaran semantik label. Tidak ada penyesuaian harga,
konversi volume split, ekstraksi event atau klaim total return baru.

Fixture sintetis membentuk dua tingkat harga dengan sepuluh bar per tingkat
dalam lookback: 200 → 100 untuk split-like jump (SMA 150), 100 → 100 untuk
split-adjusted (SMA 100), dan 95 → 100 untuk dividend-adjusted (SMA 97,5).
Ini ilustrasi konservasi harga/indikator, bukan model event nyata atau aturan
BEI. Harga, provenance dan frame sumber tetap utuh. Satu tes tambahan melewati
routing existing dari Yahoo gagal ke download yfinance sintetis, memeriksa
`auto_adjust=True`, label `split_dividend`, sumber aktual dan failed attempt.
CLI dengan adjustment hilang menghasilkan exit 2 dan status unavailable.

Kode: `src/tools/idx_research_tool.py`; tes:
`tests/test_idx_research_quality.py` dan `tests/test_idx_research.py` (relatif
terhadap `agent/`). API, agent/MCP dan CLI tetap memakai tool bersama.

Perintah dari root repository:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py
git diff --check
```

Run awal kualitas: **6 failed, 29 passed**, berupa `assert 'ok' == 'unavailable'`
dan `KeyError: 'reason'` untuk deklarasi hilang. Setelah guard, fitur/kualitas/MCP
**88 passed**; setelah tes fallback dan CLI tambahan, regresi akhir 14 modul
**520 passed**, termasuk **37 kasus kualitas**. Ruff lint/format tiga file dan
`git diff --check` lulus. Warning existing anyio/Starlette dan koneksi eksternal
tes indikator yang diblokir pytest-socket tetap muncul; bukan probe provider.

Dokumen status/backlog, kedua README dan handoff diperbarui. Frontend/build/browser,
full backend/safety, probe Yahoo nyata dan deployment tidak diulang. Penerimaan
adjustment/corporate actions nyata, suspensi/delisting dan kalender tetap terbuka;
DATA-03 penuh, UI-01 penuh, RULE-01/DATA-01/RESEARCH-01 tidak dicentang. Index Alpha
ditunda, backtest IDX tetap nonaktif. Perubahan sebelumnya dipertahankan;
tidak ada token, akun, order broker, staging atau commit.

Pemeriksaan akhir **131 tautan lokal/anchor** pada enam dokumen terkait lulus.
Git juga melaporkan warning normalisasi LF → CRLF pada delapan JSON locale
existing; file frontend tidak diedit pada slice ini. Delapan file slice ini:
tool riset, dua file tes di atas, `PROJECT_STATUS.md`, `TODO.md`, kedua README
dan handoff ini.

## DATA-03 — diagnostik penolakan observasi

Slice lokal 2026-11-03 menambahkan `quality_issue: {"code": "..."}` pada simbol
yang ditolak validasi. `reason="invalid_data_or_metadata"` tetap kompatibel.
Kode menyatakan tahap pertama yang gagal, bukan seluruh masalah atau akar
penyebab provider. Tidak ada pesan exception atau nilai bar mentah dalam field
baru maupun log penolakan; provenance existing tetap dipertahankan.

Kode tahap: `currency_declaration`, `session_timezone`, `daily_interval`,
`share_volume_unit`, `adjustment_declaration`, `unique_bar_dates`,
`local_session_dates`, `requested_date_window`, `price_values`, `volume_values`,
dan `indicator_calculation`. Kode terakhir mencakup kegagalan kontrak perhitungan
atau respons analisis existing. Pada slice backend ini UI belum menampilkan field baru ini;
follow-up UI-01 di bawah menambahkan label tahap. JSON
API/agent/MCP/CLI memakai tool bersama tanpa menghitung policy tambahan.
Simbol sehat, bar kosong atau sumber gagal tidak diberi `quality_issue` buatan;
diagnostik akuisisi existing tetap terpisah. Tidak ada klaim suspensi/delisting
berdasarkan data kosong, gap tanggal atau usia observasi.

Delapan belas kasus baru mencakup metadata salah/hilang, index non-date, NaT,
duplikasi, intraday/timezone, bar di luar request, nilai invalid di luar tail,
kolom wajib hilang dan sanitasi exception. Tes HTTP parsial dan CLI exit 2
existing diperkuat untuk field ini; kontrol sehat/kosong tetap tidak memilikinya.
Run sebelum implementasi: **16 failed, 37 passed**, semua kegagalan baru berupa
`KeyError: 'quality_issue'`. Sesudah implementasi dan tambahan tes kolom hilang,
regresi akhir **538 passed**, termasuk **55 kasus kualitas**, tanpa kegagalan.

Perintah dari root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
git diff --check
```

Ruff lint/format dua file lulus. Probe CLI terpisah menjalankan modul melalui
subprocess tanpa kredensial warisan, cwd/home/runtime sementara dan akuisisi
sintetis: exit **2**, status **partial**, BBCA ditolak dengan
`adjustment_declaration`, BBRI sehat **20 bar**, `backtest_enabled=false`.
Stderr: `IDX research rejected bars for BBCA.JK (adjustment_declaration; ValueError)`.
Ini bukti permukaan CLI, bukan probe Yahoo nyata. HTTP 200 parsial diperiksa
melalui route existing dan TestClient. Mirror MCP existing diuji dalam regresi;
tidak ada sesi MCP eksternal yang dijalankan.

Warning existing anyio/Starlette serta percobaan jaringan tes indikator yang
diblokir pytest-socket tetap muncul. Frontend/build/browser, full backend/safety,
provider nyata dan deployment tidak diulang. DATA-03/UI-01 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX
nonaktif. Tidak ada token, akun, pembelian, order broker, staging atau commit.
Tujuh file slice: tool riset dan tes kualitas di atas, handoff ini,
`PROJECT_STATUS.md`, `TODO.md`, `README.md` dan `README_id.md`.
Pemeriksaan akhir **82 tautan lokal/anchor** pada empat dokumen proyek dan bagian
pengantar IDX kedua README, whitespace dokumen terkait serta `git diff --check`
lulus. Bagian upstream README yang tidak disentuh tidak diperiksa ulang.
Warning normalisasi LF → CRLF pada delapan JSON locale existing tetap muncul;
file frontend tidak diubah pada slice ini.

## UI-01 — tahap penolakan observasi

Slice lokal 2026-11-03 menampilkan tahap validasi backend pada simbol
`unavailable` dengan `reason="invalid_data_or_metadata"`. Sebelas kode pada
kontrak di atas memiliki label terjemahan pada seluruh 11 locale. UI tidak
menjalankan ulang validasi, menghitung policy, atau menampilkan exception/kode
asing mentah. Kode hilang, null atau tidak dikenal ditandai sebagai tahap belum
tersedia; alasan penolakan umum tetap terlihat untuk respons backend lama.
Pesan menjelaskan bahwa hanya tahap pertama yang gagal yang dilaporkan, bukan
seluruh masalah atau akar penyebab provider, dan menawarkan pengambilan ulang
atau pilihan simbol lain. Simbol kosong/kegagalan akuisisi tetap memakai pesan
existing tanpa diagnostik validasi buatan. Chart/indikator/provenance simbol
sehat dan status parsial tetap tersedia saat berpindah pilihan.

Perubahan kode: `frontend/src/lib/idx-research.ts`,
`frontend/src/pages/IDXResearch.tsx`,
`frontend/src/pages/__tests__/IDXResearch.test.tsx`, dan 11 JSON locale.
Tidak ada perubahan backend, dependensi, konfigurasi target TypeScript atau
aturan pasar. Bersama lima dokumen status/backlog/handoff/README, slice ini
menyentuh 19 file yang sudah memiliki pekerjaan lokal sebelumnya.

Perintah verifikasi dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Sebelum implementasi: **26 failed, 26 passed** pada tes halaman, termasuk
`Unable to find an element with the text: Failed validation stage: Currency declaration`.
Sesudah implementasi: tes terkait **115 passed**; frontend penuh **907 passed**
dalam 92 file. Build pertama gagal
`TS2550: Property 'hasOwn' does not exist on type 'ObjectConstructor'`.
Pemakaian diganti dengan `Object.prototype.hasOwnProperty.call`, tanpa mengubah
target proyek; build ulang lulus. Tes terkait dijalankan lagi setelah perbaikan
dan tetap **115 passed**. Regresi mencakup seluruh 11 kode, respons lama,
kode asing termasuk properti bawaan `__proto__`/`toString`, rendering 11 locale,
data kosong serta perpindahan simbol sehat/ditolak. Warning Vite configLoader
dan ukuran chunk existing tetap muncul; normalisasi LF/CRLF locale juga tercatat.

Browser memeriksa build produksi pada server QA sementara `127.0.0.1:18974`
dengan cwd/home/runtime terisolasi dan environment tanpa kredensial warisan.
Route `register_idx_research_routes` dan tool existing tetap dipakai; hanya
akuisisi diganti fixture sintetis: BBCA tanpa deklarasi adjustment, BBRI dengan
60 bar valid, dan TLKM kosong. Locale Indonesia menampilkan
“Tahap validasi yang gagal: Deklarasi adjustment harga”, keterangan tahap pertama,
pesan kosong TLKM tanpa tahap buatan, serta chart/indikator/provenance BBRI.
Desktop 1280 dan mobile 390 mempunyai `innerWidth == scrollWidth`; detail
mobile membungkus tanpa overflow horizontal. Harness tidak menyediakan layanan
percakapan sehingga banner sesi tampil; itu batas harness, bukan error riset.
Screenshot tersimpan di direktori sementara OS `idx-quality-ui-36as52re`
(`desktop.png` dan `mobile.png`). Tab ditutup dan viewport direset setelah QA;
server dihentikan setelah pemeriksaan. Tidak ada pemasangan harness ke aplikasi.

Pemeriksaan akhir **84 tautan lokal/anchor** pada empat dokumen proyek dan
pengantar IDX kedua README, whitespace dokumen terkait serta `git diff --check`
lulus. Port 18974 tidak lagi listening. Daftar lingkup slice: 3 file kode/tes
frontend, 11 locale dan 5 dokumen; tidak ada file tambahan yang di-stage.

Backend/full safety, CLI/MCP eksternal, provider nyata dan deployment tidak
diulang. Ini penyelesaian slice lokal, bukan UI-01 atau DATA-03 penuh;
RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance tetap fokus pribadi,
Index Alpha ditunda dan backtest IDX nonaktif. Perubahan sebelumnya dipertahankan;
tidak ada token, akun, pembelian, order broker, staging atau commit.


## UI-01 — waktu WIB dan tanggal provenance

Slice lokal 2026-11-03 membedakan tiga informasi pada panel simbol sehat:
`retrieved_at` sebagai waktu pengambilan berzona yang diformat di Asia/Jakarta
(24 jam, detik, label WIB), `data_as_of` sebagai tanggal sesi sumber, dan
`analysis.latest_date` sebagai sesi terakhir yang dianalisis. Waktu pengambilan
bukan waktu transaksi atau bukti kuotasi real-time. Tanggal sumber tidak diganti
dengan tanggal analisis; perbedaan metadata tetap terlihat tanpa disimpulkan
sebagai penyebab kegagalan provider.

Formatter menerima timestamp ISO dengan Z/offset eksplisit untuk pengambilan.
Timestamp tanpa zona, tanggal tidak nyata, metadata hilang atau invalid ditandai
Tidak tersedia, tanpa menampilkan nilai mentah atau Invalid Date. Kontrak
as-of loader harian saat ini berupa YYYY-MM-DD atau midnight lokal tanpa zona
(dengan pecahan nol opsional); bentuk lain ditandai tidak tersedia. Tanggal ini
tidak dikonversi melalui timezone browser. Dua key baru diterjemahkan pada
seluruh 11 locale. Chart, indikator, status parsial, data kosong, diagnostik usia
dan tahap penolakan sebelumnya dipertahankan. Tidak ada perubahan backend,
dependensi, rumus indikator atau aktivasi backtest.

Grounding: `backtest/loaders/idx_contract.py:41–42` menstempel retrieval UTC dan
as-of dari index sesi lokal; panel `frontend/src/pages/IDXResearch.tsx` sebelumnya
hanya menampilkan retrieval tanpa WIB serta tanggal analisis. Perubahan melalui
helper presentasi di `frontend/src/lib/idx-research.ts` dan panel existing.

Perintah dari frontend/:

```powershell
npm run test:run -- src/lib/__tests__/idx-research.test.ts src/pages/__tests__/IDXResearch.test.tsx src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Tes terkait **149 passed**; frontend penuh **941 passed** dalam **93 file**;
build lulus. Regresi awal sebelum implementasi menunjukkan timestamp tanpa zona
masih diformat seolah valid (`1/30/2026, 6:05:06 PM`) dan label WIB belum tampil
(expected `31/01/2026, 01.05.06 WIB`, received `31/1/2026, 01.05.06`). Tes awal
Indonesia juga sempat mendahului lazy loading locale; diperbaiki dengan menunggu
tombol terjemahan. Regresi mencakup pergantian tanggal, offset setara, pecahan
mikrodetik Python, tanggal kabisat/invalid, metadata hilang, serta rendering 11 locale.
Warning existing Vite configLoader dan chunk >500 kB tetap muncul.

Browser memeriksa build produksi di loopback 127.0.0.1:18975 melalui route/tool
existing; hanya akuisisi diganti sintetis, dengan cwd/home/runtime sementara dan
environment tanpa kredensial warisan. BBRI menampilkan `03/11/2026, 01.05.06 WIB`,
as-of sumber `2026-11-02`, serta sesi analisis `2026-11-03`. BBCA dengan retrieval
tanpa zona dan as-of invalid tetap memiliki chart serta dua nilai Tidak tersedia;
TLKM kosong memakai pesan existing. Desktop 1280 dan mobile 390 memiliki
innerWidth sama dengan scrollWidth; panel metadata dan teks membungkus tanpa
overflow. Screenshot desktop-provenance.png dan mobile-provenance.png berada di
direktori sementara OS `idx-time-ui-wby40dbm`. Banner percakapan tidak tersedia
merupakan batas harness yang tidak menyediakan /sessions. Tab ditutup, viewport
direset dan server QA dihentikan. Harness tidak dipasang ke aplikasi.

Backend/full safety, provider nyata, CLI/MCP eksternal dan deployment tidak
diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha
ditunda dan backtest IDX nonaktif. Perubahan sebelumnya dipertahankan; tidak ada
token, akun, pembelian, order broker, staging atau commit.

Pemeriksaan akhir: **86 tautan lokal/anchor** lulus; `git diff --check` dan
whitespace file slice lulus. Lingkup 20 file: helper/panel dan dua tes frontend,
11 locale, serta status/backlog/handoff dan dua README. Perbandingan locale
terhadap snapshot awal memastikan hanya dua key baru ditambahkan. Warning
normalisasi LF/CRLF Git tetap tercatat. Port 18975 tidak lagi listening.


## UI-01 — cakupan observasi

Slice lokal 2026-11-03 menampilkan dua angka pada panel simbol sehat:
`analysis.read_identity.bar_count` sebagai jumlah bar yang dianalisis dan
`lookback` dari respons sebagai batas bar diminta. Batas tidak diambil dari
draft form; jumlah analisis tidak dihitung ulang dari chart. Jumlah harus
berupa angka integer positif yang aman; metadata hilang, nol, negatif,
pecahan, non-finite atau string ditampilkan Tidak tersedia. Hilangnya
`read_identity` juga tidak menggugurkan chart/indikator yang tersedia.

Panel menjelaskan bahwa bar yang diterima bisa lebih sedikit dari permintaan.
Jumlah bukan bukti kelengkapan kalender; bar hilang tidak diisi dan penyebabnya
tidak ditebak sebagai suspensi/delisting atau kegagalan provider. Simbol
unavailable tetap memakai pesan existing tanpa menampilkan jumlah buatan.
Tiga key baru diterjemahkan pada seluruh 11 locale. Tidak ada perubahan backend,
kontrak API, rumus indikator, dependensi atau aktivasi backtest.

Grounding: `agent/src/tools/idx_research_tool.py` memotong observasi tervalidasi
melalui `tail(lookback)` sebelum mengirim chart dan memanggil summarizer existing;
`agent/src/tools/technical_indicator_tool.py` menerbitkan `read_identity.bar_count`.
Panel `frontend/src/pages/IDXResearch.tsx` sebelumnya belum menampilkan jumlah
tersebut. Perubahan menambah presentasi angka di panel yang sama.

Perintah dari frontend/:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Tes terkait **169 passed**; frontend penuh **961 passed** dalam **93 file**;
build lulus. Dua puluh kasus baru mencakup jumlah terhadap lookback respons,
jumlah invalid, read identity hilang, pemilihan simbol unavailable dan rendering
11 locale. Run awal tes sempat gagal parse pada ekspresi tipe fixture baru;
setelah dikoreksi, regresi sebelum implementasi gagal sebagaimana diharapkan:
`Unable to find an element with the text: Analyzed bars`. Warning existing
Vite configLoader dan chunk >500 kB tetap muncul.

Browser memeriksa build produksi pada loopback 127.0.0.1:18975 melalui route/tool
existing dengan akuisisi sintetis, home/runtime/cwd sementara dan environment
tanpa kredensial warisan. Panel menampilkan **60 bar dianalisis / batas 200**;
setelah batas diubah dan fetch manual diulang, tampil **60 / 60**. Teks pembatasan
tetap terlihat pada kedua keadaan. TLKM kosong tidak menampilkan panel jumlah.
Desktop 1280 dan mobile 390 memiliki innerWidth sama dengan scrollWidth;
teks panel membungkus tanpa overflow. Screenshot desktop-coverage.png dan
mobile-coverage.png disimpan di direktori temporary OS `idx-coverage-b8dao0uy`.
Banner sesi tidak tersedia adalah batas harness tanpa endpoint /sessions,
bukan hasil riset. Harness tidak ditambahkan ke aplikasi.

Backend/full safety, provider nyata, CLI/MCP eksternal dan deployment tidak
diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka;
Index Alpha ditunda dan backtest IDX nonaktif. Pekerjaan sebelumnya dipertahankan;
tidak ada token, akun, pembelian, order broker, staging atau commit.

Pemeriksaan akhir: **78 tautan lokal/anchor** pada status/backlog/handoff lulus;
whitespace 18 file slice dan `git diff --check` lulus. Hash snapshot awal
memastikan file di luar slice, termasuk seluruh kode backend, tidak berubah;
penghapusan tiga baris key baru memulihkan isi awal masing-masing locale.
Warning normalisasi LF/CRLF Git tetap tercatat. Tab QA ditutup, viewport
direset, server sintetis dihentikan dan port 18975 tidak lagi listening.


## DATA-03 — tipe numerik observasi

Slice lokal 2026-11-03 memperketat pemeriksaan OHLCV pada frame yang diterima
`IDXResearchTool`, sebelum `tail(lookback)`. Boolean Python/numpy/pandas bukan
harga atau jumlah saham walaupun `math.isfinite(True)` bernilai benar. Harga
boolean ditolak dengan `price_values`; volume boolean dengan `volume_values`.
Overflow konversi angka ke float kini masuk penolakan per simbol yang sama,
dengan log tersanitasi berisi simbol, tahap dan tipe exception. HTTP tetap 200
untuk hasil parsial; CLI tetap exit 2. Simbol sehat tidak ikut digugurkan.

Grounding awal: `src/tools/idx_research_tool.py:143–149` hanya memakai pemeriksaan
OHLC, `math.isfinite` dan volume nonnegatif; handler pada baris 190 belum menangani
`OverflowError`. `src/api/idx_research_routes.py:34` meneruskan hasil tool bersama;
MCP memakai mirror kelas, CLI memanggil kelas yang sama. Perbaikan tetap pada
pemilik validasi ini, tanpa mengubah summarizer indikator atau loader pasar lain.

Sebanyak 19 kasus baru mencakup True/False pada kelima kolom sebelum tail,
kolom volume bool/nullable boolean, overflow integer `10**400` pada high/volume,
HTTP parsial, sanitasi, frame sumber tidak termutasi, CLI exit 2 serta kontrol
integer/float biasa dan nullable dengan volume nol. Tes existing volume null,
gap tanggal, adjustment, hasil kosong dan metadata tetap lulus. Fixture sintetis
bukan kutipan pasar atau contoh aturan BEI. Ini tidak memvalidasi tipe payload
mentah sebelum normalisasi loader, presisi uang, seluruh batas aritmetika
indikator, atau kebenaran data provider.

Perintah dari root repository:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
git diff --check
```

Regresi sebelum perbaikan: **8 failed, 59 passed**, berupa
`assert 'ok' == 'unavailable'` pada boolean dan
`OverflowError: int too large to convert to float` pada dua kasus HTTP.
Sesudah perbaikan, fitur/kualitas/MCP awal **120 passed**; setelah kontrol dtype
dan CLI tambahan, regresi 14 modul **557 passed**, termasuk **74 kasus kualitas**.
Ruff lint lulus; format check awal meminta pemformatan dua ekspresi baru.
Sesudah `ruff format`, lint dan format check dua file lulus.
Warning existing anyio/Starlette dan percobaan koneksi eksternal tes indikator
yang diblokir pytest-socket tetap tercatat; tidak ada probe provider nyata.

Probe permukaan CLI terpisah memakai subprocess modul existing, akuisisi
sintetis, cwd/home/runtime sementara dan environment tanpa kredensial warisan:
exit **2**, status **partial**, BBCA ditolak dengan `volume_values`, BBRI sehat
**20 bar**, latest close sintetis **105**, `backtest_enabled=false`. Stderr:
`IDX research rejected bars for BBCA.JK (volume_values; OverflowError)`.
Harness berada di temporary OS `idx-numeric-cli-4x1m69ue`, tidak masuk aplikasi.
HTTP diuji melalui route existing dengan TestClient; tidak ada server atau tab
QA yang dibuka. Tidak ada sesi MCP eksternal.

Tujuh file slice: tool riset, tes kualitas, status, backlog, handoff ini dan
kedua README. Frontend/dependensi tetap utuh. Frontend/build/browser,
full backend/safety, provider nyata dan deployment tidak diulang. UI-01/DATA-03
penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance tetap fokus riset
pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tidak ada token, akun,
pembelian, order broker, staging atau commit.

Pemeriksaan akhir: **92 tautan lokal/anchor** pada status/backlog/fondasi/handoff
serta pengantar IDX kedua README lulus. Whitespace tujuh file dan
`git diff --check` lulus, dengan warning normalisasi LF/CRLF Git tetap tercatat.
Perbandingan hash memastikan hanya tujuh file slice yang berubah; seluruh file
di luar slice, termasuk frontend dan dependensi, tetap sama tanpa file tambahan
atau hilang. Upaya snapshot awal gagal decoding nama file dengan cp1252;
snapshot berhasil setelah pembacaan daftar Git dibuat eksplisit UTF-8.


## DATA-03 — batas numerik indikator

Slice lokal **2026-11-03, Asia/Jakarta**. Input finite tidak menjamin hasil
aritmetika finite: volume sintetis `1e308` menghasilkan rata-rata overflow;
harga sintetis bergantian `1e155`/`2e155` menghasilkan Bollinger ±Infinity,
dan `1e308`/`1e307` juga menghasilkan NaN. Ini fixture uji, bukan harga atau
volume bursa dan bukan batas nominal instrumen IDX.

Grounding: `src/tools/idx_research_tool.py:175` memanggil summarizer existing;
`src/tools/technical_indicator_tool.py:333` mengizinkan token nonfinite pada
JSON helper. Sebelumnya serialisasi strict baru dijalankan sesudah loop simbol,
sehingga satu hasil invalid menggugurkan HTTP/CLI beserta simbol yang sehat.
Sekarang `idx_research_tool.py:189` memeriksa seluruh analisis dengan
`json.dumps(analysis, allow_nan=False)` di dalam batas kegagalan per simbol.
Penolakan memakai `reason=invalid_data_or_metadata` dan kode existing
`quality_issue.code=indicator_calculation`; log hanya simbol, tahap dan tipe
exception. Bars/analysis simbol gagal tidak diterbitkan. Tidak ada clamp,
penggantian NaN menjadi null, atau perubahan rumus indikator. Null existing
untuk histori pendek dan volume hilang, serta hasil besar yang masih finite,
tetap diterima. Frame sumber tidak dimutasi. HTTP meneruskan tool yang sama;
agent, mirror MCP dan CLI tetap memakai kontrak existing.

Kriteria slice: input finite dengan hasil indikator nonfinite ditolak per
simbol; HTTP parsial dan CLI exit 2 tetap menyertakan simbol sehat; kontrol
finite/null serta nonmutasi tetap lulus. Lima kasus baru memakai perhitungan
existing tanpa mock hasil indikator. Sebelum perubahan, dua regresi HTTP/CLI
**2 failed, 74 deselected**, keduanya
`ValueError: Out of range float values are not JSON compliant: inf`.
Sesudah perubahan, run fitur/kualitas/MCP awal **129 passed**. Dengan tiga
kontrol harga/finite tambahan, regresi 14 modul **562 passed**, termasuk
**79 kasus kualitas**; Ruff lint dan format check dua file lulus.

Perintah dari root repository:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
git diff --check
```

Probe CLI subprocess menjalankan modul existing via `runpy` dengan akuisisi
sintetis, cwd/home/runtime temporary dan environment minimum tanpa kredensial
warisan: exit **2**, status **partial**, BBCA ditolak pada
`indicator_calculation`, BBRI sehat **20 bar**, latest close sintetis **105**,
`backtest_enabled=false`. Log: `IDX research rejected bars for BBCA.JK
(indicator_calculation; ValueError)`. Temporary OS: `idx-derived-cli-gbrck_v3`.
HTTP diperiksa melalui route existing dengan TestClient; tidak ada server/tab
QA atau sesi MCP eksternal yang dibuka.

Warning NumPy overflow/invalid arithmetic diharapkan pada fixture ekstrem;
warning existing anyio/Starlette dan koneksi tes indikator yang diblokir
pytest-socket tetap tercatat. Tidak ada penambahan dependensi atau perubahan
frontend, loader maupun helper indikator bersama. Frontend/build/browser,
full backend/safety, provider nyata dan deployment tidak diulang. Slice ini
memastikan isolasi hasil nonfinite, bukan akurasi seluruh rumus, presisi uang,
validasi payload mentah provider atau histori event. UI-01/DATA-03 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance tetap fokus pribadi,
Index Alpha ditunda, backtest IDX nonaktif. Tidak ada pembacaan token, akun,
pembelian, order broker, staging atau commit.

Pemeriksaan akhir slice: **95 tautan lokal/anchor** pada status/backlog/fondasi/
handoff serta pengantar IDX kedua README, whitespace tujuh file dan
`git diff --check` lulus. Warning normalisasi LF/CRLF Git tetap tercatat.
Snapshot hash atas 3.187 file memastikan hanya tujuh file slice berubah:
tool riset, tes kualitas, status, backlog, handoff dan kedua README. File di
luar slice tetap sama, tanpa tambahan/hilang; index Git tetap tanpa staging.


## DATA-03 — cakupan volume observasi

Slice lokal **2026-11-03, Asia/Jakarta** menambahkan `volume_coverage` pada
setiap item riset yang berstatus `ok`. Empat integer melaporkan cakupan pada
bar yang benar-benar dianalisis, sesudah sort/tail: `bar_count`,
`available_bar_count`, `missing_bar_count` dan `zero_bar_count`. Nol termasuk
volume tersedia; null hanya dihitung sebagai hilang. Jumlah tersedia + hilang
sama dengan jumlah bar. Nol merupakan subset tersedia, bukan kategori ketiga
yang dijumlahkan lagi. Histori lebih pendek memakai jumlah aktual, bukan
lookback permintaan. Gap tanggal tidak menghasilkan bar tambahan.

Grounded: `src/tools/idx_research_tool.py:162` menentukan frame analisis;
bar chart dan summarizer memakai frame tersebut. Hitungan baru pada baris 193
berasal dari bar keluaran yang sama, setelah analisis lolos JSON strict pada
baris 190. API `src/api/idx_research_routes.py:33`, mirror MCP
`mcp_server.py:2829` dan CLI tetap memakai tool bersama. Blast radius: hanya
kontrak JSON riset pribadi dan dokumentasinya. Invariant: harga, volume,
rumus indikator, provenance dan frame sumber tetap utuh; simbol unavailable
tidak mendapat hitungan buatan; missing volume tidak menggugurkan data valid;
backtest IDX tetap nonaktif. Tidak ada policy atau penyimpanan kedua.

Kriteria penerimaan dipenuhi melalui delapan kasus sintetis baru: volume penuh,
seluruhnya null, seluruhnya nol, campuran null/nol termasuk null di luar tail,
nullable volume pada frame terbalik dengan gap tanggal, histori satu bar,
HTTP parsial valid/invalid/kosong dan CLI all-null dengan exit 0. Nonmutasi
frame/provenance juga diperiksa. Sebelum implementasi, enam kasus terpilih
**6 failed, 80 deselected**, semuanya `KeyError: 'volume_coverage'`. Run akhir
regresi 14 modul **570 passed**, termasuk **87 kasus kualitas**. Ruff lint dan
format check kedua file lulus. Perintah dari root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
git diff --check
```

Probe CLI terpisah menjalankan modul via `runpy` dengan akuisisi sintetis,
cwd/home/runtime temporary dan environment minimum tanpa kredensial warisan.
Hasil: exit **2**, `status=partial`, BBCA **20 bar / 19 tersedia / 1 hilang /
1 nol**, BBRI unavailable tanpa `volume_coverage`, `backtest_enabled=false`;
stderr kosong. Harness temporary OS `idx-volume-cli-lhvrjatn`. HTTP diperiksa
melalui route existing dengan TestClient; tidak ada server/tab QA atau sesi
MCP eksternal dibuka. Ini bukti eksekusi lokal, bukan probe provider nyata.

Hitungan tidak memverifikasi likuiditas, sesi bursa yang hilang, suspensi,
delisting, adjustment, delay atau akurasi provider. Warning NumPy pada fixture
ekstrem, deprecation anyio/Starlette dan percobaan koneksi indikator existing
yang diblokir pytest-socket tetap tercatat. Tidak ada perubahan loader,
helper/rumus indikator, frontend atau dependensi. UI belum menampilkan ringkasan
cakupan volume; frontend/build/browser, backend penuh/safety, provider nyata
dan deployment tidak diulang. DATA-03/UI-01 penuh, RULE-01/DATA-01/RESEARCH-01
tetap terbuka; Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda,
backtest IDX nonaktif. Tidak ada token, akun, pembelian, order, staging atau commit.

Pemeriksaan akhir: **98 tautan lokal/anchor**, whitespace tujuh file dan
`git diff --check` lulus; warning normalisasi LF/CRLF Git tetap tercatat.
Snapshot hash 3.187 file memastikan hanya tujuh file slice berubah: tool riset,
tes kualitas, status, backlog, handoff dan kedua README. Sebanyak 3.180 file
di luar slice tetap sama, tanpa file tambahan/hilang; index Git tidak berubah.


## UI-01 — cakupan volume

Slice lokal **2026-11-03, Asia/Jakarta** menampilkan empat hitungan dari
`volume_coverage` pada panel simbol sehat: jumlah bar cakupan, volume tersedia,
hilang dan nol. Backend tetap menjadi pemilik hitungan; UI tidak menghitung
ulang bar chart, memakai lookback atau menurunkan hitungan dari indikator.
Nol termasuk tersedia, bukan kategori ketiga yang dijumlahkan lagi. Penjelasan
panel membatasi hitungan pada bar diterima, bukan bukti kelengkapan sesi atau
likuiditas. Simbol unavailable tidak menampilkan ringkasan volume.

Grounded: `agent/src/tools/idx_research_tool.py:162` menentukan sort/tail;
baris 194–199 membentuk hitungan dan baris 214 menerbitkannya. Request API
existing mengembalikan payload ini; tipe frontend sebelumnya belum memiliki
field tersebut. Perubahan hanya menambah tipe opsional nullable, presentasi
pada `frontend/src/pages/IDXResearch.tsx`, tes halaman dan enam key pada 11 locale.
Backend, loader, rumus indikator, provenance, chart dan dependensi tetap utuh.

Hitungan total harus integer positif yang aman; tiga hitungan volume boleh nol.
Field hilang/null, boolean, string, negatif, pecahan, nonfinite dan angka di luar
safe integer ditampilkan Tidak tersedia. Validasi ini hanya format presentasi,
bukan rekonsiliasi atau koreksi kontrak backend. Field valid di sebelahnya tetap
terlihat; chart dan indikator tidak digugurkan. Respons lama tanpa ringkasan juga
mendapat empat label Tidak tersedia. Tidak ada persentase atau imputasi baru.

Kriteria slice dibuktikan dengan 27 kasus baru: metadata berbeda dari chart dan
lookback, seluruh volume null/nol/positif, metadata absen/null/invalid, total nol,
pergantian simbol unavailable lalu kembali, dan angka besar pada seluruh locale.
Sebelum implementasi UI, regresi terpilih **1 failed, 111 skipped**:
`Unable to find role="group" and name "Volume coverage"`.
Perintah dari frontend/:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Hasil akhir: tes terkait **196 passed**; frontend penuh **988 passed** dalam
**93 file**; build lulus. Satu pemanggilan npm awal di root gagal ENOENT karena
package.json berada di frontend; perintah benar di atas lulus. Warning existing
Vite configLoader dan chunk >500 kB tetap muncul; tidak menambah dependensi.

Browser memeriksa build produksi di loopback 127.0.0.1:18975 memakai route/tool
existing, akuisisi sintetis, cwd/home/runtime sementara dan environment minimum
tanpa kredensial warisan. BBCA menampilkan **20 / 19 tersedia / 1 hilang / 1 nol**;
BBRI seluruh volume null menampilkan **20 / 0 tersedia / 20 hilang / 0 nol**,
dengan indikator volume tetap Tidak tersedia. TLKM unavailable tidak memiliki
grup cakupan volume. Desktop 1280 dan mobile 390 memiliki innerWidth sama dengan
scrollWidth; seluruh teks dan angka panel membungkus tanpa overflow horizontal.
Screenshot desktop-volume.png dan mobile-volume.png tersimpan di temporary OS
`idx-volume-ui-knucc3z_`. Banner sesi tidak tersedia adalah batas harness yang
tidak menyediakan /sessions. Navigasi pertama terlalu cepat dan menghasilkan
connection refused sebelum startup selesai; setelah port siap, browser lulus.
Tidak ada perubahan untuk mengatasi banner pada aplikasi. Tab QA ditutup dan
viewport direset; server QA dihentikan. Harness tidak ditambahkan ke repository.

Ini bukti presentasi/integrasi lokal sintetis, bukan penerimaan provider.
Backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak
diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka;
Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda, backtest IDX nonaktif.
Tidak ada pembacaan token, akun, pembelian, order broker, staging atau commit.

Pemeriksaan akhir: **93 tautan lokal/anchor** pada status/backlog/fondasi/handoff
serta pengantar IDX kedua README, whitespace 19 file slice dan `git diff --check`
lulus. Warning normalisasi LF/CRLF Git existing tetap tercatat. Snapshot hash
3.187 file memastikan 19 file slice berubah dan 3.168 file lain tetap sama,
tanpa tambahan/hilang; index Git identik. Isi awal setiap locale dipulihkan
secara identik dengan menghapus enam baris key baru. Port QA 18975 sudah ditutup.


## UI-01 — diagnostik upaya sumber

Slice lokal 2026-11-03 menampilkan `diagnostics.attempts` pada panel simbol
unavailable dengan `reason=no_data_or_source_failure`. Pemilik diagnostik tetap
`src.market_data.fetch_market_data` (record upaya/finalisasi `_diagnostics`),
kemudian `IDXResearchTool.execute` meneruskannya ke API/agent/MCP/CLI. UI hanya
membaca upaya, mempertahankan urutan termasuk pengulangan, dan menerjemahkan tiga
hasil: `no_data` = tanpa bar pada rentang tersebut, `fetch_failed` = request gagal,
`source_unavailable` = periksa konfigurasi/dependensi opsional. Tidak ada inferensi
suspensi, delisting, kelengkapan kalender atau akar penyebab jaringan/provider.

Grounded: `agent/src/market_data.py:339` dan `:562`,
`agent/src/tools/idx_research_tool.py:109`, serta panel unavailable existing di
`frontend/src/pages/IDXResearch.tsx`. Blast radius: tipe respons, presentasi,
tes halaman dan tujuh key pada 11 locale. Invariant: urutan/backend tetap pemilik,
hasil sehat dan penolakan validasi tetap terpisah; tidak mengubah loader,
provenance, rumus indikator, routing, dependensi atau backtest.

Sumber dikenal `yahoo`, `yfinance`, `local` ditampilkan sebagai identitas transport.
Sumber asing/hilang ditandai Tidak tersedia; hasil asing/hilang ditandai hasil
upaya tidak tersedia. Array kosong/hilang/null/non-array mendapat pesan detail
belum tersedia, bukan kesimpulan tanpa data. Entry null tetap memiliki baris
netral. Kode mentah, sumber asing dan field `recovery` tidak dirender. Panel ini
tidak ditampilkan pada simbol sehat atau penolakan validasi observasi.

Dua puluh kasus baru memeriksa urutan yang berbeda dari fallback default, semua
tiga hasil, metadata hilang/null/kosong/non-array, entry null dan kode asing,
sanitasi, perpindahan kembali ke simbol sehat, pemisahan validasi, dan 11 locale.
Tes pembeda awal **1 failed, 130 skipped** dengan
`Unable to find an accessible element with the role "group" and name "Source attempts"`.
Run implementasi pertama mendeteksi masalah encoding default cp1252 Windows
(UnicodeDecodeError, sembilan locale belum lengkap dan separator invalid).
Penulisan UTF-8 eksplisit memperbaikinya; seluruh file terkait decode UTF-8 strict.

Perintah dari frontend/:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Hasil: tes terkait **216 passed**; suite penuh **1007 passed**, **93 file**,
sebelum satu tes tambahan pemisahan validasi (lulus dalam run terkait terakhir).
Build lulus; warning existing Vite configLoader dan chunk >500 kB tetap muncul.

Browser memeriksa build produksi melalui route/tool existing, akuisisi sintetis,
environment minimum tanpa kredensial warisan, cwd/home/runtime sementara dan
loopback `127.0.0.1:18976`. BBCA sehat mempertahankan chart/indikator; BBRI gagal
menampilkan Yahoo request gagal, yfinance tanpa bar dan local tidak tersedia
dalam urutan itu. TLKM tanpa detail menampilkan pesan detail tidak tersedia.
Locale Indonesia dan viewport desktop 1280/mobile 390 diperiksa; innerWidth dan
scrollWidth sama pada keduanya, teks panel membungkus. Banner sesi existing
adalah batas harness yang tidak menyediakan endpoint /sessions.

Ini bukti presentasi lokal sintetis. Backend penuh/safety, provider nyata,
CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance tetap fokus riset pribadi;
Index Alpha ditunda, backtest IDX nonaktif. Tidak membaca token, membuat akun,
membeli paket, menjalankan order, staging atau commit.


Pemeriksaan akhir: 97 tautan lokal/anchor pada status/backlog/fondasi/handoff,
UTF-8 strict, whitespace 19 file slice dan `git diff --check` lulus. Snapshot
3.187 file membuktikan hanya 19 file slice berubah, 3.168 file lain identik,
tanpa tambahan/hilang; index Git identik. Teks locale awal identik setelah tujuh
key baru dihapus (perbedaan newline LF/CRLF diperhitungkan). Warning LF/CRLF
Git existing tercatat. Tab QA ditutup, viewport direset dan server QA dihentikan.


## UI-01 — validasi presentasi usia observasi

Slice lokal **2026-11-03, Asia/Jakarta** memperketat presentasi `recency` pada
kartu watchlist dan panel detail memakai satu helper `getIDXRecency`.
Sebelumnya setiap status selain `warning` dipresentasikan sebagai dalam rentang,
termasuk status asing atau hilang. Kini diagnostik yang tidak didukung mendapat
pesan terjemahan existing **Usia observasi belum tersedia.**; chart, indikator,
provenance dan hasil parsial tetap tersedia. Tidak ada nilai diagnostik mentah
atau status dalam rentang/warning buatan yang ditampilkan.

Grounded: pemilik backend `agent/src/tools/idx_research_tool.py` membentuk usia,
ambang dan verdict; dua konsumen UI di `frontend/src/pages/IDXResearch.tsx`
kini melalui helper presentasi `frontend/src/lib/idx-research.ts`. Helper hanya
menerima objek non-array dengan policy `calendar_age_warning_v1`,
`calendar_verified=false`, status `warning`/`within_window`, usia/ambang integer
aman nonnegatif dan dua tanggal kalender valid berformat persis YYYY-MM-DD.
Nol sah; leap day valid diterima. Metadata null/hilang, boolean/string pada
hitungan, negatif, pecahan, nonfinite, unsafe integer, tanggal mustahil, timestamp,
policy/status asing atau scope kalender berbeda menghasilkan panel netral.
Seluruh diagnostik ditandai tidak tersedia bila salah satu field wajib invalid.

Ini pemeriksaan format/kontrak presentasi, bukan autentikasi atau rekonsiliasi
metadata. UI tidak menghitung usia dari tanggal, membandingkan ambang dengan usia,
menyimpulkan sesi hilang atau mengganti verdict backend. Status/angka yang formatnya
valid tetap dipertahankan meskipun berbeda dari chart. Backend, loader, provenance,
rumus indikator, dependensi dan seluruh locale tetap identik; pesan existing pada
11 locale dipakai tanpa key baru. Tipe respons kini juga menyatakan recency nullable.

Delapan tes pembeda awal gagal sebelum guard: **8 failed, 132 skipped**, dengan
`Unable to find an element with the text: Observation age unavailable.`.
Setelah implementasi, 68 kasus baru mencakup kartu/panel, perpindahan simbol,
retensi chart/indikator, tanggal/tipe angka dan pesan netral pada 11 locale.
Perintah dari frontend/:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts
npm run test:run
npm run build
```

Hasil akhir: frontend penuh **1076 passed**, **93 file**; build lulus.
Warning existing Vite configLoader dan chunk >500 kB tetap muncul.

Browser build produksi diperiksa di loopback `127.0.0.1:18977`, memakai route/tool
existing dengan akuisisi sintetis dan modifikasi diagnostik respons khusus QA.
Environment minimum tanpa kredensial warisan, home/cwd/runtime sementara.
BBCA berusia 15 hari tetap menampilkan warning sah; BBRI dengan status asing dan
TLKM dengan ambang nonnumerik menampilkan pesan netral, chart/indikator utuh dan
nilai mentah tidak terlihat. Locale Indonesia, desktop 1280 dan mobile 390:
`innerWidth == scrollWidth`, tanpa overflow horizontal. Banner percakapan existing
berasal dari harness yang tidak menyediakan /sessions. Tab QA ditutup, viewport
direset, proses server milik QA dihentikan setelah identitasnya diperiksa.

Ini verifikasi UI lokal sintetis. Backend penuh/safety, provider nyata,
CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance fokus riset pribadi,
Index Alpha ditunda dan backtest IDX nonaktif. Tidak membaca token, membuat akun,
membeli paket, menjalankan order, staging atau commit.

Pemeriksaan akhir: tes terkait **284 passed** (4 file), **105 tautan lokal/anchor**,
UTF-8 strict, whitespace sembilan file slice dan `git diff --check` lulus.
Snapshot 3.187 file membuktikan hanya sembilan file slice berubah; **3.178 file
lain identik**, tanpa tambahan/hilang; index Git identik. Warning normalisasi
LF/CRLF Git tetap tercatat. Port QA 18977 tidak lagi listening.

## UI-01 — tabel observasi OHLCV harian

Slice lokal **2026-11-03, Asia/Jakarta** menambahkan tabel baca-saja pada detail
simbol sehat. Sebelumnya `IDXBar` sudah memuat OHLCV di respons, tetapi halaman
hanya memperlihatkan seri close dan indikator. Tabel membuka akses ke observasi
itu tanpa akuisisi, agregasi, konversi lot, penyesuaian harga atau rumus baru.

Grounded: kontrak `frontend/src/lib/idx-research.ts:49` memiliki enam field bar;
`agent/src/tools/idx_research_tool.py:163` membentuk bar dari frame yang juga
menjadi input indikator. `ObservationTable` di `frontend/src/pages/IDXResearch.tsx`
membaca array yang sama dengan `CloseChart`. Backend tetap pemilik validasi dan
urutan observasi. Tanggal adalah label sesi YYYY-MM-DD, tanpa konversi timezone;
UI tidak mengisi gap, menyimpulkan suspensi atau memverifikasi kalender.

Kriteria penerimaan dan hasil:

- Disclosure native `details/summary` tertutup awalnya dan dapat dibuka/tutup
  dengan keyboard. Pemilihan simbol lain membuat disclosure baru; simbol
  unavailable tidak mempunyai tabel. Bar kosong/hilang ditandai tidak tersedia.
- Enam kolom memiliki header berscope; caption menyebut simbol dan region gulir
  mempunyai nama serta tab stop. OHLC berlabel IDR, volume berlabel saham.
  Angka diformat sesuai locale dengan hingga 17 digit signifikan, tanpa memakai
  pembulatan dua desimal pada ringkasan kartu. Null tetap tidak tersedia dan
  volume nol tidak dianggap hilang. Respons tidak dimutasi.
- Tabel memuat seluruh bar respons (maksimum 500 dari kontrak existing), dalam
  urutan respons, dengan tinggi gulir maksimum 20rem dan header sticky. Pada
  mobile hanya tabel yang bergulir horizontal; halaman tetap selebar viewport.
- Delapan key baru diterjemahkan pada seluruh 11 locale. Tes parity key,
  interpolation dan teks Inggris tersalin existing tetap lulus. Tidak ada
  perubahan dependensi, API/backend, loader, provenance atau rumus indikator.

Tujuh belas tes baru berada di
`frontend/src/pages/__tests__/IDXResearch.observations.test.tsx`: OHLCV aktual,
pecahan harga, gap tanggal, nol/null, nonmutasi, satu request, retensi chart dan
indikator, header/region, disclosure/pemilihan simbol, empty/missing, 500 bar serta
format locale dan volume besar pada 11 bahasa. Dua assertion awal gagal karena
query role jsdom masih menemukan isi details tertutup; tes memakai atribut native
`open`, dan visibilitas diverifikasi terpisah di browser. Build awal menemukan
TS2345 pada key i18n dinamis; daftar key literal memperbaikinya, tanpa cast luas.

Perintah dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.observations.test.tsx src/pages/__tests__/IDXResearch.test.tsx src/i18n/__tests__/i18n.test.ts src/lib/__tests__/idx-research.test.ts
npm run test:run
npm run build
```

Tes terkait **289 passed** (4 file); frontend penuh **1093 passed** (94 file);
build akhir lulus. Warning existing configLoader Vitest, chunk >500 kB dan catatan
plugin timing Vite tetap tercatat. Tidak ada gate yang gagal pada hasil akhir.

QA browser memakai build produksi dan server HTTP sintetis khusus pada loopback
`127.0.0.1:18977`; server itu hanya menyajikan dist/fixture dan tidak mengimpor
backend, membaca konfigurasi akun atau memanggil provider. BBCA 500 bar teramati,
TLKM satu bar dan BBRI unavailable diperiksa dalam locale Indonesia. Enter membuka
serta Space menutup tabel; tabel tertutup benar-benar tidak terlihat di browser.
Volume pertama 0, kedua null, berikutnya 1.234.567.890.123; harga pecahan
100,123456789 tetap tampil. Desktop 1280 dan mobile 390 memiliki
`innerWidth == documentElement.scrollWidth`; region mobile memiliki lebar 261px,
isi 801px dan dapat digulir dengan ArrowRight saat fokus. Tinggi region desktop
320px untuk 500 bar; histori satu bar hanya mempunyai dua row termasuk header.
Log error browser kosong. Screenshot sintetis disimpan di direktori temporary
`idx-column-slice-k3lvfbsm`, di luar source tree.

Ini verifikasi presentasi lokal sintetis, bukan integrasi provider atau deployment.
Backend penuh/safety, provider nyata serta CLI/MCP eksternal tidak diulang.
UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance tetap
fokus riset pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tidak membaca
token, membuat akun, membeli paket atau menjalankan order. Tidak staging/commit.

Pemeriksaan akhir: **158 tautan lokal/anchor** pada enam dokumen terkait, UTF-8
strict, whitespace 18 file slice dan `git diff --check` lulus. Dari baseline
3.187 file, hanya **17 file existing** berubah dan **1 file tes baru** ditambahkan;
**3.170 file lainnya identik**, tanpa file hilang. Index Git identik dengan awal.
Warning normalisasi LF/CRLF existing tetap tercatat. Tab QA ditutup, viewport
direset, identitas proses QA diperiksa sebelum dihentikan dan port 18977 tidak
lagi listening. Backend, loader, rumus dan manifest/lock tetap identik.

## UI-01 — kelengkapan panel indikator

Slice lokal **2026-11-03, Asia/Jakarta** melengkapi panel indikator riset pribadi.
Backend existing `agent/src/tools/technical_indicator_tool.py:246–262,316–324`
sudah menghitung komponen MACD, Bollinger Bands dan statistik volume dari satu
observasi. Panel sebelumnya hanya menampilkan MACD line, volume terbaru dan rasio.
Kini UI membaca signal line/histogram, Bollinger upper/middle/lower 20 bar (IDR),
serta volume sma_20 (saham) dari `analysis.indicators` yang sama. Tidak ada request,
rumus indikator, konversi unit, penyesuaian harga atau interpretasi sinyal baru.

Kriteria penerimaan terpenuhi:

- Keenam field baru memakai nilai respons, termasuk fixture yang sengaja berbeda
  dari chart satu bar. Memilih simbol lain tidak memicu request baru; chart,
  provenance dan hasil parsial tetap tersedia. Respons tidak dimutasi.
- Semua nilai panel indikator diformat menurut locale dengan hingga 17 digit
  signifikan, mengikuti pola tabel OHLCV. Presisi backend seperti MACD -0.0001
  tidak dibulatkan menjadi nol oleh batas dua desimal UI. Ini tidak menambahkan
  presisi data atau mengubah pembulatan existing pada backend/kartu ringkasan.
- Nol dan nilai negatif tetap ditampilkan. Komponen/struktur null atau hilang
  tetap tidak tersedia. Akses metadata volume kini juga memakai optional chaining;
  struktur volume null/hilang sebelumnya dapat menggagalkan render panel.
- Enam key diterjemahkan pada seluruh 11 locale. Tipe frontend menambahkan
  Bollinger opsional/nullable dan menyatakan komponen MACD nullable. Panel memakai
  grid existing dengan pembungkusan label/angka agar angka besar tidak melebar.

Lima belas tes baru di
`frontend/src/pages/__tests__/IDXResearch.indicators.test.tsx` menguji nilai
respons, presisi kecil, nol/negatif, null/hilang, nonmutasi, satu request,
pergantian simbol dan format pada 11 locale. Sebelum implementasi, **15 failed**,
termasuk dua error `Cannot read properties of null/undefined (reading 'latest')`.
Setelah implementasi, seluruh gate akhir lulus. Dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.indicators.test.tsx src/pages/__tests__/IDXResearch.observations.test.tsx src/pages/__tests__/IDXResearch.test.tsx src/i18n/__tests__/i18n.test.ts src/lib/__tests__/idx-research.test.ts
npm run test:run
npm run build
```

Hasil: tes terkait **304 passed** (5 file); frontend penuh **1108 passed**
(95 file); build produksi lulus. Warning existing Vite configLoader dan chunk
>500 kB tetap muncul; catatan efisiensi environment Vitest bukan kegagalan tes.

Browser memakai build produksi dan server HTTP sintetis khusus loopback
`127.0.0.1:18977`, tanpa impor backend atau konfigurasi akun/provider.
Locale Indonesia, desktop 1280 dan mobile 390: MACD -0,0001, histogram 0,
Bollinger negatif dan rata-rata volume sekitar 1.23e100 tampil; seluruh sel
indikator tidak overflow, dan `innerWidth == documentElement.scrollWidth`.
BBCA mempunyai 500 bar sintetis; TLKM satu bar dengan struktur indikator null
menampilkan pesan tidak tersedia sambil mempertahankan chart; BBRI unavailable
menampilkan status kegagalan tanpa panel indikator. Log error browser kosong.

Ini verifikasi UI lokal sintetis. Backend, loader, provenance, rumus indikator
dan dependensi tidak berubah. Backend penuh/safety, provider nyata, CLI/MCP
eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh serta
RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance fokus riset pribadi,
Index Alpha ditunda dan backtest IDX nonaktif. Tidak membaca token, membuat
akun, membeli paket atau menjalankan order broker; tanpa staging/commit.

Pemeriksaan akhir: **161 tautan lokal/anchor** pada enam dokumen, UTF-8 strict,
whitespace 19 file slice dan `git diff --check` lulus. Pemeriksa anchor awal
sempat menandai heading emoji README karena algoritme trim yang keliru;
setelah diperbaiki, tidak ada tautan rusak dan tidak ada perubahan tautan existing.
Dari baseline 3.188 file, hanya **18 file existing** slice berubah dan **1 file
tes baru** ditambahkan; **3.170 file lain identik**, tanpa file hilang. Index Git
identik dengan awal sesi. Warning normalisasi LF/CRLF existing tetap tercatat.
Tab QA ditutup, viewport direset, identitas proses server QA diperiksa sebelum
dihentikan dan port 18977 tidak lagi listening.


## DATA-03 — penolakan nilai kompleks

Slice lokal **2026-11-03, Asia/Jakarta** memperketat kontrak observasi real pada
`src/tools/idx_research_tool.py`. Scalar kompleks Python, NumPy complex64 dan
complex128, termasuk bagian imajiner nol, ditolak sebelum perbandingan OHLC,
konversi float dan pemotongan lookback. Kolom kompleks native juga ditolak.
Harga memakai kode `price_values`; volume tersedia memakai `volume_values`.
Volume null tetap missing. Tidak mengambil bagian real, mengubah harga, atau
menambah rumus, request, dependency maupun aturan pasar.

Bukti awal: 32 kasus regresi menghasilkan **16 failed, 16 passed**. Nilai
kompleks NumPy tertentu lolos sebagai `ok`, HTTP mengubah volume menjadi real
(disertai `ComplexWarning`), dan CLI keluar 0. Sesudah guard diterapkan, 34 kasus
kompleks lulus ketika warning tersebut dijadikan error. Fixture sintetis meliputi
lima kolom OHLCV sebelum tail, tiga tipe scalar, bagian imajiner nol/nonzero,
kolom complex128, frame tidak dimutasi, sanitasi log, HTTP parsial dan CLI exit 2.
Kontrol real integer/float/nullable, nol/null volume serta histori pendek pada
suite kualitas tetap lulus. Perubahan berlaku pada tool bersama API/agent/MCP/CLI;
UI tetap menggunakan label kode kualitas existing.

Dari root, runtime proyek dan jaringan dibatasi loopback:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py -k complex -q --allow-hosts=127.0.0.1,::1 -W error::numpy.exceptions.ComplexWarning --tb=short
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
```

Hasil: **34 passed, 87 deselected** untuk kompleks; **604 passed** pada 14 modul,
termasuk **121 kasus kualitas**; Ruff lint/format lulus. Gate format awal meminta
parentheses lambda; diperbaiki dan diperiksa ulang. Warning existing anyio/pytest,
Starlette, overflow pada fixture batas indikator dan upaya koneksi tes indikator
yang diblokir pytest-socket tetap tercatat. Tidak ada ComplexWarning pada gate akhir.

Probe permukaan CLI terpisah menjalankan modul existing lewat `runpy`, hanya
akuisisi diganti sintetis. Proses memakai environment tanpa kredensial warisan,
cwd/home/runtime sementara dan ComplexWarning sebagai error. Hasil: exit **2**,
status **partial**, BBCA ditolak `volume_values`, BBRI sehat dengan close 105,
TLKM tanpa data tetap unavailable, `backtest_enabled: false`. Stderr hanya
menyebut simbol, tahap dan tipe exception, tanpa nilai observasi mentah.

Ini perbaikan batas frame riset pribadi, bukan validasi independen payload Yahoo
atau corporate actions/kalender. Backend penuh/safety, frontend/build/browser,
provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance tetap fokus, Index Alpha
ditunda dan backtest IDX nonaktif. Tanpa membaca token, akun/pembelian/order,
staging atau commit.


## UI-01 — konsistensi ringkasan volume

Slice lokal **2026-11-03, Asia/Jakarta** melanjutkan UI-01 melalui panel existing.
`frontend/src/pages/IDXResearch.tsx` sebelumnya memeriksa keempat angka secara
individual. Empat fixture kontradiksi gagal sebelum perubahan karena angka tetap
tampil: tersedia + hilang di atas/di bawah total, tersedia melebihi total, serta
nol melebihi tersedia. Backend existing tetap membentuk hitungan konsisten;
perubahan ini menjaga batas presentasi respons yang rusak, bukan temuan data Yahoo.

`getIDXVolumeCoverage` di `frontend/src/lib/idx-research.ts` kini menjadi satu
pemilik pemeriksaan hitungan volume untuk panel. Integer aman nonnegatif diterima,
total harus positif; field invalid/hilang individual tetap unavailable dengan
field valid tetangganya dipertahankan. Di antara field valid yang tersedia,
tersedia/hilang/nol tidak boleh melebihi total dan nol tidak boleh melebihi tersedia.
Jika total, tersedia dan hilang tersedia, tersedia harus sama dengan total dikurangi
hilang. Kontradiksi membuat seluruh ringkasan unavailable. Tidak memperbaiki angka,
menghitung dari chart/lookback, memutasi respons, menambah request atau menafsirkan
likuiditas, suspensi maupun kelengkapan kalender. Total nol tetap unavailable
sesuai perilaku sebelumnya. Angka besar yang konsisten dan nol tetap ditampilkan.

Bukti: **4 failed** pada regresi komponen sebelum implementasi. Sesudahnya,
**57 tes baru** (53 helper, 4 komponen) memeriksa container, field invalid,
subset/total, safe integer, nol, nonmutasi, satu request serta hasil parsial.
Kontrol existing 11 locale dan indikator/chart tetap lulus. Dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/pages/__tests__/IDXResearch.indicators.test.tsx src/pages/__tests__/IDXResearch.observations.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts
npm run test:run
npm run build
```

Hasil: tes terkait **361 passed** (5 file), frontend penuh **1165 passed**
(95 file), build produksi lulus. Warning existing Vite configLoader/chunk >500 kB
dan saran efisiensi environment Vitest tetap muncul, tanpa kegagalan gate akhir.

Browser memakai build produksi dan server HTTP sintetis loopback
`127.0.0.1:18978`, tanpa mengimpor backend atau konfigurasi akun/provider.
Locale id: BBCA dengan total 500, tersedia 499, hilang 5 dan nol 1 menampilkan
empat "Tidak tersedia" sambil mempertahankan chart 500 bar. TLKM dengan total 1,
tersedia 1, hilang 0 dan nol 1 menampilkan angka persis; BBRI unavailable tidak
memiliki panel volume. Tidak ada console error. Lebar halaman sama dengan viewport
pada desktop 1280 dan mobile 390; screenshot mobile diperiksa. Pembukaan tab awal
sempat timeout tetapi tab yang telah terbuka dapat dipakai; percobaan tombol Tab
pada elemen nonfocusable gagal, lalu pemeriksaan memakai locator semantik yang sesuai.

Backend, provider, rumus indikator, struktur layout, terjemahan dan dependensi
tidak berubah. Backend penuh/safety, provider nyata, CLI/MCP eksternal dan
deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap
terbuka. Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda dan backtest IDX
nonaktif. Tidak membaca token, membuat akun, membeli paket atau menjalankan order
broker. Tanpa staging/commit.


Pemeriksaan akhir: **166 tautan lokal/anchor**, UTF-8 strict, whitespace dan
`git diff --check` lulus; warning normalisasi LF/CRLF existing tetap tercatat.
Dari baseline 3.189 file, hanya **9 file slice** berubah, **3.180 file lain
identik**, tanpa file baru/hilang. Index Git identik dengan awal sesi. Tab QA
ditutup, viewport direset dan proses server sintetis sesi ini dihentikan.

## DATA-03 — bentuk provenance

Slice lokal **2026-11-03, Asia/Jakarta** menjaga batas respons akuisisi pada
`src/tools/idx_research_tool.py`. Sebelumnya pemanggilan
`data.get("_provenance", {}).get(code)` terjadi sebelum batas penolakan per simbol.
Container provenance null/non-object atau respons akuisisi non-object menyebabkan
`AttributeError` yang menggugurkan tool, HTTP dan CLI. **13 regresi awal gagal**
dan mereproduksi masalah ini; kolom OHLCV duplikat juga diprobe tetapi ternyata
sudah ditolak dengan kode existing, sehingga tidak diubah.

Respons akuisisi kini wajib object/dict; bentuk lain memakai error akuisisi
terstruktur existing (`ok: false`, HTTP 400, CLI exit 2) dan warning tersanitasi.
Container `_provenance` atau entry per simbol non-object diperlakukan sebagai
deklarasi yang tidak tersedia: simbol berdata ditolak melalui
`quality_issue.code: currency_declaration`, dengan `provenance: null`.
Ini normalisasi bentuk metadata invalid, bukan penyediaan metadata pengganti.
Simbol kosong tetap `no_data_or_source_failure`; entry sehat mempertahankan
provenance, bar, indikator dan volume nol. Tidak menebak IDR dari simbol atau
atribut frame. Tidak menambah kode tahap/terjemahan/request, memutasi frame sumber,
mengubah routing, rumus indikator, provider atau dependensi.

**23 tes baru** pada `agent/tests/test_idx_research_provenance.py` mencakup
container/entry null, list, string, integer dan boolean, metadata hilang, frame
tetap utuh, sanitasi, tetangga sehat, hasil kosong, HTTP 200/400 dan CLI exit 2.
Tes kualitas existing tetap identik dengan awal sesi; modul baru menghindari
memperpanjang file tersebut. Dari root repository:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_provenance.py agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
```

Hasil akhir: **627 passed** pada 15 modul, termasuk 121 tes kualitas existing dan
23 tes baru. Ruff lint/format lulus. Pemindahan tes ke modul baru sempat menyisakan
tiga import tidak terpakai; dibuang sebelum gate akhir. Warning existing
anyio/pytest, Starlette, overflow fixture indikator dan upaya koneksi tes indikator
yang diblokir pytest-socket tetap tercatat.

Probe permukaan CLI terpisah memakai `runpy`, akuisisi sintetis, environment
minimum tanpa kredensial warisan, cwd/home/runtime sementara dan koneksi jaringan
yang ditolak. Tiga proses menghasilkan JSON valid dan exit **2**: entry BBCA
malformed → **partial**, BBRI sehat dengan close 105 dan 20 volume nol, TLKM kosong;
container provenance null → **unavailable**; respons akuisisi null → **ok: false**.
Log hanya memuat simbol/tahap/tipe exception, tanpa nilai malformed mentah.

Pemeriksaan akhir: **168 tautan lokal/anchor**, UTF-8 strict, whitespace dan
`git diff --check` lulus; warning normalisasi LF/CRLF existing tetap tercatat.
Dari baseline 3.189 file, hanya **6 file existing** berubah dan **1 file tes baru**
ditambahkan; **3.183 file lain identik**, tanpa file hilang. Index Git identik
dengan awal sesi. Pemeriksa tautan awal sempat menandai anchor emoji/HTML README;
setelah parser mendukungnya dengan benar, semua tautan lulus tanpa mengubah target.

Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan
deployment tidak diulang. DATA-03/UI-01 penuh serta RULE-01/DATA-01/RESEARCH-01
tetap terbuka. Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda dan backtest
IDX nonaktif. Tidak membaca token, membuat akun, membeli paket atau menjalankan
order broker. Tanpa staging/commit.


## DATA-03 — Bentuk diagnostik akuisisi

Slice lokal 2026-11-03 pada shared `IDXResearchTool`, dengan fixture sintetis
`agent/tests/test_idx_research_diagnostics.py`. Pemilik akuisisi tetap
`src.market_data.fetch_market_data`; API, agent, mirror MCP dan CLI memakai tool
bersama. Provider, routing, rumus indikator, frontend dan dependency tidak berubah.

Pada simbol tanpa data (frame hilang, bukan DataFrame, atau kosong), `_diagnostics`
dan entry per simbol harus berbentuk object bila tersedia. Container/entry non-object diubah menjadi
`diagnostics: null` dan warning hanya menyebut simbol yang sudah divalidasi;
nilai malformed tidak disalin ke respons/log. Metadata hilang/null tetap unknown
tanpa warning malformed. Tidak membuat source attempt, recovery atau kode kualitas
bar dari metadata diagnostik yang tidak tersedia. Object diagnostik dipertahankan
utuh; validasi isi nested, autentikasi sumber dan sanitasi producer tetap kontrak
existing, bukan kemampuan baru slice ini.

Alasan `no_data_or_source_failure`, HTTP 200 untuk envelope partial/unavailable,
dan CLI exit 2 dipertahankan. Simbol sehat tidak mengonsumsi diagnostik unavailable;
volume nol tetap tersedia. Frame dan metadata input tidak dimutasi. Semua data
kosong tetap unavailable; kegagalan metadata opsional tidak berubah menjadi
error akuisisi seluruh watchlist.

Verifikasi dari root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_diagnostics.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_diagnostics.py agent/tests/test_idx_research_provenance.py agent/tests/test_idx_research_quality.py agent/tests/test_idx_research.py agent/tests/test_mcp_new_tools.py agent/tests/test_idx_foundation.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_technical_indicator_tool.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_diagnostics.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_diagnostics.py
git diff --check
```

Sebelum fix: **18 failed, 3 passed**, termasuk `AttributeError` pada container,
`ValueError` serialisasi NaN, `TypeError` serialisasi DataFrame dan entry non-object
yang diteruskan mentah. Sesudah fix dan dua kontrol tambahan: **23 passed**;
regresi 16 modul **650 passed**. Ruff lint/format lulus. Warning existing
anyio/pytest, Starlette, overflow fixture indikator dan koneksi tes indikator
yang diblokir pytest-socket tetap tercatat; tidak ada gate akhir gagal.

Empat probe CLI subprocess sintetis memakai home/runtime sementara dan environment
terbatas, tanpa provider/akun nyata: container malformed dan entry NaN menghasilkan
partial dengan diagnostics null; object valid mempertahankan dua attempt berurutan;
semua data kosong dengan container malformed menghasilkan unavailable. Semuanya
exit 2, JSON terbaca, backtest false, simbol sehat tetap close 105 dan marker
malformed tidak muncul di stdout/stderr.

Pemeriksaan akhir: 165 tautan lokal/anchor, UTF-8 strict, whitespace dan
`git diff --check` lulus (warning normalisasi LF/CRLF existing tetap ada).
Dari baseline 3.190 file, enam file existing berubah dan satu modul tes baru
ditambahkan; 3.184 file lain serta index Git identik, tanpa file hilang.

UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance tetap
fokus riset pribadi; Index Alpha ditunda dan backtest IDX nonaktif. Backend penuh,
safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak
diulang. Tidak ada staging/commit.

## DATA-03 — serialisasi diagnostik akuisisi

Slice lokal **2026-11-03, Asia/Jakarta** melanjutkan batas diagnostik pada
`src/tools/idx_research_tool.py`. Pemeriksaan bentuk object sebelumnya belum
melindungi serialisasi watchlist dari nilai nested non-JSON. **18 regresi awal
gagal** pada tool/HTTP/CLI: NaN/Infinity menghasilkan `ValueError`, DataFrame,
set dan key tuple menghasilkan `TypeError`, sedangkan siklus menghasilkan
`ValueError: Circular reference detected`.

Object diagnostik simbol tanpa data kini diperiksa memakai serializer JSON strict
yang sama sebelum dipasang ke item. Bila serialisasi menolak nilai/struktur atau
melewati batas rekursi, seluruh diagnostik simbol tersebut menjadi `null` dengan
warning yang hanya menyebut simbol tervalidasi. Tidak melakukan stringifikasi,
mengganti nilai nested, atau menyalin pesan exception/nilai mentah ke respons/log.
Alasan tetap `no_data_or_source_failure`; bukan penolakan kualitas bar. Metadata
absent/null tetap unknown tanpa warning. Object valid, urutan attempt, recovery,
field tambahan yang serializable, dan frame input dipertahankan tanpa mutasi.
Simbol sehat tidak mengonsumsi diagnostik unavailable. Semua simbol kosong tetap
menghasilkan envelope `ok: true`, status `unavailable`.

**23 tes tambahan** di `agent/tests/test_idx_research_diagnostics.py` mencakup
tujuh bentuk nested pada tool, HTTP dan CLI, kontrol semua kosong, serta diagnostik
yang tidak dipakai simbol sehat. Fixture nesting awal memakai batas rekursi Python
dan menghasilkan tiga kegagalan assertion karena serializer C Python 3.12 masih
menerimanya; fixture diperbaiki menjadi 10.000 tingkat agar benar-benar menguji
kegagalan serializer. Tidak menambahkan batas kedalaman produk yang arbitrer.

Dari root, interpreter proyek dan pembatasan jaringan loopback:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_diagnostics.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_diagnostics.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_diagnostics.py
```

Hasil: **46 tes diagnostik lulus**. Perintah regresi 16 modul pada bagian
sebelumnya dijalankan ulang sesudah perubahan terakhir: **673 passed**. Ruff
lint/format lulus. Warning existing anyio/pytest, Starlette, overflow fixture
indikator dan koneksi tes indikator yang diblokir pytest-socket tetap tercatat.

Empat probe CLI subprocess terpisah memakai `runpy`, akuisisi sintetis,
environment minimum tanpa kredensial warisan, home/runtime/cwd sementara dan
koneksi jaringan diblokir. NaN nested dan siklus menghasilkan `partial` dengan
diagnostics null; object valid mempertahankan attempt Yahoo lalu yfinance; semua
data kosong menghasilkan `unavailable`. Semua exit **2**, JSON valid,
`backtest_enabled: false`; simbol sehat mempertahankan close 105 dan 20 volume nol.

Ini guard serialisasi metadata opsional, bukan validasi schema/semantik nested,
autentikasi sumber atau sanitasi isi object valid. Batas provenance existing tidak
diperluas. Provider/routing/rumus indikator/frontend/dependency tidak berubah.
Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan
deployment tidak diulang. UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01
tetap terbuka. Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda dan backtest
IDX nonaktif. Tidak membaca token, membuat akun, membeli paket, menjalankan order,
staging atau commit.

Pemeriksaan akhir: 167 path tautan lokal dan kedua anchor baru, UTF-8 strict,
whitespace serta `git diff --check` lulus (warning LF/CRLF existing tetap ada).
Tujuh file existing berubah; 3.184 file lain dan index Git identik dengan awal
sesi. Tidak ada file baru/hilang.

## DATA-03 — serialisasi provenance

Slice lokal **2026-11-03, Asia/Jakarta** melanjutkan batas metadata pada shared
`src/tools/idx_research_tool.py`. Pemeriksaan bentuk provenance sebelumnya
menerima object dengan nilai nested non-JSON; object diteruskan ke item dan
read identity indikator. Serialisasi akhir lalu menggugurkan seluruh watchlist,
termasuk simbol sehat. **28 regresi awal gagal**, dengan `ValueError` untuk
NaN/Infinity atau siklus, `TypeError` untuk set/DataFrame/key tuple, dan
`RecursionError` untuk nesting ekstrem.

Provenance per simbol kini diperiksa memakai `json.dumps(..., allow_nan=False)`
sebelum dipasang ke item atau diteruskan ke perhitungan. Bila serializer menolak
object atau batas rekursinya terlampaui, provenance menjadi `null` dan warning
hanya menyebut simbol tervalidasi. Tidak menyalin nilai atau pesan exception
mentah, mengubah nilai nested, menebak metadata dari frame, atau mencoba
memulihkan sebagian deklarasi. Simbol berdata memakai penolakan existing
`invalid_data_or_metadata` / `quality_issue.code: currency_declaration`;
ini gate deklarasi pertama, bukan diagnosis bahwa nilai currency pasti salah.
Simbol kosong tetap `no_data_or_source_failure` tanpa kode kualitas bar.
Object valid, nilai null/nol nested, urutan attempt, metadata hilang/null,
hasil sehat, frame sumber dan object input dipertahankan.

**38 tes tambahan** pada `agent/tests/test_idx_research_provenance.py` menguji
tujuh bentuk nested invalid melalui tool, HTTP dan CLI, data tersedia/kosong,
semua simbol kosong, sanitasi, nonmutasi, object valid serta read identity.
HTTP tetap 200 untuk envelope partial/unavailable, CLI tetap exit 2; seluruh
simbol sehat tetap exit 0. Tidak mengubah schema API atau exposure MCP read-only.

Perintah dari root dengan interpreter proyek:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_provenance.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
git diff --check
```

Regresi 16 modul pada bagian serialisasi diagnostik dijalankan ulang:
**711 passed**, termasuk **61 tes provenance**. Ruff lint/format lulus setelah
satu penyesuaian format tes. Warning existing anyio/pytest, Starlette, overflow
fixture indikator dan upaya koneksi tes indikator yang diblokir pytest-socket
tetap tercatat. Tidak ada dependency yang dipasang atau diubah.

Empat probe CLI subprocess terpisah memakai `runpy`, akuisisi sintetis,
environment minimum tanpa kredensial warisan, cwd/home/runtime sementara dan
koneksi jaringan diblokir. NaN nested dan siklus menghasilkan **partial**, exit
**2**, provenance null dan gate currency; BBRI sehat tetap close 105 dan 20 bar
volume nol. Semua frame kosong menghasilkan **unavailable**, exit **2**.
Provenance valid menghasilkan **ok**, exit **0**, dengan urutan attempt Yahoo
lalu yfinance tetap utuh. JSON valid pada keempat probe, marker invalid tidak
muncul di stdout/stderr dan `backtest_enabled: false` dipertahankan.

Ini perlindungan serialisasi, bukan validasi schema/semantik nested, autentikasi
atau sanitasi isi object valid, dan bukan penerimaan provider. Provider, routing,
indikator, frontend serta dependency tidak berubah. Backend penuh/safety,
frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak
diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka.
Yahoo/yfinance fokus pribadi; Index Alpha ditunda, backtest IDX nonaktif.
Tidak membaca token, membuat akun, membeli paket, menjalankan order, staging
atau commit. RTK.md tetap tidak ditemukan.

Pemeriksaan akhir: **118 path tautan lokal** pada status/backlog/panduan dan
pengantar kedua README, **dua anchor baru**, UTF-8 strict, whitespace serta
`git diff --check` lulus; warning normalisasi LF/CRLF existing tetap ada.
Hanya **tujuh file existing** berubah dari snapshot sesi, **3.184 file lain**
dan index Git identik, tanpa file baru/hilang. Run provenance terakhir sesudah
format menghasilkan **61 passed**. Tidak ada staging/commit.

## UI-01 — upaya sebelum fallback berhasil

Slice lokal **2026-11-03, Asia/Jakarta** melengkapi pengungkapan provenance pada
hasil sehat. `src/market_data.py` sudah memasukkan `attempts` ke provenance IDX,
tetapi panel sehat hanya menampilkan pemberitahuan fallback. Regresi awal gagal:
`Unable to find an accessible element with the role "group" and name "Attempts before fallback data"`.

Panel baru muncul hanya untuk simbol sehat dengan `fallback_used === true`.
Daftar membaca `provenance.attempts`, bukan diagnostik simbol kosong, tanpa
mengurutkan ulang, menyimpulkan sumber sukses dari attempt, atau mengambil data
lagi. Sumber aktual tetap ditampilkan terpisah. Metadata absent/null/non-array
atau array kosong menampilkan detail tidak tersedia. Entry invalid serta sumber
atau alasan asing mendapat label netral tanpa menyalin nilai mentah. Flag
truthy selain boolean true tidak dianggap deklarasi fallback.

`SourceAttempts` dipakai bersama panel kegagalan akuisisi existing; daftar
sumber/alasan dan pemetaan terjemahan tetap satu pemilik. Panel sehat memakai
judul/keterangan sendiri agar upaya gagal sebelumnya tidak dibaca sebagai
kegagalan data yang sedang ditampilkan. Keterangan menyatakan Yahoo/yfinance
adalah dua transport satu vendor, bukan konfirmasi independen atau bukti
kelengkapan kalender. Dua key diterjemahkan pada seluruh 11 locale.

**23 tes tambahan** menguji urutan sumber, pemisahan provenance/diagnostik,
nonmutasi, satu request saja, tetangga unavailable, metadata malformed, entry
asing, flag eksplisit dan rendering seluruh locale. Perintah dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts
npm run test:run
npm run test:run -- --maxWorkers=2
npm run build
```

Run terkait: **352 passed**. Build lulus; warning native config Vite dan chunk
lebih besar dari 500 kB tetap ada. Run penuh pertama: **1187 passed, 1 failed**
karena tes existing tabel 500 bar melebihi timeout 5000 ms, saat build dijalankan
bersamaan. Tidak ada assertion atau timeout yang diubah; suite diulang dengan
dua worker untuk membatasi kontensi lokal.

Browser melalui Playwright bawaan runtime memeriksa build di server QA loopback
sintetis terisolasi: locale id, desktop 1280 dan mobile 390. Daftar tiga alasan
sesuai urutan backend; chart tetap tampil, entry asing netral, perpindahan ke
simbol kosong menampilkan panel akuisisi existing. `innerWidth == scrollWidth`
pada kedua viewport dan tidak ada page error. Screenshot panel diperiksa visual;
semua data sintetis, tanpa provider atau akun. Playwright CLI tidak tersedia
lokal; percobaan kontrol browser in-app timeout. Runtime Playwright digunakan
langsung tanpa instalasi dependency. Artefak QA berada di direktori sementara
`idx-fallback-ui-j4gcn5aa`, di luar repository.

Backend/provider/routing/rumus/dependency tidak berubah. Backend penuh/safety,
provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh,
RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance tetap fokus pribadi;
Index Alpha ditunda dan backtest IDX nonaktif. RTK.md tetap tidak ditemukan.
Tanpa token, akun, pembelian, order broker, staging atau commit.

Run penuh akhir `npm run test:run -- --maxWorkers=2`: **95 file, 1188 passed**
(159,65 detik), termasuk tes tabel 500 bar yang timeout pada run pertama.
Tidak ada gate akhir gagal. Server QA milik sesi ini telah dihentikan.

Pemeriksaan cakupan akhir: **19 file existing** berubah dari snapshot awal,
**3.172 file lain** serta index Git identik; tidak ada file baru/hilang.
Sebanyak **117 path tautan lokal**, dua referensi anchor baru, UTF-8 strict,
whitespace dan `git diff --check` lulus. Warning normalisasi LF/CRLF existing
pada locale tetap tercatat. Tidak ada staging/commit.


## DATA-03 — bentuk kolom observasi

Slice lokal **2026-11-03, Asia/Jakarta** memperjelas kontrak frame pada shared
`src/tools/idx_research_tool.py`. Pemeriksaan sebelumnya sudah menolak kolom
duplikat melalui error pandas yang tertangkap. Celah yang direproduksi adalah
MultiIndex dengan OHLCV pada level pertama: validasi harga berjalan pada
DataFrame satu kolom, lalu kegagalan dilaporkan sebagai `volume_values`.
Regresi awal: **1 failed, 16 passed**, dengan assertion aktual
`{'code': 'volume_values'} != {'code': 'price_values'}` serta FutureWarning
konversi Series menjadi int dari validator OHLC existing.

Gate harga kini menolak MultiIndex dan mensyaratkan tepat satu kemunculan setiap
open/high/low/close; gate volume mensyaratkan tepat satu volume. Semua pemeriksaan
berada sebelum pembacaan nilai pada tahap masing-masing dan sebelum tail
lookback. Tidak meratakan level simbol, memilih kolom pertama/terakhir,
mengubah frame, atau memperluas penangkapan exception. Penolakan memakai
`invalid_data_or_metadata` dan kode kualitas existing dengan warning tersanitasi.
Kolom tambahan yang tidak dipakai, termasuk duplikatnya, tetap diperbolehkan.

Grounding: gate harga/volume dan failure boundary pada tool bersama; HTTP di
`src/api/idx_research_routes.py` dan CLI `main()` memakai kelas yang sama, MCP
memakai mirror di `mcp_server.py`. Provider, loader, routing, rumus, UI dan
dependensi dipertahankan. Invariant: simbol sehat tetap tersedia, satu akuisisi,
tidak ada perbaikan data implisit, backtest tetap false.

**19 tes baru** dalam `agent/tests/test_idx_research_quality.py` mencakup lima
kolom wajib yang duplikat identik/berbeda, kedua urutan level MultiIndex,
nonmutasi/sanitasi, kontrol duplikat kolom tambahan, HTTP partial dan CLI exit 2.
Sesudah implementasi **140 tes kualitas lulus**. Regresi 16 modul yang tercantum
pada bagian bentuk diagnostik akuisisi dijalankan ulang: **730 passed**.

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research_quality.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_quality.py
git diff --check
```

Ruff lint/format lulus setelah dua assertion tes dirapikan. Warning existing
anyio/pytest, Starlette, overflow fixture indikator dan koneksi tes indikator
yang diblokir pytest-socket tetap tercatat. Empat probe CLI subprocess melalui
`runpy` memakai data sintetis, cwd/home/runtime sementara, environment minimum
tanpa kredensial warisan dan koneksi jaringan diblokir. Kolom bertingkat dan
duplikat volume menghasilkan partial/exit 2 dengan peer sehat; semua kolom
bertingkat menghasilkan unavailable/exit 2; duplikat kolom tambahan menghasilkan
ok/exit 0. JSON valid, satu akuisisi, nonmutasi dan backtest false diperiksa.
Harness awal salah mem-patch modul yang dieksekusi ulang oleh runpy; percobaan
jaringan diblokir, lalu patch diperbaiki ke `src.market_data` dan seluruh probe
lulus. Ini koreksi harness, bukan perubahan provider atau routing.

Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan
deployment tidak diulang. DATA-03/UI-01 penuh, RULE-01/DATA-01/RESEARCH-01 tetap
terbuka. Yahoo/yfinance fokus pribadi, Index Alpha ditunda dan backtest IDX
nonaktif. RTK.md masih tidak ditemukan; tidak membaca token, membuat akun,
membeli paket, menjalankan order, staging atau commit.

Pemeriksaan akhir pada status/backlog/panduan pribadi dan 80 baris pengantar kedua
README: **124 tautan lokal**, **68 anchor**, UTF-8 strict dan whitespace lulus;
`git diff --check` lulus dengan warning LF/CRLF existing. Dibanding snapshot awal
sesi, **tujuh file existing berubah**, **3.184 file lain dan index Git identik**,
tanpa file baru/hilang. Ketujuh file adalah tool bersama, tes kualitas, status,
backlog, panduan pribadi serta kedua README; seluruh file frontend tetap utuh.

## UI-01 — identitas observasi analisis

Slice lokal **2026-11-03, Asia/Jakarta** menampilkan
`analysis.read_identity.dataset_fingerprint` pada panel simbol sehat. Pemilik
fingerprint tetap `_dataset_fingerprint` di `src/tools/technical_indicator_tool.py`:
SHA-256 atas interval, label tanggal, close dan volume input indikator. UI tidak
menghitung hash, mengambil data lagi, mengganti identitas dari chart, memotong
atau mengubah kapitalisasi nilai backend.

Kriteria slice: fingerprint 64 karakter hex lowercase ditampilkan utuh dan dapat
diseleksi untuk disalin; nilai hilang, null, nonteks, hex invalid, panjang salah,
whitespace atau format asing diberi label tidak tersedia. Metadata `read_identity`
hilang/malformed tidak menggugurkan chart/indikator. Simbol unavailable tidak
menampilkan fingerprint. Teks menjelaskan cakupan input dan bahwa ini bukan hash
seluruh field OHLCV atau bukti keaslian, akurasi maupun kelengkapan provider.
Dua key diterjemahkan pada 11 locale. Teks hash memakai arah LTR dan wrap agar
identitas tetap dapat dibaca pada mobile maupun locale RTL.

Regresi awal sebelum implementasi: **32 failed, 1 passed, 177 skipped** pada run
terfilter `fingerprint|read identity`; kegagalan `Unable to find an element with
the text: Analysis observation fingerprint (SHA-256)` (atau key locale yang belum
tersedia). Satu tes existing yang cocok filter tetap lulus. Sebanyak **32 tes
baru** mencakup nilai utuh/nonmutasi/satu request, 15 nilai malformed, lima bentuk
read identity dan 11 locale. Tidak mengubah tes atau timeout existing.

Perintah regresi terkait dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/pages/__tests__/IDXResearch.observations.test.tsx src/pages/__tests__/IDXResearch.indicators.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts src/lib/__tests__/api.test.ts --maxWorkers=2
```

Hasil: **428 passed (6 file)**. `npm run test:run -- --maxWorkers=2`:
**95 file, 1220 passed** (165,37 detik); `npm run build`: lulus. Warning existing
Vite configLoader dan ukuran chunk tetap muncul, tanpa perubahan dependency.

Browser headless Chromium memakai Playwright bundled dan respons sintetis pada
server loopback sementara yang menyajikan `frontend/dist`; tidak memanggil
provider/backend nyata. Locale id pada desktop 1280/mobile 390 mempertahankan
fingerprint utuh, menampilkan tetangga malformed sebagai tidak tersedia, serta
menyembunyikan identitas pada simbol gagal. Tiap skenario hanya satu request
riset, tanpa page error; scrollWidth sama dengan innerWidth (1280/390). Screenshot
mobile diperiksa: hash membungkus di dalam panel. Server QA telah dihentikan.
Helper `with_server.py` sempat gagal startup Windows dalam 30 detik; server
sintetis langsung berhasil dan pemeriksaan browser selesai lulus. Ini kegagalan
harness awal, bukan tes runtime aplikasi atau provider.

Backend, provider/routing, rumus indikator dan dependency tidak berubah. Backend
penuh/safety, provider nyata, MCP eksternal dan deployment tidak diulang.
UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Fokus tetap
Yahoo/yfinance untuk riset pribadi, Index Alpha ditunda dan backtest IDX nonaktif.
Pemeriksaan akhir: 173 tautan/path lokal dan 79 referensi anchor pada lima dokumen
yang diubah lulus, termasuk anchor HTML existing; UTF-8, whitespace dan
`git diff --check` lulus. Pemeriksa anchor awal hanya mengenali heading Markdown
dan menolak anchor HTML existing README; dukungan anchor HTML ditambahkan pada
skrip QA lalu pemeriksaan ulang lulus, tanpa mengubah tautan proyek.
Sebanyak 18 file existing berubah pada sesi ini, 3173 file lain dan index Git
identik dengan baseline awal; tidak ada file baru/hilang. Tidak ada staging atau commit.

## DATA-03 — konsistensi deklarasi identitas

Slice lokal **2026-11-03, Asia/Jakarta** memeriksa deklarasi identitas pada
provenance setelah gate currency dan sebelum timezone di shared
`src/tools/idx_research_tool.py`. Pemilik akuisisi `src/market_data.py` sudah
menyertakan `symbol`, `market` dan `exchange` untuk IDX; sebelumnya deklarasi
yang bertentangan tetap diterima selama metadata currency/timezone lainnya valid.

Field yang hadir wajib cocok persis: `symbol` dengan simbol kanonik permintaan,
`market` dengan hasil classifier existing `_detect_market`, dan `exchange` dengan
IDX. Tidak ada classifier baru atau normalisasi deklarasi sumber. Field absen
tetap kompatibel dengan observasi lama; null, tipe invalid, string kosong,
kapitalisasi berbeda dan identitas instrumen/venue lain ditolak per simbol.
Kode `instrument_identity` muncul melalui tool/HTTP/CLI dan mirror MCP yang sama.
UI existing memperlakukan kode baru sebagai tahap belum tersedia; label khusus
UI belum ditambahkan. Identitas request kanonik tetap berasal dari jalur existing.

Respons penolakan mempertahankan `reason=invalid_data_or_metadata`, tanpa bars
atau analysis. Log dan quality issue tidak menyalin nilai deklarasi atau pesan
exception mentah. Object provenance JSON-valid tetap dikembalikan apa adanya
untuk inspeksi, termasuk deklarasi yang bertentangan; input tidak dimutasi.
Simbol tanpa data mempertahankan alasan akuisisi existing tanpa quality issue
baru. Pemeriksaan konsistensi ini bukan autentikasi sumber, verifikasi bahwa
harga benar-benar milik instrumen tersebut, penerimaan universe atau tradability.

Regresi awal: **26 failed, 70 passed**, dengan kegagalan `assert 'ok' ==
'unavailable'` atau `assert 'ok' == 'partial'`: deklarasi salah masih diterima.
Sesudah implementasi: **96 passed** pada modul provenance. Sebanyak **35 tes
baru** mencakup tujuh nilai invalid pada tiga field, delapan kombinasi deklarasi
absen/cocok, HTTP parsial/satu akuisisi, CLI exit 2, sanitasi log, nonmutasi dan
alasan akuisisi kosong. Tes/prosedur existing tidak diubah.

Perintah regresi dari root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_research.py agent/tests/test_idx_research_quality.py agent/tests/test_idx_research_provenance.py agent/tests/test_idx_research_diagnostics.py agent/tests/test_idx_foundation.py agent/tests/test_idx_reference.py agent/tests/test_idx_symbol_search.py agent/tests/test_market_identity_parity.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_mcp_new_tools.py -q --allow-hosts=127.0.0.1,::1 --tb=short
.venv/idx312/Scripts/python.exe -m ruff check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
.venv/idx312/Scripts/python.exe -m ruff format --check agent/src/tools/idx_research_tool.py agent/tests/test_idx_research_provenance.py
```

Hasil: **755 passed (16 modul)**, Ruff lint/format lulus. Dua warning deprecation
anyio/Starlette dan empat warning aritmetika fixture ekstrem existing tetap muncul.
Empat probe CLI subprocess memakai data sintetis, cwd/home/runtime temporary,
environment minimum tanpa kredensial warisan dan koneksi jaringan ditolak:
`partial`/exit 2, `unavailable`/exit 2, identitas cocok `ok`/exit 0, serta field
identitas absen `ok`/exit 0. Masing-masing satu akuisisi, frame tidak dimutasi dan
`backtest_enabled=false`. Probe berada di temporary `idx-identity-probe-efa_o5um`,
bukan fixture data provider di repository.

Provider, loader, routing, rumus, frontend dan dependency tidak berubah. Backend
penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment
tidak diulang. DATA-03/UI-01 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka.
Fokus Yahoo/yfinance pribadi, Index Alpha ditunda dan backtest IDX tetap nonaktif.
RTK.md tidak ditemukan; tidak membaca token, membuat akun, membeli paket,
menjalankan order broker, staging atau commit.

Pemeriksaan akhir: **126 tautan lokal**, **70 anchor**, UTF-8 strict, whitespace
dan `git diff --check` lulus. Tujuh file existing mendapat tambahan; seluruh
baris sebelumnya dipertahankan. Sebanyak **3.184 file lain dan index Git identik**
dengan snapshot awal sesi, tanpa file baru/hilang. Warning LF/CRLF existing
tidak mengubah hasil pemeriksaan whitespace.

## UI-01 — label deklarasi identitas instrumen

Slice lokal **2026-11-03, Asia/Jakarta** melengkapi presentasi kode
`instrument_identity` dari slice DATA-03 sebelumnya. Peta `qualityStageKeys`
di `frontend/src/pages/IDXResearch.tsx` memakai key
`idxResearch.qualityStages.instrument_identity` pada seluruh 11 locale.
Label id adalah **Deklarasi identitas instrumen**. Ini menggantikan pesan tahap
belum tersedia untuk kode tersebut; catatan keterbatasan UI pada slice backend
sebelumnya merupakan hasil sebelum follow-up ini.

Kriteria penerimaan: label tampil saat simbol ditolak melalui
`reason=invalid_data_or_metadata`; batas tahap pertama yang gagal tetap terlihat.
Kode hilang/asing tetap memakai pesan netral, tanpa menampilkan kode mentah.
Simbol ditolak tidak mendapat chart; pengguna dapat kembali ke chart simbol
sehat tanpa akuisisi baru. Respons tidak dimutasi. UI tidak memeriksa ulang
identitas atau menyimpulkan bahwa provider terautentikasi.

Sebelas tes render baru memakai expected label literal per locale dan memeriksa
pergantian simbol, satu request serta nonmutasi. Sebelum implementasi,
**11 failed, 210 skipped**: `Unable to find an element with the text: Failed
validation stage: Instrument identity declaration` pada kasus en; locale lain
gagal pada label masing-masing. UI masih menampilkan pesan tahap belum tersedia.
Tes existing untuk kode hilang/asing, tahap lain serta akuisisi kosong tetap utuh.

Perintah dari `frontend/`:

```powershell
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx -t 'explains instrument identity rejection' --maxWorkers=2
npm run test:run -- src/pages/__tests__/IDXResearch.test.tsx src/pages/__tests__/IDXResearch.indicators.test.tsx src/pages/__tests__/IDXResearch.observations.test.tsx src/lib/__tests__/idx-research.test.ts src/i18n/__tests__/i18n.test.ts --maxWorkers=2
npm run test:run -- --maxWorkers=2
npm run build
```

Hasil sesudah implementasi: tes terkait **427 passed (5 file)**; frontend penuh
**1231 passed (95 file)** dalam 184,55 detik; build lulus. Warning existing
configLoader Vite dan ukuran chunk tetap muncul; dependency tidak berubah.

Browser headless Chromium melalui runtime Playwright bundled memakai build
produksi dan respons sintetis pada server loopback sementara, tanpa provider
atau backend nyata. Locale id desktop 1280/mobile 390 menampilkan label identitas,
pesan netral untuk kode asing dan chart sehat saat kembali. Tiap skenario hanya
satu request riset, tanpa page error; scrollWidth sama dengan innerWidth
(1280/390). Screenshot mobile diperiksa dan teks membungkus di dalam panel.
Server QA ditutup melalui shutdown/finally. Script, log dan screenshot berada
di temporary `idx-ui-identity-qmj5m_c1`, di luar source tree.

Backend/provider/loader/routing/rumus/dependensi tidak berubah. Backend penuh/
safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang.
UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance
tetap fokus riset pribadi, Index Alpha ditunda dan backtest IDX nonaktif.
Tidak membaca token, membuat akun, membeli paket atau menjalankan order broker.
Tidak ada reset, staging atau commit.

Pemeriksaan akhir: 179 tautan lokal dan 85 anchor pada lima dokumen, UTF-8
strict, whitespace serta `git diff --check` lulus. Sebanyak 18 file existing
mendapat tambahan; seluruh baris baseline dipertahankan. Sebanyak 3173 file
lain serta index Git identik dengan snapshot awal, tanpa file baru/hilang.


## DEV-START-01 — entry point file dan modul

Verifikasi 2026-11-04 WIB. Kegagalan asli direproduksi dengan perintah
`<python-proyek> agent/api_server.py` tanpa argumen, dari salinan source
terkontrol: exit 1, `RuntimeError: register_runs_routes: api_server module not
in sys.modules; ensure api_server is imported before calling this function`.
Regresi sebelum perbaikan: **8 failed, 1 passed**; CLI resmi menjadi kontrol
lulus. Impor kedua nama juga menghasilkan `duplicate API host modules`.

Pemilik tetap `agent/api_server.py`: sebelum route registration, assembler
mendaftarkan `api_server` dan `agent.api_server` dalam `sys.modules` ke module
yang sama, termasuk saat berjalan sebagai `__main__`. Tidak ada assembler baru,
perubahan guard, auth, preflight, scheduler atau lifespan. CLI legacy dan desktop
masih mengimpor `api_server.serve_main`. Tes mount frontend sebelumnya tidak
diubah.

`agent/tests/test_api_entrypoints.py` menyalin source/package data ke temporary,
memakai environment minimum dan home/appdata/runtime terpisah, serta memblokir
socket connect di subprocess. Sembilan kasus mencakup file langsung, kedua
bentuk `-m`, CLI resmi, kedua urutan import, dan app yang diteruskan ke uvicorn.
Stub uvicorn hanya dipakai pada tes identitas; probe HTTP/browser berikutnya
menjalankan uvicorn serta lifespan asli tanpa override. Module `agent.api_server`
memerlukan checkout root dan `agent/` pada import path; `-m api_server`
memerlukan `agent/` pada import path atau paket terpasang.

Perintah regresi dari root salinan terisolasi, interpreter proyek Python 3.12.13:

```powershell
<python-proyek> -m pytest agent/tests/test_api_entrypoints.py agent/tests/test_serve_bind.py agent/tests/test_preflight.py agent/tests/test_scheduling_lifespan_owner.py agent/tests/test_spa_deep_link.py agent/tests/test_security_auth_api.py agent/tests/test_auth_precedence.py -q --allow-hosts=127.0.0.1,::1
<python-proyek> -m ruff check agent/api_server.py agent/tests/test_api_entrypoints.py
<python-proyek> -m ruff format --check agent/tests/test_api_entrypoints.py
```

Hasil akhir **129 passed, 2 warnings**, 80,91 detik; Ruff lint/format lulus.
Warnings existing anyio/pytest dan Starlette/httpx tetap ada. Dua run sementara
sebelumnya mengungkap kesalahan harness QA: filter salinan terlalu luas sehingga
paket source `src.memory` hilang (dua collection errors); setelah salinan
koreksi, assertion baru mengira `router.lifespan_context` tetap identik dengan
fungsi asli (5 failed/124 passed), padahal FastAPI menggabungkan lifespan router.
Assertion dikoreksi menjadi identitas host/app/fungsi antarnama; tes lifecycle
existing tetap lulus. Guard/assertion keamanan existing tidak dilonggarkan.

Probe nyata menggunakan source/build frontend existing di
`<temp>/idx-devstart-rvtpg5g8/project`, environment minimum,
home/appdata/runtime baru, cache data/scheduler/channel auto-start nonaktif dan
key auth sintetis khusus QA. Perintah asli:

```powershell
<python-proyek> agent/api_server.py --host 127.0.0.1 --port <port-sementara>
```

- Assembler, lifespan/preflight, auth dan static mount produksi asli berjalan.
  `/health` 200, schema dengan key QA 200, schema tanpa key 401; request riset
  key hilang/salah 401, cross-site dan Host tak tepercaya 403.
- Browser locale `id` pada viewport aktual 615 px membuka `/research/idx`,
  menyimpan key sintetis melalui Settings existing, lalu mengambil **BBCA.JK,
  60 bar, Yahoo, IDR**, tanggal observasi `2026-08-07`–`2026-11-02`.
  Tanggal akhir permintaan yang tampil adalah `2026-11-04` (default Jakarta);
  percobaan mengisi input tanggal lewat browser automation tidak tercermin
  pada hasil ini, sehingga probe ini tidak membuktikan pemilihan tanggal akhir.
  Chart tampil; tabel berisi 60 bar, unit `shares`, timezone `Asia/Jakarta`,
  adjustment `unknown`. Satu POST riset sukses tercatat; membuka tabel tidak
  mengakuisisi ulang. Tidak ada log error browser; scrollWidth == innerWidth.
- `/ready` **503** tanpa LLM; preflight OKX tetap gagal
  `SSLCertVerificationError`, TLS tidak dilewati. Log server juga memuat
  `ConnectionResetError [WinError 10054]` saat koneksi browser terputus;
  request riset tetap 200. Ini tidak menyatakan LLM atau koneksi OKX siap.
- `/system/shutdown` 200, proses exit 15 dan port tertutup. Endpoint Windows
  menghentikan proses, sehingga ini tidak membuktikan seluruh finalizer
  mendapat shutdown graceful.

Frontend source tidak berubah; build existing dipakai, suite/build frontend
belum diulang pada sesi ini. Backend penuh, safety order penuh, MCP eksternal,
Electron packaged app dan deployment belum diuji. Bukti ini khusus entry point
serta riset pribadi; tidak menutup task data/rulebook/backtest yang lebih luas.
Log dan screenshot disimpan di temporary, tanpa data akun/kredensial pribadi.


## Instalasi bersih backend — 2026-11-04

**Lulus untuk paket backend dan riset HTTP minimum; distribusi UI wheel belum
tersedia.** Environment baru dibuat di luar repository:
`<temp>/idx-devstart-rvtpg5g8/clean-venv`, Python **3.12.13**, tanpa akses
system-site-packages atau venv lama. Source terkontrol dibangun menjadi wheel
non-editable `vibe_trading_ai-0.1.18-py3-none-any.whl` (15.688.974 byte), lalu
benar-benar dipasang. Ini berbeda dari pemeriksaan startup sebelumnya yang
memakai salinan source dan interpreter/venv proyek lama.

Perintah aktual (path temporary disingkat), dari luar checkout:

```powershell
<python-proyek> -m venv <temp>/clean-venv
<clean-python> -m pip install --require-hashes -r <copy>/desktop/electron/requirements-windows-lock.txt
<clean-python> -m pip install --no-deps <copy>
<clean-python> -m pip check
<clean-vibe-trading> --version
<clean-vibe-trading> serve --help
<clean-vibe-trading-mcp> --help
<clean-python> -m src.tools.idx_research_tool --help
<clean-vibe-trading> serve --host 127.0.0.1 --port <port-sementara>
```

Lock Windows existing dibuat untuk Python 3.12; root `requirements-lock.txt`
adalah jalur lain dan tidak digabungkan dengan lock Windows. Pemasangan package
menggunakan dependency yang sudah dipasang dari lock (`--no-deps`), sedangkan
build backend memakai build isolation pip sesuai manifest. Manifest/lock/pin
tidak diubah. Environment minimum tidak meneruskan credential/provider config,
`PYTHONPATH`, atau pip config pengguna (`PIP_CONFIG_FILE` menunjuk null device).
Home/appdata/runtime sementara dipisahkan lagi dari proses startup sebelumnya;
cache data, scheduler dan channel auto-start nonaktif. Tidak ada trust/TLS mesin
yang diubah.

Hasil:

- Install lock dengan hash dan build/install wheel selesai exit 0.
  `pip check`: **No broken requirements found**.
- Import `api_server`, `mcp_server`, `cli`, dan
  `src.tools.idx_research_tool` exit 0 dari environment baru. Assertion origin
  memastikan `api_server.__file__` berada di
  `clean-venv/Lib/site-packages/api_server.py`; versi distribusi `0.1.18`.
  Tidak ada `PYTHONPATH` source saat pemeriksaan ini.
- Console CLI menampilkan `vibe-trading 0.1.18`; bantuan serve, console MCP,
  dan module riset exit 0. MCP hanya diperiksa import/help; transport/akun
  MCP eksternal tidak dijalankan.
- Console serve yang terpasang menjalankan assembler/lifespan/preflight asli.
  `/health` 200; POST `/api/research/idx` dengan key QA sintetis, satu kode
  `BBCA.JK`, lookback 60, end `2026-11-02`: **200/status ok, 60 bar**, sumber
  aktual `yahoo`, IDR, IDX, `Asia/Jakarta`, `1D`, `shares`, adjustment `unknown`,
  tanpa fallback atau konversi mata uang. JSON/provenance disimpan di temporary.
- `/ready` tetap **503** tanpa LLM; preflight OKX tetap gagal SSL. Keduanya
  tidak dilewati atau disembunyikan. `/system/shutdown` 200 dan port tertutup.
- Metadata distribusi memuat **0 file `frontend/dist`**. Server mengeluarkan
  `No frontend build found at .../site-packages/frontend/dist`; deep link
  `/research/idx` **404**. Paket backend terpasang belum merupakan distribusi
  Web UI lengkap. Source checkout dengan build frontend existing berhasil pada
  probe DEV-START-01 di atas. **DEV-PACK-01** menampung kontrak distribusi UI;
  tidak ada perubahan packaging ad hoc dalam sesi ini.

Ini verifikasi lokal Windows/Python 3.12 dengan lock Windows, bukan pengujian
semua platform, install minimum Python 3.11 dari manifest, sdist roundtrip,
frontend `npm ci` baru, Electron executable, chat LLM, broker/order, seluruh
backend, seluruh safety, seluruh frontend, atau deployment. Tidak ada akun,
credential nyata, staging atau commit. DATA-01/02/03, IDX-02, UI-01 penuh,
RESEARCH-01, RULE-01 dan BT-01/02/03 tetap mengikuti kriteria asal; backtest IDX
masih nonaktif dan Index Alpha ditunda.


## DEV-PACK-01 — distribusi Web UI Python

Kontrak distribusi lokal, 2026-11-04 WIB: source frontend tetap dimiliki
`frontend/`. Maintainer menjalankan `npm ci` dan `npm run build` sebelum
membangun wheel/sdist. Hook setuptools di `setup.py` menyalin output Vite
ke `src/api/_frontend` pada build wheel; `MANIFEST.in` menyertakan output
`frontend/dist` pada sdist agar rebuild wheel tidak memerlukan Node.
Keduanya menolak build tanpa `index.html`, dengan instruksi build yang jelas.
Hasil generated tidak ditambahkan ke source tree atau Git. Ulangi build Vite
setelah perubahan frontend; hook tidak mengklaim mendeteksi build yang usang.

`src.api.frontend.resolve_frontend_dist` menjadi satu pemilik lokasi aset
untuk `server_cli` dan middleware deep-link `helpers`. UI dalam paket dipilih
lebih dahulu, kemudian layout code-relative `frontend/dist` source/desktop.
Tidak ada pencarian checkout berdasarkan CWD, environment pribadi atau runtime
home. Instalasi editable tetap boleh dilakukan sebelum build UI; warning
backend-only existing berlaku bila build source belum tersedia. Assembler/app,
auth, lifespan, scheduler dan `VIBE_TRADING_HOME` tidak diubah. Desktop masih
memiliki salinan legacy asetnya; executable Electron belum diuji pada sesi ini.

Regresi fixture `agent/tests/test_frontend_distribution.py` membangun wheel
nyata melalui pip build isolation, memeriksa HTML/JS/font bertingkat, menghapus
source fixture dan menjalankan SPA dari isi wheel. Tes lain memeriksa penolakan
build yang kehilangan frontend, layout source/desktop/wheel, serta editable
install sebelum build UI. Tes packaging bertanda `integration` dapat mengambil
backend build setuptools melalui pip; tidak menjalankan provider atau broker.
Awalnya harness gagal karena interpreter proyek tidak memiliki pip; builder
dipindah ke venv fixture dengan pip bawaan. Setelah koreksi harness, sebelum
perbaikan runtime: **2 failed**, masing-masing karena aset hilang dan build
tanpa UI tetap berhasil. Sesudah perbaikan: **6 passed**. Gabungan awal lima
tes baru dan 129 startup/auth/SPA/entry point: **134 passed, 2 warnings**;
tes packaging akhir diulang setelah penambahan kontrol editable. Isolasi mount
di `test_serve_bind.py` tetap utuh. Ruff lint dan format file baru lulus.

**Penerimaan DEV-PACK-01:** instalasi bersih baru mencapai install → startup →
UI → riset melalui wheel terpasang. Artefak QA sesi ini berada di
`%TEMP%\idx-devpack-2e4056d2`;
bukan penggunaan ulang venv sesi DEV-START-01. Source disalin dari file publik
terlacak/untracked yang relevan, tanpa file ignored, dotenv pribadi, state lama,
node_modules atau dist existing. Frontend memakai Node 24.20.0, `npm ci
--ignore-scripts`, `npm run test:run` dan `npm run build` dari salinan tersebut;
hasilnya **1231 passed/95 file** dan build exit 0. `npm ci` melaporkan empat
temuan low severity; Vite memperingatkan chunk >500 kB dan plugin timing.
Tidak ada dependency/pin atau lock yang diubah. MANIFEST packaging berubah
untuk menyertakan UI. Harness pencetak log sempat gagal `UnicodeEncodeError`
cp1252 setelah tes frontend exit 0; encoding diperbaiki dan build dijalankan
terpisah, bukan menganggap error harness sebagai kegagalan tes frontend.

Perintah aktual, path temporary disingkat:

```powershell
<python-proyek> -m venv <temp>/clean-venv
<clean-python> -m pip install --require-hashes -r <copy>/desktop/electron/requirements-windows-lock.txt
<clean-python> -m pip wheel --no-deps --no-clean --wheel-dir <temp>/wheels <copy>
# Backend setuptools dari build isolation pip dipakai untuk perintah sdist ini:
<clean-python> setup.py sdist --dist-dir <temp>/sdists
<clean-python> -m pip wheel --no-deps --wheel-dir <temp>/roundtrip-wheels <temp>/sdists/vibe_trading_ai-0.1.18.tar.gz
<clean-python> -m pip install --no-deps <temp>/wheels/vibe_trading_ai-0.1.18-py3-none-any.whl
<clean-python> -m pip check
<clean-vibe-trading> serve --host 127.0.0.1 --port <port-sementara>
```

- Venv Python **3.12.13**, `include-system-site-packages=false`. Semua proses
  memakai environment minimum, home/appdata/runtime sementara, pip/npm config
  pengguna dinonaktifkan, cache data/scheduler/channel auto-start nonaktif.
  Tidak ada `PYTHONPATH` source pada import/startup terpasang. Sebelum startup,
  pemeriksaan nama path memastikan dotenv dan direktori legacy state tidak
  tersedia di lokasi yang akan dibaca/dimigrasi. Tidak ada secret nyata dibaca.
- Lock install, build wheel, sdist, roundtrip dan install exit 0. Wheel awal
  **18.164.620 byte**, SHA-256
  `15690826b91d4694a7e4ded732812ce8d028d2f3a9aec0a5d417d291b20cec40`.
  Seluruh **143 file UI** dibandingkan byte/hash dengan output Vite pada ketiga
  artefak. Wheel awal yang dipasang; wheel roundtrip diperiksa isinya, bukan
  dipasang lagi. Ini tidak mengklaim wheel reproducible byte-for-byte.
  `pip check`: **No broken requirements found**.
- Import API/CLI/MCP/tool riset dan UI berasal dari `clean-venv/Lib/site-packages`;
  resolver middleware dan server konsisten. Console version `0.1.18`, serve help,
  MCP help dan module riset help exit 0. MCP transport eksternal tidak dijalankan.
- Console serve asli, dari luar checkout: `/health` 200. HTML pada `/`,
  `/research/idx`, `/correlation` dan `/runs/qa-package` 200, beserta referensi
  bundle JS/CSS. Dua path terakhir memverifikasi middleware path yang berbagi
  nama dengan API, bukan hanya root static mount. Key hilang/salah 401;
  cross-site dan Host tak tepercaya 403. Auth/guard tidak dilonggarkan.
- Browser locale **id**, key sintetis khusus QA melalui Settings existing:
  **BBCA.JK, 60 bar**, sumber aktual **yahoo**, **IDR**, `1D`, `shares`,
  `Asia/Jakarta`, adjustment `unknown`. Chart, indikator dan tabel OHLCV
  `2026-08-07`–`2026-11-02` tampil. Membuka tabel tidak mengakuisisi ulang;
  satu POST riset sukses tercatat. Error log browser kosong. Input tanggal
  lewat automation tidak tercermin pada hasil: akhir permintaan tetap default
  **2026-11-04**; pemilihan tanggal akhir tidak diklaim terverifikasi.
- `/ready` **503** tanpa LLM; preflight OKX tetap gagal
  `SSLCertVerificationError: unable to get local issuer certificate`.
  Tidak ada perubahan TLS/trust. `/system/shutdown` 200, proses exit 15,
  port tertutup. Endpoint shutdown Windows tidak membuktikan semua finalizer
  mendapat shutdown graceful.

Perintah regresi memakai daftar tujuh suite DEV-START-01 di atas ditambah
`agent/tests/test_frontend_distribution.py`, dengan
`--allow-hosts=127.0.0.1,::1`. Tes packaging akhir dijalankan tersendiri setelah
kontrol editable ditambahkan. Log/manifest hash, hasil HTTP, AX browser serta
`installed-ui.jpg` dan `installed-overview.jpg` tersimpan di direktori QA.

Ini penerimaan lokal Windows/Python 3.12 untuk distribusi Web UI riset pribadi.
Backend penuh, safety penuh, platform/Python lain, chat LLM, MCP eksternal,
Electron packaged app dan deployment belum diverifikasi. Tidak ada publish,
akun, order, staging atau commit. RELEASE-01, DATA-01/02/03, IDX-02, UI-01 penuh,
RESEARCH-01, RULE-01 dan BT-01/02/03 tetap mengikuti kriteria asal; backtest IDX
nonaktif dan Index Alpha ditunda.

Integritas akhir sesi DEV-PACK-01: hanya 11 file berbeda dari baseline sesi:
`setup.py`, `MANIFEST.in`, `agent/src/api/frontend.py`,
`agent/src/api/helpers.py`, `agent/src/api/server_cli.py`,
`agent/tests/test_frontend_distribution.py`, `README.md`, `README_id.md`,
`PROJECT_STATUS.md`, `TODO.md` dan `agent/IDX_PERSONAL_RESEARCH.md`.
File lain pada inventaris baseline tetap identik; dependency manifests/locks
tidak berubah. Empat tautan/anchor lokal baru, UTF-8 dan `git diff --check`
lulus. Hash index Git sebelum/sesudah identik:
`4B8F7506E2B8D5E925201C8541FFE3ADDEAC5A4D35D07E4F92B344799E759A6C`.
Pekerjaan sebelum sesi tetap uncommitted, tanpa reset, staging atau commit.
