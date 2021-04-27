import discord
from discord.ext import commands

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        doc = await self.bot.db["reactionroles"].find_one({
            "message": payload.message_id,
            "emoji": str(payload.emoji)
        })
        if not doc or not payload.member:
            return
        member = payload.member

        role = member.guild.get_role(doc["role"])
        try:
            await member.add_roles(role)
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        doc = await self.bot.db["reactionroles"].find_one({
            "message": payload.message_id,
            "emoji": str(payload.emoji)
        })
        if not doc or not payload.member:
            return
        member = payload.member

        role = member.guild.get_role(doc["role"])
        try:
            await member.remove_roles(role)
        except:
            pass

    @commands.command()
    @commands.has_guild_permissions(manage_roles=True)
    async def reactionrole(self, ctx, message:discord.Message, role:discord.Role, emoji):
        await message.add_reaction(emoji)
        await self.bot.db["reactionroles"].insert_one({
            "creator": ctx.author.id,
            "message": message.id,
            "role": role.id,
            "emoji": str(emoji)
        })
        await ctx.send("**Added**", delete_after=3)
        await ctx.message.delete()

    @commands.command()
    @commands.has_guild_permissions(manage_roles=True)
    async def send_reaction_roles_embed(self, ctx):
        embed = discord.Embed()
        embed.title = "Parties"
        embed.description = \
            "Find the parties for all of your favorite games, " \
            "to start looking for parties go into the channels below. " \
            "If you would like to get notified whenever someone is looking for a party, react here!"

        games = [
            ":bed: Bedwars",
            ":island: SkyWars",
            ":question: Other"
        ]
        for game in games:
            embed.add_field(name=game, value="React to get pinged for %s" % game, inline=False)
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(ReactionRole(bot))
