import asyncio
from telegram import Bot

async def send_telegram_message(token, user_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=user_id, text=message)


def send_telegram_notification(user_id = None, changes= None):
    token = '6182994088:AAFwEqBN16Yvudx85OkkQVpkiNwHmmO3GtY'

    if user_id is None:
        raise ValueError('user_id is required')
    if changes is None:
        raise ValueError('changes is required')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message(token, user_id, changes))

if __name__ == '__main__':
    send_telegram_notification()




