from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("praktikum", "0002_update_models"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [

        migrations.AddField(
            model_name="peserta",
            name="akun",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="profil_peserta",
                to="auth.user",
            ),
        ),

        migrations.AddField(
            model_name="acara",
            name="pembawa_acara",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={
                    "jabatan": "asisten",
                    "aktif": True,
                },
                related_name="acara_dibawakan",
                to="praktikum.staff",
            ),
        ),

        migrations.CreateModel(
            name="TugasPendahuluan",
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
                    models.CharField(max_length=200),
                ),
                (
                    "soal",
                    models.TextField(),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="tugas_pendahuluan/%Y/%m/",
                    ),
                ),
                (
                    "deadline",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "aktif",
                    models.BooleanField(default=True),
                ),
                (
                    "dibuat",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tugas_pendahuluan",
                        to="praktikum.acara",
                    ),
                ),
            ],
            options={
                "ordering": ["-dibuat"],
            },
        ),

        migrations.CreateModel(
            name="LaporanMingguan",
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
                    models.CharField(max_length=200),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="laporan_mingguan/%Y/%m/",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            (
                                "menunggu",
                                "Menunggu Pemeriksaan",
                            ),
                            (
                                "acc",
                                "Disetujui / ACC",
                            ),
                            (
                                "revisi",
                                "Perlu Revisi",
                            ),
                        ],
                        default="menunggu",
                        max_length=20,
                    ),
                ),
                (
                    "catatan_admin",
                    models.TextField(blank=True),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "acara",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="laporan_mingguan",
                        to="praktikum.acara",
                    ),
                ),
                (
                    "kelompok",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="laporan_mingguan",
                        to="praktikum.kelompok",
                    ),
                ),
                (
                    "peserta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="laporan_mingguan",
                        to="praktikum.peserta",
                    ),
                ),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
