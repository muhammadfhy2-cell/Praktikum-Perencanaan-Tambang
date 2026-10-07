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
# STAFF
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
        "progress",
        "status_kelompok",
        "akun_login",
    )

    list_filter = (
        "aktif",
    )

    search_fields = (
        "nama",
        "catatan",
    )

    filter_horizontal = (
        "mentor",
    )

    readonly_fields = (
        "logo_preview",
    )

    fieldsets = (
        (
            "Informasi Kelompok",
            {
                "fields": (
                    "nama",
                    "logo",
                    "logo_preview",
                    "aktif",
                )
            },
        ),
        (
            "Mentor",
            {
                "fields": (
                    "mentor",
                )
            },
        ),
        (
            "Akun Login",
            {
                "fields": (
                    "akun_login",
                )
            },
        ),
        (
            "Progress",
            {
                "fields": (
                    "progress",
                    "catatan",
                )
            },
        ),
    )

    def mentor_list(self, obj):
        return ", ".join(
            obj.mentor.values_list("nama", flat=True)
        ) or "-"

    mentor_list.short_description = "Mentor"

    def status_kelompok(self, obj):
        if obj.aktif:
            return format_html(
                '<span style="color:#16a34a;font-weight:700;">AKTIF</span>'
            )

        return format_html(
            '<span style="color:#dc2626;font-weight:700;">NONAKTIF</span>'
        )

    status_kelompok.short_description = "Status"

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit:cover;border-radius:12px;">',
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
    )

    list_select_related = (
        "kelompok",
        "akun",
        "acara_gugur",
    )

    fieldsets = (
        (
            "Identitas Peserta",
            {
                "fields": (
                    "nama",
                    "nim",
                    "email",
                    "kelompok",
                    "jabatan",
                    "akun",
                )
            },
        ),
        (
            "Status Kemajuan",
            {
                "fields": (
                    "status_kemajuan",
                    "acara_gugur",
                    "alasan_gugur",
                    "aktif",
                )
            },
        ),
    )


# ============================================================
# ACARA
# ============================================================

@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):
    list_display = (
        "urutan",
        "nama",
        "sub_acara",
        "tanggal_mulai",
        "tanggal_selesai",
        "status",
        "penanggung_jawab",
        "mc_list",
    )

    list_filter = (
        "status",
        "penanggung_jawab",
    )

    search_fields = (
        "nama",
        "sub_acara",
        "lokasi",
    )

    filter_horizontal = (
        "pembawa_acara",
    )

    ordering = (
        "urutan",
        "tanggal_mulai",
    )

    fieldsets = (
        (
            "Informasi Acara",
            {
                "fields": (
                    "nama",
                    "sub_acara",
                    "urutan",
                    "status",
                    "deskripsi",
                )
            },
        ),
        (
            "Waktu & Lokasi",
            {
                "fields": (
                    "tanggal_mulai",
                    "tanggal_selesai",
                    "lokasi",
                )
            },
        ),
        (
            "Penanggung Jawab",
            {
                "fields": (
                    "penanggung_jawab",
                    "pembawa_acara",
                )
            },
        ),
    )

    def mc_list(self, obj):
        return ", ".join(
            obj.pembawa_acara.values_list("nama", flat=True)
        ) or "-"

    mc_list.short_description = "MC"


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


# ============================================================
# ABSENSI
# ============================================================

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = (
        "peserta",
        "acara",
        "status",
        "nilai_kehadiran_display",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
    )

    list_filter = (
        "acara",
        "status",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
    )

    search_fields = (
        "peserta__nama",
        "peserta__nim",
    )

    list_select_related = (
        "peserta",
        "acara",
    )

    def nilai_kehadiran_display(self, obj):
        return f"{obj.nilai_kehadiran}%"

    nilai_kehadiran_display.short_description = "Nilai"


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
        "urutan",
        "judul",
        "aktif",
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

    list_select_related = (
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
                    "kelompok",
                    "peserta",
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
            "Pemeriksaan",
            {
                "fields": (
                    "status",
                    "catatan_admin",
                )
            },
        ),
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

    list_select_related = (
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

    list_select_related = (
        "kelompok",
        "acara",
        "uploaded_by",
    )

    fieldsets = (
        (
            "File",
            {
                "fields": (
                    "nama_file",
                    "jenis",
                    "file",
                    "kelompok",
                    "acara",
                    "uploaded_by",
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
    )


# ============================================================
# DAILY MOM
# ============================================================

@admin.register(DailyMOM)
class DailyMOMAdmin(admin.ModelAdmin):
    list_display = (
        "tanggal",
        "kelompok",
        "acara",
        "judul",
        "dibuat_oleh",
        "updated_at",
    )

    list_filter = (
        "kelompok",
        "acara",
        "tanggal",
    )

    search_fields = (
        "judul",
        "isi",
        "keputusan",
        "tindak_lanjut",
        "kelompok__nama",
    )

    list_select_related = (
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

    list_select_related = (
        "kelompok",
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
            "Pemeriksaan",
            {
                "fields": (
                    "status",
                    "catatan_admin",
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

    list_select_related = (
        "kelompok",
        "peserta",
        "tujuan",
        "acara",
    )

    fieldsets = (
        (
            "Informasi Konsultasi",
            {
                "fields": (
                    "kelompok",
                    "peserta",
                    "tujuan",
                    "acara",
                    "topik",
                    "pertanyaan",
                )
            },
        ),
        (
            "Tanggapan",
            {
                "fields": (
                    "jawaban",
                    "status",
                )
            },
        ),
    )
