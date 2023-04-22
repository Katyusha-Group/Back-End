# Generated by Django 3.2 on 2023-04-22 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0006_merge_20230417_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='email_address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ایمیل'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='lms_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='شماره استاد در سامانه LMS'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='teacher_image',
            field=models.ImageField(blank=True, default='images/teachers_image/default.png', upload_to='images/teachers_image/', verbose_name='تصویر استاد'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='teacher_image_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='آدرس تصویر استاد'),
        ),
    ]