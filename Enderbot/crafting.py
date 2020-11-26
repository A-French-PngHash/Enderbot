import player
import tools
import values
import utils
import errors


class Craft:
    """A class that represent the craft of an item."""

    def __init__(self, player : player.Player, item_to_craft, cnx):
        """
        Initialisation of the Craft class.

        INPUT:
            - player:player.Player : The player object
            - item_to_craft : The name of the item the user want to craft. Must be one of those : ring, pickaxe, sword, shield
            - cnx : The connection to the database
        """
        self.player = player
        self.item_to_craft = item_to_craft
        self.new_level_of_item = player.tools.__getattribute__(item_to_craft) + 1

        if values.items_max_level[item_to_craft] <= self.new_level_of_item:
            raise errors.NoNextLevelForItem(self.player.author, item_to_craft)
            return

        self.cost_of_upgrade = values.upgrade_costs[item_to_craft][str(self.new_level_of_item)]
        """At this point the cost_of_upgrade dictionary look something like that : 
        {'1': 150, '2': 50, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11': 0, '12': 0}
        where each number correspond to a resource.
        In the case of the ring being crafted, it's just an int
        """

        if item_to_craft == "ring":
            self.cost_of_upgrade = {"pp": self.cost_of_upgrade}
            # 11 correspond to pp. In order to craft the ring you only need pp.
        else:
            self.cost_of_upgrade = {values.number_correspond_to_resource[key]:value for (key, value) in self.cost_of_upgrade.items()}

        self.user_number_formatted_costs = utils.format_numbers(self.cost_of_upgrade)
        self.cnx = cnx

    def ask_for_validation_message(self) -> str:
        """
        This function return a string that can be send to the user in order to verify if he is okay
        with upgrading his tool.

        OUTPUT:
            - str : The message to send to the user
        """
        validation_message = f"{self.player.author.mention} Upgrade your {values.emojis[self.item_to_craft]} " \
                             f"{self.item_to_craft} to level {self.new_level_of_item} will cost\n\n"
        for (key, value) in self.user_number_formatted_costs.items():
            if value != "0":
                resource_name = utils.convert_resources_to_user_name([key])[0]
                validation_message += values.emojis[resource_name] + " " + resource_name + ": " + value + "\n"
        return validation_message

    def validate_craft(self) -> (str):
        """This function will verify if the user has enough resources and then update the database in order to execute
        the upgrade.

        OUTPUTS :
            - str : The message to send.
        """

        self.player = player.Player(self.cnx, self.player.author)
        # We update the player object because the user may have already upgraded his item via an other trade.

        if self.player.tools.__getattribute__(self.item_to_craft) + 1 != self.new_level_of_item:
            return f"{self.player.author.mention} you already have a {values.emojis[self.item_to_craft]} " \
               f"{self.item_to_craft} level {self.new_level_of_item}"
        elif not self.player.has_resources(self.cost_of_upgrade):
            raise errors.NotEnoughResources()
            #return f"{self.player.author.mention}, You don't have enough resources..." # We don't raise an error because this function is normally called in an event which can't easely catch errors.

        # If we arrive here, then the user fill all the conditions to upgrade his item.

        query = """
        UPDATE Player
        JOIN Tools ON Tools.id = Player.tools_id SET """

        for (key, value) in self.cost_of_upgrade.items():
            if value != 0:
                self.player.inventory.resources[key] -= int(value)

        query += f"Tools.{self.item_to_craft}_level = {self.new_level_of_item} "
        query += f"WHERE Player.id = {self.player.author.id};"

        utils.execute_query(self.cnx, query)

        return f"**+++** Your **{self.item_to_craft}** was upgraded to level " \
               f"**{self.new_level_of_item}**"
