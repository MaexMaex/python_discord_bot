import logging

from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from sqlite_models import User, Bttn
from sqlite_view import DBView
from datetime import datetime

# change the logging level between INFO - normal mode or DEBUG - verbose mode
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db = DBView()
print('[INFO]: DATABASE FIRED UP!!')

# Stages
FIRST, SECOND, THIRD = range(3)
# Callback data
YES, NO = range(2)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def undo(update, context):
    if check_user(update, context):
        user = update.message.from_user

        update.message.reply_text(
            "I removed your last bttn and reset your status!")
        db.remove_bttn(user.id)
        user_status = db.get_min_status(user.id)
        if user_status == 1:
            db.change_status(user.id, 0)
        else:
            db.change_status(user.id, 1)


def stats(update, context):
    if check_user(update, context):
        # stats = db.get_all_statistics()
        users = "These are the statistics for all users!\n"
        for line in stats:
            users += line[0] + " : " + str(line[1]) + "\n"
        update.message.reply_text(users)


# the status method returns the status of every registered user
def status(update, context):
    if check_user(update, context):
        status = db.get_all_status()
        users = "The following minotaurs are drinking!\n"
        for line in status:
            if line[1] == 1:
                users += line[0] + " : " + str(line[1]) + "\n"
            else:
                pass
        update.message.reply_text(users)


def start(update, context):
    text = "Howdy. Select sign up if you want to move your discord stats to telegram!"
    keyboard = [
        [InlineKeyboardButton("Sign up", callback_data=str(YES)),
         InlineKeyboardButton("Cancel", callback_data=str(NO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return FIRST


def signUp(update, context):
    text = "To transfer your Discord stats to Telegram, please select your old Discord username from the list below:"
    users = db.get_users()
    query = update.callback_query
    bot = context.bot
    keyboard = []

    for user, i in users:
        keyboard.append([InlineKeyboardButton(user, callback_data=i)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=text,
                          reply_markup=reply_markup)
    return SECOND


def confirm(update, context):

    query = update.callback_query
    user = db.get_user(query.data)
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=str(YES)),
            InlineKeyboardButton("No", callback_data=str(NO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="Are you sure you are {}?".format(user[1]),
                          reply_markup=reply_markup)
    return THIRD


def done(update, context):
    query = update.callback_query
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Thank you! The database has been updated with your new credentials. \n🍺🍺🍺🍺 ',
    )
    return ConversationHandler.END


def cancel(update, context):
    query = update.callback_query
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='CYA 🍺!',
    )
    return ConversationHandler.END


def bttn(update, context):
    if check_user(update, context):
        user = update.message.from_user
        # status = db.get_min_status(user.id)
        if status[0] == 0:
                # btn = Bttn(usr_obj.discord_id, message.content, message.timestamp)
                # Get the status of the user
                # db.edit_status(usr_obj, 1)
                # db.add_score(usr_obj)
                # db.add_bttn(usr_obj, btn)
            update.message.reply_text(user.username + " is drinking!")
        else:

            update.message.reply_text(user.username + " stopped drinking!")


def check_user(update, context):
    """verify that a user has signed up"""
    u_id = update.from.id
    if db.tel_get_user(u.id)


def help(update, context):
    """this help method displays what this bot does and give some stats about it"""
    user = update.message.from_user
    if user.username:
        user = user.username
    else:
        user = user.first_name
    # now = datetime.now()
    # s2 = now.strftime("%d/%m/%Y, %H:%M")
    # 'time': s2,
    botInfo = {
        'version': 'v2.0',
        'name': 'D2',
        'hobby': 'Beer',
        'user': user
    }

    #################################################################################

    helpGreeting = "Hi {user}! I am {name}-bot {version}.\n\n If your want to started press /start".format(
        **botInfo)

    ####################################################################################

    update.message.reply_text(helpGreeting)


def getToken():
    f = open("telegramToken.txt", "r")
    return f.read()


def main():
    print('[INFO]: STARTING UP!')
    updater = Updater(token=getToken(), use_context=True)
    print('[INFO]: GOT THE TOKEN!')

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(signUp, pattern='^' + str(YES) + '$'),
                    CallbackQueryHandler(cancel, pattern='^' + str(NO) + '$')],

            SECOND: [
                CallbackQueryHandler(confirm),
            ],
            THIRD: [
                CallbackQueryHandler(done, pattern='^' + str(YES) + '$'),
                CallbackQueryHandler(signUp, pattern='^' + str(NO) + '$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("bttn", bttn))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("undo", undo))
    dp.add_handler(CommandHandler("help", help))

    dp.add_error_handler(error)

    updater.start_polling()
    print('[INFO]: STARTING POLLING, THEN IDLING!!')
    updater.idle()


if __name__ == '__main__':
    main()
