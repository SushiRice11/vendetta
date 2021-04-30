from bson.objectid import ObjectId
import discord
from discord.ext import commands, tasks
import re
from datetime import datetime, timedelta
emojis = [
    '😄', '😃', '😀', '😊', '☺', '😉', '😍', '😘', '😚', '😗', '😙', '😜', '😝', '😛', '😳', '😁', '😔', '😌', '😒', '😞', '😣', '😢', '😂', '😭', '😪', '😥', '😰', '😅', '😓', '😩', '😫', '😨', '😱', '😠', '😡', '😤', '😖', '😆', '😋', '😷', '😎', '😴', '😵', '😲', '😟', '😦', '😧', '😈', '👿', '😮', '😬', '😐', '😕', '😯', '😶', '😇', '😏', '😑', '👲', '👳', '👮', '👷', '💂', '👶', '👦', '👧', '👨', '👩', '👴', '👵', '👱', '👼', '👸', '😺', '😸', '😻', '😽', '😼', '🙀', '😿', '😹', '😾', '👹', '👺', '🙈', '🙉', '🙊', '💀', '👽', '💩', '🔥', '✨', '🌟', '💫', '💥', '💢', '💦', '💧', '💤', '💨', '👂', '👀', '👃', '👅', '👄', '👍', '👎', '👌', '👊', '✊', '✌', '👋', '✋', '👐', '👆', '👇', '👉', '👈', '🙌', '🙏', '☝', '👏', '💪', '🚶', '🏃', '💃', '👫', '👪', '👬', '👭', '💏', '💑', '👯', '🙆', '🙅', '💁', '🙋', '💆', '💇', '💅', '👰', '🙎', '🙍', '🙇', '🎩', '👑', '👒', '👟', '👞', '👡', '👠', '👢', '👕', '👔', '👚', '👗', '🎽', '👖', '👘', '👙', '💼', '👜', '👝', '👛', '👓', '🎀', '🌂', '💄', '💛', '💙', '💜', '💚', '❤', '💔', '💗', '💓', '💕', '💖', '💞', '💘', '💌', '💋', '💍', '💎', '👤', '👥', '💬', '👣', '💭', '🐶', '🐺', '🐱', '🐭', '🐹', '🐰', '🐸', '🐯', '🐨', '🐻', '🐷', '🐽', '🐮', '🐗', '🐵', '🐒', '🐴', '🐑', '🐘', '🐼', '🐧', '🐦', '🐤', '🐥', '🐣', '🐔', '🐍', '🐢', '🐛', '🐝', '🐜', '🐞', '🐌', '🐙', '🐚', '🐠', '🐟', '🐬', '🐳', '🐋', '🐄', '🐏', '🐀', '🐃', '🐅', '🐇', '🐉', '🐎', '🐐', '🐓', '🐕', '🐖', '🐁', '🐂', '🐲', '🐡', '🐊', '🐫', '🐪', '🐆', '🐈', '🐩', '🐾', '💐', '🌸', '🌷', '🍀', '🌹', '🌻', '🌺', '🍁', '🍃', '🍂', '🌿', '🌾', '🍄', '🌵', '🌴', '🌲', '🌳', '🌰', '🌱', '🌼', '🌐', '🌞', '🌝', '🌚', '🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘', '🌜', '🌛', '🌙', '🌍', '🌎', '🌏', '🌋', '🌌', '🌠', '⭐', '☀', '⛅', '☁', '⚡', '☔', '❄', '⛄', '🌀', '🌁', '🌈', '🌊', '🎍', '💝', '🎎', '🎒', '🎓', '🎏', '🎆', '🎇', '🎐', '🎑', '🎃', '👻', '🎅', '🎄', '🎁', '🎋', '🎉', '🎊', '🎈', '🎌', '🔮', '🎥', '📷', '📹', '📼', '💿', '📀', '💽', '💾', '💻', '📱', '☎', '📞', '📟', '📠', '📡', '📺', '📻', '🔊', '🔉', '🔈', '🔇', '🔔', '🔕', '📢', '📣', '⏳', '⌛', '⏰', '⌚', '🔓', '🔒', '🔏', '🔐', '🔑', '🔎', '💡', '🔦', '🔆', '🔅', '🔌', '🔋', '🔍', '🛁', '🛀', '🚿', '🚽', '🔧', '🔩', '🔨', '🚪', '🚬', '💣', '🔫', '🔪', '💊', '💉', '💰', '💴', '💵', '💷', '💶', '💳', '💸', '📲', '📧', '📥', '📤', '✉', '📩', '📨', '📯', '📫', '📪', '📬', '📭', '📮', '📦', '📝', '📄', '📃', '📑', '📊', '📈', '📉', '📜', '📋', '📅', '📆', '📇', '📁', '📂', '✂', '📌', '📎', '✒', '✏', '📏', '📐', '📕', '📗', '📘', '📙', '📓', '📔', '📒', '📚', '📖', '🔖', '📛', '🔬', '🔭', '📰', '🎨', '🎬', '🎤', '🎧', '🎼', '🎵', '🎶', '🎹', '🎻', '🎺', '🎷', '🎸', '👾', '🎮', '🃏', '🎴', '🀄', '🎲', '🎯', '🏈', '🏀', '⚽', '⚾', '🎾', '🎱', '🏉', '🎳', '⛳', '🚵', '🚴', '🏁', '🏇', '🏆', '🎿', '🏂', '🏊', '🏄', '🎣', '☕', '🍵', '🍶', '🍼', '🍺', '🍻', '🍸', '🍹', '🍷', '🍴', '🍕', '🍔', '🍟', '🍗', '🍖', '🍝', '🍛', '🍤', '🍱', '🍣', '🍥', '🍙', '🍘', '🍚', '🍜', '🍲', '🍢', '🍡', '🍳', '🍞', '🍩', '🍮', '🍦', '🍨', '🍧', '🎂', '🍰', '🍪', '🍫', '🍬', '🍭', '🍯', '🍎', '🍏', '🍊', '🍋', '🍒', '🍇', '🍉', '🍓', '🍑', '🍈', '🍌', '🍐', '🍍', '🍠', '🍆', '🍅', '🌽', '🏠', '🏡', '🏫', '🏢', '🏣', '🏥', '🏦', '🏪', '🏩', '🏨', '💒', '⛪', '🏬', '🏤', '🌇', '🌆', '🏯', '🏰', '⛺', '🏭', '🗼', '🗾', '🗻', '🌄', '🌅', '🌃', '🗽', '🌉', '🎠', '🎡', '⛲', '🎢', '🚢', '⛵', '🚤', '🚣', '⚓', '🚀', '✈', '💺', '🚁', '🚂', '🚊', '🚉', '🚞', '🚆', '🚄', '🚅', '🚈', '🚇', '🚝', '🚋', '🚃', '🚎', '🚌', '🚍', '🚙', '🚘', '🚗', '🚕', '🚖', '🚛', '🚚', '🚨', '🚓', '🚔', '🚒', '🚑', '🚐', '🚲', '🚡', '🚟', '🚠', '🚜', '💈', '🚏', '🎫', '🚦', '🚥', '⚠', '🚧', '🔰', '⛽', '🏮', '🎰', '♨', '🗿', '🎪', '🎭', '📍', '🚩', '⬆', '⬇', '⬅', '➡', '🔠', '🔡', '🔤', '↗', '↖', '↘', '↙', '↔', '↕', '🔄', '◀', '▶', '🔼', '🔽', '↩', '↪', 'ℹ', '⏪', '⏩', '⏫', '⏬', '⤵', '⤴', '🆗', '🔀', '🔁', '🔂', '🆕', '🆙', '🆒', '🆓', '🆖', '📶', '🎦', '🈁', '🈯', '🈳', '🈵', '🈴', '🈲', '🉐', '🈹', '🈺', '🈶', '🈚', '🚻', '🚹', '🚺', '🚼', '🚾', '🚰', '🚮', '🅿', '♿', '🚭', '🈷', '🈸', '🈂', 'Ⓜ', '🛂', '🛄', '🛅', '🛃', '🉑', '㊙', '㊗', '🆑', '🆘', '🆔', '🚫', '🔞', '📵', '🚯', '🚱', '🚳', '🚷', '🚸', '⛔', '✳', '❇', '❎', '✅', '✴', '💟', '🆚', '📳', '📴', '🅰', '🅱', '🆎', '🅾', '💠', '➿', '♻', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '⛎', '🔯', '🏧', '💹', '💲', '💱', '〽', '〰', '🔝', '🔚', '🔙', '🔛', '🔜', '❌', '⭕', '❗', '❓', '❕', '❔', '🔃', '🕛', '🕧', '🕐', '🕜', '🕑', '🕝', '🕒', '🕞', '🕓', '🕟', '🕔', '🕠', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕡', '🕢', '🕣', '🕤', '🕥', '🕦', '✖', '➕', '➖', '➗', '♠', '♥', '♣', '♦', '💮', '💯', '✔', '☑', '🔘', '🔗', '➰', '🔱', '🔲', '🔳', '◼', '◻', '◾', '◽', '▪', '▫', '🔺', '⬜', '⬛', '⚫', '⚪', '🔴', '🔵', '🔻', '🔶', '🔷', '🔸', '🔹'
]
import asyncio

