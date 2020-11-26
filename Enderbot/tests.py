import unittest
import utils
import player
import config
import mysql.connector
import inventory
import discord
import trading
import values
import aiounittest
import errors
import datetime
import tower
import crafting


class FalseUser:
    def __init__(self, id):
        self.id = id
        self.created_at = None


class Tests(aiounittest.AsyncTestCase):
    """This TestCase test the utils module"""

    def setUp(self):
        self.cnx = mysql.connector.connect(
            user=config.user,
            password=config.password,
            host=config.ip,
            database='Enderbot',
            use_pure=True)
        self.cnx.autocommit = True
        utils.reset_account(self.cnx, 1)
        utils.reset_account(self.cnx, 2)
        values.load_json_files()
        values.generate_tower_data(self.cnx)

    def get_two_players(self) -> (player.Player, player.Player):
        """
        Return two player objects that are used for testing

        OUTPUT:
            - player.Player : The first player object
            - player.Player : The second player object
        """
        player_1 = player.Player(self.cnx, id=1)
        player_2 = player.Player(self.cnx, id=2)
        player_1.author = FalseUser(1)
        player_2.author = FalseUser(2)
        return player_1, player_2

    def test_format_number(self):
        """This function test if the conversion of number to the enderbot format work"""
        numbers = {"test": 567, "test1": 12345, "test2": 89656359, "test3": 1543762000, "test4": 230000987987654,
                   "test5": 74826386829634000}

        expected = {"test": "567", "test1": "12.34K", "test2": "89.66M", "test3": "1.54G", "test4": "230.0T",
                    "test5": '74.83P'}

        result = []
        self.assertEqual(utils.format_numbers(numbers), expected)

    def test_player_has_resources(self):
        """This function test if the function used to determine if a player has resources or not work."""
        numbers_to_verify_1 = {"emerald": "1", "ruby": "25"}
        result_1 = False
        numbers_to_verify_2 = {"stone": "97", "ruby": "20", "emerald": "0"}
        result_2 = True
        resources_of_player = {"stone": "100", "pp": "90", "ruby": "30", "emerald": "0"}

        user, _ = self.get_two_players()
        user.inventory.resources = resources_of_player
        self.assertTrue(user.has_resources(numbers_to_verify_2)
                        and not user.has_resources(numbers_to_verify_1))

    def test_given_trade_when_only_one_validation_the_trade_should_not_be_possible(self):
        sender, receiver = self.get_two_players()
        receiver.inventory.resources["pp"] = 2
        sender.inventory.resources["stone"] = 100
        trade = trading.Trade(sender, receiver, {"stone": 100}, {"pp": 2}, self.cnx)
        trade.mentioned_player_validation = True

        self.assertFalse(trade.is_possible())

    async def test_given_two_player_trade_when_both_validating_then_trade_should_happen(self):
        sender, receiver = self.get_two_players()
        receiver.inventory.resources["emerald"] = 100
        receiver.inventory.resources["pp"] = 2
        sender.inventory.resources["stone"] = 100

        given_resources = {"stone": "100"}
        received_resources = {"emerald": "100", "pp": "2"}
        trade = trading.Trade(sender, receiver, given_resources, received_resources, self.cnx)
        trade.mentioned_player_validation = True
        trade.trading_player_validation = True
        await trade.do_trade()

        sender, receiver = self.get_two_players()
        self.assertEqual(sender.inventory.resources["emerald"], 100)
        self.assertEqual(sender.inventory.resources["pp"], 2)
        self.assertEqual(receiver.inventory.resources["stone"], 100)

    async def test_given_two_player_trade_with_not_enough_resources_when_confirming_trade_the_trade_should_fail(self):
        sender, receiver = self.get_two_players()
        receiver.inventory.resources["emerald"] = 100
        sender.inventory.resources["stone"] = 100
        # Missing 2 pp

        given_resources = {"stone": "100"}
        received_resources = {"emerald": "100", "pp": "2"}
        trade = trading.Trade(sender, receiver, given_resources, received_resources, self.cnx)
        trade.mentioned_player_validation = True
        trade.trading_player_validation = True
        try:
            await trade.do_trade()
        except errors.NotEnoughResources as error:
            return

    def test_given_player_has_no_mana_when_mining_then_should_raise_error(self):
        user, _ = self.get_two_players()
        user.mana = 0
        user.author = None
        try:
            user.mine(1)
        except errors.NotEnoughManaForMining as error:
            return

    async def test_given_hourly_is_not_available_when_collecting_hourly_then_should_fail(self):
        user, _ = self.get_two_players()
        user.last_hourly_claim = datetime.datetime.now()
        begin_xp = user.xp
        begin_stone = user.inventory.resources["stone"]

        try:
            await user.hourly(None)
        except:
            pass
        user, _ = self.get_two_players()
        self.assertEqual(begin_xp, user.xp)
        self.assertEqual(begin_stone, user.inventory.resources["stone"])

    async def test_given_hourly_is_available_when_collecting_hourly_then_should_succed(self):
        user, _ = self.get_two_players()
        user.last_hourly_claim = datetime.datetime.now() + datetime.timedelta(hours=1, seconds=1)
        begin_xp = user.xp
        begin_stone = user.inventory.resources["stone"]

        try:
            await user.hourly(None)
        except:
            pass
        user, _ = self.get_two_players()
        self.assertNotEqual(begin_xp, user.xp)
        self.assertNotEqual(begin_stone, user.inventory.resources["stone"])

    async def test_given_daily_is_not_available_when_collecting_daily_then_should_fail(self):
        user, _ = self.get_two_players()
        begin_xp = user.xp
        user.last_daily_claim = datetime.datetime.now() + datetime.timedelta(days=1, seconds=1)
        user.last_hourly_claim = datetime.datetime.now() + datetime.timedelta(days=1,
                                                                              seconds=1)  # For some reasons, without this line, this test fail
        try:
            await user.daily(None)
        except:
            print("error")
            pass

        self.assertEqual(begin_xp, user.xp)

    async def test_given_daily_is_not_available_when_collecting_daily_then_should_succeed(self):
        user, _ = self.get_two_players()
        user._last_daily_claim = datetime.datetime.now() + datetime.timedelta(days=1, seconds=1)
        begin_xp = user.xp
        print(user.last_daily_claim)

        try:
            await user.daily(None)
        except:
            pass

        self.assertNotEqual(begin_xp, user.xp)

    async def test_given_rep_is_not_available_when_reputating_someone_then_should_fail(self):
        rep_sender, rep_receiver = self.get_two_players()
        false_user_1 = FalseUser(1)
        false_user_1.created_at = datetime.datetime.now() - datetime.timedelta(days=40)
        rep_sender.author = false_user_1
        rep_sender.last_reputation_claim = datetime.datetime.now()
        rep_sender.level = 10000
        begin_reputations = rep_receiver.reputations

        try:
            await rep_sender.send_rep_to(rep_receiver, None)
        except:
            pass

        self.assertEqual(rep_receiver.reputations, begin_reputations)

    async def test_given_rep_is_available_when_reputating_someone_then_should_succeed(self):
        rep_sender, rep_receiver = self.get_two_players()
        false_user_1 = FalseUser(1)
        false_user_1.created_at = datetime.datetime.now() - datetime.timedelta(days=40)
        rep_sender.author = false_user_1
        rep_sender.last_reputation_claim = datetime.datetime.now() - datetime.timedelta(days=2)
        rep_sender.level = 10000
        begin_reputations = rep_receiver.reputations

        try:
            await rep_sender.send_rep_to(rep_receiver, None)
        except:
            pass

        self.assertNotEqual(rep_receiver.reputations, begin_reputations)

    def test_given_player_has_100_stone_in_village_when_collecting_then_should_disapear_from_village_and_go_to_inventory(
            self):
        user, _ = self.get_two_players()
        user.village.stone_inside = 100
        user.village.last_claim = datetime.datetime.now()
        user.village.last_lookup = datetime.datetime.now()
        user.inventory.resources["stone"] = 0

        message = user.village.collect_stone()
        print(message)

        self.assertEqual(user.village.stone_inside, 0)
        self.assertEqual(user.inventory.resources["stone"], 100)

    def test_given_player_generated_resources_for_ten_hours_when_collecting_stone_then_stone_inside_should_be_zero_and_stone_in_inventory_greater_than_before_and_lookup_date_should_be_updated(
            self):
        user, _ = self.get_two_players()
        date_last = datetime.datetime.now() - datetime.timedelta(hours=10)
        user.village.last_claim = date_last
        user.village.last_lookup = date_last
        user.village.factories = 1
        begin_stone_in_inventory = user.inventory.resources["stone"]

        user.village.collect_stone()

        self.assertGreater(user.inventory.resources["stone"], begin_stone_in_inventory)
        self.assertEqual(user.village.stone_inside, 0)
        self.assertEqual(user.village.last_claim.replace(second=0, microsecond=0),
                         datetime.datetime.now().replace(second=0, microsecond=0))

    def test_given_having_one_rep_and_zero_inhabitants_when_recruiting_inhabitant_then_resources_should_disapear_and_there_should_be_one_inhabitant(
            self):
        user, _ = self.get_two_players()
        user.reputations = 1
        user.village.inhabitants = 0
        for (key, value) in values.villages_upgrades_costs["inhabitant"].items():
            user.inventory.resources[key] = value

        upgrade = user.village.upgrade_component("inhabitant")
        upgrade.do_upgrade()

        for key in values.villages_upgrades_costs["inhabitant"].keys():
            self.assertEqual(user.inventory.resources[key], 0)
        self.assertEqual(1, user.village.inhabitants)
        self.assertEqual(1, user.village.inhabitants)

    def test_given_having_one_rep_and_zero_inhabitants_and_not_enough_resources_when_recruiting_inhabitant_then_should_fail_and_inhabitant_should_be_one(
            self):
        user, _ = self.get_two_players()
        user.reputations = 1
        user.village.inhabitants = 0
        for key in values.villages_upgrades_costs["inhabitant"].keys():
            user.inventory.resources[key] = 3

        upgrade = user.village.upgrade_component("inhabitant")
        try:
            upgrade.do_upgrade()
        except:
            pass

        for key in values.villages_upgrades_costs["inhabitant"].keys():
            self.assertEqual(3, user.inventory.resources[key])
        self.assertEqual(0, user.village.inhabitants)

    def test_given_player_has_zero_rep_when_recruiting_then_should_fail(self):
        user, _ = self.get_two_players()
        user.reputations = 0
        user.village.inhabitants = 0

        try:
            upgrade = user.village.upgrade_component("inhabitant")
        except Exception as error:
            if isinstance(error, errors.CantUpgradeVillageComponent):
                self.assertTrue(True)
            else:
                self.assertTrue(False)

        self.assertEqual(0, user.village.inhabitants)

    def test_given_player_has_two_rep_and_enough_resources_when_recruiting_two_inhabitants_then_should_remove_proper_amount_and_should_have_two_inhabitants(
            self):
        user, _ = self.get_two_players()
        user.reputations = 2
        user.village.inhabitants = 0
        for key in values.villages_upgrades_costs["inhabitant"].keys():
            user.inventory.resources[key] = 20000000

        upgrade = user.village.upgrade_component("inhabitant", 2)
        upgrade.do_upgrade()

        for key in values.villages_upgrades_costs["inhabitant"].keys():
            self.assertEqual(0, user.inventory.resources[key])
        self.assertEqual(2, user.village.inhabitants)

    def test_given_player_has_pickaxe_level_zero_and_not_enough_resources_when_crafting_next_level_then_should_fail(
            self):
        user, _ = self.get_two_players()
        user.tools.pickaxe = 0
        user.inventory.resources["stone"] = 0
        craft = crafting.Craft(user, "pickaxe", self.cnx)

        try:
            craft.validate_craft()
        except errors.NotEnoughResources as error:
            pass

    def test_given_player_has_pickaxe_level_zero_and_enough_resources_when_crafting_next_level_then_should_succeed(self):
        user, _ = self.get_two_players()
        user.tools.pickaxe = 0
        user.inventory.resources["stone"] = 50

        craft = crafting.Craft(user, "pickaxe", self.cnx)
        craft.validate_craft()

        user, _ = self.get_two_players()
        self.assertEqual(0, user.inventory.resources["stone"])
        self.assertEqual(1, user.tools.pickaxe)

