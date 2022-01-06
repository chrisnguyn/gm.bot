import os

import discord
from discord.ext import commands
from replit import db

from auxiliary import top_users
from db_utils import add_user, update_user, user_exists, wipe
from web_server import persist

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

@bot.event
async def on_ready():
    wipe(False)
    print('gm - bot has been activated')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    raise error

@bot.command(aliases=['Gm', 'gM', 'GM'])
async def gm(ctx):
    user = str(ctx.author.id)

    if not user_exists(user):
        add_user(user)

    error = update_user(user)

    if error:
        await ctx.send(f'once per day only. try again tomorrow')
        await ctx.message.add_reaction('❌')
    else:
        await ctx.send(f'thank you for your business. your gm count is {db[user][0]}')
        await ctx.message.add_reaction('✅')

@bot.command(aliases=['Gmboard'])
async def gmboard(ctx):
    await ctx.send(embed=await top_users(bot, ctx))

persist()
bot.run(os.environ['TOKEN'])
