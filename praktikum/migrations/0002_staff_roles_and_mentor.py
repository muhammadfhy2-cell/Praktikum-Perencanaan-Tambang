from django.db import migrations, models
import django.db.models.deletion


def copy_old_mentors(apps, schema_editor):
    # The starter project stored mentor as free text. Preserve that data when possible.
    Staff = apps.get_model("praktikum", "Staff")
    Kelompok = apps.get_model("praktikum", "Kelompok")
    for kelompok in Kelompok.objects.exclude(mentor="").iterator():
        staff, _ = Staff.objects.get_or_create(
            nama=kelompok.mentor,
            defaults={"jabatan": "asisten", "aktif": True},
        )
        kelompok.mentor_new_id = staff.pk
        kelompok.save(update_fields=["mentor_new"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("praktikum", "0001_initial")]

    operations = [
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
        migrations.AddField(
            model_name="kelompok",
            name="mentor_new",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="kelompok_binaan_new",
                to="praktikum.staff",
            ),
        ),
        migrations.RunPython(copy_old_mentors, noop),
        migrations.RemoveField(model_name="kelompok", name="mentor"),
        migrations.RenameField(model_name="kelompok", old_name="mentor_new", new_name="mentor"),
        migrations.AlterField(
            model_name="staff",
            name="jabatan",
            field=models.CharField(
                choices=[
                    ("penanggung_jawab", "Penanggung Jawab Praktikum"),
                    ("koordinator", "Koordinator Asisten Dosen"),
                    ("asisten", "Asisten Dosen"),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="kelompok",
            name="mentor",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"jabatan": "asisten", "aktif": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="kelompok_binaan",
                to="praktikum.staff",
            ),
        ),
    ]
