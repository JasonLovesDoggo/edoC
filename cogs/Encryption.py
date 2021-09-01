# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import base64
import binascii
import codecs
from io import BytesIO

from discord.ext import commands
from discord.ext.commands.errors import BadArgument

from utils import default, http
from utils.vars import *

class Encryption(commands.Cog, description='Need to send a super secret encrypted message we gotchu'):
    def __init__(self, bot):
        self.PADDING = 5
        self.bot = bot
        self.config = default.config()

    @commands.group()
    async def encode(self, ctx):
        """ All encode methods """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @commands.group()
    async def decode(self, ctx):
        """ All decode methods """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def detect_file(self, ctx):
        """ Detect if user uploaded a file to convert longer text """
        if ctx.message.attachments:
            file = ctx.message.attachments[0].url

            if not file.endswith(".txt"):
                raise BadArgument(".txt files only")

        try:
            content = await http.get(file, no_cache=True)
        except Exception:
            raise BadArgument("Invalid .txt file")

        if not content:
            raise BadArgument("File you've provided is empty")
        return content

    async def encryptout(self, ctx, convert: str, input=None):
        """ The main, modular function to control encrypt/decrypt commands """
        if not input:
            return await ctx.send(f"Aren't you going to give me anything to encode/decode **{ctx.author.name}**")

        if len(input) > 1900:
            try:
                data = BytesIO(input.encode("utf-8"))
            except AttributeError:
                data = BytesIO(input)
            try:
                return await ctx.send(
                    content=f"📑 **{convert}**",
                    file=discord.File(data, filename=default.timetext("Encryption"))
                )
            except discord.HTTPException:
                return await ctx.send(f"The file I returned was over 8 MB, sorry {ctx.author.name}...")
        try:
            await ctx.send(f"📑 **{convert}**```fix\n{input.decode('utf-8')}```")
        except AttributeError:
            await ctx.send(f"📑 **{convert}**```fix\n{input}```")

    @encode.command(name="base32", aliases=["b32"])
    async def encode_base32(self, ctx, *, input: commands.clean_content = None):
        """ Encode in base32 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base32", base64.b32encode(input.encode("utf-8"))
        )

    @decode.command(name="base32", aliases=["b32"])
    async def decode_base32(self, ctx, *, input: commands.clean_content = None):
        """ Decode in base32 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base32 -> Text", base64.b32decode(input.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base32...")

    @encode.command(name="base64", aliases=["b64"])
    async def encode_base64(self, ctx, *, input: commands.clean_content = None):
        """ Encode in base64 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base64", base64.urlsafe_b64encode(input.encode("utf-8"))
        )

    @decode.command(name="base64", aliases=["b64"])
    async def decode_base64(self, ctx, *, input: commands.clean_content = None):
        """ Decode in base64 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base64 -> Text", base64.urlsafe_b64decode(input.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base64...")

    @encode.command(name="rot13", aliases=["r13"])
    async def encode_rot13(self, ctx, *, input: commands.clean_content = None):
        """ Encode in rot13 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> rot13", codecs.decode(input, "rot_13")
        )

    @decode.command(name="rot13", aliases=["r13"])
    async def decode_rot13(self, ctx, *, input: commands.clean_content = None):
        """ Decode in rot13 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "rot13 -> Text", codecs.decode(input, "rot_13"))
        except Exception:
            await ctx.send("Invalid rot13...")

    @encode.command(name="hex")
    async def encode_hex(self, ctx, *, input: commands.clean_content = None):
        """ Encode in hex """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> hex", binascii.hexlify(input.encode("utf-8"))
        )

    @decode.command(name="hex")
    async def decode_hex(self, ctx, *, input: commands.clean_content = None):
        """ Decode in hex """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "hex -> Text", binascii.unhexlify(input.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid hex...")

    @encode.command(name="base85", aliases=["b85"])
    async def encode_base85(self, ctx, *, input: commands.clean_content = None):
        """ Encode in base85 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base85", base64.b85encode(input.encode("utf-8"))
        )

    @decode.command(name="base85", aliases=["b85"])
    async def decode_base85(self, ctx, *, input: commands.clean_content = None):
        """ Decode in base85 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base85 -> Text", base64.b85decode(input.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base85...")

    @encode.command(name="ascii85", aliases=["a85"])
    async def encode_ascii85(self, ctx, *, input: commands.clean_content = None):
        """ Encode in ASCII85 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> ASCII85", base64.a85encode(input.encode("utf-8"))
        )

    @decode.command(name="ascii85", aliases=["a85"])
    async def decode_ascii85(self, ctx, *, input: commands.clean_content = None):
        """ Decode in ASCII85 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "ASCII85 -> Text", base64.a85decode(input.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid ASCII85...")

    @encode.command(name='morse')
    async def encode_to_morse(self, ctx, *, text: commands.clean_content = None):
        """ Encode in morse code """
        answer = "Sorry i belive im having some problems rn"
        if not text:
            text = await self.detect_file(ctx)
            ctxisfile = True
        else:
            ctxisfile = False
        if len(text) >= 1900:
            return await ctx.reply(
                embed=discord.Embed(description="❌ Sorry that file is too large please use a smaller one", colour=red))
        try:
            answer = ' '.join(MorseCode.get(i.upper()) for i in text)
        except TypeError:
            await ctx.reply(f"Some of the characters in your message are not valid {ctx.author.mention}")

        if not ctxisfile:
            await ctx.send(f"📑 **Text -> Morse** ```fix\n {answer}```")
        else:
            try:
                data = BytesIO(answer.encode("utf-8"))
            except AttributeError:
                data = BytesIO(text)
            try:
                return await ctx.send(
                    content=f"📑 **Text -> Morse** ",
                    file=discord.File(data, filename=default.CustomTimetext("fix", "morsecode")))
            except discord.HTTPException:
                return await ctx.reply(
                    embed=discord.Embed(description=f"❌ The file I returned was over 8 MB, sorry {ctx.author.name}...",
                                        colour=red))

    @decode.command(name='morse')
    async def decode_from_morse(self, ctx, *, text: commands.clean_content = None):
        """ Decode in morse code """
        if not text:
            text = await self.detect_file(ctx)
            ctxisfile = True
        else:
            ctxisfile = False

        try:
            answer = ''.join(MorseCodeReversed.get(i) for i in text.split())
        except TypeError:
            return await ctx.reply(f"Some of the characters in your message are not valid")
        if not ctxisfile:
            await ctx.send(f"📑 **Morse -> Text** ```fix\n {answer}```")
        else:
            try:
                data = BytesIO(answer.encode("utf-8"))
            except AttributeError:
                data = BytesIO(text)
            try:
                return await ctx.send(
                    content=f"📑 **Morse -> Text** ",
                    file=discord.File(data, filename=default.CustomTimetext("fix", "morsecode")))
            except discord.HTTPException:
                return await ctx.reply(
                    embed=discord.Embed(description=f"❌ The file I returned was over 8 MB, sorry {ctx.author.name}...",
                                        colour=red))

    #@decode.command(name='all')
    #async def decode_all(self, ctx, *, text=None):
    #    """ loops through all the encoding types and sends em all """
    #    if not text:
    #        text = await self.detect_file(ctx)
    #    try:
    #        data = BytesIO(text.encode("utf-8"))
    #    except AttributeError:
    #        data = BytesIO(text)
    #    encyptions = {}
    #    # b32 = base64.b32decode(text.encode())
    #    # b64 = base64.b85encode(text.encode())
    #    # a85 = base64.a85encode(text.encode())
    #    # encyptions["Base32"] = b32
    #    # encyptions["base85"] = b64[:-1]
    #    # encyptions["Ascii85"] =a85[:-1]
    #    encyptions["test"] = await self.encryptout(ctx, "base32 -> Text", base64.b32decode(text.encode("utf-8")))
#
    #    emb = discord.Embed(title="Encryption Outputs",
    #                        color=blue,
    #                        description="")
    #    for k, v in encyptions.items():
    #        pad = ' ' * (self.PADDING - len(str(v)))
    #        emb.description += f"`{pad}{v}`: **{k}**\n"
    #    await ctx.reply(embed=emb)
#

def setup(bot):
    bot.add_cog(Encryption(bot))