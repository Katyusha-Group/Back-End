# Generated by Django 3.2 on 2023-07-05 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botapp', '0006_user_telegram_telegram_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_telegram',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
