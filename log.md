okay so i don't know how to sync my repl.it repo with this github repo but anyways

<h3>01/06/2022</h3>

- so i had a separate thread that controlled a scheduler, idk what was going on but it kept bugging out. it was supposed to reset all cooldowns at midnight but people kept being able to use the command twice, maybe even more, in a day
- maybe it was the same original problem of doing a @cooldown on a user for 86,400 seconds? the 'thread' or 'process' holding onto it would die?
- anyways, found out a better way of tracking who is on cooldown, and bonus points, even if you turn the bot off and on it'll persist the cooldowns
- database now stores (count, DAY of the last successful invocation)
- we used this implementation before, and it was actually really good at its job. it kept the 86,400 second cooldown perfectly, but the problem was that if you gm'd at 7pm, you couldn't gm again until 7:01pm the next day
- the solution? we can take the current time (time.time()) and get the DAY NUMBER - as in right now the unix timestamp is '1641450606' which equates to '06', so before we kept a database of { user_id : [count, last successful invocation timestamp] }
- now what we'll do instead is keep a database of { user : [count, last successful invocation DAY] }

```python
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
```

```python
def add_user(user):
    db[user] = [0, float('-inf')]

def update_user(user):
    curr_time = round(time.time())
    day_number = datetime.utcfromtimestamp(curr_time).strftime('%d')

    if day_number == db[user][1]:
        return -1
    else:
        db[user][0] = db[user][0] + 1
        db[user][1] = day_number
```

<h3>01/02/2022</h3>

- okay so someone suggested the idea of resetting the cooldown at midnight instead of actually having to wait 86,400 seconds. i agreed that it was a good idea
- so two things, one, how do we do that - how can we make users on a cooldown then reset it at midnight? and two, how can we schedule python code to run at a specific time, everyday?
- for the first problem it's actually pretty simple. as users use the command, we can add their ID to a set. if someone tries to use the command, check if their ID is in that set or not. at midnight, clear the set (which ties into problem two)
- we can use the schedule library to schedule jobs, but the problem is that all examples that use the library use it on the main thread. the `while True` part will block the main thread and you'd never turn on the bot, so to alleviate that, we can spin up another thread similar to how we did for running a web server
- also to avoid circular imports and for general overall quality of life, moved all database logic into its own utility file and same thing for any utility functions related to cooldowns
- also added a new command, leaderboard. tracks top 10 users. reminds me of top K elements from leetcode. guess it taught me something after all. having to pass the `bot` and `ctx` object around though, really makes me wonder if there's a better way of doing it

```python
# main.py

@bot.command(aliases=['Gm', 'gM', 'GM'])
async def gm(ctx):
    user = str(ctx.author.id)

    if not user_exists(user):
        add_user(user)
    
    if user in users_on_cooldown:
        # bad - prevent command
    else:
        # good - update user in database and add their ID to the cooldown set
```

```python
# cooldown_utils.py

users_on_cooldown = set()

def watcher():
    while True:
        schedule.run_pending()

def reset_cooldowns():
    users_on_cooldown.clear()

schedule.every().day.at('00:00').do(reset_cooldowns)

def overwatch():
    t = Thread(target=watcher)
    t.start()
```

```python
# auxiliary.py

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
```

<h3>12/29/2021</h3>

- i originally had a `@commands.cooldown(1, 86400, commands.BucketType.user)`, but this isn't good for anything over 1 hour. the process holding onto it for 86k seconds will die eventally
- repl.it database is a simple `key : value` store and you only get one, so i was already using it for `{ user_id : count }`
- i updated it to be an array of data, so now we have `{ user_id : (count, last_successful_invocation) }`
- when a user calls the command i'll store the timestamp of last successful, if it was < 86_400
- ok cool

```python
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
```

```python
def query_db(user):
    if user in db.keys():
        time_diff = time.time() - db[user][1]

        if time_diff < 86_400:
            return 86_400 - round(time_diff)
        else:
            db[user][0], db[user][1] = db[user][0] + 1, time.time()
    else:
        db[user] = [1, time.time()]
```
