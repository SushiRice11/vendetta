import discord
from discord.ext import commands
import yaml


class Loader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, cog):
        if not cog.startswith("exts."):
            cog = "exts." + cog
        self.bot.unload_extension(cog)
        await ctx.send("Success!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, cog):
        if not cog.startswith("exts."):
            cog = "exts." + cog
        self.bot.load_extension(cog)
        await ctx.send("Success!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, cog):
        if not cog.startswith("exts."):
            cog = "exts." + cog
        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)
        await ctx.send("Success!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload_config(self, ctx):
        self.bot.config = yaml.safe_load(open("config.yaml", "r").read())

        await ctx.send("Success!")

def setup(bot):
    bot.add_cog(Loader(bot))