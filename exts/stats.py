import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from helpers import charts
import io

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

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["gamblestats", "gs"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.cooldown(30, 30, commands.BucketType.guild)
    async def gstats(self, ctx, member:discord.Member=None):
        async with ctx.typing():
            if member:
                co = self.bot.db.gambles.find({"user": member.id})
            else:
                co = self.bot.db.gambles.find()
            wins = []
            losses = []
            async for doc in co:
                if doc["win"]:
                    wins.append(doc["points"])
                else:
                    losses.append(doc["points"])


            embed = discord.Embed()
            embed.color = discord.Color.blue()
            embed.title = "Gamble Stats"
            embed.description = f"Some epic gamer stats"

            embed.set_image(url="attachment://fancy.png")
            if member:
                im = self.generate_stats(wins, losses, member)
            else:
                im = self.generate_stats(wins, losses)
            with io.BytesIO() as output:
                im.save(output, format="JPEG")
                output.seek(0)
                await ctx.send(file=discord.File(output, filename="fancy.png"), embed=embed)

    def generate_stats(self, wins, losses, member="Overall"):
        if isinstance(member, discord.Member):
            member = member.name + "'s"
        bg = Image.open("home/ven/assets/minecraft.jpg")
        bg_layer = Image.new("RGBA", bg.size, color=(24, 24, 24, 240))
        bg.paste(bg_layer, (0, 0), bg_layer)
        draw = ImageDraw.Draw(bg)
        fontcolour = (244, 244, 244, 255)
        o = 40
        big = ImageFont.truetype("home/ven/assets/font.ttf", int(1.5*o))
        medium = ImageFont.truetype("home/ven/assets/font.ttf", int(1.25*o))
        small = ImageFont.truetype("home/ven/assets/font.ttf", o)
        verysmall = ImageFont.truetype("home/ven/assets/font.ttf", int(0.75*o))

        draw.text((o, o), f"{member} Wins", font=big, fill=fontcolour)
        draw.text((o, 3*o), to_str(len(wins)), font=small, fill=fontcolour)
        draw.text((15*o, o), f"{member} Losses", font=big, fill=fontcolour)
        draw.text((15*o, 3*o), to_str(len(losses)),
                  font=small, fill=fontcolour)
        draw.text((27*o, o), f"{member} Points Won", font=big, fill=fontcolour)
        draw.text((27*o, 3*o), to_str(sum(wins)),
                  font=small, fill=fontcolour)
        draw.text((o, 5.5*o), f"{member} Points Lost", font=big, fill=fontcolour)
        draw.text((o, 7.5*o), to_str(sum(losses)), font=small, fill=fontcolour)
        draw.text((15*o, 5.5*o), "W/L", font=big, fill=fontcolour)
        draw.text((15*o, 7.5*o), str(round(len(wins)/len(losses), 2)),
                  font=small, fill=fontcolour)
        draw.text((27*o, 5.5*o), "PW/L",
                  font=big, fill=fontcolour)
        draw.text((27*o, 7.5*o), str(round(sum(wins)/sum(losses), 2)),
                  font=small, fill=fontcolour)
    

        r = 1.5 # scaleing factor
        wlchart = charts.create_pie_chart(
            ("Wins", "Losses"), (len(wins), len(losses)), (0, 0), colours=((.3, .3, 1), (1, .3, .3)))
        wlchart = wlchart.resize(
            (int(wlchart.width*r), int(wlchart.height*r)), Image.NEAREST)
        bg.paste(wlchart, (int(0*o), int(10*o)), wlchart)       
        pwlchart = charts.create_pie_chart(
            ("Points Won", "Points Lost"), (sum(wins), sum(losses)), (0, 0), colours=((.3, .3, 1), (1, .3, .3)), rotation=30)
        pwlchart = pwlchart.resize(
            (int(pwlchart.width*r), int(pwlchart.height*r)), Image.NEAREST)
        bg.paste(pwlchart, (int(25*o), int(10*o)), pwlchart) 

        return bg

def setup(bot):
    bot.add_cog(Stats(bot))