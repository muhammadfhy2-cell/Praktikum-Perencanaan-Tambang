
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("praktikum", "0006_add_dijawab_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="konsultasi",
            name="tanggal_konsultasi",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Tanggal Konsultasi",
            ),
        ),
        migrations.AddField(
            model_name="konsultasi",
            name="waktu_mulai",
            field=models.TimeField(
                blank=True,
                null=True,
                verbose_name="Waktu Mulai",
            ),
        ),
        migrations.AddField(
            model_name="konsultasi",
            name="waktu_selesai",
            field=models.TimeField(
                blank=True,
                null=True,
                verbose_name="Waktu Selesai",
            ),
        ),
        migrations.AddField(
            model_name="konsultasi",
            name="lokasi",
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name="Lokasi Konsultasi",
            ),
        ),
    ]
