import discord
from discord.ext import commands
import random
import asyncio

class Player:
    def __init__(self, bot, member, uuid):
        self.user = member
        self.uuid = uuid
        self.bot = bot


    @classmethod
    async def from_discord(cls, bot, member):
        doc = await bot.db["links"].find_one({
            "user" : member.id
        })
        try:
            return cls(bot, member, doc["uuid"])
        except:
            raise discord.NotFound()

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.giveaway)

    @giveaway.command()
    @commands.has_permissions(administrator=True)
    async def new(self, ctx):
        embed = discord.Embed()
        embed.title = "What channel should the giveaway go to?"
        embed.description = "Mention a channel with #."
        check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        await ctx.send(embed=embed)
        m = await self.bot.wait_for("message",
            check=lambda m: check(m) and len(m.channel_mentions) > 0)
        channel = m.channel_mentions[0]

        embed = discord.Embed(title="What should the title for this giveaway be?", description="Keep it short, this will be at the top of the embed.")
        await ctx.send(embed=embed)

        m = await self.bot.wait_for("message", check=check)
        title = m.content

        embed = discord.Embed(title="What should the description for this giveaway be?", description="Describe what you will giveaway.")

        await ctx.send(embed=embed)
        m = await self.bot.wait_for("message", check=check)
        description = m.content

        embed = discord.Embed(title="How many winners should there be?", description="How many people should be chosen to win")
        msg = await ctx.send(embed=embed)
        for i in ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "🔢"):
            await msg.add_reaction(i)

        r, u = await self.bot.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == msg and u.id == ctx.author.id and str(r.emoji) in ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "🔢")
        )
        i = 0
        if str(r.emoji) == "1️⃣":
            i = 1
        elif str(r.emoji) == "2️⃣":
            i = 2
        elif str(r.emoji) == "3️⃣":
            i = 3
        elif str(r.emoji) == "4️⃣":
            i = 4
        if i == 0:
            embed = discord.Embed()
            embed.title = "How many winners should there be"
            embed.description = "Please respond with a number between 5-100 here"
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            def check(m):
                try:
                    if not (4 < int(m.content) and int(m.content) < 101):
                        raise ValueError
                except ValueError:
                    return False
                return m.channel.id == msg.channel.id and m.author.id == ctx.author.id

            m = await self.bot.wait_for("message", check=check)
            i = int(m.content)
        win_num = i

        embed = discord.Embed(
            colour=discord.Colour.green(),
            title=title,
            description=description
        )
        embed.set_footer(text="React with 🎉 to enter")

        message = await channel.send(embed=embed)
        c = f"\n\n**Verification!**\nTo prevent people joining with alts, please link your minecraft account to enter, when you enter, you will be dmed if your entry was succsessful"
        embed.description += c
        await message.edit(embed=embed)

        await message.add_reaction("🎉")
        embed = discord.Embed(title=f"End the giveaway with {ctx.prefix}giveaway end {message.id}", description=f"Giveaway started in {channel.mention}.")
        await ctx.send(embed=embed)
        data = {
            "message" : message.id,
            "channel" : message.channel.id,
            "title": title,
            "description": description,
            "creator": ctx.author.id,
            "winners": [],
            "entries": [],
            "win_num": win_num,
            "active" : True
        }
        await self.bot.db.giveaways.insert_one(data)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member:
            return
        if payload.member.bot:
            return
        if not str(payload.emoji) == "🎉":
            return
        doc = await self.bot.db.giveaways.find_one({
            "message": payload.message_id,
            "channel": payload.channel_id,
            "active": True
        })
        if not doc:
            return
        if payload.user_id in doc["entries"]:
            return
        async with self.lock:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            try:
                player = await Player.from_discord(self.bot, payload.member)
            except:
                await message.remove_reaction(str(payload.emoji), payload.member)
                try:
                    await payload.member.send("You could not enter into the giveaway! Please verify your account")
                except:
                    pass
                return
            if not player:
                await message.remove_reaction(str(payload.emoji), payload.member)
                try:
                    await payload.member.send("You could not enter into the giveaway! Please verify your account")
                except:
                    pass
                return
            doc["entries"].append(payload.user_id)
            try:
                await payload.member.send("You have entered the giveaway!")
            except:
                pass
            await self.bot.db.giveaways.find_one_and_replace({
                "message": payload.message_id,
                "channel": payload.channel_id
            }, doc)

    @giveaway.command()
    async def end(self, ctx, messageid: int):
        doc = await self.bot.db.giveaways.find_one({
            "message": messageid,
            "active": True
        })
        if not doc:
            raise commands.BadArgument()
        r = doc["entries"]
        winners = []
        for _ in range(doc["win_num"]):
            x = random.choice(r)
            while x in winners:
                x = random.choice(r)
                try:
                    player = await Player.from_discord(self.bot, bot.get_user(x))
                except:
                    continue
                if not player:
                    continue
            winners.append(x)

        doc["winners"] = winners[::]
        doc["active"] = False
        channel = self.bot.get_channel(doc["channel"])
        message = await channel.fetch_message(doc["message"])
        await channel.send("**Giveaway Ended**\n\n" + "\n".join(
            [f"<@!{winner}> won {doc['title']}!" for winner in winners])
        )
        await ctx.send("**Ended!**")
        await self.bot.db.giveaways.find_one_and_replace({
            "message": message.id
        }, doc)

    @giveaway.command()
    async def reroll(self, ctx, messageid: int):
        doc = await self.bot.db.giveaways.find_one({
            "message": messageid,
            "active": False
        })
        if not doc:
            raise commands.BadArgument()
        r = doc["entries"]
        winners = []
        for _ in range(doc["win_num"]):
            x = random.choice(r)
            while x in winners:
                x = random.choice(r)
                try:
                    player = await Player.from_discord(self.bot, bot.get_user(x))
                except:
                    continue
                if not player:
                    continue
            winners.append(x)

        doc["winners"] = winners[::]
        doc["active"] = False
        channel = self.bot.get_channel(doc["channel"])
        message = await channel.fetch_message(doc["message"])
        await channel.send("**Giveaway Rerolled**\n\n" + "\n".join(
            [f"<@!{winner}> won {doc['title']}!" for winner in winners])
        )
        await ctx.send("**Rerolled!**")
        await self.bot.db.giveaways.find_one_and_replace({
            "message": message.id
        }, doc)


def setup(bot):
    bot.add_cog(Giveaway(bot))