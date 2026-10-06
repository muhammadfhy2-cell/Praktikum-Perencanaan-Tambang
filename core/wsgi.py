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

application = get_wsgi_application()
