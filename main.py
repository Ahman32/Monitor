import cv2
import time
import csv
import os
import threading
import requests
from datetime import datetime

try:
    from plyer import gps
    GPS_TERSEDIA = True
except Exception:
    GPS_TERSEDIA = False

# ======== PENGATURAN ========
INTERVAL_FOTO = 10          # ambil foto otomatis setiap 10 detik (ubah sesuai kebutuhan)
INTERVAL_LOKASI_IP = 60     # refresh lokasi dari IP setiap 60 detik (dipakai saat GPS asli tidak ada)
FOLDER_FOTO = "foto_otomatis"
# =============================

lokasi = {"lat": None, "lon": None, "sumber": None}
gps_aktif = False

os.makedirs(FOLDER_FOTO, exist_ok=True)


def on_location(**kwargs):
    """Dipanggil otomatis setiap ada update lokasi dari GPS asli (HP/perangkat dengan GPS)."""
    lokasi["lat"] = kwargs.get("lat")
    lokasi["lon"] = kwargs.get("lon")
    lokasi["sumber"] = "GPS"


def mulai_gps():
    """Coba aktifkan GPS asli. Kalau perangkat tidak punya GPS (misal laptop/PC), ini akan gagal
    dengan wajar dan program otomatis memakai lokasi dari IP sebagai gantinya."""
    global gps_aktif
    if not GPS_TERSEDIA:
        print("Modul plyer.gps tidak tersedia di environment ini.")
        return
    try:
        gps.configure(on_location=on_location)
        gps.start(minTime=1000, minDistance=1)
        gps_aktif = True
        print("GPS asli aktif, mencari sinyal...")
    except NotImplementedError:
        print("Perangkat ini tidak punya modul GPS bawaan (umum terjadi di laptop/PC).")
        print("Akan memakai lokasi perkiraan dari alamat IP sebagai gantinya.")
        gps_aktif = False


def ambil_lokasi_ip():
    """Ambil perkiraan lokasi dari alamat IP publik.
    Akurasinya hanya level kota (bukan presisi GPS), tapi cukup untuk tahu area lokasi."""
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            lokasi["lat"] = data.get("lat")
            lokasi["lon"] = data.get("lon")
            lokasi["sumber"] = "IP"
            print(f"Lokasi (perkiraan dari IP): {data.get('city')}, {data.get('regionName')} "
                  f"-> {lokasi['lat']}, {lokasi['lon']}")
        else:
            print("Gagal mendapatkan lokasi dari IP (respons tidak sukses).")
    except Exception as e:
        print(f"Tidak bisa mengambil lokasi dari IP: {e}")


def loop_lokasi_ip():
    """Jalan di background: refresh lokasi dari IP secara berkala,
    hanya dipakai kalau GPS asli tidak aktif."""
    while True:
        if not gps_aktif:
            ambil_lokasi_ip()
        time.sleep(INTERVAL_LOKASI_IP)


def simpan_log(nama_file, lat, lon, sumber):
    """Catat setiap foto beserta waktu, koordinat, dan sumber lokasinya (GPS atau IP)."""
    file_log = os.path.join(FOLDER_FOTO, "log_foto.csv")
    baru = not os.path.exists(file_log)
    with open(file_log, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if baru:
            writer.writerow(["file", "waktu", "lat", "lon", "sumber", "maps"])
        writer.writerow([
            nama_file,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lat,
            lon,
            sumber or "",
            f"https://www.google.com/maps?q={lat},{lon}" if lat else "",
        ])


def ambil_foto(kamera):
    """Ambil satu frame dari kamera dan simpan sebagai foto, tanpa menampilkan jendela apa pun."""
    berhasil, frame = kamera.read()
    if not berhasil:
        print("Gagal membaca frame dari kamera.")
        return

    waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    lat, lon, sumber = lokasi["lat"], lokasi["lon"], lokasi["sumber"]

    if lat is not None:
        nama_file = f"foto_{waktu}_{lat:.5f}_{lon:.5f}.jpg"
    else:
        nama_file = f"foto_{waktu}.jpg"

    path_lengkap = os.path.join(FOLDER_FOTO, nama_file)
    cv2.imwrite(path_lengkap, frame)
    simpan_log(nama_file, lat, lon, sumber)

    print(f"[OTOMATIS] Foto disimpan: {nama_file}")
    if lat is not None:
        print(f"Lokasi ({sumber}): https://www.google.com/maps?q={lat},{lon}")
    else:
        print("Lokasi belum tersedia untuk foto ini.")


def main():
    mulai_gps()

    # ambil lokasi IP sekali di awal supaya foto pertama langsung punya koordinat
    if not gps_aktif:
        ambil_lokasi_ip()

    # refresh lokasi IP secara berkala di background (dipakai hanya kalau GPS asli tidak aktif)
    thread_lokasi = threading.Thread(target=loop_lokasi_ip, daemon=True)
    thread_lokasi.start()

    kamera = cv2.VideoCapture(0)
    if not kamera.isOpened():
        print("Kamera tidak bisa dibuka!")
        if gps_aktif:
            gps.stop()
        return

    print(f"Berjalan di latar belakang. Foto diambil otomatis tiap {INTERVAL_FOTO} detik.")
    print("Tidak ada jendela yang ditampilkan. Tekan Ctrl+C di terminal untuk berhenti.")

    try:
        while True:
            ambil_foto(kamera)
            time.sleep(INTERVAL_FOTO)
    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna (Ctrl+C).")
    finally:
        kamera.release()
        if gps_aktif:
            gps.stop()


if __name__ == "__main__":
    main()