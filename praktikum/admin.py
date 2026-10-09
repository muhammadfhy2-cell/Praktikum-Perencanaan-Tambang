
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html

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
    ProgressAcara,
    FileKelompok,
    DailyMOM,
    LaporanLengkap,
    FormatDokumen,
    Konsultasi,
)


# ============================================================
# HELPER TAUTAN UNDUHAN LAPORAN
# ============================================================

def tautan_download_laporan(obj, jenis, nama_url, label):
    """
    Mengarahkan admin ke view download laporan.
    File tidak diakses langsung menggunakan URL media.
    """
    field = (
        getattr(obj, "file_revisi", None)
        if jenis == "revisi"
        else getattr(obj, "file", None)
    )

    if not field or not getattr(field, "name", ""):
        return "Belum ada file"

    try:
        url = reverse(nama_url, args=[obj.pk, jenis])
    except NoReverseMatch:
        return "Rute unduhan belum tersedia"

    nama_file = field.name.rsplit("/", 1)[-1]

    return format_html(
        '<a href="{}" target="_blank" rel="noopener noreferrer">'
        'Unduh {} — {}</a>',
        url,
        label,
        nama_file,
    )


# ============================================================
# SETTING
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


# ============================================================
# STAFF / ASISTEN
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

    list_editable = (
        "aktif",
        "urutan",
    )


# ============================================================
# KELOMPOK
# ============================================================

@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "akun_login",
        "aktif",
        "jumlah_anggota",
        "jumlah_event",
        "progress_persen",
    )

    list_filter = ("aktif",)

    search_fields = (
        "nama",
        "akun_login__username",
    )

    filter_horizontal = ("mentor",)

    list_editable = ("aktif",)

    readonly_fields = (
        "jumlah_anggota",
        "jumlah_event",
        "progress_persen",
    )

    fieldsets = (
        (
            "Informasi Kelompok",
            {
                "fields": (
                    "nama",
                    "mentor",
                    "logo",
                    "aktif",
                )
            },
        ),
        (
            "Akun Login",
            {"fields": ("akun_login",)},
        ),
        (
            "Progress",
            {
                "fields": (
                    "progress",
                    "progress_persen",
                    "catatan",
                )
            },
        ),
        (
            "Informasi Otomatis",
            {
                "fields": (
                    "jumlah_anggota",
                    "jumlah_event",
                )
            },
        ),
    )


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
        "status_kemajuan",
        "aktif",
    )

    list_filter = (
        "kelompok",
        "jabatan",
        "status_kemajuan",
        "aktif",
    )

    search_fields = (
        "nama",
        "nim",
        "email",
        "kelompok__nama",
    )

    list_editable = ("aktif",)

    autocomplete_fields = (
        "kelompok",
        "akun",
        "acara_gugur",
    )


# ============================================================
# ACARA
# ============================================================

@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "sub_acara",
        "tanggal_mulai",
        "tanggal_selesai",
        "status",
        "urutan",
        "penanggung_jawab",
    )

    list_filter = (
        "status",
        "penanggung_jawab",
    )

    search_fields = (
        "nama",
        "sub_acara",
        "lokasi",
        "deskripsi",
    )

    list_editable = (
        "status",
        "urutan",
    )

    filter_horizontal = ("pembawa_acara",)

    autocomplete_fields = ("penanggung_jawab",)


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
    )

    autocomplete_fields = ("acara",)


# ============================================================
# ABSENSI
# ============================================================

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = (
        "peserta",
        "acara",
        "status",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
        "nilai_persentase",
    )

    list_filter = (
        "status",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
        "acara",
    )

    search_fields = (
        "peserta__nama",
        "peserta__nim",
        "acara__nama",
    )

    list_editable = (
        "status",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
    )

    autocomplete_fields = (
        "peserta",
        "acara",
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

    list_filter = ("aktif",)

    search_fields = (
        "judul",
        "isi",
    )

    list_editable = ("aktif",)


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

    list_filter = ("aktif",)

    search_fields = (
        "judul",
        "isi",
    )

    list_editable = (
        "aktif",
        "urutan",
    )


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
    )

    search_fields = (
        "judul",
        "soal",
    )

    list_editable = ("aktif",)

    autocomplete_fields = ("acara",)


# ============================================================
# LAPORAN MINGGUAN
# ============================================================

