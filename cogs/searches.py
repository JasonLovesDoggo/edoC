import requests
from discord.ext.commands import CommandInvokeError

import discord
import wikipedia
from wikipedia.exceptions import WikipediaException
from discord.ext import commands
from utils import default
from utils.vars import *
from cogs.events import Error
# todo add a fuckton of elif's for the search commands so it just changes strings that the embed sends based off the cmd

def urlamazon(ctx):
    if ctx.invoked_with == "amazonCA":
        urlloco = ".ca"
    elif ctx.invoked_with == "amazonFR":
        urlloco = ".fr"
    elif ctx.invoked_with == "amazonCOM":
        urlloco = ".com"
    elif ctx.invoked_with == "amazonBR":
        urlloco = ".com.br"
    elif ctx.invoked_with == "amazonMX":
        urlloco = ".com.mx"
    elif ctx.invoked_with == "amazonCN":
        urlloco = ".cn"
    elif ctx.invoked_with == "amazonIN":
        urlloco = ".in"
    elif ctx.invoked_with == "amazonJP":
        urlloco = ".co.jp"
    elif ctx.invoked_with == "amazonSG":
        urlloco = ".sg"
    elif ctx.invoked_with == "amazonTR":
        urlloco = ".com.tr"
    elif ctx.invoked_with == "amazonAE":
        urlloco = ".ae"
    elif ctx.invoked_with == "amazonSA":
        urlloco = ".sa"
    elif ctx.invoked_with == "amazonDE":
        urlloco = ".de"
    elif ctx.invoked_with == "amazonIT":
        urlloco = ".it"
    elif ctx.invoked_with == "amazonNL":
        urlloco = ".nl"
    elif ctx.invoked_with == "amazonPL":
        urlloco = ".pl"
    elif ctx.invoked_with == "amazonES":
        urlloco = ".es"
    elif ctx.invoked_with == "amazonUK":
        urlloco = ".co.uk"
    elif ctx.invoked_with == "amazonAU":
        urlloco = ".com.au"
    return urlloco

async def embed_maker(ctx, url: str, icon: str, color: str, title: str):
    embed = discord.Embed(title=f"{title} search by edoC",
                          color=color,
                          timestamp=ctx.message.created_at)
    embed.set_author(name="edoC", icon_url=icon)
    embed.add_field(name="Link", value=url, inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)


class Searches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    @commands.command()#aliases=["yt"])
    async def youtube(self, ctx, *, search: str):
        """ ALL OF THESE SEARCH THE RESPECTIVE SITE """
        urlsafe = search.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={urlsafe}"
        icon = "https://i.imgur.com/9ue6lja.jpeg"
        color = red
        title = "Youtube"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def twitch(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.twitch.tv/search?term={urlsafe}"
        icon = "https://i.imgur.com/BFiwUxW.png"
        color = purple
        title = "Twitch"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def google(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.google.com/search?q={urlsafe}"
        icon = "https://i.imgur.com/YHDHKKG.png"
        color = green
        title = "Google"
        await embed_maker(ctx, url, icon, color, title)

#    @commands.command(aliases=["wikipedia"])
#    async def wiki(self, ctx, *, search: str):
#        urlsafe = search.replace(" ", "%20")
#        url = f"https://en.wikipedia.org/w/index.php?search={urlsafe}"
#        icon = "https://i.imgur.com/NBe9iIK.jpeg"
#        color = white
#        title = "Wikipedia"
#        await embed_maker(ctx, url, icon, color, title)

    @commands.command(
        aliases=["amazonBR", "amazonCA", "amazonMX", "amazonCOM", "amazonCN", "amazonIN", "amazonJP", "amazonSG",
                 "amazonTR", "amazonAE", "amazonSA", "amazonFR", "amazonDE", "amazonIT", "amazonNL", "amazonPL",
                 "amazonES", "amazonSE", "amazonUK", "amazonAU", ])
    async def amazon(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        try:
            urlloco = urlamazon(ctx)
        except UnboundLocalError:
            await ctx.reply(embed=discord.Embed(colour=red, description=f"You forgot to specify the type of amazon link you wanted\nplease refer to {ctx.prefix}help amazon for the types of links you can specify"))
            return
        url = f"https://www.amazon{urlloco}/s?k={urlsafe}"
        icon = "https://i.imgur.com/nrqpruo.jpeg"
        color = white
        title = "amazon"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command(aliases=["twtr"])
    async def twitter(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://twitter.com/search?q={urlsafe}"
        icon = "https://i.imgur.com/0mgjZpc.jpeg"
        color = blue
        title = "Twitter"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def fandom(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.fandom.com/?s={urlsafe}"
        icon = "https://i.imgur.com/8KaioFi.png"
        color = dark_blue
        title = "Fandom"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def imdb(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.imdb.com/find?q={urlsafe}"
        icon = "https://i.imgur.com/ZHx0Ypw.png"
        color = orange
        title = "IMDB"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def reddit(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.reddit.com/search/?q={urlsafe}"
        icon = "https://i.imgur.com/3O0V7U6.png"
        color = orange
        title = "Reddit"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command(aliases=["insta"])
    async def instagram(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.instagram.com/{urlsafe}"
        icon = "https://i.imgur.com/0E5UmAi.png"
        color = magenta
        title = "Instagram"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def ebay(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.ebay.ca/sch/i.html?_nkw={urlsafe}"
        icon = "https://i.imgur.com/BMVTDMb.png"
        color = white
        title = "Ebay"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def nytimes(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.nytimes.com/search?query={urlsafe}"
        icon = "https://i.imgur.com/nSOPlcF.jpeg"
        color = white
        title = "NyTimes"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def github(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://github.com/search?q={urlsafe}"
        icon = "https://i.imgur.com/jsGNdRQ.png"
        color = white
        title = "Github"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def microsoft(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.microsoft.com/en-ca/search?q={urlsafe}"
        icon = "https://i.imgur.com/zBhJ7Fx.png"
        color = blue
        title = "Microsoft"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def etsy(self, ctx, *, search: str):
        urlsafe = search.replace(" ", "%20")
        url = f"https://www.etsy.com/search?q={urlsafe}"
        icon = "https://i.imgur.com/G2GYNgm.png"
        color = orange
        title = "Etsy"
        await embed_maker(ctx, url, icon, color, title)

    @commands.command()
    async def skycrypt(self, ctx, *, ign: str):
        urlsafe = ign.replace(" ", "%20")
        url = f"https://sky.shiiyu.moe/stats/{urlsafe}"
        icon = "https://i.imgur.com/SVRO0zQ.png"
        color = green
        title = "SkyCrypt"
        await ctx.send(f"|| {url} ||")
        await embed_maker(ctx, url, icon, color, title)

    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, *query):
        try:
            thequery = " ".join(query)
            link = wikipedia.page(thequery)
            await ctx.reply(link.url)
        except WikipediaException:
            embed = discord.Embed(title="**Error!**",
                                  color=red,
                                  timestamp=ctx.message.created_at,
                                  description="Search is currently too busy. Please try again later")
            await ctx.reply(embed=embed)
#       yelp.com
#       walmart.com
#       craigslist.org

# pinterest https://www.pinterest.ca/search/pins/?q=

def setup(bot):
    bot.add_cog(Search(bot))
