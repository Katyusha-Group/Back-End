#!/usr/bin/env python
import asyncio
import django
import json
import logging
import os
from django.conf import settings




from django.conf import settings







# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance

import logging
import requests





# Configure the Django settings module

# Import the models


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

    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,

)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# TOTAL_VOTER_COUNT = 3


# Set up Django environment




from asgiref.sync import sync_to_async







async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(update.message.chat.id)
    name = update.message.chat.first_name + " " + (update.message.chat.last_name if update.message.chat.last_name else "")




    if context.args:
        logging.info(context.args)
        logging.info("created user")
        logger.info(update.message.chat.id)
        hashed_number = context.args[0]


        response = requests.post("http://127.0.0.1:8000/bot/is_it_in_database/", data={"hashed_number": hashed_number, "telegram_chat_id": str(update.message.chat.id), 'name': name}).json()
        message = response['message']
        await update.message.reply_text(message)


    # else:
    #     create_func = sync_to_async(is_user_in_databese)
    #     user_telegram, message = await create_func(hashed_number=None, telegram_chat_id=str(update.message.chat.id), name=name)
    #     if message == "The user doesn't exist. You never entered with a URL.":
    #         await update.message.reply_text(message_fail)
    #
    #     else:
    #         await update.message.reply_text(message_success)

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
