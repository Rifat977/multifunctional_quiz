# Generated by Django 5.0.2 on 2024-07-11 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_userattempt_useranswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionpattern',
            name='points',
            field=models.FloatField(default=1.0, verbose_name='Points for each Question'),
        ),
    ]