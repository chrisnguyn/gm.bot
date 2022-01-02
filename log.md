okay so i don't know how to sync my repl.it repo with this github repo but anyways

<h3>02/01/2022</h3>

- okay so someone suggested the idea of resetting the cooldown at midnight instead of actually having to wait 86,400 seconds. i agreed that it was a good idea
- so two things, one, how do we do that - how can we make users on a cooldown then reset it at midnight? and two, how can we schedule python code to run at a specific time, everyday?
- for the first problem it's actually pretty simple. as users use the command, we can add their ID to a set. if someone tries to use the command, check if their ID is in that set or not. at midnight, clear the set (which ties into problem two)
- we can use the schedule library to schedule jobs, but the problem is that all examples that use the library use it on the main thread. the `while True` part will block the main thread and you'd never turn on the bot, so to alleviate that, we can spin up another thread similar to how we did for running a web server
- also to avoid circular imports and for general overall quality of life, moved all database logic into its own utility file and same thing for any utility functions related to cooldowns

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
