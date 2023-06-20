# Generated by Django 3.2 on 2023-06-20 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_wallettransaction_applied_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='transaction_type',
            field=models.CharField(choices=[('D', 'کاهش'), ('I', 'افزایش')], max_length=1, verbose_name='نوع تراکنش'),
        ),
    ]
