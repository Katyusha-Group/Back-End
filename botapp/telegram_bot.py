#!/usr/bin/env python
import asyncio
import django
import json
import logging
import os
from django.conf import settings
import ast




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
    logger.info(f"name= {name}, telegram_chat_id= {str(update.message.chat.id)} start bot.")

    if context.args:
        logging.info(context.args)
        hashed_number = context.args[0]

        logger.info(f"hashed_number= {hashed_number}, telegram_chat_id= {str(update.message.chat.id)}, name= {name}")

        response = requests.post("https://katyushaiust.ir/bot/is_it_in_database/", data={"hashed_number": hashed_number, "telegram_chat_id": str(update.message.chat.id), 'name': name}).json()
        logger.info(response)
        message = response['message']

        await update.message.reply_text(message)


    else:
        logger.info("USER DOESNT START WITH URL")
        response = requests.post("https://katyushaiust.ir/bot/is_it_in_database/", data={ "telegram_chat_id": str(update.message.chat.id), 'name': name}).json()
        logger.info(response)
        message = response['message']
        logger.info(message)
        await update.message.reply_text(message)


async def my_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(update.message.chat.id)
    data_user = requests.get(f'http://katyushaiust.ir/bot/get_email/{update.message.chat_id}').json()
    logger.info(data_user)
    await update.message.reply_text(
        text=f"این اطلاعاتیه که من ازت میدونم:\n"
             f"User Name: {data_user['username']}\nDeparment Name: {data_user['department_name']}"
    )

async def get_course_in_my_calender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends information about the user and its chat."""
    data_user = requests.get(f'http://katyushaiust.ir/bot/get_email/{update.message.chat_id}').json()
    id = data_user['id']
    # get data of user
    data_user = requests.get(f"http://katyushaiust.ir/bot/get_courses_on_calendar/{id}/").json()

    if data_user == []:
        await update.message.reply_text(
            text=f"هیچ درسی به کلندرت اضافه نکردی هنوز!"
        )
    else:
        await update.message.reply_text(
            text=f"این درس ها رو به کلندرت اضافه کردی:\n"
        )
        for course in data_user:
            code = course['complete_course_number']
            day = []
            course_start_time = []
            course_end_time = []
            place = []
            for inf in course['course_times']:
                day.append(inf['course_day'])
                course_start_time.append(inf['course_start_time'])
                course_end_time.append(inf['course_end_time'])
                place.append(inf['place'])


            text = ""
            prefix_code = code[:6]
            suffix_code = code[8:]
            code = suffix_code + "__" + prefix_code
            for a_day in course['course_times']:
                text += f"روز: {a_day['course_day']}\nساعت شروع: {a_day['course_start_time']}\nساعت پایان: {a_day['course_end_time']}\nمکان: {a_day['place']}\n\n"
                text += "\n"
            await update.message.reply_text(
                text=f"<b><u>📚{course['name']}</u></b>\n"
                     f"<b>🔢کد درس:</b> {code}\n"
                     f"<b>ظرفیت کلاس:</b> {course['capacity']}\n"
                     f"<b>تعداد افرادی که درس را برداشته اند:</b> {course['registered_count']}\n"
                     f"<b>تعداد افراد در لیست انتظار:</b> {course['waiting_count']}\n"
                     f"<b>محدودیت اخذ:</b>\n{course['registration_limit']}\n"
                     f"<b>⏰زمان و مکان کلاس:</b>\n{text}\n"
                     f"<b>📝تاریخ امتحان:</b> \n"
                     f"زمان امتحان:{course['exam_times'][0]['date']}\n"
                     f"ساعت شروع امتحان:{course['exam_times'][0]['exam_start_time']} \n"
                     f"ساعت پایان امتحان:{course['exam_times'][0]['exam_end_time']}\n",
                parse_mode='HTML'
            )

    # logger.info(data_user)
    # logger.info(data_user['courses'])
    # formatted_data = json.dumps(data_user, indent=4, ensure_ascii=False)
    # data_list = ast.literal_eval(data_user)
    # data_dict = dict(data_list[0])
    #
    #
    # else:
    #
    #     await update.message.reply_text(data_dict)


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
