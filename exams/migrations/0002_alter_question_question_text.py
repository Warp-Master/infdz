# Generated by Django 4.1.7 on 2023-02-16 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(blank=True),
        ),
    ]
