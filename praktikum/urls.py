from django.urls import path

from . import views


app_name = "praktikum"


urlpatterns = [

    # ========================================================
    # PUBLIC
    # ========================================================

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "personel/",
        views.personel,
        name="personel",
    ),

    path(
        "kelompok/",
        views.kelompok,
        name="kelompok",
    ),

    path(
        "jadwal/",
        views.jadwal,
        name="jadwal",
    ),

    path(
        "materi/",
        views.materi,
        name="materi",
    ),

    path(
        "absensi/",
        views.absensi,
        name="absensi",
    ),

    path(
        "pengumuman/",
        views.pengumuman,
        name="pengumuman",
    ),

    path(
        "tata-tertib/",
        views.tata_tertib,
        name="tata_tertib",
    ),

    path(
        "tugas-pendahuluan/",
        views.tugas_pendahuluan,
        name="tugas_pendahuluan",
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


    # ========================================================
    # LOGIN KELOMPOK
    # ========================================================

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


    # ========================================================
    # DASHBOARD
    # ========================================================

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


    # ========================================================
    # LAPORAN
    # ========================================================

    path(
        "laporan/upload/",
        views.upload_laporan,
        name="upload_laporan",
    ),

    path(
        "laporan/revisi/<int:laporan_id>/download/",
        views.download_file_revisi,
        name="download_file_revisi",
    ),

]
