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
    TugasPendahuluan,
    LaporanMingguan,
)


# ============================================================
# SETTING PRAKTIKUM
# ============================================================

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

    def has_add_permission(self, request):
        # Hanya boleh ada satu Setting
        return not Setting.objects.exists()


# ============================================================
# STAFF / PERSONEL
# ============================================================

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


# ============================================================
# KELOMPOK
# ============================================================

@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "jumlah_anggota",
        "mentor_list",
        "progress",
        "aktif_logo",
    )

    search_fields = (
        "nama",
        "catatan",
        "mentor__nama",
    )

    list_filter = (
        "progress",
    )

    # Memilih lebih dari satu mentor
    filter_horizontal = (
        "mentor",
    )

    ordering = (
        "nama",
    )

    def jumlah_anggota(self, obj):
        return obj.peserta.count()

    jumlah_anggota.short_description = "Jumlah Anggota"

    def mentor_list(self, obj):
        mentors = obj.mentor.all()

        if not mentors:
            return "Belum ditentukan"

        return ", ".join(
            mentor.nama
            for mentor in mentors
        )

    mentor_list.short_description = "Mentor"

    def aktif_logo(self, obj):
        return "Ya" if obj.logo else "Tidak"

    aktif_logo.short_description = "Logo"


# ============================================================
# PESERTA
# ============================================================

@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "nim",
        "kelompok",
        "jabatan",
        "email",
        "akun",
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
        "kelompok__nama",
    )

    list_select_related = (
        "kelompok",
        "akun",
    )

    ordering = (
        "kelompok",
        "jabatan",
        "nama",
    )


# ============================================================
# ACARA / JADWAL
# ============================================================

@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "sub_acara",
        "tanggal_mulai",
        "tanggal_selesai",
        "lokasi",
        "status",
        "mc_list",
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
        "deskripsi",
        "pembawa_acara__nama",
    )

    filter_horizontal = (
        "pembawa_acara",
    )

    ordering = (
        "urutan",
        "tanggal_mulai",
    )

    def mc_list(self, obj):

        mc = obj.pembawa_acara.all()

        if not mc:
            return "Belum ditentukan"

        return ", ".join(
            personel.nama
            for personel in mc
        )

    mc_list.short_description = "Pembawa Acara / MC"


# ============================================================
# MATERI
# ============================================================

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
        "acara__nama",
    )

    ordering = (
        "-uploaded_at",
    )


# ============================================================
# ABSENSI
# ============================================================

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):

    list_display = (
        "peserta",
        "kelompok",
        "acara",
        "status",
        "catatan",
    )

    list_filter = (
        "status",
        "acara",
        "peserta__kelompok",
    )

    search_fields = (
        "peserta__nama",
        "peserta__nim",
        "peserta__kelompok__nama",
        "acara__nama",
    )

    list_select_related = (
        "peserta",
        "peserta__kelompok",
        "acara",
    )

    def kelompok(self, obj):

        if obj.peserta.kelompok:
            return obj.peserta.kelompok.nama

        return "-"

    kelompok.short_description = "Kelompok"


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

@admin.register(TugasPendahuluan)
class TugasPendahuluanAdmin(admin.ModelAdmin):

    list_display = (
        "judul",
        "acara",
        "deadline",
        "aktif",
        "dibuat",
    )

    list_filter = (
        "aktif",
        "acara",
        "deadline",
    )

    search_fields = (
        "judul",
        "soal",
        "acara__nama",
    )

    ordering = (
        "-dibuat",
    )

    readonly_fields = (
        "dibuat",
    )

    fieldsets = (
        (
            "Informasi Tugas",
            {
                "fields": (
                    "judul",
                    "acara",
                    "soal",
                    "file",
                )
            },
        ),

        (
            "Pengaturan",
            {
                "fields": (
                    "deadline",
                    "aktif",
                )
            },
        ),

        (
            "Informasi Sistem",
            {
                "fields": (
                    "dibuat",
                )
            },
        ),
    )


# ============================================================
# LAPORAN MINGGUAN
# ============================================================

@admin.register(LaporanMingguan)
class LaporanMingguanAdmin(admin.ModelAdmin):

    list_display = (
        "judul",
        "peserta",
        "kelompok",
        "acara",
        "status",
        "uploaded_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "acara",
        "kelompok",
        "uploaded_at",
    )

    search_fields = (
        "judul",
        "peserta__nama",
        "peserta__nim",
        "kelompok__nama",
        "acara__nama",
    )

    list_select_related = (
        "peserta",
        "kelompok",
        "acara",
    )

    ordering = (
        "-uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
    )

    # Admin bisa mengubah status langsung dari daftar
    list_editable = (
        "status",
    )

    fieldsets = (
        (
            "Informasi Laporan",
            {
                "fields": (
                    "judul",
                    "peserta",
                    "kelompok",
                    "acara",
                    "file",
                )
            },
        ),

        (
            "Pemeriksaan",
            {
                "fields": (
                    "status",
                    "catatan_admin",
                )
            },
        ),

        (
            "Informasi Waktu",
            {
                "fields": (
                    "uploaded_at",
                    "updated_at",
                )
            },
        ),
    )


# ============================================================
# PENGUMUMAN
# ============================================================

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

    ordering = (
        "-dibuat",
    )


# ============================================================
# TATA TERTIB
# ============================================================

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
