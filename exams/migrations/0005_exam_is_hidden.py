# Generated by Django 4.1.7 on 2023-08-29 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0004_question_atomic_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
