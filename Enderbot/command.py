import discord
from discord.ext import commands
from player import *
import checks
import trading
import crafting


def setup(bot):
    bot.add_cog(Command(bot))


check: checks.Checks = None
cnx = None


def has_account_if_not_create(ctx):
    return check.has_account_if_not_create(ctx)


class Command(commands.Cog):
    def __init__(self, bot):
        """
        Initialisation of this cog.

        INPUT:
            - bot : The bot object
            - check : An instance of the Checks class in order to call checks.
            - cnx : The connnection to the database
        """
        self.bot = bot
        self.active_trades = {}  # A dictionary which represent all the ongoing trades
        self.active_crafts = {}  # A dictionary which represent all the ongoing upgrades that are waiting for the
        # emoji ✅
        self.active_village_upgrades = {}  # A dictionary which represent all the ongoing upgrade fo the villages
        self.active_towers = {} # A dictionary which represent all the tower where the user is active
        self.active_drop_confirmation = {}
    """
    async def cog_command_error(self, ctx, error):
        print("error")
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Mmmh i don't know this command...")
        elif isinstance(error, errors.NoNextLevelForItem):
            await ctx.send(error)
        elif isinstance(error, errors.NotEnoughManaForMining):
            await ctx.send(error)
        elif isinstance(error, errors.NoAccount):
            await ctx.send(error)
        elif isinstance(error, errors.CantUpgradeVillageComponent):
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
        else:
            await ctx.send("-----------ERROR---------------")
            await ctx.send("DISABLE THE ON COMMAND ERROR EVENT TO SEE THE FULL ERROR")
            print(error)
    """

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return
        if reaction.message.id in self.active_trades:
            trade = self.active_trades[reaction.message.id]
            if reaction.emoji == "❌":  # A player canceled the trade. We delete the trade.
                await reaction.message.edit(content=trade.get_trade_recap("canceled"))
                del self.active_trades[reaction.message.id]
                return
            elif reaction.emoji != "✅":
                return

            if trade.trading_player.author == user:
                trade.trading_player_validation = True
            elif trade.mentioned_player.author == user:
                trade.mentioned_player_validation = True
            if trade.is_possible():
                await trade.do_trade(reaction.message)
                del self.active_trades[reaction.message.id]
                dm_message = trade.get_trade_log()
                await trade.trading_player.author.send(dm_message)
                await trade.mentioned_player.author.send(dm_message)

        elif reaction.message.id in self.active_crafts:
            if self.active_crafts[reaction.message.id].player.author == user:
                if reaction.emoji == "✅":
                    craft = self.active_crafts[reaction.message.id]
                    await reaction.message.channel.send(craft.validate_craft())
                elif reaction.emoji != "❌":
                    return
                del self.active_crafts[reaction.message.id]
        elif reaction.message.id in self.active_village_upgrades:
            if self.active_village_upgrades[reaction.message.id].village.player.author == user:
                if reaction.emoji == "✅":
                    try:
                        edit = self.active_village_upgrades[reaction.message.id].do_upgrade()
                    except Exception as error:
                        await reaction.message.channel.send(error)
                        return
                    await reaction.message.edit(content=edit)
                elif reaction.emoji != "❌":
                    return
                del self.active_village_upgrades[reaction.message.id]
        elif reaction.message.id in self.active_towers:
            await self.active_towers[reaction.message.id].emoji_pressed(reaction.emoji, await self.bot.get_context(reaction.message), self.bot)
            await reaction.message.edit(content=self.active_towers[reaction.message.id].display_tower())

    @commands.command(aliases=["i", "inv"])
    @commands.check(has_account_if_not_create)
    async def inventory(self, ctx, user: str = None, color=None):
        """
        This function print the inventory of the user passed as argument.
        If no argument is passed then it print the inventory of the person who wrote the command
        """
        if user:
            if user == "color":
                player = Player(cnx, ctx.author)
                try:
                    embed = discord.Embed(color=discord.Colour(int(color, 16)))
                except:
                    await ctx.send("Cette couleur n'est pas une couleur valide")
                    return
                player.inventory.change_color(color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.add_field(name="Changed inventory color", value=f"Your inventory color was changed to {color}")
                await ctx.send(embed=embed)

                return
            else:
                user = user.replace("<", "")
                user = user.replace(">", "")
                user = user.replace("@", "")
                user = user.replace("!", "")
                user = self.bot.get_user(int(user))
                if check.has_account(user):
                    player = Player(cnx, user)
                    if not player.can_show_inventory():
                        await ctx.send(f"{ctx.author.mention}, The inventory that you tried to check is protected by a "
                                       f"10-level house.")
                else:
                    raise errors.NoAccount()
        else:
            player = Player(cnx, ctx.author)

        embed = player.inventory.get_embed()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(has_account_if_not_create)
    async def trade(self, ctx, *parameters):
        given_resources = []
        received_resources = []
        mentioned_id = 0
        for (pos, i) in enumerate(parameters):
            if i[0:2] == "<@":  # this id the id of the other participant of the trade
                mentioned_id = int(i[3:-1])
                given_resources = utils.get_resources_values_and_name_for(parameters[0:pos])
                received_resources = utils.get_resources_values_and_name_for(parameters[pos + 1:])
                break

        player_mentioned = Player(cnx, self.bot.get_user(mentioned_id))
        player_trading = Player(cnx, ctx.author)
        trade_object = trading.Trade(player_trading, player_mentioned, given_resources, received_resources, cnx)
        transaction_recap = await ctx.send(trade_object.get_trade_recap("waiting"))
        self.active_trades[transaction_recap.id] = trade_object

        await utils.add_validation_emojis_to_message(transaction_recap)

    @commands.command(aliases=["mi"])
    @commands.check(has_account_if_not_create)
    async def mine(self, ctx, amount=None):
        player = Player(cnx, ctx.message.author)
        amount_to_mine = amount
        if not amount:
            amount_to_mine = 1
        if amount == "all" or amount == "a" or int(amount_to_mine) > player.mana:
            amount_to_mine = math.floor(player.mana)

        if int(amount_to_mine) > 0:
            embed = player.mine(int(amount_to_mine))
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention}, You don't have enough mana")

    @commands.command()
    @commands.check(has_account_if_not_create)
    async def craft(self, ctx, item: str):
        # The minimal letters to input in order for the bot to recognize the correct item.
        for (key, value) in values.items_shortcuts.items():
            if item.startswith(key):
                player = Player(cnx, ctx.author)
                item_craft = crafting.Craft(player, value, cnx)
                message = await ctx.send(item_craft.ask_for_validation_message())
                await utils.add_validation_emojis_to_message(message)
                self.active_crafts[message.id] = item_craft

    @commands.command(aliases=["hr"])
    @commands.check(has_account_if_not_create)
    async def hourly(self, ctx):
        player = Player(cnx, ctx.author)
        await player.hourly(ctx)

    @commands.command(aliases=["da", "day"])
    @commands.check(has_account_if_not_create)
    async def daily(self, ctx):
        player = Player(cnx, ctx.author)
        await player.daily(ctx)

    @commands.command()
    @commands.check(has_account_if_not_create)
    async def rep(self, ctx, user: discord.User):
        sender = Player(cnx, ctx.author)
        if not check.has_account(user):
            raise errors.NoAccount()
        receiver = Player(cnx, user)
        await sender.send_rep_to(receiver, ctx)

    @commands.command(aliases=["v", "vi", "vil", "villa"])
    @commands.check(has_account_if_not_create)
    async def village(self, ctx, parameter: str = None, amount: int = 1):
        player = Player(cnx, ctx.author)

        upgrade = None

        if parameter:
            if parameter == "claim"[:len(parameter)]:
                await ctx.send(player.village.collect_stone())
                return
            elif parameter == "factory"[:len(parameter)]:
                upgrade = village.VillageUpgrade(player.village, "factory", amount)
            elif parameter == "academy"[:len(parameter)]:
                upgrade = village.VillageUpgrade(player.village, "academy", amount)
            elif parameter == "recruit"[:len(parameter)]:
                upgrade = village.VillageUpgrade(player.village, "inhabitant", amount)

        if upgrade and upgrade.is_valid:
            message = await ctx.send(upgrade.get_upgrade_summary())
            await utils.add_validation_emojis_to_message(message)
            self.active_village_upgrades[message.id] = upgrade
        else:
            await ctx.send(embed=player.village.get_embed())

    @commands.command(aliases=["to", "tow"])
    @commands.check(has_account_if_not_create)
    async def tower(self, ctx):
        player = Player(cnx, ctx.author)
        message = await ctx.send("Summoning your tower...")
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("⬇️")
        await message.add_reaction("⬆️")
        await message.add_reaction("✅")
        await message.edit(content=player.tower.display_tower())
        self.active_towers[message.id] = player.tower

    @commands.command(aliases=["pi", "pick"])
    @commands.check(has_account_if_not_create)
    async def pickup(self, ctx):
        pass

    @commands.command(aliases=["dr", "dro"])
    @commands.check(has_account_if_not_create)
    async def drop(self, ctx, resources):
        player = Player(cnx, ctx.author)
