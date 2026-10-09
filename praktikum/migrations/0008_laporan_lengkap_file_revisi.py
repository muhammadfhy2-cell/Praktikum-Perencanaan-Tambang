
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("praktikum", "0007_jadwal_konsultasi"),
    ]

    operations = [
        migrations.AddField(
            model_name="laporanlengkap",
            name="file_revisi",
            field=models.FileField(
                upload_to="laporan_lengkap/revisi/",
                blank=True,
                null=True,
                verbose_name="File Revisi Admin",
            ),
        ),
    ]
