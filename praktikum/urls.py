from django.urls import path
from . import views


app_name = "praktikum"


urlpatterns = [
    # =========================
    # HALAMAN UTAMA
    # =========================
    path("", views.home, name="home"),

    # =========================
    # INFORMASI PRAKTIKUM
    # =========================
    path("personel/", views.personel, name="personel"),
    path("kelompok/", views.kelompok, name="kelompok"),
    path("jadwal/", views.jadwal, name="jadwal"),
    path("materi/", views.materi, name="materi"),
    path("pengumuman/", views.pengumuman, name="pengumuman"),
    path("tata-tertib/", views.tata_tertib, name="tata_tertib"),

    # =========================
    # ABSENSI
    # =========================
    path("absensi/", views.absensi, name="absensi"),
]
