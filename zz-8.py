#!/usr/bin/env python3
"""
The main code for ZZ-8

ZZ-8 is designed to perform some basic bot functions
Includes some intregation with reddit
"""
import asyncio
import configparser
import logging
import os
import re
import sys
import discord
import praw
import youtube_dl
from discord.ext import commands
from discord.utils import get
from db_init import zz8_db

logger = logging.getLogger("zz-8")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("zz-8.log")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")

c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

logger.addHandler(c_handler)
logger.addHandler(f_handler)


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def getconfigpath():
    """
    Returns the path for the config
    """

    path = os.path.join(sys.path[0], "config", "zz-8.cfg")

    return path


def readconfig():
    """
    reads the config for zz-8
    """

    configpath = getconfigpath()

    config = configparser.RawConfigParser()
    config.read(configpath)

    if not config.sections():
        return False

    appconfig = {}
    appconfig["client_token"] = config.get("prod", "client_token")
    appconfig["reddit_cid"] = config.get("prod", "reddit_client_id")
    appconfig["reddit_csec"] = config.get("prod", "reddit_client_secret")
    appconfig["db_user"] = config.get("prod", "db_user")
    appconfig["db_pass"] = config.get("prod", "db_pass")
    appconfig["db_host"] = config.get("prod", "db_host")
    appconfig["db_port"] = config.get("prod", "db_port")
    return appconfig


# Config variables
config = readconfig()

# Sets up the reddit instance
# for querying subreddits
reddit = praw.Reddit(
    client_id=config["reddit_cid"],
    client_secret=config["reddit_csec"],
    user_agent="zz-8",
)

TEST_RE = re.compile(r"(?i)ye{2,}t")
YEET_URL = "https://www.youtube.com/watch?v=2Bjy5YQ5xPc"
DESCRIPTION = "ZZ-8 the lovable youngest bot"

bot = commands.Bot(command_prefix="!", description=DESCRIPTION)
zz8_db = zz8_db(config)
zz8_db.connection()
zz8_db.db_init()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        discord.opus.load_opus("libopus.so.0")
        channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(
            source, after=lambda e: print("Player error: %s" % e) if e else None
        )

        await ctx.send("Now playing: {}".format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        await ctx.send("Now playing: {}".format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        await ctx.send("Now playing: {}".format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


class Reminders(commands.Cog):
    def __init__(self, bot):
        """
        Reminders [summary]

        :param commands: [description]
        :type commands: [type]
        :param bot: [description]
        :type bot: [type]
        """
        self.bot = bot

    @commands.command()
    async def remind_me(self, ctx, num):
        """
        remind_me [summary]

        :param ctx: context in which the command was invokved
        :type ctx: obj
        :param num: variable provided by user
        :type num: int
        """
        uuid = ctx.message.author.id
        await ctx.send(f"I have recieved {num}")
        await asyncio.sleep(int(num))
        await ctx.send(f"this is a test <@{uuid}>")


class Interests(commands.Cog):
    def __init__(self, bot):
        """
        Interests
        List of commands that zz-8 has in order to give users
        a personalized experience from reddit
        """
        self.bot = bot

    @commands.command()
    async def list_interests(self, ctx):
        """
        Command to add user interests
        """
        uuid = ctx.message.author.id
        interests = []

        response = zz8_db.get_user_interests(uuid)

        for var in response:
            interests.append(var.lower())

        logger.info(f"retrieved interests for user {uuid}")
        await ctx.send(f"According to what I've been told, you like {interests}")

    @commands.command()
    async def update_interests(self, ctx):
        """
        Command to add user interests
        """
        interests = []
        uuid = ctx.message.author.id
        author = ctx.message.author
        response = zz8_db.get_user_interests(uuid)
        channel = ctx.channel

        def check(m):
            return m.author == author and m.channel == channel

        #        def int_check(m):
        #            return m.author == author and m.channel == channel
        for var in response:
            interests.append(var.lower())

        logger.info(f"Listing current interests for user {uuid}")
        await ctx.send(f"Which topic would you like to update {interests}?")
        await ctx.send(f"Please state a number 1 through {len(interests)}")

        msg = await bot.wait_for("message", check=check, timeout=60)
        await ctx.send(f"What would you like to change it to?")

        new_int = await bot.wait_for("message", check=check, timeout=60)

        interests[int(msg.content) - 1] = new_int.content

        zz8_db.update_user_interests(uuid, interests)
        logger.info(f"Updated interests for user {uuid}")
        await ctx.send(f"I have updated your interests for you")

    @commands.command()
    async def add_interests(self, ctx, *topic):
        """
        Command to add user interests
        """
        uuid = ctx.message.author.id
        interests = []

        for var in topic:
            interests.append(var.lower())

        zz8_db.store_user_interests(uuid, interests)
        logger.info(f"Stored interests for user {uuid}")
        await ctx.send(f"Thank you for letting me know you like {topic}")

    @commands.command()
    async def quick_reddit_view(self, ctx):
        """
        Do a quick feed for reddit

        Posts top 5 posts from a users list interests
        """
        uuid = ctx.message.author.id
        user = ctx.message.author
        message = []
        response = zz8_db.get_user_interests(uuid)

        for sub in reddit_posts(response, 5):
            message.append(sub.title)
            message.append(f"<https://reddit.com{sub.permalink}>")

        await user.send("\n".join(message))

    @commands.command()
    async def raspberries(self, ctx):
        """
        This server needs more boondocks
        """
        await ctx.send("The radar sir")
        await asyncio.sleep(1)
        await ctx.send("it appears to be...")
        await asyncio.sleep(5)
        await ctx.send("jammed!")
        await asyncio.sleep(3)
        await ctx.send("There's only one man...")
        await asyncio.sleep(3)
        await ctx.send("who would _dare_ give me the raspberry!")
        await asyncio.sleep(3)
        await ctx.send("Lone Starr!")

    @commands.command()
    async def reddit(self, ctx, subreddit, posts):
        """
        Reddit command for zz-8 for a user
        specified subreddit and number of posts
        """

        for sub in reddit_posts(subreddit, int(posts)):
            await ctx.send(sub.title)
            await ctx.send(sub.url)


@bot.event
async def on_ready():
    """
    Gives us some status output for zz-8
    """
    print(f"Logged on as {bot.user.name}, beep beep")


@bot.event
async def on_message(message):
    """
    This is the real action for zz-8
    """
    # No self replies for the bot

    if message.author == bot.user:
        return

    if message.content == "Hello":
        await message.channel.send("World")

    if TEST_RE.search(message.content):
        await message.channel.send(YEET_URL)

    if message.content == "Tech News":
        for sub in reddit_posts("technology", 5):
            await message.channel.send(sub.title)
            await message.channel.send(sub.url)

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    uuid = message.author.id
    await message.channel.send(f"I saw that, <@{uuid}>")


@bot.event
async def on_message_edit(old_msg, new_msg):
    """
    Performs a list of actions on reciving message
     edit event
    """
    emoji = get(bot.emojis, name="rah")
    await new_msg.add_reaction(emoji)


def reddit_posts(subreddit, num_posts):
    """
    Function to search subreddits for new posts
    """
    limit = len(subreddit) * num_posts
    sub_list = "+".join(subreddit)
    posts = []

    for sub in reddit.subreddit(sub_list).new(limit=limit):
        posts.append(sub)

    return posts


bot.add_cog(Music(bot))
bot.add_cog(Interests(bot))
bot.add_cog(Reminders(bot))
bot.run(config["client_token"])
