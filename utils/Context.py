# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import logging
from io import BytesIO
from typing import Union

import discord
from discord import Embed, Colour
from discord.embeds import _EmptyEmbed
from discord.ext.commands import Context
from discord.utils import cached_property

from utils.vars import *


class edoCContext(Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    def tick(self, val=True):
        # inspired by Rapptz' RoboDanny
        # (no code was used)
        return {
            True: self.bot.get_emoji(879161311353778247),
            False: self.bot.get_emoji(879146899322601495),
            None: self.bot.get_emoji(879146777842962454)
        }.get(val)

    async def try_reply(self, content=None, *, mention_author=False, **kwargs):
        """Try reply, if failed do send instead"""
        try:
            action = self.safe_reply
            return await action(content, mention_author=mention_author, **kwargs)
        except BaseException:
            if mention_author:
                content = f"{self.author.mention} " + content if content else ""

            action = self.safe_send
            return await self.safe_send(content, **kwargs)

    async def safe_send(self, content, *, escape_mentions=True, channel=False, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if channel:
            channel = self.bot.get_channel(channel)
        else:
            channel = self

        if len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop('file', None)
            return await channel.send(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await channel.send(content)

    async def safe_reply(self, content, *, escape_mentions=True, **kwargs):
        return await self.safe_send_reply(
            content, escape_mentions=escape_mentions, type="reply", **kwargs
        )

    async def safe_send_reply(
            self, content, *, escape_mentions=True, type="send", **kwargs
    ):
        action = getattr(self, type)

        if escape_mentions and content is not None:
            content = discord.utils.escape_mentions(content)

        if content is not None and len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop("file", None)
            return await action(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )
        else:
            if content is not None:
                kwargs["content"] = content
            return await action(**kwargs)

    async def cembed(self, color: Union[int, Colour, _EmptyEmbed], success_message: str, **kwargs):
        e = Embed(color=color, **kwargs)
        e.description = str(success_message)
        return await self.try_reply(embed=e)

    async def error(self, error_message, real=False, **kwargs):
        e = Embed(color=colors['error'])
        e.description = str(error_message)
        await self.try_reply(embed=e, **kwargs)
        if real:
            for error in INVALID_ERRORS:
                if str(error_message).startswith(error):
                    return
            dbug = self.bot.get_channel(self.bot.config['debug'])
            await dbug.send(embed=e)
            logging.debug(error_message)

    async def success(self, success_message: str = None, **kwargs):
        e = Embed(color=green)
        e.description = str(success_message)
        return await self.try_reply(embed=e, **kwargs)

    async def warn(self, warn_message: str = None, log=False, **kwargs):
        e = Embed(color=yellow)
        e.description = str(warn_message)
        await self.try_reply(embed=e, **kwargs)
        if log:
            logging.debug(warn_message)

    async def invis(self, invis_message, **kwargs):
        e = Embed(color=invis, **kwargs)
        e.description = str(invis_message)
        return await self.try_reply(embed=e)

    async def unknown(self, unknownerror, command):
        e = Embed(color=error, title=command.name)
        e.description = str(unknownerror)
        channel = self.bot.get_channel(867828022752444416)
        await self.try_reply(f'An unknown error happend with {command.name}')
        return await channel.send(embed=e)

    async def report(self, ctx, msg):
        channel = self.bot.get_channel(877724111420391515)
        if len(msg) > 300:
            return self.error('Too Long please keep under 300 characters')
        elif len(msg) < 20:
            return self.warn('Too short please keep over 20 characters')
        e = Embed(color=green)
        e.description = str(msg)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        await channel.send(embed=e)

    @cached_property
    def replied_reference(self):
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return self.message

    @cached_property
    async def reference(self):
        if ref := self.message.reference:
            # Get referenced message
            # if user reply to a message while doing this command
            return (
                ref.cached_message
                if ref.cached_message
                else (await self.fetch_message(ref.message_id))
            )
        return self

    @cached_property
    async def replied_author(self):
        if ref := self.message.reference:
            # Get referenced message
            # if user reply to a message while doing this command
            return (
                ref.cached_message.author
                if ref.cached_message
                else (await self.fetch_message(ref.message_id)).author
            )
        return self.author

