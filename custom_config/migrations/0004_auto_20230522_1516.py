# Generated by Django 3.2 on 2023-05-22 11:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0005_alter_course_semester'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_config', '0003_alter_reviewvote_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewvote',
            name='review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='custom_config.teacherreview'),
        ),
        migrations.AlterField(
            model_name='reviewvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_votes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='teacherreview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='teachervote',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_votes', to='university.teacher'),
        ),
        migrations.AlterField(
            model_name='teachervote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_votes', to=settings.AUTH_USER_MODEL),
        ),
    ]
