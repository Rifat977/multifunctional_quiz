# Generated by Django 5.0.2 on 2024-07-11 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_questionpattern_points'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionpattern',
            old_name='duration',
            new_name='exam_duration',
        ),
    ]
