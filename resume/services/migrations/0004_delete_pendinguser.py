# Generated by Django 4.2.20 on 2025-05-30 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PendingUser',
        ),
    ]
