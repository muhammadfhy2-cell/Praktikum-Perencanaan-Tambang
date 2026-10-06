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


# =========================================================
# SETTING PRAKTIKUM
# =========================================================

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "nama_praktikum",
        "periode",
        "dosen_pengampu",
        "kontak",
        "updated_at",
    )

    search_fields = (
        "nama_praktikum",
        "periode",
        "dosen_pengampu",
    )

    fieldsets = (
        (
            "Informasi Praktikum",
            {
                "fields": (
                    "nama_praktikum",
                    "periode",
                    "deskripsi",
                )
            },
        ),
        (
            "Kontak",
            {
                "fields": (
                    "dosen_pengampu",
                    "kontak",
                )
            },
        ),
    )


# =========================================================
# STAFF / PERSONEL
# =========================================================

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

    list_editable = (
        "urutan",
        "aktif",
    )

    ordering = (
        "jabatan",
        "urutan",
        "nama",
    )


# =========================================================
# KELOMPOK
# =========================================================

@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "mentor",
        "progress",
        "jumlah_peserta",
    )

    list_filter = (
        "mentor",
    )

    search_fields = (
        "nama",
        "mentor__nama",
    )

    list_editable = (
        "progress",
    )

    autocomplete_fields = (
        "mentor",
    )

    def jumlah_peserta(self, obj):
        return obj.peserta.count()

    jumlah_peserta.short_description = "Jumlah Peserta"


# =========================================================
# PESERTA
# =========================================================

@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "nim",
        "kelompok",
        "email",
        "aktif",
    )

    list_filter = (
        "aktif",
        "kelompok",
    )

    search_fields = (
        "nama",
        "nim",
        "email",
    )

    list_editable = (
        "aktif",
    )

    autocomplete_fields = (
        "kelompok",
    )


# =========================================================
# ACARA
# =========================================================

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
        "tanggal_mulai",
    )

    search_fields = (
        "nama",
        "sub_acara",
        "lokasi",
    )

    list_editable = (
        "status",
        "urutan",
    )

    ordering = (
        "urutan",
        "tanggal_mulai",
    )


# =========================================================
# MATERI
# =========================================================

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

    autocomplete_fields = (
        "acara",
    )

    readonly_fields = (
        "uploaded_at",
    )


# =========================================================
# ABSENSI
# =========================================================

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
        "acara__nama",
    )

    autocomplete_fields = (
        "peserta",
        "acara",
    )


# =========================================================
# PENGUMUMAN
# =========================================================

@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "aktif",
        "dibuat",
    )

    list_filter = (
        "aktif",
        "dibuat",
    )

    search_fields = (
        "judul",
        "isi",
    )

    list_editable = (
        "aktif",
    )

    readonly_fields = (
        "dibuat",
    )


# =========================================================
# TATA TERTIB
# =========================================================

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

    list_editable = (
        "aktif",
        "urutan",
    )

    ordering = (
        "urutan",
        "id",
    )
