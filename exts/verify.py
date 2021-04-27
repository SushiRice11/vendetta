import asyncio
from discord.ext import commands, tasks
from aiohttp import ClientTimeout
import discord
from helpers.hypixel import name_to_uuid, uuid_to_name


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_player_roles.start()

    def cog_unload(self):
        self.update_player_roles.cancel()

    async def get_guild_id(self, player):
        url = self.bot.config["linking"]["guild_endpoint"].format(player)
        async with self.bot.session.get(url, timeout=ClientTimeout(5)) as resp:
            return (await resp.json())["guild"]["_id"]

    async def get_player_discord(self, player):
        url = self.bot.config["linking"]["player_endpoint"].format(player)
        async with self.bot.session.get(url, timeout=ClientTimeout(5)) as resp:
            return (await resp.json())["player"]["socialMedia"]["links"]["DISCORD"]

    async def ensure_has_guild_role(self, member, player):
        try:
            guild_id = await self.get_guild_id(player)
        except:
            guild_id = ""
        roles_to_rm = []
        roles_to_add = []
        for guild in self.bot.config["linking"]["guilds"]:
            if guild["id"] == guild_id:
                roles_to_add.append(member.guild.get_role(guild["role"]))
            else:
                roles_to_rm.append(member.guild.get_role(guild["role"]))
        try:
            if roles_to_add:
                await member.add_roles(*roles_to_add)
        except:
            pass
        try:
            if roles_to_rm:
                await member.remove_roles(*roles_to_rm)
        except:
            pass

    @tasks.loop(seconds=60*15)
    async def update_player_roles(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(2)
        async for item in self.bot.db["links"].find({}):
            player = item["uuid"]
            member = self.bot.get_guild(
                self.bot.config["guild"]).get_member(item["user"])
            if not member:
                continue
            await self.ensure_has_guild_role(member, player)
            await asyncio.sleep(2)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id != self.bot.config["linking"]["channel"]:
            return
        await message.delete()
        try:
            uuid = await name_to_uuid(self.bot, message.content)
            memberdc = await self.get_player_discord(uuid)
        except:
            return await message.channel.send("**Player Not Found**", delete_after=5)
        print(memberdc)
        print(self.bot.config["linking"]["look_for"].format(message.author))
        if memberdc == self.bot.config["linking"]["look_for"].format(message.author):

            doc = await self.bot.db["links"].find_one({
                "user": message.author.id
            })
            if doc:
                return await message.channel.send(f"**Account already linked**", delete_after=5)
            doc = await self.bot.db["links"].find_one({
                "uuid": uuid
            })
            if doc:
                return await message.channel.send(f"**Minecraft already linked**", delete_after=5)

            await message.channel.send(f"**Linked with {message.content}**", delete_after=5)
            await self.bot.db["links"].insert_one({
                "user": message.author.id,
                "uuid": uuid
            })
            await self.ensure_has_guild_role(message.author, uuid)
        else:
            await message.channel.send("**Player Not Linked In Game**", delete_after=5)

    @commands.command()
    async def unlink(self, ctx):
        await self.bot.db["links"].find_one_and_delete({"user": ctx.author.id})
        await ctx.send("**Unlinked!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def force_unlink(self, ctx, member: discord.Member):
        await self.bot.db["links"].find_one_and_delete({"user": member.id})
        await ctx.send("**Unlinked!**")
    
    @commands.command()
    async def check_link(self, ctx, member:discord.Member=None):
        if not member:
            member = ctx.author

        doc = await self.bot.db["links"].find_one({
            "user": member.id
        })
        embed = discord.Embed()
        if not doc:
            embed.color = discord.Color.red()
            embed.title = "Not Linked!"
            embed.description = "We couldnt find a linked account, please use the verify channel!"
            return await ctx.send(embed=embed)
        name = await uuid_to_name(self.bot, doc["uuid"])
        embed.title = f"{member.name} is linked with {name}"
        embed.description = f"`{doc['uuid']}`: {name} is linked with {member.mention}"
        embed.color = discord.Color.blue()
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Verify(bot))
