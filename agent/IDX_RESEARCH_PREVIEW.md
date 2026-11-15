# Keputusan IDX Research Preview — 2026-11-15

Dokumen ini mencatat keputusan pengguna untuk sesi 2026-11-15 (Asia/Jakarta):
tiga keputusan awal, keputusan hak distribusi fakta bersumber BEI (bagian 4),
dan draf README Bahasa Indonesia untuk scope rilis yang disepakati. Tidak ada
tag, rilis, paket atau publikasi yang dibuat. Draf README diterapkan ke
[README_id.md](../README_id.md) pada 2026-11-15 (bagian 5). Status penerimaan tetap dimiliki [PROJECT_STATUS.md](../PROJECT_STATUS.md)
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

## 4. Hak distribusi fakta bersumber BEI (DATA-03)

**Keputusan (2026-11-15, Asia/Jakarta).** Kalender sesi 2026
([bei_sessions_2026.json](tests/fixtures/idx_calendar/bei_sessions_2026.json))
dan record suspensi MLPT
([mlpt_2026-03_suspension.json](tests/fixtures/idx_event_records/mlpt_2026-03_suspension.json))
**boleh tetap** di repository publik.

**Alasan.** Isinya hanya fakta tanggal dan nomor pengumuman, bukan salinan PDF
atau data harga BEI. Pemakaiannya nonkomersial dan selalu disertai atribusi
serta tanggal akses, sesuai klausul 6
[syarat situs BEI](IDX_PRIMARY_INPUT_DISCOVERY.md#official-website-permission-evidence--2026-11-05).

**Syarat yang diuji.**

- Setiap nomor pengumuman BEI di field `source` file JSON kedua folder diikuti
  tanggal pengumuman dan tanggal baca, dengan pola
  `<nomor> (<tanggal pengumuman>; read YYYY-MM-DD`. Tanggal baca tidak boleh
  lebih awal dari tanggal pengumuman.
- Kedua folder punya README yang menyebut sumber (BEI), atribusi, tanggal
  akses, sifat nonkomersial, tautan syarat situs, dan bahwa PDF/teks
  pengumuman tidak disalin. Selain README, folder hanya boleh berisi JSON.
- Tes [test_idx_bei_fixture_attribution.py](tests/test_idx_bei_fixture_attribution.py)
  gagal bila salah satu syarat itu dilanggar.

**Tetap dilarang:** menyalin PDF atau teks pengumuman BEI, menyimpan data harga
atau statistik BEI, scraping/crawling situs BEI, dan penggunaan komersial.
Keputusan ini tidak memberi izin diseminasi komersial dan tidak berlaku untuk
data harga dari vendor mana pun.

## 5. Gate RELEASE-01: hak data, verifikasi Linux dan README (2026-11-15)

**Hak data Yahoo/yfinance (keputusan pengguna).** Preview hanya untuk pemakaian
pribadi lokal oleh satu operator. Bar Yahoo tidak di-commit, tidak dibundel ke
paket dan tidak diredistribusi. README menyatakan bahwa pemakaian data mengikuti
syarat Yahoo dan menjadi tanggung jawab operator. Tidak ada deployment publik
atau multiuser.

**Pemuatan `.env` yang terbukti.** Tes
[test_idx_research_env_file.py](tests/test_idx_research_env_file.py) menjalankan
lifespan asli `api_server.app` dengan probe jaringan preflight diganti stub dan
slot `.env` dialihkan ke folder sementara (file `.env` milik operator tidak
dibaca):

- Startup API (`run_preflight` → `_ensure_dotenv`) membaca **file pertama yang
  ada** di antara `~/.vibe-trading/.env`, `agent/.env` dan `./.env`.
  `VIBE_TRADING_IDX_CALENDAR_PATH` di `~/.vibe-trading/.env` membuat
  `POST /api/research/idx` melaporkan kalender `loaded`; tanpa file home,
  `agent/.env` dipakai.
- Bila `~/.vibe-trading/.env` ada tetapi tidak memuat variabel itu, nilai di
  `agent/.env` **tidak** dibaca.
- Variabel yang sudah di-export menang atas `.env` (`override=False`).
- CLI `python -m src.tools.idx_research_tool` tidak membaca `.env` apa pun.
- Server MCP memanggil `_ensure_dotenv` yang sama di `main()`
  ([test_mcp_server_dotenv.py](tests/test_mcp_server_dotenv.py)).
- Lokasi `~` mengikuti `Path.home()` (`%USERPROFILE%` di Windows), bukan
  `VIBE_TRADING_HOME`.

Tes ini mengunci perilaku yang sudah ada, tanpa perubahan kode; ketujuh kasus
lulus pada run pertama.

**Bukti tes Linux yang ada.** Check wajib `test / Python 3.11`,
`test / Python 3.14` dan `frontend` berjalan di `ubuntu-latest` dan menjalankan
suite penuh (editable install `pip install -e ".[dev,...]"`) serta build/tes
frontend. `Hash lock / Linux x64` hanya me-resolve lock berhash secara dry-run.
Semua itu bukti tes di Linux, **bukan** alur bersih install non-editable → riset.

**Rencana smoke test Linux (belum dijalankan di Linux).** Tanpa WSL/Docker dan
tanpa mengubah workflow CI. Jaringan hanya dipakai di langkah persiapan;
instalasi dan riset berjalan di namespace tanpa jaringan (`unshare -rn`), dan
data pasar datang dari fixture sintetis lewat seam `fetch_market_data`.

1. Persiapan (online, sekali), dari checkout commit rilis:

   ```bash
   python3.12 -m venv /tmp/vt-smoke
   /tmp/vt-smoke/bin/pip download --require-hashes -r requirements-lock.txt -d /tmp/vt-wheelhouse
   (cd frontend && npm ci && npm run build)
   /tmp/vt-smoke/bin/pip wheel --no-deps -w /tmp/vt-dist .
   ```

   Hasil: wheelhouse berisi wheel Linux untuk seluruh lock, dan satu
   `vibe_trading_ai-0.1.19-*.whl` di `/tmp/vt-dist`.

2. Instalasi bersih tanpa jaringan:

   ```bash
   unshare -rn /tmp/vt-smoke/bin/pip install --no-index --find-links /tmp/vt-wheelhouse --require-hashes -r requirements-lock.txt
   unshare -rn /tmp/vt-smoke/bin/pip install --no-index --no-deps /tmp/vt-dist/vibe_trading_ai-*.whl
   unshare -rn /tmp/vt-smoke/bin/pip check
   unshare -rn /tmp/vt-smoke/bin/vibe-trading --version
   unshare -rn /tmp/vt-smoke/bin/python -I -m src.tools.idx_research_tool --help
   ```

   Hasil: kedua instalasi sukses, `pip check` melaporkan tidak ada konflik,
   `--version` mencetak `0.1.19`, `--help` keluar dengan kode 0.

3. Riset tanpa jaringan: simpan skrip di bawah sebagai `/tmp/idx_smoke.py`,
   lalu jalankan dari root checkout (fixture dibaca dari
   `agent/tests/fixtures/`, kode dari paket terpasang karena `-I`):

   ```bash
   unshare -rn /tmp/vt-smoke/bin/python -I /tmp/idx_smoke.py
   ```

   ```python
   import json, os, socket
   from pathlib import Path

   _connect = socket.socket.connect


   def _loopback_only(self, address):
       if isinstance(address, tuple) and address[0] not in ("127.0.0.1", "::1", "localhost"):
           raise OSError("network disabled for the IDX preview smoke test")
       return _connect(self, address)


   socket.socket.connect = _loopback_only

   import pandas as pd
   from fastapi import FastAPI
   from fastapi.testclient import TestClient

   from src.api.idx_research_routes import register_idx_research_routes
   from src.config.accessor import reset_env_config
   from src.tools import idx_research_tool
   import src

   print("0 package:", Path(src.__file__).parent)

   fixtures = Path("agent/tests/fixtures")
   frame = pd.read_csv(fixtures / "idx_data_quality" / "normal.csv", parse_dates=["date"], index_col="date")
   provenance = {"source": "fixture", "quote_currency": "IDR", "exchange_timezone": "Asia/Jakarta",
                 "interval": "1D", "volume_unit": "shares", "adjustment": "unknown", "freshness": "not_evaluated"}
   idx_research_tool.fetch_market_data = lambda **_k: {"SYNA.JK": frame, "_provenance": {"SYNA.JK": provenance}}
   request = {"codes": ["SYNA.JK"], "lookback": 20, "end_date": "2030-01-18"}

   for name in ("VIBE_TRADING_IDX_CALENDAR_PATH", "VIBE_TRADING_IDX_EVENT_RECORDS_PATH"):
       os.environ.pop(name, None)
   reset_env_config()
   result = json.loads(idx_research_tool.IDXResearchTool().execute(**request))
   item = result["items"][0]
   assert result["status"] == "ok" and item["status"] == "ok", result
   assert "sourced_reference" not in result
   print("1 tool ok:", item["symbol"], "bars", item["volume_coverage"]["bar_count"], "bar_audit", item["bar_audit"]["policy"])

   os.environ["VIBE_TRADING_IDX_CALENDAR_PATH"] = str(fixtures / "idx_calendar" / "bei_sessions_2026.json")
   os.environ["VIBE_TRADING_IDX_EVENT_RECORDS_PATH"] = str(fixtures / "idx_event_records" / "mlpt_2026-03_suspension.json")
   reset_env_config()
   app = FastAPI()
   register_idx_research_routes(app, lambda: None)
   with TestClient(app) as client:
       response = client.post("/api/research/idx", json=request)
   body = response.json()
   assert response.status_code == 200 and body["status"] == "ok", body
   reference = body["sourced_reference"]
   assert reference["calendar"]["status"] == "loaded" and reference["event_records"]["status"] == "loaded", reference
   print("2 api ok:", response.status_code, "calendar", reference["calendar"]["covered_from"], "..",
         reference["calendar"]["covered_until"], "records", reference["event_records"]["status"])
   print("IDX preview smoke passed")
   ```

   Hasil yang diharapkan: baris `0 package:` menunjuk
   `/tmp/vt-smoke/lib/python3.12/site-packages/src` (bukan `agent/src`), lalu
   `1 tool ok: SYNA.JK bars 9 bar_audit idx_daily_bar_audit_v1`,
   `2 api ok: 200 calendar 2026-01-01 .. 2026-12-31 records loaded` dan
   `IDX preview smoke passed`, exit 0. Guard socket menolak koneksi non-loopback
   sebagai lapis kedua selain `unshare`.

**Validasi skrip di Windows (2026-11-15).** Langkah 3 dijalankan di venv
proyek yang sudah ada (`.venv/idx312`, editable install; **bukan** instalasi
bersih): keluaran baris 1–2 dan `IDX preview smoke passed` sesuai harapan,
dengan `0 package:` menunjuk `agent/src` karena editable. Guard terbukti
menolak `socket.create_connection` ke alamat publik. Langkah 1–2 tidak
dijalankan karena mengunduh paket.

**Usulan (belum dijalankan, perlu izin pengguna).** Jalankan langkah 1–3 pada
host Linux milik operator, atau tambahkan job CI Linux yang menjalankan langkah
yang sama. Workflow CI tidak diubah di sesi ini.

**Tes/build pada HEAD PR ini (Windows, 2026-11-16).** Suite IDX
(`agent/tests/test_idx*.py` + `test_market_detection.py` + `test_registry.py` +
`test_mcp_server_dotenv.py`, `--allow-hosts=127.0.0.1,::1`) **1.252 passed**.
`npm run test:run` dengan timeout bawaan 5 detik **gagal 1–4 tes** per run
karena timeout (berganti-ganti: `IDXResearch.observations` 500 bar,
`AgentBackgroundStreamCompletion`, `VolatilitySurfaceGrid`; tes 500 bar juga
timeout saat dijalankan sendiri). Dengan `npx vitest run --testTimeout=30000`
ketiga file **28 passed** dan suite penuh **1.407 passed** (103 file), jadi
penyebabnya waktu di mesin ini, bukan assertion. Frontend tidak berubah di PR
ini. `npm run build` lulus. Hasil final dicatat ulang pada HEAD sesi terakhir.

**Akibat untuk RELEASE-01.** Alur bersih install → riset di Linux belum
benar-benar dijalankan, jadi RELEASE-01 **tidak dicentang**.

## Draf README (Bahasa Indonesia)

Draf pengganti bagian "🇮🇩 IDX Edition" di [README_id.md](../README_id.md). Isinya
hanya perilaku yang tersedia pada `feature/idx-edition` per 2026-11-15. Versi
yang diterapkan ke README_id.md (2026-11-15) menambah pernyataan hak data,
skill `idx-research` dan perilaku `.env` yang terbukti di bagian 5; README_id.md
adalah versi yang berlaku.

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
