from telegram.ext import (updater,
                          CommandHandler,
                          MessageHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)
from start import *

import os

# PORT = int(os.environ.get('PORT', 8443))


def main():
    updater = updater("6182994088:AAFwEqBN16Yvudx85OkkQVpkiNwHmmO3GtY", use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    dispatcher.add_handler(CommandHandler("start", start))


    updater.start_polling()
    # updater.start_webhook(listen="0.0.0.0",
    #                         port=PORT,
    #                         url_path=TOKEN)
    # updater.bot.setWebhook('https://accordion.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()