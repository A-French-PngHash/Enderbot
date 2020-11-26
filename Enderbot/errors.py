import discord
import values
import utils


class NotEnoughResources(Exception):
    def __init__(self, author: discord.User = None):
        self.author = author

    def __str__(self):
        return f"{self.author.mention}, You don't have enough resources..."


class NoNextLevelForItem(Exception):
    def __init__(self, author: discord.User, item: str):
        self.author = author
        self.item = item

    def __str__(self):
        return f"{self.author.mention} There is no level {values.items_max_level[self.item] + 1} for the" \
               f" {values.emojis[self.item]} {self.item.capitalize()}"


class NotEnoughManaForMining(Exception):
    def __init__(self, author: discord.User):
        self.author = author

    def __str__(self):
        return f"{self.author.mention}, You don't have enough mana"


class NoAccount(Exception):
    def __str__(self):
        return f"This user has no account..."


class ReputationsNotAvailable(Exception):
    def __str__(self):
        return "You don't fullfill the requirements to give reputations points"


class CantUpgradeVillageComponent(Exception):
    def __init__(self, component):
        if component == "inhabitant":
            self.message = "You can't recruit more inhabitants, be more reputable first !"
        elif component == "academy":
            self.message = "You can't build more academies, recruit more citizens first !"
        else:
            self.message = "You can't build more factories, your population must be more educated first !"

    def __str__(self):
        return self.message
