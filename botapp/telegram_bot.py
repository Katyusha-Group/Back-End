#!/usr/bin/env python
import asyncio
import json
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance

import logging

import requests
import os
from django import setup



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




def is_user_in_databese(hashed_number=None, telegram_chat_id=None ,name= None):
    if hashed_number is None:
        logger.info("hashed_number is none, user didnt enter with url")
        try:
            user_telegram = User_telegram.objects.get(telegram_chat_id=telegram_chat_id)
            logger.info(user_telegram)
            return user_telegram, ""
        except User_telegram.DoesNotExist:
            logger.info("user doesnt exist, User never enter with url.")
            return (None, "The user doesn't exist. You never entered with a URL.")

    elif hashed_number is not None:
        logger.info("hashed_number is not none, user entered with url")
        try:
            user_telegram = User_telegram.objects.get(hashed_number=hashed_number)
        except User_telegram.DoesNotExist:
            logger.info("user enter with invalid url")
            return (None, "You entered with an invalid URL.")

        if user_telegram.telegram_chat_id is None:
            logger.info("user doesnt have telegram_chat_id")
            user_telegram.telegram_chat_id = telegram_chat_id
            user_telegram.telegram_name = name
            user_telegram.save()
            logger.info(f"{user_telegram} updated")
            return user_telegram, ""

        elif user_telegram.telegram_chat_id == telegram_chat_id:
            logger.info("user already have telegram_chat_id")
            return user_telegram, ""

        elif user_telegram.telegram_chat_id != telegram_chat_id:
            logger.info("user have different telegram_chat_id")
            return (None, "The user doesn't exist. You entered with a URL.")






async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(update.message.chat.id)
    name = update.message.chat.first_name + " " + (update.message.chat.last_name if update.message.chat.last_name else "")


    message_success = (f"Hello {name}, welcome to the Katyusha bot.\n"
                       "Please select /my_information to get your information, /get_course_in_my_calender to get Courses that were added to the calendar.")

    message_fail = (f"Hello {name}, welcome to the Katyusha bot.\n"
                "You should first log in to the website and then access the Telegram bot through the link provided by the website in order to utilize the bot's features.\n"
                "http://katyushaiust.ir/accounts/login/")


    if context.args:
        logging.info(context.args)
        logging.info("created user")
        logger.info(update.message.chat.id)

        create_func = sync_to_async(is_user_in_databese)
        hashed_number = context.args[0]
        user_telegram, message = await create_func(hashed_number, str(update.message.chat.id), name)

        if user_telegram:
            await update.message.reply_text(message_success)
        else:
            await update.message.reply_text(message_fail + f'\n{message}')

    else:
        create_func = sync_to_async(is_user_in_databese)
        user_telegram, message = await create_func(hashed_number=None, telegram_chat_id=str(update.message.chat.id), name=name)
        if message == "The user doesn't exist. You never entered with a URL.":
            await update.message.reply_text(message_fail)

        else:
            await update.message.reply_text(message_success)

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

    if formatted_data == "[]":
        await update.message.reply_text(
            text=f"You have no course in your calendar."
        )
    else:
        await update.message.reply_text(formatted_data)


def main() -> None:
    """Run the bot."""


    # Create the Application and pass it your bot's token.
    application =  Application.builder().token("6182994088:AAFZbZ9_fMeWebvb4x9_vb3k4q74RYWAuOM").build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("my_information", my_information))
    application.add_handler(CommandHandler("get_course_in_my_calender", get_course_in_my_calender))


    # Run the bot until the user presses Ctrl-C
    application.run_polling()



if __name__ == "__main__":
    main()
