# Generated by Django 4.2.7 on 2024-02-28 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_course_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
