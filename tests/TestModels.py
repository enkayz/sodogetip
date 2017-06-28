import datetime
import unittest

import config
import models
import user_function
from MockRpc import MockRpc


class TestTip(unittest.TestCase):
    def test_tip_simple(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " 100 doge", None)
        self.assertEqual(100, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(False, tip.verify)

    def test_tip_simpl_float_comma(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " 10,8 doge", None)
        self.assertEqual(10, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(False, tip.verify)

    def test_tip_simple_float_dot(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " 10.8 doge", None)
        self.assertEqual(10, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(False, tip.verify)

    def test_tip_simple_verify(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " 100 doge verify", None)
        self.assertEqual(100, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(True, tip.verify)

    def test_tip_random(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " random100 doge", None)
        self.assertLess(tip.amount, 100)
        self.assertGreater(tip.amount, 1)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(False, tip.verify)

    def test_tip_roll(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " roll doge verify", None)
        self.assertLessEqual(tip.amount, 6)
        self.assertGreaterEqual(tip.amount, 1)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(True, tip.verify)

    def test_tip_flip(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " flip doge verify", None)
        self.assertLessEqual(tip.amount, 2)
        self.assertGreaterEqual(tip.amount, 1)
        self.assertEqual("doge", tip.currency)
        self.assertEqual(True, tip.verify)

    def test_tip_dogecar(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " dogecar doge verify", None)
        self.assertEqual(tip.amount, config.tip_keyword['dogecar'])
        self.assertEqual("doge", tip.currency)
        self.assertEqual(True, tip.verify)

    def test_tip_random_verify(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " random10000 doge", None)
        self.assertLess(tip.amount, 10000)
        self.assertGreater(tip.amount, 1)
        self.assertEqual("doge", tip.currency)
        if tip.amount >= 1000:
            self.assertEqual(True, tip.verify)

    def test_tip_user_mention(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " /u/just-an-dev 1000 doge", None)
        self.assertEqual(1000, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual("just-an-dev", tip.receiver.username)

    def test_tip_user_mention_add(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " +/u/just-an-dev 1000 doge", None)
        self.assertEqual(1000, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual("just-an-dev", tip.receiver.username)

    def test_tip_user_mention_at(self):
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " @just-an-dev 1000 doge", None)
        self.assertEqual(1000, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual("just-an-dev", tip.receiver.username)

    def test_tip_address(self):
        mock_rpc = MockRpc()
        tip = models.Tip()
        tip.parse_message("+/u/" + config.bot_name + " nnBKn39onxAuS1cr6KuLAoV2SdfFh1dpsR 1000 doge", mock_rpc)
        self.assertEqual(1000, tip.amount)
        self.assertEqual("doge", tip.currency)
        self.assertEqual("nnBKn39onxAuS1cr6KuLAoV2SdfFh1dpsR", tip.receiver.address)

    def test_tip_not_expired(self):
        tip = models.Tip()
        tip.time = datetime.datetime.now()
        self.assertEqual(False, tip.is_expired())

    def test_tip_expired(self):
        tip = models.Tip()
        tip.time = datetime.datetime.now() - datetime.timedelta(days=5)
        self.assertEqual(True, tip.is_expired())

    def test_tip_unregistered(self):
        list_tips = user_function.get_unregistered_tip()

        tip = models.Tip().create_from_array(list_tips[0])
        self.assertEqual(True, tip.is_expired())


class TestUser(unittest.TestCase):
    def test_user_is_registered(self):
        user = models.User("just-an-dev")
        self.assertEqual("nnBKn39onxAuS1cr6KuLAoV2SdfFh1dpsR", user.address)
        self.assertEqual(True, user.is_registered())

    def test_user_exist(self):
        u1 = models.User('just-an-dev')
        u2 = models.User('Just-An-dEv')
        self.assertEqual(True, u1.is_registered())
        self.assertEqual(False, u2.is_registered())

        self.assertEqual(True, user_function.user_exist('just-an-dev'))
        self.assertEqual(True, user_function.user_exist('Just-An-dEv'))

    def test_user_not_exist(self):
        user = models.User("doge")
        self.assertEqual(None, user.address)
        self.assertEqual(False, user.is_registered())

    def test_user_exist_by_addr(self):
        user = models.User("doge")
        user.address = "nnBKn39onxAuS1cr6KuLAoV2SdfFh1dpsR"
        self.assertEqual("nnBKn39onxAuS1cr6KuLAoV2SdfFh1dpsR", user.address)
        self.assertEqual(True, user.is_registered())

    def test_unregistered_tip_empty(self):
        user = models.User("doge")
        self.assertEqual(0, user.get_balance_unregistered_tip())

    def test_unregistered_tip(self):
        user = models.User("just-an-dev")
        self.assertEqual(1000, user.get_balance_unregistered_tip())


if __name__ == '__main__':
    unittest.main()
