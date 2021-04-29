import discord
from discord.ext import commands, tasks
import re
from datetime import datetime, timedelta


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_processes = {}
        self.clear_processes.start()
    
    def cog_unload(self):
        self.clear_processes.cancel()

    @tasks.loop(seconds=10*60)
    async def clear_processes(self):
        self.last_processes = {}
    
    def process(self, message):
        if message.author.id not in self.last_processes:
            self.last_processes[message.author.id] = [message]
        self.last_processes[message.author.id].append(message)

    def is_duplicate(self, m):
        if len(self.last_processes[m.author.id]) < 3:
            return False
        m2 = self.last_processes[m.author.id][-2]
        m3 = self.last_processes[m.author.id][-3]
        return m.content.lower() == m2.content.lower() == m3.content.lower()

    def is_mention_spam(self, m):
        if len(self.last_processes[m.author.id]) < 2:
            return False
        m2 = self.last_processes[m.author.id][-2]
        for ment in m2.mentions:
            if ment in m.mentions:
                return True
        if len(m.mentions) > 2:
            return True
        return False

    def is_spam(self, message):
        if len(self.last_processes[message.author.id]) < 3:
            return False
        m2 = self.last_processes[message.author.id][-2]
        m3 = self.last_processes[message.author.id][-3]
        if (message.created_at - m3.created_at).seconds < 1:
            return True
        return False

    def is_caps(self, message):
        if len(message.content) < 5:
            return False 
        if message.content.upper() == message.content:
            return True
        p = 0
        for char in message.content:
            if char == char.upper():
                p+=1
        if (p/len(message.content)) > 0.7:
            return True
        return False
    
    def is_zalgo(self, message):
        return bool(re.search('[̀-ͯ᪰-᫿᷀-᷿⃐-⃿︠-︯]', message.content))
    
    @commands.Cog.listener()
    async def on_message(self, message):
        self.process(message)
        print(message)
        if self.is_zalgo(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Zalgo Usage.")
        if self.is_mention_spam(message):
            return await self.add_infraction(message.author, message.channel, reason="Mention Spam.")
        if self.is_duplicate(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Duplicate Messages.")
        if self.is_spam(message):
            await message.delete()
            return await self.add_infraction(message.author, message.channel, reason="Spamming.")
        if self.is_caps(message):
            return await self.add_infraction(message.author, message.channel, reason="Too many capital letters.")
        

    
    async def add_infraction(self, member, channel, moderator=None, reason="No given reason"):
        await self.bot.db.infractions.insert_one({
            "user": member.id,
            "moderator": moderator.id if moderator else None,
            "reason": reason,
            "time": datetime.utcnow()
        })
        infractions = len(await self.bot.db.infractions.find({"user":member.id}))
        embed = discord.Embed()
        embed.title = f"{member} has been warned!"
        embed.description = f"Reason: `{reason}`\nModerator: {moderator}"
        embed.color = discord.Color.red()
        await channel.send(embed=embed)
        try:
            embed.title = "You have been warned!"
            await member.send(embed=embed)
        except:
            pass
        mins = 0
        for i in self.bot.config["tempmute_after"]:
            mins = self.bot.config["tempmute_after"][i]
            if infractions == i:
                break
        if max(self.bot.config["tempmute_after"]) >= infractions:
            mins = max(self.bot.config["tempmute_after"].values())
        if mins > 0:
            await self.temp_mute(member, mins, channel, moderator, f"{infractions} infractions, are causing you to get temp muted for {mins} mins")
        

    async def temp_mute(self, member, mins, channel, moderator=None, reason="No given reason"):
        pass

def setup(bot):
    bot.add_cog(AutoMod(bot))