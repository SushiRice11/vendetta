import discord
from discord.ext import commands
import random
import asyncio
from helpers.hypixel import uuid_to_name

def convert_invite(invite):
    if isinstance(invite, str):
        return int(invite, 16)
    return str(hex(invite))[2::]


class Party:
    def __init__(self, bot, channel, _id, game, leader, players, player_limit, has_vc, description, vc=None,
                 public=False, public_channel=None, public_message=None, invites=[]):
        self.bot = bot
        self.id = _id
        self.channel = channel
        self.leader = leader
        self.game = game
        self.players = players
        self.player_limit = player_limit
        self.has_vc = has_vc
        self.vc = vc
        self.description = description
        self.public = public
        self.public_channel = public_channel
        self.public_message = public_message
        self.invites = invites

    async def disband(self):
        await self.channel.delete(reason="Party disbanded!")
        if self.vc:
            await self.vc.delete(reason="Party disbanded!")
        if self.public:
            await self.public_message.delete()
        await self.bot.db["parties"].find_one_and_delete({"id": self.id}, self.format())

    async def update(self):
        await self.bot.db["parties"].find_one_and_replace({"id": self.id}, self.format())
        if self.public:
            old_embed = self.public_message.embeds[0]
            embed = discord.Embed()
            embed.title = old_embed.title
            embed.description = old_embed.description
            embed.add_field(name=old_embed.fields[0].name, value=old_embed.fields[0].value)
            embed.add_field(name=old_embed.fields[1].name, value=f"{len(self.players)+1}/{self.player_limit}")
            embed.add_field(name=old_embed.fields[2].name, value=old_embed.fields[2].value)
            embed.add_field(name=old_embed.fields[3].name, value=old_embed.fields[3].value)
            await self.public_message.edit(embed=embed)

    async def join(self, member):
        if len(self.players) + 1 >= self.player_limit or member.id in [p.id for p in self.players] or member.id == self.leader.id:
            return
        self.players.append(member)
        await self.channel.set_permissions(member, read_messages=True, send_messages=True)
        if self.has_vc:
            await self.vc.set_permissions(member, view_channel=True, connect=True, speak=True)
        await self.update()
        await self.channel.send(f"Welcome, {member.mention} to the party!")

    async def leave(self, member):
        if member.id not in [p.id for p in self.players]:
            raise discord.NotFound(self.players, "Not found!")
        x = 0
        for i, p in enumerate(self.players):
            x = i
            if p.id == member.id:
                break
        else:
            self.players.pop(x)
        if member.id in [p.id for p in self.players]:
            self.players.remove(member)
        await self.channel.set_permissions(member, read_messages=False, send_messages=False)
        if self.has_vc:
            await self.vc.set_permissions(member, view_channel=False,  connect=False, speak=False)
        await self.update()
        await self.channel.send(f"{member.mention} just left the party!")

    async def invite(self, member):
        invite_id = random.randint(0, 16 ** 4)
        display_id = str(hex(invite_id))[2::]
        display_id = "".join(["0" for _ in range(4 - len(display_id))]) + display_id

        self_display_id = str(hex(self.id))[2::]
        self_display_id = "".join(["0" for _ in range(4 - len(self_display_id))]) + self_display_id

        await member.send(f"**You've Been Invited To {self.leader}'s party.**\nDo +accept {self_display_id} {display_id} to join!")
        self.invites.append(invite_id)
        await self.update()

    async def accept_invite(self, member, invite_id):
        invite_id = convert_invite(invite_id) if isinstance(invite_id,str) else invite_id
        if not invite_id in self.invites:
            return False
        self.invites.remove(invite_id)
        await self.join(member)

    async def deny_invite(self, member, invite_id):
        invite_id = convert_invite(invite_id) if isinstance(invite_id,str) else invite_id
        if not invite_id in self.invites:
            return False
        self.invites.remove(invite_id)
        await self.update()

    def format(self):
        return {
            "id": self.id,
            "channel": self.channel.id,
            "game": self.game,
            "leader": self.leader.id,
            "players": [p.id for p in self.players],
            "player_limit": self.player_limit,
            "has_vc": self.has_vc,
            "vc": self.vc.id if self.vc else None,
            "description": self.description,
            "public": self.public,
            "public_channel": self.public_channel.id if self.public_channel else None,
            "public_message": self.public_message.id if self.public_message else None,
            "invites": self.invites
        }

    @classmethod
    async def from_id(cls, bot, _id):
        data = await bot.db["parties"].find_one({"id": _id})
        channel = bot.get_channel(data["channel"])
        game = data["game"]
        leader = await bot.fetch_user(data["leader"])
        players = [channel.guild.get_member(p) for p in data["players"]]
        player_limit = data["player_limit"]
        has_vc = data["has_vc"]
        description = data["description"]
        vc = bot.get_channel(data["vc"])
        public = data["public"]
        public_channel = bot.get_channel(data["public_channel"])
        public_message = await public_channel.fetch_message(data["public_message"]) if public_channel else None
        invites = data["invites"]
        return cls(bot, channel, data["id"], game, leader, players, player_limit, has_vc, description, vc,
                 public, public_channel, public_message, invites)

    @classmethod
    async def from_channel(cls, bot, channel):
        data = await bot.db["parties"].find_one({"channel": channel.id})

        game = data["game"]
        leader = await bot.fetch_user(data["leader"])
        players = [channel.guild.get_member(p) for p in data["players"]]
        player_limit = data["player_limit"]
        has_vc = data["has_vc"]
        description = data["description"]
        vc = bot.get_channel(data["vc"])
        public = data["public"]
        public_channel = bot.get_channel(data["public_channel"])
        public_message = await public_channel.fetch_message(data["public_message"]) if public_channel else None
        invites = data["invites"]
        return cls(bot, channel, data["id"], game, leader, players, player_limit, has_vc, description, vc,
                 public, public_channel, public_message, invites)


    @classmethod
    async def new_party(cls, bot, game, role, leader, channel):
        _id = random.randint(0, 16 ** 4)
        display_id = str(hex(_id))[2::]
        display_id = "".join(["0" for _ in range(4 - len(display_id))]) + display_id
        party_channel = await leader.guild.create_text_channel(
            name=f"party-{display_id}",
            overwrites={
                leader.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                leader.guild.me: discord.PermissionOverwrite(read_messages=True),
                leader: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            },
            category=bot.get_channel(bot.config["parties"]),
            reason="New party!"
        )
        embed = discord.Embed()
        embed.title = "Welcome to your new party!"
        embed.description = "You will be asked some questions now about your party."
        await party_channel.send(leader.mention, embed=embed)
        embed = discord.Embed()
        embed.title = "Members"
        embed.description = "Please select how many people should be in this, party or select :1234: for a custom size!"
        msg = await party_channel.send(embed=embed)
        for i in ("2️⃣", "3️⃣", "4️⃣", "🔢"):
            await msg.add_reaction(i)

        r, u = await bot.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == msg and u.id == leader.id and str(r.emoji) in ("2️⃣", "3️⃣", "4️⃣", "🔢")
        )
        i = 0
        if str(r.emoji) == "2️⃣":
            i = 2
        elif str(r.emoji) == "3️⃣":
            i = 3
        elif str(r.emoji) == "4️⃣":
            i = 4
        if i == 0:
            embed = discord.Embed()
            embed.title = "How many members should there be"
            embed.description = "Please respond with a number between 5-40 here"
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            def check(m):
                try:
                    if not (4 < int(m.content) and int(m.content) < 41):
                        raise ValueError
                except ValueError:
                    return False
                return m.channel.id == msg.channel.id and m.author.id == leader.id

            m = await bot.wait_for("message", check=check)
            i = int(m.content)
        player_limit = i

        embed = discord.Embed()
        embed.title = "Description"
        embed.description = "Please give a brief party description, this will be showed if you make it public"
        await msg.clear_reactions()
        await msg.edit(embed=embed)

        def check(m):
            return m.channel.id == msg.channel.id and m.author.id == leader.id

        m = await bot.wait_for("message", check=check)

        description = m.content

        embed = discord.Embed()
        embed.title = "Voice Chat"
        embed.description = "Does this party need a vc? React with the corresponding emote"
        await msg.edit(embed=embed)
        await msg.clear_reactions()
        for i in ("✅", "❎"): await msg.add_reaction(i)
        r, u = await bot.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == msg and u.id == leader.id and str(r.emoji) in ("✅", "❎")
        )
        has_vc = False
        if str(r.emoji) == "✅":
            has_vc = True
        embed = discord.Embed()
        embed.title = "Public"
        embed.description = "Should this party be public?"
        await msg.edit(embed=embed)
        await msg.clear_reactions()
        for i in ("✅", "❎"): await msg.add_reaction(i)
        r, u = await bot.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == msg and u.id == leader.id and str(r.emoji) in ("✅", "❎")
        )
        public = False
        public_channel = None
        if str(r.emoji) == "✅":
            public = True
            public_channel = channel
        embed = discord.Embed(title="Done!", description="Your party has been created")
        await msg.edit(embed=embed)
        vc = None
        if has_vc:
            vc = await leader.guild.create_voice_channel(
                name=f"Party {display_id} VC",
                overwrites={
                    leader.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    leader.guild.me: discord.PermissionOverwrite(read_messages=True),
                    leader: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                },
                category=bot.get_channel(bot.config["parties"]),
                reason="New party!",
                user_limit=player_limit
            )
        public_message = None
        if public:
            embed = discord.Embed()
            embed.title = f"{game} party"
            embed.description = f"Join {leader.mention} Playing {game}! React with ✅ to join!"

            embed.add_field(name="Description", value=description)
            embed.add_field(name="Players", value="1/" + str(player_limit))
            embed.add_field(name="VC", value="This party has a vc!" if has_vc else "This party does not have a vc!")
            embed.add_field(name="ID", value=f"The party id is: {display_id}")

            public_message = await public_channel.send(role.mention, embed=embed)
            await public_message.add_reaction("✅")
        data = {
            "id": _id,
            "channel": party_channel.id,
            "game": game,
            "leader": leader.id,
            "players": [],
            "player_limit": player_limit,
            "has_vc": has_vc,
            "vc": vc.id if vc else None,
            "description": description,
            "public": public,
            "public_channel": public_channel.id if public_channel else None,
            "public_message": public_message.id if public_message else None,
            "invites": []
        }
        await bot.db["parties"].insert_one(data)
        return cls(bot, channel, id, game, leader, [], player_limit, has_vc,
                   description, vc, public, public_channel, public_message)

    @classmethod
    async def from_public_message(cls, bot, message):
        data = await bot.db["parties"].find_one({"public_message": message.id})
        if not data:
            return None
        channel = bot.get_channel(data["channel"])
        game = data["game"]
        leader = await bot.fetch_user(data["leader"])
        players = [channel.guild.get_member(p) for p in data["players"]]
        player_limit = data["player_limit"]
        has_vc = data["has_vc"]
        description = data["description"]
        vc = bot.get_channel(data["vc"])
        public = data["public"]
        public_channel = bot.get_channel(data["public_channel"])
        public_message = await public_channel.fetch_message(data["public_message"]) if public_channel else None
        invites = data["invites"]
        return cls(bot, channel, data["id"], game, leader, players, player_limit, has_vc, description, vc,
                 public, public_channel, public_message, invites)


class LookingForGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.p_cooldowns = []

    #@commands.command()
    async def send_initial_gaming_message(self, ctx, game, role: discord.Role):
        embed = discord.Embed()
        embed.title = "%s Parties" % game.capitalize()
        embed.description = "React to create a party for %s, below you will find a list of currently public parties" % game

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await self.bot.db["game_messages"].insert_one({
            "game": game,
            "message": msg.id,
            "role": role.id
        })

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member:
            return
        if payload.member.bot:
            return
        doc = await self.bot.db["game_messages"].find_one({
            "message": payload.message_id
        })
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if not doc:
            party = await Party.from_public_message(self.bot, message)
            if not party:
                return
            await message.remove_reaction(payload.emoji, payload.member)
            await party.join(payload.member)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)
        game = doc["game"]
        role = payload.member.guild.get_role(doc["role"])
        if payload.member.id in self.p_cooldowns:
            return
        self.p_cooldowns.append(payload.member.id)
        await Party.new_party(self.bot, game, role, payload.member, channel)
        await asyncio.sleep(60*60)
        self.p_cooldowns.remove(payload.member.id)

    #@commands.command()
    async def accept(self, ctx, party_id: convert_invite, invite_id: convert_invite):
        party = await Party.from_id(self.bot, party_id)
        if not party:
            raise discord.DiscordException("No party found")
        await party.accept_invite(ctx.author, invite_id)
        await ctx.send("Party joined!")

    #@commands.command()
    async def deny(self, ctx, party_id: convert_invite, invite_id: convert_invite):
        party = await Party.from_id(self.bot,party_id)
        if not party:
            raise discord.DiscordException("No party found")
        await party.deny_invite(ctx.author, invite_id)
        await ctx.send("Party Denied!")

    #@commands.command()
    async def invite(self, ctx, member: discord.Member):
        party = await Party.from_channel(self.bot, ctx.channel)
        if not party:
            raise discord.DiscordException("No party found")
        await party.invite(member)
        await ctx.send("**Invited!**")

    @commands.command()
    async def leave(self, ctx):
        party = await Party.from_channel(self.bot, ctx.channel)
        if not party:
            raise discord.DiscordException("No party found")
        await party.leave(ctx.author)

    @commands.command()
    async def disband(self, ctx):
        party = await Party.from_channel(self.bot, ctx.channel)
        if not party:
            raise discord.DiscordException("No party found")
        if ctx.author.id == party.leader.id or ctx.author.guild_permissions.administrator:
            await party.disband()
        else:
            await ctx.send("**Only the party leader (or admins) can do this!**")

    @commands.command()
    async def party_kick(self, ctx, member:discord.Member):
        party = await Party.from_channel(self.bot, ctx.channel)
        if not party:
            raise discord.DiscordException("No party found")
        if ctx.author.id == party.leader.id or ctx.author.guild_permissions.administrator:
            await party.leave(member)
        else:
            await ctx.send("**Only the party leader (or admins) can do this!**")

    async def has_pl_role(self, ctx):
        return any([role.id == self.bot.config["pleader"] for role in ctx.author.roles])

    @commands.command()
    @commands.check(has_pl_role)
    async def start_party(self, ctx, *, description):
        

        doc = await self.bot.db["links"].find_one({
            "user": ctx.author.id
        })
        embed = discord.Embed()
        if not doc:
            embed.color = discord.Color.red()
            embed.title = "Not Linked!"
            embed.description = "We couldnt find a linked account, please use the verify channel!"
            return await ctx.send(embed=embed)
        name = await uuid_to_name(self.bot, doc["uuid"])
        embed.title = f"{name} is hosting a public party"
        embed.description = f"{description} ```/p join {name}```"
        embed.color = discord.Color.blue()
        pchannel = self.bot.get_channel(self.bot.config["pchannel"])
        await pchannel.send(embed=embed)
        await ctx.send("Done!")

def setup(bot):
    bot.add_cog(LookingForGame(bot))
