import discord
import player
import utils
import datetime
import values
import errors


class VillageUpgrade:
    def __init__(self, village, component_name, amount):
        """
        Initialisation of the VillageUpgrade object.

        INPUT:
            - village : The village in question
            - component_name : The name of the component to upgrade.
                Must be on of these three : ["inhabitant", "academy", "factory"]
            - amount = The number of component the user wish to upgrade
        """
        self.village = village
        self.component_name = component_name
        self.upgrade_cost = values.villages_upgrades_costs[self.component_name]
        for (key, value) in self.upgrade_cost.items():
            self.upgrade_cost[key] *= amount
        self.amount = amount
        self.is_valid = True

        if component_name == "inhabitant":
            if self.village.player.reputations >= self.village.inhabitants + amount:
                return
        elif component_name == "academy":
            if self.village.inhabitants >= self.village.academies + amount:
                return
        else:
            if self.village.academies >= self.village.factories + amount:
                return

        self.is_valid = False
        raise errors.CantUpgradeVillageComponent(component_name)

    def do_upgrade(self) -> str:
        """
        Complete the upgrade. Remove the resources from the player and add the new element.

        OUTPUT:
            - str : The upgrade message need to be edited with this message
        """

        if not self.village.player.has_resources(self.upgrade_cost):
            raise errors.NotEnoughResources(self.village.player.author)

        for (key, value) in self.upgrade_cost.items():
            self.village.player.inventory.resources[key] -= value

        message = "Village upgrade completed successfully !"
        if self.component_name == "factory":
            self.village.factories += self.amount
            message += f"Your factory level just increased to {self.village.factories}"
        elif self.component_name == "academy":
            self.village.academies += self.amount
            message += f"Your academy level just increased to level {self.village.academies}"
        elif self.component_name == "inhabitant":
            self.village.inhabitants += self.amount
            message += f"Your population size just increased to {self.village.inhabitants}"
        return message

    def get_upgrade_summary(self) -> str:
        """
        Called when needing to inform the user oin what will be going on with this upgrade.

        OUTPUT:
            - str : The message to send to the user
        """
        name = self.component_name
        if name == "inhabitants":
            name = "house"
        message = f"Do you really want to build more {name} for 1 citizens ? It will cost you :\n"
        for (key, value) in self.upgrade_cost.items():
            message += values.emojis[utils.convert_resources_to_user_name([key])[
                0]] + f" {10 * self.amount}M " + key.upper() + "\n"
        return message


class Village:
    def __init__(self, cnx, player):
        """
        Initialisation of the Village object.

        INPUT:
            - player:player.Player : The player object associated with the village
            - cnx : The connection to the mysql database.


        The village has two main datetime variable. It has the last_lookup and the last_claim. Every time the user
            craft a factory in his village, the last_lookup is updated and the number of stone in his village also.
            However it must not be possible to let stone generate more than 24 hours. This is when the last_claim
            variable come in game. This is the variable that store the last time the user claimed his stone. It is
            compared to the last lookup to know the number of stone to add.
        Basically the last_lookup is when the player look without collecting and the last_claim is when he look and
            collect.
        """
        self.player = player
        self.cnx = cnx
        get_village_data_query = f"""
        SELECT * FROM Village
        WHERE id = {self.player.village_id};
        """
        result = utils.execute_query(self.cnx, get_village_data_query)[0]
        self.id = result["id"]
        self._last_lookup = result["last_lookup"]
        self._last_claim = result["last_claim"]
        self._stone_inside = result["stone_inside"]
        self._factories = result["factories"]
        self._academies = result["academies"]
        self._inhabitants = result["inhabitants"]

    def set_value(self, new_value, name):
        """
        Set a a value in the Village table in the database for this village

        INPUT:
            - new_value : The new value to set in the database
            - name : The name of the value in the database
        """
        query = f"UPDATE Village SET {name} = {new_value} WHERE id = {self.id};"
        result = utils.execute_query(self.cnx, query)
        return result

    @property
    def last_lookup(self):
        return self._last_lookup

    @last_lookup.setter
    def last_lookup(self, value):
        self._last_lookup = value
        self.set_value(f"'{value.replace(microsecond=0)}'", "last_lookup")

    @property
    def last_claim(self):
        return self._last_claim

    @last_claim.setter
    def last_claim(self, value):
        self._last_claim = value
        self.set_value(f"'{value.replace(microsecond=0)}'", "last_claim")

    @property
    def stone_inside(self):
        self.update_stone_inside()
        return self._stone_inside

    @stone_inside.setter
    def stone_inside(self, value):
        self._stone_inside = value
        self.set_value(value, "stone_inside")

    @property
    def factories(self):
        return self._factories

    @factories.setter
    def factories(self, value):
        self.set_value(value, "factories")
        self._factories = value

    @property
    def academies(self):
        return self._academies

    @academies.setter
    def academies(self, value):
        self.set_value(value, "academies")
        self._academies = value

    @property
    def inhabitants(self):
        return self._inhabitants

    @inhabitants.setter
    def inhabitants(self, value):
        self.set_value(value, "inhabitants")
        self._inhabitants = value

    def update_stone_inside(self):
        """
        Update the number of stone stored inside the village depending on the last_lookup and the last_claim.
        """
        if not self.last_lookup:
            self.last_claim = datetime.datetime.now()
            self.last_lookup = datetime.datetime.now()
            self.stone_inside = 0

        if (datetime.datetime.now() - self.last_claim).seconds / 3600 > 24:
            return self._stone_inside

        factories_to_consider = self.factories
        if factories_to_consider > values.max_factories:
            factories_to_consider = values.max_factories

        minutes_passed = (datetime.datetime.now() - self.last_lookup).seconds // 60
        stone_per_factory_per_minutes = self.player.level * 10
        new_stone_amount = minutes_passed * stone_per_factory_per_minutes * factories_to_consider + self._stone_inside

        self.stone_inside = new_stone_amount

        self.last_lookup = datetime.datetime.now() - datetime.timedelta(
            seconds=(datetime.datetime.now() - self.last_lookup).seconds % 60)

    def collect_stone(self) -> str:
        """
        Collect the stone stored in the village.

        OUTPUT:
            - str : The message to send to the user.
        """
        self.update_stone_inside()
        self.player.receive_resource_from({"stone": self.stone_inside})
        self.last_claim = datetime.datetime.now()
        self.last_lookup = datetime.datetime.now()
        message = f"You just claimed {values.emojis['Stone']} {self.stone_inside} stones !"
        self.stone_inside = 0
        return message

    def get_embed(self) -> discord.Embed:
        """
        Called when needing the representation of the village in an embed.

        OUTPUT:
            - discord.Embed -> The representation of the village
        """
        embed = discord.Embed(title=f"{self.player}'s village")
        embed.add_field(name="Reputation", value=self.player.reputations)
        embed.add_field(name="Inhabitants", value=self.inhabitants)
        embed.add_field(name="Academy", value=self.academies)
        embed.add_field(name="Factory", value=self.factories)
        embed.add_field(name="Stone Claimable", value=self.stone_inside)
        return embed

    def upgrade_component(self, name: str, amount: int = 1) -> VillageUpgrade:
        """
        Upgrade an element of the village.

        INPUT:
            - name:str : The name of the component to upgrade

        OUTPUT:
            - VillageUpgrade : The upgrade object
        """
        upgrade = VillageUpgrade(self, name, amount)
        return upgrade
