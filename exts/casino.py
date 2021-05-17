import discord
from discord.ext import commands
import random
from helpers.hypixel import is_linked

choices = {"🪨": 0, "📰": 1, "✂️": 2}


def rigged_coice(true, false):
    w = [True] * true + [False] * false
    return random.choice(w)

def roundhalf(x):
    return x // 2

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


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rig(self, ctx, member: discord.Member, win: int, loss: int):
        doc = await self.bot.db.rigged.find_one({"user": member.id})
        if doc:
            doc["win"] = win
            doc["loss"] = loss
            await self.bot.db.rigged.find_one_and_replace({"user": member.id}, doc)
        else:
            await self.bot.db.rigged.insert_one({"user": member.id, "win": win, "loss": loss})
        await ctx.send("||Rigged!||")

    @commands.command(aliases=["casino", "coinflip", "cf"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.cooldown(30, 45, commands.BucketType.guild)
    @is_linked()
    async def gamble(self, ctx, amount):
        r = await self.bot.db.points.find_one({"user": ctx.author.id})
        if not r:
            raise discord.DiscordException(
                "Please win first! You don't have any points!")

        try:
            amount = int(amount)
        except:
            if amount.lower() == "all":
                amount = r["points"]
            elif amount.lower() == "half":
                amount = roundhalf(r["points"])
            else:
                raise ValueError(amount)
        if r["points"] < amount:
            raise discord.DiscordException(
                "Not enough points! You don't have enough points!")

        if amount < 1:
            raise discord.DiscordException(
                "Negative points! You can't gamble negatives!")
        # doc = await self.bot.db.rigged.find_one({"user": ctx.author.id})
        win = rigged_coice(1, 1)
        # if doc:
        #    win = rigged_coice(doc["win"], doc["loss"])
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points": amount if win else 0 - amount}})
        embed = discord.Embed()
        embed.title = "You win!" if win else "Rip, you lost!"
        embed.description = f"You just won {amount} points! " if win else f"You just lost {amount} points! "

        embed.color = discord.Color.green() if win else discord.Color.red()
        await ctx.send(embed=embed)
        await self.bot.db.gambles.insert_one({
            "user": ctx.author.id,
            "points": amount,
            "win": win
        })

    @commands.command(aliases=["roll", "dice", "die"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    @commands.cooldown(30, 45, commands.BucketType.guild)
    @is_linked()
    async def dice_roll(self, ctx, prediction: int, amount="All"):
        r = await self.bot.db.points.find_one({"user": ctx.author.id})
        if not r:
            raise discord.DiscordException(
                "Please win first! You don't have any points!")

        try:
            amount = int(amount)
        except:
            amount = r["points"]
        if r["points"] < amount:
            raise discord.DiscordException(
                "Not enough points! You don't have enough points!")

        if amount < 1:
            raise discord.DiscordException(
                "Negative points! You can't gamble negatives!")
        if prediction not in range(1, 7):
            raise discord.DiscordException(
                "You need to choose a positive number")

        roll = random.randint(1, 6)
        win = False
        if prediction == roll:
            win = True

        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points": amount * 6 if win else 0 - amount}})
        embed = discord.Embed()
        embed.title = "You win!" if win else "Rip, you lost!"
        embed.description = f"You just won {amount*6} points! You guessed {prediction} which was also rolled!" if win else f"You just lost {amount} points! You guessed {prediction} and {roll} was rolled!"

        embed.color = discord.Color.green() if win else discord.Color.red()
        await ctx.send(embed=embed)

        await self.bot.db.rolls.insert_one({
            "user": ctx.author.id,
            "points": amount,
            "win": win,
            "prediction": prediction,
            "roll": roll
        })

    async def get_choice(self, user, channel, op):
        embed = discord.Embed()
        embed.title = "Rock Paper Scissors!"
        embed.description = "\n".join(list(choices.keys()))
        if op:
            embed.description = "\n".join(list(choices.keys())) + f"\n\n**Your opponent is {op.mention}!**"
        m = await channel.send(embed=embed)
        for e in list(choices.keys()):
            await m.add_reaction(e)
        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in list(choices.keys()) and r.message.id == m.id and u.id == user.id, timeout=15)
        return choices[str(r.emoji)]

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.cooldown(30, 10, commands.BucketType.guild)
    @is_linked()
    async def rps(self, ctx, amount="All", challenged: discord.Member = None):
        r = await self.bot.db.points.find_one({"user": ctx.author.id})
        if not r:
            raise discord.DiscordException(
                "Please win first! You don't have any points!")

        try:
            amount = int(amount)
        except:
            amount = r["points"]
        if r["points"] < amount:
            raise discord.DiscordException(
                "Not enough points! You don't have enough points!")

        if amount < 1:
            raise discord.DiscordException(
                "Negative points! You can't gamble negatives!")

        opponent_choice = random.choice(list(choices.values()))
        if not challenged:
            own_choice = await self.get_choice(ctx.author, ctx.channel, None)
        elif challenged:
            r = await self.bot.db.points.find_one({"user": challenged.id})
            if r["points"] < amount:
                raise discord.DiscordException("Not enough points! You dont have enough points!")
            own_choice = await self.get_choice(ctx.author, ctx.author, challenged)
            opponent_choice = await self.get_choice(challenged, challenged, ctx.author)
            
        r = await self.bot.db.points.find_one({"user": ctx.author.id})

        try:
            amount = int(amount)
        except:
            amount = r["points"]
        if r["points"] < amount:
            raise discord.DiscordException(
                "Not enough points! You don't have enough points!")

        if amount < 1:
            raise discord.DiscordException(
                "Negative points! You can't gamble negatives!")

        if challenged:
            r = await self.bot.db.points.find_one({"user": challenged.id})
            if r["points"] < amount:
                raise discord.DiscordException("Not enough points! You don't have enough points!")

        if own_choice == opponent_choice:
            embed = discord.Embed()
            embed.title = "Tie!"
            embed.description = f"It was a tie, both players chose {list(choices.keys())[own_choice]}"
            await ctx.send(embed=embed)
            if challenged:
                for u in challenged, ctx.author:
                    await u.send(embed=embed)
        elif (own_choice - 1 if own_choice > 0 else 2) == opponent_choice:
            embed = discord.Embed()
            embed.title = f"{ctx.author.name} Wins!"
            embed.description = f"{ctx.author.mention} chose {list(choices.keys())[own_choice]}\n{challenged.mention if challenged else 'Bot'} choose: {list(choices.keys())[opponent_choice]}"
            await ctx.send(embed=embed)
            await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points": amount}})

            if challenged:
                await self.bot.db.points.find_one_and_update({"user": challenged.id}, {"$inc": {"points": 0- amount}})
                for u in challenged, ctx.author:
                    await u.send(embed=embed)
        else:
            embed = discord.Embed()
            embed.title = f"{challenged.name if challenged else 'Bot'} Wins!"
            embed.description = f"{ctx.author.mention} choose {list(choices.keys())[own_choice]}\n{challenged.mention if challenged else 'Bot'} choose: {list(choices.keys())[opponent_choice]}"
            await ctx.send(embed=embed)
            await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points": 0 - amount}})
            if challenged:
                await self.bot.db.points.find_one_and_update({"user": challenged.id}, {"$inc": {"points": amount}})
                for u in challenged, ctx.author:
                    await u.send(embed=embed)
                    
    @commands.command(aliases=["dr", "daily"])
    @commands.cooldown(1, 60*60*24, commands.BucketType.user)
    @commands.cooldown(10, 45, commands.BucketType.guild)
    @is_linked()
    async def dailyreward(self, ctx):
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points":  15}}) 
        embed = discord.Embed() 
        embed.title = "Claimed Daily Reward"
        embed.description = "You Earned 15 Points!"

        embed.color = discord.Color.green() 
        await ctx.send(embed=embed)

    @commands.command(aliases=["hr", "hourly"])
    @commands.cooldown(1, 60*60, commands.BucketType.user)
    @commands.cooldown(10, 45, commands.BucketType.guild)
    @is_linked()
    async def hourlyreward(self, ctx):
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points":  5}}) 
        embed = discord.Embed() 
        embed.title = "Claimed Hourly Reward"
        embed.description = "You Earned 5 Points!"

        embed.color = discord.Color.green() 
        await ctx.send(embed=embed)


    @commands.command(aliases=["wr", "weekly"])
    @commands.cooldown(1, 60*60*24*7, commands.BucketType.user)
    @commands.cooldown(10, 45, commands.BucketType.guild)
    @is_linked()
    async def weeklyreward(self, ctx):
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points":  50}}) 
        embed = discord.Embed() 
        embed.title = "Claimed Weekly Reward"
        embed.description = "You Earned 50 Points!"

        embed.color = discord.Color.green() 
        await ctx.send(embed=embed)


    @commands.command(aliases=["mr", "monthly"])
    @commands.cooldown(1, 60*60*24*30, commands.BucketType.user)
    @commands.cooldown(10, 45, commands.BucketType.guild)
    @is_linked()
    async def monthlyreward(self, ctx):
        await self.bot.db.points.find_one_and_update({"user": ctx.author.id}, {"$inc": {"points":  200}}) 
        embed = discord.Embed() 
        embed.title = "Claimed Monthly Reward"
        embed.description = "You Earned 200 Points!"

        embed.color = discord.Color.green() 
        await ctx.send(embed=embed)

        

def setup(bot):
    bot.add_cog(Casino(bot))
