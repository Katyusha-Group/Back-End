# Generated by Django 3.2 on 2023-07-06 21:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_config', '0016_auto_20230707_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='is_sent_to_telegram',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='order_items',
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='accounts.user'),
            preserve_default=False,
        ),
    ]
