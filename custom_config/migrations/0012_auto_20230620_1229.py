# Generated by Django 3.2 on 2023-06-20 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_config', '0011_ordertransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='ordertransaction',
            name='amount',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
    ]