from django.contrib import admin
from .models import Setting, Staff, Kelompok, Peserta, Acara, Materi, Absensi, Pengumuman, TataTertib

admin.site.site_header = "Praktikum Perencanaan Tambang — Admin"
admin.site.site_title = "Admin Praktikum Perencanaan Tambang"
admin.site.index_title = "Pengelolaan Portal Praktikum"


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("nama_praktikum", "periode", "dosen_pengampu", "kontak", "updated_at")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("nama", "jabatan", "kontak", "urutan", "aktif")
    list_filter = ("jabatan", "aktif")
    search_fields = ("nama", "kontak")
    list_editable = ("urutan", "aktif")


@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):
    list_display = ("nama", "mentor", "progress")
    list_filter = ("mentor",)
    search_fields = ("nama", "mentor__nama")
    list_editable = ("progress",)


@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):
    list_display = ("nama", "nim", "kelompok", "email", "aktif")
    list_filter = ("aktif", "kelompok")
    search_fields = ("nama", "nim", "email")


@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):
    list_display = ("nama", "sub_acara", "tanggal_mulai", "lokasi", "status", "urutan")
    list_filter = ("status",)
    search_fields = ("nama", "sub_acara", "lokasi")
    ordering = ("urutan", "tanggal_mulai")


@admin.register(Materi)
class MateriAdmin(admin.ModelAdmin):
    list_display = ("judul", "kategori", "acara", "uploaded_at")
    list_filter = ("kategori",)
    search_fields = ("judul", "deskripsi")


@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = ("peserta", "acara", "status", "catatan")
    list_filter = ("status", "acara")
    search_fields = ("peserta__nama", "peserta__nim")


@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = ("judul", "aktif", "dibuat")
    list_filter = ("aktif",)
    search_fields = ("judul", "isi")


@admin.register(TataTertib)
class TataTertibAdmin(admin.ModelAdmin):
    list_display = ("judul", "aktif", "urutan")
    list_filter = ("aktif",)
    search_fields = ("judul", "isi")
    list_editable = ("urutan", "aktif")
