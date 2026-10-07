from django.contrib import admin
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
        "logo_preview",
        "mentor_list",
        "jumlah_anggota_admin",
        "progress_persen",
        "status_kelompok",
        "akun_login",
    )

    list_filter = (
        "aktif",
    )

    search_fields = (
        "nama",
        "catatan",
        "akun_login__username",
    )

    filter_horizontal = (
        "mentor",
    )

    readonly_fields = (
        "logo_preview",
        "jumlah_anggota_admin",
        "progress_persen",
    )

    fieldsets = (
        (
            "Informasi Kelompok",
            {
                "fields": (
                    "nama",
                    "logo",
                    "logo_preview",
                    "catatan",
                )
            },
        ),
        (
            "Mentor / Pembimbing",
            {
                "fields": (
                    "mentor",
                )
            },
        ),
        (
            "Akun Login Kelompok",
            {
                "fields": (
                    "akun_login",
                    "aktif",
                )
            },
        ),
        (
            "Progress",
            {
                "fields": (
                    "progress",
                    "progress_persen",
                )
            },
        ),
    )

    def mentor_list(self, obj):
        mentors = obj.mentor.all()

        if not mentors:
            return "-"

        return ", ".join(
            mentor.nama for mentor in mentors
        )

    mentor_list.short_description = "Mentor"

    def jumlah_anggota_admin(self, obj):
        return obj.jumlah_anggota

    jumlah_anggota_admin.short_description = "Anggota Aktif"

    def status_kelompok(self, obj):
        if obj.aktif:
            return format_html(
                '<span style="color:green;font-weight:bold;">AKTIF</span>'
            )

        return format_html(
            '<span style="color:red;font-weight:bold;">NONAKTIF</span>'
        )

    status_kelompok.short_description = "Status"

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit:contain;border-radius:8px;" />',
                obj.logo.url,
            )

        return "-"

    logo_preview.short_description = "Logo"


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
        "akun",
    )

    list_filter = (
        "jabatan",
        "status_kemajuan",
        "aktif",
        "kelompok",
    )

    search_fields = (
        "nama",
        "nim",
        "email",
        "kelompok__nama",
        "akun__username",
    )

    autocomplete_fields = (
        "kelompok",
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
        "lokasi",
        "status",
        "penanggung_jawab",
        "urutan",
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

    autocomplete_fields = (
        "penanggung_jawab",
    )

    filter_horizontal = (
        "pembawa_acara",
    )

    ordering = (
        "urutan",
        "tanggal_mulai",
    )


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

    autocomplete_fields = (
        "acara",
    )


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

    autocomplete_fields = (
        "peserta",
        "acara",
    )

    readonly_fields = (
        "nilai_persentase",
    )

    fieldsets = (
        (
            "Data Kehadiran",
            {
                "fields": (
                    "peserta",
                    "acara",
                    "status",
                    "catatan",
                )
            },
        ),
        (
            "Komponen Kehadiran",
            {
                "fields": (
                    "start",
                    "ishoma_1",
                    "ishoma_2",
                    "ishoma_3",
                    "ls",
                )
            },
        ),
        (
            "Nilai",
            {
                "fields": (
                    "nilai_persentase",
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

    autocomplete_fields = (
        "acara",
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
    )

    search_fields = (
        "judul",
        "peserta__nama",
        "peserta__nim",
        "kelompok__nama",
        "acara__nama",
    )

    autocomplete_fields = (
        "peserta",
        "kelompok",
        "acara",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
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
            "File",
            {
                "fields": (
                    "file",
                    "file_revisi",
                )
            },
        ),
        (
            "Pemeriksaan Admin",
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


# ============================================================
# PROGRESS KELOMPOK PER ACARA
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
        "laporan_acc",
        "peta_acc",
        "ppt_acc",
        "acara",
        "kelompok",
    )

    search_fields = (
        "kelompok__nama",
        "acara__nama",
    )

    autocomplete_fields = (
        "kelompok",
        "acara",
    )

    readonly_fields = (
        "updated_at",
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
        "acara",
        "kelompok",
    )

    search_fields = (
        "nama_file",
        "kelompok__nama",
        "acara__nama",
        "uploaded_by__nama",
    )

    autocomplete_fields = (
        "kelompok",
        "acara",
        "uploaded_by",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Informasi File",
            {
                "fields": (
                    "nama_file",
                    "kelompok",
                    "acara",
                    "jenis",
                    "file",
                    "uploaded_by",
                )
            },
        ),
        (
            "Pemeriksaan Admin",
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


# ============================================================
# DAILY MOM
# ============================================================

@admin.register(DailyMOM)
class DailyMOMAdmin(admin.ModelAdmin):

    list_display = (
        "tanggal",
        "judul",
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
        "dibuat_oleh__nama",
    )

    autocomplete_fields = (
        "kelompok",
        "acara",
        "dibuat_oleh",
    )

    readonly_fields = (
        "dibuat",
        "updated_at",
    )

    fieldsets = (
        (
            "Informasi MOM",
            {
                "fields": (
                    "tanggal",
                    "judul",
                    "kelompok",
                    "acara",
                    "dibuat_oleh",
                )
            },
        ),
        (
            "Isi",
            {
                "fields": (
                    "isi",
                    "keputusan",
                    "tindak_lanjut",
                )
            },
        ),
        (
            "Waktu",
            {
                "fields": (
                    "dibuat",
                    "updated_at",
                )
            },
        ),
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

    autocomplete_fields = (
        "kelompok",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Laporan",
            {
                "fields": (
                    "judul",
                    "kelompok",
                    "file",
                )
            },
        ),
        (
            "Pemeriksaan Admin",
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

    readonly_fields = (
        "uploaded_at",
    )

    fieldsets = (
        (
            "Dokumen",
            {
                "fields": (
                    "judul",
                    "jenis",
                    "file",
                    "deskripsi",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "aktif",
                )
            },
        ),
        (
            "Waktu",
            {
                "fields": (
                    "uploaded_at",
                )
            },
        ),
    )


# ============================================================
# KONSULTASI
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
        "tujuan__nama",
    )

    autocomplete_fields = (
        "kelompok",
        "peserta",
        "tujuan",
        "acara",
    )

    readonly_fields = (
        "dibuat",
    )

    fieldsets = (
        (
            "Informasi Konsultasi",
            {
                "fields": (
                    "topik",
                    "kelompok",
                    "peserta",
                    "acara",
                    "tujuan",
                )
            },
        ),
        (
            "Pertanyaan",
            {
                "fields": (
                    "pertanyaan",
                )
            },
        ),
        (
            "Jawaban",
            {
                "fields": (
                    "jawaban",
                    "status",
                    "dijawab_at",
                )
            },
        ),
        (
            "Waktu",
            {
                "fields": (
                    "dibuat",
                )
            },
        ),
    )
