import discord
from discord.ext import commands
import random
from PIL import Image

from io import BytesIO

from PIL import Image, ImageDraw, ImageOps, ImageFont
from io import BytesIO
from helpers.charts import create_pie_chart
from pymongo import DESCENDING


def to_str(num):
    if num < 1000:
        return str(num)
    if num < 100000:
        x = num/1000
        x = round(x, 1)
        return str(x) + "K"
    x = num/1000000
    x = round(x, 2)
    return str(x) + "M"


def c_xp(length):
    return random.randint(15, min(25, length+20))


class Leveling:
    def __init__(self, bot, db=None, session=None):
        self.bot = bot
        self.db = db or bot.db
        self.session = session or bot.session
        self.last_processes = {}

    @staticmethod
    def calc_level(xp):
        def next(l): return 5 * (l ** 2) + (50 * l) + 100
        i = 0
        while next(i) < xp:
            xp -= next(i)
            i += 1

        return i

    @staticmethod
    def progress(xp):
        def next(l): return 5 * (l ** 2) + (50 * l) + 100
        i = 0
        while next(i) < xp:
            xp -= next(i)
            i += 1

        return (xp, next(i)-xp)

    async def level_up(self, member, level):
        channel = self.bot.get_channel(self.bot.config["levelup"])
        await channel.send(f"{member.mention} is now level {level}!")

    async def proccess_xp(self, message):
        if message.author.id in self.last_processes and (message.created_at - self.last_processes[message.author.id]).seconds < 60:
            return
        xp = c_xp(len(message.content))

        self.last_processes[message.author.id] = message.created_at

        old = await self.db.leveling.find_one({
            "user": message.author.id
        })

        if not old:
            level = self.calc_level(xp)
            await self.db.leveling.insert_one({
                "user": message.author.id,
                "xp": xp,
                "level": level,
                "messages": 1
            })
        else:
            level = self.calc_level(old["xp"] + xp)
            if level > old["level"]:
                await self.level_up(message.author, level)
            await self.db.leveling.find_one_and_replace(old, {
                "user": message.author.id,
                "xp": old['xp'] + xp,
                "level": level,
                "messages": old['messages'] + 1
            })

    async def get_rank_data(self, member):
        d = await self.db.leveling.find_one({"user": member.id})
        if not d:
            raise discord.DiscordException("No data found")
        i = 0
        async for doc in self.db.leveling.find().sort("xp", DESCENDING):
            i += 1
            if doc["user"] == member.id:
                break
        d["rank"] = i
        return d

    async def generate_rank_card(self, member, xp, messages, level, rank):

        o = 20
        im = Image.open("./assets/minecraft.jpg")
        bg_layer = Image.new("RGBA", im.size, color=(24, 24, 24, 200))
        im.paste(bg_layer, (0, 0), bg_layer)
        asset = member.avatar_url_as(size=512, format="png")
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)

        mask = mask.resize(pfp.size, Image.BOX)
        pfp.putalpha(mask)
        pfp = pfp.resize((o*30, o*30))
        output = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        try:
            im.paste(pfp, (int(o*3), int(im.size[1]/2 - o * 25)), pfp)
        except:
            im.paste(pfp, (int(o*3), int(im.size[1]/2 - o * 25)))
        draw = ImageDraw.Draw(im)

        fontcolour = (244, 244, 244, 255)
        big = ImageFont.truetype("./assets/font.ttf", int(3.5*o))
        medium = ImageFont.truetype("./assets/font.ttf", int(3*o))
        small = ImageFont.truetype("./assets/font.ttf", 2*o)
        verybig = ImageFont.truetype("./assets/font.ttf", int(5*o))

        draw.text((int(im.size[1]/2 - o * 25), o*35),
                    f"{member} | #{rank}", font=big, fill=fontcolour)
        draw.text((int(3*o), o*40),
                    f"Level {level}", font=medium, fill=fontcolour)
        draw.text((int(3*o), o*44),
                    f"{to_str(xp)} XP", font=medium, fill=fontcolour)
        draw.text((int(3*o), o*48), f"{to_str(messages)} Messages",
                    font=medium, fill=fontcolour)

        draw.text((o*45, o*5), f"Progress to level {level+1}",
                    font=verybig, fill=fontcolour)

        chart = create_pie_chart(('', ''), self.progress(xp), colours=(
            (0, 190/255, 230/255), (.3, .3, .3)))
        r = 2
        chart = chart.resize(
            (int(chart.width*r), int(chart.height*r)), Image.NEAREST)

        im.paste(chart, (34*o, 10*o), chart)
        return im
