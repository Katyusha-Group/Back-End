# Generated by Django 3.2 on 2023-07-06 10:21

from django.db import migrations
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_config', '0014_alter_orderitem_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='placed_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
    ]
