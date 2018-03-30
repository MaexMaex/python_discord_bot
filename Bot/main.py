# -*- coding: utf-8 -*-
import discord
import asyncio

# Load the secret token
with open('../token.txt') as f:
    token = f.read().strip()

client = discord.Client()

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await client.send_message(server, fmt.format(member, server))

@client.event
async def on_message(message):
    if message.content.startswith('/bttn'):
        author = message.author
        fmt = str(author.name) + ' id: ' + str(author.id) + ' is drinking BEER!'
        await client.send_message(message.channel, fmt.format())

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)