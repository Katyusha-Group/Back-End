# Generated by Django 3.2 on 2023-04-03 15:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=255, verbose_name='مدل')),
                ('instance_id', models.IntegerField(verbose_name='شناسه')),
                ('action', models.CharField(choices=[('C', 'ایجاد'), ('U', 'بروزرسانی')], max_length=1, verbose_name='عملیات')),
                ('status', models.CharField(choices=[('U', 'اعمال نشده'), ('C', 'اعمال شده')], max_length=1, verbose_name='وضعیت')),
                ('applied_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'ترکر',
                'verbose_name_plural': 'ترکرها',
                'ordering': ['-applied_at'],
            },
        ),
        migrations.CreateModel(
            name='FieldTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=255, verbose_name='ستون')),
                ('value', models.CharField(max_length=1023, verbose_name='مقدار')),
                ('tracker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='custom_config.modeltracker', verbose_name='ترکر')),
            ],
            options={
                'verbose_name': 'تغییرات ستون',
                'verbose_name_plural': 'تغییر ستون ها',
            },
        ),
    ]