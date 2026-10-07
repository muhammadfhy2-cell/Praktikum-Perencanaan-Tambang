from django.db import models
from django.contrib.auth.models import User


class Setting(models.Model):
    nama_praktikum = models.CharField(
        max_length=200,
        default="Praktikum Perencanaan Tambang"
    )
    periode = models.CharField(max_length=100, default="2026/2027")
    deskripsi = models.TextField(blank=True)
    dosen_pengampu = models.CharField(max_length=200, blank=True)
    kontak = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_praktikum


class Staff(models.Model):
    ROLE = [
        ("penanggung_jawab", "Penanggung Jawab Praktikum"),
        ("koordinator", "Koordinator Asisten Dosen"),
        ("asisten", "Asisten Dosen"),
    ]

    nama = models.CharField(max_length=200)
    jabatan = models.CharField(max_length=30, choices=ROLE)
    kontak = models.CharField(max_length=100, blank=True)
    urutan = models.PositiveIntegerField(default=0)
    aktif = models.BooleanField(default=True)

    class Meta:
        ordering = ["jabatan", "urutan", "nama"]

    def __str__(self):
        return f"{self.nama} - {self.get_jabatan_display()}"


class Kelompok(models.Model):
    nama = models.CharField(max_length=100, unique=True)

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

    progress = models.PositiveIntegerField(
        default=0,
        help_text="Progress keseluruhan kelompok dalam persen."
    )

    catatan = models.TextField(blank=True)

    # LOGIN KELOMPOK
    akun_login = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="akun_kelompok",
    )

    aktif = models.BooleanField(default=True)

    class Meta:
        ordering = ["nama"]

    def __str__(self):
        return self.nama


class Peserta(models.Model):
    JABATAN = [
        ("ketua", "Ketua"),
        ("anggota", "Anggota"),
    ]

    STATUS = [
        ("aktif", "AKTIF"),
        ("gugur", "GUGUR"),
    ]

    nama = models.CharField(max_length=200)
    nim = models.CharField(max_length=50, blank=True)

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="peserta",
    )

    jabatan = models.CharField(
        max_length=20,
        choices=JABATAN,
        default="anggota"
    )

    email = models.EmailField(blank=True)
    aktif = models.BooleanField(default=True)

    akun = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profil_peserta",
    )

    # STATUS KEMAJUAN PESERTA
    status_kemajuan = models.CharField(
        max_length=20,
        choices=STATUS,
        default="aktif",
    )

    acara_gugur = models.ForeignKey(
        "Acara",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="peserta_gugur",
    )

    alasan_gugur = models.TextField(blank=True)

    class Meta:
        ordering = ["kelompok", "jabatan", "nama"]

    def __str__(self):
        return self.nama


class Acara(models.Model):
    nama = models.CharField(max_length=200)
    sub_acara = models.CharField(max_length=200, blank=True)

    tanggal_mulai = models.DateTimeField()
    tanggal_selesai = models.DateTimeField(
        null=True,
        blank=True
    )

    lokasi = models.CharField(max_length=200, blank=True)

    status = models.CharField(
        max_length=50,
        default="Belum Dimulai"
    )

    deskripsi = models.TextField(blank=True)
    urutan = models.PositiveIntegerField(default=0)

    # MC
    pembawa_acara = models.ManyToManyField(
        Staff,
        blank=True,
        related_name="acara_dibawakan",
        limit_choices_to={
            "jabatan__in": ["koordinator", "asisten"],
            "aktif": True,
        },
    )

    # PJ ACARA
    penanggung_jawab = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acara_penanggung_jawaban",
        limit_choices_to={
            "jabatan": "penanggung_jawab",
            "aktif": True,
        },
    )

    class Meta:
        ordering = ["urutan", "tanggal_mulai"]

    def __str__(self):
        return self.nama


class Materi(models.Model):
    KAT = [
        ("modul", "Modul"),
        ("dataset", "Dataset"),
        ("template", "Template"),
        ("lainnya", "Lainnya"),
    ]

    judul = models.CharField(max_length=200)
    kategori = models.CharField(
        max_length=30,
        default="modul",
        choices=KAT
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    file = models.FileField(
        upload_to="materi/%Y/%m/"
    )

    deskripsi = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul


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

    # 5 KOMPONEN ABSENSI
    start = models.BooleanField(
        default=False,
        verbose_name="START (20%)"
    )

    ishoma_1 = models.BooleanField(
        default=False,
        verbose_name="ISHOMA 1 (10%)"
    )

    ishoma_2 = models.BooleanField(
        default=False,
        verbose_name="ISHOMA 2 (10%)"
    )

    ishoma_3 = models.BooleanField(
        default=False,
        verbose_name="ISHOMA 3 (10%)"
    )

    ls = models.BooleanField(
        default=False,
        verbose_name="LS (50%)"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["peserta", "acara"],
                name="unique_peserta_acara"
            )
        ]

    @property
    def nilai_kehadiran(self):
        nilai = 0

        if self.start:
            nilai += 20

        if self.ishoma_1:
            nilai += 10

        if self.ishoma_2:
            nilai += 10

        if self.ishoma_3:
            nilai += 10

        if self.ls:
            nilai += 50

        return nilai


