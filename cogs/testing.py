from urllib.parse import quote_plus

import discord
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


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('google')

        @bot.command()
        async def google(ctx: commands.Context, *, query: str):
            """Returns a google link for a query"""
            await ctx.send(f'Google Result for: `{query}`', view=Google(query))

        @bot.command()
        async def counter(ctx: commands.Context):
            """Starts a counter for pressing."""
            await ctx.send('Press!', view=Counter())


def setup(bot):
    bot.add_cog(Test(bot))
