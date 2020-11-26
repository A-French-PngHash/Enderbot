import discord
import utils
import values
import math


class ResourcesDict(dict):

    def __init__(self, cnx, player):
        super().__init__()
        self.player = player
        self.cnx = cnx
        self.resources_already_added = []
        # When we intialize the dictionary we go through all the resources stored in the database. It would be dumb
        # and a loss of performance that during this inisialisation we would send a request to the database at each
        # resources changement. This list prevent this. It say if a resources has already been initialised. If yes
        # then it won't send a query to the database.

    def __setitem__(self, key, value):
        if key in self.resources_already_added:
            query = f"""UPDATE Player
                JOIN Resources ON Resources.id = Player.resource_id
                SET {key} = {value}
                WHERE Player.id = {self.player.id}"""
            utils.execute_query(self.cnx, query)
        else:
            self.resources_already_added.append(key)
        super().__setitem__(key, value)


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
        self.player = player  # We store the player object because we may need data from it.
        self.resources = ResourcesDict(self.cnx, self.player)
        #self.resources = {}  # A dictionary that contain all the resources of this player
        self.load_resources()

    def load_resources(self):
        resources_query = f"""
                    SELECT *
                    FROM Resources
                    WHERE id = {self.player.resource_id};
                """
        resources_query_result = utils.execute_query(self.cnx, resources_query)[0]

        for name in values.resources_name_in_database:
            self.resources[name] = resources_query_result[name]

    def change_color(self, new_color):
        utils.set_value_for(self.player, f"UNHEX('{new_color}')", "inventory_color", self.cnx)

    def get_embed(self):  # This function return the embed that need to be printed to display the inventory
        resources_order = {"Resources (1)": ["Stone", "Perfect Prism", "Antimatter"],
                           "Resources (2)": ["Iron", "Gold", "Obsidian"],
                           "Resources (3)": ["Ruby", "Sapphire", "Emerald"],
                           "Resources (4)": ["Cobalt", "Adamantite", "Mithril"]}

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
                    resources_displayed[
                        key] += f"{values.emojis[resourceName]} {resourceName}: {formatted[resource_name_in_db]}\n"
                    # Here it will be in the user format because we did not modify the "resources_order" dictionary
        embed = discord.Embed(color=discord.Colour(self.player.inventory_color))
        embed.set_author(name=f"Inventory of {self.player.author.name}", icon_url=self.player.author.avatar_url)
        embed.add_field(name=f"{values.emojis['mana']} Mana [+1/{self.player.interval_for_one_mana}s]",
                        value=f"{utils.add_space_number(math.floor(self.player.mana))}/{utils.add_space_number(self.player.max_mana)}",
                        inline=True)
        embed.add_field(name=f"{values.emojis['hp']} HP [+1/60s]",
                        value=f"{utils.add_space_number(math.floor(self.player.life_points))}/{utils.add_space_number(self.player.max_life_points)}",
                        inline=True)
        embed.add_field(name=f"{values.emojis['energy']} Energy [+1/{self.player.interval_for_one_energy}]",
                        value=f"{math.floor(self.player.energy)}/{self.player.max_energy}")
        embed.add_field(name=f"{values.emojis['xp']} Level",
                        value=f"{utils.add_space_number(self.player.level)} [{values.emojis['xp']} exp: {utils.add_space_number(self.player.xp)}]",
                        inline=True)
        for (key, value) in resources_displayed.items():
            embed.add_field(name=key, value=value, inline=True)

        tools_string = f"""
                        {values.emojis["pickaxe"]} Pickaxe - Level: {self.player.tools.pickaxe}
                        {values.emojis["house"]} House - Level: {self.player.tools.house}
                        {values.emojis["ring"]} Ring - Level: {self.player.tools.ring}"""

        embed.add_field(name=":hammer_pick: Items", value=tools_string, inline=True)
        embed.add_field(name=f"{values.emojis['sword']} Fight",
                        value=f"{values.emojis['sword']} Sword | Level: {self.player.tools.sword}\n"
                              f"{values.emojis['shield']} Shield | Level: {self.player.tools.shield}\n", inline=True)
        return embed
