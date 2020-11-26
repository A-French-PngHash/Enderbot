import discord
from discord.ext import commands
import values


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["h"])
    async def help(self, ctx, command: str = None):
        """
        Help function which give information about what the bot can do to the user.

        INPUT:
            - ctx : the context
            - command:str : the command the user want to get info on. If None then the general help is sent.
        """
        if not command:
            embed = discord.Embed(title="Game Commands", color=values.help_pages_color)
            embed.add_field(name="help", value="Send you the help page, but if you specify the name of another "
                                               "command after it, you can get more information about a specific "
                                               "command", inline=False)
            embed.add_field(name="inventory", value="Show your inventory", inline=False)
            embed.add_field(name="mine", value="Mine resources with your mana")
            embed.add_field(name="craft", value="Upgrade your tools to collect more resources", inline=False)
            embed.add_field(name="daily", value="Give life, energy and XP once a day", inline=False)
            embed.add_field(name="hourly", value="Earn bonus resources every hour !", inline=False)
            embed.add_field(name="rep", value="Give reputation points to others people", inline=False)
            embed.add_field(name="treasure", value="Treasure is a random event that grants lots of resources, "
                                                   "but only one player can get it, battle for it !", inline=False)
            embed.add_field(name="trade", value="Allow trade between two people who must both agree", inline=False)
            embed.add_field(name="village", value=f"Obtenez des villageois pour miner de la {values.emojis['Stone']} "
                                                  f"stone pour vous !", inline=False)
            embed.add_field(name="drop (TODO)", value="Linked to >pickup, allows you to drop resources in a channel, "
                                                      "resources dropped in a channel can be pickup up by anyone",
                            inline=False)
            embed.add_field(name="pickup (TODO)", value="Linked to >drop, allows you to pickup resources dropped by "
                                                        "other players", inline=False)
            embed.add_field(name="tower", value="Progress in the tower, a place full of bosses you must "
                                                "defeat, everything is controlled with reactions", inline=False)
            embed.add_field(name="enchant (TODO)", value="Allows you to enchant your stuff to have more power.",
                            inline=False)
            embed.add_field(name="chest (TODO)", value="Allows chest opening to get runes", inline=False)
            embed.add_field(name="generator (TODO)", value="Get a lot of experience every 4 hours.", inline=False)
            embed.add_field(name="potion (TODO)", value="Heal yourself with potions", inline=False)
            embed.add_field(name="structure (TODO)", value="Global structure which is linked to an organization ("
                                                           ">organization), can be upgraded and give bonuses to its "
                                                           "members.", inline=False)
            embed.add_field(name="organization (TODO)", value="Join, invite and manage an organization of players",
                            inline=False)


        else:
            embed = getattr(self, "help_" + command)()

        await ctx.send(embed=embed)

    def help_mine(self):
        embed = discord.Embed(title="MINE", color=values.help_pages_color)
        embed.add_field(name="Description", value="Mine resources with your mana", inline=False)
        embed.add_field(name="Documentation", value="Basic command, allow you to trade mana for resources, add a "
                                                    "number as argument to use a specific amount of mana, use all to "
                                                    "use `all` your mana available", inline=False)
        embed.add_field(name="Examples", value=">mine\n>mine 42\n>mine all", inline=False)
        embed.add_field(name="Aliases", value="mi", inline=False)
        return embed

    def help_inventory(self):
        embed = discord.Embed(title="INVENTORY", color=values.help_pages_color)
        embed.add_field(name="Description", value="Show your inventory.", inline=False)
        embed.add_field(name="Documentation",
                        value="You can specify a user with a mention after the command to check their inventory. "
                              "You can use the argument color followed by a hexadecimal color code to change the "
                              "display color of your inventory.",
                        inline=False)
        embed.add_field(name="Examples",
                        value=">inventory\n"
                              ">inventory <@719857024304676955>\n"
                              ">inventory color 16a085",
                        inline=False)
        embed.add_field(name="Aliases",
                        value="i, inv",
                        inline=False)
        return embed

    def help_craft(self):
        embed = discord.Embed(title="CRAFT", color=values.help_pages_color)
        embed.add_field(name="Description", value="Upgrade your tools to collect more resources.", inline=False)
        embed.add_field(name="Documentation", value="Add as the first argument the name of the item you want to "
                                                    "upgrade, available items are the following : [ pickaxe / house / "
                                                    "ring / sword / shield]", inline=False)
        embed.add_field(name="Examples", value=">craft pickaxe", inline=False)
        embed.add_field(name="Aliases", value="No Aliases", inline=False)
        return embed

    def help_treasure(self):
        embed = discord.Embed(title="TREASURE", color=values.help_pages_color)
        embed.add_field(name="Description", value="Treasure is a random event that grants lots of resources, but only "
                                                  "one player can get it, battle for it !", inline=False)
        embed.add_field(name="Documentation", value="To get the treasures, just send a quick wave of treasure "
                                                    "commands when the counter is low, there is one treasure per "
                                                    "shard. You can add a jump option followed by a number to jump on"
                                                    "a virtual shard. You can also add a time option to get the "
                                                    "remaining time of all the treasures", inline=False)
        embed.add_field(name="Examples", value=">treasure\n>tr\n>tr jump 3\n", inline=False)
        embed.add_field(name="Aliases", value="tr", inline=False)
        return embed

    def help_hourly(self):
        embed = discord.Embed(title="HOURLY", color=values.help_pages_color)
        embed.add_field(name="Description", value="Earn bonus resources every hour !", inline=False)
        embed.add_field(name="Documentation", value="N/A", inline=False)
        embed.add_field(name="Examples", value=">hourly\n>hr", inline=False)
        embed.add_field(name="Aliases", value="hr", inline=False)
        return embed

    def help_daily(self):
        embed = discord.Embed(title="DAILY", color=values.help_pages_color)
        embed.add_field(name="Description", value="Give life and XP once a day.", inline=False)
        embed.add_field(name="Documentation", value="N/A", inline=False)
        embed.add_field(name="Examples", value=">daily\n>da", inline=False)
        embed.add_field(name="Aliases", value="da, day", inline=False)
        return embed

    def help_rep(self):
        embed = discord.Embed(title="REP", color=values.help_pages_color)
        embed.add_field(name="Description", value="Give reputation points to others people", inline=False)
        embed.add_field(name="Documentation", value="Reputation points allow you to develop your village (>village). "
                                                    "You can grant (create) a rep point to another player every day, "
                                                    "requires level 1000.", inline=False)
        embed.add_field(name="Examples", value=">rep\n>rep @Somebody", inline=False)
        embed.add_field(name="Aliases", value="No aliases", inline=False)
        return embed

    def help_village(self):
        embed = discord.Embed(title="VILLAGE", color=values.help_pages_color)
        embed.add_field(name="Description", value="Obtenez des villageois pour miner de la :stone: stone pour vous !",
                        inline=False)
        embed.add_field(name="Documentation", value="Cette commande est directement lié à la commande >rep., "
                                                    "vos points de réputation donnent des habitants qui permettent la "
                                                    "construction d'académies qui permettent la construction "
                                                    "d'usines. Chaque minute, votre village produit une certaine "
                                                    "quantité de stone basé sur votre niveau et le nombre d'usines "
                                                    "présentes dans le village. Le production de stone est limité à "
                                                    "24h. Vous devez faire >village claim pour récupérer la stone "
                                                    "produite par les villageois.", inline=False)
        embed.add_field(name="Examples", value=">village\n>village recruit\n>village academy 12\n>village factory "
                                               "3\n>village claim", inline=False)
        embed.add_field(name="Aliases", value="v, vi, vil, villa", inline=False)
        return embed

    def help_help(self):
        embed = discord.Embed(title="HELP", color=values.help_pages_color)
        embed.add_field(name="Description", value="Send you the help page, but if you specify the name of another "
                                                  "command after it, you can get more information about a specific "
                                                  "command", inline=False)
        embed.add_field(name="Documentation", value="N/A", inline=False)
        embed.add_field(name="Examples", value=">help\n>help help\n>help give", inline=False)
        embed.add_field(name="Aliases", value="h", inline=False)
        return embed

    def help_tower(self):
        embed = discord.Embed(title="TOWER", color=values.help_pages_color)
        embed.add_field(name="Description",
                        value="Progress in the tower, a place full of bosses you must defeat, everything is controlled with reactions",
                        inline=False)
        embed.add_field(name="Documentation",
                        value="In each floor, there is a boss you must defeat, your amount of orbs determines if you can pass on the next floor or not.",
                        inline=False)
        embed.add_field(name="Examples", value=">tower", inline=False)
        embed.add_field(name="Aliases", value="to, tow", inline=False)
        return embed

    def default_help_embed(self):
        embed = discord.Embed(title="", color=values.help_pages_color)
        embed.add_field(name="Description", value="", inline=False)
        embed.add_field(name="Documentation", value="", inline=False)
        embed.add_field(name="Examples", value="", inline=False)
        embed.add_field(name="Aliases", value="", inline=False)
        return embed
