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


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):

    list_display = (
        "nama_praktikum",
        "periode",
        "dosen_pengampu",
        "kontak",
        "updated_at",
    )


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


@admin.register(Kelompok)
class KelompokAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "progress",
    )

    search_fields = (
        "nama",
    )

    filter_horizontal = (
        "mentor",
    )


@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "nim",
        "kelompok",
        "jabatan",
        "akun",
        "aktif",
    )

    list_filter = (
        "kelompok",
        "jabatan",
        "aktif",
    )

    search_fields = (
        "nama",
        "nim",
        "email",
        "akun__username",
    )

    autocomplete_fields = (
        "akun",
    )


@admin.register(Acara)
class AcaraAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "sub_acara",
        "tanggal_mulai",
        "lokasi",
        "status",
        "tampilkan_pembawa_acara",
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

    filter_horizontal = (
        "pembawa_acara",
    )

    fieldsets = (
        (
            "Informasi Acara",
            {
                "fields": (
                    "nama",
                    "sub_acara",
                    "tanggal_mulai",
                    "tanggal_selesai",
                    "lokasi",
                    "status",
                    "deskripsi",
                    "urutan",
                )
            },
        ),
        (
            "Pembawa Acara",
            {
                "description": (
                    "Pilih satu atau beberapa Asisten Dosen "
                    "yang bertugas sebagai pembawa acara."
                ),
                "fields": (
                    "pembawa_acara",
                ),
            },
        ),
    )

    @admin.display(
        description="Pembawa Acara"
    )
    def tampilkan_pembawa_acara(self, obj):

        data = obj.pembawa_acara.all()

        if not data:
            return "-"

        return ", ".join(
            staff.nama
            for staff in data
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
        "start_display",
        "ishoma1_display",
        "ishoma2_display",
        "ishoma3_display",
        "ls_display",
        "nilai_absensi",
        "akumulasi_absensi",
    )

    list_filter = (
        "acara",
        "start",
        "ishoma_1",
        "ishoma_2",
        "ishoma_3",
        "ls",
    )

    search_fields = (
        "peserta__nama",
        "peserta__nim",
        "acara__nama",
    )

    fieldsets = (
        (
            "Data Absensi",
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
            "Penilaian Absensi",
            {
                "description": (
                    "Setiap acara memiliki nilai maksimum 100%."
                ),
                "fields": (
                    "start",
                    "ishoma_1",
                    "ishoma_2",
                    "ishoma_3",
                    "ls",
                ),
            },
        ),
    )

    @admin.display(description="START")
    def start_display(self, obj):
        return "20%" if obj.start else "0%"

    @admin.display(description="ISHOMA 1")
    def ishoma1_display(self, obj):
        return "10%" if obj.ishoma_1 else "0%"

    @admin.display(description="ISHOMA 2")
    def ishoma2_display(self, obj):
        return "10%" if obj.ishoma_2 else "0%"

    @admin.display(description="ISHOMA 3")
    def ishoma3_display(self, obj):
        return "10%" if obj.ishoma_3 else "0%"

    @admin.display(description="LS")
    def ls_display(self, obj):
        return "50%" if obj.ls else "0%"

    @admin.display(description="Nilai Acara")
    def nilai_absensi(self, obj):
        return f"{obj.nilai_persentase}%"

    @admin.display(description="Akumulasi")
    def akumulasi_absensi(self, obj):

        peserta = obj.peserta

        jumlah = peserta.absensi.count()

        if jumlah == 0:
            return "0%"

        return f"{peserta.persentase_absensi}%"


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
        "urutan",
        "aktif",
    )

    list_filter = (
        "aktif",
    )

    search_fields = (
        "judul",
        "isi",
    )


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
        "kelompok",
        "acara",
    )

    search_fields = (
        "judul",
        "peserta__nama",
        "peserta__nim",
        "kelompok__nama",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Laporan Peserta",
            {
                "fields": (
                    "peserta",
                    "kelompok",
                    "acara",
                    "judul",
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
                    "file_revisi",
                )
            },
        ),
        (
            "Informasi Sistem",
            {
                "fields": (
                    "uploaded_at",
                    "updated_at",
                )
            },
        ),
    )

    ordering = (
        "-uploaded_at",
    )
