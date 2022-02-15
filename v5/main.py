import os

import discord
from discord.ext import commands
from replit import db

from auxiliary import top_users
from db_utils import add_user, update_user, user_exists, migrate, wipe
from web_server import persist

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

@bot.event
async def on_ready():
    migrate(False)
    wipe(False)
    print('gm - bot has been activated')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'using command too soon. try again in {round(error.retry_after)} seconds')
        await ctx.message.add_reaction('❌')
    else:
        raise error

@commands.cooldown(1, 600, commands.BucketType.user)
@bot.command(aliases=['Gm', 'GM'])
async def gm(ctx):
    user = str(ctx.author.id)

    if not user_exists(user):
        add_user(user)

    error = update_user(user)

    if error:
        await ctx.send(f'once per day only. try again tomorrow')
        await ctx.message.add_reaction('❌')
    else:
        await ctx.send(f'thank you for your patronage. your gm count is **{db[user][0]}** and streak is **{db[user][1]}')
        await ctx.message.add_reaction('✅')

@commands.cooldown(1, 600, commands.BucketType.user)
@bot.command(aliases=['Gmself'])
async def gmself(ctx):
    user = str(ctx.author.id)

    if not user_exists(user):
        await ctx.send(f'no record of you saying gm')
        await ctx.message.add_reaction('❌')
    else:
        await ctx.send(f'gm count: **{db[user][0]}** \nstreak: **{db[user][1]}**')
        await ctx.message.add_reaction('✅')

@commands.cooldown(1, 600, commands.BucketType.guild)
@bot.command(aliases=['Gmboard'])
async def gmboard(ctx):
    await ctx.send(embed=await top_users(bot, ctx))

persist()
bot.run(os.environ['TOKEN'])
