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
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
from db_init import zz8_db
from cogs.admin import Admin
from cogs.interests import Interests
from cogs.music import Music
from cogs.reminders import Reminders
from cogs.events import Events

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

DESCRIPTION = "ZZ-8 the lovable youngest bot"

zz8_db = zz8_db(config)
zz8_db.connection()
zz8_db.db_init()

bot = commands.Bot(command_prefix="!", description=DESCRIPTION)

bot.add_cog(Admin(bot, zz8_db, logger))
bot.add_cog(Music(bot))
bot.add_cog(Interests(bot, zz8_db, reddit, logger))
bot.add_cog(Reminders(bot, zz8_db, logger))
bot.add_cog(Events(bot, logger))
bot.run(config["client_token"])

