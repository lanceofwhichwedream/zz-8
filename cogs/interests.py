import asyncio
import configparser
import os
import sys
import discord
import praw
from discord.ext import commands


class Interests(commands.Cog):
    def __init__(self, bot, zz8_db, reddit, logger):
        """
        Interests
        List of commands that zz-8 has in order to give users
        a personalized experience from reddit
        """
        self.bot = bot
        self.zz8_db = zz8_db
        self.logger = logger
        self.reddit = reddit

    def reddit_posts(self, subreddit, num_posts):
        """
        Function to search subreddits for new posts
        """
        limit = len(subreddit) * num_posts
        sub_list = "+".join(subreddit)
        posts = []

        for sub in self.reddit.subreddit(sub_list).new(limit=limit):
            posts.append(sub)

        return posts

    @commands.command()
    async def list_interests(self, ctx):
        """
        Command to add user interests
        """
        uuid = ctx.message.author.id
        interests = []

        response = self.zz8_db.get_user_interests(uuid)

        for var in response:
            interests.append(var.lower())

        self.logger.info(f"retrieved interests for user {uuid}")
        await ctx.send(f"According to what I've been told, you like {interests}")

    @commands.command()
    async def update_interests(self, ctx):
        """
        update_interests

        Responsible for upserting a user's interests.

        Takes in a series of strings from user and transofmrs it into an array.
        It then takes that array and stores it into a mongodb colelction by way
        of db_init class.

        :param ctx: [description]
        :type ctx: [type]
        :return: [description]
        :rtype: [type]
        """
        interests = []
        uuid = ctx.message.author.id
        author = ctx.message.author
        response = self.zz8_db.get_user_interests(uuid)
        channel = ctx.channel

        def check(m):
            return m.author == author and m.channel == channel

        # Candidate for list comprehension
        # Consider execution and when it would need to be executed or not

        self.logger.info(f"Listing current interests for user {uuid}")

        await ctx.send("Fetching current interests, please hold")

        if response:
            interests = [var.lower() for var in response]

            await ctx.send("Interests have been found.")
            await asyncio.sleep(1)
            await ctx.send(f"Which topic would you like to update {interests}?")
            await ctx.send(f"Please state a number 1 through {len(interests)}")

            msg = await self.bot.wait_for("message", check=check, timeout=60)
            await ctx.send(f"What would you like to change it to?")

            new_int = await self.bot.wait_for("message", check=check, timeout=60)

            interests[int(msg.content) - 1] = new_int.content
        else:
            await ctx.send("I'm unable to find any interests stored for you")
            await asyncio.sleep(1)
            await ctx.send("Let's fix that")
            await ctx.send("What are you interested in?")

            new_int = await self.bot.wait_for("message", check=check, timeout=60)

            interests = new_int.content

        self.zz8_db.update_user_interests(uuid, interests)
        self.logger.info(f"Updated interests for user {uuid}")
        await ctx.send(f"I have updated your interests for you")

    @commands.command()
    async def add_interests(self, ctx, *new_interests):
        """
        Command to add user interests
        """
        uuid = ctx.message.author.id
        old_interests = self.zz8_db.get_user_interests(uuid)
        interests = old_interests + list(new_interests)

        # We upsert the record
        self.zz8_db.update_user_interests(uuid, interests)
        self.logger.info(f"Stored interests for user {uuid}")

        # Nice to have some feedback
        await ctx.send(f"Thank you for letting me know you like {list(new_interests)}")

    @commands.command()
    async def quick_reddit_view(self, ctx):
        """
        Do a quick feed for reddit

        Posts top 5 posts from a users list interests
        """
        uuid = ctx.message.author.id
        user = ctx.message.author
        message = []
        response = self.zz8_db.get_user_interests(uuid)

        for sub in self.reddit_posts(response, 5):
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
    async def my_reddit(self, ctx, subreddit, posts):
        """
        Reddit command for zz-8 for a user
        specified subreddit and number of posts
        """

        for sub in self.reddit_posts(subreddit, int(posts)):
            await ctx.send(sub.title)
            await ctx.send(sub.url)
