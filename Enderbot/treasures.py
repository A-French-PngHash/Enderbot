import utils
import discord
from discord.ext import commands
import datetime
import random
import player
import values
import asyncio


class Treasure(commands.Cog):
    def __init__(self, bot, cnx):
        self.bot = bot
        asyncio.run_coroutine_threadsafe(self.bot.wait_until_ready(), bot.loop)
        self.cnx = cnx
        self.shards = [Shard(i, self.cnx, self.bot) for i in range(values.number_of_shards)]
        self.shard_dictionary = {}
        for i in self.shards:
            self.shard_dictionary[i.shard_id] = i
        self.shards.sort()

    @commands.command(aliases=["tr"])
    async def treasure(self, ctx, *argument):
        """
        A command used to catch a treasure. May be used to jump onto an other shard or to print all the treasures times.
        """
        if argument and len(argument) == 2:
            if argument[0] == "jump" and 0 <= int(argument[1]) < values.number_of_shards:
                change_shard_query = f"""
                UPDATE Player
                SET actual_shard_id = {int(argument[1])};
                """
                utils.execute_query(self.cnx, change_shard_query)
                await ctx.send(f"You have successfully jumped on the shard {int(argument[1])}.")
        elif len(argument) == 1 and argument[0] == "time":
            times_remaining = ""
            for shard in self.shards:
                minutes, seconds = utils.get_remaining_time(shard.release_date)
                times_remaining += f"Shard {shard.shard_id}: {minutes}m{seconds}s\n"
            await ctx.send(times_remaining)

        elif len(argument) == 0:
            user_shard_id = utils.execute_query(
                self.cnx,
                f"SELECT actual_shard_id FROM Player WHERE id = {ctx.author.id}")[0]["actual_shard_id"]

            catch_shard_result = self.shard_dictionary[user_shard_id].catch_shard(ctx.author, ctx.author.guild)
            if catch_shard_result[0]:
                self.shards.sort()
            await ctx.send(catch_shard_result[1])


class Shard:
    def __init__(self, shard_id: int, cnx, bot: commands.Bot):
        self.shard_id = shard_id
        self.cnx = cnx
        get_treasure_data_query = f"""
        SELECT * FROM Treasures
        WHERE shard = {self.shard_id};
        """
        try:
            result = utils.execute_query(self.cnx, get_treasure_data_query)[0]
            self.last_guild_id = result["last_guild_id"]
            self.last_guild = bot.get_guild(int(self.last_guild_id))

            self.last_user_id = result["last_person_id"]
            self.last_user = bot.get_user(int(self.last_user_id))

            self.release_date = result["release_date"]
        except:  # We need to create this shard in the db
            add_shard_query = f"""
            INSERT INTO Treasures 
            VALUES({shard_id}, NOW(), 0, 0);
            """
            utils.execute_query(self.cnx, add_shard_query)
            self.release_date = datetime.datetime.today()

    def __lt__(self, other):
        return self.release_date > other.release_date

    def catch_shard(self, user: discord.User, guild: discord.Guild) -> (bool, str):
        """Called each time a user try to catch this shard.
        INPUT :
            - user : The user who is trying to catch the treasure.
            - guild : The guild on which he is trying to catch it

        OUTPUT :
            - bool : True if the treasure was caught. False otherwise
            - str : The message to send to the user. Whether he caught it or not
        """

        if (self.release_date - datetime.datetime.today()).total_seconds() <= 0:  # This user catch it.
            self.last_user = user
            self.last_user_id = user.id

            self.last_guild = guild
            self.last_guild_id = guild.id

            self.release_date = datetime.datetime.today() + datetime.timedelta(minutes=random.randint(35, 50),
                                                                               seconds=random.randint(0, 59))

            update_treasure_data_query = f"""
            UPDATE Treasures
            SET last_guild_id = {self.last_guild_id}, last_person_id = {self.last_user_id}, release_date = "{self.release_date}"
            WHERE shard = {self.shard_id};
            """
            utils.execute_query(self.cnx, update_treasure_data_query)
            winner = player.Player(self.cnx, self.last_user)
            return True, winner.win_treasure()
        else:
            minutes, seconds = utils.get_remaining_time(self.release_date)
            return False, f"{user} - You are currently fighting for the treasure on the shard [VIRTUAL] {self.shard_id}. \n" \
                          f"Last treasure has been taken by the following person : {self.last_user}, " \
                          f"from the following guild : {self.last_guild}, it will be available again in : " \
                          f"**{minutes}m{seconds}s**"

