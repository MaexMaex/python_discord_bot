# -*- coding: utf-8 -*-
import discord
import asyncio
import argparse
import logging
import random
import matplotlib.pyplot as plt
import numpy as np
from sys import platform

from sqlite_models import User, Bttn
from sqlite_view import DBView

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", type=str, required=True,
	help="path to your token.txt")
ap.add_argument("-c", "--channel", type=str, required=True,
	help="path to the chan_id.txt")
    
args = vars(ap.parse_args())

# Load the secret token based on os
if platform == "linux" or platform == "linux2":
    print('Loading production token ' + args['token'])
    with open(args['token']) as f:
        token = f.read().strip()
elif platform == "darwin":
    # OS X
    print('Loading development token '+ args['token'])
    with open(args['token']) as f:
        token = f.read().strip()


# Load channel ids
print('Your main Bot channel id is: '+ args['channel'])
with open(args['channel']) as f:
    chan_id = f.read().strip()

client = discord.Client()
db = DBView()

games = ['Beer Simulator 2018', 'Not feeling so well', 'Time for a cold one!', 'Bag in Box?', 'Relaxing!']

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
    # check for users who has no nick
    if after.nick is None:
        usr = User(before.id, after.name)
        db.update_nickname(usr)
    else:
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
        label = []
        no_bttns = []

        stats = db.get_all_score()
        # builds the labels and number of bttns lists
        for user in stats:
            if user[0] is None:
                fmt += "This is an error message! There are people without nicknames, I hate that! \nThis has probably messed.\nTell people to set their nicknames or I will do so! \nhttps://support.discordapp.com/hc/en-us/articles/219070107-Server-Nicknames"
            else:
                label.append(user[0])
                no_bttns.append(user[1])
        
        index = np.arange(len(label))
        plt.bar(index, no_bttns)
        plt.xticks(index, label, fontsize=10, rotation=30)
        plt.title('Number of Bttns as of 1 Jan 2019')

        for a,b in zip(index, no_bttns):
            plt.text(a, b, str(b), color='red', fontweight='bold', ha='center', va='bottom', fontsize=20)

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig('figure.png')
        plt.close(fig) 

        await client.send_file(message.channel, 'figure.png')

    if message.content.startswith('/start'):
        author = message.author
        if db.get_discord_id(author.id) is None:
            usr = User(author.id, author.name, 0, 0) 
            db.add_user(usr)
            fmt = "http://gph.is/24IKcSC"
            await client.send_message(message.channel, fmt.format())
        else:
            fmt = "https://gph.is/1ANwFZc"
            await client.send_message(message.channel, fmt.format())

    if message.content.startswith('/status'):
        status = db.get_all_status()
        
        # stupid loop to check if there are 1 in the stats
        for user in status:
            if user[1] is 0:
                Bttns = False
            else:
                Bttns = True
                break

        if Bttns:
            fmt = "The following minotaurs are drinking:\n"
            for user in status:
                if user[1] is None:
                    fmt += "This is an error message! There are people without nicknames, I hate that! \nThis has probably messed.\nTell people to set their nicknames or I will do so! \nhttps://support.discordapp.com/hc/en-us/articles/219070107-Server-Nicknames"
                    return
                else:
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
        fmt = "Hi, I'm **D2-Bot**.\n\n__Here are my commands.__\n*Have a cold one and give it a try!!!*\n ```/bttn      - Time to let get that 💡 on!\n/stats     - Plots a beautiful graph of the current stats!\n/status    - Someone is surely having a better day than you!\n/undo      - Undo you last bttn with this!\n/help      - Show this text right here ^^^```\n"
        
        await client.send_message(message.channel, fmt.format())


    
    if checkWord(message.content):
        # Make the toasts a little more random
        array = ['🍻', '🍺']
        if random.random() > 0.5:
            await client.add_reaction(message, random.choice(array))
        

def checkWord(content):
    biraList = ['öl ', 'bisse ', 'bärs ', 'kalja ', 'bira ', 'beer ', 'pilsner ']
    for word in biraList:
        if content.find(word) is not -1:
            return True
        elif content.find(word.upper()) is not -1:
            return True
        elif content.find(word.title()) is not -1:
            return True

client.run(token)
