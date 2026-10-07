from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("praktikum", "0003_praktikum_features"),
    ]

    operations = [

        migrations.AddField(
            model_name="absensi",
            name="start",
            field=models.BooleanField(
                default=False,
                verbose_name="START (20%)"
            ),
        ),

        migrations.AddField(
            model_name="absensi",
            name="ishoma_1",
            field=models.BooleanField(
                default=False,
                verbose_name="ISHOMA 1 (10%)"
            ),
        ),

        migrations.AddField(
            model_name="absensi",
            name="ishoma_2",
            field=models.BooleanField(
                default=False,
                verbose_name="ISHOMA 2 (10%)"
            ),
        ),

        migrations.AddField(
            model_name="absensi",
            name="ishoma_3",
            field=models.BooleanField(
                default=False,
                verbose_name="ISHOMA 3 (10%)"
            ),
        ),

        migrations.AddField(
            model_name="absensi",
            name="ls",
            field=models.BooleanField(
                default=False,
                verbose_name="LS (50%)"
            ),
        ),

        migrations.AddField(
            model_name="laporanmingguan",
            name="file_revisi",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="laporan_revisi/%Y/%m/",
                verbose_name="File Revisi"
            ),
        ),
    ]
