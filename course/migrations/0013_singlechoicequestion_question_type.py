# Generated by Django 5.0.2 on 2024-07-11 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0012_remove_question_question_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlechoicequestion',
            name='question_type',
            field=models.CharField(default='single_choice', max_length=255),
        ),
    ]
