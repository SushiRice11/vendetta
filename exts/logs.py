import discord
from discord.ext import commands
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages, self.user, self.punishment = None, None, None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Saving log channels...")
        self.messages = self.bot.get_channel(self.bot.config["logs"]["messages"])
        self.user = self.bot.get_channel(self.bot.config["logs"]["user"])
        self.punishment = self.bot.get_channel(self.bot.config["logs"]["punishment"])
    

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        embed = discord.Embed(title=f"Message sent by {message.author} deleted!", description=f"**Channel**: {message.channel.mention}\n**Content**:\n{message.content}", color=discord.Color.red())
        embed.timestamp = datetime.now()
        await self.messages.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, b, a):
        embed = discord.Embed(title=f"(Message)[{a.jump_url}] sent by {a.author} edited!", description=f"**Channel**: {a.channel.mention} \n**Before**:\n{b.content}\n**After**:\n{a.content}", color=discord.Color.yellow())
        embed.timestamp = datetime.now()
        await self.messages.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(description=f"**Created At**: {member.created_at}", color=discord.Color.green())
        embed.set_author(name=f"{member} Joined!", icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.now()
        await self.user.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(description=f"**ID**: {member.id}", color=discord.Color.red())
        embed.set_author(name=f"{member} Left!", icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.now()
        await self.user.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_update(self, b, a):
        if b.nick != a.nick:
            embed = discord.Embed(description=f"**Before**: {b.nick}\n**After**: {a.nick}", color=discord.Color.red())
            embed.set_author(name=f"{a} Nickname Changed!", icon_url=a.avatar_url)
            embed.set_thumbnail(url=a.avatar_url)
            embed.timestamp = datetime.now()
            await self.user.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))