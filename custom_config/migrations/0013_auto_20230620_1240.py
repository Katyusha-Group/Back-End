# Generated by Django 3.2 on 2023-06-20 09:10

from django.db import migrations, models
import utils.transactions.transaction_functions


class Migration(migrations.Migration):

    dependencies = [
        ('custom_config', '0012_auto_20230620_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordertransaction',
            name='order',
        ),
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=utils.transactions.transaction_functions.create_ref_code, max_length=20, unique=True),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['ref_code'], name='custom_conf_ref_cod_fe62e4_idx'),
        ),
        migrations.DeleteModel(
            name='OrderTransaction',
        ),
    ]
