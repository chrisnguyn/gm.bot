okay so i don't know how to sync my repl.it repo with this github repo but anyways

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
