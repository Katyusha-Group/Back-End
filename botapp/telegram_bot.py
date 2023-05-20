#!/usr/bin/env python
import json
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, PicklePersistence

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance
bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN")

import logging

import jwt
import requests
import os
from django import setup
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


from django.conf import settings

# Configure the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
setup()
# Import the models
from botapp.models import User_telegram


from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


TOTAL_VOTER_COUNT = 3
DJANGO_SETTINGS_MODULE = 'core.settings'

from asgiref.sync import sync_to_async


def is_user_in_databese(hashed_number, telegram_chat_id):
    try:
        user_telegram = User_telegram.objects.get(hashed_number=hashed_number)
        user_telegram.telegram_chat_id = telegram_chat_id
        logger.info("changed telegram chat_id")
        # Convert the synchronous save() operation to asynchronous using sync_to_async
        user_telegram.save()
        logger.info("saved")
    except User_telegram.DoesNotExist:
        user_telegram = None

    return user_telegram


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    hashed_number = context.args[0]
    logging.info(context.args)
    create_func = sync_to_async(is_user_in_databese)

    if context.args:
        logging.info("created user")
        logger.info(update.message.chat.id)

        user_telegram = await create_func(hashed_number, str(update.message.chat.id))

        if user_telegram:
            await update.message.reply_text(
                f"Hello {update.message.chat.first_name}, welcome to the Katyusha bot.\n"
                "Please select /my_information to get your information, /quiz to get a Quiz, or /preview"
                " to generate a preview for your poll."
            )
        else:
            await update.message.reply_text(
                f"Hello {update.message.chat.first_name}, welcome to the Katyusha bot.\n"
                "You should first log in to the website and then access the Telegram bot through the link provided by the website in order to utilize the bot's features.\n"
                "http://katyushaiust.ir/accounts/login/"
            )

def get_user_id(telegram_chat_id):
    try:
        user_telegram = User_telegram.objects.get(telegram_chat_id=telegram_chat_id)
        user_id = user_telegram.user_id
    except User_telegram.DoesNotExist:
        user_id = None

    return user_id
async def my_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends information about the user and its chat."""
    user_id = sync_to_async(get_user_id)
    user_id_number = await user_id(str(update.message.chat.id))
    # get data of user
    data_user = requests.get(f"http://127.0.0.1:8000/bot/get_song/{user_id_number}/").json()
    logger.info(data_user)
    await update.message.reply_text(
        text=f"User Name: {data_user['inf']['username']}\nDeparment Name: {data_user['inf']['department_name']}"
    )

async def get_course_in_my_calender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends information about the user and its chat."""
    user_id = sync_to_async(get_user_id)
    user_id_number = await user_id(str(update.message.chat.id))
    # get data of user
    data_user = requests.get(f"http://127.0.0.1:8000/bot/get_courses_on_calendar/{user_id_number}/").json()
    logger.info(data_user)
    formatted_data = json.dumps(data_user, indent=4, ensure_ascii=False)

    await update.message.reply_text(formatted_data)



def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("6182994088:AAFwEqBN16Yvudx85OkkQVpkiNwHmmO3GtY")
        .arbitrary_callback_data(True)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("my_information", my_information))
    application.add_handler(CommandHandler("get_course_in_my_calender", get_course_in_my_calender))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()