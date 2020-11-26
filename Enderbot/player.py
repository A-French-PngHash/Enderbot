import discord
from datetime import *
from inventory import *
import tools
import numpy
import random
import discord
import binascii
import errors
import village
import tower


class Player:

    def __init__(self, cnx, author: discord.User = None, id = None):
        """
        Base init of the player class. Load a lot of things so may be a bit slow. Don't use for fast lookup.

        INPUT :
            - author:discord.Member : The user from which we load the player object
            - cnx : The database connection to execute queries
            - id : Used for testing, in case the author is None then the id is provided so that
                the program can still retrieve data
        """
        self.cnx = cnx
        if author:
            self.id = author.id
            self.author = author
        else:
            self.id = id

        profile_data_query = f"""
            SELECT *
            FROM Player 
            WHERE id = {self.id};
        """

        result = utils.execute_query(self.cnx, profile_data_query)[0]

        self._xp = result["xp"]
        self.level = utils.level_for(self._xp)

        self.tools_id = result["tools_id"]
        self.tools = tools.Tools(cnx, self)
        self.update_auto_regenerating_values(result)
        self.village_id = result["village_id"]

        update_last_lookup_query = f"""
            UPDATE Player
            SET last_lookup = NOW(), mana = {self._mana}, life_points = {self._life_points}, energy = {self._energy}
            WHERE id = {self.id};
        """
        utils.execute_query(self.cnx, update_last_lookup_query)

        self._orbs = result["orbs"]
        self.treasure_combo = result["treasure_combo"]
        self.shard_id = result["actual_shard_id"]
        self._village = None

        self._reputations = result["reputations"]
        self._last_reputation_claim = result["last_reputation_claim"]

        self._last_hourly_claim = result["last_hourly_claim"]
        self._last_daily_claim = result["last_daily_claim"]
        self._hourly_combo = result["hourly_combo"]

        try:
            self.inventory_color = int(binascii.hexlify(result["inventory_color"]), base=16)
        except:
            self.inventory_color = 9013641
        self.resource_id = result["resource_id"]
        self.tower_id = result["tower_id"]
        self._inventory : Inventory = None
        self._tower : tower.Tower = None
        """
        It seems that no one except Enderspirit (the original creator of the bot) know the formula to calculate the
            critical value of a player.
        The formula that i use is mine, it does not reflect appropriately the critical formula of enderspirit.
        What is important is that we have a formula and don't change it. 
        """
        self.critical = round(self.level / 100 + 1) * 100 * (self.tools.pickaxe * 10 + self.tools.ring * 5 + 1)

        self._attack = self.level * (1 + self.orbs / 100) + (self.orbs + 1) * (self.tools.sword * 2)
        self._defense = self.level * (1 + self.orbs / 100) + (self.orbs + 1) * (self.tools.shield * 2)

    def __str__(self):
        return str(self.author)

    def update_auto_regenerating_values(self, result = None):
        """
        This function updatr the gauges of mana, energy and life points of this player.

        INPUT:
            - result : Optionnal result from a query in the database of a player object
        """
        profile_data_query = f"""
            SELECT *
            FROM Player 
            WHERE id = {self.id};
        """
        if not result:
            result = utils.execute_query(self.cnx, profile_data_query)[0]
        seconds_passed = (datetime.today() - result["last_lookup"]).total_seconds()

        self.max_mana = 20 + self.level // 10
        self.max_life_points = 20 + self.level - 1
        self.max_energy = 20 + self.level // 1000

        self.interval_for_one_mana = round(60 - 3 * self.tools.house)
        self.interval_for_one_life_point = 60
        # TODO When adding enchant change interval for one hp
        self.interval_for_one_energy = 300
        # TODO : When adding enchants change interval for one energy

        mana = float(result["mana"]) + seconds_passed / self.interval_for_one_mana
        life_points = float(result["life_points"]) + seconds_passed / self.interval_for_one_life_point
        energy = float(result["energy"]) + seconds_passed / self.interval_for_one_energy

        if mana > self.max_mana:
            mana = self.max_mana
        if life_points > self.max_life_points:
            life_points = self.max_life_points
        if energy > self.max_energy:
            energy = self.max_energy
        self.energy = energy
        self.mana = mana
        self.life_points = life_points
        self.life_points = 100


    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, value):
        self._xp = value
        utils.set_value_for(self, value, "xp", self.cnx)

    @property
    def mana(self):
        self.update_auto_regenerating_values()
        return self._mana

    @mana.setter
    def mana(self, value):
        self._mana = value
        utils.set_value_for(self, value, "mana", self.cnx)

    @property
    def life_points(self):
        self.update_auto_regenerating_values()
        if self._life_points > self.max_life_points:
            self.life_points = self.max_life_points
        return self._life_points

    @life_points.setter
    def life_points(self, value):
        utils.set_value_for(self, value, "life_points", self.cnx)
        self._life_points = value

    @property
    def energy(self):
        return 20
        self.update_auto_regenerating_values()
        return self._energy

    @energy.setter
    def energy(self, value):
        utils.set_value_for(self, value, "energy", self.cnx)
        self._energy = value

    @property
    def hourly_combo(self):
        return self._hourly_combo

    @hourly_combo.setter
    def hourly_combo(self, value):
        utils.set_value_for(self, value, "hourly_combo", self.cnx)
        self._hourly_combo += 1

    @property
    def last_hourly_claim(self):
        return self._last_hourly_claim

    @last_hourly_claim.setter
    def last_hourly_claim(self, value):
        utils.set_value_for(self, f"\"{value.replace(microsecond=0)}\"", "last_hourly_claim", self.cnx)
        self._last_hourly_claim = value

    @property
    def last_daily_claim(self):
        return self._last_hourly_claim

    @last_daily_claim.setter
    def last_daily_claim(self, value):
        print("updating daily claim")
        utils.set_value_for(self, f"\"{value.replace(microsecond=0)}\"", "last_daily_claim", self.cnx)
        self._last_daily_claim = value

    @property
    def reputations(self):
        return self._reputations

    @reputations.setter
    def reputations(self, value):
        # TODO : When updating reputation update village
        utils.set_value_for(self, value, "reputations", self.cnx)
        self._reputations = value

    @property
    def last_reputation_claim(self):
        return self._last_reputation_claim

    @last_reputation_claim.setter
    def last_reputation_claim(self, value):
        utils.set_value_for(self, f"\"{value.replace(microsecond=0)}\"", "last_reputation_claim", self.cnx)
        self._last_reputation_claim = value


    @property
    def village(self):
        if not self._village:
            self._village = village.Village(self.cnx, self)
        return self._village

    @property
    def inventory(self):
        if not self._inventory:
            self._inventory = Inventory(self)
        return self._inventory

    @property
    def tower(self):
        if not self._tower:
            self._tower = tower.Tower(self, self.cnx)
        return self._tower

    @property
    def orbs(self):
        return self._orbs

    @orbs.setter
    def orbs(self, value):
        self._orbs = value
        utils.set_value_for(self, value, "orbs", self.cnx)

    @property
    def attack(self):
        self._attack = self.level * (1 + self.orbs / 100) + (self.orbs + 1) * (2*self.tools.sword)
        return self._attack

    @property
    def defense(self):
        self._defense = self.level * (1 + self.orbs / 100) + (self.orbs + 1) * (self.tools.shield * 2)
        return self._defense

    def can_show_inventory(self):
        """Determine if the inventory of the user can be shown to other players

        OUTPUT:
            - bool : True if it can be shown, False otherwise"""

        return self.tools.house < 10

    def receive_resource_from(self, resources, sender=None):
        """
        This function is the function used to transfer resources between account or to generate resources..

        INPUTS :
            - resources : a dictionary formatted like this : {"stone": "65", "ruby": 78} which contain the
                resources.
            - sender : a Player Object and will remove resources from this user and add them on this player. If no
                Player Object is passed as parameter, this function will generate the resources from nothing.
        """
        if sender and not sender.has_resources(resources):
            raise errors.NotEnoughResources()

        for (name, value) in resources.items():
            if value != 0:
                self.inventory.resources[name] += int(value)

        if not sender:
            return

        for (name, value) in resources.items():
            if value != 0:
                sender.inventory.resources[name] -= int(value)

    def mine(self, amount: int):
        """
        Take as input an int which correspond to the number of mana to use for the mine. The amount must be less or
        equal to the mana the player has.
        This function return the embed that need to be printed to inform the user on what he gained.
        """
        if amount > self.mana:
            raise errors.NotEnoughManaForMining(self.author)

        percentages = [values.resources_drop_rate[i]/100 for i in values.resources_name_in_database]
        resources_dropped = {i:0 for i in values.resources_name_in_database}
        xp_dropped = 0
        for i in range(amount):
            dropped = numpy.random.choice(values.resources_name_in_database, p=percentages)
            if dropped == "am" or dropped == "pp":
                resources_dropped[dropped] += random.randint(1, 3)
                xp_dropped += random.randint(1, 2) * 10
            else:
                resources_dropped[dropped] += int(self.critical / numpy.random.choice(
                    [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8],
                    p=[0.25, 0.2, 0.125, 0.125, 0.075, 0.05, 0.05, 0.075, 0.05]))
                xp_dropped += int(values.resources_xp_min[dropped] * random.randint(1, 2))

        self.receive_resource_from(resources_dropped)
        self.xp += xp_dropped
        self.mana -= amount

        return utils.get_mine_embed(resources_dropped, self, amount, xp_dropped)

    def win_treasure(self) -> str:
        """Called when a user won a treasure.

        OUTPUT :
            - A string to send to the user which contain the loot that the user won.
        """

        # This loot is not the true formulas of the bot. If someone know it, please add it
        self.treasure_combo += 1
        pp_loot = random.randint(30, 80)
        am_loot = random.randint(20, 55)
        stone_loot = random.randint(50000000, 200000000) * self.treasure_combo
        max_multiplier = 500 - self.treasure_combo
        if max_multiplier < 100:
            max_multiplier = 100
        min_multiplier = int(max_multiplier / 8)

        xp_loot = random.randint(min_multiplier, max_multiplier) * self.treasure_combo

        self.receive_resource_from({"stone": stone_loot,
                                    "pp": pp_loot,
                                    "am": am_loot}) # Generating resources

        utils.set_value_for(self, self.treasure_combo, "treasure_combo", self.cnx)
        self.xp += xp_loot

        message = f"{self.author.mention} You are currently fighting on shard {self.shard_id}\n" \
                  f"GG ! You just catch the treasure, you won the following resources : " \
                  f"{utils.add_space_number(stone_loot)} {values.emojis['Stone']} Stones, {pp_loot} " \
                  f"{values.emojis['Perfect Prism']} Perfect Prisms, {am_loot} {values.emojis['Antimatter']} " \
                  f"Antimatter and {xp_loot} {values.emojis['xp']} XP." \
                  f"Continue to collect treasures ! [Combo = {self.treasure_combo}]"
        return message

    async def hourly(self, ctx):
        """
        This function is called when the user want to get his hourly.

        INPUT:
            - ctx : The context of the command
        """
        if self.last_hourly_claim:
            interval = datetime.today() - self.last_hourly_claim
            if interval.total_seconds() > 0:
                if interval.total_seconds() > 3600:
                    if interval.total_seconds() > 7200: # The user get the +1 combo
                        self.hourly_combo = 0
                else:
                    date_disponible = self.last_hourly_claim + timedelta(hours=1)

                    minutes, seconds = utils.get_remaining_time(date_disponible)
                    await ctx.send(f"{ctx.author.mention}, You can not perform this command yet, you can collect your "
                                   f"due within {minutes}m{seconds}s.")
                    return
        # This loot is not the true formulas of the bot. If someone know it, please add it
        self.last_hourly_claim = datetime.today()
        combo_percentage = self.hourly_combo * 20
        combo_multiplier = combo_percentage / 100 + 1
        xp_loot = random.randint(800, 5000) * combo_multiplier
        stone_loot = (self.tools.pickaxe * self.tools.pickaxe * self.tools.pickaxe + 1) * (100 - self.tools.pickaxe * 3.3) * combo_multiplier
        # TODO : When adding enchants, change formulas

        utils.set_value_for(self, self.hourly_combo, "hourly_combo", self.cnx)
        self.xp += xp_loot
        self.receive_resource_from({"stone": stone_loot})
        await ctx.send(f"You found {values.emojis['Stone']} Stone ({utils.add_space_number(round(stone_loot))}). "
                       f"[{values.emojis['xp']} Exp: {utils.add_space_number(round(xp_loot))} | Combo : {self.hourly_combo} "
                       f"(+{combo_percentage} %)]")
        if not self.hourly_combo > 50:
            self.hourly_combo += 1

    async def daily(self, ctx):
        """
        This function is called when the user want to get his daily.

        INPUT:
            - ctx : The context of the command
        """
        embed = discord.Embed(color=0xe5d62e)

        if self.last_daily_claim:
            interval = datetime.today() - self.last_daily_claim
            if interval.days < 1:
                date_disponible = self.last_daily_claim + timedelta(days=1)

                minutes, seconds = utils.get_remaining_time(date_disponible)

                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.add_field(name="Next Daily in", value=f"{minutes//60}h{minutes%60}m{seconds}s")
                await ctx.send(embed=embed)
                return
        min_xp_dropped = math.ceil(self.level/1000)*1000
        if min_xp_dropped < 1700:
            min_xp_dropped = 200
        else:
            min_xp_dropped -= 1500
        xp_loot = random.randint(min_xp_dropped, math.ceil(self.level/1000)*1000)
        health_loot = random.randint(750, 1500)
        self.life_points += health_loot
        self.xp += xp_loot
        self.last_daily_claim = datetime.now()

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Recovered Daily", value=f"{values.emojis['xp']} Exp: {xp_loot}\n"
                                                      f"{values.emojis['hp']} HP: {health_loot}")
        embed.set_footer(text="See you tomorow ;)")
        await ctx.send(embed=embed)

    async def send_rep_to(self, player, ctx):
        if self.author.created_at > datetime.now() - timedelta(days=30) or self.level < 10000:
            raise errors.ReputationsNotAvailable

        rep_available_date = 0
        if self.last_reputation_claim:
            rep_available_date = self.last_reputation_claim + timedelta(days=1)

        if not self.last_reputation_claim or datetime.today() >= rep_available_date:
            player.reputations += 1
            self.last_reputation_claim = datetime.today()
            await ctx.send(f"{self.author.mention} - Your reputation point has been successfully given to "
                           f"{player.author.mention} !")
        else:
            minutes, seconds = utils.get_remaining_time(rep_available_date)
            await ctx.send("Your reputation point is not available yet ! Come back in "
                           f"{minutes//60}h{minutes%60}m{seconds}s"
                           f"to reward a good person ! :) You currently have {self.reputations} reputations points.")

    def has_resources(self, resources):
        """
        Verify if a given player has the resources in his inventory.

        INPUT:
            - user : A Player object
            - resources : A dictionary that contain all the resources dropped. it is formated like that :
                {"stone": 65, "ruby": 57 }.

        OUTPUT:
            - bool : Whether or not the user has the resources.
        """
        for (key, value) in resources.items():
            if int(self.inventory.resources[utils.convert_resources_to_db_name([key])[0]]) < int(value):
                return False
        return True

    def drop(self, resources, channel_id):
        """
        Called when this player want to drop resources in a channel

        INPUT:
            - resources : A dictionary formatte dlike that : {"stone" : 98, "ruby" : 10}
            - channel_id : The id of the channel where the resources were dropped
        """
        query = ""

