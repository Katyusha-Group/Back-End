# Generated by Django 3.2 on 2023-11-26 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0002_twitte'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('L', 'لایک'), ('R', 'پاسخ'), ('F', 'دنبال کردن'), ('M', 'منشن'), ('P', 'پست جدید')], max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='triggered_notifications', to='social_media.profile')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='social_media.profile')),
                ('tweet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.twitte')),
            ],
        ),
    ]
