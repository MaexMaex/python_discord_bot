import logging

from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from sqlite_models import User, Bttn
from sqlite_view import DBView
from datetime import datetime

#change the logging level between INFO - normal mode or DEBUG - verbose mode
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)    

db = DBView()  
print('[INFO]: DATABASE FIRED UP!!')


def error(update, context, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def undo(update, context):
    if checkUser(update, context):
        user = update.message.from_user 
        
        update.message.reply_text("I removed your last bttn and reset your status!")
        db.remove_bttn(user.id)
        user_status = db.get_min_status(user.id)
        if user_status == 1:
            db.change_status(user.id, 0)
        else:
            db.change_status(user.id, 1)

def stats(update, context):
    if checkUser(update, context):
        #stats = db.get_all_statistics()        
        users = "These are the statistics for all users!\n"
        for line in stats:
            users += line[0] + " : " + str(line[1]) + "\n"
        update.message.reply_text(users)

#the status method returns the status of every registered user   
def status(update, context):
    if checkUser(update, context):
        status = db.get_all_status()
        users = "The following minotaurs are drinking!\n"
        for line in status:
            if line[1] == 1:
                users += line[0] + " : " + str(line[1]) + "\n"
            else:
                pass
        update.message.reply_text(users)


def start(update, context):
    users = db.get_users()
    keyboard = []
    for user, i in users:
        keyboard.append([InlineKeyboardButton(user, callback_data=i)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('To begin moving your discord stats to telegram, please select your name from the list of users below:', reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    user = db.get_user(query.data)
    # query.edit_message_text(text="Selected option: {}".format(user))
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=0),
        InlineKeyboardButton("No", callback_data=1)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.edit_message_text(chat_id=update.callback_query.message.chat_id,
                      message_id=update.callback_query.message.message_id,
                      text="Are you sure you are {}?".format(user.name), 
                      reply_markup=InlineKeyboardMarkup(keyboard))
    
    update.answer_callback_query(update.callback_query.id, text='')

def bttn(update, context):
    stat = db.get_all_score()
    print(stat)
    return
    if checkUser(update, context):
        user = update.message.from_user 
        #status = db.get_min_status(user.id) 
        if status[0] == 0:
                #btn = Bttn(usr_obj.discord_id, message.content, message.timestamp)
                # Get the status of the user
                #db.edit_status(usr_obj, 1)
                #db.add_score(usr_obj)
                #db.add_bttn(usr_obj, btn)
            update.message.reply_text(user.username + " is drinking!")
        else:
            
            update.message.reply_text(user.username + " stopped drinking!")


# def checkUser(user):

#the help method displays what this bot is does and give some stats about it
def help(update, context):
    # current date and time
    now = datetime.now()
    s2 = now.strftime("%d/%m/%Y, %H:%M")
    print(update)
    botInfo = {
        'version': '2.0',
        'name': 'D2',
        'hobby': 'Beer',
        'time': s2
    }

    #################################################################################    

    helpGreeting = "[INFO]: I am {name}-bot mark {version}.\n\n[INFO:] Your are [STATUS] :(\nTo begin, click here => /start".format(**botInfo)                
    print('helpGreeting')
    ####################################################################################

    update.message.reply_text(helpGreeting)


def getToken():
    f = open("telegramToken.txt","r")
    return f.read()


    


def main():
    print('[INFO]: STARTING UP!')
    updater = Updater(token=getToken(), use_context=True)
    print('[INFO]: GOT THE TOKEN!')

    dp = updater.dispatcher 

    dp.add_handler(CommandHandler("bttn", bttn))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("undo", undo))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)

    updater.start_polling()
    print('[INFO]: STARTING POLLING, THEN IDLING!!')
    updater.idle()

if __name__ == '__main__':
    main()