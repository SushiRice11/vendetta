import discord
from discord.ext import commands
from datetime import date
from aiohttp import ClientTimeout
from helpers.hypixel import uuid_to_name, name_to_uuid


class Player:
    def __init__(self, bot, member, uuid):
        self.user = member
        self.uuid = uuid
        self.bot = bot

    @classmethod
    async def from_user(cls, bot, member):
        doc = await bot.db["links"].find_one({
            "user" : member.id
        })
        try:
            return cls(bot, member, doc["uuid"])
        except:
            raise discord.NotFound()

    @classmethod
    async def from_mc(cls, bot, uuid):
        try:
            doc = await bot.db["links"].find_one({
                "uuid" : uuid
            })

            if doc:
                member = bot.get_user(doc["user"])
            else:
                member = None
        except:
            member = None
        return cls(bot, member, uuid)

    @classmethod
    async def from_mc_ign(cls, bot, ign):
        uuid = await name_to_uuid(bot, ign)
        try:
            doc = await bot.db["links"].find_one({
                "uuid" : uuid
            })

            if doc:
                member = bot.get_user(doc["user"])
            else:
                member = None
        except:
            member = None
        return cls(bot, member, uuid)

async def make_player(ctx, argument):
    print(ctx, argument)
    try:
        if not argument:
            member = ctx.author
            return await Player.from_user(ctx.bot, member)
        try:
            member = await commands.MemberConverter().convert(ctx, argument)
        except:
            
            d = await Player.from_mc_ign(ctx.bot, argument)
            if not d:
                d = await Player.from_mc(ctx.bot, argument)
            return d
        return await Player.from_user(ctx.bot, member)
    except:
        raise commands.BadArgument(argument)


class CheckXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_member(self, uuid):
        url = self.bot.config["linking"]["guild_endpoint"].format(uuid)
        async with self.bot.session.get(url, timeout=ClientTimeout(5)) as resp:
            data = (await resp.json())
        

        valid_days = None
        for member in data["guild"]["members"]:
            if member["uuid"] == uuid:
                return member

    async def get_guild_xp(self, uuid):
        member = await self.get_guild_member(uuid)
        x = 0
        for i, daydate in enumerate(reversed(list(member["expHistory"].keys()))):
            year = int(daydate.split("-")[0])
            month = int(daydate.split("-")[1])
            day = int(daydate.split("-")[2])
            if date(year, month, day).weekday() == 0:
                x = i
        xps = [xp for i, xp in enumerate(reversed(list(member["expHistory"].values()))) if i >= x]
        return sum(xps)

    @commands.command(aliases=["requirement", "r", "xp"])
    async def checkxp(self, ctx, *, player=None):
        player = await make_player(ctx, player)
        xp = await self.get_guild_xp(player.uuid)
        
        name = await uuid_to_name(self.bot, player.uuid)


        embed = discord.Embed()
        req_xp = self.bot.config["req_xp"]
        
        x = round(xp/req_xp*100, 2)
        embed.title = "Xp requirement reached!" if xp >= req_xp else "Xp requirement not reached!"
        embed.description = f"{name} has {xp}\n The requirement is {req_xp}.\n{x}% Reaced!"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CheckXP(bot))