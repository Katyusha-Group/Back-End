# Generated by Django 3.2 on 2023-04-19 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_verification_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='code',
            field=models.CharField(max_length=4),
        ),
    ]
