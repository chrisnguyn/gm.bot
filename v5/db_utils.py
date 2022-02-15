import time
from datetime import datetime
from replit import db

def add_user(user):  # [count, streak, last_successful_invocation]
    db[user] = [0, 0, 0]

def update_user(user):
    curr_time = round(time.time()) - (3600 * 5)  # to turn GMT to EST, subtract 5 hours
    day_number = int(datetime.utcfromtimestamp(curr_time).strftime('%d'))

    if day_number == db[user][2]:
        return -1
    else:
        db[user][0] = db[user][0] + 1  # increment count

        if db[user][2] == day_number + 1:  # increment streak
            db[user][1] = db[user][1] + 1
        else:
            db[user][1] = 1
        
        db[user][2] = day_number  # set last successful invocation

def user_exists(user):
    return user in db.keys()

def migrate(trigger):  # use this to change db model while preserving user data
    if trigger:
        for user in db:
            count, streak, last_used = db[user][0], db[user][1], db[user][2]
            db[user] = []  # make this anything to change db values

def wipe(trigger):
    if trigger:
        for key in db.keys():
            del db[key]
