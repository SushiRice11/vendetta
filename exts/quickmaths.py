import discord
from discord.ext import commands, tasks
import random
import asyncio

e = [":zero:", ":one:", ":two:", ":three:", ":four:",
     ":five:", ":six:", ":seven:", ":eight:", ":nine:"]


def f_n(num):
    n = ""
    for let in str(num):
        if let == "-":
            n += "<:minus:831871414481977465>"   
            continue
        n += e[int(let)]
    return n

def f_w(x, y, o):
    return f_n(x) + " " + o + " " + f_n(y)


class Maths(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ans = None
        self.channel_id = None
        self.maths.start()
        self.remaining_winnings = []
        self.lock = asyncio.Lock()
        self.already_won = []
        self.operations = {
            "<:plus:831871106058944536>": lambda x, y: x+y,
            "<:minus:831871414481977465>": lambda x, y: x-y,
            "<:times:831871105652097129>": lambda x, y: x*y,
        }

    def cog_unload(self):
        self.maths.cancel()

    @tasks.loop(seconds=10)
    async def maths(self):
        await self.bot.wait_until_ready()
        self.maths.change_interval(
            minutes=random.randint(self.bot.config["min_minutes"], self.bot.config["max_minutes"]))
        if not self.ans:
            self.ans = 1
            return
        await self.do_quickmaths(self.bot.get_channel(self.bot.config["quickmaths"]))

    async def do_quickmaths(self, channel):
        async with self.lock:
            x = random.randint(10, 99)
            y = random.randint(10, 99)
            o = random.choice(list(self.operations))
            op = self.operations[o]
            self.ans = op(x, y)

            embed = discord.Embed(
                title="Quickmaths!",
                description=f"Solve this: \n{f_w(x, y, o)}\n and win Points!",
                color=discord.Color.blue()
            )
            embed.set_footer(
                text=f"1st place gets {self.bot.config['winnings'][0]} Points!")
            await channel.send(embed=embed)
            await channel.set_permissions(channel.guild.default_role, send_messages=True)
            self.channel_id = channel.id
            self.remaining_winnings = self.bot.config["winnings"][::]
            self.already_won = []

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def quickmaths(self, ctx):
        """
        Starts a quickmaths in the current channel
        """
        await self.do_quickmaths(ctx.channel)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.config["quickmaths"] and not message.author.bot:
            await message.delete()
        try:
            i = int(message.content)
        except:
            return
        if i == self.ans and message.channel.id == self.channel_id and message.author.id not in self.already_won:
            async with self.lock:
                if self.remaining_winnings != []:
                    win = self.remaining_winnings.pop(0)
                    user = message.author
                    try:
                        await user.send(f"**Congrats! You won {win} points!**")
                    except:
                        pass

                    r = await self.bot.db.points.find_one({"user": user.id})
                    if r:
                        await self.bot.db.points.find_one_and_update({"user": user.id}, {"$inc": {"points": win}})
                    else:
                        await self.bot.db.points.insert_one({"user": user.id, "points": win})
                    self.already_won.append(message.author.id)
                    if self.remaining_winnings == []:
                        await message.channel.send(embed=discord.Embed(color=discord.Color.blue(), title="Finished!", description=f"The answer was: {f_n(self.ans)}!").set_footer(text="All prizes have been rewarded"))
                        await message.channel.set_permissions(message.channel.guild.default_role, send_messages=False)


def setup(bot):
    bot.add_cog(Maths(bot))
