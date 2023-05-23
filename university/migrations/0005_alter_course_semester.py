# Generated by Django 3.2 on 2023-05-22 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0004_auto_20230521_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='university.semester', verbose_name='ترم ارائه'),
        ),
    ]