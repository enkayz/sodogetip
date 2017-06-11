import datetime
import json
import random
from tinydb import TinyDB, Query

import bot_logger
from config import bot_config, DATA_PATH


# read file
def get_users():
    with open(DATA_PATH + bot_config['user_file'], 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            bot_logger.logger.warning("Error on read user file")
            data = {}
        return data

# read file
def get_multisig_users():
    with open(DATA_PATH + bot_config['user_file'], 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            bot_logger.logger.warning("Error on read user file")
            data = {}
        return data

# save to file:
def add_user(user, address):
    bot_logger.logger.info("Add user " + user + ' ' + address)
    data = get_users()
    with open(DATA_PATH + bot_config['user_file'], 'w') as f:
        data[user] = address
        json.dump(data, f)


def mutisig_enabled(username, type_multisig):
    db = TinyDB(DATA_PATH + bot_config['multisig_user'])
    table = db.table(username)
    User = Query()
    return table.search(User.type == type_multisig)

def get_user_address(user):
    multi = mutisig_enabled(user, "1of2")
    if multi[0]['enabled']:
        return multi[0]['address']
    else:
        user_list = get_users()
        return user_list[user]


def user_exist(user):
    user_list = get_users()
    if user in user_list.keys():
        return True
    else:
        return False


def get_unregistered_tip():
    db = TinyDB(DATA_PATH + bot_config['unregistered_tip_user'])
    data = db.all()
    db.close()
    return data


def save_unregistered_tip(sender, receiver, amount, message_fullname):
    bot_logger.logger.info("Save tip form %s to %s " % (sender, receiver))
    db = TinyDB(DATA_PATH + bot_config['unregistered_tip_user'])
    db.insert({
        'id': random.randint(0, 99999999),
        'amount': amount,
        'receiver': receiver,
        'sender': sender,
        'message_fullname': message_fullname,
        'time': datetime.datetime.now().isoformat(),
    })
    db.close()


def remove_pending_tip(id_tip):
    db = TinyDB(DATA_PATH + bot_config['unregistered_tip_user'])
    tip = Query()
    db.remove(tip.id == id_tip)
    db.close()


def get_balance_unregistered_tip(user):
    pending_tips = []

    list_tip_unregistered = get_unregistered_tip()
    if list_tip_unregistered:
        for tip in list_tip_unregistered:
            if tip['sender'] == user:
                pending_tips.append(int(tip['amount']))

    return int(sum(pending_tips))


def save_multisig(username, multisig, type="1of2"):
    db = TinyDB(DATA_PATH + bot_config['multisig_user'])
    table = db.table(username)
    table.insert({
        'address': multisig['address'],
        'redeemscript': multisig['redeemScript'],
        'type': type,
        'enabled': True,
    })
    db.close()
