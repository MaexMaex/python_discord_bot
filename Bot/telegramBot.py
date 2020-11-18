#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import re
import argparse
from sys import platform

from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler, ConversationHandler, Filters, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from sqlite_models import User, Bttn, TelegramBttn, TelegramUser
from sqlite_view import DBView
from datetime import datetime

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", type=str, required=True,
                help="path to your token.txt")
ap.add_argument("-c", "--channel", type=str, required=False,
                help="path to the chan_id.txt")
args = vars(ap.parse_args())


if platform == "linux" or platform == "linux2":
    print('Loading production token ' + args['token'])
    with open(args['token']) as f:
        token = f.read().strip()
elif platform == "darwin":
    # OS X
    print('Loading development token ' + args['token'])
    with open(args['token']) as f:
        token = f.read().strip()

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
undogifs = ['https://media.giphy.com/media/VbrGKu56dceVa/giphy.gif',
            'http://giphygifs.s3.amazonaws.com/media/I7kkegrRyNrk4/giphy.gif', 'https://media.giphy.com/media/vohOR29F78sGk/giphy.gif']
biralist = ['öl', 'bisse', 'bärs', 'kalja', 'bira',
            'beer', 'pilsner', 'ipa', 'ale', 'stout', 'lager']
beergifs = ['https://media.giphy.com/media/Zw3oBUuOlDJ3W/giphy.gif', 'https://media.giphy.com/media/3o7btZjaYxqkGyOYA8/giphy.gif', 'https://media.giphy.com/media/xT1R9XnFJkL1S2BFqo/giphy.gif',
            'https://media.giphy.com/media/3o7TKoQ2whJd062fba/giphy.gif', 'https://media.giphy.com/media/zXubYhkWFc9uE/giphy.gif', 'https://media.giphy.com/media/KylMzku5T57A4/giphy.gif', 'https://media.giphy.com/media/26ght6psZEpil8pHy/giphy.gif',
            'https://media.giphy.com/media/qA6m3bCy71Ukw/giphy.gif', 'https://media.giphy.com/media/5WKhPddhq34Eo/giphy.gif', 'https://media.giphy.com/media/3ohc10ewmaWSM5UBTa/giphy.gif', 'https://media.giphy.com/media/fvB5VRSCElfzO/giphy.gif',
            'https://media.giphy.com/media/6b8D22vANc2mPzs178/giphy.gif', 'https://media.giphy.com/media/B2kqzdgMSBcpxHL33q/giphy.gif', 'https://media.giphy.com/media/1xmBbk9i6cQCjuVTzC/giphy.gif',
            'https://media.giphy.com/media/3o6MbexPF7FxgIkxLW/giphy.gif', 'http://giphygifs.s3.amazonaws.com/media/149EV8wlV75ZQc/giphy.gif', 'https://media.giphy.com/media/3ohfFJUMgs8m5F9qec/giphy.gif',
            ]


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def undo(update, context):
    query = update.callback_query
    bot = context.bot
    user_obj = context.user_data['user']
    status = db.tel_get_status(user_obj)

    if status[0] is 1:
        text = "I WILL FIX!\n\n\n" + \
            random.choice(undogifs) + \
            "\n\nI removed your last bttn and reset your status!"
        db.tel_edit_status(user_obj, 0)
        db.tel_remove_score(user_obj)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
        )
        return ConversationHandler.END

    else:
        text = 'I dont know why you would ever want to stop the party, but okay \n' + \
            random.choice(undogifs)
        db.tel_edit_status(user_obj, 1)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
        )
        return ConversationHandler.END


def stats(update, context):
    query = update.callback_query
    bot = context.bot
    stats = db.tel_get_all_score()
    text = "These are the statistics for all users!\n"
    for line in stats:
        text += line[0] + " : " + str(line[1]) + "\n"
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
    )
    return ConversationHandler.END


def status(update, context):
    """the status method returns the status of every registered user"""

    query = update.callback_query
    bot = context.bot
    status = db.tel_get_all_status()

    for user in status:
        if user[1] is 0:
            Bttns = False
        else:
            Bttns = True

    if Bttns:
        text = 'The following minotaurs are drinking!\n'
        for line in status:
            if line[1] is 1:
                text += line[0] + "\n"
            else:
                pass

    else:
        text = "Awfully silent here 😞😞😞"

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
    )
    return ConversationHandler.END


def get_status(user_obj):
    status = db.tel_get_status(user_obj)
    if status[0] is 0:
        return "You are not drinking."
    else:
        return "You are currently drinking."


def bttn(update, context):
    user_obj = context.user_data['user']
    status = db.tel_get_status(user_obj)
    query = update.callback_query
    bot = context.bot
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
        db.tel_edit_status(user_obj, 0)
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
        'version': 'v3.0',
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
    status = get_status(user_obj)
    text = random.choice(hellolist) + \
        " {}!🍻\n{}\n\n".format(user_obj.name, status)
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
    text = random.choice(hellolist) + " {}! Select sign up if you want to move your discord stats to telegram!".format(
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


def check_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def word_finder(update, context):
    content = update.message.text.split()
    check = ' '.join(biralist)
    if random.random() <= 0.6:
        if check_word(content)(check):
            text = "🍺 😍" + random.choice(beergifs)
            update.message.reply_text(text)


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
    updater = Updater(token, use_context=True)
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
    dp.add_handler(MessageHandler(Filters.text, word_finder))
    dp.add_error_handler(error)

    updater.start_polling()
    print('[INFO]: STARTING POLLING, THEN IDLING!!')
    updater.idle()


if __name__ == '__main__':
    main()
