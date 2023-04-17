# Generated by Django 3.2 on 2023-04-12 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.CharField(choices=[('Computer Engineering', 'Computer Engineering'), ('Electrical Engineering', 'Electrical Engineering'), ('Mechanical Engineering', 'Mechanical Engineering'), ('Civil Engineering', 'Civil Engineering'), ('Industrial Engineering', 'Industrial Engineering'), ('Chemical Engineering', 'Chemical Engineering'), ('Material Engineering', 'Material Engineering'), ('Railway Engineering', 'Railway Engineering'), ('Computer Science', 'Computer Science'), ('Mathematics', 'Mathematics'), ('Physics', 'Physics')], max_length=50),
        ),
    ]