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

import discord
from discord.ext import commands
from discord.ext.commands.errors import BadArgument

from utils import default, http
from utils.vars import *


class Encryption(commands.Cog, description='Need to send a super secret encrypted message we gotchu'):
    def __init__(self, bot):
        self.PADDING = 5
        self.bot = bot
        self.config = bot.config

    async def binary_encode(self, ctx, text):
        text = str(text, 'utf-8')
        async with ctx.session.get(f"https://some-random-api.ml/binary?encode={text}") as resp:
            if 300 > resp.status >= 200:
                data = await resp.json()
            else:
                return await ctx.error(f"Recieved a bad status code of {resp.status}.")
            return data['binary']

    async def binary_decode(self, ctx, text):
        text = str(text, 'utf-8')
        async with ctx.session.get(f"https://some-random-api.ml/binary?decode={text}") as resp:
            if 300 > resp.status >= 200:
                data = await resp.json()
            else:
                return await ctx.error(f"Recieved a bad status code of {resp.status}.")
            return data['text']

    @commands.group(aliases=['e'])
    async def encode(self, ctx):
        """ All encode methods """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @commands.group(aliases=['d'])
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

    async def encryptout(self, ctx, convert: str, text=None):
        """ The main, modular function to control encrypt/decrypt commands """
        if not text:
            return await ctx.warn(f"Aren't you going to give me anything to encode/decode **{ctx.author.name}**")
        if len(text) > 1900:
            try:
                data = BytesIO(text.encode("utf-8"))
            except AttributeError:
                data = BytesIO(text)
            try:
                return await ctx.send(
                    content=f"📑 **{convert}**",
                    file=discord.File(data, filename=default.timetext("Encryption"))
                )
            except discord.HTTPException:
                return await ctx.error(f"The file I returned was over 8 MB, sorry {ctx.author.name}...")
        await ctx.success(f"📑 **{convert}**```fix\n{text}```")

    @encode.command(name="base32", aliases=["b32"], brief='Encode in base32')
    async def encode_base32(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base32", base64.b32encode(text.encode("utf-8"))
        )

    @decode.command(name="base32", aliases=["b32"], brief='Decode in base32')
    async def decode_base32(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        try:
            await self.encryptout(ctx, "base32 -> Text", base64.b32decode(text.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base32...")

    @encode.command(name="base64", aliases=["b64"], brief='Encode in base64')
    async def encode_base64(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base64", base64.urlsafe_b64encode(text.encode("utf-8"))
        )

    @decode.command(name="base64", aliases=["b64"], brief='Decode in base64')
    async def decode_base64(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base64 -> Text", base64.urlsafe_b64decode(text.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base64...")

    @encode.command(name="rot13", aliases=["r13"], brief='Encode in rot13')
    async def encode_rot13(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> rot13", codecs.decode(text, "rot_13")
        )

    @decode.command(name="rot13", aliases=["r13"], brief='Decode in rot13')
    async def decode_rot13(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "rot13 -> Text", codecs.decode(text, "rot_13"))
        except Exception:
            await ctx.send("Invalid rot13...")

    @encode.command(name="hex", brief='Encode in hex')
    async def encode_hex(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> hex", binascii.hexlify(text.encode("utf-8"))
        )

    @decode.command(name="hex", brief='Decode in hex')
    async def decode_hex(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "hex -> Text", binascii.unhexlify(text.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid hex...")

    @encode.command(name="base85", aliases=["b85"], brief='Encode in base85')
    async def encode_base85(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base85", base64.b85encode(text.encode("utf-8"))
        )

    @decode.command(name="base85", aliases=["b85"], brief='Decode in base85')
    async def decode_base85(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base85 -> Text", base64.b85decode(text.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid base85...")

    @encode.command(name="ascii85", aliases=["a85"], breif='Encode in ASCII85')
    async def encode_ascii85(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        await self.encryptout(ctx, "Text -> ASCII85", base64.a85encode(text.encode("utf-8")))

    @decode.command(name="ascii85", aliases=["a85"], brief='Decode in ASCII85')
    async def decode_ascii85(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "ASCII85 -> Text", base64.a85decode(text.encode("utf-8")))
        except Exception:
            await ctx.send("Invalid ASCII85...")

    @encode.command(name='morse', brief='Encode in morse code')
    async def encode_to_morse(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        try:
            answer = ' '.join(MorseCode.get(i.upper()) for i in text)
        except TypeError:
            return await ctx.reply(f"Some of the characters in your message are not valid {ctx.author.mention}")
        await self.encryptout(ctx, "Text -> Morse", answer)

    @decode.command(name='morse', brief='Decode to morse code')
    async def decode_to_morse(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        try:
            answer = ' '.join(MorseCodeReversed.get(i.upper()) for i in text.split())
        except TypeError:
            return await ctx.reply(f"Some of the characters in your message are not valid {ctx.author.mention}")
        await self.encryptout(ctx, "Morse -> Text", answer)

    @encode.command(name='binary', aliases=['b'], brief='Encode to binary')
    async def encode_to_binary(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        await self.encryptout(ctx, "Text -> binary", await self.binary_encode(ctx, text.encode("utf-8")))

    @decode.command(name='binary', aliases=['b'], brief='Decode in binary')
    async def decode_to_binary(self, ctx, *, text: commands.clean_content = None):
        if not text:
            text = await self.detect_file(ctx)
        await self.encryptout(ctx, "Binary -> Text", await self.binary_decode(ctx, text.encode("utf-8")))

    # @decode.command(name='all')
    # async def decode_all(self, ctx, *, text=None):
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
