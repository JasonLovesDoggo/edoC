import asyncio
import logging
import time
import aiohttp
from discord.ext.commands import ExtensionNotLoaded
from jishaku.models import copy_context_with

import discord
import importlib
import os
import sys
import json
from discord.ext import commands
from utils import permissions, default, http
from io import BytesIO
from cogs.mod import BanUser, MemberID
on = False

class Admin(commands.Cog):
    def __init__(self, bot):
        self.highest_num = 0
        self.bot = bot
        self.config = default.config()
        self._last_result = None
        self.DoggoPath = r"C:/Users/Jason/edoC/data/Dog Picks"
        self.filenum = 0

    @commands.command()
    @commands.check(permissions.is_owner)
    async def update(self, ctx):
        sh = "jsk sh"

        git = f"{sh} git pull"
        update = f"{sh} make update"

        git_command_ctx = await copy_context_with(
            ctx, content=ctx.prefix + git
        )
        update_command_ctx = await copy_context_with(
            ctx, content=ctx.prefix + update
        )

        await git_command_ctx.command.invoke(git_command_ctx)
        await update_command_ctx.command.invoke(update_command_ctx)
        await self.shutdown()

    @commands.command()
    @commands.check(permissions.is_owner)
    async def change_config_value(self, value: str, changeto: str):
        """ Change a value from the configs """
        config_name = "config.json"
        with open(config_name, "r") as jsonFile:
            data = json.load(jsonFile)

        data[value] = changeto
        with open(config_name, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)

    @commands.command()
    async def amiadmin(self, ctx):
        """ Are you an admin? """
        """ Are you an admin? """
        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- Jason
        if ctx.author.id == 511724576674414600:
            return await ctx.send(f"Well kinda **{ctx.author.name}**.. you own the source code")
        if ctx.author.id in self.config["owners"]:
            return await ctx.send(f"Yes **{ctx.author.name}** you are an admin! ✅")

        await ctx.send(f"no, heck off {ctx.author.name}")

    @commands.command(aliases=["botusers", "botmembers", "thepeoplemybothaspowerover"])
    @commands.check(permissions.is_owner)
    async def users(self, ctx):
        """ Gets all users """
        allusers = ""
        for num, user in enumerate(self.bot.get_all_members(), start=1):
            allusers += f" \n[{str(num).zfill(2)}] {user} ~ {user.id}"
        data = BytesIO(allusers.encode("utf-8"))
        await ctx.send(content=f"Users", file=discord.File(data, filename=f"{default.timetext('Users')}"))

    @users.error
    async def users_error(self, ctx: commands.Context, error: commands.CommandError):
        # if the conversion above fails for any reason, it will raise `commands.BadArgument`
        # so we handle this in this error handler:
        if isinstance(error, commands.BadArgument):
            return await ctx.send("Couldn\'t find that user.")

    @commands.command()  # idk i wanted this
    @commands.check(permissions.is_owner)
    async def print(self, what_they_said: str):
        """ prints to console said text"""
        print(what_they_said)

    @commands.command()
    @commands.check(permissions.is_owner or permissions.is_mod)
    async def say(self, ctx, *, what_to_say: str):
        """ says text """  # todo add a thing that deletes the message that the ~say'er sent prob with ctx.message smth
        await ctx.send(f'{what_to_say}')

    @commands.command()
    @permissions.has_permissions(manage_guild=True)
    async def prefix(self, ctx, next_prefix: str):
        await ctx.send("this command currently does not exist its just a placeholder")
        """
         Change the value of prefix for the guild and insert it into the guilds table
         @param next_prefix:
         """
        """guildid = ctx.guild.id
        prefixchange = ''' INSERT INTO guilds(name,begin_date,end_date)
                  VALUES(?,?,?) '''
        db.execute(prefixchange)
        conn.commit()
        return cur.lastrowid
            """

    @commands.command(aliases=["rp", "saymore"])
    @commands.check(permissions.is_owner or permissions.is_mod)
    async def repeat(self, ctx, times: int, *, content='repeating...'):
        """Repeats a message multiple times."""
        for i in range(times):
            await ctx.send(content)
            await asyncio.sleep(1.0)

    @commands.group()
    @commands.check(permissions.is_owner)
    async def file(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @file.command(name="read", aliases=["sayscript", "readscript"])
    @commands.check(permissions.is_owner)
    async def file_read(self, ctx, filename: str):
        """ Reads the file specified and sends it"""
        await ctx.send(f'Why you madman why dare try to open {filename}')
        await asyncio.sleep(1.0)
        file = open(f"C:/Users/Jason/edoC/cogs/Texts/{filename}.txt", "r")
        for word in file:
            await ctx.send(word)
            await asyncio.sleep(1.2)

    @file.command(name="write", aliases=["writescript"])
    @commands.check(permissions.is_owner)
    async def file_write(self, ctx, filename: str, *, everythin_else):
        """ Writes a file from discord to the pc/server """
        message = await ctx.send('starting...')
        file = open(f"C:/Users/Jason/edoC/cogs/Texts/{filename}.txt",
                    "w+")
        for line in everythin_else:
            file.writelines(f"\n{str(line)}")
        file.close()
        await message.edit(content="Done!")

    @commands.command(aliases=["bban"])
    @commands.check(permissions.is_owner or permissions.is_mod)
    async def botban(self, ctx, userid: MemberID, *, reason: str):
        await BanUser(ctx, userid, reason)
        await ctx.send(f"banned {userid} for {reason}")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def unload(self, ctx, name: str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(aliases=["r"])
    @commands.check(permissions.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command(aliases=["ra"])
    @commands.check(permissions.is_owner)
    async def reloadall(self, ctx):
        """ Reloads all extensions. """
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
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command(aliases=["ru"])
    @commands.check(permissions.is_owner)
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"Module **{name_maker}** returned error and was not reloaded...\n{error}")
        await ctx.send(f"Reloaded module **{name_maker}**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send("Rebooting now...")
        time.sleep(1)
        sys.exit(0)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def shutdown(self, ctx):
        """ shut down the bot """
        await ctx.send("Shuting down now...")
        # logs it to a file
        logging.basicConfig(filename="log.txt",
                            format='%(asctime)s %(message)s',
                            filemode='w+')
        logging.warning('Shutting down now')
        await asyncio.sleep(2)
        sys.exit("Bot shut down")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def todoadd(self, ctx, *, message: str):
        """Dumps the message into todo.txt"""
        todofile = open("todo.txt", "a")
        todofile.write(f"\n \n **{message}** \n~ {ctx.author} ~ {ctx.message.created_at}")
        await ctx.send(f'Dumping "**{message}** " Into {todofile.name}')
        todofile.close()

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.check(permissions.is_owner or permissions.is_mod)
    async def nuke(self, ctx):
        """ Joke cmd doesnt rly do anything """
        message = await ctx.send("Making server backup then nuking")
        time.sleep(0.5)
        await message.edit(content="Backup 33% complete")
        await asyncio.sleep(.5)
        await message.edit(content="Backup 64% complete")
        await asyncio.sleep(.7)
        await message.edit(content="Backup 86% complete")
        await asyncio.sleep(.57)
        await message.edit(content="Backup 93% complete")
        await asyncio.sleep(2)
        await message.edit(content="Backup 100% complete")
        await asyncio.sleep(.5)
        await ctx.send("Nuking everything now")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def clearfile(self, ctx, filename: str):
        """clears the specified filename file"""
        file2 = open(filename, "w+")
        file2.truncate(0)
        await ctx.send(f'{filename} purged ')
        file2.close

    @commands.command(pass_context=True)
    @commands.check(permissions.is_owner)
    async def massrole(self, ctx, role_id: discord.Role = None):
        """ Gives all the members of the server said role """
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
        await ctx.send(content=f"The roles have been added to", file=discord.File(data, filename=f"{default.timetext('AddedUsers')}"))

    @commands.command(pass_context=True)
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
            return await ctx.send("**{}** role has been added to {}.".format(role, ctx.message.author.mention))

        if role in ctx.message.author.roles:
            await self.bot.remove_roles(role)
            return await ctx.send("**{}** role has been removed from {}."
                                  .format(role, ctx.message.author.mention))

    @commands.command()
    @commands.check(permissions.is_owner or permissions.is_mod)
    async def dm(self, ctx, user_id: int, *, message: str):
        """ DM the user of your choice """
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.group()
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="playing")
    @commands.check(permissions.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        activity = self.config["activity_type"].lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        try:
            await self.bot.change_presence(
                activity=discord.Game(
                    type=activity_type.get(activity, 0), name=playing
                ),
                status=status_type.get(status, discord.Status.online)
            )
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
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
            await ctx.send("You need to either provide an image URL or upload one with the command")

    @commands.Cog.listener()
    async def on_ready(self):
        path = self.DoggoPath
        files = os.listdir(path)
        for filename in files:
            truename = filename[:-4]
            if ' ' in truename:
                continue
            try:
                if int(truename) > self.highest_num:
                    self.highest_num = int(truename)
            except ValueError:
                pass
        self.filenum = self.highest_num

    @commands.check(permissions.is_owner)
    @commands.command(aliases=["FDP"])
    async def FormatDogPhotos(self, ctx):
        """ Function to rename all the doggo files """
        path = self.DoggoPath
        files = os.listdir(path)
        for count, file in enumerate(files):
            if file.startswith("1" or "2" or "3" or "4" or "5" or "6" or "7" or "8" or "9"):
                continue
            else:
                self.filenum += 1
                os.rename(os.path.join(path, file), os.path.join(path, ''.join([str(self.filenum + 1), '.jpg'])))
        await ctx.send(f"done\ncurrent limit is {self.filenum}")


def setup(bot):
    bot.add_cog(Admin(bot))
