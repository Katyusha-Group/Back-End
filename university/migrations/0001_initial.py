# Generated by Django 3.2 on 2023-04-12 07:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_jalali.db.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCourse',
            fields=[
                ('course_number', models.IntegerField(db_index=True, primary_key=True, serialize=False, verbose_name='شماره درس')),
                ('name', models.CharField(max_length=255, verbose_name='نام درس')),
                ('total_unit', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='کل واحد')),
                ('practical_unit', models.PositiveSmallIntegerField(verbose_name='واحد های عملی')),
                ('emergency_deletion', models.BooleanField(verbose_name='حذف اضطراری')),
            ],
            options={
                'verbose_name': 'درس پایه',
                'verbose_name_plural': 'دروس پایه',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_gp', models.CharField(max_length=2, verbose_name='گروه درس')),
                ('capacity', models.PositiveSmallIntegerField(verbose_name='ظرفیت')),
                ('registered_count', models.PositiveSmallIntegerField(verbose_name='تعداد ثبت نام شده ها')),
                ('waiting_count', models.PositiveSmallIntegerField(verbose_name='تعداد افراد حاضر در لیست انتظار')),
                ('guest_able', models.BooleanField(verbose_name='قابل اخذ توسط مهمان')),
                ('registration_limit', models.CharField(max_length=4000, verbose_name='محدودیت اخذ')),
                ('description', models.CharField(max_length=400, verbose_name='توضیحات')),
                ('sex', models.CharField(choices=[('M', 'مرد'), ('F', 'زن'), ('B', 'مختلط')], max_length=1, verbose_name='جنسیت')),
                ('presentation_type', models.CharField(choices=[('N', 'عادی'), ('E', 'الکترونیکی'), ('B', 'عادی-نوری'), ('A', 'آرشیو')], max_length=1, verbose_name='نحوه ارائه درس')),
            ],
            options={
                'verbose_name': 'درس',
                'verbose_name_plural': 'درس ها',
            },
        ),
        migrations.CreateModel(
            name='CourseStudyingGP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gp_id', models.IntegerField(verbose_name='کد گروه آموزشی')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='نام گروه آموزشی')),
            ],
            options={
                'verbose_name': 'گروه آموزشی',
                'verbose_name_plural': 'گروه های آموزشی',
            },
        ),
        migrations.CreateModel(
            name='CourseTimePlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(verbose_name='زمان شروع')),
                ('end_time', models.TimeField(verbose_name='زمان پایان')),
                ('day', models.IntegerField(choices=[(1, 'شنبه'), (2, 'یک شنبه'), (3, 'دوشنبه'), (4, 'سه شنبه'), (5, 'چهارشنبه')], verbose_name='روز جلسه')),
                ('place', models.CharField(max_length=255, verbose_name='مکان برگزاری جلسه')),
            ],
            options={
                'verbose_name': 'زمان و مکان کلاس',
                'verbose_name_plural': 'زمان و مکان کلاس ها',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('department_number', models.SmallIntegerField(primary_key=True, serialize=False, verbose_name='کد دانشکده')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='نام دانشکده')),
            ],
            options={
                'verbose_name': 'دانشکده',
                'verbose_name_plural': 'دانشکده ها',
            },
        ),
        migrations.CreateModel(
            name='ExamTimePlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', django_jalali.db.models.jDateField(help_text='سال را به فرم yyyy-mm-dd وارد کنید.', verbose_name='تاریخ امتحان')),
                ('start_time', models.TimeField(verbose_name='زمان شروع')),
                ('end_time', models.TimeField(verbose_name='زمان پایان')),
            ],
            options={
                'verbose_name': 'تاریخ امتحان',
                'verbose_name_plural': 'تاریخ امتحانات',
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('year', models.IntegerField(primary_key=True, serialize=False, verbose_name='ترم ارائه درس')),
            ],
            options={
                'verbose_name': 'ترم',
                'verbose_name_plural': 'ترم ها',
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='نام و نام خانوادگی')),
            ],
            options={
                'verbose_name': 'استاد',
                'verbose_name_plural': 'اساتید',
            },
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['name'], name='university__name_4b7ef7_idx'),
        ),
        migrations.AddField(
            model_name='examtimeplace',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.course', verbose_name='درس'),
        ),
        migrations.AddField(
            model_name='coursetimeplace',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.course', verbose_name='درس'),
        ),
        migrations.AddField(
            model_name='course',
            name='base_course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='university.basecourse', verbose_name='درس پایه'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='university.teacher', verbose_name='استاد درس'),
        ),
        migrations.AddField(
            model_name='basecourse',
            name='course_studying_gp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='university.coursestudyinggp', verbose_name='دوره آموزشی درس'),
        ),
        migrations.AddField(
            model_name='basecourse',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='university.department', verbose_name='دانشکده درس'),
        ),
        migrations.AddField(
            model_name='basecourse',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='university.semester', verbose_name='ترم ارائه'),
        ),
    ]
