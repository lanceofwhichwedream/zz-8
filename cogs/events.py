import asyncio
import discord
import re
from discord.ext import commands
from discord.utils import get


TEST_RE = re.compile(r"(?i)ye{2,}t")
YEET_URL = "https://www.youtube.com/watch?v=2Bjy5YQ5xPc"


class Events(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = []

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready When the bot starts up, executes these functions
        """
        self.guilds = self.bot.get_cog("Admin").guilds

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        This is the real action for zz-8
        """
        # No self replies for the bot

        #    channel = message.channel
        #    guild = message.guild
        #    if channels[guild][channel]:
        #        return
        if message.channel.id in self.guilds:
            return

        if message.author == self.bot.user:
            return

        if message.content == "Hello":
            await message.channel.send("World")

        if TEST_RE.search(message.content):
            await message.channel.send(YEET_URL)

    @commands.Cog.listener()
    async def on_message_edit(self, old_msg, new_msg):
        """
        on_message_edit Performs actions on message edits

        :param old_msg: Details of the message before edit
        :type old_msg: Ctx
        :param new_msg: Details of the message after edit
        :type new_msg: Ctx
        """
        emoji = get(self.bot.emojis, name="rah")
        print(new_msg)
        print(new_msg.embeds)
        if new_msg.channel.id in self.guilds:
            return

        if new_msg.author != self.bot.user and not new_msg.embeds:
            await new_msg.add_reaction(emoji)

