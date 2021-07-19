import os
import psutil
import requests
from discord.ext import commands
from edoC.utils import default
import discord
from edoC.utils.vars import *


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())
        self.openweathermap_api = self.config["open_weather_map_api_key"]

    @commands.command(aliases=["w"])
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def weather(self, ctx, *, city: str):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = city
        weather_key = self.config["open_weather_map_api_key"]
        complete_url = base_url + "appid=" + weather_key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()
        channel = ctx.message.channel
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsius = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            e = discord.Embed(title=f"Weather in {city_name}",
                              color=blue,
                              timestamp=ctx.message.created_at, )
            e.add_field(name="Description", value=f"{weather_description}", inline=False)
            e.add_field(name="Temperature(C)", value=f"{current_temperature_celsius}C", inline=False)
            e.add_field(name="Humidity(%)", value=f"{current_humidity}%", inline=False)
            e.add_field(name="Atmospheric Pressure(hPa)", value=f"{current_pressure}hPa", inline=False)
            e.set_footer(text=f"Requested by {ctx.author.name}")
            e.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png%22")
            e.set_footer(text=f"Requested by {ctx.author.name}\n{embedfooter}")
            await channel.send(embed=e)
        elif x["cod"] == "404":
            await channel.send(ErrorEmbed(ctx, "City Not Found"))


def setup(bot):
    bot.add_cog(Weather(bot))
