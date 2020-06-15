import unittest
import utils
import player
import config
import mysql.connector
import inventory


class UtilsTest(unittest.TestCase):
    """This TestCase test the utils module"""

    def setUp(self):
        self.cnx = mysql.connector.connect(
            user=config.user,
            password=config.word,
            host=config.ip,
            database='Enderbot')
        self.cnx.autocommit = True

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
        resources_of_player = {"stone": "100", "pp": "90", "ruby": "30", "emerald" : "0"}

        user = player.Player()
        user.cnx = self.cnx
        user.inventory = inventory.Inventory()
        user.inventory.resources = resources_of_player
        self.assertTrue(utils.player_has_resources(user, numbers_to_verify_2)
                        and not utils.player_has_resources(user, numbers_to_verify_1))

