from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "praktikum",
            "0005_group_system",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="konsultasi",
            name="dijawab_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
    ]
