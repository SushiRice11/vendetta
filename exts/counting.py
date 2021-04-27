import discord
from discord.ext import commands, tasks
from discord import Webhook, AsyncWebhookAdapter

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_num = -1
        self.fetch_num.start()

    def cog_unload(self):
        self.fetch_num.cancel()

    @tasks.loop(seconds=60*1)
    async def fetch_num(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.bot.config["counting_channel"])
        async for message in channel.history(limit=100):
            try:
                self.current_num = int(message.content)
                break
            except ValueError:
                continue
        if self.current_num == -1:
            self.current_num = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.config["counting_channel"] and not message.author.bot:
            await message.delete()
            try:
                if int(message.content) != self.current_num + 1:
                    raise ValueError
            except ValueError:
                webhook = Webhook.from_url(self.bot.config["counting_webhookurl"],
                                           adapter=AsyncWebhookAdapter(self.bot.session))
                await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url)
                self.current_num = 0
                await message.channel.send("Looks like someone made a mistake! Lets start again:")
                await message.channel.send("0")
                return
            webhook = Webhook.from_url(self.bot.config["counting_webhookurl"], adapter=AsyncWebhookAdapter(self.bot.session))
            await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url)
            self.current_num += 1

def setup(bot):
    bot.add_cog(Counting(bot))