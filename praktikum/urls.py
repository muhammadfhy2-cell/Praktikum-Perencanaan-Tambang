from django.urls import path

from . import views


app_name = "absensi"


urlpatterns = [
    # ========================================================
    # LOGIN
    # ========================================================

    path(
        "",
        views.login_kelompok,
        name="login_kelompok",
    ),

    path(
        "login/",
        views.login_kelompok,
        name="login_kelompok",
    ),

    # ========================================================
    # LOGOUT
    # ========================================================

    path(
        "logout/",
        views.logout_kelompok,
        name="logout_kelompok",
    ),

    # ========================================================
    # DASHBOARD
    # ========================================================

    path(
        "dashboard/",
        views.dashboard_kelompok,
        name="dashboard_kelompok",
    ),
]
