import discord
from discord.ext import commands
import yaml
import os
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.level import Leveling

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f.read())

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(config["prefix"], intents=intents)

bot.config = config
@bot.event
async def on_ready():
    bot.session = ClientSession()
    bot.db = AsyncIOMotorClient(bot.config["db_login"])[bot.config["db_name"]]
    bot.leveling = (Leveling(bot))

@bot.event
async def on_message(message):
    if message.channel.id not in bot.config["banned_channels"] or message.author.guild_permissions.administrator:
        await bot.process_commands(message)

def run():
    for i in os.listdir("/home/ven/exts"):
        if i.endswith(".py"):
            try:
                bot.load_extension("exts."+ i[:-3:])
            except Exception as e:
                print(e)
    bot.run(bot.config["token"])


__name__ == "__main__" and run()
