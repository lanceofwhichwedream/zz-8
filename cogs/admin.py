import asyncio
import discord
from discord.ext import commands
from prettytable import PrettyTable


class Admin(commands.Cog):
    def __init__(self, bot, zz8_db, logger):
        self.bot = bot
        self.zz8_db = zz8_db
        self.logger = logger

    #        self.guild_prefs = zz8_db.guilds

    @commands.command()
    async def configure_muting(self, ctx):
        """
        Configures the channels ZZ8 will respond in

        :param ctx: Context surrounding the invoked command
        :type ctx: Object
        """

        ignore_channels = []
        author = ctx.message.author
        channel = ctx.channel
        guild = ctx.message.guild
        channels = ctx.message.guild.text_channels

        def check(m):
            return m.author == author and m.channel == channel

        table = PrettyTable()
        column_names = ["Number", "Channel"]
        channel_names = [i.name for i in channels]
        numbers = [i + 1 for i in range(len(channel_names))]
        table.add_column(column_names[0], numbers)
        table.add_column(column_names[1], channel_names)
        await ctx.send("What channels should I not interact with?")
        await ctx.send(f"```{table}```")
        await ctx.send("Please reply with a space separated list of numbers")
        res = await self.bot.wait_for("message", check=check, timeout=180)
        ignores = res.content.split(" ")
        for i in ignores:
            ignore_channels.append({"name": channels[i].name, "id": channels[i].id})

