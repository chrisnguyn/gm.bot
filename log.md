okay so i don't know how to sync my repl.it repo with this github repo but anyways

<h2>02/28/2022</h2>

- okay this one is going to be a fucking nightmare. right now gm.bot is only used in one discord server, but i want to use him in another; why is this an issue? because users in serverA will show up on the leaderboard for serverB, and so on
- this is because this is the database:

```
{
    user_id : [count, streak, last_day]
}
```

- there's no discerning between servers. what can we do? add the server id into the values, right? so last night i attempted this:

```
{
    user_id : [server_id, count, streak, last_day]
}
```

- why is this an issue? because i had one, update a bunch of functions. for example, 'user_exists'. i changed it to something like this;

```
for key in db:
    if key == user and user[0] == guild:
        return True
    
    return False
```

- this is a BIG problem. because, if a user didn't exist, i added them. `db[user] = [server, 0, 0, 0]`, right? well...if you were in serverA, you just got deleted. you're now in serverB, though. KEYS WERE GETTING REPLACED IN THE DATABASE
- i needed to make it part of the key, so i had two options

```
{
    (user_id, server_id) : []
}
```

or

```
{
    serverA : {
        user1 : []
    },

    serverB : {
        user1 : []
    }
}
```

- honestly option 2 is the best one but under a time constrain i went with option 1 since i have like 2 midterms this week lol
- yeah i had to do a lot of other updates for functions since i totally revamped the schema, getting the top users was a little hard as well. keys are saved as STRINGS in replit db, so i had to split, check if the 2nd element is the same server as where it was invoked, etc.
- big mess. definitely not my best software engineering work. it's all working in the end though which is good
- also added enums to make code a little cleaning
- LOTS of migration work to be done

```python
def migrate(ctx):  # from user : [] -> (user, guild) : []
    current_users = []
    curr_time = round(time.time()) - (3600 * 5)
    day_num = curr_time // 86_400

    for user in db:
        count, streak, last_day = db[user][0], db[user][1], db[user][2]
        current_users.append((user, count, streak, last_day))

    for user in db:
        del db[user]

    for user_id, count, streak, last_day in current_users:
        key = (user_id, str(ctx.guild.id))
        db[key] = [count, streak, day_num]

    for key in db:
        print(f'{key} - {db[key]}')
```

- one other VERY LARGE issue i overlooked, since today is february 28, tomorrow on march 1, all streaks were going to be lost. this is because the way i currenty check is, i grab the timestamp and see what day of the month it is. today would be '28'. then when a user does gm, i check their data. was the last time they used the command, today - 1? did they use it on 27? if so, streak += 1.

- tomorrow is march 1. i would grab 1. 1 - 1 != 28, so everyone was going to lose their streaks.

- instead i went with "how many days has it been since the epoch" so i don't have to worry about months turning over, it's a continuously number counting up (19051, 19052, 19053, ...)


<h2>02/15/2022</h2>

- added streaks. had to update the database schema from [count, last_successful_invocation] to [count, streak, last_successful_invocation], and when a user uses 'gm' i just check to see if 'today' is equal to 'last_successful + 1'. if it is, streak += 1. otherwise, streak = 1
- no 'cooldowns_util.py' in v5 since we handle the cooldown in db_utils
- how do we change the database schema (port over to the new model) without losing everyone's data? historically i always just dropped everyone's data and reinitialized it, but some people have daily counts of 40 and 50, so i don't think they'll be too happy if they lost it
- i ran a migrate() function where it goes over all the keys in the DB and reinitializes it

```python
# db[user] = [count, last_used]
# db[user] = [count, streak, last_used]

def migrate():
    for user in db:
        count, last_used = db[user][0], db[user][1]
        db[user] = [count, 0, last_used]
```


<h2>01/07/2022</h2>

- okay so, i thought it was perfect, but it wasn't. resets are happening at 7:00pm - why so specific? because that's 12:00am in GMT. i didn't account for timezones when doing the reset! simple fix, just subtract 5 hours and we'll turn it to EST
- also, next issue, rate limits. the people in this discord are monsters, so we'll just slap 10 minute timeouts on 'gm' for a user, and a 10 minute server wide cooldown for gmboard


<h2>01/06/2022</h2>

- so i had a separate thread that controlled a scheduler, idk what was going on but it kept bugging out. it was supposed to reset all cooldowns at midnight but people kept being able to use the command twice, maybe even more, in a day
- maybe it was the same original problem of doing a @cooldown on a user for 86,400 seconds? the 'thread' or 'process' holding onto it would die?
- anyways, found out a better way of tracking who is on cooldown, and bonus points, even if you turn the bot off and on it'll persist the cooldowns
- database now stores (count, DAY of the last successful invocation)
- we used this implementation before, and it was actually really good at its job. it kept the 86,400 second cooldown perfectly, but the problem was that if you gm'd at 7pm, you couldn't gm again until 7:01pm the next day
- the solution? we can take the current time (time.time()) and get the DAY NUMBER - as in right now the unix timestamp is '1641450606' which equates to '06', so before we kept a database of { user_id : [count, last successful invocation timestamp] }
- now what we'll do instead is keep a database of { user : [count, last successful invocation DAY] }

```python
@commands.cooldown(1, 600, commands.BucketType.user)

@commands.cooldown(1, 600, commands.BucketType.guild)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'using command too soon. try again in {round(error.retry_after)} seconds')
```

```python
def update_user(user):
    curr_time = round(time.time()) - (3600 * 5)  # turn GMT to EST, subtract 5 hours
    day_number = datetime.utcfromtimestamp(curr_time).strftime('%d')

    if day_number == db[user][1]:
        return -1
    else:
        db[user][0] = db[user][0] + 1
        db[user][1] = day_number
```

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


<h2>01/02/2022</h2>

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


<h2>12/29/2021</h2>

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
