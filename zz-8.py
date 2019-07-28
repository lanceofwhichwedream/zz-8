"""
The main code for ZZ-8

ZZ-8 is designed to perform some basic bot functions
Includes some intregation with reddit
"""
import configparser
import os
import re
import sys

import praw
from discord.ext import commands


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
    appconfig["reddit_client_id"] = config.get("prod", "reddit_client_id")
    appconfig["reddit_client_secret"] = config.get("prod",
                                                   "reddit_client_secret")

    return appconfig


CONFIG = readconfig()
REDDIT = praw.Reddit(
    client_id=CONFIG["reddit_client_id"],
    client_secret=CONFIG["reddit_client_secret"],
    user_agent="zz-8",
)


def reddit_posts(subreddit, posts):
    """
    Function to search subreddits for new posts
    """

    return REDDIT.subreddit(subreddit).new(limit=posts)


TEST_RE = re.compile(r"(?i)^ye{2,}t")
YEET_URL = "https://www.youtube.com/watch?v=2Bjy5YQ5xPc"
DESCRIPTION = "ZZ-8 the lovable youngest bot"

ZZ8 = commands.Bot(command_prefix="!", description=DESCRIPTION)


@ZZ8.event
async def on_ready():
    """
    Gives us some status output for zz-8
    """
    print("Logged on as", ZZ8.user.name)


@ZZ8.command()
async def reddit(subreddit, posts):
    """
    Reddit command for zz-8 for a user specified subreddit and number of posts
    """

    for sub in reddit_posts(subreddit, int(posts)):
        await ZZ8.say(sub.title)
        await ZZ8.say(sub.url)


@ZZ8.event
async def on_message(message):
    """
    This is the real action for zz-8
    """
    # No self replies for the bot

    if message.author == ZZ8.user:
        return

    if message.content == "Hello":
        await ZZ8.send_message(message.channel, "World")

    if TEST_RE.match(message.content):
        await ZZ8.send_message(message.channel, YEET_URL)

    if message.content == "Tech News":
        for sub in reddit_posts("technology", 5):
            await ZZ8.send_message(message.channel, sub.title)
            await ZZ8.send_message(message.channel, sub.url)

    await ZZ8.process_commands(message)


ZZ8.run(CONFIG["client_token"])
