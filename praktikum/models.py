from django.db import models
from django.contrib.auth.models import User


# ============================================================
# SETTING PRAKTIKUM
# ============================================================

class Setting(models.Model):
    nama_praktikum = models.CharField(
        max_length=200,
        default="Praktikum Perencanaan Tambang",
    )
    periode = models.CharField(
        max_length=100,
        default="2026/2027",
    )
    deskripsi = models.TextField(blank=True)
    dosen_pengampu = models.CharField(max_length=200, blank=True)
    kontak = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_praktikum


# ============================================================
# STAFF / ASISTEN
# ============================================================

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
        verbose_name = "Staff Praktikum"
        verbose_name_plural = "Staff Praktikum"

    def __str__(self):
        return f"{self.nama} - {self.get_jabatan_display()}"


# ============================================================
# KELOMPOK
# ============================================================

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
        null=True,
    )

    progress = models.PositiveIntegerField(default=0)
    catatan = models.TextField(blank=True)

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
        verbose_name = "Kelompok"
        verbose_name_plural = "Kelompok"

    def __str__(self):
        return self.nama

    @property
    def jumlah_anggota(self):
        return self.peserta.filter(aktif=True).count()

    @property
    def jumlah_event(self):
        return self.progress_acara.count()

    @property
    def progress_persen(self):
        return min(max(self.progress or 0, 0), 100)


# ============================================================
# PESERTA
# ============================================================

class Peserta(models.Model):
    JABATAN = [
        ("ketua", "Ketua"),
        ("anggota", "Anggota"),
    ]

    STATUS_KEMAJUAN = [
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
        default="anggota",
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

    status_kemajuan = models.CharField(
        max_length=20,
        choices=STATUS_KEMAJUAN,
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
        verbose_name = "Peserta"
        verbose_name_plural = "Peserta"

    def __str__(self):
        return self.nama

    @property
    def is_ketua(self):
        return self.jabatan == "ketua"

    @property
    def is_aktif(self):
        return self.status_kemajuan == "aktif"


# ============================================================
# ACARA / PERTEMUAN / PRAKTIKUM
# ============================================================

class Acara(models.Model):
    nama = models.CharField(max_length=200)
    sub_acara = models.CharField(max_length=200, blank=True)
    tanggal_mulai = models.DateTimeField()
    tanggal_selesai = models.DateTimeField(null=True, blank=True)
    lokasi = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, default="Belum Dimulai")
    deskripsi = models.TextField(blank=True)
    urutan = models.PositiveIntegerField(default=0)

    penanggung_jawab = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acara_penanggung_jawab",
        limit_choices_to={
            "jabatan": "penanggung_jawab",
            "aktif": True,
        },
    )

    pembawa_acara = models.ManyToManyField(
        Staff,
        blank=True,
        related_name="acara_dibawakan",
        limit_choices_to={
            "jabatan__in": ["koordinator", "asisten"],
            "aktif": True,
        },
    )

    class Meta:
        ordering = ["urutan", "tanggal_mulai"]
        verbose_name = "Acara Praktikum"
        verbose_name_plural = "Acara Praktikum"

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

    judul = models.CharField(max_length=200)

    kategori = models.CharField(
        max_length=30,
        default="modul",
        choices=KAT,
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    file = models.FileField(upload_to="materi/%Y/%m/")
    deskripsi = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Materi"
        verbose_name_plural = "Materi"

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
        related_name="absensi",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="absensi",
    )

    status = models.CharField(max_length=1, choices=STATUS, default="H")
    catatan = models.CharField(max_length=200, blank=True)

    start = models.BooleanField(default=False, verbose_name="START (20%)")
    ishoma_1 = models.BooleanField(default=False, verbose_name="ISHOMA 1 (10%)")
    ishoma_2 = models.BooleanField(default=False, verbose_name="ISHOMA 2 (10%)")
    ishoma_3 = models.BooleanField(default=False, verbose_name="ISHOMA 3 (10%)")
    ls = models.BooleanField(default=False, verbose_name="LS (50%)")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["peserta", "acara"],
                name="unique_peserta_acara",
            )
        ]
        verbose_name = "Absensi"
        verbose_name_plural = "Absensi"

    def __str__(self):
        return f"{self.peserta.nama} - {self.acara.nama}"

    @property
    def nilai_persentase(self):
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


# ============================================================
# PENGUMUMAN
# ============================================================

class Pengumuman(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    aktif = models.BooleanField(default=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat"]
        verbose_name = "Pengumuman"
        verbose_name_plural = "Pengumuman"

    def __str__(self):
        return self.judul


# ============================================================
# TATA TERTIB
# ============================================================

class TataTertib(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    aktif = models.BooleanField(default=True)
    urutan = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["urutan", "id"]
        verbose_name = "Tata Tertib"
        verbose_name_plural = "Tata Tertib"

    def __str__(self):
        return self.judul


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

class TugasPendahuluan(models.Model):
    judul = models.CharField(max_length=200)

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="tugas_pendahuluan",
    )

    soal = models.TextField()

    file = models.FileField(
        upload_to="tugas_pendahuluan/%Y/%m/",
        blank=True,
        null=True,
    )

    deadline = models.DateTimeField(null=True, blank=True)
    aktif = models.BooleanField(default=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat"]
        verbose_name = "Tugas Pendahuluan"
        verbose_name_plural = "Tugas Pendahuluan"

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
        related_name="laporan_mingguan",
    )

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="laporan_mingguan",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="laporan_mingguan",
    )

    judul = models.CharField(max_length=200)
    file = models.FileField(upload_to="laporan_mingguan/%Y/%m/")

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu",
    )

    catatan_admin = models.TextField(blank=True)

    file_revisi = models.FileField(
        upload_to="laporan_revisi/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="File Revisi",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Laporan Mingguan"
        verbose_name_plural = "Laporan Mingguan"

    def __str__(self):
        return self.judul


# ============================================================
# PROGRESS KELOMPOK PER ACARA
# ============================================================

class ProgressAcara(models.Model):
    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="progress_acara",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="progress_kelompok",
    )

    nilai_progress = models.PositiveIntegerField(default=0)
    laporan_acc = models.BooleanField(default=False)
    peta_acc = models.BooleanField(default=False)
    ppt_acc = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kelompok", "acara"],
                name="unique_progress_kelompok_acara",
            )
        ]
        ordering = ["kelompok", "acara"]
        verbose_name = "Progress Acara"
        verbose_name_plural = "Progress Acara"

    def __str__(self):
        return f"{self.kelompok.nama} - {self.acara.nama}"


