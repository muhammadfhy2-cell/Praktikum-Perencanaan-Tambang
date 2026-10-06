from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("praktikum", "0001_intial"),
    ]

    operations = [
        # Kelompok: mentor lama berupa CharField dihapus
        migrations.RemoveField(
            model_name="kelompok",
            name="mentor",
        ),

        # Kelompok: mentor sekarang dapat lebih dari satu Staff
        migrations.AddField(
            model_name="kelompok",
            name="mentor",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={
                    "jabatan__in": [
                        "penanggung_jawab",
                        "koordinator",
                        "asisten",
                    ],
                    "aktif": True,
                },
                related_name="kelompok_binaan",
                to="praktikum.staff",
            ),
        ),

        # Logo kelompok
        migrations.AddField(
            model_name="kelompok",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="logo_kelompok/",
            ),
        ),

        # Staff: tambahkan Penanggung Jawab dan field administrasi
        migrations.AlterField(
            model_name="staff",
            name="jabatan",
            field=models.CharField(
                choices=[
                    (
                        "penanggung_jawab",
                        "Penanggung Jawab Praktikum",
                    ),
                    (
                        "koordinator",
                        "Koordinator Asisten Dosen",
                    ),
                    (
                        "asisten",
                        "Asisten Dosen",
                    ),
                ],
                max_length=30,
            ),
        ),

        migrations.AddField(
            model_name="staff",
            name="urutan",
            field=models.PositiveIntegerField(default=0),
        ),

        migrations.AddField(
            model_name="staff",
            name="aktif",
            field=models.BooleanField(default=True),
        ),

        # Setting: field koordinator tidak lagi digunakan
        migrations.RemoveField(
            model_name="setting",
            name="koordinator",
        ),

        # Peserta: posisi dalam kelompok
        migrations.AddField(
            model_name="peserta",
            name="jabatan",
            field=models.CharField(
                choices=[
                    ("ketua", "Ketua"),
                    ("anggota", "Anggota"),
                ],
                default="anggota",
                max_length=20,
            ),
        ),

        # Absensi: unique_together lama diganti UniqueConstraint
        migrations.AlterUniqueTogether(
            name="absensi",
            unique_together=set(),
        ),

        migrations.AddConstraint(
            model_name="absensi",
            constraint=models.UniqueConstraint(
                fields=("peserta", "acara"),
                name="unique_peserta_acara",
            ),
        ),
    ]
