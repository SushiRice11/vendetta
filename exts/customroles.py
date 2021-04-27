import discord
from discord.ext import commands
import random

class CustomRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_custom_role(self, ctx, member:discord.Member, role:discord.Role=None):
        if not role:
            role = await ctx.guild.create_role(name=f"{member.name}", color=discord.Color(random.randint(0x000000, 0xffffff)))
        x = (ctx.guild.me.top_role.position)
        try:
            await member.add_roles(role)
        except:
            pass

        await ctx.guild.edit_role_positions({
            role : x - 1
        })
        await self.bot.db.custom_roles.insert_one({
            "member": member.id,
            "role": role.id,
            "guild": member.guild.id
        })
        await ctx.send("Added!")

    @commands.group()
    async def role(self, ctx):
        if not ctx.invoked_subcommand:
            doc = await self.bot.db.custom_roles.find_one({
                "member": ctx.author.id
            })
            if not doc:
                raise discord.DiscordException("You dont have a custom role")
            guild = self.bot.get_guild(doc["guild"])
            role = guild.get_role(doc["role"])
            embed = discord.Embed(title="Your custom role!", description=f"Name: `{role.name}`\nColor: {role.color}", color=role.color)
            await ctx.send(embed=embed)
    
    @role.command(aliases=["colour"])
    async def color(self, ctx, color):
        doc = await self.bot.db.custom_roles.find_one({
            "member": ctx.author.id
        })
        if not doc:
            raise discord.DiscordException("You dont have a custom role")
        for r in (("0x", ""), ("#", "")):
            color = color.replace(*r)
        c = int(color, 16)
        color = discord.Color(value=c)
        #if color.r + color.b + color.g < 170:
        #    raise discord.DiscordException("Color too ugly! You cant have a color this bad.")
        guild = self.bot.get_guild(doc["guild"])
        role = guild.get_role(doc["role"]) 
        await role.edit(color=color)
        embed = discord.Embed(title="Your custom role!", description=f"Color updated: `{role.color}`", color=role.color)
        await ctx.send(embed=embed)

    @role.command()
    async def name(self, ctx, name):
        doc = await self.bot.db.custom_roles.find_one({
            "member": ctx.author.id
        })
        if not doc:
            raise discord.DiscordException("You dont have a custom role")
        guild = self.bot.get_guild(doc["guild"])
        role = guild.get_role(doc["role"]) 
        await role.edit(name=name)
        embed = discord.Embed(title="Your custom role!", description=f"Name updated: `{role.name}`", color=role.color)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(CustomRoles(bot))