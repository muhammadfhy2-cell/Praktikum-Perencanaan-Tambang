from django.contrib import admin
from django.contrib.auth.models import User

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
            {
                "fields": ("akun_login",)
            },
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
# KONSULTASI PRIVAT
# ============================================================

@admin.register(Konsultasi)
class KonsultasiAdmin(admin.ModelAdmin):
    list_display = (
        "topik",
        "kelompok",
        "acara",
        "tujuan",
        "tanggal_konsultasi",
        "waktu_mulai",
        "waktu_selesai",
        "lokasi",
        "status",
        "dibuat",
    )

    list_filter = (
        "status",
        "tanggal_konsultasi",
        "tujuan",
        "acara",
        "kelompok",
    )

    search_fields = (
        "topik",
        "pertanyaan",
        "jawaban",
        "lokasi",
        "kelompok__nama",
        "peserta__nama",
        "tujuan__nama",
        "acara__nama",
    )

    list_per_page = 25
    date_hierarchy = "tanggal_konsultasi"
    ordering = (
        "-tanggal_konsultasi",
        "-waktu_mulai",
        "-dibuat",
    )

    autocomplete_fields = (
        "kelompok",
        "peserta",
        "tujuan",
        "acara",
    )

    readonly_fields = (
        "dibuat",
        "dijawab_at",
    )

    fieldsets = (
        (
            "Penerima dan Penanggung Jawab",
            {
                "description": (
                    "Pilih kelompok yang menerima informasi konsultasi. "
                    "Pastikan kelompok yang dipilih sudah benar."
                ),
                "fields": (
                    "kelompok",
                    "peserta",
                    "acara",
                    "tujuan",
                ),
            },
        ),
        (
            "Jadwal Konsultasi",
            {
                "fields": (
                    "topik",
                    "tanggal_konsultasi",
                    "waktu_mulai",
                    "waktu_selesai",
                    "lokasi",
                ),
            },
        ),
        (
            "Pertanyaan dan Jawaban",
            {
                "fields": (
                    "pertanyaan",
                    "jawaban",
                ),
            },
        ),
        (
            "Status dan Riwayat",
            {
                "fields": (
                    "status",
                    "dibuat",
                    "dijawab_at",
                ),
            },
        ),
    )


# ============================================================
# USER DJANGO
# ============================================================
#
# User bawaan Django tetap digunakan untuk login kelompok.
# Admin Django bawaan User tetap tersedia.
#
# Tidak perlu membuat model User baru.
# ============================================================
