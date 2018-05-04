# -*- coding: utf-8 -*-
import discord
import asyncio
import logging
import random

from sqlite_models import User, Bttn
from sqlite_view import DBView

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Load the secret token
with open('../token.txt') as f:
    token = f.read().strip()

# Load channel ids
with open('../chan_id.txt') as f:
    chan_id = f.read().strip()

client = discord.Client()
db = DBView()

games = ['Beer Simulator 2018', 'Pong', 'Bar Fighter VR', 'Get to the Choppah', 'Meme-Lord-9000']

@client.event
async def on_ready():
    print('Logged in as')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name=random.choice(games)))

# Returns a user_object from the database
def get_user_obj(id):
    usr_list = db.get_user(id)
    usr_obj = User(usr_list[0], usr_list[1], usr_list[2], usr_list[3])
    return usr_obj

@client.event
async def on_member_update(before, after):
    usr = User(before.id, after.nick)
    db.update_nickname(usr)

# Adds new users to the database as they join the server.
@client.event
async def on_member_join(member):
    server = member.server
    usr = User(member.id, member.name) 
    db.add_user(usr)


@client.event
async def on_message(message):
    # Ignore messages sent by the bot
    if message.author == client.user:
        return

    if message.content.startswith('/bttn'):
        author = message.author
        # Checks if the user is added to the db
        if db.get_discord_id(author.id) is not None:
            # Create a User object
            usr_obj = get_user_obj(author.id)
            # Checks the user status
            status = db.get_status(usr_obj)
            if status[0] is 0:
                # Create a bttn object              
                btn = Bttn(usr_obj.discord_id, message.content, message.timestamp)
                # Get the status of the user
                db.edit_status(usr_obj, 1)
                db.add_score(usr_obj)
                db.add_bttn(usr_obj, btn)
                fmt = '{0.author.mention}'.format(message) + ' is drinking!'
                await client.send_message(message.channel, fmt.format())
            else:
                db.edit_status(usr_obj, 0)
                fmt = '{0.author.mention}'.format(message) + ' stopped drinking!'
                await client.send_message(message.channel, fmt.format())
        else:
            fmt = "You don't seem to be in the database, try /start !"

    if message.content.startswith('/stats'):
        stats = db.get_all_score()
        fmt = "Here are the stats:\n"
        for user in stats:
            fmt += user[0] + " : " + str(user[1]) + "\n"
        await client.send_message(message.channel, fmt.format())

    if message.content.startswith('/start'):
        author = message.author
        if db.get_discord_id(author.id) is None:
            usr = User(author.id, author.name, 0, 0) 
            db.add_user(usr)
            fmt = "http://gph.is/24IKcSC"
            await client.send_message(message.channel, fmt.format())
        else:
            msg = await client.send_message(message.channel, 'I did the math, your have already signed up to the d2-service.\nI will try deleting the database, maybe that helps!')
            await client.delete_message(msg)

    if message.content.startswith('/status'):
        status = db.get_all_status()
        if status is not None:
            fmt = "The following minotaurs are drinking:\n"
            for user in status:
                if user[1] is 1:
                    fmt += user[0] + "\n"
        else:
            fmt = "Is this what tipaton looks like?"
        await client.send_message(message.channel, fmt.format())

    if message.content.startswith('/undo'):
        author = message.author
        # Checks if the user is added to the db
        if db.get_discord_id(author.id) is not None:
            fmt = "*I WILL FIX!*\n\n\nhttp://gph.is/SXx5gj"
            # Create a User object
            usr_obj = get_user_obj(author.id)
            # Checks the user status
            status = db.get_status(usr_obj)
            # A faulty bttn that is ON
            if status[0] is 1:
                # Delete last enty in bttns and rollback score and stats
                db.edit_status(usr_obj, 0)
                db.remove_score(usr_obj)
                # Create a bttn object
                # 
                # Fix this in the next update             
                btn = Bttn(usr_obj.discord_id, 'PLEASE REMOVE THE ROW ABOVE, THIS WAS IS A UNDO', message.timestamp)
                db.add_bttn(usr_obj, btn)
                await client.send_message(message.channel, fmt.format())
            else:
                db.edit_status(usr_obj, 1)
                await client.send_message(message.channel, fmt.format())

    if message.content.startswith('/help'):
        fmt = "*hick*\n\nHi, I'm D2-Bot and I live here now.\nThe old commands are still available :\nbttn, stats, status, undo and help!\n*hick*"
        await client.send_message(message.channel, fmt.format())

    
    if checkWord(message.content):
        # Make the toasts a little more random
        array = ['🍻', '🍺']
        if random.random() > 0.5:
            await client.add_reaction(message, random.choice(array))
        

        
@client.event
async def on_message_delete(message):
    if message.author == client.user:
        fmt = '*[SERVER RESPOND]* : {0.author.name} tried nuking the service, unacceptable, the show *MUST* go on! \n*[SERVER RESPOND]* :{0.author.name} wrote: \n{0.content}'
        await client.send_message(message.channel, fmt.format(message))
    else:
        gifList = ['http://gph.is/1tqdwbx', 'http://gph.is/1a6zuNG', 'http://gph.is/2FUSxMU', 'http://gph.is/2Cd1e3e', 'http://gph.is/1OZm0mH']
        fmt = random.choice(gifList)
        await client.send_message(message.channel, fmt.format(message))

def checkWord(content):
    biraList = ['öl', 'bisse', 'bärs', 'kalja', 'bira', 'beer', 'pilsner']
    for word in biraList:
        if content.find(word) is not -1:
            return True
        elif content.find(word.upper()) is not -1:
            return True
        elif content.find(word.title()) is not -1:
            return True

client.run(token)