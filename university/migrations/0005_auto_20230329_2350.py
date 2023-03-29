# Generated by Django 3.2 on 2023-03-29 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0004_alter_coursetimeplace_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='نام و نام خانوادگی'),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['name'], name='university__name_4b7ef7_idx'),
        ),
    ]
