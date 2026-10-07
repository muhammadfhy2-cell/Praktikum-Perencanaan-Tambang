from django.contrib.auth.models import User
from django.db import models


# ============================================================
# SETTING
# ============================================================

class Setting(models.Model):
    nama_praktikum = models.CharField(
        max_length=200,
        default="Praktikum Perencanaan Tambang"
    )
    periode = models.CharField(
        max_length=100,
        default="2026/2027"
    )
    deskripsi = models.TextField(blank=True)
    dosen_pengampu = models.CharField(max_length=200, blank=True)
    kontak = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_praktikum


# ============================================================
# STAFF
# ============================================================

class Staff(models.Model):

    ROLE = [
        (
            "penanggung_jawab",
            "Penanggung Jawab Praktikum"
        ),
        (
            "koordinator",
            "Koordinator Asisten Dosen"
        ),
        (
            "asisten",
            "Asisten Dosen"
        ),
    ]

    nama = models.CharField(max_length=200)

    jabatan = models.CharField(
        max_length=30,
        choices=ROLE
    )

    kontak = models.CharField(
        max_length=100,
        blank=True
    )

    urutan = models.PositiveIntegerField(
        default=0
    )

    aktif = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = [
            "jabatan",
            "urutan",
            "nama"
        ]

    def __str__(self):
        return f"{self.nama} - {self.get_jabatan_display()}"


# ============================================================
# KELOMPOK
# ============================================================

class Kelompok(models.Model):

    nama = models.CharField(
        max_length=100,
        unique=True
    )

    mentor = models.ManyToManyField(
        Staff,
        blank=True,
        related_name="kelompok_binaan",
        limit_choices_to={
            "jabatan__in": [
                "penanggung_jawab",
                "koordinator",
                "asisten",
            ],
            "aktif": True,
        },
    )

    logo = models.ImageField(
        upload_to="logo_kelompok/",
        blank=True,
        null=True
    )

    # AKUN LOGIN KELOMPOK
    akun_login = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="akun_kelompok",
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    catatan = models.TextField(
        blank=True
    )

    aktif = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nama


# ============================================================
# PESERTA
# ============================================================

class Peserta(models.Model):

    JABATAN = [
        ("ketua", "Ketua"),
        ("anggota", "Anggota"),
    ]

    STATUS = [
        ("aktif", "AKTIF"),
        ("gugur", "GUGUR"),
    ]

    nama = models.CharField(
        max_length=200
    )

    nim = models.CharField(
        max_length=50,
        blank=True
    )

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="peserta"
    )

    jabatan = models.CharField(
        max_length=20,
        choices=JABATAN,
        default="anggota"
    )

    email = models.EmailField(
        blank=True
    )

    aktif = models.BooleanField(
        default=True
    )

    # Dipertahankan untuk kompatibilitas data lama
    akun = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profil_peserta",
    )

    # STATUS KEMAJUAN
    status_kemajuan = models.CharField(
        max_length=20,
        choices=STATUS,
        default="aktif"
    )

    acara_gugur = models.ForeignKey(
        "Acara",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="peserta_gugur",
    )

    alasan_gugur = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.nama


# ============================================================
# ACARA
# ============================================================

class Acara(models.Model):

    nama = models.CharField(
        max_length=200
    )

    sub_acara = models.CharField(
        max_length=200,
        blank=True
    )

    tanggal_mulai = models.DateTimeField()

    tanggal_selesai = models.DateTimeField(
        null=True,
        blank=True
    )

    lokasi = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        default="Belum Dimulai"
    )

    deskripsi = models.TextField(
        blank=True
    )

    urutan = models.PositiveIntegerField(
        default=0
    )

    # MC:
    # KOORDINATOR + ASISTEN
    pembawa_acara = models.ManyToManyField(
        Staff,
        blank=True,
        related_name="acara_dibawakan",
        limit_choices_to={
            "jabatan__in": [
                "koordinator",
                "asisten",
            ],
            "aktif": True,
        },
    )

    # PENANGGUNG JAWAB ACARA
    # HANYA PENANGGUNG JAWAB PRAKTIKUM
    penanggung_jawab = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acara_ditangani",
        limit_choices_to={
            "jabatan": "penanggung_jawab",
            "aktif": True,
        },
    )

    class Meta:
        ordering = [
            "urutan",
            "tanggal_mulai"
        ]

    def __str__(self):
        return self.nama


# ============================================================
# MATERI
# ============================================================

class Materi(models.Model):

    KAT = [
        ("modul", "Modul"),
        ("dataset", "Dataset"),
        ("template", "Template"),
        ("lainnya", "Lainnya"),
    ]

    judul = models.CharField(
        max_length=200
    )

    kategori = models.CharField(
        max_length=30,
        default="modul",
        choices=KAT
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    file = models.FileField(
        upload_to="materi/%Y/%m/"
    )

    deskripsi = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.judul


# ============================================================
# ABSENSI
# ============================================================

class Absensi(models.Model):

    STATUS = [
        ("H", "Hadir"),
        ("I", "Izin"),
        ("S", "Sakit"),
        ("A", "Alfa"),
    ]

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.CASCADE,
        related_name="absensi"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="absensi"
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        default="H"
    )

    catatan = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "peserta",
                    "acara"
                ],
                name="unique_peserta_acara"
            )
        ]

    def __str__(self):
        return f"{self.peserta.nama} - {self.acara.nama}"


# ============================================================
# PENGUMUMAN
# ============================================================

