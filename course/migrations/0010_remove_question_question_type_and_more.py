# Generated by Django 5.0.2 on 2024-07-11 11:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_alter_question_question_pattern_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='question_type',
        ),
        migrations.AlterField(
            model_name='question',
            name='question_pattern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Question', to='course.questionpattern'),
        ),
    ]