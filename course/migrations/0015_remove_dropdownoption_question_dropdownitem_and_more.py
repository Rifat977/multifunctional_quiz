# Generated by Django 5.0.2 on 2024-07-29 20:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0014_remove_singlechoicequestion_question_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dropdownoption',
            name='question',
        ),
        migrations.CreateModel(
            name='DropDownItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dropdown_items', to='course.dropdownquestion')),
            ],
        ),
        migrations.AddField(
            model_name='dropdownoption',
            name='dropdown_item',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='course.dropdownitem'),
            preserve_default=False,
        ),
    ]