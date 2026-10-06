from django.db import models


class Setting(models.Model):
    nama_praktikum = models.CharField(max_length=200, default="Praktikum Perencanaan Tambang")
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
    mentor = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kelompok_binaan",
        limit_choices_to={"jabatan": "asisten", "aktif": True},
    )
    progress = models.PositiveIntegerField(default=0)
    catatan = models.TextField(blank=True)

    def __str__(self):
        return self.nama


class Peserta(models.Model):
    nama = models.CharField(max_length=200)
    nim = models.CharField(max_length=50, blank=True)
    kelompok = models.ForeignKey(
        Kelompok, on_delete=models.SET_NULL, null=True, blank=True, related_name="peserta"
    )
    email = models.EmailField(blank=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.nama


class Acara(models.Model):
    nama = models.CharField(max_length=200)
    sub_acara = models.CharField(max_length=200, blank=True)
    tanggal_mulai = models.DateTimeField()
    tanggal_selesai = models.DateTimeField(null=True, blank=True)
    lokasi = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, default="Belum Dimulai")
    deskripsi = models.TextField(blank=True)
    urutan = models.PositiveIntegerField(default=0)

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
    kategori = models.CharField(max_length=30, choices=KAT, default="modul")
    acara = models.ForeignKey(Acara, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="materi/%Y/%m/")
    deskripsi = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul


class Absensi(models.Model):
    STATUS = [("H", "Hadir"), ("I", "Izin"), ("S", "Sakit"), ("A", "Alfa")]
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE, related_name="absensi")
    acara = models.ForeignKey(Acara, on_delete=models.CASCADE, related_name="absensi")
    status = models.CharField(max_length=1, choices=STATUS, default="H")
    catatan = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["peserta", "acara"], name="unique_peserta_acara")]


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
