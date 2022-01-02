import schedule
import time
from threading import Thread

users_on_cooldown = set()

def watcher():
    while True:
        schedule.run_pending()
        time.sleep(300)

def reset_cooldowns():
    print(f'cooldowns have been reset: {round(time.time())}')
    users_on_cooldown.clear()

def job():
    print(f'time is: {round(time.time())}')

schedule.every().day.at('00:00').do(reset_cooldowns)
schedule.every(1).hour.do(job)

def overwatch():  # multithreading yay. don't block the main thread or the bot won't run
    t = Thread(target=watcher)
    t.start()
