# Generated by Django 5.0.2 on 2024-03-03 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_customuser_otp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='point',
            field=models.FloatField(default=0.0),
        ),
    ]
