
from django.urls import path

from . import views
from .daily_mom_views import (
    tambah_daily_mom,
    edit_daily_mom,
    hapus_daily_mom,
)

app_name = "praktikum"

urlpatterns = [
    # =====================================================
    # HALAMAN PUBLIK
    # =====================================================
    path("", views.home, name="home"),
    path("personel/", views.personel, name="personel"),
    path("kelompok/", views.kelompok, name="kelompok"),
    path("jadwal/", views.jadwal, name="jadwal"),
    path("materi/", views.materi, name="materi"),
    path("absensi/", views.absensi, name="absensi"),
    path("pengumuman/", views.pengumuman, name="pengumuman"),
    path("tata-tertib/", views.tata_tertib, name="tata_tertib"),

    path(
        "tugas-pendahuluan/",
        views.tugas_pendahuluan,
        name="tugas_pendahuluan",
    ),
    path(
        "tugas-pendahuluan/<int:tugas_id>/download/",
        views.download_tugas_pendahuluan,
        name="download_tugas_pendahuluan",
    ),

    path(
        "informasi-peserta/",
        views.informasi_peserta,
        name="informasi_peserta",
    ),
    path(
        "format-dokumen/",
        views.format_dokumen,
        name="format_dokumen",
    ),

    # =====================================================
    # DOWNLOAD MATERI DAN FORMAT DOKUMEN
    # =====================================================
    path(
        "materi/<int:materi_id>/download/",
        views.download_materi,
        name="download_materi",
    ),
    path(
        "format-dokumen/<int:dokumen_id>/download/",
        views.download_format_dokumen,
        name="download_format_dokumen",
    ),

    # =====================================================
    # LOGIN, LOGOUT, DAN DASHBOARD
    # =====================================================
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
    path(
        "dashboard/kelompok/",
        views.dashboard_kelompok,
        name="dashboard_kelompok",
    ),
    path(
        "dashboard/peserta/",
        views.dashboard_peserta,
        name="dashboard_peserta",
    ),

    # =====================================================
    # DAILY MOM
    # =====================================================
    path(
        "dashboard/kelompok/daily-mom/tambah/",
        tambah_daily_mom,
        name="tambah_daily_mom",
    ),
    path(
        "dashboard/kelompok/daily-mom/<int:daily_mom_id>/edit/",
        edit_daily_mom,
        name="edit_daily_mom",
    ),
    path(
        "dashboard/kelompok/daily-mom/<int:daily_mom_id>/hapus/",
        hapus_daily_mom,
        name="hapus_daily_mom",
    ),

    # =====================================================
    # LAPORAN MINGGUAN
    # =====================================================
    path(
        "laporan/upload/",
        views.upload_laporan,
        name="upload_laporan",
    ),
    path(
        "laporan/<int:laporan_id>/download/",
        views.download_laporan_mingguan,
        name="download_laporan_mingguan",
    ),
    path(
        "laporan/revisi/<int:laporan_id>/download/",
        views.download_file_revisi,
        name="download_file_revisi",
    ),
    path(
        "admin-file/laporan-mingguan/<int:laporan_id>/<str:jenis>/",
        views.download_laporan_mingguan_admin,
        name="download_laporan_mingguan_admin",
    ),

    # =====================================================
    # LAPORAN LENGKAP
    # =====================================================
    path(
        "laporan-lengkap/upload/",
        views.upload_laporan_lengkap,
        name="upload_laporan_lengkap",
    ),
    path(
        "laporan-lengkap/<int:laporan_id>/download/",
        views.download_laporan_lengkap,
        name="download_laporan_lengkap",
    ),
    path(
        "laporan-lengkap/<int:laporan_id>/revisi/download/",
        views.download_laporan_lengkap_revisi,
        name="download_laporan_lengkap_revisi",
    ),
    path(
        "admin-file/laporan-lengkap/<int:laporan_id>/<str:jenis>/",
        views.download_laporan_lengkap_admin,
        name="download_laporan_lengkap_admin",
    ),

    # =====================================================
    # FILE KELOMPOK
    # =====================================================
    path(
        "file-kelompok/<int:file_id>/download/",
        views.download_file_kelompok,
        name="download_file_kelompok",
    ),
]
