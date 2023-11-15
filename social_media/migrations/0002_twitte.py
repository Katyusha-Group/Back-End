# Generated by Django 3.2 on 2023-11-10 10:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twitte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=280, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(280)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='social_media.twitte')),
                ('likes', models.ManyToManyField(blank=True, related_name='liked_tweets', to='social_media.Profile')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='social_media.twitte')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.profile')),
            ],
        ),
    ]