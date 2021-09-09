# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from urllib.parse import quote_plus

import discord
from discord.app import Option
from discord.ext import commands


class Counter(discord.ui.View):

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f'https://www.google.com/search?q={query}'

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))


class Test(commands.Cog, description='Testing cog for... testing'):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('google')

        @bot.slash_command()
        async def hello(
                ctx,
                name: Option(str, "Enter your name"),
                gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
                age: Option(int, "Enter your age", required=False, default=18),
        ):
            await ctx.send(f"Hello {name}")

        @bot.command()
        async def google(ctx, *, query: str):
            """Returns a google link for a query"""
            await ctx.send(f'Google Result for: `{query}`', view=Google(query))

        @bot.command()
        async def counter(ctx):
            """Starts a counter for pressing."""
            await ctx.send('Press!', view=Counter())

        @bot.command()
        async def top(ctx):
            await ctx.reply("please wait ...")
            from bs4 import BeautifulSoup
            import requests
            def GETC():
                url = f'https://www.google.com/search?q=bitcoin+price'
                HTML = requests.get(url)
                soup = BeautifulSoup(HTML.text, 'html.parser')
                text = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).find('div', attrs={
                    'class': 'BNeawe iBp4i AP7Wnd'}).text
                return text

            def bitC():
                url = f'https://www.google.com/search?q=bitcoin cash+price'
                HTML = requests.get(url)
                soup = BeautifulSoup(HTML.text, 'html.parser')
                text = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).find('div', attrs={
                    'class': 'BNeawe iBp4i AP7Wnd'}).text
                return text

            def LITE():
                url = f'https://www.google.com/search?q=litecoin+price'
                HTML = requests.get(url)
                soup = BeautifulSoup(HTML.text, 'html.parser')
                text = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).find('div', attrs={
                    'class': 'BNeawe iBp4i AP7Wnd'}).text
                return text

            def ETH():
                url = f'https://www.google.com/search?q=ethereum+price'
                HTML = requests.get(url)
                soup = BeautifulSoup(HTML.text, 'html.parser')
                text = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).find('div', attrs={
                    'class': 'BNeawe iBp4i AP7Wnd'}).text
                return text

            eth = ETH()
            lite = LITE()
            bitca = bitC()
            bit = GETC()
            await ctx.send(f'eth {eth}\nlite {lite}\nbitcoin cash {bitca}\nbitcoin {bit}')


def setup(bot):
    bot.add_cog(Test(bot))
