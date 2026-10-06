import os
import subprocess

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    subprocess.run(
        ["python", "manage.py", "migrate", "--noinput"],
        check=True,
        timeout=120,
    )
except Exception as e:
    print(f"[WARNING] Migration gagal atau tidak dapat dijalankan: {e}")

# Buat akun admin otomatis jika belum ada
try:
    import django
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = "asisten_perencanaan_tambang"
    password = "mineplan2026"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            password=password,
            email="admin@praktikum.local",
        )
        print("[INFO] Superuser admin berhasil dibuat.")
    else:
        print("[INFO] User admin sudah ada.")

except Exception as e:
    print(f"[WARNING] Pembuatan admin gagal: {e}")

application = get_wsgi_application()
