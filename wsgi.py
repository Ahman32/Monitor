# wsgi.py — Entry point untuk hosting (Gunicorn / Railway / Render / dll)
# Mengimport app dari dashboard.py lalu menambahkan blueprint kamera.
# Tidak mengubah dashboard.py maupun main.py sama sekali.

from dashboard import app
from camera_web import camera_bp

# Daftarkan blueprint — tambahkan route /snap tanpa ubah dashboard.py
app.register_blueprint(camera_bp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
