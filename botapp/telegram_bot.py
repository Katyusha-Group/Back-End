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
    ContextTypes, Updater, ConversationHandler, MessageHandler, filters

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

    course_number = 1




def main() -> None:
    """Run the bot."""
    course_number = 1
    # Define a function to handle the user's age input

    def getnumberconvert_to_date(number):
        if number == '0':
            return "شنبه"
        elif number == '1':
            return "یکشنبه"
        elif number == '2':
            return "دوشنبه"
        elif number == '3':
            return "سه شنبه"
        elif number == '4':
            return "چهارشنبه"
        elif number == '5':
            return "پنجشنبه"
        elif number == '6':
            return "جمعه"

    async def get_course_information(update: Update, context):
        text = '<b>کد درس برو بهم بده تا من اطلاعاتی که از اون درس میدونم رو بهت بگم. </b>'
        await update.message.reply_text(text, parse_mode='HTML')
        return course_number


    async def get_age(update: Update, context):
        course_number = update.message.text
        # request with token
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg5NjgxOTQyLCJpYXQiOjE2ODg4MTc5NDIsImp0aSI6ImFhZDBkMzVlMmNlYzRiYWQ4YWMyYjExMzEzN2NiYWIwIiwidXNlcl9pZCI6MTB9.vp0kqPgX-JX6W55Sh6ofDcVnrE8qNRr3t7JxP0Q3cHM"
        }
        course_information = requests.get(f"http://127.0.0.1:7000/courses/{course_number}/", headers=headers).json()

        name = course_information['name'] if course_information['name'] else "نام درس موجود نیست"
        capacity = course_information['capacity'] if course_information['capacity'] else "ظرفیت درس موجود نیست"
        registered_count = course_information['registered_count'] if course_information['registered_count'] else "تعداد افرادی که درس را برداشته اند موجود نیست"
        waiting_count = course_information['waiting_count'] if course_information['waiting_count'] else "تعداد افراد در لیست انتظار موجود نیست"
        registration_limit = course_information['registration_limit'] if course_information['registration_limit'] else "محدودیت اخذ موجود نیست"
        exam_times = course_information['exam_times'] if course_information['exam_times'] else "زمان امتحان موجود نیست"
        date = exam_times[0]['date'] if exam_times[0]['date'] else "تاریخ امتحان موجود نیست"
        exam_start_time = exam_times[0]['exam_start_time'] if exam_times[0]['exam_start_time'] else "ساعت شروع امتحان موجود نیست"
        exam_end_time = exam_times[0]['exam_end_time'] if exam_times[0]['exam_end_time'] else "ساعت پایان امتحان موجود نیست"
        course_times = course_information['course_times'] if course_information['course_times'] else "زمان کلاس موجود نیست"
        course_day = getnumberconvert_to_date(course_times[0]['course_day']) if course_times[0]['course_day'] else "روز کلاس موجود نیست"
        course_start_time = course_times[0]['course_start_time'] if course_times[0]['course_start_time'] else "ساعت شروع کلاس موجود نیست"
        course_end_time = course_times[0]['course_end_time'] if course_times[0]['course_end_time'] else "ساعت پایان کلاس موجود نیست"
        place = course_times[0]['place'] if course_times[0]['place'] else "مکان کلاس موجود نیست"

        teachers = course_information['teachers'] if course_information['teachers'] else "استاد موجود نیست"

        text = ""
        for a_day in course_times:
            text += f"روز: {getnumberconvert_to_date(a_day['course_day'])}\nساعت شروع: {a_day['course_start_time']}\nساعت پایان: {a_day['course_end_time']}\nمکان: {a_day['place']}\n\n"
            text += "\n"

        await update.message.reply_text(
            text=f"<b><u>📚{name}</u></b>\n"
                 f"<b>استاد:</b> {teachers}\n"
                 f"<b>ظرفیت کلاس:</b> {capacity}\n"
                 f"<b>تعداد افرادی که درس را برداشته اند:</b> {registered_count}\n"
                 f"<b>تعداد افراد در لیست انتظار:</b> {waiting_count}\n"
                 f"<b>محدودیت اخذ:</b>\n{registration_limit}\n"
                 f"<b>⏰زمان و مکان کلاس:</b>\n{text}\n"  
                f"زمان امتحان:{date}\n"
                 f"ساعت شروع امتحان:{exam_start_time} \n"
                 f"ساعت پایان امتحان:{exam_end_time}\n",
            parse_mode='HTML'
        )

        await update.message.reply_text(
                                     "می تونی این کارهارو با بات کاتیوشا انجام بدی:\n\n"
                                    "/get_course_information\n"
                                    "درس هایی که به کلندرت اضافه کردی\n\n"
                                    "/get_course_in_my_calender")


        return ConversationHandler.END



    # Create the Application and pass it your bot's token.
    application =  Application.builder().token("6182994088:AAFZbZ9_fMeWebvb4x9_vb3k4q74RYWAuOM").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("my_information", my_information))
    application.add_handler(CommandHandler("get_course_in_my_calender", get_course_in_my_calender))
    # application.add_handler(CommandHandler("get_information_course", get_information_course))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("get_course_information", get_course_information)],
        states={
            course_number: [MessageHandler(filters.TEXT, get_age)]
        },
        fallbacks=[]
    )

    # Add the conversation handler to the dispatcher
    application.add_handler(conversation_handler)


    # Run the bot until the user presses Ctrl-C
    application.run_polling()



if __name__ == "__main__":
    main()
