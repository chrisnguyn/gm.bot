# not actually used in v3 - read blog

import schedule
import time
from threading import Thread

users_on_cooldown = set()

def watcher():
    schedule.every().day.at('05:00').do(reset_cooldowns)

    while True:
        schedule.run_pending()
        time.sleep(1)

def reset_cooldowns():
    users_on_cooldown.clear()

def overwatch():
    t = Thread(target=watcher)
    t.start()
