import re
import discord
from discord.ext import commands
import praw

bot = commands.Bot(command_prefix='$', description='description')

@bot.command()
async def test(ctx):
    await bot.say(ctx)

bot.run('NTQ5Nzg2NjA5NzY0MTM5MDE5.D1Y-Hw.uz2LUtYiL2q3yLJJqQhJmR_Ls3g')
