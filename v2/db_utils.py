from replit import db

def add_user(user):
    db[user] = 0

def update_user(user):
    db[user] = db[user] + 1

def user_exists(user):
    return user in db.keys()

def wipe(active):
    if active:
        for key in db.keys():
            del db[key]
