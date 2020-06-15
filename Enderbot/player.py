import discord
from datetime import *
from inventory import *
import tools


class Player:

    def __init__(self, author: discord.Member, cnx):
        self.id = author.id
        self.cnx = cnx
        self.avatar_url = author.avatar_url
        self.author = author
        profile_data_query = f"""
            SELECT *
            FROM Player 
            WHERE id = {author.id};
        """

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(profile_data_query)
        result = cursor.fetchall()[0]

        self.xp = result["xp"]
        self.level = utils.level_for(self.xp)
        self.max_mana = 20 + self.level // 10
        self.max_life_points = 20 + self.level - 1
        # + One life point every level.

        seconds_passed = (datetime.today() - result["last_lookup"]).total_seconds()
        # We use the time passed since the last lookup to update gauges
        self.life_points = float(result["life_points"]) + seconds_passed / 60
        # 1 HP per minute
        self.mana = float(result["mana"]) + seconds_passed / 30
        # The player win 2 mana per seconds

        if self.mana > self.max_mana:
            self.mana = self.max_mana
        if self.life_points > self.max_life_points:
            self.life_points = self.max_life_points
        update_last_lookup_query = f"""
            UPDATE Player
            SET last_lookup = NOW(), mana = {self.mana}, life_points = {self.life_points}
            WHERE id = {author.id};
        """
        cursor.execute(update_last_lookup_query)
        self.tools_id = result["tools_id"]
        self.resource_id = result["resource_id"]
        cursor.close()
        self.inventory = Inventory(self)
        self.tools = tools.Tools(cnx, self)
        """
        It seems that no one except Enderspirit (the original creator of the bot) know the formula to calculate the
            critical value of a player.
        The formula that i use is mine, it does not reflect appropriately the critical formula of enderspirit.
        What is important is that we have a formula and don't change it. 
        """
        self.critical = self.xp / self.level * (self.tools.pickaxe + self.tools.ring / 2)

    def __str__(self):
        return str(self.author)

    def receive_resource_from(self, resources, sender=None):
        """
        This function is the function used to transfer resources between account.
        It take as input a dictionary formatted like this : ["stone": "65", "ruby": 78] which contain the
        resources.
        It also takes as input a Player Object and will remove resources from this user and add them on this player.
        If no Player Object is passed as parameter, this function will generate the resources from nothing.
        """
        update_resources_query = """
            UPDATE Player
            JOIN Resources ON Resources.id = Player.resource_id
            SET 
            """
        for (name, value) in resources.items():
            update_resources_query += f"{name} = {self.inventory.resources[name] + int(value)}, "

        # The way we formatted the request, at the end of the string we will have ", " so we need to remove that :
        update_resources_query = update_resources_query[:-2]

        update_resources_query += f"""
            WHERE Player.id = {self.id};
            """
        cursor = self.cnx.cursor()
        cursor.execute(update_resources_query)

        if not sender:
            cursor.close()
            return
        update_resources_query = """
                    UPDATE Player
                    JOIN Resources ON Resources.id = Player.resource_id
                    SET 
                    """
        for (name, value) in resources.items():
            update_resources_query += f"{name} = {sender.inventory.resources[name] - int(value)}, "
        update_resources_query = update_resources_query[:-2]
        update_resources_query += f"""
            WHERE Player.id = {sender.id};
            """
        cursor.execute(update_resources_query)
