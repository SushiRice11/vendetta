import discord
from discord.ext import commands, tasks
import random
import asyncio

def f_w(word):
    n = ""
    for letter in word:
        n+=":regional_indicator_%s: " % letter.lower()
    return n

class Unscramble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./unscramblewords.txt", "r") as f:
            ws = f.readlines()
        self.words = []
        for word in ws:
            self.words.append(word.replace("\n", ""))
        self.word = None
        self.channel_id = None
        self.unscrambler.start()
        self.remaining_winnings = []
        self.lock = asyncio.Lock()
        self.already_won = []
        self.last = random.choice(self.words)

    def cog_unload(self):
        self.unscrambler.cancel()

    @tasks.loop(seconds=10)
    async def unscrambler(self):
        await self.bot.wait_until_ready()
        self.unscrambler.change_interval(
            minutes=random.randint(self.bot.config["min_minutes"], self.bot.config["max_minutes"]))
        if not self.word:
            self.word = random.choice(self.words)
            return
        await self.do_unscramble(self.bot.get_channel(self.bot.config["unscramble"]))

    async def do_unscramble(self, channel):
        async with self.lock:
            self.last = self.word
            while self.word == self.last:
                self.word = random.choice(self.words)
            shuffled = self.word
            while shuffled == self.word:
                shuffled = list(self.word)
                random.shuffle(shuffled)
                shuffled = ''.join(shuffled)
            embed = discord.Embed(
                title="Unscramble!",
                description=f"Unscramble this: \n{f_w(shuffled)}\n and win Points!",
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
    async def unscramble(self, ctx):
        """
        Starts an unscramble in the current channel
        """
        await self.do_unscramble(ctx.channel)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.config["unscramble"] and not message.author.bot:
            await message.delete()
        if message.content.lower() == self.word.lower() and message.channel.id == self.channel_id and message.author.id not in self.already_won:
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
                        await message.channel.send(embed=discord.Embed(color=discord.Color.blue(), title="Finished!", description=f"The word was: {f_w(self.word)}!").set_footer(text="All prizes have been rewarded"))
                        await message.channel.set_permissions(message.channel.guild.default_role, send_messages=False)

    def save_words(self):
        with open("./unscramblewords.txt", "w") as f:
            f.write("\n".join(self.words))

    def reload_words(self):
        with open("./unscramblewords.txt", "r") as f:
            ws = f.readlines()
        self.words = []
        for word in ws:
            self.words.append(word.replace("\n", ""))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_word(self, ctx, word):
        self.words.append(word)
        self.save_words()
        await ctx.send("Word added!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def word_list(self, ctx):
        await ctx.author.send("\n".join(self.words))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fix_dupes(self, ctx):
        self.words = [w.lower() for w in self.words]
        self.words = list(set(self.words))
        self.save_words()
        await ctx.send("Words Fixed!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload_words(self, ctx):
        self.reload_words()
        await ctx.send("Reloaded")


def setup(bot):
    bot.add_cog(Unscramble(bot))