@admin.register(LaporanMingguan)
class LaporanMingguanAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "kelompok",
        "peserta",
        "acara",
        "status",
        "tautan_file_asli",
        "tautan_file_revisi",
        "uploaded_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "kelompok",
        "acara",
    )

    search_fields = (
        "judul",
        "peserta__nama",
        "kelompok__nama",
    )

    list_editable = ("status",)

    autocomplete_fields = (
        "peserta",
        "kelompok",
        "acara",
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
                )
            },
        ),
        (
            "File Laporan",
            {
                "fields": (
                    "file",
                    "tautan_file_asli",
                    "file_revisi",
                    "tautan_file_revisi",
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
            "Waktu",
            {
                "fields": (
                    "uploaded_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
        "tautan_file_asli",
        "tautan_file_revisi",
    )

    @admin.display(description="Unduh File Asli")
    def tautan_file_asli(self, obj):
        return tautan_download_laporan(
            obj,
            "asli",
            "praktikum:download_laporan_mingguan_admin",
            "file asli",
        )

    @admin.display(description="Unduh File Revisi")
    def tautan_file_revisi(self, obj):
        return tautan_download_laporan(
            obj,
            "revisi",
            "praktikum:download_laporan_mingguan_admin",
            "file revisi",
        )


# ============================================================
# PROGRESS ACARA
# ============================================================

@admin.register(ProgressAcara)
class ProgressAcaraAdmin(admin.ModelAdmin):
    list_display = (
        "kelompok",
        "acara",
        "nilai_progress",
        "laporan_acc",
        "peta_acc",
        "ppt_acc",
        "updated_at",
    )

    list_filter = (
        "kelompok",
        "acara",
        "laporan_acc",
        "peta_acc",
        "ppt_acc",
    )

    search_fields = (
        "kelompok__nama",
        "acara__nama",
    )

    list_editable = (
        "nilai_progress",
        "laporan_acc",
        "peta_acc",
        "ppt_acc",
    )

    autocomplete_fields = (
        "kelompok",
        "acara",
    )


# ============================================================
# FILE KELOMPOK
# ============================================================

@admin.register(FileKelompok)
class FileKelompokAdmin(admin.ModelAdmin):
    list_display = (
        "nama_file",
        "kelompok",
        "acara",
        "jenis",
        "status",
        "uploaded_by",
        "uploaded_at",
    )

    list_filter = (
        "jenis",
        "status",
        "kelompok",
        "acara",
    )

    search_fields = (
        "nama_file",
        "kelompok__nama",
        "uploaded_by__nama",
    )

    list_editable = ("status",)

    autocomplete_fields = (
        "kelompok",
        "acara",
        "uploaded_by",
    )


# ============================================================
# DAILY MOM
# ============================================================

@admin.register(DailyMOM)
class DailyMOMAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "tanggal",
        "kelompok",
        "acara",
        "dibuat_oleh",
        "dibuat",
    )

    list_filter = (
        "tanggal",
        "kelompok",
        "acara",
    )

    search_fields = (
        "judul",
        "isi",
        "keputusan",
        "tindak_lanjut",
        "kelompok__nama",
    )

    autocomplete_fields = (
        "kelompok",
        "acara",
        "dibuat_oleh",
    )


# ============================================================
# LAPORAN LENGKAP
# ============================================================

@admin.register(LaporanLengkap)
class LaporanLengkapAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "kelompok",
        "status",
        "tautan_file_asli",
        "tautan_file_revisi",
        "uploaded_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "kelompok",
    )

    search_fields = (
        "judul",
        "kelompok__nama",
    )

    list_editable = ("status",)

    autocomplete_fields = ("kelompok",)

    fieldsets = (
        (
            "Informasi Laporan",
            {
                "fields": (
                    "judul",
                    "kelompok",
                    "status",
                    "catatan_admin",
                )
            },
        ),
        (
            "File Laporan",
            {
                "fields": (
                    "file",
                    "tautan_file_asli",
                    "file_revisi",
                    "tautan_file_revisi",
                )
            },
        ),
        (
            "Waktu",
            {
                "fields": (
                    "uploaded_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
        "tautan_file_asli",
        "tautan_file_revisi",
    )

    @admin.display(description="Unduh File Asli")
    def tautan_file_asli(self, obj):
        return tautan_download_laporan(
            obj,
            "asli",
            "praktikum:download_laporan_lengkap_admin",
            "file asli",
        )

    @admin.display(description="Unduh File Revisi")
    def tautan_file_revisi(self, obj):
        return tautan_download_laporan(
            obj,
            "revisi",
            "praktikum:download_laporan_lengkap_admin",
            "file revisi",
        )


# ============================================================
# FORMAT DOKUMEN
# ============================================================

@admin.register(FormatDokumen)
class FormatDokumenAdmin(admin.ModelAdmin):
    list_display = (
        "judul",
        "jenis",
        "aktif",
        "uploaded_at",
    )

    list_filter = (
        "jenis",
        "aktif",
    )

    search_fields = (
        "judul",
        "deskripsi",
    )

    list_editable = ("aktif",)


# ============================================================
# KONSULTASI
# Tetap dipertahankan; tidak ada perubahan fitur konsultasi.
# ============================================================

@admin.register(Konsultasi)
class KonsultasiAdmin(admin.ModelAdmin):
    list_display = (
        "topik",
        "kelompok",
        "peserta",
        "tujuan",
        "acara",
        "status",
        "dibuat",
        "dijawab_at",
    )

    list_filter = (
        "status",
        "tujuan",
        "acara",
        "kelompok",
    )

    search_fields = (
        "topik",
        "pertanyaan",
        "jawaban",
        "kelompok__nama",
        "peserta__nama",
    )

    list_editable = ("status",)

    autocomplete_fields = (
        "kelompok",
        "peserta",
        "tujuan",
        "acara",
    )
