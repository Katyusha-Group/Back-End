import requests
from django.conf import settings


def get_bot_url(csrftoken, token):
    url = f'{settings.WEBSITE_URL}/bot/telegram_link'
    headers = {
        'X-CSRFToken': f'{csrftoken}',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    telegram_response = requests.get(url, headers=headers)
    return telegram_response.json()['link telegram']
