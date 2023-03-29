# Generated by Django 3.2 on 2023-03-29 17:45

from django.db import migrations, models
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examtimeplace',
            name='place',
        ),
        migrations.AddField(
            model_name='course',
            name='registration_limit',
            field=models.CharField(default='هیچ', max_length=255, verbose_name='محدودیت اخذ'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='examtimeplace',
            name='date',
            field=django_jalali.db.models.jDateField(help_text='سال را به فرم yyyy-mm-dd وارد کنید.', verbose_name='تاریخ امتحان'),
        ),
    ]
