# Generated by Django 3.2 on 2023-10-28 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_remove_profile_telegram_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
