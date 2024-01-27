# Generated by Django 3.2 on 2024-01-27 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_config', '0027_alter_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacherreview',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='teacherreview',
            name='user',
        ),
        migrations.RemoveField(
            model_name='teachervote',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='teachervote',
            name='user',
        ),
        migrations.RemoveField(
            model_name='webnotification',
            name='tracker',
        ),
        migrations.RemoveField(
            model_name='webnotification',
            name='user',
        ),
        migrations.DeleteModel(
            name='ReviewVote',
        ),
        migrations.DeleteModel(
            name='TeacherReview',
        ),
        migrations.DeleteModel(
            name='TeacherVote',
        ),
        migrations.DeleteModel(
            name='WebNotification',
        ),
    ]
