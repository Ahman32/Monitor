from flask import Flask, render_template_string, send_from_directory
import os
import csv

FOLDER_FOTO = "foto_otomatis"
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Foto Pribadi</title>
<meta http-equiv="refresh" content="15">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0b0d12;
    --bg-soft:#11141b;
    --card:#171b24;
    --card-hover:#1d2230;
    --border:#242a38;
    --teks:#e8ebf2;
    --teks-redup:#8b92a5;
    --aksen:#5b8cff;
    --aksen2:#7f5bff;
    --hijau:#38d39f;
    --kuning:#f0b84b;
  }
  *{ box-sizing:border-box; }
  body{
    margin:0; padding:0;
    font-family:'Inter', sans-serif;
    background:
      radial-gradient(900px 500px at 10% -10%, rgba(91,140,255,.12), transparent 60%),
      radial-gradient(900px 500px at 100% 0%, rgba(127,91,255,.10), transparent 55%),
      var(--bg);
    color:var(--teks);
    min-height:100vh;
  }

  header{
    padding:36px 24px 20px;
    text-align:center;
  }
  header h1{
    font-family:'Poppins', sans-serif;
    font-weight:700;
    font-size:28px;
    margin:0 0 6px;
    display:flex; align-items:center; justify-content:center; gap:10px;
  }
  header p{
    color:var(--teks-redup);
    font-size:14px;
    margin:0;
  }

  .stats{
    display:flex; justify-content:center; flex-wrap:wrap;
    gap:14px; margin:22px auto 4px; max-width:900px; padding:0 20px;
  }
  .stat{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:14px;
    padding:14px 22px;
    min-width:130px;
    text-align:center;
  }
  .stat .angka{
    font-family:'Poppins', sans-serif;
    font-size:22px; font-weight:600;
  }
  .stat .label{
    font-size:11px; color:var(--teks-redup);
    text-transform:uppercase; letter-spacing:.06em; margin-top:2px;
  }
  .stat.gps .angka{ color:var(--hijau); }
  .stat.ip .angka{ color:var(--kuning); }

  main{ max-width:1200px; margin:0 auto; padding:24px; }

  .grid{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap:18px;
  }

  .card{
    position:relative;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:16px;
    overflow:hidden;
    cursor:pointer;
    transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  }
  .card:hover{
    transform:translateY(-4px);
    border-color:rgba(91,140,255,.45);
    box-shadow:0 14px 30px rgba(0,0,0,.45);
    background:var(--card-hover);
  }
  .thumb{ position:relative; overflow:hidden; aspect-ratio:4/3; background:#000; }
  .thumb img{
    width:100%; height:100%; object-fit:cover; display:block;
    transition:transform .35s ease;
  }
  .card:hover .thumb img{ transform:scale(1.06); }

  .badge{
    position:absolute; top:10px; right:10px;
    font-size:11px; font-weight:600; letter-spacing:.03em;
    padding:4px 9px; border-radius:999px;
    backdrop-filter:blur(6px);
    background:rgba(0,0,0,.45);
    border:1px solid rgba(255,255,255,.15);
  }
  .badge.gps{ color:var(--hijau); }
  .badge.ip{ color:var(--kuning); }
  .badge.none{ color:var(--teks-redup); }

  .info{ padding:12px 14px 14px; }
  .info .waktu{ font-size:13px; font-weight:500; }
  .info .sub{ font-size:12px; color:var(--teks-redup); margin-top:2px; }
  .info a{ color:var(--aksen); font-size:12px; text-decoration:none; }
  .info a:hover{ text-decoration:underline; }

  .kosong{
    text-align:center; margin-top:60px; color:var(--teks-redup);
    display:flex; flex-direction:column; align-items:center; gap:10px;
  }
  .kosong .ikon{ font-size:44px; opacity:.5; }

  /* ===== Modal detail foto ===== */
  .overlay{
    display:none; position:fixed; inset:0;
    background:rgba(5,6,10,.85);
    backdrop-filter:blur(4px);
    align-items:center; justify-content:center;
    padding:20px; z-index:100;
  }
  .overlay.aktif{ display:flex; }
  .modal{
    background:var(--bg-soft);
    border:1px solid var(--border);
    border-radius:18px;
    max-width:920px; width:100%;
    max-height:90vh; overflow-y:auto;
    display:grid; grid-template-columns:1fr;
    position:relative;
    box-shadow:0 30px 70px rgba(0,0,0,.6);
  }
  @media (min-width:700px){ .modal{ grid-template-columns:1.1fr 1fr; } }
  .modal img{ width:100%; height:100%; object-fit:cover; display:block; }
  .modal-info{ padding:26px; }
  .modal-info h2{
    margin:0 0 16px; font-size:14px; font-weight:500;
    color:var(--teks-redup); word-break:break-all;
  }
  .modal-info table{ width:100%; border-collapse:collapse; font-size:14px; margin-bottom:18px; }
  .modal-info td{ padding:7px 0; vertical-align:top; border-bottom:1px solid var(--border); }
  .modal-info td:first-child{ color:var(--teks-redup); width:100px; }
  .modal-info iframe{ width:100%; height:220px; border:0; border-radius:12px; }
  .modal-info a.tombol{
    display:inline-block; margin-top:12px; padding:10px 16px;
    background:linear-gradient(135deg, var(--aksen), var(--aksen2));
    color:#fff; border-radius:10px; text-decoration:none; font-size:13px; font-weight:600;
  }
  .tutup{
    position:absolute; top:12px; right:16px;
    font-size:26px; color:var(--teks); cursor:pointer; user-select:none;
    width:34px; height:34px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    background:rgba(255,255,255,.06);
    z-index:2;
  }
  .tutup:hover{ background:rgba(255,255,255,.15); }

  ::-webkit-scrollbar{ width:10px; }
  ::-webkit-scrollbar-track{ background:transparent; }
  ::-webkit-scrollbar-thumb{ background:var(--border); border-radius:10px; }
</style>
</head>
<body>

<header>
  <h1>📷 Dashboard Foto Pribadi</h1>
  <p>Galeri otomatis dari capture_gps.py · hanya kamu yang bisa melihat ini</p>
</header>

<div class="stats">
  <div class="stat">
    <div class="angka">{{ foto_list|length }}</div>
    <div class="label">Total Foto</div>
  </div>
  <div class="stat gps">
    <div class="angka">{{ foto_list|selectattr('sumber','equalto','GPS')|list|length }}</div>
    <div class="label">Dari GPS</div>
  </div>
  <div class="stat ip">
    <div class="angka">{{ foto_list|selectattr('sumber','equalto','IP')|list|length }}</div>
    <div class="label">Dari IP</div>
  </div>
</div>

<main>
{% if foto_list %}
<div class="grid">
  {% for f in foto_list %}
  <div class="card"
       onclick="bukaDetail('{{ f.file }}','{{ f.waktu }}','{{ f.lat }}','{{ f.lon }}','{{ f.sumber }}')">
    <div class="thumb">
      <img src="/foto/{{ f.file }}" alt="{{ f.file }}" loading="lazy">
      {% if f.sumber == 'GPS' %}
        <span class="badge gps">● GPS</span>
      {% elif f.sumber == 'IP' %}
        <span class="badge ip">● IP</span>
      {% else %}
        <span class="badge none">Tanpa lokasi</span>
      {% endif %}
    </div>
    <div class="info">
      <div class="waktu">{{ f.waktu }}</div>
      {% if f.maps %}
        <div class="sub"><a href="{{ f.maps }}" target="_blank" onclick="event.stopPropagation()">Lihat di Peta ↗</a></div>
      {% else %}
        <div class="sub">Lokasi tidak tercatat</div>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</div>
{% else %}
<div class="kosong">
  <div class="ikon">🖼️</div>
  <p>Belum ada foto.<br>Jalankan <code>capture_gps.py</code> dulu untuk mulai mengambil foto.</p>
</div>
{% endif %}
</main>

<!-- Modal detail foto + lokasi -->
<div class="overlay" id="overlay" onclick="tutupDetail(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <span class="tutup" onclick="tutupDetail()">&times;</span>
    <img id="modalFoto" src="" alt="">
    <div class="modal-info">
      <h2 id="modalNama"></h2>
      <table>
        <tr><td>Waktu</td><td id="modalWaktu"></td></tr>
        <tr><td>Latitude</td><td id="modalLat"></td></tr>
        <tr><td>Longitude</td><td id="modalLon"></td></tr>
        <tr><td>Sumber</td><td id="modalSumber"></td></tr>
      </table>
      <div id="modalPeta"></div>
    </div>
  </div>
</div>

<script>
function bukaDetail(file, waktu, lat, lon, sumber) {
  document.getElementById("modalFoto").src = "/foto/" + file;
  document.getElementById("modalNama").textContent = file;
  document.getElementById("modalWaktu").textContent = waktu;
  document.getElementById("modalSumber").textContent = sumber && sumber !== "None" ? sumber : "-";

  var petaDiv = document.getElementById("modalPeta");
  if (lat && lon && lat !== "None" && lon !== "None") {
    document.getElementById("modalLat").textContent = lat;
    document.getElementById("modalLon").textContent = lon;
    petaDiv.innerHTML =
      '<iframe loading="lazy" ' +
      'src="https://maps.google.com/maps?q=' + lat + ',' + lon + '&z=16&output=embed"></iframe>' +
      '<br><a class="tombol" target="_blank" ' +
      'href="https://www.google.com/maps?q=' + lat + ',' + lon + '">Buka di Google Maps ↗</a>';
  } else {
    document.getElementById("modalLat").textContent = "-";
    document.getElementById("modalLon").textContent = "-";
    petaDiv.innerHTML = "<p style='color:var(--teks-redup)'>Lokasi tidak tersedia untuk foto ini.</p>";
  }

  document.getElementById("overlay").classList.add("aktif");
}

function tutupDetail(e) {
  document.getElementById("overlay").classList.remove("aktif");
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") tutupDetail();
});
</script>
</body>
</html>
"""


def baca_log():
    path_log = os.path.join(FOLDER_FOTO, "log_foto.csv")
    data = []
    if os.path.exists(path_log):
        with open(path_log, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for baris in reader:
                data.append(baris)
    data.reverse()  # foto terbaru ditampilkan paling atas
    return data


@app.route("/")
def index():
    return render_template_string(TEMPLATE, foto_list=baca_log())


@app.route("/foto/<path:nama_file>")
def foto(nama_file):
    return send_from_directory(FOLDER_FOTO, nama_file)


if __name__ == "__main__":
    # host="127.0.0.1" artinya dashboard HANYA bisa diakses dari komputer ini sendiri,
    # tidak bisa diakses orang lain lewat jaringan/internet.
    print("Dashboard berjalan di: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)