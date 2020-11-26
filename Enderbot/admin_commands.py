import discord
from discord.ext import commands
import values
import utils
from player import *


class AdminCommands(commands.Cog):
    def __init__(self, bot, cnx):
        self.bot = bot
        self.cnx = cnx

    async def cog_check(self, ctx):
        print(values.author_id)
        return int(ctx.author.id) == int(values.author_id)

    @commands.command()
    async def reset(self, ctx, id):
        utils.reset_account(self.cnx, id)
        await ctx.send("Reseted account")

    @commands.command()
    async def add(self, ctx, player_id: int, *resources):
        """
        This is an admin function which usability is defined by the "is_owner" function.
        It basically generates the resources given as parameters under the form : "resource_name value".
        It gives them to the player passed as argument.
        """

        player = Player(self.cnx, self.bot.get_user(player_id))
        resources_transfer = utils.get_resources_values_and_name_for(resources)

        player.receive_resource_from(
            resources_transfer)  # We generate the resources so we need to input no user parameter
        await ctx.send("Added resources")