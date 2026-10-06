#!/bin/sh
set -e

echo "========================================"
echo "PRAKTIKUM PERENCANAAN TAMBANG"
echo "Menjalankan database migration..."
echo "========================================"

python manage.py migrate --noinput

echo "========================================"
echo "Memeriksa akun Super Admin..."
echo "========================================"

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser '{username}' berhasil dibuat.")
    else:
        print(f"Superuser '{username}' sudah ada.")
else:
    print("Variabel superuser belum lengkap.")
PY

echo "========================================"
echo "Migration dan pemeriksaan admin selesai."
echo "Menjalankan Gunicorn..."
echo "========================================"

exec gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8080}
