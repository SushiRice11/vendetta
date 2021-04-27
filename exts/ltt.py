import discord
from discord.ext import commands

class LastToType(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        r = await self.bot.db.points.find_one({})
        if r:
            await self.bot.db.points.find_one_and_update({}, {"$inc": {"messages": 1}})
        else:
            await self.bot.db.points.insert_one({"messages": 1})