def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    Usage:
        # 149 day(s) 8 hr(s) 36 min 19 sec
        print human_delta(datetime(2014, 3, 30) - datetime.now())
    Example Results:
        23 sec
        12 min 45 sec
        1 hr(s) 11 min 2 sec
        3 day(s) 13 hr(s) 56 min 34 sec
    :param tdelta: The timedelta object.
    :return: The human formatted timedelta
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] == 0:
        fmt = '{sec} sec'
    elif d['hrs'] == 0:
        fmt = '{min} min'
    elif d['days'] == 0:
        fmt = '{hrs} hr(s) {min} min'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'

    return fmt.format(**d)


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_processes = {}
        self.last_infractions = {}
        self.last_caps = {}
        self.clear_processes.start()
        self.unmuter.start()

    def cog_unload(self):
        self.clear_processes.cancel()
        self.unmuter.cancel()

    @tasks.loop(seconds=10*60)
    async def clear_processes(self):
        self.last_processes = {}
        self.last_infractions = {}
        self.last_caps = {}

    def process(self, message):
        if message.author.id not in self.last_processes:
            self.last_processes[message.author.id] = [message]
        self.last_processes[message.author.id].append(message)

    def is_duplicate(self, m):
        if len(self.last_processes[m.author.id]) < 4:
            return False
        m2 = self.last_processes[m.author.id][-2]
        m3 = self.last_processes[m.author.id][-3]
        m4 = self.last_processes[m.author.id][-3]
        return m.content.lower() == m2.content.lower() == m3.content.lower() == m4.content.lower()


    def is_mention_spam(self, m):
        return False  # for some reason there is bug this is fix for now
        if m.reference:  # temporary fix for messages with refrence
            return False
        if len(self.last_processes[m.author.id]) < 2:
            return len(m.mentions) > 2
        m2 = self.last_processes[m.author.id][-2]
        for ment in m2.mentions:
            if ment in m.mentions:
                return True
        if len(m.mentions) > 2:
            return True
        return False

    def is_spam(self, message):
        if len(self.last_processes[message.author.id]) < 5:
            return False
        m5 = self.last_processes[message.author.id][-5]
        if (message.created_at - m5.created_at).seconds < 2:
            return True
        return False

    def is_caps(self, message):
        if len(message.content) < 10:
            return False
        if message.content.upper() == message.content != message.content.lower():
            return True
        p = 0
        for char in message.content:
            if char == char.upper() != char.lower():
                p += 1
        if (p/len(message.content)) > 0.7:
            return True
        return False

    def is_emoji_spam(self, message):
        found_emojis = []
        for word in message.content.split():
            if word.startswith("<:") or word.startswith("<a:"):
                found_emojis.append(word)
        for e in emojis:
            [found_emojis.append(0) for _ in range(message.content.count(e))]
        return len(found_emojis) > 5

    def is_zalgo(self, message):
        return bool(re.search('[̀-ͯ᪰-᫿᷀-᷿⃐-⃿︠-︯]', message.content))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return
        self.process(message)

        if self.is_zalgo(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Zalgo Usage.")
        if self.is_emoji_spam(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Emoji Spam.")
        if self.is_caps(message):
            if not message.author.id in self.last_caps:
                self.last_caps[message.author.id] = 0
                return await message.reply("Please dont use as many capital letters!")
            else:
                return await self.add_infraction(message.author, message.channel, reason="Too many capitals.")
        if message.author.id in self.last_infractions and (message.created_at - self.last_infractions[message.author.id]).seconds < 5:
            return
        if self.is_mention_spam(message):
            return await self.add_infraction(message.author, message.channel, reason="Mention Spam.")
        if self.is_duplicate(message) and not message.content.startswith(self.bot.config["preifx"]):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Duplicate Messages.")
        if self.is_spam(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Spamming.")

    async def add_infraction(self, member, channel, moderator=None, reason="No given reason"):
        self.last_infractions[member.id] = datetime.utcnow()
        await self.bot.db.infractions.insert_one({
            "user": member.id,
            "moderator": moderator.id if moderator else None,
            "reason": reason,
            "time": datetime.utcnow()
        })
        infractions = 0
        async for _ in self.bot.db.infractions.find({"user": member.id}):
            infractions += 1
        embed = discord.Embed()
        embed.title = f"{member} has been warned!"
        embed.description = f"Reason: `{reason}`\nModerator: {moderator}"
        embed.color = discord.Color.red()
        await channel.send(embed=embed)
        punishments = self.bot.get_channel(self.bot.config["punishments"])
        await punishments.send(embed=embed)
        try:
            embed.title = "You have been warned!"
            await member.send(embed=embed)
        except:
            pass
        mins = 0
        for i in self.bot.config["tempmute_after"]:
            if infractions == i:
                mins = self.bot.config["tempmute_after"][i]

        if max(self.bot.config["tempmute_after"]) <= infractions:
            mins = max(self.bot.config["tempmute_after"].values())
        if mins > 0:
            await self.temp_mute(member, mins, channel, moderator, f"{infractions} infractions, are causing you to get temp muted for {mins} mins")

    async def temp_mute(self, member, mins, channel, moderator=None, reason="No given reason"):
        role = member.guild.get_role(self.bot.config["muted_role"])
        await member.add_roles(role)
        await self.bot.db.mutes.insert_one({
            "user": member.id,
            "moderator": moderator.id if moderator else None,
            "reason": reason,
            "time": datetime.utcnow(),
            "active": True,
            "unmute_at": datetime.utcnow() + timedelta(minutes=mins)
        })
        embed = discord.Embed()
        embed.title = f"{member} has been muted for {mins} Minuites!"
        embed.description = f"Reason: `{reason}`\nModerator: {moderator}\nExpires: `{datetime.utcnow() + timedelta(minutes=mins)}`"
        embed.color = discord.Color.red()
        await channel.send(embed=embed)
        punishments = self.bot.get_channel(self.bot.config["punishments"])
        await punishments.send(embed=embed)
        try:
            embed.title = f"You have been muted for {mins} Minuites!"
            await member.send(embed=embed)
        except:
            pass

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, objid:ObjectId):
        await self.bot.db.infractions.find_one_and_delete({"_id": objid})
        await ctx.send("Done!")

    @tasks.loop(seconds=60)
    async def unmuter(self):
        print("unmuting...")
        await self.bot.wait_until_ready()
        await asyncio.sleep(2)
        async for mute in self.bot.db.mutes.find({"active": True}):
            if (datetime.utcnow() - mute["unmute_at"]) < timedelta(seconds=1):
                guild = self.bot.get_guild(self.bot.config["guild"])
                member = await guild.fetch_member(mute["user"])
                role = guild.get_role(self.bot.config["muted_role"])
                try:
                    await member.remove_roles(role)
                except:
                    pass
                mute["active"] = False
                await self.bot.db.mutes.find_one_and_replace({"_id": mute["_id"]}, mute)

        async for ban in self.bot.db.bans.find({"active": True}):
            if (datetime.utcnow() - ban["unban_at"]) < timedelta(seconds=1):
                guild = self.bot.get_guild(self.bot.config["guild"])
                user = self.bot.get_user(ban["user"])
                try:
                    await guild.unban(user)
                except:
                    pass
                ban["active"] = False
                await self.bot.db.mutes.find_one_and_replace({"_id": mute["_id"]}, mute)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, reason="No given reason."):
        if member.guild_permissions.manage_messages:
            return await ctx.message.reply("You cant kick a moderator.")
        embed = discord.Embed()
        embed.title = f"{member} has been kicked!"
        embed.description = f"Reason: `{reason}`\nModerator: {ctx.author}`"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        punishments = self.bot.get_channel(self.bot.config["punishments"])
        await punishments.send(embed=embed)
        try:
            embed.title = f"You have been kicked!"
            await member.send(embed=embed)
        except:
            pass
        await member.kick(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member, reason="No given reason."):
        if member.guild_permissions.ban_members:
            return await ctx.message.reply("You cant ban a moderator.")
        embed = discord.Embed()
        embed.title = f"{member} has been banned!"
        embed.description = f"Reason: `{reason}`\nModerator: {ctx.author}`"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        punishments = self.bot.get_channel(self.bot.config["punishments"])
        await punishments.send(embed=embed)
        try:
            embed.title = f"You have been banned!"
            await member.send(embed=embed)
        except:
            pass
        await member.ban(reason=reason)


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def tempban(self, ctx, member:discord.Member, mins:int, reason="No given reason."):
        if member.guild_permissions.manage_messages:
            return await ctx.message.reply("You cant kick a moderator.")
        embed = discord.Embed()
        embed.title = f"{member} has been kicked!"
        embed.description = f"Reason: `{reason}`\nModerator: {ctx.author}`"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        punishments = self.bot.get_channel(self.bot.config["punishments"])
        await punishments.send(embed=embed)
        try:
            embed.title = f"You have been kicked!"
            await member.send(embed=embed)
        except:
            pass
        await member.ban(reason=reason)
        await self.bot.db.mutes.insert_one({
            "user": member.id,
            "moderator": ctx.author.id,
            "reason": reason,
            "time": datetime.utcnow(),
            "active": True,
            "unban_at": datetime.utcnow() + timedelta(minutes=mins)
        })

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        mute = await self.bot.db.mutes.find_one({"active": True, "user": member.id})
        if not mute:
            return await ctx.send("This person is not mtued")
        role = member.guild.get_role(self.bot.config["muted_role"])
        try:
            await member.remove_roles(role)
        except:
            pass
        mute["active"] = False
        await self.bot.db.mutes.find_one_and_replace({"_id": mute["_id"]}, mute)
        await ctx.send("Unmuted!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, mins: int, reason="No given reason."):
        if member.guild_permissions.manage_messages:
            return await ctx.message.reply("You cant mute a moderator.")
        await self.temp_mute(member, mins, ctx.channel, moderator=ctx.author, reason=reason)

    @commands.command()
    async def infractions(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed()
        embed.title = f"{member}'s infractions!"
        infractions = []
        async for doc in self.bot.db.infractions.find({"user": member.id}):
            infractions.append(doc)

        embed.description = f"{member.mention} currently has {len(infractions)} infractions!"
        if len(infractions) > 0:
            embed.add_field(name=f"{member.name}'s last {min(10, len(infractions))} infractions",
                            value="\n".join([f"`{d['reason']}` - {human_delta(datetime.utcnow() - d['time'])} ago. Id: `{d['_id']}`" for d in infractions[-1:-10:-1]]))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No given reason"):
        if member.guild_permissions.manage_messages:
            return await ctx.message.reply("You cant warn a moderator.")
        await self.add_infraction(member, ctx.channel, moderator=ctx.author, reason=reason)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit:int, user:discord.User=None):
        await ctx.message.delete()
        await ctx.channel.purge(limit=limit, check=(lambda m: m.author.id == user.id) if user else None)
        await ctx.send("Done!", delete_after=3)

def setup(bot):
    bot.add_cog(AutoMod(bot))