class Pengumuman(models.Model):

    judul = models.CharField(
        max_length=200
    )

    isi = models.TextField()

    aktif = models.BooleanField(
        default=True
    )

    dibuat = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-dibuat"]

    def __str__(self):
        return self.judul


# ============================================================
# TATA TERTIB
# ============================================================

class TataTertib(models.Model):

    judul = models.CharField(
        max_length=200
    )

    isi = models.TextField()

    aktif = models.BooleanField(
        default=True
    )

    urutan = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = [
            "urutan",
            "id"
        ]

    def __str__(self):
        return self.judul


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

class TugasPendahuluan(models.Model):

    judul = models.CharField(
        max_length=200
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="tugas_pendahuluan"
    )

    soal = models.TextField()

    file = models.FileField(
        upload_to="tugas_pendahuluan/%Y/%m/",
        blank=True,
        null=True
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True
    )

    aktif = models.BooleanField(
        default=True
    )

    dibuat = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-dibuat"]

    def __str__(self):
        return self.judul


# ============================================================
# LAPORAN MINGGUAN
# ============================================================

class LaporanMingguan(models.Model):

    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("acc", "Disetujui / ACC"),
        ("revisi", "Perlu Revisi"),
    ]

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.CASCADE,
        related_name="laporan_mingguan"
    )

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="laporan_mingguan"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="laporan_mingguan"
    )

    judul = models.CharField(
        max_length=200
    )

    file = models.FileField(
        upload_to="laporan_mingguan/%Y/%m/"
    )

    file_revisi = models.FileField(
        upload_to="laporan_revisi/%Y/%m/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.judul


# ============================================================
# PROGRESS PER ACARA
# ============================================================

class ProgressAcara(models.Model):

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="progress_acara"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="progress_kelompok"
    )

    nilai = models.PositiveIntegerField(
        default=0
    )

    catatan = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "acara__urutan",
            "acara__tanggal_mulai"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "kelompok",
                    "acara"
                ],
                name="unique_progress_kelompok_acara"
            )
        ]

    def __str__(self):
        return f"{self.kelompok.nama} - {self.acara.nama}"


# ============================================================
# FILE KELOMPOK
# PETA / PPT
# ============================================================

class FileKelompok(models.Model):

    JENIS = [
        ("peta", "Peta"),
        ("ppt", "Desain / PPT"),
    ]

    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("acc", "Disetujui / ACC"),
        ("revisi", "Perlu Revisi"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="file_kelompok"
    )

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.CASCADE,
        related_name="file_kelompok",
        null=True,
        blank=True
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="file_kelompok",
        null=True,
        blank=True
    )

    jenis = models.CharField(
        max_length=20,
        choices=JENIS
    )

    judul = models.CharField(
        max_length=200
    )

    file = models.FileField(
        upload_to="file_kelompok/%Y/%m/"
    )

    file_revisi = models.FileField(
        upload_to="file_kelompok_revisi/%Y/%m/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.judul


# ============================================================
# DAILY MOM
# ============================================================

class DailyMOM(models.Model):

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="daily_mom"
    )

    tanggal = models.DateField()

    kegiatan = models.TextField()

    progress = models.TextField(
        blank=True
    )

    kendala = models.TextField(
        blank=True
    )

    rencana = models.TextField(
        blank=True
    )

    dibuat = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-tanggal",
            "-id"
        ]

    def __str__(self):
        return f"{self.kelompok.nama} - {self.tanggal}"


# ============================================================
# LAPORAN LENGKAP
# ============================================================

class LaporanLengkap(models.Model):

    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("acc", "Disetujui / ACC"),
        ("revisi", "Perlu Revisi"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="laporan_lengkap"
    )

    file = models.FileField(
        upload_to="laporan_lengkap/%Y/%m/"
    )

    file_revisi = models.FileField(
        upload_to="laporan_lengkap_revisi/%Y/%m/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Laporan Lengkap - {self.kelompok.nama}"


# ============================================================
# KEMAJUAN PESERTA
# ============================================================

class KemajuanPeserta(models.Model):

    STATUS = [
        ("aktif", "AKTIF"),
        ("gugur", "GUGUR"),
    ]

    peserta = models.OneToOneField(
        Peserta,
        on_delete=models.CASCADE,
        related_name="kemajuan"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="aktif"
    )

    acara_gugur = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kemajuan_gugur"
    )

    alasan_gugur = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.peserta.nama} - {self.get_status_display()}"


# ============================================================
# FORMAT DOKUMEN
# ============================================================

class FormatDokumen(models.Model):

    judul = models.CharField(
        max_length=200
    )

    kategori = models.CharField(
        max_length=100,
        blank=True
    )

    file = models.FileField(
        upload_to="format/%Y/%m/"
    )

    deskripsi = models.TextField(
        blank=True
    )

    aktif = models.BooleanField(
        default=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.judul


# ============================================================
# KONSULTASI
# ============================================================

class Konsultasi(models.Model):

    DENGAN = [
        ("asisten", "Asisten Dosen"),
        ("koordinator", "Koordinator Asisten Dosen"),
        ("pj_acara", "Penanggung Jawab Acara"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="konsultasi"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi"
    )

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi"
    )

    konsultasi_dengan = models.CharField(
        max_length=30,
        choices=DENGAN
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi_masuk"
    )

    tanggal = models.DateTimeField()

    topik = models.CharField(
        max_length=200
    )

    hasil = models.TextField(
        blank=True
    )

    tindak_lanjut = models.TextField(
        blank=True
    )

    dibuat = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-tanggal"]

    def __str__(self):
        return f"{self.kelompok.nama} - {self.topik}"
