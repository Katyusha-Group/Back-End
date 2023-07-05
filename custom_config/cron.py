import time
from datetime import timedelta

from django.utils import timezone

from custom_config.models import Order, Cart
from custom_config.scripts.notification_requirements import send_notification_for_courses


def delete_pending_orders():
    orders = Order.objects.filter(status='P')
    for order in orders:
        if order.created_at + timedelta(hours=1) < timezone.now():
            order.delete()


def delete_failed_orders():
    orders = Order.objects.filter(status='F')
    for order in orders:
        if order.created_at + timedelta(days=7) < timezone.now():
            order.delete()


def delete_expired_orders():
    orders = Order.objects.filter()
    for order in orders:
        if order.created_at + timedelta(days=90) < timezone.now():
            order.delete()


def delete_expired_carts():
    carts = Cart.objects.filter()
    for cart in carts:
        if cart.created_at + timedelta(days=1) < timezone.now():
            cart.delete()


def send_notifications():
    pre = time.time()

    send_notification_for_courses()

    print('Completed sending notification in', time.time() - pre)
