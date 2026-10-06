#!/bin/sh

echo "========================================"
echo "Menjalankan database migration..."
echo "========================================"

python manage.py migrate --noinput

echo "========================================"
echo "Migration selesai."
echo "Menjalankan aplikasi Django..."
echo "========================================"

exec gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8080}
