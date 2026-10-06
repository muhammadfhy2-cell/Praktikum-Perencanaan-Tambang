from django.contrib import admin

from .models import (
    Setting,
    Staff,
    Kelompok,
    Peserta,
    Acara,
    Materi,
    Absensi,
    Pengumuman,
    TataTertib,
)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "nama_praktikum",
        "periode",
        "dosen_pengampu",
        "kontak",
        "updated_at",
    )

    def has_add_permission(self, request):
        return not Setting.objects.exists()


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "jabatan",
        "kontak",
        "urutan",
        "aktif",
    )

    list_filter = (
        "jabatan",
        "aktif",
    )

    search_fields = (
        "nama",
        "kontak",
    )

    ordering = (
        "jabatan",
        "urutan",
        "nama",
    )


@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "jumlah_anggota",
        "progress",
        "catatan",
    )

    search_fields = (
        "nama",
    )

    filter_horizontal = (
        "mentor",
    )

    def jumlah_anggota(self, obj):
        return obj.peserta.count()

    jumlah_anggota.short_description = "Jumlah Anggota"


@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "nim",
        "kelompok",
        "jabatan",
        "email",
        "aktif",
    )

    list_filter = (
        "jabatan",
        "kelompok",
        "aktif",
    )

    search_fields = (
        "nama",
        "nim",
        "email",
    )


@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "sub_acara",
        "tanggal_mulai",
        "tanggal_selesai",
        "lokasi",
        "status",
        "urutan",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "nama",
        "sub_acara",
        "lokasi",
    )

    ordering = (
        "urutan",
        "tanggal_mulai",
    )


@admin.register(Materi)
class MateriAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "kategori",
        "acara",
        "uploaded_at",
    )

    list_filter = (
        "kategori",
        "acara",
    )

    search_fields = (
        "judul",
        "deskripsi",
    )


@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = (
        "peserta",
        "acara",
        "status",
        "catatan",
    )

    list_filter = (
        "status",
        "acara",
    )

    search_fields = (
        "peserta__nama",
        "peserta__nim",
    )


@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "aktif",
        "dibuat",
    )

    list_filter = (
        "aktif",
    )

    search_fields = (
        "judul",
        "isi",
    )


@admin.register(TataTertib)
class TataTertibAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "aktif",
        "urutan",
    )

    list_filter = (
        "aktif",
    )

    search_fields = (
        "judul",
        "isi",
    )

    ordering = (
        "urutan",
        "id",
    )
