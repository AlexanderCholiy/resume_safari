# Generated by Django 4.2.20 on 2025-05-23 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_alter_education_options_alter_experience_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='responsibilities',
            field=models.TextField(blank=True, help_text='В качестве разделителя используйте "новую строку"', null=True, verbose_name='Обязанности'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
    ]
