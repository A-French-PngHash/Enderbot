import discord
from discord.ext import commands
import mysql.connector
import config
from player import *
import trading
import errors
import traceback

bot = commands.Bot(command_prefix=">", description="The rewrite in python of enderbot, an rpg bot.")
cnx = mysql.connector.connect(
    user=config.user,
    password=config.word,
    host=config.ip,
    database='Enderbot')
cnx.autocommit = True
active_trades = {}
"""
In order to allow a faster lookup onto the trades, this is a dictionary.
The key is a discord.Message.id and the value is a trade object.
"""


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Mmmh i don't know this command...")
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, errors.NotEnoughResourcesError):
            await ctx.send(error.original)
        else:
            print(traceback.print_tb(error.__traceback__))


def create_account(player_id):  # Create account for the user with the corresponding id.
    print(f"creating account for player {player_id}")
    cursor = cnx.cursor()
    cursor.callproc("add_new_player", (player_id,))
    # Use the stored procedure named add_new_player.
    # See database construction for more information.
    cursor.close()


def has_account(user: discord.User):
    query = f"""
        SELECT * 
        FROM Player
        WHERE id = {user.id};"""
    cursor = cnx.cursor()
    cursor.execute(query)
    return not (cursor.fetchone() is None)
    cursor.close()


def has_account_if_not_create(ctx):
    # Check to determine if a user has an account.
    # If not, this function will create one automatically. It always return True.
    if not has_account(ctx.author):
        create_account(ctx.author.id)
    return True


def is_owner(ctx):
    return ctx.message.author.id == values.author_id


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    if reaction.message.id in active_trades.keys():
        print("trade")
        trade = active_trades[reaction.message.id]
        if reaction.emoji == "❌":  # A player canceled the trade. We delete the trade.
            await reaction.message.edit(content=trade.get_trade_recap("canceled"))
            del active_trades[reaction.message.id]
            return
        elif reaction.emoji != "✅":
            return

        if trade.trading_player.author == user:
            trade.trading_player_validation = True
        elif trade.mentioned_player.author == user:
            trade.mentioned_player_validation = True
        if trade.is_possible():
            await trade.do_trade(reaction.message)
        


@bot.command(aliases=["i", "inv"])
@commands.check(has_account_if_not_create)
async def inventory(ctx, user: discord.User= None):
    """
    This function print the inventory of the user passed as argument.
    If no argument is passed then it print the inventory of the person who wrote the command
    """
    if user:
        if has_account(user):
            player = Player(user, cnx)
        else:
            await ctx.send("This user has no account")
            return
    else:
        player = Player(ctx.author, cnx)

    embed = player.inventory.get_embed()
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_owner)
async def add(ctx, player_id: int, *resources):
    """
    This is an admin function which usability is defined by the "is_owner" function.
    It basically generates the resources given as parameters under the form : "resource_name value".
    It gives them to the player passed as argument.
    """
    player = Player(bot.get_user(player_id), cnx)
    resources_transfer = utils.get_resources_values_and_name_for(resources)

    player.receive_resource_from(resources_transfer)  # We generate the resources so we need to input no user parameter
    await ctx.send("Added resources")


@bot.command()
@commands.check(has_account_if_not_create)
async def trade(ctx, *parameters):
    given_resources = []
    received_resources = []
    mentioned_id = 0
    for (pos, i) in enumerate(parameters):
        if i[0:2] == "<@":  # this id the id of the other participant of the trade
            mentioned_id = int(i[3:-1])
            given_resources = utils.get_resources_values_and_name_for(parameters[0:pos])
            received_resources = utils.get_resources_values_and_name_for(parameters[pos + 1:])
            break
    trading_player_recap = utils.get_trade_recap_for(given_resources)
    mentioned_player_recap = utils.get_trade_recap_for(received_resources)

    player_mentioned = Player(bot.get_user(mentioned_id), cnx)
    player_trading = Player(ctx.author, cnx)
    trade_object = trading.Trade(player_trading, player_mentioned, given_resources, received_resources)
    transaction_recap = await ctx.send(trade_object.get_trade_recap("waiting"))
    active_trades[transaction_recap.id] = trade_object

    await transaction_recap.add_reaction("✅")
    await transaction_recap.add_reaction("❌")

    pass

bot.run("NzE5ODU3MDI0MzA0Njc2OTU1.XuEcDQ.Lijnj9BqFdgAcei0ZyWGGh8kO8o")
