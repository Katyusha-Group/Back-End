# Generated by Django 3.2 on 2023-07-06 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_user_last_verification_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='telegram_id',
        ),
    ]