# Generated by Django 5.0.2 on 2024-03-08 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0016_questionpattern_is_sequenced'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionpattern',
            name='total_questions_served',
            field=models.PositiveIntegerField(default=0, verbose_name='Total Questions Served'),
        ),
    ]
