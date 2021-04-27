import discord
from discord.ext import commands, tasks
import asyncio


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.send_initial_message.start()

    @tasks.loop(seconds=30 * 60)
    async def send_initial_message(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.bot.config["ticket_channel"])
        await channel.purge(limit=25)
        embed = discord.Embed()

        embed.title = "Create a report"
        embed.description = "Simply add a reaction here, to report a user. All reports are anonymous, unless they are abused."
        msg = await channel.send(embed=embed)
        for report_type in self.bot.config["ticket"]["types"]:
            embed.add_field(
                name=report_type["emoji"] + " " + report_type["name"],
                value=report_type["description"])
            await msg.add_reaction(report_type["emoji"])
            await msg.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.bot.wait_until_ready()
        await asyncio.sleep(2)
        if payload.channel_id == self.bot.config["ticket_channel"]:
            channel = self.bot.get_channel(self.bot.config["ticket_channel"])
            message = await channel.fetch_message(payload.message_id)
            member = await channel.guild.fetch_member(payload.user_id)
            if member.bot:
                return
            await message.remove_reaction(str(payload.emoji), member)
            if str(payload.emoji) not in [i["emoji"] for i in self.bot.config["ticket"]["types"]]:
                return

            report_type = [i for i in self.bot.config["ticket"]["types"] if i["emoji"] == str(payload.emoji)][0]

            cat = self.bot.get_channel(self.bot.config["ticket_category"])
            overwrites = {
                channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                channel.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                              manage_messages=True),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            nc = await channel.guild.create_text_channel(f"report-{member.name}", category=cat, overwrites=overwrites)

            embed = discord.Embed()
            embed.title = "Report started, Please answer the following quesitons"
            embed.description = "There is an option to cancel the report at the end."

            await nc.send(member.mention, embed=embed)

            try:
                ans = {}
                for q in self.bot.config["ticket"]["questions"]:
                    embed = discord.Embed()
                    embed.title = q["name"]
                    embed.description = q["question"]

                    await nc.send(embed=embed)
                    msg = await self.bot.wait_for("message",
                                                  check=lambda m: m.author.id == member.id and m.channel.id == nc.id,
                                                  timeout=60)
                    ans[q["name"]] = msg.content
                embed = discord.Embed()
                embed.title = "Do you want to submit this report?"
                embed.description = "React to confirm."
                m = await nc.send(embed=embed)
                await m.add_reaction("✅")
                await m.add_reaction("❎")

                def check(r, u):
                    return u.id == member.id and r.message.id == m.id and str(r.emoji) in ["✅", "❎"]

                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                if str(r.emoji) == "❎":
                    await nc.delete(reason="Report Ended.")
                    try:
                        await member.send("Your report was closed. You cancled it.")
                    except:
                        pass
                    return

                report_channel = self.bot.get_channel(self.bot.config["report_channel"])

                message = await report_channel.send(embed=discord.Embed(title="Report!"))
                embed = discord.Embed()
                embed.title = "Report!"
                embed.description = f"A report was sent, please look into it use the command +reveal_reporter {message.id}"

                embed.add_field(name="Report type", value=report_type["name"])
                for a in ans:
                    embed.add_field(name=a, value=ans[a])

                await message.edit(embed=embed)

                await self.bot.db["reports"].insert_one({
                    "reporter": member.id,
                    "answers": ans,
                    "message": message.id
                })

                await nc.delete(reason="Report sent.")

            except TimeoutError:
                await nc.delete(reason="Took to long.")
                try:
                    await member.send("Your report was closed. Took to long to respond.")
                except:
                    pass

    @commands.command(aliases=["rr", "who", "whoreported"])
    @commands.has_permissions(manage_messages=True)
    async def reveal_reporter(self, ctx, messageid:int):
        doc = await self.bot.db["reports"].find_one({
            "message": messageid
        })
        if not doc:
            await ctx.send("**Report not found**")
            return
        user = self.bot.get_user(doc["reporter"])

        if not user:
            await ctx.send(f"**Reporter left server, id: {doc['reporter']}**")
            return

        await ctx.send(f"The reporter was **{user.name}#{user.discriminator}** with the id *{user.id}*")


def setup(bot):
    bot.add_cog(Ticket(bot))
