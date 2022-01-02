import os
import discord
from discord.ext import commands
from replit import db
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

def update_db(user):
    if user not in db.keys():
        db[user] = 0
    db[user] = db[user] + 1

def wipe():
    for key in db.keys():
        del db[key]

@bot.event
async def on_ready():
    # wipe()
    print('bot has been activated')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'once per day only. use again in {round(error.retry_after)} seconds')

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def gm(ctx):
    user = str(ctx.author.id)
    update_db(user)
    await ctx.send(f'your gm count is {db[user]}')
    await ctx.message.add_reaction('✅')

keep_alive()
bot.run(os.environ['TOKEN'])
