import asyncio
import dateparser
from datetime import datetime
from discord.ext import commands, tasks
from prettytable import PrettyTable


class Reminders(commands.Cog):
    def __init__(self, bot, zz8_db):
        """
        Reminders [summary]

        :param commands: [description]
        :type commands: [type]
        :param bot: [description]
        :type bot: [type]
        """
        self.bot = bot
        self.zz8_db = zz8_db

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

    @commands.command()
    async def view_reminders(self, ctx):
        """
        view_reminders

        Simple function to show a user all of their scheduled
        reminders

        :param ctx: Context in which the command was invoked
        :type ctx: Context
        """
        # Sets up our early variables
        table = PrettyTable()
        column_names = ["Time", "Reminder"]
        uuid = ctx.message.author.id
        user = ctx.message.author

        # Start doing the heavy lifting
        reminders = self.zz8_db.search_reminders_by_uuid(uuid)

        # Some nice loop comprehension
        if not reminders:
            table = "You have not given me anything to remind you about"
            await user.send(f"{table}")
        else:
            time = [
                datetime.strptime(i["time"], "%m-%d-%Y-%H-%M").strftime(
                    "%m/%d/%Y, %H:%M"
                )
                for i in reminders
            ]
            reminder = [i["reminder"] for i in reminders]
            table.add_column(column_names[0], time)
            table.add_column(column_names[1], reminder)
            await user.send(f"```{table}```")

    @commands.command()
    async def add_reminder(self, ctx):
        """
        add_reminder

        Function to add reminders for users

        :param ctx: Context in which the command
        was invoked
        :type ctx: Context
        """
        uuid = ctx.message.author.id
        user = ctx.message.author
        channel = ctx.channel

        def check(m):
            return m.author == user and m.channel == channel

        await ctx.send("What would you like to be reminded of?")
        msg = await self.bot.wait_for("message", check=check, timeout=60)

        await ctx.send("When would you like to be reminded?")
        time = await self.bot.wait_for("message", check=check, timeout=60)

        when = dateparser.parse(time).strftime("%m-%d-%Y-%H-%M")

        self.zz8_db.store_reminder(uuid, user, msg, when)
        human_date = dateparser.parse(time).strftime("%m/%d/%Y")
        human_time = dateparser.parse(time).strftime("%H:%M")
        await ctx.send(f"I will remind you of this on {human_date} at {human_time}")

    @tasks.loop(minutes=1.0)
    async def remind_people(self):
        """
        remind_people

        Background task to send reminders
        to people, runs every minute
        """
        now = datetime.now.strftime("%m-$d-%Y-%H-%M")
        reminders = self.zz8_db.search_reminders_by_time(now)
        if reminders:
            for i in reminders:
                await i["user"].send(f"You asked to be reminded about this")
                await i["user"].send(f"{i['reminder']}")

