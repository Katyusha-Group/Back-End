import time
from datetime import timedelta

from django.utils import timezone

from custom_config.models import Order, Cart
from custom_config.scripts.golestan import watch_golestan
from custom_config.scripts.notification import send_notification_for_courses


def delete_pending_orders():
    orders = Order.objects.filter(status='P')
    for order in orders:
        if order.created_at + timedelta(hours=6) < timezone.now():
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


def watch_and_send_notifications():
    pre = time.time()

    # watch_golestan()
    # print('Completed watching golestan in', time.time() - pre)

    post = time.time()
    send_notification_for_courses()

    print('Completed sending notification in', time.time() - post)

    print('Total time:', time.time() - pre)