# ============================================================
# FILE KELOMPOK
# ============================================================

class FileKelompok(models.Model):
    JENIS = [
        ("peta", "Peta / Desain"),
        ("ppt", "PowerPoint"),
        ("lainnya", "Lainnya"),
    ]

    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("acc", "ACC"),
        ("revisi", "Perlu Revisi"),
    ]

    nama_file = models.CharField(max_length=200)

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="file_kelompok",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="file_kelompok",
    )

    jenis = models.CharField(
        max_length=20,
        choices=JENIS,
        default="lainnya",
    )

    file = models.FileField(upload_to="file_kelompok/%Y/%m/")

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu",
    )

    uploaded_by = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_yang_diunggah",
    )

    catatan_admin = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "File Kelompok"
        verbose_name_plural = "File Kelompok"

    def __str__(self):
        return self.nama_file


# ============================================================
# DAILY MOM
# ============================================================

class DailyMOM(models.Model):
    tanggal = models.DateField()

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="daily_mom",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.CASCADE,
        related_name="daily_mom",
    )

    judul = models.CharField(max_length=200)

    dibuat_oleh = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mom_dibuat",
    )

    isi = models.TextField()
    keputusan = models.TextField(blank=True)
    tindak_lanjut = models.TextField(blank=True)
    dibuat = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-tanggal", "-dibuat"]
        verbose_name = "Daily MOM"
        verbose_name_plural = "Daily MOM"

    def __str__(self):
        return self.judul


# ============================================================
# LAPORAN LENGKAP
# ============================================================

class LaporanLengkap(models.Model):
    STATUS = [
        ("menunggu", "Menunggu Pemeriksaan"),
        ("acc", "ACC"),
        ("revisi", "Perlu Revisi"),
    ]

    judul = models.CharField(max_length=200)

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="laporan_lengkap",
    )

    file = models.FileField(
        upload_to="laporan_lengkap/%Y/%m/",
    )

    file_revisi = models.FileField(
        upload_to="laporan_lengkap/revisi/",
        blank=True,
        null=True,
        verbose_name="File Revisi Admin",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu",
    )

    catatan_admin = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Laporan Lengkap"
        verbose_name_plural = "Laporan Lengkap"

    def __str__(self):
        return self.judul


# ============================================================
# FORMAT DOKUMEN DARI ADMIN
# ============================================================

class FormatDokumen(models.Model):
    JENIS = [
        ("pdf", "PDF"),
        ("word", "Microsoft Word"),
        ("excel", "Microsoft Excel"),
        ("ppt", "Microsoft PowerPoint"),
        ("lainnya", "Lainnya"),
    ]

    judul = models.CharField(max_length=200)

    jenis = models.CharField(
        max_length=20,
        choices=JENIS,
        default="lainnya",
    )

    file = models.FileField(upload_to="format_dokumen/%Y/%m/")
    deskripsi = models.TextField(blank=True)
    aktif = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Format Dokumen"
        verbose_name_plural = "Format Dokumen"

    def __str__(self):
        return self.judul


# ============================================================
# KONSULTASI
# ============================================================

class Konsultasi(models.Model):
    STATUS = [
        ("menunggu", "Menunggu Jawaban"),
        ("dijawab", "Sudah Dijawab"),
        ("selesai", "Selesai"),
    ]

    topik = models.CharField(max_length=200)

    kelompok = models.ForeignKey(
        Kelompok,
        on_delete=models.CASCADE,
        related_name="konsultasi",
    )

    peserta = models.ForeignKey(
        Peserta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi",
    )

    tujuan = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi_masuk",
    )

    acara = models.ForeignKey(
        Acara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="konsultasi",
    )

    tanggal_konsultasi = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tanggal Konsultasi",
    )

    waktu_mulai = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Mulai",
    )

    waktu_selesai = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Selesai",
    )

    lokasi = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Lokasi Konsultasi",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="menunggu",
    )

    pertanyaan = models.TextField()
    jawaban = models.TextField(blank=True)
    dibuat = models.DateTimeField(auto_now_add=True)
    dijawab_at = models.DateTimeField(null=True, blank=True)

    # Menyimpan waktu perubahan terakhir.
    # Field ini juga diperlukan untuk menyelaraskan model dengan database.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-dibuat", "-id"]
        verbose_name = "Konsultasi"
        verbose_name_plural = "Konsultasi"

    def __str__(self):
        return self.topik
