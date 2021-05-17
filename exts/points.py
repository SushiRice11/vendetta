import discord
from discord.ext import commands
import math
import random


def is_linked():
    async def predicate(ctx):
        return bool(await ctx.bot.db.links.find_one({"user": ctx.author}))
    return commands.check(predicate)

def can_be_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def to_str(num):
    if num < 1000:
        return str(num)
    if num < 100000:
        x = num/1000
        x = round(x, 1)
        return str(x) + "K"
    x = num/1000000
    x = round(x, 2)
    return str(x) + "M"

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, member: discord.Member, points: int):
        await self.bot.db.points.find_one_and_update({"user": member.id}, {"$inc": {"points": 0 - points}})
        await ctx.send("**Points Removed**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member, points: int):
        await self.bot.db.points.find_one_and_update({"user": member.id}, {"$inc": {"points": points}})
        await ctx.send("**Points Added**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, member: discord.Member, points: int):
        await self.bot.db.points.find_one_and_replace({"user": member.id}, {"points": points, "user": member.id})
        await ctx.send("**Points Set**")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.cooldown(30, 30, commands.BucketType.guild)
    @is_linked()
    async def points(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.author

        r = await self.bot.db.points.find_one({"user": user.id})
        if not r:
            p = 0
        else:
            p = r["points"]
        await ctx.send(
            embed=discord.Embed(title=user.name + "'s points!", description=f"{user.name} currently has {p} Points!"))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.cooldown(30, 30, commands.BucketType.guild)
    @is_linked()
    async def give(self, ctx, member: discord.Member, points: int):
        r = await self.bot.db.points.find_one({"user": ctx.author.id})
        if not r:
            p = 0
        else:
            p = r["points"]
        if points > p:
            embed = discord.Embed(colour=discord.Colour.red(
            ), title="Error!", description="You don't have enough points!")
            await ctx.send(embed=embed)
            return

        if points < 1:
            raise commands.BadArgument("You can't have less than 1 point")

        r = await self.bot.db.points.find_one({"user": member.id})
        if r:
            await self.bot.db.points.find_one_and_update({"user": member.id},  {"$inc": {"points":  points}})
        else:
            await self.bot.db.points.insert_one({"user": member.id, "points": points})
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points":  0 - points}})
        await ctx.send(f"**Gave {points} points to {member}!**")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.cooldown(30, 30, commands.BucketType.guild)
    @is_linked()
    async def buy(self, ctx, points: int):
        if points not in list(self.bot.config["buy"].keys()):
            embed = discord.Embed(colour=discord.Colour.red(
            ), title="Error!", description="This is not a valid package!")
            await ctx.send(embed=embed)
            return
        r = await self.bot.db.points.find_one({"user": ctx.author.id})
        if not r:
            p = 0
        else:
            p = r["points"]
        if points > p:
            embed = discord.Embed(colour=discord.Colour.red(
            ), title="Error!", description="You don't have enough points!")
            await ctx.send(embed=embed)
            return
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points": 0 - points}})
        if can_be_int(self.bot.config['buy'][points]):
            embed = discord.Embed(
                colour=discord.Colour.blue(),
                title="Add XP!",
                description=f"Please add this xp, using the following command ```!give-xp {ctx.author.mention} {self.bot.config['buy'][points]} ```"
            )
        else:
            embed = discord.Embed(
                colour=discord.Colour.blue(),
                title="Give Items!",
                description=f"Please give this item to the user! {self.bot.config['buy'][points]} to {ctx.author.mention} with id {ctx.author.id}"
            ) 
        c = self.bot.get_channel(self.bot.config["command_channel"])
        await c.send(embed=embed)
        embed = discord.Embed(
            title="Done!",
            description="Your package should be awarded soon!"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @is_linked()
    async def packages(self, ctx):

        p = "\n".join(
            [f"**{to_str(points)} Points will give you {self.bot.config['buy'][points]}{' XP' if can_be_int(self.bot.config['buy'][points]) else ''}!**" for points in
             list(self.bot.config["buy"].keys())])
        embed = discord.Embed(
            title="Packages",
            description=f"A list of all packages you can use to convert points into xp and more!! \n{p}"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["lb"])
    @is_linked()
    async def leaderboard(self, ctx, _type="rank", page=1):
        page -= 1
        if page < 0:
            page = 0
        data = []
        if _type == "rank":
            async for doc in self.bot.db.leveling.find():
                data.append(doc)
            data = sorted(data, key=lambda i: i["xp"], reverse=True)

            max_pages = math.ceil(len(data) / 10)

            if page >= max_pages:
                page = max_pages - 1

            rd = [[i, d] for i, d in enumerate(data) if i // 10 == page]
            d = "\n".join(
                (f"#{doc[0]+1} <@!{doc[-1]['user']}> is level {doc[-1]['level']}" for doc in rd))

            embed = discord.Embed()
            embed.color = discord.Color.blue()
            embed.title = "Leaderboard"
            embed.description = f"**Page {page+1}**\n\n{d}"
            await ctx.send(embed=embed)      
            return
        async for doc in self.bot.db.points.find().sort("points"):
            data.append(doc)
        data = sorted(data, key=lambda i: i["points"], reverse=True)

        max_pages = math.ceil(len(data) / 10)

        if page >= max_pages:
            page = max_pages - 1

        rd = [[i, d] for i, d in enumerate(data) if i // 10 == page]
        d = "\n".join(
            (f"#{doc[0]+1} <@!{doc[-1]['user']}>: {doc[-1]['points']}" for doc in rd))

        embed = discord.Embed()
        embed.color = discord.Color.blue()
        embed.title = "Leaderboard"
        embed.description = f"**Page {page+1}**\n\n{d}"
        await ctx.send(embed=embed)



    """
    @commands.command()
    async def pstats(self, ctx, page=1):
        page -= 1
        if page < 0:
            page = 0
        data = {}
        async for doc in self.bot.db.gambles.find().sort("points"):
            if doc["user"] in data:
                data[doc["user"]] += amount if doc["win"] else 0 - amount
        data = sorted(data, key=lambda i: i["points"], reverse=True)

        max_pages = math.ceil(len(data) / 10)

        if page >= max_pages:
            page = max_pages - 1

        rd = [[i, d] for i, d in enumerate(data) if i // 10 == page]
        d = "\n".join(
            (f"#{doc[0]+1} <@!{doc[-1]['user']}>: {doc[-1]['points']}" for doc in rd))

        embed = discord.Embed()
        embed.color = discord.Color.blue()
        embed.title = "Leaderboard"
        embed.description = f"**Page {page+1}**\n\n{d}"
        await ctx.send(embed=embed)
        """

def setup(bot):
    bot.add_cog(Points(bot))
