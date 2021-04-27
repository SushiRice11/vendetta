import discord
from discord.ext import commands

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title=f"Error!", colour=discord.Colour(0xff0000), description=f"You dont have permission to do that!")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            time = str(error)
            time = str(time.replace('You are on cooldown. Try again in "', " "))
            embed = discord.Embed(title=f"Error!", colour=discord.Colour(0xff0000), description=f"You have to wait {time} before you can do that!")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Error! Something happend!", colour=discord.Colour(0xff0000), description=f"```{error}```")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Error(bot))