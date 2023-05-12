# Generated by Django 3.2 on 2023-05-12 11:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0002_course_students'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_config', '0002_cart_cartitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('payment_status', models.CharField(choices=[('P', 'در حال پردازش'), ('C', 'موفق'), ('F', 'ناموفق')], default='P', max_length=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'سفارش',
                'verbose_name_plural': 'آیتم های سفارش',
            },
        ),
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name': 'سبد خرید', 'verbose_name_plural': 'سبدهای خرید'},
        ),
        migrations.AlterModelOptions(
            name='cartitem',
            options={'verbose_name': 'آیتم سبد خرید', 'verbose_name_plural': 'آیتم های سبد خرید'},
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='custom_config.cart'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contain_telegram', models.BooleanField(default=False)),
                ('contain_sms', models.BooleanField(default=False)),
                ('contain_email', models.BooleanField(default=False)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='university.course')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='custom_config.order')),
            ],
            options={
                'verbose_name': 'سفارش',
                'verbose_name_plural': 'آیتم های سفارش',
            },
        ),
    ]