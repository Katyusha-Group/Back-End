# import asyncio
#
import asyncio

import requests
from telegram import Bot

async def send_telegram_message(token, user_id, message):
    bot = Bot(token=token)
    user_id = '968800834'
    await bot.send_message(chat_id=user_id, text=message)


def send_telegram_notification(email = None, changes= None):
    params = {'email': email}
    response = requests.get(f'https://katyushaiust.ir/bot/get_user_id/{email}').json()


    token = '6182994088:AAFZbZ9_fMeWebvb4x9_vb3k4q74RYWAuOM'

    # if user is None:
    #     raise ValueError('user_id is required')
    # if changes is None:
    #     raise ValueError('changes is required')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message(token, 968800834, changes))
    loop.close()

if __name__ == '__main__':
    send_telegram_notification( email='ali.dada.28880@gmail.com', changes= 'بیبی')
#


# class TelegramNotification:
#     token_cons = '6182994088:AAFZbZ9_fMeWebvb4x9_vb3k4q74RYWAuOM'
#
#     def __init__(self):
#         self.token = self.token_cons
#
#     async def send_telegram_message(self, user_id, message):
#         bot = Bot(token=self.token)
#         await bot.send_message(chat_id=user_id, text=message)
#
#     def send_telegram_notification(self, email = None, changes= None):
#
#         response = requests.get(f'http://127.0.0.1:8000/bot/get_user_id/{email}').json()
#
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(self.send_telegram_message(self.token, response['user_id'], changes))
#         loop.close()
#
#

