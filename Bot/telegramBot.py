import logging
import random

from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from sqlite_models import User, Bttn, TelegramBttn, TelegramUser
from sqlite_view import DBView
from datetime import datetime

# change the logging level between INFO - normal mode or DEBUG - verbose mode
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = DBView()
print('[INFO]: DATABASE FIRED UP!!')

# Stages
FIRST, SECOND, THIRD, MENU = range(4)
# Callback data
YES, NO, BTTN, STATUS, STATS, UNDO = range(6)

byelist = ['CYA !', 'Goodbye', 'So long!', 'Godspeed', 'Bye-Bye', 'Adios']
hellolist = ['Greetings', 'Hi', 'Howdy',
             'Welcome', 'Howdy-do', 'How are you', 'Hey']


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
    if check_user(update):
        status = db.get_all_status()
        users = "The following minotaurs are drinking!\n"
        for line in status:
            if line[1] == 1:
                users += line[0] + " : " + str(line[1]) + "\n"
            else:
                pass
        update.message.reply_text(users)


def get_status(user_obj):
    status = db.tel_get_status(user_obj)
    if status is 0:
        return "You are currently drinking."
    else:
        return "You are not drinking."


def bttn(update, context):
    user_obj = context.user_data['user']
    status = db.tel_get_status(user_obj)
    query = update.callback_query
    bot = context.bot
    print('I AM HERE', status[0])
    if status[0] is 0:
        btn = TelegramBttn(user_obj.telegram_id,
                           'TESTICOL', context.user_data['date'])
        db.tel_edit_status(user_obj, 1)
        db.tel_add_score(user_obj)
        db.tel_add_bttn(user_obj, btn)
        text = user_obj.name + ' is drinking! 🍺!'
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
        )
        return ConversationHandler.END
    else:
        text = user_obj.name + ' stopped drinking!'
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
        )
        return ConversationHandler.END


def get_user_obj(id):
    """Create a user object that is used within the bot"""
    user = db.tel_get_user(id)
    user_obj = TelegramUser(user[0], user[1], user[2], user[3], user[4])
    return user_obj


def check_user(update):
    """verify that a user has signed up"""
    user = update.message.from_user
    if db.tel_get_user(user.id) is not None:
        return True
    else:
        return False


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

    helpGreeting = "Hi {user}! I am {name}-bot {version}.\n\nTo sign up press /start\nTo open the menu press /menu\n".format(
        **botInfo)

    ####################################################################################

    update.message.reply_text(helpGreeting)


def menu(update, context):
    if not check_user(update):
        update.message.reply_text(
            'Go away!!!🖕\nPlease press \n\n/start\n\nto continue!')
        return

    user_obj = get_user_obj(update.message.from_user.id)
    if update.message.from_user.username is not None:
        if user_obj.name is not update.message.from_user.username:
            user_obj.name = update.message.from_user.username
            db.tel_update_nickname(user_obj)
    context.user_data['date'] = update.message.date
    context.user_data['user'] = user_obj
    print('I AM HERE')
    status = get_status(user_obj)
    text = random.choice(hellolist) + \
        " {}!🍻\n\n{}".format(user_obj.name, status)

    keyboard = [
        [InlineKeyboardButton("Bttn", callback_data=str(BTTN)),
         InlineKeyboardButton("Status", callback_data=str(STATUS)),
         InlineKeyboardButton("Stats", callback_data=str(STATS)),
         InlineKeyboardButton("Undo", callback_data=str(UNDO)),
         InlineKeyboardButton("Close", callback_data=str(NO)), ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return MENU


def start(update, context):
    if check_user(update):
        update.message.reply_text(
            '🍺🍺🍺🍺🍺🍺🍺🍺 You are already singed up! 🍺🍺🍺🍺🍺🍺🍺🍺')
        return
    uuid = update.message.from_user.id
    if update.message.from_user.username is not None:
        username = update.message.from_user.username
    else:
        username = update.message.from_user.first_name
    text = random.choise(hellolist) + " {}! Select sign up if you want to move your discord stats to telegram!".format(
        username)

    context.user_data['uuid'] = uuid
    context.user_data['username'] = username
    keyboard = [
        [InlineKeyboardButton("Sign up", callback_data=str(YES)),
         InlineKeyboardButton("Cancel", callback_data=str(NO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return FIRST


def signUp(update, context):
    text = "To transfer your Discord stats to Telegram, please select your old Discord username from the list below:"

    users = db.get_signup()
    query = update.callback_query
    bot = context.bot
    keyboard = []

    for user, i in users:
        keyboard.append([InlineKeyboardButton(user, callback_data=i)])
    keyboard.append([InlineKeyboardButton("Cancel", callback_data=str(NO))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=text,
                          reply_markup=reply_markup)
    return SECOND


def confirm(update, context):

    query = update.callback_query
    discord_user = db.get_user(query.data)
    bot = context.bot
    context.user_data['choise'] = discord_user
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=str(YES)),
            InlineKeyboardButton("No", callback_data=str(NO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="Are you sure you are {}?".format(
                              discord_user[1]),
                          reply_markup=reply_markup)
    return THIRD


def done(update, context):
    query = update.callback_query
    discord_user = context.user_data['choise']
    user = TelegramUser(
        context.user_data['uuid'],
        discord_user[0],
        context.user_data['username'],
        discord_user[2],
        0
    )
    db.tel_clone_discord_user(user)
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
        text=random.choice(byelist) + '🍺',
    )
    return ConversationHandler.END


def getToken():
    f = open("telegramToken.txt", "r")
    return f.read()


def main():
    print('[INFO]: STARTING UP!')
    updater = Updater(token=getToken(), use_context=True)
    print('[INFO]: GOT THE TOKEN!')

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start', start), CommandHandler('menu', menu)],
        states={
            FIRST: [CallbackQueryHandler(signUp, pattern='^' + str(YES) + '$'),
                    CallbackQueryHandler(cancel, pattern='^' + str(NO) + '$')],

            SECOND: [
                CallbackQueryHandler(cancel, pattern='^' + str(NO) + '$'),
                CallbackQueryHandler(confirm)
            ],
            THIRD: [
                CallbackQueryHandler(done, pattern='^' + str(YES) + '$'),
                CallbackQueryHandler(signUp, pattern='^' + str(NO) + '$')
            ],
            MENU: [
                CallbackQueryHandler(bttn, pattern='^' + str(BTTN) + '$'),
                CallbackQueryHandler(stats, pattern='^' + str(STATS) + '$'),
                CallbackQueryHandler(status, pattern='^' + str(STATUS) + '$'),
                CallbackQueryHandler(undo, pattern='^' + str(UNDO) + '$'),
                CallbackQueryHandler(cancel, pattern='^' + str(NO) + '$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))

    dp.add_error_handler(error)

    updater.start_polling()
    print('[INFO]: STARTING POLLING, THEN IDLING!!')
    updater.idle()


if __name__ == '__main__':
    main()