class Pengumuman(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    aktif = models.BooleanField(default=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat"]

    def __str__(self):
        return self.judul


class TataTertib(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    aktif = models.BooleanField(default=True)
    urutan = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["urutan", "id"]

    def __str__(self):
        return self.judul


class TugasPendahuluan(models.Model):
    judul = models.CharField(max_length=200)

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

    aktif = models.BooleanField(default=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat"]

    def __str__(self):
        return self.judul


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

    judul = models.CharField(max_length=200)

    file = models.FileField(
        upload_to="laporan_mingguan/%Y/%m/"
    )

    # SUDAH ADA DI MIGRATION 0004
    file_revisi = models.FileField(
        upload_to="laporan_revisi/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="File Revisi"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(blank=True)

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

    nilai_progress = models.PositiveIntegerField(
        default=0,
        help_text="Nilai progress acara 0-100 persen."
    )

    laporan_acc = models.BooleanField(default=False)
    peta_acc = models.BooleanField(default=False)
    ppt_acc = models.BooleanField(default=False)

    catatan = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["acara__urutan", "acara__tanggal_mulai"]
        constraints = [
            models.UniqueConstraint(
                fields=["kelompok", "acara"],
                name="unique_progress_kelompok_acara"
            )
        ]

    def __str__(self):
        return f"{self.kelompok} - {self.acara}"


# ============================================================
# FILE KELOMPOK
# ============================================================

class FileKelompok(models.Model):
    JENIS = [
        ("peta", "Peta"),
        ("ppt", "PPT"),
        ("excel", "Excel"),
        ("word", "Word"),
        ("pdf", "PDF"),
        ("lainnya", "Lainnya"),
    ]

    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("revisi", "Perlu Revisi"),
        ("acc", "ACC"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="file_kelompok"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_kelompok"
    )

    nama_file = models.CharField(max_length=200)

    jenis = models.CharField(
        max_length=20,
        choices=JENIS,
        default="lainnya"
    )

    file = models.FileField(
        upload_to="file_kelompok/%Y/%m/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(blank=True)

    uploaded_by = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_diupload"
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
        return self.nama_file


# ============================================================
# DAILY MOM
# ============================================================

class DailyMOM(models.Model):
    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="daily_mom"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="daily_mom"
    )

    tanggal = models.DateField()

    judul = models.CharField(
        max_length=200,
        default="Daily Minutes of Meeting"
    )

    isi = models.TextField()

    keputusan = models.TextField(blank=True)

    tindak_lanjut = models.TextField(blank=True)

    dibuat_oleh = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mom_dibuat"
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-tanggal", "-created_at"]

    def __str__(self):
        return f"{self.kelompok} - {self.tanggal}"


# ============================================================
# FULL REPORT
# ============================================================

class LaporanLengkap(models.Model):
    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("revisi", "Perlu Revisi"),
        ("acc", "ACC"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="laporan_lengkap"
    )

    judul = models.CharField(max_length=200)

    file = models.FileField(
        upload_to="laporan_lengkap/%Y/%m/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    catatan_admin = models.TextField(blank=True)

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
# FORMAT DOKUMEN ADMIN
# ============================================================

class FormatDokumen(models.Model):
    JENIS = [
        ("pdf", "PDF"),
        ("excel", "Excel"),
        ("word", "Word"),
        ("ppt", "PowerPoint"),
        ("lainnya", "Lainnya"),
    ]

    judul = models.CharField(max_length=200)

    jenis = models.CharField(
        max_length=20,
        choices=JENIS,
        default="lainnya"
    )

    file = models.FileField(
        upload_to="format_dokumen/%Y/%m/"
    )

    deskripsi = models.TextField(blank=True)

    aktif = models.BooleanField(default=True)

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.judul


# ============================================================
# KONSULTASI
# ============================================================

class Konsultasi(models.Model):
    STATUS = [
        ("menunggu", "Menunggu"),
        ("diproses", "Diproses"),
        ("selesai", "Selesai"),
    ]

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="konsultasi"
    )

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi_dibuat"
    )

    tujuan = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi_masuk"
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    topik = models.CharField(max_length=200)

    pertanyaan = models.TextField()

    jawaban = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu"
    )

    dibuat = models.DateTimeField(
        auto_now_add=True
    )

    diperbarui = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-dibuat"]

    def __str__(self):
        return self.topik
