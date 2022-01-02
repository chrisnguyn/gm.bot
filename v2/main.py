import os

import discord
from discord.ext import commands
from replit import db

from cooldown_utils import overwatch, users_on_cooldown
from db_utils import add_user, update_user, user_exists, wipe
from web_server import persist

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

@bot.event
async def on_ready():
    wipe(False)
    print('gm - bot has been activated')

@bot.command(aliases=['Gm', 'gM', 'GM'])
async def gm(ctx):
    user = str(ctx.author.id)

    if not user_exists(user):
        add_user(user)
    
    if user in users_on_cooldown:
        await ctx.send(f'once per day only. try again tomorrow')
        await ctx.message.add_reaction('❌')
    else:
        users_on_cooldown.add(user)
        update_user(user)
        await ctx.send(f'thank you for your business. your gm count is {db[user]}')
        await ctx.message.add_reaction('✅')

persist()
overwatch()
bot.run(os.environ['TOKEN'])
