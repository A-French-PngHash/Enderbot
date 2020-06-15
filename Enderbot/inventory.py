import discord
import utils
import values
import math


class Inventory:
    """
    This class contain all the data that can be found in an inventory.
    """

    def __init__(self, player):
        """
        This constructor take the id of the person as a parameter.
        It will send request to the database in order to get all the necessary data.
        """
        self.cnx = player.cnx
        cursor = self.cnx.cursor(dictionary=True)

        resources_query = f"""
            SELECT *
            FROM Resources
            WHERE id = {player.resource_id};
        """
        cursor.execute(resources_query)
        resources_query_result = cursor.fetchall()[0]
        cursor.close()

        self.player = player  # We store the player object because we may need data from it.
        self.cnx = player.cnx
        self.resources = {}  # A dictionary that contain all the resources of this player

        for name in values.resources_name_in_database:
            self.resources[name] = resources_query_result[name]


    def get_embed(self):  # This function return the embed that need to be printed to display the inventory
        resources_order = {"Resources (1)": ["Stone", "Perfect Prism", "Anti Matter"],
                           "Resources (2)": ["Iron", "Gold", "Obsidian"],
                           "Resources (3)": ["Ruby", "Sapphire", "Emerald"]}

        resources_displayed = {}  # This dictionary will be presented like this : \
        # {"Resources (1)" : "Stone 1000\nPerfect Prism 32", "Resources (3)" : "Sapphire 3948"}

        formatted = utils.format_numbers(self.resources)

        for (key, value) in resources_order.items():
            for resourceName in value:
                # The name of resources in this dictionary are stored as the user format.
                # The name of resources in the "resources" property of this class are stored as the database format.
                # We have to convert to db format to find it in the property :
                resource_name_in_db = utils.convert_resources_to_db_name([resourceName])[0]
                if formatted[resource_name_in_db] != "0":
                    if key not in resources_displayed.keys():
                        # If the key "Resources (x)" is not already in the dictionary we add it
                        resources_displayed[key] = ""
                    resources_displayed[key] += f"{values.emojis[resourceName]} {resourceName}: {formatted[resource_name_in_db]}\n"
                    # Here it will be in the user format because we did not modify the "resources_order" dictionary

        embed = discord.Embed(color=0xff9200)
        embed.set_author(name=f"Inventory of {self.player.author.name}", icon_url=self.player.avatar_url)
        embed.add_field(name=f"{values.emojis['mana']} Mana [+1/30s]", value=f"{math.floor(self.player.mana)}/{self.player.max_mana}", inline=True)
        embed.add_field(name=f"{values.emojis['hp']} HP [+1/60s]", value=f"{math.floor(self.player.life_points)}/{self.player.max_life_points}", inline=True)
        embed.add_field(name=f"{values.emojis['xp']} Level", value=f"{self.player.level} [{values.emojis['xp']} exp: {self.player.xp}]", inline=True)
        #TODO : Add field for tools.

        for (key, value) in resources_displayed.items():
            embed.add_field(name=key, value=value, inline=True)
        return embed
