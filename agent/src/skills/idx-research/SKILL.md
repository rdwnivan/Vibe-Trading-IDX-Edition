---
name: idx-research
description: Riset pribadi saham IDX/BEI .JK dalam Bahasa Indonesia menggunakan observasi harian IDR, indikator, provenance dan profil Yahoo snapshot opsional; untuk analisis watchlist lokal, bukan simulasi eksekusi.
category: analysis
---

# Riset pribadi IDX

Gunakan untuk analisis saham Indonesia dengan tool aplikasi. Kemampuan harga
yang diterima terbatas pada maksimum delapan saham reguler `.JK`, harian IDR,
untuk riset pribadi lokal. Nama perusahaan belum membuktikan identitas instrumen;
`BBCA` tanpa venue tetap memiliki arti pasar lain dalam aplikasi.

## Identitas dan satu observasi

1. Terima ticker `.JK` eksplisit. Jika pengguna memberi nama/ticker ambigu,
   gunakan `search_symbol(query=..., market="idx")`, tampilkan kandidat, lalu
   minta pilihan bila lebih dari satu. Hasil pencarian bukan master resmi atau
   bukti saham masih dapat diperdagangkan. Hasil kosong tidak membatalkan ticker
   `.JK` eksplisit yang dimasukkan pengguna.
2. Panggil `idx_research(codes=["BBCA.JK"], lookback=200)` sekali untuk satu
   observasi watchlist. Gunakan `end_date="YYYY-MM-DD"` bila pengguna menetapkan
   batas tanggal; parameter itu membatasi harga, bukan tanggal fundamental.
3. Untuk tiap item sehat, baca `analysis.latest_close`, `latest_date`,
   `indicators`, `read_identity`, `provenance`, `recency` dan `volume_coverage`.
   Gunakan SMA/RSI/MACD/Bollinger/volume yang sudah dihitung tool; pertahankan
   null sebagai belum tersedia. Analisis pendek boleh memiliki indikator yang
   belum cukup warmup. Hindari akuisisi kedua hanya untuk menghitung ulang
   indikator dari observasi berbeda.
4. Pisahkan item `unavailable` dari item sehat. Laporkan `quality_issue.code`
   atau diagnostik sumber bila ada. `recency` adalah usia kalender terhadap
   tanggal permintaan, bukan kalender sesi, suspensi atau status real-time.
   Volume nol adalah observasi; volume null adalah belum tersedia. Volume
   saham bukan lot, turnover transaksi, free float atau bukti smart money.

## Profil snapshot opsional

Jika pengguna meminta konteks fundamental/valuasi, gunakan tool existing
`get_stock_profile(ticker="BBCA.JK", sections=["key_stats", "financials"])`.
Jalur IDX menolak respons dengan identitas listing/venue/currency yang tidak
cocok. Laporkan kegagalan profil secara terpisah agar hasil harga sehat tetap
berguna. Coverage provider nyata untuk profil IDX belum diterima hanya karena
kontrak tool dan fixture lulus.

`listing.currency` adalah mata uang kuotasi; `financial_currency` adalah
deklarasi pelaporan terpisah dan boleh berbeda atau belum tersedia. Sajikan
nilai persis dengan unit yang terbukti; jangan mengonversi/menjumlahkan currency
atau membentuk multiple dari EPS, revenue dan harga yang basisnya belum jelas.
`provenance.retrieved_at` adalah waktu retrieval, bukan publikasi.
`financial_period` dan `publication_time` yang null berarti belum terverifikasi;
`historical_use="not_supported"` melarang penggunaan snapshot ini sebagai
fundamental point-in-time untuk analisis historis/backtest. Estimasi analis
adalah estimasi, bukan hasil laporan atau target hasil strategi.

Dividen, corporate actions, laporan historis, broker summary, foreign flow dan
fundamental yang tidak dikembalikan tetap `unavailable`. Jelaskan input berizin
yang dibutuhkan untuk menjawabnya. Jangan meminjam angka saham asing atau
memperlakukan adjustment harga sebagai riwayat aksi korporasi lengkap.

## Jawaban berbukti

Jawab dalam Bahasa Indonesia dengan urutan yang sesuai permintaan:

- **Cakupan:** ticker/IDX, IDR, harian, jumlah bar aktual, tanggal harga terakhir,
  sumber aktual dan adjustment. Yahoo/yfinance adalah dua transport satu vendor.
- **Temuan:** pisahkan observasi numerik tool dari interpretasi bersyarat.
  Kaitkan setiap angka dengan simbol, field respons dan tanggal/periode yang
  tersedia. Simpan `analysis.read_identity.dataset_fingerprint` sebagai identitas
  observasi bila artefak/catatan riset dibuat, bukan sebagai bukti kebenaran data.
- **Risiko dan kekurangan:** uraikan indikator belum warmup, hasil parsial,
  `unavailable`, volume hilang, usia data, serta histori/izin yang belum terbukti.
  Tidak ada universe historis, benchmark IHSG atau kinerja strategi terverifikasi
  yang bisa disimpulkan dari watchlist ini.
- **Langkah lanjut:** skenario harga yang ditopang indikator boleh dinyatakan
  sebagai hipotesis; pisahkan dari instruksi order/sizing dan klaim profit.

Backtest IDX tetap nonaktif. Paper/live, mandate, akun dan izin data remote/publik
adalah jalur terpisah; panduan ini hanya memuat alur riset lokal read-only.
