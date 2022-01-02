import os
import time

import discord
from discord.ext import commands
from replit import db

from keep_alive import keep_alive

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

def query_db(user):
    if user in db.keys():
        time_diff = time.time() - db[user][1]

        if time_diff < 86_400:
            return 86_400 - round(time_diff)
        else:
            db[user][0], db[user][1] = db[user][0] + 1, time.time()
    else:
        db[user] = [1, time.time()]

def wipe():
    for key in db.keys():
        del db[key]

@bot.event
async def on_ready():
    # wipe()
    print('gm - bot has been activated')

@bot.command(aliases=['Gm', 'gM', 'GM'])
async def gm(ctx):
    user = str(ctx.author.id)
    error = query_db(user)
    
    if not error:
        await ctx.send(f'thank you for your business. your gm count is {db[user][0]}')
        await ctx.message.add_reaction('✅')
    else:
        await ctx.send(f'once per day only. try again in {error} seconds')
        await ctx.message.add_reaction('❌')

keep_alive()
bot.run(os.environ['TOKEN'])
