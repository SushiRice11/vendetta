import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from helpers.hypixel import name_to_uuid


class Tourney(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start_tourney(self, ctx, participant_role: discord.Role, tchannel: discord.TextChannel, year: int, month: int, day: int, hour: int, mins: int, tname, tdesc, tmaxpart: int, teamsize: int = 1):
        start_date = datetime(
            year, month, day, hour, mins, 0, tzinfo=timezone.utc)
        embed = discord.Embed()
        embed.color = discord.Color.blurple()
        embed.title = tname
        embed.description = f"""React with :crossed_swords: to sign up for the upcoming {tname}! 
        Starts at (UTC): {start_date}
        Max Participants: {tmaxpart} (You can still enter as a backup player, after this has been passed)
        Signed-up: 0
        Team Size: {teamsize} (Teams are randomly choosen)
        {tdesc}"""
        embed.set_footer(
            text="By reacting you agree to getting notified further about this tourney. You aren't garantueed an entry by reacting.")
        m = await tchannel.send(embed=embed)
        await m.add_reaction("⚔")
        await self.bot.db.tourneys.insert_one({
            "channel": tchannel.id,
            "start_date": start_date,
            "name": tname,
            "desc": tdsec,
            "max_size": tmaxpart,
            "team_size": teamsize,
            "signed_up": [],
            "message": m.id,
            "creator": ctx.author.id,
            "participant_role": participant_role.id
        })

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != "⚔" or not payload.member or payload.member.bot:
            return
        doc = await self.bot.db.tourneys.find_one({
            "channel": payload.channel_id,
            "message": payload.message_id,
        })
        if not doc or payload.user_id in [u["user"] for u in doc["signed_up"]]:
            return
        d = await self.bot.db["links"].find_one({
            "user": payload.user_id
        })
        if not d:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "Not Linked!"
            embed.description = "We couldnt find a linked account, please use the verify channel!"
            return await ctx.send(embed=embed, delete_after=3)
        name = await uuid_to_name(self.bot, d["uuid"])

        doc["signed_up"].append(d)
        role = payload.member.guild.get_role(doc["participant_role"])
        try:
            await payload.member.add_roles(role)
        except:
            pass
        try:
            await member.send(f"You joined the {doc['name']}")
        except:
            pass
        await self.bot.db.tourneys.find_one_and_update({"_id": doc["_id"]}, doc)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = discord.Embed()
        embed.color = discord.Color.blurple()
        embed.title = tname
        embed.description = f"""React with :crossed_swords: to sign up for the upcoming {tname}! 
        Starts at (UTC): {start_date}
        Max Participants: {tmaxpart} (You can still enter as a backup player, after this has been passed)
        Signed-up: {len(doc["signed_up"])}
        Team Size: {teamsize} (Teams are randomly choosen)
        {tdesc}"""
        embed.set_footer(
            text="By reacting you agree to getting notified further about this tourney. You aren't garantueed an entry by reacting.")
        m = await m.edit(embed=embed)


def setup(bot):
    bot.add_cog(Tourney(bot))
