import heapq
from replit import db

async def top_users(bot, ctx):  # has to be a better way than passing stuff around all the time
    min_heap = []

    i = 0
    for key in db.keys():
        heapq.heappush(min_heap, (db[key], i, int(key)))
        i += 1

        if len(min_heap) > 10:
            heapq.heappop(min_heap)

    msg = ''

    j = len(min_heap)
    while min_heap:
        count, _, user_id = heapq.heappop(min_heap)
        msg = f'{j}. {await bot.fetch_user(user_id)} with a count of {count} \n' + msg
        j -= 1

    return msg
