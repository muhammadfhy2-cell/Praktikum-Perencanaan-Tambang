import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Jalankan migration database sebelum aplikasi dimulai.
try:
    call_command("migrate", interactive=False, verbosity=2)
    print("[INFO] Database migration berhasil dijalankan.")
except Exception as e:
    print("[ERROR] Database migration gagal:")
    print(repr(e))
    raise

application = get_wsgi_application()
