# Generated by Django 5.0.2 on 2024-06-15 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0020_userattempt_is_correct'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionpattern',
            name='pattern_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
