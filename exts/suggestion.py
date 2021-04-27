from discord.ext import commands
import discord

class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.channel.id == self.bot.config["suggestion"]:
            if message.reference:
                r = await message.channel.fetch_message(message.reference.message_id)
                if r.author.id == self.bot.user.id:
                    await message.delete()
                    embed = r.embeds[0]
                    embed.add_field(name=f"Reply by {message.author}", value=message.content)
                    await r.edit(embed=embed)
                
                return
            await message.delete()
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = f"Suggestion by {message.author.name}"
            embed.description = message.content

            m = await message.channel.send(embed=embed)
            for e in ("👍", "👎"): await m.add_reaction(e)

def setup(bot):
    bot.add_cog(Suggestion(bot))