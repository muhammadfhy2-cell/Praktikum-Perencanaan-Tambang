
#!/bin/sh

set -eu

echo "========================================"
echo "PRAKTIKUM PERENCANAAN TAMBANG"
echo "========================================"

# ============================================================
# PEMERIKSAAN ENVIRONMENT DAN DATABASE
# ============================================================

echo "Memeriksa konfigurasi penyimpanan..."

python manage.py shell <<'PY'
import os
from pathlib import Path
from django.conf import settings

print("Persistent data directory:", settings.PERSISTENT_DATA_DIR)
print("Database engine:", settings.DATABASES["default"]["ENGINE"])

db = settings.DATABASES["default"]

if db["ENGINE"] == "django.db.backends.sqlite3":
    path = Path(db["NAME"])
    parent = path.parent

    print("Database path:", path)
    print("Database exists before migration:", path.is_file())
    print("Database directory exists:", parent.is_dir())
    print(
        "Database directory writable:",
        os.access(parent, os.W_OK),
    )

    if str(settings.PERSISTENT_DATA_DIR) == "/data":
        if not str(path).startswith("/data/"):
            raise SystemExit(
                "ERROR: SQLite tidak menggunakan persistent volume /data."
            )

        if not parent.is_dir():
            raise SystemExit(
                "ERROR: Direktori /data tidak tersedia."
            )

        if not os.access(parent, os.W_OK):
            raise SystemExit(
                "ERROR: Direktori /data tidak dapat ditulis."
            )
else:
    print("Database menggunakan koneksi eksternal.")
PY

echo "========================================"
echo "Menjalankan system check..."
echo "========================================"

python manage.py check

echo "========================================"
echo "Menjalankan database migration..."
echo "========================================"

python manage.py migrate --noinput

echo "========================================"
echo "Mengumpulkan static files..."
echo "========================================"

python manage.py collectstatic --noinput

echo "========================================"
echo "Memeriksa akun Super Admin..."
echo "========================================"

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv(
    "DJANGO_SUPERUSER_USERNAME",
    "asdos_perencanaan_tambang",
).strip()

email = os.getenv(
    "DJANGO_SUPERUSER_EMAIL",
    "",
).strip()

password = os.getenv(
    "DJANGO_SUPERUSER_PASSWORD",
    "",
)

if not username:
    raise SystemExit(
        "ERROR: DJANGO_SUPERUSER_USERNAME tidak boleh kosong."
    )

user = User.objects.filter(username=username).first()

if user is None:
    if not password:
        raise SystemExit(
            "ERROR: DJANGO_SUPERUSER_PASSWORD wajib diatur "
            "untuk membuat superuser baru."
        )

    user = User.objects.create_superuser(
        username=username,
        email=email or "",
        password=password,
    )

    print(f"Superuser '{username}' berhasil dibuat.")

else:
    print(f"Superuser '{username}' sudah tersedia.")

    # Jangan mereset password atau mengubah hak akses
    # akun yang sudah ada secara otomatis.
PY

echo "========================================"
echo "Pemeriksaan akhir database..."
echo "========================================"

python manage.py shell <<'PY'
from pathlib import Path
from django.conf import settings
from django.db import connection

db = settings.DATABASES["default"]

with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    cursor.fetchone()

print("Database connection: OK")
print("Database engine:", db["ENGINE"])

if db["ENGINE"] == "django.db.backends.sqlite3":
    path = Path(db["NAME"])
    print("Database path:", path)
    print("Database file exists:", path.is_file())
    print("Database file size:", path.stat().st_size if path.is_file() else 0)
PY

echo "========================================"
echo "Migration, static files, dan admin selesai."
echo "========================================"

echo "Menjalankan Gunicorn..."
echo "========================================"

exec gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}"
