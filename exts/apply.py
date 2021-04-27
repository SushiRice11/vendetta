import discord
from discord.ext import commands, tasks
import random
import asyncio
from helpers.hypixel import name_to_uuid, uuid_to_name
from aiohttp import ClientTimeout

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.send_initial_message.start()

    def cog_unload(self):
        self.send_initial_message.cancel()

    async def get_guild_id(self, player):
        url = self.bot.config["linking"]["guild_endpoint"].format(player)

        async with self.bot.session.get(url, timeout=ClientTimeout(5)) as resp:
            data = (await resp.json())
            return data["guild"]["_id"]

    async def check_if_in_guild(self, player):
        try:
            guild_id = await self.get_guild_id(player)
        except:
            guild_id = ""
        r = []
        for guild in self.bot.config["linking"]["guilds"]:
            if guild["id"] == guild_id:
                r.append("in guild")

        print(r)
        print(guild_id)
        print(self.bot.config["linking"]["guilds"])
        return len(r) > 0 

    @tasks.loop(seconds=30 * 60)
    async def send_initial_message(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.bot.config["apply_channel"])
        await channel.purge(limit=25)
        embed = discord.Embed()

        embed.title = "Apply"
        embed.description = "To apply to join our guild or apply for helper, react below, you need to be verified! If you are in our guild, your application will automatically be for helper, otherwise you will apply to join our guild."
        msg = await channel.send(embed=embed)

        await msg.add_reaction("✅")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == self.bot.config["apply_channel"]:
            if not payload.member:
                return
            if payload.member.bot:
                return
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = payload.member
            if not member:
                return
            await message.remove_reaction(str(payload.emoji), member)

            doc = await self.bot.db.links.find_one({"user": member.id})
            if not doc:
                return await channel.send("**Please Link Your Account First!**", delete_after=3)

            uuid = doc["uuid"]
            ign = await uuid_to_name(self.bot, uuid)
            cat = self.bot.get_channel(self.bot.config["app_category"])

            overwrites = {
                channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                channel.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                              manage_messages=True),
                member: discord.PermissionOverwrite(
                    read_messages=True, send_messages=True)
            }

            apply_for_staff = await self.check_if_in_guild(uuid)

            nc = await channel.guild.create_text_channel(f"app-{member.name}", category=cat, overwrites=overwrites)
            if not apply_for_staff:
                try:
                    embed = discord.Embed()
                    embed.title = "Welcome to your Application"
                    embed.description = "You now need to answer some basic questions."

                    await nc.send(member.mention, embed=embed)

                    embed = discord.Embed()
                    embed.title = "Timezone"
                    embed.description = "Which timezone are you in, eg. GMT, CET?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    timezone = msg.content

                    embed = discord.Embed()
                    embed.title = "Why do you want to join us?"
                    embed.description = "How did you find our guild? What makes you interested?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    why = msg.content

                    embed = discord.Embed()
                    embed.title = "Can you be able to reach the guild requirement of %s?" % self.bot.config[
                        "req_xp"]
                    embed.description = \
                        "If yes, tell us how much xp you'll get on average, and if not, why not and how much you can get!"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    xpreq = msg.content

                    embed = discord.Embed()
                    embed.title = "Tell us a joke"
                    embed.description = "Whats your best joke?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    joke = msg.content

                    embed = discord.Embed()
                    embed.title = "Can you join our waitlist guild?"
                    embed.description = "If you cant, you wont be able to join our main guild."

                    mesg = await nc.send(embed=embed)
                    for e in ("✅", "❎"):
                        await mesg.add_reaction(e)
                    r = None
                    r, u = await self.bot.wait_for("reaction_add",
                                                check=lambda r, u: u.id == member.id and r.message.id == mesg.id and str(
                                                    r.emoji) in ("✅", "❎"),
                                                timeout=60*10)
                    waitlist = str(r.emoji) == "✅"
                except:
                    await nc.delete(reason="Application Timed Out!")
                    await member.send("Application Timed Out!")
                    return

                await nc.send("**Application Submitted! This channel will be deleted in 5 seconds!**")

                embed = discord.Embed()
                embed.title = "Application!"
                embed.description = "A new application has come in!"
                embed.color = discord.Color(random.randint(0x000000, 0xffffff))

                embed.add_field(name="IGN", value=uuid + " | " + ign, inline=True)
                embed.add_field(name="Discord", value=member.mention, inline=True)
                embed.add_field(name="Timezone", value=timezone, inline=False)
                embed.add_field(name="Reason for joining", value=why, inline=False)
                embed.add_field(name="XP requirement", value=xpreq, inline=False)
                embed.add_field(name="Waitlist join", value=waitlist, inline=False)
                applications = self.bot.get_channel(
                    self.bot.config["applications"])
                m = await applications.send(embed=embed)
                await m.add_reaction("🤗")
                await asyncio.sleep(5)
                await nc.delete(reason="Application Finished!")
            else:
                try:
                    embed = discord.Embed()
                    embed.title = "Welcome to your Application"
                    embed.description = "You now need to answer some qusetions on why you want to become helper."

                    await nc.send(member.mention, embed=embed)

                    embed = discord.Embed()
                    embed.title = "Reason"
                    embed.description = "Why do you want to become a helper? What qualifies you?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    reason = msg.content



                    embed = discord.Embed()
                    embed.title = "Why Are You better?"
                    embed.description = "What puts you above other applicants? Why should we choose you?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    better = msg.content

                    embed = discord.Embed()
                    embed.title = "Referals"
                    embed.description = "Do you have any past expirience with moderating? What other servers have you / are you moderating?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    referals = msg.content


                    embed = discord.Embed()
                    embed.title = "Senario One: Ping Spam"
                    embed.description = "Someone is mentioning other users in the chat, repetedly and randomly. How do you react as a helper?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    s1 = msg.content

                    embed = discord.Embed()
                    embed.title = "Senario Two: Doxxing"
                    embed.description = "Someone is sending private/personal information about another member. How do you react as a helper?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    s2 = msg.content

                    embed = discord.Embed()
                    embed.title = "Senario Three: Toxicity"
                    embed.description = "Someone is being toxic in chat, lightly swearing at others and calling people bad. How do you react as a helper?"

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                timeout=60*10)
                    s3 = msg.content
                    await nc.send("**Application Submitted! This channel will be deleted in 5 seconds!**")

                    embed = discord.Embed()
                    embed.title = "Application!"
                    embed.description = "A new application for helper has come in! Current status: 'POSTED'"
                    embed.color = discord.Color(0x0000ff)

                    embed.add_field(name="IGN", value=uuid + " | " + ign, inline=True)
                    embed.add_field(name="Discord", value=member.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Better than others", value=better, inline=False)
                    embed.add_field(name="Referals", value=referals, inline=False)
                    embed.add_field(name="Senario One: Ping Spamming", value=s1, inline=False)
                    embed.add_field(name="Senario Two: Doxxing", value=s2, inline=False)
                    embed.add_field(name="Senario Threee: Toxicity", value=s3, inline=False)
                    applications = self.bot.get_channel(
                        self.bot.config["helper_apps"])
                    m = await applications.send(embed=embed)
                    for e in ("✅", "❎"): await m.add_reaction(e)
                    await self.bot.db.helper_apps.insert_one({
                        "user": member.id,
                        "answers": {
                            "reason": reason,
                            "better": better,
                            "referals": referals,
                            "s1": s1,
                            "s2": s2,
                            "s3": s3
                        },
                        "status": "POSTED",
                        "message": m.id,
                        "deny_reason": None
                    })
                    await asyncio.sleep(5)
                    await nc.delete(reason="Application Finished!")
                except:
                    await nc.delete(reason="Application Timed Out!")
                    await member.send("Application Timed Out!")
                    return
        doc = await self.bot.db.helper_apps.find_one({
            "message": payload.message_id,
            "status": "POSTED"
        })
        if not doc:
            return
        if not payload.member:
            return
        if payload.member.bot:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = payload.member
        if not member:
            return
        await message.remove_reaction(str(payload.emoji), member)

        if str(payload.emoji) in ("✅", "❎"):
            await message.clear_reactions()
            member = channel.guild.get_member(doc["user"])
            if str(payload.emoji) == "✅":
                color = discord.Color(0x00ff00)
                doc["status"] = "ACCEPTED"
                role = channel.guild.get_role(self.bot.config["helper_role"])
                await member.add_roles(role)
                try:
                    embed = discord.Embed(color=color)
                    embed.title = "Application Accepted!"
                    embed.description = "Your application has been accepted, and you have been added to the staff team."
                    await member.send(embed=embed)
                except:
                    pass
            else:
                color = discord.Color(0xff0000)
                await channel.send("**Please enter a reason for denial**, if you dont enter one in 30 seconds, it will default to none given.", delete_after=30)
                try:
                    m = await self.bot.wait_for("message", check=lambda m: m.author.id == member.id and m.channel.id == channel.id, timeout=30)
                    doc["deny_reason"] = m.content
                except:
                    doc["deny_reason"] = "No Given Reason!"
                try:
                    embed = discord.Embed(color=color)
                    embed.title = "Application Denied!"
                    embed.description = "Your application has been denied, you may re-apply in 3 months. Reason: '%s'" % doc["deny_reason"]
                    await member.send(embed=embed)
                except:
                    pass
                doc["status"] = "DENIED"

            await self.bot.db.helper_apps.find_one_and_replace({
            "message": payload.message_id,
            "status": "POSTED"
            }, doc)
            embed = message.embeds[0]
            embed.color = color
            embed.description = "Application! Current status: '%s'" % doc["status"]
            await message.edit(embed=embed)
        

    
def setup(bot):
    bot.add_cog(Apply(bot))
