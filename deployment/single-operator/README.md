# Paket review deployment untuk satu operator

Paket ini menyiapkan Web UI/CLI riset untuk **satu operator tepercaya**.
Shared `API_AUTH_KEY` memberi akses operator ke aplikasi, termasuk Settings dan
state bersama; key tersebut bukan akun pengguna atau isolasi tenant. Jangan
membagikannya kepada pengguna publik. Template tidak menyediakan mode khusus
read-only untuk seluruh API. Broker/account tidak dikonfigurasi, shell tools,
advisory, scheduler dan channel auto-start tetap off.

Penggunaan Yahoo/yfinance yang diterima tetap riset pribadi lokal. Hak display,
redistribusi, pengiriman cloud dan penggunaan remote belum diterima. Template
teknis tidak memberi izin data. Backtest IDX tetap nonaktif; paper/live IDX dan
Local Data Bridge belum diterima. [Scope dan status](../../PROJECT_STATUS.md).

## Isi dan batas verifikasi

- [environment.example](environment.example): nama variabel, key kosong,
  hostname reserved dan feature opt-in off; tidak berisi secret.
- [vibe-trading.service](vibe-trading.service): backend pada **127.0.0.1:8899**,
  pre-start menolak key kosong, state di luar source, restart terbatas.
- [nginx.conf.example](nginx.conf.example): terminasi HTTPS, forwarding header
  ditimpa, SSE tidak dibuffer, tanpa retry upstream, log tanpa query ticket,
  shutdown HTTP ditolak di proxy. Tidak ada key ditanam di proxy.

Tidak ada paket OS/Python/npm baru dipasang oleh template. Nginx/systemd adalah
contoh untuk host Linux yang sudah dipersiapkan operator; keduanya tidak berjalan
di QA Windows ini. Sertifikat, domain, aturan jaringan, ownership filesystem,
`nginx -t`, `systemd-analyze verify`, TLS dan SSE melalui proxy nyata **belum
diverifikasi**. Docker tidak tersedia pada lingkungan QA ini, sehingga build
image Linux/Compose tidak diklaim lulus. Container existing adalah jalur terpisah.

