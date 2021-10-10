# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os

import discord
import psutil
from discord.ext import commands

from utils.apis.openweathermap import *


class Weather(commands.Cog, description="Weather cmd"):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.process = psutil.Process(os.getpid())
        self.openweathermap_api_key = self.config["open_weather_map_api_key"]
        self.openweather = OpenWeatherAPI(
            key=self.openweathermap_api_key, session=self.bot.session
        )

    @commands.command(
        aliases=("w",),
        brief="Get current weather for specific city",
        extras=dict(example=("weather Palembang", "w London")),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, city):
        if not self.openweather.apiKey:
            return await ctx.error(
                "OpenWeather's API Key is not set! Please contact the bot owner to solve this issue."
            )

        try:
            weatherData = await self.openweather.get_from_city(city)
        except CityNotFound as err:
            return await ctx.error(str(err))

        e = discord.Embed(
            title=f"{weatherData.city}, {weatherData.country}",
            description=f"Feels like {weatherData.tempFeels.celcius}\N{DEGREE SIGN}C, {weatherData.weatherDetail}",
            colour=discord.Colour(0xEA6D4A),
        )
        e.set_author(
            name="OpenWeather",
            icon_url="https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/icons/logo_60x60.png",
        )
        e.add_field(
            name="Temperature", value=f"{weatherData.temp.celcius}\N{DEGREE SIGN}C"
        )
        e.add_field(name="Humidity", value=weatherData.humidity)
        e.add_field(name="Wind", value=str(weatherData.wind))
        e.set_thumbnail(url=weatherData.iconUrl)
        await ctx.try_reply(embed=e)


def setup(bot):
    bot.add_cog(Weather(bot))
