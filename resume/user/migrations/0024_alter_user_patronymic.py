# Generated by Django 4.2.20 on 2025-06-05 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='patronymic',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Отчество'),
        ),
    ]
