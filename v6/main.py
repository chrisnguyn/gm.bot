import os
import discord
import db_utils as dbu
from replit import db
from discord.ext import commands
from auxiliary import top_users
from web_server import persist


bot = commands.Bot(command_prefix='', intents=discord.Intents.default())

@bot.event
async def on_ready():
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


# @commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(aliases=['Gm', 'GM'])
async def gm(ctx):
    user_id, guild_id = ctx.author.id, ctx.guild.id
    key = str((user_id, guild_id))

    if not dbu.user_exists(key):
        dbu.add_user(key)

    error = dbu.update_user(key)

    if error:
        await ctx.send(f'once per day only. try again tomorrow')
        await ctx.message.add_reaction('❌')
    else:
        await ctx.send(f'thank you for your patronage. your gm count is **{db[key][dbu.Db.COUNT.value]}** and streak is **{db[key][dbu.Db.STREAK.value]}**')
        await ctx.message.add_reaction('✅')


# @commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(aliases=['Gmself'])
async def gmself(ctx):
    user_id, guild_id = ctx.author.id, ctx.guild.id
    key = str((user_id, guild_id))

    if not dbu.user_exists(key):
        await ctx.send(f'no record of you saying gm')
        await ctx.message.add_reaction('❌')
    else:
        await ctx.send(f'count: **{db[key][dbu.Db.COUNT.value]}** \nstreak: **{db[key][dbu.Db.STREAK.value]}**')
        await ctx.message.add_reaction('✅')


# @commands.cooldown(1, 60, commands.BucketType.guild)
@bot.command(aliases=['Gmboard'])
async def gmboard(ctx):
    await ctx.send(embed = await top_users(bot, ctx))

persist()
bot.run(os.environ['TOKEN'])
