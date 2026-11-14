# Status Proyek — Vibe-Trading IDX Edition

Tanggal pembaruan: **2026-11-11, Asia/Jakarta**. Snapshot struktur awal: 2026-11-03. Basis analisis: commit `2ac20879`, branch lokal `feature/idx-edition`. Snapshot awal dibuat sebelum implementasi; perubahan Fase 2 tercatat di bawah.

## Kesimpulan kesiapan

**Paket lokal diperbarui, 2026-11-11 WIB:** wheel dan sdist baru memuat
profil IDX/skill terbaru serta build UI baru. Kedua wheel langsung/roundtrip
memiliki 1.662 source cocok hash, 143 aset UI cocok dan 91 skill. Instalasi
terisolasi dengan dependency existing, pip check, CLI help/version dan API/MCP
in-memory lulus; modul terbukti dari package terpasang. Frontend **1.231 passed**
(95 file) dan build lulus; regresi targeted **233 passed/2 warnings**. Run awal
timeout dan bootstrap pywin32 QA yang dikoreksi dicatat terpisah, tanpa perubahan
runtime produk/dependency. [Artefak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#paket-lokal-terbaru--2026-11-11).
Bukan integrasi provider baru, instalasi dependency bersih atau deployment.
ROE serta task penuh tetap terbuka; izin data tidak diperluas dan LLM tetap
ditunda pengguna karena biaya token.

**Follow-up upstream ROE, 2026-11-11 WIB:** petunjuk indeks bantuan Yahoo
tentang migrasi Financials ke Morningstar diperiksa terhadap dokumentasi
Morningstar baru. Definisi ROE berbeda menurut surface; belum ada pemetaan
field/versi dataset ke capture BBRI. Tidak menerima atribusi provider atau
formula dari nama vendor. [Disposisi dan input pembuka](agent/IDX_PERSONAL_RESEARCH.md#follow-up-upstream-dan-batas-pencarian-publik).
Pencarian publik increment ini ditutup menunggu bukti spesifik baru; ROE tetap
belum selesai dan revenue/EPS/saham belum dilanjutkan. QA bukti offline dan
integritas tiga dokumen lulus; tanpa perubahan runtime, tes runtime baru,
perluasan izin atau deployment. LLM tetap ditunda pengguna karena biaya token.

**Pembuktian satu field ROE BBRI, 2026-11-11 WIB:** belum selesai pada basis
provider. Bukti primer baru publikasi Juni BRI membedakan denominator rata-rata
ekuitas Tier 1 dan total ekuitas; tidak dipindahkan ke ROE B/S September atau
Yahoo. Statement interim konsolidasian September lengkap berhasil dibaca secara
terarah, tetapi formula ROE yang diperlukan belum ditemukan. Publikasi ringkas
Q3 berbeda yang ditemukan melalui listing tidak dapat diakses; lane dihentikan.
[Disposisi per field, sumber dan input pembuka](agent/IDX_PERSONAL_RESEARCH.md#pembuktian-roe-bbri--2026-11-11).
Unit/periode/scope/denominator dan waktu pembaruan Yahoo tetap unknown; raw dan
null/history dipertahankan. Comparator offline exit 0; perubahan hanya tiga
dokumen, tanpa tes runtime baru. Revenue/EPS/saham belum dilanjutkan karena
prasyarat ROE masih terbuka. Task penuh, izin tambahan dan deployment tetap
belum diterima; uji LLM nyata tetap ditunda oleh pengguna karena biaya token.

**Pencocokan issuer BRI, 2026-11-11 WIB:** bukti primer mengonfirmasi unit,
periode dan pemisahan konsolidasian/bank-only pada tabel issuer yang dibaca.
Pencocokan ROE menolak penyamaan otomatis dengan raw Yahoo; belum menerima
unit/periode provider. Tanggal release pada listing tidak menjadi timestamp
publikasi per field. Comparator offline exit 0; hanya tiga dokumen berubah,
tanpa perubahan runtime atau pengulangan tes runtime. [Sumber, halaman dan QA](agent/IDX_PERSONAL_RESEARCH.md#pencocokan-issuer-bri--2026-11-11).
BCA 403 dan statement BRI inaccessible dicatat; lane yang ditolak dihentikan.
EPS/saham, definisi metrik Yahoo, publikasi/histori dan hak tambahan tetap
memerlukan bukti. RESEARCH-01/02/03 penuh tetap terbuka; LLM masih ditunda oleh
pengguna karena biaya token. Tidak ada probe Yahoo, UI fundamental atau deployment.

**Audit semantik profil, 2026-11-11 WIB:** 56 field enam section dipetakan
hingga source Yahoo dan diverifikasi offline melalui client/registry existing.
Shaper tidak mereskalakan angka; metadata sel `fmt/longFmt`, periode dan currency
nested yang tidak dipilih hilang dari envelope. Capture lama tidak menyimpan
sel itu. Aritmetika EV/revenue konsisten secara internal, tetapi PE×EPS tidak
sama dengan currentPrice dan populasi recommendation tidak sama dengan analyst
opinions; tidak diasumsikan satu basis/waktu. Akses primer Yahoo mendapat 429,
lalu lane dihentikan. Tidak ada bug runtime baru atau metadata yang dikarang;
hanya tiga dokumen diperbarui. Audit offline exit 0; regresi targeted
**91 passed/1 warning**, termasuk MCP in-memory dan kontrol pasar lain.
[Peta field, QA dan input minimum](agent/IDX_PERSONAL_RESEARCH.md#audit-semantik-dan-metadata-profil--2026-11-11).
Unit/skala, rasio-versus-persen, periode/publikasi dan kalibrasi independen tetap
belum diterima. RESEARCH-02/03 penuh terbuka; LLM ditunda oleh pengguna karena
biaya token. Tidak ada probe profil ulang, perluasan izin atau deployment.

**Validasi angka profil, 2026-11-11 WIB:** bug offline direproduksi:
`forwardPE=true` dan revenue berupa string lolos sebagai profil IDX sukses.
Tool existing kini menolak boolean/string/container pada field numerik enam
section melalui error tersanitasi; null, nol dan angka bertanda dipertahankan.
Validasi hanya untuk IDX, tanpa perubahan transport atau kontrak pasar lain.
Regresi awal **12 failed/45 passed**, sesudah fix **91 passed/1 warning**,
Ruff lulus; nilai snapshot BBCA/BBRI sebelumnya lolos replay offline tanpa
akuisisi baru. [Bukti dan batas validasi](agent/IDX_PERSONAL_RESEARCH.md#validasi-tipe-angka-profil--2026-11-11).
Pengguna menunda uji LLM nyata karena biaya token; tidak ada panggilan LLM,
perubahan konfigurasi/credential atau provider probe baru pada increment ini.
Unit, periode/publikasi dan kalibrasi fundamental tetap terbuka.

**Probe profil Yahoo nyata, 2026-11-11 WIB:** `get_stock_profile` berhasil untuk
BBCA.JK dan BBRI.JK melalui client existing, masing-masing quoteSummary HTTP 200;
listing cocok JKT/EQUITY, currency kuotasi dan laporan IDR. Tiap profil memuat
13/14 field key stats dan 13/13 financials, empat baris estimasi, satu pemegang
institusi, nol insider dan empat baris recommendation trend. Unit per field,
periode/publikasi laporan dan kalibrasi fundamental belum terbukti; retrieval
bukan publikasi. Regresi targeted **74 passed/1 warning**, termasuk MCP in-memory
dan kontrol pasar lain. Tidak ada bug direproduksi atau kode runtime diubah.
LLM nyata belum dijalankan: nama konfigurasi environment yang diperiksa serta
tiga kandidat dotenv dan tiga konfigurasi agent standar tidak ditemukan; tidak
membaca secret atau mencoba akun/endpoint baru. [Receipt, coverage dan batas](agent/IDX_PERSONAL_RESEARCH.md#probe-profil-yahoo-nyata--2026-11-11).
RESEARCH-01/02/03 penuh tetap terbuka; izin data tambahan dan deployment belum
diterima. Wheel pada probe tersebut belum memuat increment profil/skill; paket lokal terbaru tersedia pada follow-up packaging 2026-11-11 di atas.

**Riset lokal dilanjutkan, 2026-11-11 WIB:** `get_stock_profile` kini memakai
classifier existing untuk `.JK`, memberi label `idx`, menolak listing tanpa
symbol/venue equity/currency IDR yang cocok, dan mempertahankan mata uang laporan
terpisah dari kuotasi. Waktu retrieval dinyatakan eksplisit; periode/publikasi
fundamental tetap null dan penggunaan historis ditandai tidak didukung. Error
provider IDX disanitasi, respons cacat/nonfinite menjadi kegagalan terstruktur,
field hilang tetap unavailable. Alias venue Yahoo dimiliki satu konstanta yang
dipakai pencarian/profil. Skill bawaan `idx-research` memandu riset lokal Bahasa
Indonesia menggunakan satu observasi, indikator/provenance existing dan profil
snapshot opsional. Regresi awal profil **29 failed/7 passed**, skill **3 failed**;
sesudah implementasi, regresi lintas pasar/skill/MCP **1.162 passed**, gate
order/mandate/kill switch/read-only/SSE **137 passed**, Ruff lint lulus.
[Bukti, penggunaan dan batas QA](agent/IDX_PERSONAL_RESEARCH.md#research-local--2026-11-11).
Ini kontrak offline pada source checkout, bukan penerimaan coverage profil Yahoo
IDX nyata, fundamental point-in-time, corporate events, universe resmi atau
deployment. RESEARCH-01/02/03 penuh dan DATA/RULE/backtest tetap terbuka;
frontend, dependency, akun, kredensial dan jalur trading tidak diubah.

**Follow-up deployment, 2026-11-11 WIB:** Linux disposable belum tersedia.
`wsl --list --verbose` exit 1 / `wsl --status` exit 50 menyatakan belum
terpasang; Docker/Podman/Nginx/systemd-analyze tidak ditemukan. Tidak ada
instalasi, aktivasi service, image pull atau akses guest/container pengguna.
Pemeriksaan independen backup/restore **Windows sintetis lulus**: sesi dibuat
melalui API, pesan melalui SessionStore existing, proses berhenti sebelum
snapshot, 11 file cocok hash di lokasi restore kedua, sesi/pesan/list API 200,
tanpa key 401. Kedua proses final exit 15 dan port tertutup. Direktori konfigurasi
home ikut dicadangkan tetapi kosong; bukan bukti pemulihan secret/konfigurasi
produksi, ownership Linux atau finalizer graceful. Ekspresi pre-start menolak
key absent/kosong/whitespace; unit systemd sendiri belum dijalankan.
Empat dokumen diperbarui; tanpa perubahan kode, suite/build baru, provisioning
dependency atau deployment. [Bukti, kegagalan harness dan blocker minimum](agent/IDX_PERSONAL_RESEARCH.md#deployment-follow-up--2026-11-11).
Linux/Nginx/systemd/TLS/SSE proxy nyata dan pemulihan pada Linux tetap terbuka.
DEPLOY-PREP-01 tetap selesai sebagai persiapan; RELEASE-01 dan hak data
remote/publik belum diterima.

**Persiapan deployment satu operator, 2026-11-05 WIB:** dua gap terukur
diperbaiki: Origin ber-port cacat kini ditolak 403, dan Vite `serve --dev`
tetap pada loopback. Enam regresi gagal sebelum fix; regresi startup/auth/SSE/
read-only **128 passed**, packaging/gate/mandate/kill switch **117 passed**.
Wheel baru dibangun/dipasang offline ke target terisolasi dengan runtime
dependency existing; 143 aset UI cocok hash dan 262 file sumber frontend
identik dengan build terverifikasi sebelumnya. HTTP paket di luar checkout:
UI/deep links 200, key hilang/salah 401, Host/Origin tak tepercaya/cacat 403,
forwarded request tetap memerlukan key; sesi sintetis bertahan setelah restart.
Kedua proses QA berhenti dan port tertutup. `/ready` tetap 503 tanpa LLM.
[Template, batas operator bersama dan gate host tujuan](deployment/single-operator/README.md)
serta [hasil/perintah QA](agent/IDX_PERSONAL_RESEARCH.md#deployment-local--2026-11-05).
Nginx/systemd/TLS/proxy SSE nyata, Docker/Linux, pemulihan backup, hak display
remote/publik dan deployment belum terverifikasi. Shared key bukan isolasi
multiuser; riset Yahoo lokal tetap scope yang diterima. Tidak ada dependency,
akun, kredensial nyata, order, publish atau staging/commit yang ditambahkan.

**Follow-up kandidat publik baru, 2026-11-05 WIB:** dokumentasi Stock Chart
Invezgo menyatakan seluruh OHLC Rupiah, volume lembar dan tanggal sesi WIB,
termasuk suffix `Z` yang secara khusus bukan UTC. Namun terms mensyaratkan
akun/paket Developer/key dan melarang distribusi ulang; tidak ada ekspor aktual
BBCA/BBRI atau deklarasi adjustment/board/vintage/revisi terikat file.
Halaman OHLC ERPIW menyatakan data belum diunggah. Kedua jalur **belum memenuhi
intake**, tanpa akun/key/outreach atau API dipanggil.
[Bukti primer baru, receipt dan input pembuka](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#new-public-candidates-disposition--2026-11-05).
Paket original berizin tetap diperlukan; kepemilikan file oleh pihak ketiga
tidak otomatis mengizinkan pembagian. Empat dokumen saja berubah, tanpa kode,
tes runtime baru, penerimaan local, integrasi provider atau deployment.
Currency gate, backtest nonaktif dan task penuh tetap.

**Panduan primer BEI dituntaskan, 2026-11-05 WIB:** manual v1.2 berhasil
diunduh lewat preview individual Drive publik tanpa login (981.358 bytes,
7 halaman, hash/receipt dan render di luar repo). Manual menjelaskan statistik
agregat/peringkat, termasuk volume saham lintas reguler/tunai/negosiasi dan
perbandingan gainers/losers dengan adjustment aksi korporasi; bukan spesifikasi
seluruh OHLCV ekspor saham. **Jalur panduan selesai diperiksa dan dihentikan
menunggu paket input eksternal**; belum ada ekspor OHLCV target yang diterima.
[Bukti per halaman, batas deklarasi dan paket pembuka](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#official-manual-disposition--2026-11-05).
Review dapat lanjut tanpa akun/outreach bila paket asli BBCA/BBRI 26–30 Oktober
2026 beserta semantik/coverage/vintage/revisi/terms yang berlaku tersedia publik
atau dari pemegang berizin; jalur publik lengkap itu belum terbukti tersedia.
Empat dokumen saja berubah; kode, currency gate dan index dipertahankan.
Local Data Bridge belum diterima, backtest nonaktif dan task penuh tetap terbuka;
tanpa tes runtime baru, integrasi provider atau deployment.

**Ekspor publik alternatif berhasil diperoleh, 2026-11-05 WIB:** PDF resmi
IDX Daily Statistics 30 Oktober 2026 diunduh melalui tautan halaman Statistik,
1.974.315 bytes/9 halaman. File **ditolak untuk intake OHLCV harian per saham**:
isinya ringkasan/pemeringkatan dan agregat, tanpa OHLC lengkap BBCA/BBRI.
Terms publikasi memberi bukti izin nonkomersial bersyarat, bukan pengganti
kolom yang tidak ada. [Receipt, pemeriksaan halaman dan keputusan](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#official-statistics-file-review--2026-11-05).
Folder panduan publik yang ditautkan PDF ditemukan tanpa login; isi panduan
belum diperoleh. Tidak ada normalisasi/metadata produksi, penerimaan runtime,
integrasi provider atau deployment. Paket input OHLCV masih diperlukan;
currency gate, task penuh dan backtest nonaktif tetap.

**Jalur ekspor resmi dihentikan menunggu input, 2026-11-05 WIB:** halaman
Ringkasan Saham kanonik tidak menampilkan tabel/tanggal/tombol unduhan di browser;
console mencatat SyntaxError/ChunkLoadError. GET biasa terpisah mendapat 403 dan
tidak dilewati. Belum diperoleh file pasar atau deklarasi terikat ekspor yang
memenuhi intake. [Bukti akses, keputusan dan satu paket input pembuka](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#official-download-disposition--2026-11-05).
Paket subset BBCA/BBRI, window 26–30 Oktober 2026, dapat direview tanpa paket
seluruh pasar setelah file asli, semantik dan terms yang berlaku tersedia.
Pencarian sesi ini ditutup; bukan penolakan kualitas dataset yang belum diperoleh.
Empat dokumen saja diperbarui; tanpa penerimaan data, implementasi, tes runtime,
integrasi provider atau deployment. MVP Yahoo/yfinance tetap terpisah;
currency gate, backtest nonaktif dan task penuh tetap.

**Bukti izin website BEI baru, 2026-11-05 WIB:** ketentuan resmi pasal 6
memperbolehkan penggunaan nonkomersial dengan sumber lengkap/tanggal akses dan
melarang scraping/crawling. Bukti ini membuka penilaian ekspor resmi melalui
unduhan yang diperbolehkan tanpa otomatis mensyaratkan surat terpisah; kecocokan
file, metode dan penggunaan tetap harus dibuktikan. Tidak membuktikan hak
redistribusi Pholenk atau entitlement TICMI. [Keputusan terbatas dan receipt](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#official-website-permission-evidence--2026-11-05).
Belum ada file pasar diterima/diunduh, metadata produksi, perubahan kode,
integrasi provider atau deployment. Currency gate dan task penuh tetap.

**Keputusan follow-up sumber primer, 2026-11-05 WIB:** Pholenk menunggu
manifest/deklarasi yang mengikat file ke transformasi, metadata OHLCV/sesi,
vintage/revisi dan hak hulu untuk storage/processing riset pribadi lokal.
Pohon commit lengkap berisi 983 CSV saham, bukan bukti universe/cakupan historis;
riwayat schema terbaru hanya memperbaiki path, bukan tanggal coverage.
Ketentuan umum TICMI yang baru dibaca belum memberi spesifikasi atau entitlement.
Kedua jalur pencarian dihentikan sampai dokumen/file spesifik tersedia.
[Keputusan, input pembuka dan receipt baru](agent/IDX_PRIMARY_INPUT_DISCOVERY.md#follow-up-decision--2026-11-05).
Empat dokumen diperbarui; tanpa perubahan kode, intake CSV, tes runtime baru,
integrasi provider atau deployment. Currency gate tetap; task luas tetap terbuka.

**Follow-up packaging offline, 2026-11-05 WIB:** ketiga tes integrasi yang
sebelumnya dikeluarkan kini diuji memakai backend setuptools yang sudah ada,
tanpa unduhan dependency. Modul packaging **7 passed/1 warning**; kontrol tanpa
backend **4 passed/3 skipped**; regresi startup/auth/SPA **129 passed/2 warnings**.
Pip memakai `--no-index --no-build-isolation --no-deps`, tanpa konfigurasi pip
pengguna. Audit Python/child mencatat nol percobaan DNS/socket eksternal; ini
bukan sandbox jaringan OS. Tidak ada perubahan runtime produk atau build UI baru.
[Perintah, red-before-fix dan batas](agent/IDX_PERSONAL_RESEARCH.md#packaging-offline-dan-input-primer-baru--2026-11-05).

**Penemuan input primer baru, 2026-11-05 WIB:** kandidat Pholenk memberi
metadata/schema/preview CSV dengan commit dan identitas file; ketentuan layanan
TICMI memberi jalur izin yang dapat dibaca. Currency/unit/tanggal/adjustment/
vintage dan hak hulu belum cukup untuk menerima kandidat. Lensetek hanya
terindeks, URL hidup 404; tidak dipakai. [Sumber, receipt dan gap per kandidat](agent/IDX_PRIMARY_INPUT_DISCOVERY.md).
Tidak mengulang audit Mendeley atau membuat metadata produksi; penerimaan
Local Data Bridge, provider/referensi dan backtest IDX tetap terbuka.

**Verifikasi backend Windows, 2026-11-05 WIB:** suite penuh sesuai seleksi
contributor guide pascakoreksi **22.213 passed, 231 skipped, 3 deselected,
28 warnings**, tanpa failure; regresi terpisah 57 modul **1.507 passed,
31 skipped, 2 warnings**. Run awal sesi menemukan satu kegagalan aplikasi:
`BackgroundTaskStore` gagal menyimpan status terminal karena WinError 5.
Pemilik kini memakai retry terbatas existing; enam regresi baru membuktikan
recovery, exhaustion, cleanup dan propagasi error. Tiga failure packaging awal
berasal dari kesalahan seleksi harness; child pip mencoba DNS yang ditolak guard.
Seleksi final membuktikan tepat tiga tes provisioning dikeluarkan. Skip native,
extra opsional dan canary bukan bukti lulus; audit Python/child bukan sandbox
jaringan OS. [Hasil, perintah, audit dan batas](agent/IDX_PERSONAL_RESEARCH.md#verifikasi-backend-windows--2026-11-05).
Ini bukan baseline pra-IDX atau penerimaan provider/Mendeley: BASE-02,
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. MVP riset pribadi
read-only Yahoo/yfinance tetap diterima; Local Data Bridge belum diterima,
backtest IDX tetap nonaktif, paper/live terpisah dan Index Alpha ditunda.

**Follow-up registry/kode publik Mendeley v5, 2026-11-04 WIB:** OAI dan DataCite
berhasil dibaca tanpa akun. Waktu issued 30 September 2026 14:45:31 UTC dan satu
aktivitas create metadata 14:45:32 UTC kini terverifikasi; keduanya bukan vintage
retrieval Yahoo. Record belum memberi manifest recipe/CSV, currency seluruh OHLC
atau hak hulu; pencarian repo penulis/institusi belum menemukan manifest target.
Implementasi metadata tetap ditahan, Local Data Bridge belum diterima riset,
task luas tetap terbuka. Empat dokumen saja berubah; tidak ada probe runtime baru.
[Bukti registry, batas riwayat koreksi dan keputusan](agent/IDX_PROVIDER_RESEARCH.md#mendeley-v5-public-registry-and-code-discovery--2026-11-04).

**Follow-up perbandingan rilis/hak Mendeley v5, 2026-11-04 WIB:** jalur baru
perbandingan resmi v4→v5 mengonfirmasi perubahan deskripsi paket Excel ke
CSV/README/notebook dan lisensi v5 CC BY-NC; belum ada log transformasi yang
mengikat recipe ke CSV. Associated data/pencarian koreksi tidak menemukan
manifest tambahan. Teks CC BY-NC berhasil dibaca, tetapi tidak membuktikan hak
hulu; halaman bantuan Yahoo baru hanya discovery (full read 429), terms kanonik
tetap 999. Currency seluruh OHLC masih inferensi; vintage/revisi tetap unknown
dalam review. Metadata produksi tidak diimplementasikan, Local Data Bridge belum
diterima riset dan task luas tetap terbuka. Dokumentasi saja, tanpa probe runtime
baru; hasil 15 × 722/CLI 8+7 di bawah adalah historis.
[Bukti baru, kelas bukti dan input minimum](agent/IDX_PROVIDER_RESEARCH.md#mendeley-v5-release-comparison-and-rights-follow-up--2026-11-04).

**Follow-up metadata Mendeley v5, 2026-11-04 WIB:** artikel primer kini
mendeklarasikan volume saham dan close IDR; notebook publik menyatakan
`auto_adjust=True` untuk seluruh OHLC serta proyeksi tanggal lokal. Notebook
hanya diinspeksi statis. Satuan dan recipe adjustment kini punya bukti; IDR
seluruh OHLC masih inferensi dari proyeksi yang sama. CSV date/ticker berbeda
dari urutan ekspor notebook ticker/date; source vintage/metadata Yahoo dan
review izin hulu belum terikat pada rilis. Implementasi metadata/provider
belum diterima. Probe offline baru 15 × 722 bar lulus loader/helper; CLI 8+7
menolak currency_declaration, exit 2/unavailable. Task luas tetap terbuka.
[Bukti baru, batas dan handoff](agent/IDX_PROVIDER_RESEARCH.md#mendeley-v5-metadata-evidence-follow-up--2026-11-04).

**Audit Mendeley v5 sebelumnya, 2026-11-04 WIB:** CSV asli dan README berhasil diunduh
melalui UI publik normal; GET langsung 403 tidak dilewati. CSV 920.606 bytes,
10.830 baris/15 ticker × 722, 2022-01-03–2024-12-30; tanpa duplikat/pelanggaran
OHLC, 627 volume nol dipertahankan. Seluruh 15 seri lulus loader/nilai numerik
persis dan helper JSON; CLI dua batch 8+7 tetap unavailable/exit 2 pada
currency_declaration, backtest_enabled false. README mendeklarasikan WIB;
IDR, unit volume dan kontrak adjustment OHLC belum cukup. Metadata/provider
belum diterima; DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka.
[Receipt, audit dan blocker](agent/IDX_PROVIDER_RESEARCH.md#mendeley-v5-original-file-audit--2026-11-04).
Kode/tes/dependency tetap utuh; bukan run pytest/Ruff/frontend/deployment baru.

**Pencarian ekspor local sebelumnya, 2026-11-04 WIB:** CSV publik Aethereal berhasil
diunduh dan diaudit: 518.044 baris, 114 ticker (halaman menyebut 120), 308 bar
melanggar invariant OHLC. Seleksi BBCA/BBRI tanpa perbaikan data ditolak loader
existing (5/8 bar cacat); JSON/CLI `fetch_failed`, exit 2/unavailable,
backtest false. Penerbit menyatakan gratis riset/pendidikan, IDR dan volume saham,
tetapi timezone, adjustment OHLC, sumber hulu dan cakupan izin lain belum terbukti.
Pada pencarian sebelumnya Mendeley v5 CC BY-NC belum diunduh; audit baru di atas melanjutkan bukti tersebut.
[Bukti unduhan, hash, audit dan batas](agent/IDX_PROVIDER_RESEARCH.md#public-local-export-search--2026-11-04).
Ini kemajuan penerimaan input, bukan implementasi metadata/provider: kode runtime
tidak berubah, file asli di luar repo, local belum diterima riset; DATA-01/02/03,
IDX-02 dan RESEARCH-01 penuh tetap terbuka. Guard tidak dilonggarkan dan tidak
ada konfigurasi pengguna, dependency, staging atau commit yang diubah.

**Follow-up list tanpa mapping Local Data Bridge, 2026-11-04 WIB:** pemilik
`_ensure_config` kini menolak list `sources` nonempty tanpa satu pun simbol string
nonblank sebelum mempublikasikan snapshot atau mengakses cache. Resolver/direct
helper melaporkan `fetch_failed`; availability tetap pemeriksaan deklarasi.
Simbol tak terkonfigurasi dalam indeks valid dan sumber valid kosong tetap
`no_data`; absent/list kosong dan isolasi peer lintas pasar tetap existing.
Ini sengaja mencakup list seluruh absent/blank, tanpa mengubah skip per entri
pada list campuran. Awal **18 failed, 5 passed**, akhir **23 tes baru passed**;
regresi 48 modul **1.526 passed, 3 skipped, 7 warnings**, Ruff dan 20 kombinasi
JSON/CLI sintetis lulus. Retry/koreksi instance serta cache IDX/AS utuh tanpa
token baru. [Audit, kontrak dan perintah](agent/IDX_PERSONAL_RESEARCH.md#data-03--list-tanpa-mapping-local-data-bridge).
Local tetap belum diterima riset pada metadata currency; DATA-01/02/03, IDX-02
dan RESEARCH-01 penuh tetap terbuka, backtest IDX nonaktif, Index Alpha ditunda.
Backend/safety penuh, frontend, provider nyata, MCP eksternal, Electron dan
deployment tidak diuji. Tanpa dependency, staging atau commit.

**Follow-up container sources Local Data Bridge, 2026-11-04 WIB:** `_load_config`
kini menolak nilai `sources` non-list dengan ValueError spesifik tanpa isi mentah.
Key absent/list kosong tetap existing; null eksplisit kini ditolak. Semua pasar
berbagi guard struktur, sementara item/simbol/reader/cache tidak berubah. Regresi
awal **44 failed, 7 passed**; **51 tes baru** lulus dan regresi 47 modul
**1.503 passed, 3 skipped, 7 warnings**. Ruff serta JSON/CLI sintetis terisolasi
lulus; cache positif/revision dan byte file cache utuh tanpa token baru.
[Bukti, kompatibilitas dan perintah](agent/IDX_PERSONAL_RESEARCH.md#data-03--container-sources-local-data-bridge).
Resolver tetap `source_unavailable`, direct-loader melalui helper `fetch_failed`;
sumber valid kosong tetap `no_data`. Struktur global cacat tidak mengisolasi peer.
List all-invalid ditangani follow-up di atas; simbol tanpa entri tetap omission
dalam indeks valid, dan metadata local tetap terbuka;
local belum diterima riset, DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap
terbuka. Backtest IDX nonaktif, Index Alpha ditunda. Backend/safety penuh,
frontend, provider nyata, MCP eksternal, Electron dan deployment tidak diuji;
tanpa dependency, staging atau commit.

**Follow-up dokumen top-level Local Data Bridge, 2026-11-04 WIB:** pemilik
`_load_config` kini menolak scalar/list top-level dengan ValueError spesifik tanpa
isi mentah. Empty/null, file absent dan mapping valid tetap kompatibel lintas
pasar. Regresi awal **40 failed, 9 passed**; **49 tes baru** lulus, regresi
46 modul **1.452 passed, 3 skipped, 7 warnings**, Ruff serta JSON/CLI sintetis
terisolasi lulus. Cache positif/revision dan byte file cache tetap utuh tanpa
token baru. Resolver melaporkan `source_unavailable`; direct-loader melalui
helper `fetch_failed`. Struktur global cacat tidak menjamin isolasi simbol.
[Bukti, matriks audit dan perintah](agent/IDX_PERSONAL_RESEARCH.md#data-03--dokumen-top-level-local-data-bridge).
Container `sources` ditangani follow-up di atas; diagnostik simbol tanpa entri
dan metadata local masih terbuka; local belum diterima riset, DATA-01/02/03, IDX-02 dan RESEARCH-01
penuh tetap terbuka. Backtest IDX nonaktif, Index Alpha ditunda. Backend/safety
penuh, provider nyata, frontend, MCP eksternal, Electron dan deployment tidak
diverifikasi; tanpa dependency, staging atau commit.

**Follow-up simbol non-string Local Data Bridge, 2026-11-04 WIB:** mapping dengan
`symbol` bukan string kini dilewati dengan warning nomor entri tanpa nilai mentah
melalui pemilik indeks existing. Peer sehat IDX/pasar lain tidak lagi terhenti
oleh `.strip()` pada null, boolean, angka, list, mapping atau tanggal YAML.
Tidak ada coercion simbol; string numerik, case-sensitive lookup, strip,
duplikat terakhir dan absent/blank tetap memakai kontrak existing. Regresi awal
**36 failed, 30 passed**; **38 kasus baru**, modul entri **66 passed**, regresi
45 modul **1.403 passed, 3 skipped, 7 warnings**. Ruff dan JSON/CLI sintetis
terisolasi lulus; Black tidak tersedia. Cache positif/revision tetap utuh dan
warning tidak tersembunyi, tanpa token baru/penghapusan cache. [Bukti dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--simbol-non-string-local-data-bridge).
Top-level/container `sources` ditangani follow-up di atas; diagnostik simbol
tanpa entri masih terbuka. Local belum diterima fitur riset; DATA-01/02/03, IDX-02 dan RESEARCH-01
penuh tetap terbuka, backtest IDX nonaktif dan Index Alpha ditunda. Provider
nyata, backend/safety penuh, frontend, MCP eksternal, Electron dan deployment
tidak diuji; tanpa perubahan dependency, staging atau commit.

**Follow-up isolasi entri YAML Local Data Bridge, 2026-11-04 WIB:** satu item
bukan mapping pada list `sources` tidak lagi menggagalkan simbol sehat. Pemilik
indeks existing melewati item tanpa identitas dengan warning nomor entri,
tanpa nilai mentah. Pemilihan duplikat terakhir, strip simbol, validasi reader
dan perilaku entri valid pasar lain dipertahankan. Regresi awal **23 failed,
5 passed**; **28 tes baru**, enam modul local **304 passed**, regresi 45 modul
**1.365 passed, 3 skipped, 7 warnings**, Ruff dan JSON/CLI sintetis lulus.
Black tidak tersedia. Cache positif tetap dapat dipakai dan tidak menyembunyikan
warning; tanpa token baru/penghapusan cache. [Audit, perintah dan gap tersisa](agent/IDX_PERSONAL_RESEARCH.md#data-03--isolasi-entri-yaml-local-data-bridge).
Top-level, container `sources` dan simbol non-string ditutup follow-up di atas. Local
tetap belum diterima untuk riset pada metadata currency. DATA-01/02/03, IDX-02,
RESEARCH-01 penuh tetap terbuka; backtest IDX nonaktif dan Index Alpha ditunda.
Provider nyata, backend/safety penuh, frontend, MCP eksternal, Electron dan
deployment tidak diuji; tanpa perubahan dependency, staging atau commit.

**Follow-up konfigurasi sumber Local Data Bridge, 2026-11-04 WIB:** IDX kini
menolak type tidak didukung dan field wajib path/db_path/query yang absent,
blank atau bukan string sebelum reader I/O. Error menyebut field tanpa nilai
mentah; helper merekam fetch_failed, sumber valid kosong tetap no_data. Default
CSV dan pasar lain dipertahankan. Regresi awal **47 failed, 14 passed**;
**61 tes baru**, lima modul local IDX **276 passed**, regresi 44 modul
**1.337 passed, 3 skipped, 7 warnings**, Ruff serta JSON/CLI sintetis lulus.
Black tidak tersedia. Cache deklarasi/revision existing cukup tanpa token baru
atau penghapusan entry. [Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--konfigurasi-sumber-local-data-bridge).
Timestamp/bucket dan metadata local masih memerlukan ekspor berizin; local
tetap ditolak pada currency. DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap
terbuka, backtest IDX nonaktif. Tanpa provider nyata, perubahan dependency,
frontend/trading, staging, commit atau deployment.

**Follow-up DATA-03 schema tanggal Local Data Bridge, 2026-11-04 WIB:** kolom
tanggal absent tanpa DatetimeIndex kini menolak schema local IDX melalui
normalizer existing, termasuk pada file kosong. Helper melaporkan fetch_failed;
file kosong berschema valid tetap no_data. Regresi awal **18 failed, 17 passed**;
35 tes baru, run akhir empat modul local **215 passed**, regresi 43 modul
**1.276 passed, 3 skipped, 7 warnings**, Ruff dan probe JSON/CLI sintetis lulus.
Black tidak tersedia. Cache tidak memerlukan token baru: None/empty tidak
disimpan dan source revision/schema existing tetap diuji. [Audit timestamp,
bucket, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--schema-tanggal-local-data-bridge).
Semantik UTC/format/bucket belum diterima untuk ekspor IDX; metadata local tetap
ditolak pada currency. DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka,
backtest IDX nonaktif. Tanpa provider nyata, dependency/frontend/trading,
staging, commit atau deployment.

**Follow-up DATA-03 OHLC Local Data Bridge, 2026-11-04 WIB:** normalizer local IDX
kini menolak field harga hilang, OHLC parsial/nonnumerik/nonfinite, boolean/
kompleks dan pelanggaran invariant sebelum bar dibuang, difilter atau
diresample. Bar bertanggal dengan OHLC all-null ditolak; file kosong dengan
schema tetap no_data. Cache menambah `idx_local_prices_v1` tanpa menghapus entry
lama, dengan source revision dan kontrol pasar lain tetap terjaga. Regresi awal
**101 failed, 13 passed**; 114 tes baru, gabungan 42 modul **1.241 passed,
3 skipped, 7 warnings**, Ruff serta probe JSON/CLI sintetis terisolasi lulus.
Black tidak tersedia. [Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--ohlc-local-data-bridge).
Konversi UTC/bucket dan metadata ekspor nyata masih perlu validasi; local tetap
ditolak fitur riset pada currency. DATA-01/02/03, IDX-02, RESEARCH-01 penuh
tetap terbuka; backtest IDX nonaktif. Tidak ada akses provider, perubahan
dependency/frontend/trading, staging, commit atau deployment.

**Follow-up DATA-03 tanggal Local Data Bridge, 2026-11-04 WIB:** normalizer local
IDX kini menolak tanggal hilang/gagal parse sebelum bar dapat dibuang, difilter
atau diagregasi. Cache menambah `idx_local_dates_v1` tanpa menghapus entry lama;
source revision dan kebijakan pasar lain tetap sama. Regresi awal **19 failed,
9 passed**; 28 tes baru, gabungan 40 modul **1.121 passed, 3 skipped, 7 warnings**,
Ruff dan probe JSON/CLI sintetis terisolasi lulus. Black tidak tersedia.
File kosong tetap `no_data`, tanggal cacat `fetch_failed`, peer sehat serta
volume nol/null tetap tersedia. [Audit, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--tanggal-local-data-bridge).
Gap OHLC yang ditemukan pada run tersebut ditutup follow-up di atas; konversi
UTC/bucket belum dikalibrasi terhadap ekspor nyata, dan metadata local tetap
ditolak fitur riset. DATA-01/02/03, IDX-02
dan RESEARCH-01 penuh tetap terbuka; backtest IDX nonaktif. Tidak ada akses
provider, perubahan dependency/frontend/trading, staging, commit atau deployment.

**Follow-up DATA-03 volume Local Data Bridge, 2026-11-04 WIB:** local IDX kini
mempertahankan kolom volume absent sebagai null dan menolak volume invalid dengan
guard kontrak bersama. Resampling menghasilkan null jika ada volume penyusun
yang hilang; nol teramati dan total lengkap tetap tersedia. Cache local IDX lama
dilewati, file lama dipertahankan, pasar lain memakai kebijakan existing.
Sebanyak **38 tes baru**, regresi **1.093 passed, 3 skipped** (39 modul,
7 warning deprecation/fixture), Ruff serta probe CSV/CLI terisolasi lulus.
Local tetap ditolak fitur riset pada metadata currency; ini perbaikan volume,
bukan penerimaan local IDX atau sertifikasi IDR/Jakarta/satuan/adjustment.
[Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--volume-local-data-bridge).
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka; tanpa perubahan
trading/dependency/frontend, akses provider, staging, commit atau deployment.

**Follow-up DATA-03 volume mentah, 2026-11-04 WIB:** kontrak IDX bersama kini
menolak volume invalid sebelum coercion: teks invalid/NaN tekstual, boolean,
kompleks, negatif, nonfinite dan overflow; volume null tetap hilang dan nol tetap
observasi. Parser strict Yahoo mempertahankan volume mentah; pembentukan frame
IDX menjaga tipe sampai validasi. Cache kedua transport memakai identitas baru
tanpa menghapus cache lama. Sebanyak **53 tes baru**, regresi **1.055 passed,
3 skipped** (38 modul, 6 warning existing/fixture), Ruff dan CLI sintetis exit
2/partial lulus; peer sehat tetap memiliki 20 bar dengan nol/null terpisah.
Local Data Bridge dikonfirmasi mengisi kolom volume absent dengan nol tetapi
ditolak jalur riset karena metadata IDR tidak tersedia; loader itu belum diterima
untuk riset IDX. [Bukti, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--volume-mentah-sebelum-coercion).
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. Tanpa probe provider,
perubahan dependency/frontend/trading, staging atau commit; backend/safety penuh,
MCP eksternal, Electron packaged app dan deployment tidak diverifikasi ulang.

**Follow-up DATA-03 harga tidak lengkap, 2026-11-04 WIB:** Yahoo parser kini
memakai mode strict khusus loader IDX; Yahoo/yfinance berbagi guard normalisasi
untuk menolak OHLC parsial/non-numerik dan field harga hilang. Slot OHLCV yang
sepenuhnya kosong dipisahkan sebelum coercion, tanpa inferensi libur/suspensi;
volume nol/null tetap berbeda. Cache kedua transport memakai identitas kontrak
baru. Probe CLI dua simbol mengungkap kegagalan batch yang ikut membuang simbol
sehat; helper bersama kini mengisolasi akuisisi IDX per simbol sambil menjaga
batching pasar lain. Sebanyak **39 tes baru**, regresi gabungan **915 passed**
(30 modul, 6 warning existing/fixture), Ruff dan CLI sintetis terisolasi lulus:
exit 2, partial, BBCA unavailable/BBRI sehat 20 bar, backtest false.
[Bukti, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--ohlc-tidak-lengkap-dan-isolasi-simbol).
Tidak ada probe harga jaringan, impor referensi resmi atau penerimaan provider;
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. Frontend, backend/safety
penuh, MCP eksternal serta deployment tidak diverifikasi ulang; tanpa staging/commit.

**Slice DATA-03 validasi OHLC yfinance, 2026-11-04 WIB:** bar IDX yang melanggar
invariant OHLC kini menolak seri pada normalisasi, sebelum bar cacat dapat dibuang
dan seri pendek dilaporkan sehat. Identitas cache khusus kontrak IDX melewati
cache lama; cache baru mempertahankan metadata dan waktu retrieval. Delapan
regresi awal mereproduksi cacat; 13 tes baru dan regresi gabungan **785 passed**
(6 warning existing/fixture), Ruff lulus. HTTP in-process membuktikan hasil
unavailable dengan upaya `fetch_failed`; kontrol AAPL serta seluruh modul tes
yfinance lulus. [Cakupan, peta gap dan perintah](agent/IDX_PERSONAL_RESEARCH.md#data-03--validasi-ohlc-yfinance-sebelum-pembuangan-bar).
DATA-01/02/03, IDX-02 dan RESEARCH-01 penuh tetap terbuka. Tidak ada probe harga
jaringan, impor resmi, perubahan frontend/dependency, staging atau commit;
backend/safety penuh, MCP eksternal dan deployment tidak dijalankan.

**Keputusan MVP pribadi, 2026-11-04 WIB:** riset lokal read-only Yahoo/yfinance
untuk watchlist manual maksimal delapan saham reguler `.JK`, harian IDR melalui
UI/CLI, diterima secara teknis dalam batas yang disepakati. Lima run CLI nyata
meluluskan 22 kombinasi simbol/periode (60/200/500 bar), termasuk sumber aktual
yfinance; browser provider nyata id desktop/mobile, 719 regresi backend terkait,
121 safety, 1231 frontend/95 file dan build lulus. Pencarian Yahoo dapat kosong;
input `.JK` manual menjadi pemulihan yang teruji. [Kriteria, bukti dan batas
penerimaan](agent/IDX_PERSONAL_RESEARCH.md#penerimaan-mvp-pribadi--2026-11-04).
Ini penerimaan scope riset pribadi, bukan seluruh dukungan IDX atau baseline
sebelum perubahan IDX. DATA-01/02/03, IDX-02, UI-01 penuh, RESEARCH-01 dan tahap
trading tetap terbuka; backend penuh, MCP eksternal dan deployment belum
diverifikasi. Penerimaan MVP-A01 hanya memperbarui tiga dokumen.

**Follow-up startup/auth, 2026-11-04 WIB:** CLI resmi `python -m cli serve`
menjalankan assembler, lifespan/preflight dan static frontend asli pada salinan
source/runtime sementara tanpa kredensial pribadi. Loopback tanpa key dan auth
key sintetis lulus; browser id desktop/mobile mengambil tiga saham × 60 bar
dari Yahoo. Key hilang/salah ditolak 401, cross-site/Host tak tepercaya 403;
server dihentikan dan port tertutup. `/ready` tetap 503 karena LLM belum
dikonfigurasi; preflight OKX gagal SSL, tanpa menghalangi riset langsung.
Regresi startup/auth awal 119 passed/1 failed mengungkap kebocoran mount antar
tes; isolasi fixture diperbaiki, run akhir **120 passed**, Ruff lulus.
Pada follow-up tersebut belum ada perubahan runtime dan jalur file langsung
masih gagal. **DEV-START-01 kini selesai:** nama host disatukan pada assembler;
file/modul/CLI/import terisolasi serta startup/auth/SPA **129 passed**. Browser
id pada file langsung berhasil memperoleh BBCA.JK 60 bar Yahoo/IDR; auth dan
shutdown/port tertutup terverifikasi. `/ready` tetap 503 tanpa LLM. [Bukti dan batas](agent/IDX_PERSONAL_RESEARCH.md#startup-aplikasi-dan-auth-nyata--2026-11-04).

**Instalasi bersih lokal, 2026-11-04 WIB:** venv Python 3.12.13 baru di luar
repository berhasil memasang lock Windows berhash dan wheel proyek non-editable.
`pip check`, import dari `site-packages`, console CLI/MCP help, serta startup
console serve dan satu riset BBCA.JK 60 bar Yahoo/IDR lulus; server berhenti dan
port tertutup. `/ready` tetap 503 tanpa LLM, OKX tetap gagal SSL. **Wheel tidak
menyertakan frontend/dist**: deep link UI 404 pada paket murni; distribusi UI
masih terbuka di DEV-PACK-01. [Perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#instalasi-bersih-backend--2026-11-04).
Tidak membuktikan backend penuh, MCP eksternal, Electron atau deployment.
Gap pada run historis tersebut kini ditutup oleh verifikasi DEV-PACK-01 berikut.

**DEV-PACK-01 selesai, 2026-11-04 WIB:** wheel lokal kini membundel hasil build
Vite baru di `src/api/_frontend`; sdist membawa `frontend/dist`. Pemeriksaan
hash membuktikan 143 file UI identik pada build, wheel, sdist dan wheel hasil
roundtrip. Resolver bersama dipakai static mount dan middleware SPA, dengan
fallback source/desktop code-relative. Venv Python 3.12.13 baru di luar checkout
memasang lock Windows berhash dan wheel non-editable; `pip check`, origin
`site-packages`, CLI/MCP help, startup serta UI browser id → BBCA.JK 60 bar
Yahoo/IDR lulus. Deep link 200, key hilang/salah 401, Host/cross-site 403,
shutdown dan port tertutup terverifikasi. Gabungan startup/auth/SPA/entry point
dan packaging awal **134 passed**, packaging akhir **6 passed**; frontend
**1231 passed/95 file**, build dan Ruff lulus. `/ready` tetap 503 tanpa LLM,
OKX tetap gagal SSL; TLS tidak diubah. [Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#dev-pack-01--distribusi-web-ui-python).
Ini distribusi lokal yang belum dipublish; tidak menutup RELEASE-01 atau
verifikasi backend/safety penuh, MCP eksternal, Electron dan deployment.

Repository menyediakan fondasi Vibe-Trading multi-market yang luas. Versi backend dan frontend adalah `0.1.18`; desktop Electron merupakan community build terpisah versi `0.3.0`. **Fondasi riset harian IDX kini tersedia dan diuji; dukungan IDX end-to-end belum selesai.** Identitas `id_equity`/IDR, loader Yahoo/yfinance, provenance, registry snapshot, dan primitive rulebook/calendar tersedia. Backtest IDX ditolak secara eksplisit; paper/live IDX belum ditambahkan. Asesmen dan milestone: [IDX_FOUNDATION.md](agent/IDX_FOUNDATION.md).

Analisis mencakup inventaris seluruh file terlacak dan direktori tingkat atas, pemetaan seluruh paket `agent/src`, pembacaan implementasi jalur inti, konfigurasi, kontrak paper, panduan kontribusi, dan inventaris pengujian. Ini analisis struktur dan kesiapan pengembangan, bukan audit setiap baris atau sertifikasi seluruh fitur upstream. Implementasi saat ini memperluas seam pasar/data yang ada. Manifest/lock dependensi dan state akun tidak diubah; lingkungan pengujian terisolasi dipasang dari lock Windows.

## Inventaris repository

Inventaris `git ls-files -z` menghasilkan **3.164 file terlacak**: `agent/` 2.777, `frontend/` 256, `desktop/` 33, `wiki/` 42, `.github/` 11, dan sisanya aset, kontrak, tools, deployment, serta dokumen root. Angka ini adalah baseline sebelum dokumen baru ditambahkan ke Git.

- `agent/`: backend Python, entry point API/MCP, CLI, mesin backtest, paket domain, skill riset, eval, dan tes.
- `frontend/`: React 19, TypeScript, Vite, Tailwind, Zustand, ECharts, i18next, Vitest. Versi serta scripts bersumber dari [package.json](frontend/package.json).
- `desktop/electron/`: shell Electron, lifecycle backend, build runtime Windows, packaging, dan smoke checks; bukan backend terpisah. Konfigurasi: [package.json](desktop/electron/package.json).
- `wiki/`: situs statis HTML/JavaScript/CSS, partials bersama, skrip sinkronisasi, Cloudflare configuration/functions, dan konten dokumentasi. Tidak terdapat `wiki/package.json` pada snapshot ini. Lihat [wiki/README.md](wiki/README.md).
- `schema/tool_contracts/`: kontrak JSON `paper_trade_step` v1.1/v1.2.
- `pixel-office/`: dokumentasi papan tugas riset manual; implementasi berada di `src/pixel_agents`. Assign task tidak otomatis menjalankan agen atau order ([README](pixel-office/README.md)).
- `assets/`: aset branding/demo. `scripts/dev`: pengelola dev server berbasis Bash; perlu lingkungan Bash bila digunakan dari Windows.
- `tools/`: gate kebersihan file privat dan environment variable, tes gate, utilitas font laporan, dan kebutuhan pemeriksaan loader.
- `.github/workflows/`: pengujian Python/frontend, build desktop Windows, Docker, loader health, serta validasi/publikasi wiki. Keberadaan workflow tidak membuktikan run CI terakhir lulus.
- `.devcontainer/`, `Dockerfile`, `docker-compose.yml`, `zimaos/`: pilihan development dan deployment. Docker memakai build bertahap frontend/Python, lock berhash, volume state, dan hardening runtime; Compose mengekspos port default ke loopback host.
- `pyproject.toml`, `agent/requirements*.txt`, lock root, `MANIFEST.in`: packaging dan dependensi. Root Python mensyaratkan Python >=3.11; frontend mensyaratkan Node >=22.22.0.
- Dokumen upstream: README dalam beberapa bahasa termasuk `README_id.md`, changelog, lisensi/notice, panduan kontribusi, contributor guide agen, dan kebijakan keamanan.

## Arsitektur dan alur eksekusi

```text
Web React ── HTTP + SSE ──> FastAPI assembler ──> route modules
CLI / kanal pesan ────────────────────────────> SessionService / AgentLoop
                                               │
                                               ├─ provider LLM + konteks/skill/memory
                                               ├─ ToolRegistry + tool policy
                                               │    ├─ data / analytics / backtest
                                               │    ├─ paper / portfolio / shadow
                                               │    └─ goal / swarm / research artifacts
                                               └─ grounding + trace + state / artefak run
MCP entry point ──> tool riset bersama, dengan batas exposure tersendiri

Permintaan data ──> klasifikasi simbol ──> registry/fallback ──> loader
Backtest config + signal engine ──> runner ──> aturan engine pasar
                                              └─ hasil / metrik / validasi / run card
Live execution ──> pemilihan akun + mandate + halt + pre-trade gate
                                              └─ connector broker + audit
```

Diagram merangkum relasi utama, bukan menyatakan semua mode memanggil setiap komponen.

### Permukaan aplikasi

- [agent/api_server.py](agent/api_server.py) adalah assembler FastAPI: lifecycle, middleware, auth, route registration, dan penyajian frontend. Logika endpoint dipisahkan di `agent/src/api/`.
- [sessions_routes.py](agent/src/api/sessions_routes.py) menyediakan sesi/goal dan streaming. [SessionService](agent/src/session/service.py) mengelola attempt, event, cancel/recovery, dan satu loop aktif per sesi; event diteruskan ke SSE.
- [cli/main.py](agent/cli/main.py) menangani onboarding dan REPL; subcommand lain diteruskan ke jalur CLI legacy. Console entry point didefinisikan di `pyproject.toml`.
- [agent/mcp_server.py](agent/mcp_server.py) mengekspos tool riset melalui stdio/SSE/HTTP. Exposure MCP dibatasi terpisah dari akses internal aplikasi; bukan endpoint order live umum.
- Frontend masuk melalui [main.tsx](frontend/src/main.tsx) dan [router.tsx](frontend/src/router.tsx). Halaman mencakup agent, run detail/compare, runtime, scheduled research, laporan, artefak riset, paper trading, portfolio, correlation, Alpha Zoo, Options Lab, settings, dan Pixel Office.
- [lib/api.ts](frontend/src/lib/api.ts) memusatkan request, auth, timeout, dan error. [vite.config.ts](frontend/vite.config.ts) mem-proxy API ke backend default `127.0.0.1:8899`; dev frontend memakai port `5899`.

### Peta paket backend

- `src/agent/`: ReAct loop, context budget/compaction, skill loading, lifecycle tool, trace, dan numerical grounding. [loop.py](agent/src/agent/loop.py) memanggil provider, registry, dan gate rilis jawaban.
- `src/providers/`: adapter LLM, streaming, auth provider, capabilities, dan tool policy. `src/tools/`: implementasi tool; auto-discovery dan pembangunan registry di [__init__.py](agent/src/tools/__init__.py), kontrak/eksekusi di [agent/tools.py](agent/src/agent/tools.py).
- `src/config/`: schema, loader/writer, accessor, migrasi, dan path runtime. `src/core/`: eksekusi subprocess strategi dan state run. `src/security/`: validasi jaringan serta kebijakan akses workspace dan scanner.
- `src/session/`: lifecycle dan penyimpanan percakapan, search, checkpoint, serta events. `src/memory/`: memory persisten, indeks pencarian, hierarchy, consolidation, dan compression.
- `src/goal/`: sasaran dan kelanjutan pekerjaan; `src/hypotheses/`: registry hipotesis; `src/research_artifacts/`: artefak riset persisten berversi; `src/governance/`: manifest dan ledger metodologi.
- `src/factors/`: registry Alpha Zoo, data availability, benchmark/compare, dan kontrak riset. `src/quantlib/`: primitive kuantitatif seperti risk, statistik, opsi, attribution, event study, dan portfolio. `src/entities/`: instrumen serta cashflow; cashflow analytics terpisah dari simulator OHLCV.
- `src/strategy_store/`: artefak strategi dan decay monitoring. `src/strategy_discovery/`: facade katalog dan evidence dari run yang dapat direproduksi; keberadaan strategi bukan bukti performa IDX.
- `src/swarm/`: preset, DAG/runtime, worker, grounding, event, dan artifact store untuk multi-agent research.
- `src/scheduled_research/`: proposal/playbook, eksekutor, verdict, store, serta delivery. `src/scheduling/`: kernel, trigger/timezone, registry callable, dan system jobs bersama. Startup scheduled executor berada pada lifespan API.
- `src/trading/`: koneksi/profile/akun, kredensial, onboarding, capability matrix, dan connector broker/exchange. `src/live/`: mandate, enforcement, order guard, SDK gate, halt, counter, audit, serta runtime live. **Area kritis finansial.**
- `src/portfolio/`: agregasi read-only, normalisasi, impor, FX, rebalance, dan snapshot. `src/shadow_account/`: ekstraksi pola jurnal, codegen/backtest bayangan, atribusi, dan laporan.
- `src/channels/`: adapter kanal pesan dan bus/manager; `src/channelsui/`: layanan koneksi/gateway dan UI kanal. `src/openbb_bridge/`: integrasi opsional OpenBB.
- `src/pixel_agents/`: papan tugas Pixel Office; `src/br_data/`: pipeline data Brasil, bukan IDX; `src/utils/`: utilitas media.
- `src/skills/`: pustaka skill riset yang dibundel. `agent/skills/` adalah direktori tambahan yang berbeda; jangan mengasumsikan keduanya memiliki mekanisme loading yang sama.

### Data, backtest, paper, dan penyimpanan

- [market_data.py](agent/src/market_data.py) menyediakan deteksi sumber, pengambilan data bersama, provenance, dan pembatasan output untuk tool lokal/MCP.
- [loaders/registry.py](agent/backtest/loaders/registry.py) memiliki registrasi loader, sumber valid, fallback per pasar, serta larangan fallback jaringan untuk sumber eksplisit tertentu. Mengubah `.markets` pada loader saja tidak cukup untuk menambahkan pasar.
- [engines/_market_hooks.py](agent/backtest/engines/_market_hooks.py) memiliki classifier dan currency mapping yang dipakai runner/composite. [composite.py](agent/backtest/engines/composite.py) memilih rule engine dan menolak pool modal lintas mata uang tanpa konversi.
- [backtest/runner.py](agent/backtest/runner.py) memvalidasi konfigurasi, memuat data/signal engine, menjalankan engine, dan menghasilkan artefak. Bedakan dengan [src/core/runner.py](agent/src/core/runner.py), yang mengatur subprocess dan sandbox kode hasil generasi.
- `agent/backtest/engines/`, `loaders/`, `optimizers/`, metrics, validation, run card, correlation, regime, dan risk x-ray membentuk mesin riset kuantitatif.
- [paper_trade/schema.py](agent/src/tools/paper_trade/schema.py) dan [rules.py](agent/src/tools/paper_trade/rules.py) membentuk kontrak matching tersendiri. [paper_trade_routes.py](agent/src/api/paper_trade_routes.py) dan [accounts.py](agent/src/tools/paper_trade/accounts.py) membuktikan API akun paper persisten sudah tersedia. Komentar lama dalam package `__init__.py` yang menyebut persistence belum wired tidak mewakili implementasi route saat ini.
- [config/paths.py](agent/src/config/paths.py) menetapkan runtime root: parent config eksplisit, lalu `VIBE_TRADING_HOME`, lalu `~/.vibe-trading`. Runtime menggunakan kombinasi file JSON/JSONL, SQLite, cache data, dan artefak direktori sesuai subsystem; tidak ada satu database universal.
- Secret, state broker, mandate/audit, sesi, data pasar, serta laporan privat bukan source code. `.gitignore` memiliki daftar runtime paths yang harus dipertahankan.

## Fondasi IDX dan kesenjangan yang masih terbuka

- **Identitas:** `_market_hooks.py` mengenali saham reguler empat huruf `.JK` sebagai `id_equity` dan IDR; input `.JK` yang tidak didukung ditolak. Bare `BBCA` tetap `us_equity`. Grounding dan pencarian Yahoo mengenali `.JK`/IDX/IDR. Probe definisi commit baseline versus kode kini membuktikan `BBCA.JK: a_share → id_equity`.
- **Registry:** [idx.py](agent/src/markets/idx.py) menyediakan record bersumber/bertanggal dan normalisasi bare ticker hanya pada konteks snapshot IDX eksplisit. Universe resmi lengkap, company profiles tersinkronisasi, dan listing history belum diimpor. Snapshot tidak membuktikan tradability atau membership historis.
- **Fase 2B — impor referensi:** [idx_reference.py](agent/src/markets/idx_reference.py) memvalidasi JSON lokal untuk registry instrumen, kalender bounded dan primitive lot/tick, memakai model di atas. Metadata sumber/retrieval/usage terms dan SHA-256 dipertahankan; validasi struktur tidak menyertifikasi autentisitas, lisensi atau kelengkapan. Tidak ada download, instalasi snapshot global atau state runtime. [Kontrak impor dan sumber resmi](agent/IDX_REFERENCE.md) mencatat daftar saham BEI/KSEI, pengumuman kalender KSEI dan IDX Data Services. Ekspor lengkap, amendment kalender, entitlement provider dan rulebook historis masih terbuka.
- **Lanjutan riset 2B (2026-11-03):** HTML publik BEI memuat 962 record instrumen, tetapi ekspor lewat UI belum berhasil diverifikasi dan tanggal/revisi serta izin penggunaannya belum terbukti. Kalender KSEI awal Oktober 2025 dan penyesuaian Januari 2026 dibandingkan; daftar 22 penutupannya sama, sedangkan kelengkapan amendment sampai hari ini belum terbukti. Tautan keputusan II-A/II-X, pedoman perdagangan dan kondisi darurat ditemukan dari halaman resmi; PDF utama mengembalikan 403 sehingga tanggal berlaku/histori belum diterima. [Bukti dan batas akses](agent/IDX_REFERENCE.md#follow-up-evidence-instruments-calendars-and-rule-history).
- **Dokumentasi provider:** [riset provider](agent/IDX_PROVIDER_RESEARCH.md) mencatat sampel ZIP EoD resmi, hash, tanggal contoh, katalog 2026 serta terms 2024/2027. Katalog 2026 kini diperiksa per halaman dengan PDFium; hash cocok dengan unduhan sebelumnya. Deskripsi direct/indirect Professional tidak mencantumkan opening price, Basic juga tidak mencantumkan high/low. Data Reference mencakup laporan suspensi/unsuspensi; histori point-in-time belum terbukti. Katalog menunjukkan kebutuhan perjanjian/koordinasi dan NSP leased line untuk akses langsung, bukan API produksi publik. Unit volume, adjustment, schema produksi dan hak pemrosesan/display/retensi/redistribusi tetap belum terbukti. Tidak ada integrasi provider berizin atau aktivasi backtest.
- **Pemeriksaan akses lanjutan 2B:** kalender BEI tetap tidak memberikan lampiran terverifikasi; index KSEI tetap menunjuk pengumuman Januari, tanpa bukti kelengkapan amendment. Register aturan diperluas dengan I-L (suspensi), I-I (split/konsolidasi), I-N (delisting/relisting); ketiga PDF dan recheck II-A/II-X/pedoman mengembalikan 403. Isi/tanggal berlaku tidak diterima dari judul atau cuplikan pencarian. Rincian ada di [catatan akses](agent/IDX_REFERENCE.md#additional-public-access-checks-2026-11-03).
- **Disposisi lokal 2B:** kontrak importer, pemanggil, model registry/rules/calendar dan penolakan runner/composite dicocokkan dengan bukti yang sudah ada. [Paket input minimum dan prosedur penerimaan](agent/IDX_REFERENCE.md#phase-2b-disposition-and-minimum-handoff) serta [handoff teknis provider](agent/IDX_PROVIDER_RESEARCH.md#minimum-technical-handoff) kini tersedia. Satu ekspor instrumen berizin dengan tanggal/cakupan cukup untuk memulai review impor terbatas; kalender/rulebook/provider diterima terpisah. Persiapan lokal selesai untuk increment ini; normalisasi data nyata, penerimaan penuh 2B dan integrasi tetap menunggu input eksternal. Tidak ada bukti resmi baru, perubahan kode atau aktivasi backtest.
- **Data:** fallback `yahoo → yfinance → local` mengikuti registry yang ada; dua jalur Yahoo bukan sumber independen. Keduanya mensyaratkan deklarasi IDR dan menerima harian `1D`; timestamp dikonversi ke tanggal sesi Jakarta. Missing volume tetap unavailable. Provenance menyimpan sumber aktual, upaya gagal, currency, adjustment, retrieval/as-of, timezone/interval/unit dan quality. Cache v10 mempertahankan metadata. Freshness `not_evaluated`, delay `unknown`; adjustment HTTP Yahoo `unknown`, yfinance mengikuti `auto_adjust=True`. Jalur shared tool/MCP diuji melalui helper yang sama.
- **Aturan:** [idx_rules.py](agent/src/markets/idx_rules.py) menyediakan rule version/effective coverage, lot eksplisit, tier Decimal berdasarkan previous close, dan kalender bounded yang menolak tanggal di luar coverage. Belum ada default rulebook/kalender historis. [idx_bar_quality.py](agent/src/markets/idx_bar_quality.py) melaporkan bahaya bar harian vendor (baris di luar kalender yang diberikan, sesi hilang, harga berubah saat volume nol, hari volume nol yang hanya disebut `suspended` bila ada record suspensi bersumber) tanpa mengubah bar; belum dipanggil permukaan mana pun. Observasi sumber resmi, batas penggunaan, dan bukti yang masih dibutuhkan ada di [panduan](agent/IDX_FOUNDATION.md).
- **Backtest:** runner dan direct composite menolak IDX sampai model historis yang lengkap tersedia. Currency guard menolak IDR bercampur USD/CNY/HKD. Tidak ada simulasi IDX memakai aturan A-share/US/crypto sebagai substitusi.
- **Belum tersedia:** fundamental/disclosure point-in-time, corporate actions lengkap, suspensi, broker summary/foreign flow, screener/scoring IDX, workflow analis IDX, dashboard khusus, matching paper, portfolio/FX IDR end-to-end, dan konektor live IDX. Fase 3–8 tetap backlog.

## Verifikasi dan batasnya

- **Slice UI-01 label deklarasi identitas instrumen (2026-11-03):** `instrument_identity` kini memakai label khusus melalui peta `qualityStages` existing pada 11 locale, menggantikan pesan tahap belum tersedia untuk kode ini. Sebelas regresi baru awalnya gagal; tes terkait **427 passed** (5 file), frontend penuh **1231 passed (95 file)**, build dan browser sintetis locale id desktop 1280/mobile 390 lulus tanpa overflow horizontal/page error. Hasil sehat, pesan kode asing, satu akuisisi dan nonmutasi respons dipertahankan. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--label-deklarasi-identitas-instrumen). Backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 konsistensi deklarasi identitas (2026-11-03):** shared research tool menolak field provenance `symbol`/`market`/`exchange` yang bertentangan dengan instrumen permintaan melalui `instrument_identity`, sesudah gate currency dan sebelum timezone. Field absen tetap kompatibel; deklarasi yang ada tidak diperbaiki atau dinormalisasi. Sebanyak 26 regresi awal gagal; 35 tes baru, **755 regresi** (16 modul), Ruff dan empat probe CLI sintetis terisolasi lulus. [Kontrak dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--konsistensi-deklarasi-identitas). UI existing memakai pesan tahap belum tersedia untuk kode baru. Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. DATA-03/UI-01 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 bentuk kolom observasi (2026-11-03):** shared research tool memeriksa kolom datar dan satu kemunculan per field OHLCV sebelum memakai nilainya. Kolom bertingkat ditolak pada `price_values`; duplikat volume memakai `volume_values`, tanpa menebak level atau memilih duplikat. Kolom tambahan tidak dipakai tetap diterima. Sebanyak 19 tes baru; **730 regresi** dalam 16 modul, Ruff lint/format dan empat probe CLI sintetis terisolasi lulus. [Kontrak dan hasil](agent/IDX_PERSONAL_RESEARCH.md#data-03--bentuk-kolom-observasi). Provider/loader/rumus/frontend/dependency tidak berubah. Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. DATA-03/UI-01 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice UI-01 identitas observasi analisis (2026-11-03):** fingerprint SHA-256 backend ditampilkan utuh pada panel simbol sehat; metadata hilang/malformed ditandai tidak tersedia, tanpa hash/fetch tambahan. Cakupan interval/tanggal/close/volume serta batas autentisitas diterangkan pada 11 locale. Sebanyak 32 tes baru; **428 tes terkait**, frontend penuh **1220 passed** (95 file, dua worker), build dan browser sintetis id desktop 1280/mobile 390 lulus tanpa overflow/page error. [Kontrak dan hasil lengkap](agent/IDX_PERSONAL_RESEARCH.md#ui-01--identitas-observasi-analisis). Backend/provider/rumus/dependensi tetap sama. Backend penuh/safety, provider nyata, MCP eksternal dan deployment tidak diulang; UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Yahoo/yfinance tetap fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice UI-01 upaya sebelum fallback berhasil (2026-11-03):** simbol sehat dengan flag fallback eksplisit menampilkan upaya gagal dari provenance dalam urutan backend. Renderer bersama mempertahankan panel akuisisi gagal; nilai asing/hilang tetap netral, tanpa fetch/perhitungan tambahan. Dua key pada 11 locale, 23 tes tambahan, **352 tes terkait** serta frontend penuh **1188 passed** (95 file, dua worker); build serta browser sintetis locale id desktop 1280/mobile 390 lulus tanpa overflow horizontal. [Kontrak dan hasil lengkap](agent/IDX_PERSONAL_RESEARCH.md#ui-01--upaya-sebelum-fallback-berhasil). UI-01 penuh tetap terbuka; Yahoo/yfinance fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif.

- **Slice DATA-03 serialisasi provenance (2026-11-03):** object provenance yang gagal serialisasi JSON strict kini menjadi `null` dengan warning tersanitasi sebelum analisis. Simbol berdata ditolak melalui `currency_declaration`; simbol kosong mempertahankan alasan akuisisi dan tetangga sehat tetap tersedia. Sebanyak 28 regresi awal gagal; 38 tes tambahan, regresi 16 modul **711 passed**, Ruff dan empat probe CLI sintetis terisolasi lulus. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--serialisasi-provenance). Provider/routing/indikator/frontend/dependency tidak berubah. Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 serialisasi diagnostik (2026-11-03):** object diagnostik simbol tanpa data yang gagal serialisasi JSON kini menjadi `null` dengan warning tersanitasi. Hasil sehat, alasan unavailable dan object valid tetap dipertahankan. Sebanyak 18 regresi awal gagal; 23 tes tambahan, regresi 16 modul **673 passed**, Ruff serta empat probe CLI sintetis terisolasi lulus. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--serialisasi-diagnostik-akuisisi). Provider, routing, indikator, frontend dan dependency tidak berubah. Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 bentuk diagnostik akuisisi (2026-11-03):** container/entry `_diagnostics` non-object pada simbol tanpa data menjadi `null` dengan warning tersanitasi, tanpa menggugurkan simbol sehat atau mengubah object diagnostik valid. Absent/null tetap unknown. Sebanyak 18 regresi awal gagal; 23 tes baru dan regresi 16 modul **650 passed**, Ruff serta empat probe CLI sintetis terisolasi lulus. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--bentuk-diagnostik-akuisisi). Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance tetap fokus pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 bentuk provenance (2026-11-03):** container/entry provenance non-object kini menghasilkan penolakan `currency_declaration` per simbol; metadata tidak ditebak dari frame. Respons akuisisi non-object menghasilkan error terstruktur existing. Sebanyak 13 regresi awal mereproduksi `AttributeError`; 23 tes baru, regresi 15 modul **627 passed**, Ruff dan tiga probe CLI sintetis terisolasi lulus. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--bentuk-provenance). Full backend/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Yahoo/yfinance fokus riset pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **UI-01 konsistensi ringkasan volume:** Slice lokal konsistensi ringkasan volume selesai (2026-11-03): guard presentasi menandai seluruh `volume_coverage` tidak tersedia bila hitungan tersedia/hilang tidak cocok dengan total atau nol melebihi tersedia; batas subset juga diperiksa pada field valid yang ada. Field invalid individual tetap tidak tersedia tanpa menebak chart. Empat regresi awal gagal; 57 tes baru, tes terkait **361 passed**, frontend penuh **1165 passed** (95 file), build dan browser sintetis locale id desktop 1280/mobile 390 lulus tanpa overflow horizontal. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--konsistensi-ringkasan-volume). Backend/provider/rumus/dependensi tetap sama; UI-01/DATA-03 penuh tetap terbuka. Backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. Yahoo/yfinance tetap fokus riset pribadi, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice DATA-03 nilai kompleks (2026-11-03):** OHLCV kompleks Python/NumPy ditolak per simbol sebelum perbandingan/konversi float dan pemotongan lookback; kode kualitas existing dipertahankan. Sebelumnya nilai NumPy tertentu lolos dan bagian imajinernya hilang. Sebanyak 34 kasus kompleks lulus dengan `ComplexWarning` sebagai error; regresi 14 modul **604 passed**, termasuk **121 kasus kualitas**. Ruff serta CLI sintetis terisolasi lulus: exit 2, hasil parsial, simbol sehat tetap tersedia. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--penolakan-nilai-kompleks). Provider/rumus/UI/dependensi tidak berubah. Backend penuh/safety, frontend/build/browser, provider nyata, MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice UI-01 kelengkapan panel indikator (2026-11-03):** field existing sinyal/histogram MACD, Bollinger 20 bar dalam IDR dan rata-rata volume 20 bar dalam saham kini tampil tanpa perhitungan atau akuisisi baru. Presisi respons dipertahankan, termasuk nilai negatif kecil dan nol; metadata indikator hilang tetap tidak tersedia. Enam key pada 11 locale; 15 tes baru, tes terkait **304 passed**, frontend penuh **1108 passed** (95 file), build serta browser sintetis desktop 1280/mobile 390 lulus tanpa overflow horizontal. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--kelengkapan-panel-indikator). Backend/loader/provenance/rumus/dependensi tetap sama; backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice UI-01 tabel observasi OHLCV (2026-11-03):** tabel yang dapat dibuka lewat keyboard membaca bar respons chart, menampilkan OHLC IDR dan volume saham; nol/null serta tanggal tanpa pengisian dipertahankan. Delapan key pada 11 locale, 17 tes baru; tes terkait **289 passed**, frontend penuh **1093 passed** (94 file), build dan browser sintetis desktop 1280/mobile 390 lulus. Tabel 500 bar memakai area gulir terfokus, tanpa overflow horizontal halaman. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--tabel-observasi-ohlcv-harian). Backend/loader/provenance/rumus/dependensi tidak berubah; backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif, tanpa staging/commit.

- **Slice UI-01 validasi presentasi usia (2026-11-03):** kartu dan detail hanya menampilkan `recency` yang memenuhi kontrak format existing. Status/policy asing, field hilang/invalid atau scope berbeda mendapat pesan netral; UI tidak menghitung ulang usia/ambang/verdict. 68 kasus baru termasuk 11 locale; frontend penuh **1076 passed** (93 file), build serta browser sintetis desktop/mobile lulus tanpa overflow. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--validasi-presentasi-usia-observasi). Backend/loader/rumus/dependensi/locale tetap utuh; backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif, tanpa staging/commit.

- **Slice UI-01 diagnostik upaya sumber (2026-11-03):** panel gagal akuisisi menampilkan upaya sumber berurutan dari backend dengan label data kosong, fetch gagal dan sumber tidak tersedia. Metadata hilang/invalid/asing mendapat pesan netral; nilai mentah dan recovery text tidak ditampilkan. Tujuh key pada 11 locale; tes terkait **216 passed**, frontend penuh **1007 passed** (93 file, sebelum satu tes tambahan pemisahan validasi yang lulus pada run terkait), build serta browser sintetis desktop 1280/mobile 390 lulus tanpa overflow. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--diagnostik-upaya-sumber). Backend/provider/rumus/dependensi tidak berubah; backend penuh/safety, provider nyata, CLI/MCP eksternal dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda dan backtest IDX nonaktif. Tanpa staging/commit.

- **Slice UI-01 cakupan volume (2026-11-03):** panel simbol sehat menampilkan empat hitungan `volume_coverage` dari backend, tanpa menghitung ulang chart/lookback. Nol tetap tersedia; metadata hilang/invalid ditandai tidak tersedia; simbol unavailable tidak mendapat ringkasan buatan. Enam key pada 11 locale. Tes terkait **196 passed**, frontend penuh **988 passed** (93 file), build serta browser sintetis desktop 1280/mobile 390 lulus tanpa overflow horizontal. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--cakupan-volume). Backend/loader/rumus/dependensi tidak berubah; full backend/safety, provider nyata dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX nonaktif; tanpa staging/commit.

- **Slice DATA-03 cakupan volume observasi (2026-11-03):** JSON tool bersama menambah `volume_coverage` dari bar analisis aktual: jumlah bar, volume tersedia, hilang dan nol. Nol termasuk tersedia; null tidak menjadi nol; gap sesi tidak diisi atau disimpulkan sebagai suspensi. Histori pendek, nonmutasi, HTTP parsial dan CLI diuji. Regresi 14 modul **570 passed**, termasuk **87 kasus kualitas**; Ruff lint/format dan probe CLI sintetis terisolasi lulus (exit 2, partial, 20 bar: 19 tersedia/1 hilang/1 nol). [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--cakupan-volume-observasi). UI belum menampilkan ringkasan ini; frontend/build/browser, backend penuh/safety, provider nyata dan deployment tidak diulang. DATA-03/UI-01 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka; backtest IDX nonaktif, Index Alpha ditunda, tanpa staging/commit.

- **Slice DATA-03 batas numerik indikator (2026-11-03):** hasil analisis diperiksa dengan serialisasi JSON strict di dalam batas kegagalan per simbol. NaN/Infinity hasil aritmetika dari input finite menghasilkan `indicator_calculation`; hasil sehat dan null indikator yang sah tetap tersedia. Regresi 14 modul **562 passed**, termasuk **79 kasus kualitas**; Ruff lint/format serta probe CLI sintetis terisolasi lulus (exit 2, partial, satu simbol sehat 20 bar). [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--batas-numerik-indikator). Warning NumPy pada fixture ekstrem, anyio/Starlette existing serta koneksi tes indikator yang diblokir pytest-socket tercatat. Frontend/build/browser, full backend/safety, provider nyata dan deployment tidak diulang. DATA-03/UI-01 penuh dan RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif, tanpa staging/commit.

- **Slice DATA-03 tipe numerik observasi (2026-11-03):** tool riset bersama menolak boolean pada OHLCV dan menangani overflow konversi numerik sebagai penolakan per simbol dengan kode existing. Nilai invalid sebelum tail tidak tersembunyi; hasil sehat tetap tersedia. Regresi 14 modul **557 passed**, termasuk **74 kasus kualitas**; Ruff lint/format serta probe CLI sintetis terisolasi lulus. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--tipe-numerik-observasi). Frontend/build/browser, full backend/safety, provider nyata dan deployment tidak diulang. DATA-03/UI-01 penuh dan RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif, tanpa staging/commit.

- **Slice UI-01 cakupan observasi (2026-11-03):** panel menampilkan jumlah bar analisis dari metadata backend dan batas bar dari respons permintaan secara terpisah, dengan penjelasan bahwa jumlah bukan bukti kelengkapan sesi bursa. Jumlah hilang/invalid tidak ditebak dari chart. Tiga key pada 11 locale; tes terkait **169 passed**, frontend penuh **961 passed** (93 file), build serta browser sintetis desktop 1280/mobile 390 lulus tanpa overflow. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--cakupan-observasi). Tidak ada perubahan backend/dependensi; backend/full safety, provider nyata dan deployment tidak diulang. UI-01/DATA-03 penuh dan RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda, backtest IDX nonaktif; belum staging/commit.

- **Slice UI-01 waktu provenance (2026-11-03):** retrieval ditampilkan dengan zona WIB eksplisit, as-of sesi sumber dibedakan dari sesi terakhir analisis, dan metadata waktu hilang/invalid ditandai tidak tersedia. Dua key pada 11 locale; tes terkait **149 passed**, frontend penuh **941 passed** (93 file), build dan browser sintetis desktop 1280/mobile 390 lulus tanpa overflow. Chart sehat, metadata invalid dan data kosong diperiksa melalui route/tool existing. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#ui-01--waktu-wib-dan-tanggal-provenance). Backend/full safety, provider nyata dan deployment tidak diulang. Warning Vite existing tetap tercatat; UI-01/DATA-03 penuh serta RULE-01/DATA-01/RESEARCH-01 tetap terbuka. Index Alpha ditunda, backtest IDX nonaktif; belum staging/commit.

- **Slice UI-01 tahap penolakan observasi (2026-11-03):** watchlist menampilkan label untuk 11 kode `quality_issue.code` pada seluruh 11 locale, pesan tahap belum tersedia untuk kode hilang/asing, serta batas bahwa kode hanya tahap pertama yang gagal. Data kosong/kegagalan akuisisi tetap memakai pesan existing. Tes terkait **115 passed**, frontend penuh **907 passed** (92 file), build ulang dan browser sintetis desktop 1280/mobile 390 lulus tanpa overflow horizontal. Build awal gagal TS2550 pada `Object.hasOwn`; diperbaiki memakai `hasOwnProperty.call` sesuai target proyek. Chart sehat dan pergantian ke simbol kosong/ditolak diperiksa melalui endpoint/tool existing dalam harness QA loopback terisolasi. [Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#ui-01--tahap-penolakan-observasi). Warning Vite configLoader/chunk dan LF/CRLF locale existing tetap tercatat. Backend/full safety, provider nyata dan deployment tidak diulang. UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX nonaktif. Tidak ada staging atau commit.

- **Slice DATA-03 diagnostik penolakan (2026-11-03):** tool bersama menambah `quality_issue.code` untuk tahap validasi yang gagal, mempertahankan `reason` existing dan hasil parsial. Regresi 14 modul **538 passed**, termasuk **55 kasus kualitas**; Ruff lint/format dua file lulus. Probe CLI subprocess dengan akuisisi sintetis dan runtime sementara menghasilkan exit 2, status partial, `adjustment_declaration` untuk simbol invalid serta 20 bar untuk simbol sehat. [Kontrak, perintah dan batas](agent/IDX_PERSONAL_RESEARCH.md#data-03--diagnostik-penolakan-observasi). Warning existing anyio/Starlette dan percobaan koneksi indikator yang diblokir pytest-socket tercatat. Frontend/build/browser, full backend/safety, provider nyata dan deployment tidak diulang. DATA-03/UI-01 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda dan backtest IDX nonaktif. Tidak ada staging atau commit.

- **Slice DATA-03 deklarasi adjustment (2026-11-03):** metadata adjustment wajib berupa teks nonkosong; `unknown` eksplisit tetap diterima tanpa inferensi dari nama sumber. Fixture aksi sintetis membuktikan harga/SMA tidak disesuaikan ulang, termasuk jalur fallback Yahoo → yfinance `auto_adjust=True`; HTTP parsial dan CLI exit 2 untuk metadata hilang diuji. Regresi 14 modul **520 passed**, Ruff lint/format tiga file dan `git diff --check` lulus. Warning existing anyio/Starlette dan percobaan koneksi indikator yang diblokir pytest-socket tetap tercatat. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--deklarasi-adjustment-dan-fixture-aksi-sintetis). Frontend/build/browser, full backend/safety, probe Yahoo nyata dan deployment tidak diulang. Kalibrasi aksi korporasi nyata, DATA-03/UI-01 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX nonaktif. Tidak ada staging atau commit.
- **Slice UI-01 usia observasi (2026-11-03):** watchlist kini menampilkan warning per simbol dan detail usia, tanggal bar terakhir, tanggal acuan serta ambang dari `recency` backend; respons tanpa field tersebut ditandai belum tersedia. Data/chart/provenance tetap tampil. Sembilan key pada 11 locale ditambahkan; tes terkait **88 passed**, frontend penuh **880 passed** (92 file), build dan `git diff --check` lulus. Browser memakai endpoint/tool existing dengan akuisisi sintetis pada server QA loopback sementara: warning 15 hari, status 0 hari, chart dan hasil parsial tampil; desktop 1280/mobile 390 tidak overflow horizontal. Warning Vite configLoader/chunk existing tetap muncul. Backend/full safety, probe Yahoo nyata dan deployment tidak diulang. [Kontrak dan hasil](agent/IDX_PERSONAL_RESEARCH.md#ui-01--usia-observasi-pada-watchlist). UI-01/DATA-03 penuh, RULE-01/DATA-01/RESEARCH-01 tetap terbuka, Index Alpha ditunda dan backtest IDX nonaktif. Tidak ada staging atau commit.
- **Slice DATA-03 usia observasi (2026-11-03):** JSON API/agent/MCP/CLI kini menyertakan `recency` dari bar terakhir aktual terhadap tanggal akhir permintaan. Usia >14 hari kalender memicu warning tersanitasi; data valid tetap tersedia. Ini alarm pribadi, bukan verifikasi sesi bursa, suspensi atau delay. Provenance loader tetap utuh; UI belum menampilkan field pada run backend ini (follow-up UI-01 tercatat di atas). Regresi 14 modul **507 passed**, termasuk **25 kasus kualitas**; Ruff lint/format kedua file kode/tes dan `git diff --check` lulus. Warning existing anyio/Starlette dan koneksi tes indikator yang diblokir pytest-socket tetap tercatat. Full backend/safety, frontend/build, browser, probe Yahoo nyata dan deployment tidak diulang. [Kontrak dan bukti](agent/IDX_PERSONAL_RESEARCH.md#data-03--diagnostik-usia-observasi). DATA-03 penuh/RULE-01/DATA-01/RESEARCH-01 tetap terbuka; Index Alpha ditunda, backtest IDX tetap nonaktif. Tidak ada staging atau commit.
- **Slice DATA-03 riset pribadi (2026-11-03):** tool bersama memvalidasi seluruh frame yang diterima sebelum pemotongan lookback dan mensyaratkan metadata interval `1D` serta unit volume `shares`. Observasi invalid tetap unavailable; simbol sehat tetap tersedia. Fixture sintetis mencakup OHLCV rusak di luar tail, metadata hilang/tidak kompatibel, nol/null volume, gap tanggal dan nonmutasi frame. Regresi 14 modul **497 passed**, termasuk **15 kasus kualitas**; Ruff lint/format tes dan `git diff --check` lulus. Tidak ada perubahan frontend, rumus indikator atau routing provider. Warning deprecation existing dan percobaan koneksi tes indikator existing yang diblokir pytest-socket tercatat. Frontend/build, full backend/safety, probe Yahoo nyata, browser dan deployment tidak diulang. [Detail](agent/IDX_PERSONAL_RESEARCH.md#data-03--validasi-observasi-riset-pribadi). DATA-03/RULE-01/DATA-01/RESEARCH-01 tetap terbuka; backtest IDX tetap nonaktif. Tidak ada commit.
- **MVP-I18N (2026-11-03):** 312 teks Riset IDX (39 per locale) pada ar/de/es/fa/ja/ko/pt-BR/zh-CN diterjemahkan, termasuk navigasi dan pencarian simbol; en/id/tr dipertahankan. Key/interpolation parity dan rendering halaman/pencarian kosong delapan locale diuji: targeted **77 passed**, frontend penuh **874 passed** (92 file), build dan `git diff --check` lulus. Teks di luar fitur IDX tetap sama; warning Vite configLoader/ukuran chunk existing tetap muncul. Backend/Ruff, probe Yahoo nyata, browser dan deployment tidak diulang. [Detail verifikasi](agent/IDX_PERSONAL_RESEARCH.md#mvp-i18n--terjemahan-riset-idx). Tidak ada commit; RULE-01/DATA-01/RESEARCH-01 tetap terbuka dan backtest IDX tetap nonaktif.
- **MVP-R02 (2026-11-03):** pencarian watchlist melalui `search_symbol(market="idx")`, Yahoo-only tanpa connector akun, endpoint ber-auth dan pemilihan kandidat saham reguler `.JK` ber-venue IDX/IDR tersedia. Hasil adalah kandidat provider, bukan master resmi. Regresi backend pencarian/data/identitas/MCP **234 passed**; frontend penuh **858 passed** (92 file), termasuk halaman/klien HTTP **23 passed**; build dan Ruff lulus. Kueri ambigu, hasil kosong/kegagalan, pembatalan respons lama, duplikasi dan kapasitas watchlist diuji. Probe jaringan dan deployment tidak diulang; batas acceptance RULE-01/DATA-01/RESEARCH-01 tetap terbuka.
- **MVP riset pribadi Yahoo (2026-11-03):** halaman `/research/idx`, endpoint ber-auth, tool agent/MCP `idx_research` dan CLI modul tersedia. Watchlist manual maksimum 8 simbol `.JK`, chart harian, indikator existing dan provenance memakai satu observasi; input salah/hasil parsial tetap terlihat. Regresi data/IDX/indikator **499 passed**; run akhir fitur/MCP **50 passed**; frontend penuh **850 passed**, targeted akhir **54 passed**. Probe CLI nyata BBCA/BBRI/TLKM masing-masing **60 bar** sampai 2026-10-30 berhasil melalui Yahoo, IDR, adjustment unknown; terpisah dari browser QA sintetis. Detail, perintah, batas izin dan titik lanjut: [handoff riset pribadi](agent/IDX_PERSONAL_RESEARCH.md). Index Alpha ditunda. RULE-01/DATA-01/RESEARCH-01 tetap terbuka; backtest IDX tetap nonaktif. Belum deployment atau commit.

- Probe melalui Playground Index Alpha oleh pengguna (2026-11-03): respons OHLCV `success: true`, 20 bar tanggal 2–30 Januari 2026; formulir menunjukkan BBCA, rentang 1–31 Januari, sumber IDX as-traded. Angka finite, volume nonnegatif dan batas high/low konsisten; kalender lengkap, unit, hak penggunaan dan integrasi loader belum terbukti. Respons sebelumnya adalah broker summary, bukan OHLCV. [Batas bukti dan provenance](agent/IDX_PROVIDER_RESEARCH.md#user-operated-playground-response-observation). Tidak ada raw rows/token disimpan di repo atau backtest diaktifkan.

- Riset dokumentasi Index Alpha (2026-11-03): dokumentasi publik kini mencantumkan API OHLCV harian, base URL, autentikasi Bearer dan batas akses. Ini bukti kontrak yang dinyatakan provider, belum respons data aktual, entitlement atau penerimaan DATA-01. Detail dan batas cakupan ada di [riset provider](agent/IDX_PROVIDER_RESEARCH.md). Tidak ada perubahan kode, akun, impor snapshot atau aktivasi backtest.

- Sesi disposisi lokal 2B (2026-11-03): dokumentasi saja, tanpa permukaan runtime baru. Pemeriksaan lima dokumen dengan Python proyek menghasilkan **64 tautan lokal/anchor valid, 0 masalah**; whitespace dan `git diff --check` lulus. Perbandingan SHA-256 awal/akhir menunjukkan hanya lima dokumen status/backlog/fondasi/referensi/provider berubah; 22 file kode/fixture dan dua README sebelumnya tetap sama, tanpa file tambahan/hilang. Tes 102/435 dan Ruff tidak diulang karena kode tidak berubah; hasilnya tetap bukti sesi sebelumnya. Tidak ada permintaan jaringan ulang, impor data resmi, integrasi provider, deployment, staging atau commit.
- Sesi pemeriksaan katalog/akses lanjutan (dokumentasi saja): command dua modul importer/fondasi di bawah kembali menghasilkan **102 passed, 1 warning** (deprecation anyio/pytest). Ruff lint dan `ruff format --check` pada importer/tesnya lulus; 52 tautan lokal termasuk anchor serta whitespace pada lima dokumen lulus; `git diff --check` lulus. SHA-256 22 file kode/fixture uncommitted cocok dengan awal sesi. Hanya lima dokumen status/fondasi/referensi/provider/backlog diubah; tidak ada permukaan runtime baru. Regresi 435, full backend/frontend, safety, integrasi provider berizin dan deployment tidak dijalankan ulang. Tidak ada staging, commit, impor snapshot resmi atau aktivasi backtest.
- Sesi riset lanjutan 2B (dokumentasi saja, tanpa permukaan runtime baru): `.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_reference.py agent/tests/test_idx_foundation.py -q --disable-socket`: **102 passed**, satu warning deprecation plugin anyio/pytest. Ruff pada importer/tesnya lulus; tautan lokal dan whitespace pada lima dokumen yang diubah diperiksa, `git diff --check` lulus. Hash 22 file kode/fixture uncommitted tetap sama sepanjang perubahan dokumentasi. Angka 435 di bawah adalah verifikasi sesi sebelumnya; full backend/frontend, safety, deployment dan integrasi provider berizin tidak dijalankan ulang. Tidak ada snapshot resmi yang diimpor atau backtest diaktifkan.
- Lanjutan Fase 2B: `.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_reference.py agent/tests/test_idx_foundation.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_market_identity_parity.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_loader_retry_helpers.py -q --disable-socket`: **435 passed**. Ruff lint/format lulus pada dua file Python baru; CLI modul berhasil memvalidasi fixture sintetis (1 record, structure_only) dan menolak file hilang. Black belum tersedia (`No module named black`); dependency tidak ditambahkan. Full backend, frontend, safety dan probe provider tidak dijalankan ulang untuk increment importer ini; hasil historis di bawah tetap terpisah. Satu warning deprecation plugin anyio/pytest muncul.
- Interpreter pengujian: `.venv/idx312/Scripts/python.exe`, Python 3.12.13. Dependensi runtime berhasil dipasang dengan hash dari `desktop/electron/requirements-windows-lock.txt` (185 paket). Percobaan awal Python 3.11 gagal: `scipy==1.18.0 depends on Python>=3.12`; pin tidak diubah. Dev tools mengikuti constraint `pyproject.toml` (pytest 9.2.0, pytest-socket 0.8.1, Ruff 0.17.3).
- Perintah regresi dijelaskan di [panduan reproduksi](agent/IDX_FOUNDATION.md). Regresi backend diperluas (classifier, registry, composite, Yahoo/yfinance, local, shared data, grounding/search, cache): **752 passed, 3 skipped**. Tiga skip adalah pembacaan Parquet lokal yang membutuhkan engine pandas opsional `pyarrow`, bukan tes fondasi IDX. Run tambahan setelah penguatan validasi rulebook: **87 passed, 3 skipped**; run akhir setelah pembatasan fallback lintas market: **163 passed, 3 skipped**, menggunakan `test_idx_foundation.py`, `test_market_data.py`, `test_market_data_serving_source.py`, `test_market_identity_parity.py`, dan `test_local_loader_source_revision.py`. Tes offline memakai fixture sintetis, termasuk null volume, pergantian tanggal Jakarta, error versus empty, fallback dan roundtrip Parquet.
- Safety: `python -m pytest agent/tests/test_sdk_order_gate.py agent/tests/test_mandate_enforcement.py agent/tests/test_killswitch_blocks_orders.py agent/tests/test_readonly_default.py -q --allow-hosts=127.0.0.1,::1`: **121 passed**. Percobaan `--disable-socket` menghasilkan 5 kegagalan karena socketpair internal asyncio Windows diblokir (`pytest_socket.SocketBlockedError`), bukan koneksi broker. Run loopback memperbaiki konfigurasi validasi tanpa perubahan kode safety.
- Frontend: `npm ci` berhasil; `npm run test:run`: **91 file / 846 tes lulus**; `npm run build`: **berhasil**. Ada empat advisory npm kategori low dan peringatan chunk >500 kB/configLoader; dependency tidak diperbarui otomatis.
- Probe provider terpisah, runtime/home sementara: Yahoo HTTP `BBCA.JK` dan `BBRI.JK`, rentang 2026-10-26 s.d. 2026-10-30, **masing-masing 5 bar**, currency IDR, as-of 2026-10-30. Ini bukan verifikasi semua ticker, corporate actions, unit volume independen, SLA, lisensi redistribusi, atau kelengkapan historis. Retrieval UTC pada artefak probe: 2026-11-02T20:40:55Z (2026-11-03 WIB).
- Smoke import backend terisolasi berhasil untuk `backtest.runner`, `src.market_data`, `api_server`, dan `mcp_server`. Tes keseluruhan backend dan deployment belum diverifikasi. Tidak menjalankan server eksternal, akun broker, mandate nyata, order, kredensial, atau publikasi. Sumber Yahoo publik diuji tanpa autentikasi; Dokumentasi publik Index Alpha kini ditemukan; akses akun dan integrasi runtime belum dikonfigurasi.
- `RTK.md` masih tidak ditemukan. Sesuai `CONTRIBUTING.md`, instruksi agen tetap lokal/untracked; `AGENTS.md` di-ignore. Tidak ada staging atau commit yang dibuat.

## Arah pengembangan

Usulan urutan kerja adalah baseline yang dapat dijalankan, identitas/routing IDX dan kualitas data, riset read-only, backtest dengan aturan terverifikasi, lalu paper trading. Konektor order live IDX merupakan fase terpisah setelah kebutuhan dan akses broker jelas. Scope awal mengikuti master prompt pengguna: saham reguler IDX, riset harian read-only dalam IDR, tanpa order broker nyata. Tooling impor Phase 2B tersedia; penerimaan penuh menunggu referensi historis/provider coverage yang memadai. Kriteria rinci tetap di backlog.

Rincian prioritas, dependensi, bukti penerimaan, dan keputusan yang belum tersedia berada hanya di [TODO.md](TODO.md). Pedoman kerja agen berada di [AGENTS.md](AGENTS.md).
