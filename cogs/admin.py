import asyncio
import discord
import re
from discord.ext import commands
from discord.utils import get
from prettytable import PrettyTable

TEST_RE = re.compile(r"(?i)ye{2,}t")
YEET_URL = "https://www.youtube.com/watch?v=2Bjy5YQ5xPc"


class Admin(commands.Cog):
    guilds = []

    def __init__(self, bot, zz8_db, logger):
        self.bot = bot
        self.zz8_db = zz8_db
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready When the bot starts up, executes these functions
        """
        Admin.guilds = self.zz8_db.get_channel_prefs()

    @commands.command()
    async def list_muted(self, ctx):
        """
        list_muted Lists the muted channels

        :param ctx: Context surrounding the invoked command
        :type ctx: Object
        """

        channels = [self.bot.get_channel(i).name for i in Admin.guilds]
        print(channels)
        await ctx.send(channels)

    @commands.command()
    async def configure_muting(self, ctx):
        """
        Configures the channels ZZ8 will respond in

        :param ctx: Context surrounding the invoked command
        :type ctx: Object
        """

        ignored_channels = []
        author = ctx.message.author
        channel = ctx.channel
        guild = ctx.message.guild.id
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
        await asyncio.sleep(2)
        await ctx.send(f"```{table}```")
        await ctx.send("Please reply with a space separated list of numbers")
        res = await self.bot.wait_for("message", check=check, timeout=180)
        ignores = res.content.split(" ")

        for i in ignores:
            Admin.guilds.append(channels[int(i) - 1].id)
            ignored_channels.append(channels[int(i) - 1].id)

        self.zz8_db.store_guild_channel_prefs(guild, ignored_channels)
        self.logger.info(f"Stored preferences for guild {guild}")
