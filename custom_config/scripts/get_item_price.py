from custom_config.models import CartItem


EMAIL_PRICE = 1000
SMS_PRICE = 2000
TELEGRAM_PRICE = 1000


def get_item_price(cart_item: CartItem):
    total_price = 0
    if cart_item.contain_email:
        total_price += EMAIL_PRICE
    if cart_item.contain_sms:
        total_price += SMS_PRICE
    if cart_item.contain_telegram:
        total_price += TELEGRAM_PRICE
    return total_price
