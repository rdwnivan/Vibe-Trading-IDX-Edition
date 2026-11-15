# Keputusan IDX Research Preview — 2026-11-15

Dokumen ini mencatat tiga keputusan pengguna untuk sesi 2026-11-15 (Asia/Jakarta)
dan draf README Bahasa Indonesia untuk scope rilis yang disepakati. Ini **draf**:
tidak ada tag, rilis, paket atau publikasi yang dibuat, dan README di root belum
diubah. Status penerimaan tetap dimiliki [PROJECT_STATUS.md](../PROJECT_STATUS.md)
dan [TODO.md](../TODO.md).

## 1. Disposisi EODHD (DATA-01)

**Keputusan.** EODHD **tidak** dipakai sebagai loader, sumber utama atau
fallback. Statusnya hanya rujukan rekonsiliasi pribadi: operator boleh
membandingkan bar vendor lain dengan data EODHD miliknya sendiri di luar
repository.

**Alasan** (bukti di [riset provider](IDX_PROVIDER_RESEARCH.md#eodhd-free-plan-probe-and-yahoo-comparison--2026-11-13)):

- Syarat EODHD mengizinkan penyimpanan dan analisis pribadi nonkomersial, tetapi
  **melarang tampilan dan redistribusi**. Halaman riset, API, MCP dan CLI semuanya
  menampilkan atau meneruskan bar, sehingga memakai EODHD di sana bertentangan
  dengan syarat itu.
- Syarat memuat **disclaimer akurasi**: data tidak dijamin akurat atau real-time,
  dan tanpa garansi.
- Syarat **tidak mengatur penggunaan untuk LLM**. Bar yang diteruskan ke agen atau
  model pihak ketiga tidak punya dasar izin yang tertulis.
- Bukti teknis menambah alasan: baris hari libur dengan harga sentinel
  999.999,9999 untuk sebagian simbol, OHLC mentah dengan volume yang sudah
  disesuaikan split, dan kedalaman histori `.JK` yang belum diketahui pada paket
  gratis ([split dan baris libur](IDX_PROVIDER_RESEARCH.md#eodhd-split-handling-history-depth-and-holiday-rows--2026-11-14)).

**Akibat.** Tidak ada loader, entri fallback, kunci env baru atau fixture berisi
data EODHD. Token di `agent/.env` tetap milik pengguna dan tidak dipakai kode.
Paket berbayar (termasuk Historian) tetap ditunda. **DATA-01 tetap terbuka**
karena belum ada provider IDX yang lolos semua kriteria (cakupan, histori,
adjustment, corporate actions, unit volume, izin pemakaian dan penanganan tidak
tersedia). Yahoo/yfinance tetap kandidat existing, bukan sumber yang lolos.

## 2. Permintaan II-A ke BEI tidak dikirim

**Keputusan.** Permintaan teks II-A ke BEI (rute lewat halaman Hubungi Kami yang
dicatat di [rujukan](IDX_REFERENCE.md#kpei-ii-5-2026-text-guarantee-fund-and-calendar-access-2026-11-14))
**tidak dikirim**.

**Alasan.** Lampiran II-A **Kep-00158/BEI/10-2026** (berlaku 20 Oktober 2026)
sudah dapat dibaca publik: URL lampiran memberi HTTP 200 ke sesi browser biasa
sejak 2026-11-12 dan isinya sudah dibaca serta di-hash
([catatan baca](IDX_REFERENCE.md#ii-a-kep-00158bei10-2026-read-2026-11-12)).
Itu cukup untuk scope research preview, yang tidak menjalankan aturan
perdagangan.

**Batas yang tetap terbuka.** Teks II-A yang berlaku sebelum 20 Oktober 2026
(antara lain Kep-00196, Kep-00003, Kep-00136 dan Kep-00157) tetap belum dibaca,
karena tidak ditemukan salinan publiknya. Jadi rulebook bertanggal untuk masa
sebelum 20 Oktober 2026 tetap tidak tersedia, dan **backtest IDX tetap ditolak**.
Keputusan ini dapat ditinjau lagi bila backtest historis masuk scope.

## 3. Scope rilis: "IDX research preview" (RELEASE-01)

**Masuk scope:**

- Riset IDX pribadi read-only: watchlist manual `/research/idx`, tool
  `idx_research` untuk agen/MCP, endpoint API dan CLI tanpa LLM.
- Audit kualitas data yang sudah dikembalikan riset: cakupan volume, peringatan
  harga saat volume nol (`bar_audit` v1), recency 14 hari kalender, provenance,
  dan diagnostik penolakan per simbol.
- File kalender dan record peristiwa bersumber yang **opt-in** lewat
  `VIBE_TRADING_IDX_CALENDAR_PATH` dan `VIBE_TRADING_IDX_EVENT_RECORDS_PATH`.

**Di luar scope:** backtest IDX, paper matching, Shadow Account dan live trading
IDX. Semuanya tetap ditolak atau tidak disambungkan untuk IDX. Juga di luar scope:
universe instrumen resmi, rulebook bertanggal, model fee/pajak, provider
berbayar, uji LLM nyata, deployment publik dan multiuser.

**Gate rilis yang masih harus dipenuhi sebelum RELEASE-01 dicentang:** alur
bersih install → riset diverifikasi pada platform sasaran (Windows sudah diuji
lokal; Linux belum), tes/build relevan lulus pada commit rilis, keterbatasan
tercatat di README, dan keputusan hak data untuk Yahoo/yfinance sesuai
pemakaian. Backtest tidak masuk scope, jadi kriteria "research → backtest"
berlaku hanya untuk bagian riset. Packaging atau publish tidak dijalankan dari
dokumen ini.

## Draf README (Bahasa Indonesia)

Draf pengganti bagian "🇮🇩 IDX Edition" di [README_id.md](../README_id.md). Isinya
hanya perilaku yang tersedia pada `feature/idx-edition` per 2026-11-15.

````markdown
## 🇮🇩 IDX Edition — research preview

Fork ini menambahkan **riset pribadi read-only** untuk saham Bursa Efek Indonesia.
Ini pratinjau riset, bukan alat transaksi.

**Yang tersedia**

- Simbol `XXXX.JK` dikenali sebagai `id_equity` dalam IDR dan diambil lewat loader
  Yahoo/yfinance yang sudah ada, dengan tanggal sesi Asia/Jakarta dan volume
  dalam lembar saham. Ticker tanpa akhiran tetap pada arti pasarnya semula.
- Watchlist manual di `/research/idx` (maksimum 8 saham, data harian): chart close,
  indikator teknikal, asal data, peringatan kebaruan 14 hari kalender, cakupan
  volume, dan peringatan bar bervolume nol yang harganya berubah. Simbol yang
  gagal tetap tampil beserta tahap penolakannya.
- Riset yang sama tersedia sebagai tool `idx_research` untuk agen dan MCP,
  endpoint `POST /api/research/idx`, dan CLI tanpa akun LLM:

  ```bash
  cd agent
  python -m src.tools.idx_research_tool BBCA.JK BBRI.JK --lookback 200
  ```

- Opsional: file kalender sesi dan record peristiwa (suspensi, delisting, aksi
  korporasi) yang bersumber dan disediakan operator. Ekspor path-nya sebagai
  variabel lingkungan sebelum menjalankan server API, MCP atau CLI:

  ```bash
  export VIBE_TRADING_IDX_CALENDAR_PATH=~/.vibe-trading/idx/bei_sessions_2026.json
  export VIBE_TRADING_IDX_EVENT_RECORDS_PATH=~/.vibe-trading/idx/event_records.json
  ```

  Riset lalu melaporkan bar di hari bursa tutup, sesi tanpa bar, status suspensi,
  akhir seri dalam hitungan sesi, dan perubahan harga di tanggal ex. Bar tidak
  diubah. Format file ada di [IDX_FOUNDATION.md](agent/IDX_FOUNDATION.md); contoh
  kalender BEI 2026 bersumber ada di
  `agent/tests/fixtures/idx_calendar/bei_sessions_2026.json`. Tidak ada kalender
  atau daftar peristiwa bawaan.

**Batas**

- Backtest, paper matching, Shadow Account dan live trading IDX **tidak tersedia**
  dan tetap ditolak.
- Data Yahoo/yfinance tertunda dan dapat memuat baris pengganti atau volume yang
  keliru; temuan audit adalah peringatan, bukan koreksi. Hak pemakaian data
  mengikuti syarat masing-masing penyedia.
- Kalender bersumber hanya mencakup tahun yang ada di file operator dan dapat
  direvisi BEI. Tanpa file, pemeriksaan kalender dan suspensi tidak berjalan.
- Bukan universe instrumen resmi, bukan rekomendasi investasi.

**Pemulihan**

- File kalender/record yang rusak atau hilang tampil sebagai "tidak tersedia";
  riset tetap jalan. Perbaiki file atau kosongkan env-nya.
- Simbol berstatus tidak tersedia menampilkan sumber yang dicoba dan alasannya;
  coba lagi nanti atau periksa koneksi.

Lihat [arsitektur dan batasan](agent/IDX_FOUNDATION.md),
[panduan riset pribadi](agent/IDX_PERSONAL_RESEARCH.md) dan
[rujukan aturan resmi](agent/IDX_REFERENCE.md).
````
