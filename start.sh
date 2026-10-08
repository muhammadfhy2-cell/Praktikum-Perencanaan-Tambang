#!/bin/sh

set -e

echo "========================================"
echo "PRAKTIKUM PERENCANAAN TAMBANG"
echo "========================================"

echo "Menjalankan system check..."
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
    "asdos_perencanaan_tambang"
)

email = os.getenv(
    "DJANGO_SUPERUSER_EMAIL",
    "admin@praktikumperencanaantambang.local"
)

password = os.getenv(
    "DJANGO_SUPERUSER_PASSWORD",
    "AdminPraktikum2026!"
)

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
    },
)

if created:
    user.set_password(password)
    user.save()

    print(
        f"Superuser '{username}' berhasil dibuat."
    )

else:
    changed = False

    if not user.is_staff:
        user.is_staff = True
        changed = True

    if not user.is_superuser:
        user.is_superuser = True
        changed = True

    if not user.is_active:
        user.is_active = True
        changed = True

    if changed:
        user.save()

    print(
        f"Superuser '{username}' sudah tersedia."
    )

PY

echo "========================================"
echo "Migration, static files, dan admin selesai."
echo "========================================"

echo "Menjalankan Gunicorn..."
echo "========================================"

exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120}
