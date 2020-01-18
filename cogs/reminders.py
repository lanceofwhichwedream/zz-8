import asyncio
from discord.ext import commands


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
