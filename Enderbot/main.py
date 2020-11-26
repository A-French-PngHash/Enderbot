import discord
from discord.ext import commands
import mysql.connector
import config
from player import *
import trading
import json
import admin_commands
import crafting
import treasures
import checks
import help
import information_commands
import tower

with open(f"../data/project_data.json") as json_file:
    data = json.load(json_file)
    values.bot_id = data["bot_id"]
    values.bot_token = data["bot_token"]
    values.author_id = data["author_id"]
    config.ip = data["mysql_db_ip"]
    config.user = data["mysql_db_user"]
    config.password = data["mysql_db_password"]

bot = commands.Bot(command_prefix=[f"<@{values.bot_id}> ", ">", f"<@!{values.bot_id}> ", f"<@{values.bot_id}>",
                                   f"<@!{values.bot_id}>"],
                   description="The rewrite in python of enderbot, an rpg bot.")
bot.remove_command("help")

cnx = mysql.connector.connect(
    user=config.user,
    password=config.password,
    host=config.ip,
    database='Enderbot',
    use_pure=True)
cnx.autocommit = True
check = checks.Checks(cnx)


@bot.event
async def on_ready():
    status = discord.Game("Loading...")
    await bot.change_presence(status=discord.Status.dnd, activity=status)
    values.load_json_files()
    values.generate_tower_data(cnx)
    bot.add_cog(admin_commands.AdminCommands(bot, cnx))
    bot.add_cog(treasures.Treasure(bot, cnx))
    bot.add_cog(help.Help(bot))
    _load("command")

    status = discord.Game(">help")
    await bot.change_presence(status=discord.Status.online, activity=status)
    print("Bot is ready")


@bot.command()
@commands.check(check.is_owner)
async def load(ctx, name):
    if name:
        bot.load_extension(ctx, name)
        await ctx.send("Extension was loaded")


@bot.command()
@commands.check(check.is_owner)
async def unload(ctx, name):
    if name:
        bot.unload_extension(name)
        await ctx.send("Extension was unloaded")


@bot.command()
@commands.check(check.is_owner)
async def reload(ctx, name):
    if name:
        try:
            bot.reload_extension(name)
        except:
            bot.load_extension(name)
        await ctx.send("Extension was reloaded")
        if name.lower() == "command":
            bot.extensions[name].cnx = cnx
            bot.extensions[name].check = check


def _load(name):
    if name:
        bot.load_extension(name)
        if name.lower() == "command":
            bot.extensions[name].cnx = cnx
            bot.extensions[name].check = check


bot.add_cog(information_commands.InformationCommands(bot))
bot.run(values.bot_token)
