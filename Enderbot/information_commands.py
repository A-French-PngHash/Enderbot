import discord
from discord.ext import commands
import values


class InformationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong ! {values.emojis['thecat']} *({round(self.bot.latency * 1000)}ms)*")