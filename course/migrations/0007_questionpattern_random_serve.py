# Generated by Django 5.0.2 on 2024-07-11 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_rename_duration_questionpattern_exam_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionpattern',
            name='random_serve',
            field=models.BooleanField(default=False),
        ),
    ]