QA Windows membangun wheel baru secara offline dengan backend existing,
menggunakan kembali 143 aset Vite yang sumber frontend-nya dicocokkan byte/hash
ke build terverifikasi sebelumnya. Tidak mengklaim build/test frontend baru.
Wheel dijalankan di luar checkout dengan home/runtime terisolasi dan key sintetis,
untuk memeriksa UI, auth, Origin, header, restart/persistensi serta shutdown.
Hasil aktual, perintah, hash dan batas ada di
[catatan QA](../../agent/IDX_PERSONAL_RESEARCH.md#deployment-local--2026-11-05).

## Persiapan host tujuan sebelum aktivasi

### Pemeriksaan lingkungan 2026-11-11

Discovery read-only terbaru: `wsl --list --verbose` exit **1** dan
`wsl --status` exit **50**, keduanya menyatakan WSL belum terpasang. Docker,
Podman, Nginx, `systemd-analyze`, Multipass dan Lima tidak ditemukan di PATH;
executable Docker/Podman juga tidak ada pada lokasi instalasi umum yang dicek.
Tidak ada guest/container yang diakses, service diaktifkan, paket diinstal atau
image ditarik. **Verifikasi deployment Linux masih terblokir**, bukan lulus dari
pemeriksaan teks atau QA Windows.

Prasyarat minimum untuk melanjutkan adalah lingkungan Linux disposable yang
sudah tersedia beserta runtime/dependency aplikasi, Nginx, `systemd-analyze`
dan alat sertifikat existing. Jangan memakai dependency/lock Windows sebagai
bukti Linux. Untuk QA, adaptasikan **salinan** konfigurasi ke listener
`127.0.0.1:<port-tinggi>`; contoh `listen 80/443` di atas bukan konfigurasi
listener lokal QA. Gunakan CA/sertifikat sintetis dengan SAN yang cocok dan
trust store khusus klien QA, tanpa melemahkan verifikasi TLS.

Gate native tetap: `systemd-analyze verify`, `nginx -t`, bind/key/startup,
UI/deep links, 401/403, forwarding, shutdown ditolak proxy, SSE deterministik
(streaming/buffering/cancel/timeout), tanpa replay write dan tanpa key/ticket
pada log. Host asing perlu diuji pada virtual host penolak di Nginx: template
menimpa Host upstream, sehingga guard Host backend tidak membuktikan penolakan
Host asli pada proxy. Bukti baru dan pemulihan sintetis dicatat di
[follow-up QA](../../agent/IDX_PERSONAL_RESEARCH.md#deployment-follow-up--2026-11-11).

1. Sediakan user sistem `vibe-trading` tanpa login interaktif, venv di
   `/opt/vibe-trading/venv`, direktori konfigurasi `/etc/vibe-trading`, TLS dan
   reverse proxy sesuai kebijakan host. Instalasi itu tidak dijalankan sesi ini.
2. Pasang dependency runtime dari lock yang cocok **untuk OS/Python tujuan**
   dengan hash verification; jangan gunakan lock Windows sebagai lock Linux.
   Pasang wheel dengan `python -m pip install --no-deps <wheel>` dan jalankan
   `python -m pip check`. [Distribusi existing](../../README.md#path-b-local-install).
3. Salin contoh environment ke `/etc/vibe-trading/server.env`, isi key kuat
   melalui pengelolaan secret milik operator, dan sesuaikan domain di environment
   serta proxy secara bersamaan. Simpan mode 0600; jangan commit atau menaruh key
   pada URL, argumen CLI, frontend bundle maupun access log. Jangan forward
   `X-Forwarded-For` dari klien apa adanya atau memakai trusted proxy `*`.
4. Backend berjalan satu proses pada loopback. `StateDirectory` menyimpan
   `/var/lib/vibe-trading`; `HOME` dan `VIBE_TRADING_HOME` berada di dalamnya.
   Settings memakai `HOME/.vibe-trading/.env`, sedangkan state terstruktur memakai
   `VIBE_TRADING_HOME`. Keduanya perlu dipertahankan. Environment service adalah
   konfigurasi deployment; jangan mengandalkan perubahan Settings untuk
   mengganti konfigurasi service yang diinject melalui environment.
5. Tinjau limit upload, durasi SSE, penyimpanan, retensi log dan kontrol akses
   host. Nginx harus hanya menerima virtual host/domain yang dimaksud; tambahkan
   default virtual host penolak sesuai host yang sudah ada. Tutup port backend
   dari jaringan. HSTS template hanya cocok untuk domain HTTPS yang siap.

Template unit/proxy tetap perlu validasi pada host tujuan. Jangan menjalankan
enable/start/reload sampai perubahan konkret, izin data dan aktivasi host
disetujui operator. User sesi ini hanya mengizinkan persiapan dan QA lokal.

## Pemeriksaan penerimaan di host tujuan

- `/live` dan `/health` membuktikan HTTP hidup, bukan provider berhasil.
  `/ready` mengukur konfigurasi LLM: **503 tanpa LLM** tidak berarti halaman
  riset IDX membutuhkan LLM. Jangan melemahkan probe agar terlihat hijau.
- Buka `/research/idx` melalui HTTPS. Tanpa key/salah key, API riset harus 401;
  key benar mencapai validasi request. Origin tak tepercaya dan Origin dengan
  port cacat harus 403. `/system/shutdown` melalui proxy harus 403.
- Periksa header CSP/nosniff/frame denial dan tidak adanya ticket/key pada log.
  Uji SSE panjang, pembatalan, dan respons parsial melalui proxy sebenarnya.
  Template menimpa header forwarding; QA aplikasi langsung tidak membuktikan
  perilaku Nginx/TLS.
- Untuk provider nyata, periksa izin dahulu, lalu gunakan watchlist kecil dan
  laporkan sumber/coverage/metadata aktual. Jangan gunakan order broker sebagai QA.
- Restart terkontrol harus mempertahankan state milik operator. Backup kedua
  direktori state/config dengan service berhenti atau snapshot konsisten;
  backup berisi secret/data privat dan disimpan terenkripsi di luar repo.
  Buktikan restore pada lokasi terisolasi sebelum mengklaim pemulihan siap.

## Rollback

Pertahankan wheel/config versi sebelumnya dan backup yang konsisten. Bila QA
host gagal, jangan membuka listener publik: kembalikan executable/konfigurasi
ke versi terverifikasi setelah persetujuan operator. Jangan menghapus state,
volume atau ledger. Tidak ada migrasi database atau perubahan pin dependency
dalam increment ini. Mengembalikan versi kode tidak berarti restore data sudah
diuji; kompatibilitas state harus diperiksa tersendiri.

Referensi teknis: [Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
dan [systemd service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html).
