import heapq
from replit import db

async def top_users(bot, ctx):  # has to be a better way than passing stuff around all the time right
    min_heap = []

    i = 0
    for key in db.keys():
        heapq.heappush(min_heap, (db[key], i, int(key)))
        i += 1

        if len(min_heap) > 10:
            heapq.heappop(min_heap)
    
    msg = ''

    for count, _, user_id in min_heap:
        msg += f'{i} - {await bot.fetch_user(user_id)} with count of {count}'
    
    return msg
