# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from io import BytesIO

import discord
from discord.ext import commands

from utils.default import config


class coggers(commands.Cog, description='e'):
    def __init__(self, bot):
        self.bot = bot
        self.config = config()

    @commands.command()
    @commands.is_owner()
    async def htm(self, ctx):
        for command in self.bot.walk_commands():
            print(f"""<br>
            <button type="button" class="collapsible">{command.name}<span> - {command.description}</span></button>
            <div class="content">
                <h4 style="color: rgb(169, 247, 247);">Category:</h4>
                <p style="color: aqua;">{command.cog}</p>
                <h4 style="color: #cccccc;">Usage:</h4>
                <p>Hprefix</p>
                <h4 style="color: #cccccc;">Examples:</h4>
                <p>Hprefix ~</p>
            </div>
            <br>""")

    @commands.command(brief='sends a formmated html of all the commands (tis for the website)')
    @commands.is_owner()
    async def form(self, ctx):
        tosend = ''

        for command in self.bot.walk_commands():

            if command.parent is not None:
                print(command, "~", command.name)
                continue

            cogname = command.cog
            y = str(cogname).split('.')
            if y == ['None']:
                continue
            elif y[2].split()[0] == 'Owner':
                continue
            elif y[2].split()[0] == 'Jishaku':
                continue
            # elif y[2].split()[0] == 'Mod':
            #    color = '#'
            try:
                if command.description and command.short_doc:
                    description = f'{command.description}\n{command.short_doc}'
                elif command.description:
                    description = f'{command.description}'
                elif command.short_doc:
                    description = f'{command.short_doc}'
                else:
                    description = 'No Info Given...'
                sig = str(command.signature)
                finalsig = sig.replace('<', '&lt;').replace('>', '&gt;')
                aliases = ', '.join(command.aliases)
                parent = command.full_parent_name
                name = command.name if not parent else f'{parent} {command.name}'
                description = description.replace('```', '').replace('yaml', '').replace('|', '')  # .replace('', '')

                tosend += f"""
                <br><button type="button" class="collapsible">{name}<span></span></button>
                <div class="content">
                    <h4 style="color: silver;">Category:</h4>
                    <p style="color: #464f7a;">{y[2].split()[0]}</p>
                    {'<h4 style="color: silver;">Aliases:</h4>'
                     f'<p>{aliases}</p>' if aliases else ''}
                    <h4 style="color: silver;">Usage:</h4>
                    <p>{self.bot.prefix}{name} {finalsig}</p>
                    <h4 style="color: silver">Help:</h4>
                    <p> {description} </p>                    
                </div><br>\n"""
            except IndexError:
                return await ctx.send(y)
        fp = BytesIO(tosend.encode())
        return await ctx.send(file=discord.File(fp, filename='message_too_long.html'))


def setup(bot):
    bot.add_cog(coggers(bot))
