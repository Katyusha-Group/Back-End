# Generated by Django 3.2 on 2023-11-24 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_config', '0022_auto_20231115_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='accounts.user'),
            preserve_default=False,
        ),
    ]
