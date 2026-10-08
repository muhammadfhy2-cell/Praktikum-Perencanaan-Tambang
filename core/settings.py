# ============================================================
# HOST / DOMAIN
# ============================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost,praktikumperencanaantambang.velixir.run"
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://praktikumperencanaantambang.velixir.run"
    ).split(",")
    if origin.strip()
]


# ============================================================
# LOGIN / LOGOUT
# ============================================================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/kelompok/"
LOGOUT_REDIRECT_URL = "/login/"


# ============================================================
# SESSION
# ============================================================

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
