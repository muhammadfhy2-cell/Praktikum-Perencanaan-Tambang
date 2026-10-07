from django.urls import path

from . import views


app_name = "praktikum"


urlpatterns = [
    # ============================================================
    # PUBLIC
    # ============================================================

    path("", views.home, name="home"),
    path("kelompok/", views.kelompok, name="kelompok"),
    path("personel/", views.personel, name="personel"),
    path("jadwal/", views.jadwal, name="jadwal"),
    path("materi/", views.materi, name="materi"),
    path("absensi/", views.absensi, name="absensi"),
    path("tata-tertib/", views.tata_tertib, name="tata_tertib"),
    path("pengumuman/", views.pengumuman, name="pengumuman"),
    path(
        "tugas-pendahuluan/",
        views.tugas_pendahuluan,
        name="tugas_pendahuluan",
    ),

    # ============================================================
    # LOGIN KELOMPOK
    # ============================================================

    path(
        "login/",
        views.login_kelompok,
        name="login_kelompok",
    ),

    path(
        "logout/",
        views.logout_kelompok,
        name="logout_kelompok",
    ),

    # ============================================================
    # DASHBOARD
    # ============================================================

    path(
        "dashboard/",
        views.dashboard_kelompok,
        name="dashboard_kelompok",
    ),

    path(
        "dashboard-peserta/",
        views.dashboard_peserta,
        name="dashboard_peserta",
    ),

    # ============================================================
    # LAPORAN MINGGUAN
    # ============================================================

    path(
        "laporan/upload/",
        views.upload_laporan,
        name="upload_laporan",
    ),

    path(
        "laporan/revisi/<int:laporan_id>/",
        views.download_file_revisi,
        name="download_file_revisi",
    ),
]
