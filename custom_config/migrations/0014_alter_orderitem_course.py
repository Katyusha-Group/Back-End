# Generated by Django 3.2 on 2023-07-05 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0007_auto_20230621_1532'),
        ('custom_config', '0013_auto_20230620_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='university.course'),
        ),
    ]