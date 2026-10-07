from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "praktikum",
            "0004_absensi_components_laporan_revisi",
        ),
    ]

    operations = [

        # =====================================================
        # KELOMPOK
        # Field mentor, logo, progress, catatan SUDAH ADA
        # dari migration 0001 dan 0002.
        # =====================================================

        migrations.AddField(
            model_name="kelompok",
            name="akun_login",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="akun_kelompok",
                to="auth.user",
            ),
        ),

        migrations.AddField(
            model_name="kelompok",
            name="aktif",
            field=models.BooleanField(
                default=True,
            ),
        ),

        # =====================================================
        # PESERTA
        # jabatan SUDAH ADA dari migration 0002.
        # =====================================================

        migrations.AddField(
            model_name="peserta",
            name="status_kemajuan",
            field=models.CharField(
                choices=[
                    ("aktif", "AKTIF"),
                    ("gugur", "GUGUR"),
                ],
                default="aktif",
                max_length=20,
            ),
        ),

        migrations.AddField(
            model_name="peserta",
            name="acara_gugur",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="peserta_gugur",
                to="praktikum.acara",
            ),
        ),

        migrations.AddField(
            model_name="peserta",
            name="alasan_gugur",
            field=models.TextField(
                blank=True,
            ),
        ),

        # =====================================================
        # ACARA
        # pembawa_acara SUDAH ADA dari migration 0003.
        # =====================================================

        migrations.AddField(
            model_name="acara",
            name="penanggung_jawab",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="acara_penanggung_jawab",
                to="praktikum.staff",
            ),
        ),

        # =====================================================
        # PROGRESS ACARA
        # =====================================================

        migrations.CreateModel(
            name="ProgressAcara",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nilai_progress",
                    models.PositiveIntegerField(
                        default=0,
                    ),
                ),
                (
                    "laporan_acc",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "peta_acc",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "ppt_acc",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_kelompok",
                        to="praktikum.acara",
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_acara",
                        to="praktikum.kelompok",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=[
                            "kelompok",
                            "acara",
                        ],
                        name="unique_progress_kelompok_acara",
                    ),
                ],
            },
        ),

        # =====================================================
        # FILE KELOMPOK
        # =====================================================

        migrations.CreateModel(
            name="FileKelompok",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nama_file",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "jenis",
                    models.CharField(
                        choices=[
                            ("peta", "Peta / Desain"),
                            ("ppt", "PowerPoint"),
                            ("lainnya", "Lainnya"),
                        ],
                        default="lainnya",
                        max_length=20,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="file_kelompok/%Y/%m/",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("menunggu", "Menunggu Pemeriksaan"),
                            ("acc", "ACC"),
                            ("revisi", "Perlu Revisi"),
                        ],
                        default="menunggu",
                        max_length=20,
                    ),
                ),
                (
                    "catatan_admin",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="file_kelompok",
                        to="praktikum.acara",
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="file_kelompok",
                        to="praktikum.kelompok",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="file_yang_diunggah",
                        to="praktikum.peserta",
                    ),
                ),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),

        # =====================================================
        # DAILY MOM
        # =====================================================

        migrations.CreateModel(
            name="DailyMOM",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tanggal",
                    models.DateField(),
                ),
                (
                    "judul",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "isi",
                    models.TextField(),
                ),
                (
                    "keputusan",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "tindak_lanjut",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "dibuat",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_mom",
                        to="praktikum.acara",
                    ),
                ),
                (
                    "dibuat_oleh",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mom_dibuat",
                        to="praktikum.peserta",
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_mom",
                        to="praktikum.kelompok",
                    ),
                ),
            ],
            options={
                "ordering": ["-tanggal", "-dibuat"],
            },
        ),

        # =====================================================
        # LAPORAN LENGKAP
        # =====================================================

        migrations.CreateModel(
            name="LaporanLengkap",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "judul",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="laporan_lengkap/%Y/%m/",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("menunggu", "Menunggu Pemeriksaan"),
                            ("acc", "ACC"),
                            ("revisi", "Perlu Revisi"),
                        ],
                        default="menunggu",
                        max_length=20,
                    ),
                ),
                (
                    "catatan_admin",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="laporan_lengkap",
                        to="praktikum.kelompok",
                    ),
                ),
            ],
        ),

        # =====================================================
        # FORMAT DOKUMEN
        # =====================================================

        migrations.CreateModel(
            name="FormatDokumen",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "judul",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "jenis",
                    models.CharField(
                        choices=[
                            ("pdf", "PDF"),
                            ("word", "Microsoft Word"),
                            ("excel", "Microsoft Excel"),
                            ("ppt", "Microsoft PowerPoint"),
                            ("lainnya", "Lainnya"),
                        ],
                        default="lainnya",
                        max_length=20,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="format_dokumen/%Y/%m/",
                    ),
                ),
                (
                    "deskripsi",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "aktif",
                    models.BooleanField(
                        default=True,
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
            ],
        ),

        # =====================================================
        # KONSULTASI
        # =====================================================

        migrations.CreateModel(
            name="Konsultasi",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "topik",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "pertanyaan",
                    models.TextField(),
                ),
                (
                    "jawaban",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("menunggu", "Menunggu Jawaban"),
                            ("dijawab", "Sudah Dijawab"),
                            ("selesai", "Selesai"),
                        ],
                        default="menunggu",
                        max_length=20,
                    ),
                ),
                (
                    "dibuat",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="konsultasi",
                        to="praktikum.acara",
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="konsultasi",
                        to="praktikum.kelompok",
                    ),
                ),
                (
                    "peserta",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="konsultasi",
                        to="praktikum.peserta",
                    ),
                ),
                (
                    "tujuan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="konsultasi_masuk",
                        to="praktikum.staff",
                    ),
                ),
            ],
        ),
    ]
