from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("kelompok/", views.kelompok, name="kelompok"),
    path("personel/", views.personel, name="personel"),
    path("jadwal/", views.jadwal, name="jadwal"),
    path("materi/", views.materi, name="materi"),
    path("absensi/", views.absensi, name="absensi"),
    path("tata-tertib/", views.tata_tertib, name="tata_tertib"),
    path("pengumuman/", views.pengumuman, name="pengumuman"),

    # PESERTA
    path("login/", views.login_peserta, name="login_peserta"),
    path("logout/", views.logout_peserta, name="logout_peserta"),
    path("dashboard/", views.dashboard_peserta, name="dashboard_peserta"),
    path("laporan/upload/", views.upload_laporan, name="upload_laporan"),
]
