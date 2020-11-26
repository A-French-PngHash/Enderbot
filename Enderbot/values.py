import json
import tower

bot_id = 719857024304676955
author_id = 441881039338471425  # This id the id of my discord account. Used to verify if a command is executed by me
bot_token = "NzE5ODU3MDI0MzA0Njc2OTU1.XuEcDQ.Lijnj9BqFdgAcei0ZyWGGh8kO8o"

help_pages_color = 0x565656
number_of_shards = 5
resources_name_in_database = ["stone", "pp", "am", "iron", "gold", "obsidian", "ruby", "sapphire",
                              "emerald", "cobalt", "mithril", "adamantite"]
resources_name_for_user = ["Stone", "Perfect Prism", "Antimatter", "Iron", "Gold", "Obsidian", "Ruby", "Sapphire",
                           "Emerald", "Cobalt", "Mithril", "Adamantite"]
max_factories = 10000
# The list contain the resources name that will be displayed for users.

emojis = {"xp": "<:xp:720659625342402632>",
          "hp": "❤",
          "mana": "⭐",
          "energy" : "⚡",
          "pickaxe": "⛏️",
          "house": "🏡",
          "ring": "💍",
          "shield": "🛡️",
          "sword": "⚔️",
          "thecat": "<:thecat:728222277732270111>",
          "Stone": "<:stone:720659627934613626>",
          "Perfect Prism": "<:pp:720659626814865469>",
          "Antimatter": "<:am:720659633295065140>",
          "Iron": "<:iron:720659628215762995>",
          "Gold": "<:gold:720659632628170792>",
          "Obsidian": "<:obsidian:720659632212934697>",
          "Ruby": "<:ruby:720659626260955196>",
          "Sapphire": "<:sapphire:720659632154083420>",
          "Emerald": "<:emerald:720659625875210290>",
          "Cobalt": "<:cobal:720659631290056795>",
          "Adamantite": "<:adamantite:720659629058687086>",
          "Mithril": "<:mithril:720659629759004712>",
          "boss": ":skull:",
          "up_door": ":arrow_double_up:",
          "down_door": ":arrow_double_down:",
          "player": ":white_check_mark:",
          "black_tile": ":black_large_square:",
          "white_tile": ":white_large_square:"
          }
"""
This dictionary contain all the emojis that are used in the bot.
To make it work for you you need to add all the enderbot emojis in a server. You can then replace the id by the new 
emoji's id. You can eventually replace their name.
The key for emoji corresponding to resources is the name of the resource formatted for user.
"""

resources_drop_rate = {
    "stone": 50,
    "pp": 2,
    "am": 0.2,
    "iron": 15,
    "gold": 5,
    "obsidian": 5,
    "ruby": 5.6,
    "sapphire": 5.6,
    "emerald": 5.6,
    "cobalt": 3,
    "mithril": 2,
    "adamantite": 1
}
"""Resources drop rate in percentage."""

resources_xp_min = {
    "stone": 2,
    "pp": 10,
    "am": 15,
    "iron": 4,
    "gold": 6,
    "obsidian": 6,
    "ruby": 6,
    "sapphire": 6,
    "emerald": 6,
    "cobalt": 6,
    "mithril": 6,
    "adamantite": 6
}
"""Resources minimal xp drop."""

villages_upgrades_costs = {
    "inhabitant": {"iron": 10000000, "gold": 10000000, "obsidian": 10000000},
    "academy": {"emerald": 10000000, "sapphire": 10000000, "ruby": 10000000},
    "factory": {"cobalt": 10000000, "mithril": 10000000, "adamantite": 10000000}
}

number_correspond_to_resource = {
    "1": "stone",
    "2": "iron",
    "3": "gold",
    "4": "obsidian",
    "5": "ruby",
    "6": "emerald",
    "7": "sapphire",
    "8": "cobalt",
    "9": "mithril",
    "10": "adamantite",
    "11": "pp",
    "12": "am"
}
"""
When loading the costs of an upgrade from the json file, we don't have resources names. We have number.
Each number correspond to one resource. This dictionary is used to determine which number goes with which resource.
"""

items_shortcuts = {"p": "pickaxe",
                   "r": "ring",
                   "h": "house",
                   "sh": "shield",
                   "sw": "sword"}

items_max_level = {
    "pickaxe": 30,
    "ring": 50,
    "house": 10,
    "shield": 21,
    "sword": 21
}
upgrade_costs = {}
"""The dictionary that contain all the costs for the items in the game."""

boss_data = {}


def load_json_files():
    file_names = {"house_data.json": "house",
                  "pickaxes_data.json": "pickaxe",
                  "ring_data.json": "ring",
                  "sword_and_shield_data.json": "sword"}
    # This dictionary contains the name of a file associated with a key that represent how we should name the data
    # contained in this file in our new dictionary.
    for (key, value) in file_names.items():

        with open(f"../data/{key}") as json_file:
            data = json.load(json_file)
            upgrade_costs[value] = data
            if value == "sword":
                upgrade_costs["shield"] = data
    with open(f"../data/boss_data.json") as json_file:
        data = json.load(json_file)
        global boss_data
        boss_data = data


tower_data = []  # Contain the information about each of the 100 levels of the towers (position of bosses, of up doors...)


def generate_tower_data(cnx):
    for floor in range(1, 100):
        tower_data.append(tower.TowerBossData(floor, cnx))
