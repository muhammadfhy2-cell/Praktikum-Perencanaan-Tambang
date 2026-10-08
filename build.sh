#!/usr/bin/env bash

set -o errexit

echo "========================================"
echo "BUILD PRAKTIKUM PERENCANAAN TAMBANG"
echo "========================================"

echo "Mengumpulkan static files..."
python manage.py collectstatic --noinput

echo "Menjalankan database migration..."
python manage.py migrate --noinput

echo "========================================"
echo "BUILD SELESAI"
echo "========================================"
