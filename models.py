import datetime
import random
import re

import bot_logger
import config
import crypto
import user_function
import utils


class Tip(object):
    """Class to represent a tip of user"""

    def __init__(self):
        self.receiver = None
        self.amount = None
        self.verify = False
        self.currency = None
        self.sender = None
        self.finish = False
        self.status = None
        self.tx_id = None

        self.id = random.randint(0, 99999999)
        # reddit message id
        self.message_fullname = None,
        self.time = datetime.datetime.now().isoformat()

    def parse_message(self, message_to_parse, rpc=None):
        if rpc is None:
            # init rpc to validate address
            rpc = crypto.get_rpc()

        p = re.compile(
            '(\+\/u\/' + config.bot_name + ')\s?(@?[0-9a-zA-Z-_\/\+]+)?\s+(\d+|[0-9a-zA-Z,.]+)\s(doge)\s?(verify)?',
            re.IGNORECASE)
        m = p.search(message_to_parse.strip())
        # Group 1 is +/u/sodogetiptest
        # Group 2 is either blank(tip to the commentor), an address, or a user
        self.receiver = m.group(2)
        # Group 3 is the tip amount in integers(ex.  100) or a word(ex.roll)
        self.amount = m.group(3).replace(',', '.')
        # Group 4 is doge
        self.currency = m.group(4)
        # Group 5 is either blank(no verify message) or verify(verify message)
        self.verify = True if (m.group(5) == "verify") else False

        if self.receiver is not None:
            # to support send tip to username
            if '+/u/' in self.receiver:
                self.receiver = User(self.receiver[4:])
            elif '/u/' in self.receiver:
                self.receiver = User(self.receiver[3:])
            elif 'u/' in self.receiver:
                self.receiver = User(self.receiver[2:])
            elif '@' in self.receiver:
                self.receiver = User(self.receiver[1:])
            # to support send tip to an address
            elif len(self.receiver) == 34 and rpc.validateaddress(self.receiver)['isvalid']:
                address = self.receiver
                bot_logger.logger.info("Send an tip to address")
                self.receiver = User("address-" + address)
                self.receiver.address = address

        # to support any type of randomXXX amount
        if 'random' in self.amount and utils.check_amount_valid(self.amount[6:]):
            self.amount = random.randint(1, int(self.amount[6:]))

        # here amount is numeric, make magic to support not whole tips
        if utils.check_amount_valid(self.amount):
            self.amount = round(float(self.amount) - 0.5)

        # if amount is all, get balance
        if self.amount == 'all':
            # get user balance
            self.amount = crypto.get_user_spendable_balance(self.sender.address, rpc)

        bot_logger.logger.debug("isinstance self.amount = %s" % str(isinstance(self.amount, str)))
        bot_logger.logger.debug("type self.amount = %s" % str(type(self.amount)))

        if type(self.amount) is unicode or type(self.amount) is str:
            bot_logger.logger.debug("self.amount is str")
            if self.amount == "roll":
                self.amount = random.randint(1, 6)

            elif self.amount == "flip":
                self.amount = random.randint(1, 2)

            elif self.amount in config.tip_keyword.keys():
                self.amount = config.tip_keyword[self.amount]

        bot_logger.logger.debug("self.amount = %s" % str(self.amount))

        # if tip is over 1000 doge set verify
        if float(self.amount) >= float(1000):
            self.verify = True

    def set_sender(self, sender_username):
        self.sender = User(sender_username)

    def set_receiver(self, receiver_username):
        # update only if previous is blank (other case it will be set in parse_message)
        if self.receiver is None:
            self.receiver = User(receiver_username)

    def get_value_usd(self):
        return utils.get_coin_value(self.amount)

    def create_from_array(self, arr_tip):
        # import user

        self.receiver = User(arr_tip['receiver'])
        self.sender = User(arr_tip['sender'])

        self.id = arr_tip['id']
        self.amount = arr_tip['amount']

        if 'message_fullname' in arr_tip.keys():
            self.message_fullname = arr_tip['message_fullname']

        if 'finish' in arr_tip.keys():
            self.finish = arr_tip['finish']

        if 'tx_id' in arr_tip.keys():
            self.tx_id = arr_tip['tx_id']

        if 'status' in arr_tip.keys():
            self.status = arr_tip['status']

        self.time = arr_tip['time']

        return self

    def is_expired(self):
        limit_date = datetime.datetime.now() - datetime.timedelta(days=3)

        if type(self.time) is str:
            return limit_date > datetime.datetime.strptime(self.time, '%Y-%m-%dT%H:%M:%S.%f')

        if type(self.time) is datetime.datetime:
            return limit_date > self.time

        if type(self.time) is unicode:
            return limit_date > datetime.datetime.strptime(self.time, '%Y-%m-%dT%H:%M:%S.%f')


class User(object):
    """Class to represent an user"""

    def __init__(self, user):
        self.username = user
        self.address = None

        if user_function.user_exist(self.username):
            self.address = user_function.get_user_address(self.username)

    def is_registered(self):
        # if user have address it's registered
        if self.address is not None:
            return True
        else:
            return False

    # get total of tips send to users who are not registered
    def get_balance_unregistered_tip(self):
        return user_function.get_balance_unregistered_tip(self.username)

    # user CONFIRMED balance
    def get_balance_confirmed(self):
        # check if user have pending tips
        pending_tips = self.get_balance_unregistered_tip()
        bot_logger.logger.debug("pending_tips %s" % (str(pending_tips)))

        return crypto.get_user_confirmed_balance(self.address) - int(pending_tips)

    # user UN-CONFIRMED balance
    def get_balance_unconfirmed(self):
        return crypto.get_user_unconfirmed_balance(self.address)

    def get_new_address(self):
        # create a new simple address
        rpc = crypto.get_rpc()
        self.address = rpc.getnewaddress("reddit-%s" % self.username)

        # todo : register in users table
