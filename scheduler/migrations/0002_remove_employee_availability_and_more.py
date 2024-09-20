# Generated by Django 5.1.1 on 2024-09-20 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduler", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employee",
            name="availability",
        ),
        migrations.RemoveField(
            model_name="shift",
            name="shift_block",
        ),
        migrations.RemoveField(
            model_name="employee",
            name="preferred_shifts",
        ),
        migrations.AddField(
            model_name="shift",
            name="shift_time",
            field=models.CharField(
                choices=[
                    ("MORNING", "9AM to 6PM"),
                    ("AFTERNOON", "12PM to 9PM"),
                    ("EVENING", "3PM to 12AM"),
                    ("NIGHT", "6PM to 3AM"),
                    ("LATE_NIGHT", "9PM to 6AM"),
                    ("EARLY_MORNING", "12AM to 9AM"),
                ],
                default="MORNING",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="availability",
            field=models.JSONField(default=dict),
        ),
        migrations.DeleteModel(
            name="ShiftBlock",
        ),
        migrations.AddField(
            model_name="employee",
            name="preferred_shifts",
            field=models.JSONField(default=dict),
        ),
    ]
