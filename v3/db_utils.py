import time
from datetime import datetime
from replit import db

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

def user_exists(user):
    return user in db.keys()

def wipe(trigger):
    if trigger:
        for key in db.keys():
            del db[key]
