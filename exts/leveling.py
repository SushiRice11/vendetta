import discord
from discord.ext import commands
import io

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.channel.id not in self.bot.config["levelbanned"]:
            await self.bot.leveling.proccess_xp(message)
    
    @commands.command()
    async def rank(self, ctx, member:discord.Member=None):
        if not member:
            member = ctx.author
        
        doc = await self.bot.leveling.get_rank_data(member)

        im = await self.bot.leveling.generate_rank_card(member, doc["xp"], doc["messages"], doc["level"], doc["rank"])


        embed = discord.Embed()
        embed.color = discord.Color.blue()
        embed.title = f"{member.name}'s Leveling Info!"
        embed.set_image(url="attachment://fancy.png")
        
        with io.BytesIO() as output:
            im.save(output, format="JPEG")
            output.seek(0)
            await ctx.send(file=discord.File(output, filename="fancy.png"), embed=embed)

def setup(bot):
    bot.add_cog(Leveling(bot))