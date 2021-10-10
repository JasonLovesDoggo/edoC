# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import asyncio
import importlib
import inspect
import io
import json
import logging
import os
import textwrap
import traceback
from contextlib import redirect_stdout
from io import BytesIO
from random import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import command, is_owner
from jishaku.models import copy_context_with
from jishaku.paginators import WrappedPaginator, PaginatorInterface

from cogs.Mod import BanUser, MemberID
from utils import default, http
from utils.vars import *

logger = logging.getLogger(__name__)
on = False


class Owner(commands.Cog, description="Only i can use these so shoo"):
    def __init__(self, bot):
        self.highest_num = 0
        self.bot = bot
        self.config = bot.config
        self._last_result = None
        self.DoggoPath = r"C:/Users/Jason/edoC/data/img/Dog Picks"
        self._last_result = None
        self.sessions = set()

    @commands.command(aliases=["ExitGuild"])
    @commands.is_owner()
    async def LeaveGuild(self, ctx, *, name_or_id):
        if type(name_or_id) == str:
            guild = discord.utils.get(self.bot.guilds, name=name_or_id)
        elif type(name_or_id) == int:
            guild = self.bot.get_guild(name_or_id)
        else:
            return await ctx.warn(
                "I either could not get that guild or my quantum phase disruptor is out of sync"
            )
        if guild is None:
            return await ctx.warn("I don't recognize that guild.")
        confirmcode = randint(0, 99999)
        confirm_msg = await ctx.send(
            f"Type `{confirmcode}` within 30s to confirm this choice\n"
        )

        def check_confirm(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                if m.content.startswith(str(confirmcode)):
                    return True
            return False

        try:
            user = await self.bot.wait_for("message", timeout=30.0, check=check_confirm)
        except asyncio.TimeoutError:
            return await confirm_msg.edit(
                content=f"~~{confirm_msg.clean_content}~~\n\nStopped process..."
            )
        await guild.leave()
        await ctx.send(f":ok_hand: Left guild: {guild.name} ({guild.id})")

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @commands.command(aliases=["pyeval"])
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")

    @commands.command()
    @commands.is_owner()
    async def rules(self, ctx):
        emb = discord.Embed(
            title="edoC Support Server Rules\nPlease Read Carefully", color=white
        )
        emb.set_author(
            name="Jason",
            url="https://bio.link/edoC",
            icon_url="https://i.imgur.com/LOJhKuN.png",
        )
        emb.description = rules
        emb.set_footer(
            text="Saying that you’re joking isn’t an excuse for breaking rules.\nThese rules are subject to change at anytime without prior notice."
        )
        emb.set_thumbnail(url="https://i.imgur.com/yww1r5E.jpeg")
        await ctx.send(
            allowed_mentions=discord.AllowedMentions(
                roles=True, users=True, everyone=True, replied_user=True
            ),
            embed=emb,
        )

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        sh = "jsk sh"

        git = f"{sh} git pull"
        update = f"{sh} make update"

        git_command_ctx = await copy_context_with(ctx, content=ctx.prefix + git)
        update_command_ctx = await copy_context_with(ctx, content=ctx.prefix + update)

        await git_command_ctx.command.invoke(git_command_ctx)
        await update_command_ctx.command.invoke(update_command_ctx)
        await self.shutdown()

    @commands.group(aliases=["su"])
    @commands.is_owner()
    async def sudo(self, ctx, target: discord.User, *, command_string: str):
        """
        Run a command as someone else.

        This will try to resolve to a Member, but will use a User if it can't find one.
        """

        if ctx.guild:
            # Try to upgrade to a Member instance
            # This used to be done by a Union converter, but doing it like this makes
            #  the command more compatible with chaining, e.g. `~in .. ~su ..`
            target = ctx.guild.get_member(target.id) or target

        alt_ctx = await copy_context_with(
            ctx, author=target, content=ctx.prefix + command_string
        )

        if alt_ctx.command is None:
            if alt_ctx.invoked_with is None:
                return await ctx.send(
                    "This bot has been hard-configured to ignore this user."
                )
            return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

        return await alt_ctx.command.invoke(alt_ctx)

    @sudo.command(name="in")
    @commands.is_owner()
    async def edoC_in(self, ctx, channel: discord.TextChannel, *, command_string: str):
        """Run a command as if it were run in a different channel."""

        alt_ctx = await copy_context_with(
            ctx, channel=channel, content=ctx.prefix + command_string
        )

        if alt_ctx.command is None:
            return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

        return await alt_ctx.command.invoke(alt_ctx)

    @sudo.command(aliases=["src"])
    @commands.is_owner()
    async def source(self, ctx, *, command_name: str):
        """
        Displays the source code for a command.
        """

        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"Couldn't find command `{command_name}`.")

        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            return await ctx.send(
                f"Was unable to retrieve the source for `{command}` for some reason."
            )

        # getsourcelines for some reason returns WITH line endings
        source_lines = "".join(source_lines).split("\n")

        paginator = WrappedPaginator(prefix="```py", suffix="```", max_size=1985)
        for line in source_lines:
            paginator.add_line(line)

        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.command()
    @commands.is_owner()
    async def change_config_value(self, value: str, changeto: str):
        """Change a value from the configs"""
        config_name = "config.json"
        with open(config_name, "r") as jsonFile:
            data = json.load(jsonFile)

        data[value] = changeto
        with open(config_name, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)

    @commands.command()
    async def amiadmin(self, ctx):
        """Are you an admin?"""
        """ Are you an admin? """
        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- Jason
        auth = ctx.author
        if auth.id == 511724576674414600:
            return await ctx.send(
                f"Well kinda **{auth.name}**.. you own the source code"
            )
        elif auth.id == 86477779717066752:
            return await ctx.send(
                f"Well kinda **{auth.name}**.. you own the core source code"
            )
        if auth.id in self.config["owners"]:
            return await ctx.send(f"Yes **{auth.name}** you are an admin! ✅")

        await ctx.send(f"no, heck off {auth.name}")

    @commands.command(aliases=["botusers", "botmembers", "thepeoplemybothaspowerover"])
    @commands.is_owner()
    async def users(self, ctx):
        """Gets all users"""
        allusers = ""
        for num, user in enumerate(self.bot.get_all_members(), start=1):
            allusers += f" \n[{str(num).zfill(2)}] {user} ~ {user.id}"
        data = BytesIO(allusers.encode("utf-8"))
        await ctx.send(
            content=f"Users",
            file=discord.File(data, filename=default.CustomTimetext("ini", "Users")),
        )

    @users.error
    async def users_error(self, ctx, error: commands.CommandError):
        # if the conversion above fails for any reason, it will raise `commands.BadArgument`
        # so we handle this in this error handler:
        if isinstance(error, commands.BadArgument):
            return await ctx.send("Couldn't find that user.")

    @commands.command()  # idk i wanted this
    @commands.is_owner()
    async def print(self, what_they_said: str):
        """prints to console said text"""
        print(what_they_said)

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, what_to_say: str):
        """says text"""
        await ctx.message.delete()
        await ctx.send(f"{what_to_say}")

    # @commands.command()
    # @commands.has_permissions(manage_guild=True)
    # async def prefix(self, ctx, next_prefix: str):
    #    """
    #     Change the value of prefix for the guild and insert it into the guilds table
    #     """
    #    await ctx.send("this command currently does not exist its just a placeholder")
    #    db.execute("UPDATE  SET Prefix=? WHERE GuildId=?", (next_prefix, ctx.guild.id))
    #    self.bot.db.commit()
    #    return cur.lastrowid todo make this a group

    @commands.command(aliases=["rp", "saymore"])
    @commands.is_owner()
    async def saymany(self, ctx, times: int, *, content="repeating..."):
        """Repeats a message multiple times."""
        saidtimes = 0
        for i in range(times):
            saidtimes += 1
            await ctx.send(content + f" ||({saidtimes})||")
            await asyncio.sleep(1.0)

    @commands.group()
    @commands.is_owner()
    async def file(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @file.command(name="send")
    @commands.is_owner()
    async def file_send(self, ctx, filename: str):
        """sends the filename file"""
        file = discord.File(f"C:/Users/Jason/edoC/cogs/Texts/{filename}.txt")
        await ctx.send(file=file)

    @file.command(name="read", aliases=["sayscript", "readscript"])
    @commands.is_owner()
    async def file_read(self, ctx, filename: str):
        """Reads the file specified and sends it"""
        await ctx.send(f"Why you madman why dare try to open {filename}")
        await asyncio.sleep(1.0)
        file = open(f"C:/Users/Jason/edoC/cogs/Texts/{filename}.txt", "r")
        for word in file:
            for letr in word:
                if not letr.isprintable():
                    continue
            await ctx.send(word)
            await asyncio.sleep(1.2)

    @file.command(name="write", aliases=["writescript"])
    @commands.is_owner()
    async def file_write(self, ctx, filename: str, *, everythin_else):
        """Writes a file from discord to the pc/server"""
        message = await ctx.send("starting...")
        file = open(f"C:/Users/Jason/edoC/cogs/Texts/{filename}.txt", "w+")
        for line in everythin_else:
            file.writelines(f"\n{str(line)}")
        file.close()
        await message.edit(content="Done!")

    @commands.command(aliases=["bban"])
    @commands.is_owner()
    async def botban(self, ctx, userid: MemberID, *, reason: str):
        await BanUser(ctx, userid, reason)
        await ctx.send(f"banned {userid} for {reason}")

    @commands.command(
        aliases=["l"],
        brief="Loads an Extension",
        description="The command is used to load the Extensions into the Bot.",
    )
    @commands.is_owner()
    async def load(self, ctx, name: str):
        """Loads an extension."""
        name = name.title()
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command(aliases=["ul"])
    @commands.is_owner()
    async def unload(self, ctx, name: str):
        """Unloads an extension."""
        name = name.title()
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(aliases=["r"])
    @commands.is_owner()
    async def reload(self, ctx, name: str):
        """Reloads an extension."""
        name = name.title()
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command(aliases=["ra"])
    @commands.is_owner()
    async def reloadall(self, ctx):
        """Reloads all extensions."""
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

        if error_collection:
            output = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection]
            )
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command(aliases=["ru"])
    @commands.is_owner()
    async def reloadutils(self, ctx, name: str):
        """Reloads a utils module."""
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(
                f"Module **{name_maker}** returned error and was not reloaded...\n{error}"
            )
        await ctx.send(f"Reloaded module **{name_maker}**")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """shut down the bot"""
        await ctx.warn("Shuting down now...", log=True)
        await self.bot.close()

    @command()
    @is_owner()
    async def restart(self, ctx):
        """restarts the bot using pm2"""
        await ctx.warn("Restarting..", log=True)
        await self.bot.restart()

    @commands.command()
    @commands.is_owner()
    async def todoadd(self, ctx, *, message: str):
        """Dumps the message into todo.txt"""
        todofile = open("todo.txt", "a")
        todofile.write(
            f"\n \n **{message}** \n~ {ctx.author} ~ {ctx.message.created_at}"
        )
        await ctx.send(f'Dumping "**{message}** " Into {todofile.name}')
        todofile.close()

    @commands.command()
    @commands.is_owner()
    async def clearfile(self, ctx, filename: str):
        """clears the specified filename file"""
        file2 = open(filename, "w+")
        file2.truncate(0)
        await ctx.send(f"{filename} purged ")
        file2.close()

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def massrole(self, ctx, role_id: discord.Role = None):
        """Gives all the members of the server said role"""
        if role_id is None:
            await ctx.send("You haven't specified a role! ")
            return
        if role_id not in ctx.message.guild.roles:
            await ctx.send("That role doesn't exist.")
            return
        addedusers = ""

        for members, num in enumerate(ctx.message.guild.members):
            if role_id not in ctx.message.author.roles:
                addedusers += f" \n[{str(num).zfill(2)}] {members}"
                await self.bot.add_roles(members, role_id)

        data = BytesIO(addedusers.encode("utf-8"))
        await ctx.send(
            content=f"The roles have been added to",
            file=discord.File(data, filename=f"{default.timetext('AddedUsers')}"),
        )

    @commands.command(aliases=["trole", "ToggleRole"])
    @commands.is_owner()
    async def role(self, ctx, *, role: discord.Role = None):
        """
        Toggle whether or not you have a role. Usage: `~role CoolDudes`. Can take roles with spaces.
        """
        if role is None:
            return await ctx.send("You haven't specified a role! ")

        if role not in ctx.message.guild.roles:
            return await ctx.send("That role doesn't exist.")

        if role not in ctx.message.author.roles:
            await ctx.message.author.add_roles(role)
            return await ctx.send(
                "**{}** role has been added to {}.".format(
                    role, ctx.message.author.mention
                )
            )

        if role in ctx.message.author.roles:
            await self.bot.remove_roles(role)
            return await ctx.send(
                "**{}** role has been removed from {}.".format(
                    role, ctx.message.author.mention
                )
            )

    @commands.command(aliases=["pm"])
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        fmt = (
            message
            + "\n\n*This is a DM sent because you had previously requested feedback or I found a bug"
            " in a command you used, I do not monitor this DM.*"
        )
        try:
            await user.send(fmt)
            await ctx.send(f"✉️ Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send(
                "This user might be having DMs blocked or it's a bot account..."
            )

    @commands.group()
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="playing")
    @commands.is_owner()
    async def change_playing(self, ctx, *, playing: str):
        """Change playing status."""
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        activity = self.config["activity_type"].lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        try:
            await self.bot.change_presence(
                activity=discord.Game(
                    type=activity_type.get(activity, 0), name=playing
                ),
                status=status_type.get(status, discord.Status.online),
            )
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.is_owner()
    async def change_username(self, ctx, *, name: str):
        """Change username."""
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """Change nickname."""
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.is_owner()
    async def change_avatar(self, ctx, url: str = None):
        """Change avatar."""
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None

        try:

            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a usable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send(
                "You need to either provide an image URL or upload one with the command"
            )

    # @commands.Cog.listener()
    # async def on_ready(self):
    #    path = self.DoggoPath
    #    files = os.listdir(path)
    #    for filename in files:
    #        truename = filename[:-4]
    #        if ' ' in truename:
    #            continue
    #        try:
    #            if int(truename) > self.highest_num:
    #                self.highest_num = int(truename)
    #        except ValueError:
    #            pass
    #    self.filenum = self.highest_num

    @commands.is_owner()
    @commands.command(aliases=["RDPN"])
    async def ResetDogPhotoNames(self, ctx):
        path = self.DoggoPath
        files = os.listdir(path)
        for count, file in enumerate(files):
            os.rename(
                os.path.join(path, file), os.path.join(path, "".join(f"{random()}.jpg"))
            )
        await ctx.send(f"done")

    @commands.is_owner()
    @commands.command(aliases=["FDP"])
    async def FormatDogPhotos(self, ctx):
        """Function to rename all the doggo files"""
        path = self.DoggoPath
        files = os.listdir(path)
        filenum = 0
        for count, file in enumerate(files):
            filenum += 1
            os.rename(
                os.path.join(path, file),
                os.path.join(path, "".join([str(filenum), ".jpg"])),
            )
        await ctx.send(f"done\ncurrent limit is {filenum}")


def setup(bot):
    bot.add_cog(Owner(bot))
