import discord
import heapq
from replit import db

async def top_users(bot, ctx):  # has to be a better way than passing stuff around all the time
    message = ''
    min_heap = []

    for key in db.keys():
        heapq.heappush(min_heap, (db[key][0], int(key)))

        if len(min_heap) > 10:
            heapq.heappop(min_heap)

    i = len(min_heap)
    while min_heap:
        count, user_id = heapq.heappop(min_heap)
        message = f'{i}) {await bot.fetch_user(user_id)} with a count of {count} \n' + message
        i -= 1

    embed = discord.Embed(title='gm.bot leaderboard', color=0x87CEEB)
    embed.add_field(name='Users', value=message, inline=False)
    return embed
