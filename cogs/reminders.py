import asyncio
import dateparser
from datetime import datetime
from discord.ext import commands, tasks
from prettytable import PrettyTable


class Reminders(commands.Cog):
    def __init__(self, bot, zz8_db, logger):
        """
        Reminders [summary]

        :param commands: [description]
        :type commands: [type]
        :param bot: [description]
        :type bot: [type]
        """
        self.bot = bot
        self.zz8_db = zz8_db
        self.logger = logger
        self.remind_people.start()

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
        reminder = []
        time = []
        uuid = ctx.message.author.id
        user = ctx.message.author

        # Start doing the heavy lifting
        reminders = self.zz8_db.search_reminders_by_uuid(uuid)

        # Some nice loop comprehension
        if reminders.collection.count_documents({}) >= 1:
            for post in reminders:
                reminder.append(post["msg"])
                time.append(
                    datetime.strptime(post["time"], "%m-%d-%Y-%H-%M").strftime(
                        "%m/%d/%Y, %H:%M"
                    )
                )

            table.add_column(column_names[0], time)
            table.add_column(column_names[1], reminder)
            await user.send(f"```{table}```")
        else:
            table = "You have not given me anything to remind you about"
            await user.send(f"{table}")

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
        await ctx.send(
            'Please use a normally accepted time format such as a date and time or something like "in 5 minutes"'
        )
        time = await self.bot.wait_for("message", check=check, timeout=60)

        when = dateparser.parse(str(time.content))
        when_formatted = when.strftime("%m-%d-%Y-%H-%M")

        self.zz8_db.store_reminder(uuid, msg.content, when_formatted)
        human_date = when.strftime("%m/%d/%Y")
        human_time = when.strftime("%H:%M")
        await ctx.send(f"I will remind you of this on {human_date} at {human_time} UTC")

    @tasks.loop(minutes=1.0)
    async def remind_people(self):
        """
        remind_people

        Background task to send reminders
        to people, runs every minute
        """
        await self.bot.wait_until_ready()
        now = datetime.now().strftime("%m-%d-%Y-%H-%M")
        self.logger.info(f"Checking reminders for {now}")

        reminders = self.zz8_db.search_reminders_by_time(now)
        if reminders.collection.count_documents({}) >= 1:
            self.logger.info("Found some reminders, sending them out")
            for i in reminders:
                user = self.bot.get_user(i["uuid"])
                await user.send(f"You asked to be reminded about this")
                await user.send(f"{i['msg']}")
                self.zz8_db.delete_reminder(i["_id"])
        else:
            self.logger.info("No reminders to send out at this time")

