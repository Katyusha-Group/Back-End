# Generated by Django 3.2 on 2023-05-22 11:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_config', '0002_reviewvote_teacherreview_teachervote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewvote',
            name='vote',
            field=models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(1)]),
        ),
    ]