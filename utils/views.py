# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import asyncio
import contextlib
import re
import time
from functools import partial
from typing import Optional, Dict, Any, List

import discord
from discord import Embed, ui
from discord.ext import menus
from discord.ext.commands import *
from discord.ext.commands import Paginator as CommandPaginator

from utils.Context import edoCContext
from utils.vars import error


class BaseView(ui.View):
    def reset_timeout(self):
        self.set_timeout(time.monotonic() + self.timeout)

    def set_timeout(self, new_time):
        self._View__timeout_expiry = new_time


class CallbackView(BaseView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for b in self.children:
            self.wrap(b)

    def wrap(self, b):
        callback = b.callback
        b.callback = partial(self.handle_callback, callback, b)

    async def handle_callback(self, callback, item, interaction):
        pass

    def add_item(self, item: ui.Item) -> None:
        self.wrap(item)
        super().add_item(item)


class ViewAuthor(BaseView):
    def __init__(self, ctx: edoCContext, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.context = ctx
        self.is_command = ctx.command is not None
        self.cooldown = CooldownMapping.from_cooldown(1, 10, BucketType.user)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
        ctx = self.context
        author = ctx.author
        if interaction.user == ctx.bot.stella:
            return True
        if interaction.user != author:
            bucket = self.cooldown.get_bucket(ctx.message)
            if not bucket.update_rate_limit():
                if self.is_command:
                    command = ctx.bot.get_command_signature(ctx, ctx.command)
                    content = f"Only `{author}` can use this. If you want to use it, use `{command}`"
                else:
                    content = f"Only `{author}` can use this."
                embed = Embed(color=error, description=content)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True


class FreeNitroView(discord.ui.View):
    def __init__(self, ctx: edoCContext):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.value = None

    @discord.ui.button(
        label="Claim", custom_id="claim", style=discord.ButtonStyle.green
    )
    async def claim(self, _, interaction: discord.Interaction):
        await interaction.message.edit(
            content="https://imgur.com/NQinKJB", embed=None, view=None
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This isn't your command!", ephemeral=True
        )
        return False


class ConfirmView(ViewAuthor, CallbackView):
    """ConfirmView literally handles confirmation where it asks the user at start() and returns a Tribool"""

    def __init__(
        self,
        ctx: edoCContext,
        *,
        delete_after: Optional[bool] = False,
        message_error=None,
    ):
        super().__init__(ctx)
        self.result = None
        self.message = None
        self.delete_after = delete_after
        self.message_error = message_error or "I'm waiting for your confirm response."

    async def handle_callback(self, callback, item, interaction):
        self.result = await callback(interaction)
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.stop()

    async def send(self, content: str, **kwargs: Any) -> Optional[bool]:
        return await self.start(content=content, **kwargs)

    async def start(
        self, message: Optional[discord.Message] = None, **kwargs: Any
    ) -> Optional[bool]:
        self.message = message or await self.context.reply(view=self, **kwargs)

        if not self.delete_after:
            for x in self.children:
                x.disabled = True
            coro = self.message.edit(view=self)
        else:
            coro = self.message.delete()

        with contextlib.suppress(discord.HTTPException):
            await coro
        return self.result

    async def confirmed(self, button: ui.Button, interaction: discord.Interaction):
        pass

    async def denied(self, button: ui.Button, interaction: discord.Interaction):
        pass

    @ui.button(
        emoji="<a:yes:879161309315346582> ",
        label="Confirm",
        style=discord.ButtonStyle.green,
    )
    async def confirmed_action(
        self, button: ui.Button, interaction: discord.Interaction
    ):
        await self.confirmed(button, interaction)
        return True

    @ui.button(
        emoji="<a:no:879146899322601495>",
        label="Cancel",
        style=discord.ButtonStyle.danger,
    )
    async def denied_action(self, button: ui.Button, interaction: discord.Interaction):
        await self.denied(button, interaction)
        return False


class edoCPages(discord.ui.View):
    def __init__(
        self,
        source: menus.PageSource,
        *,
        ctx,
        check_embeds: bool = True,
        compact: bool = False,
    ):
        super().__init__()
        self.source: menus.PageSource = source
        self.check_embeds: bool = check_embeds
        self.ctx = ctx
        self.message: Optional[discord.Message] = None
        self.current_page: int = 0
        self.compact: bool = compact
        self.input_lock = asyncio.Lock()
        self.clear_items()
        self.fill_items()

    def fill_items(self) -> None:
        if not self.compact:
            self.numbered_page.row = 1
            self.stop_pages.row = 1

        if self.source.is_paginating():
            max_pages = self.source.get_max_pages()
            use_last_and_first = max_pages is not None and max_pages >= 2
            if use_last_and_first:
                self.add_item(self.go_to_first_page)  # type: ignore
            self.add_item(self.go_to_previous_page)  # type: ignore
            if not self.compact:
                self.add_item(self.go_to_current_page)  # type: ignore
            self.add_item(self.go_to_next_page)  # type: ignore
            if use_last_and_first:
                self.add_item(self.go_to_last_page)  # type: ignore
            if not self.compact:
                self.add_item(self.numbered_page)  # type: ignore
            self.add_item(self.stop_pages)  # type: ignore

    async def _get_kwargs_from_page(self, page: int) -> Dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self.source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"embed": value, "content": None}
        else:
            return {}

    async def show_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        page = await self.source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(page_number)
        if kwargs:
            if interaction.response.is_done():
                if self.message:
                    await self.message.edit(**kwargs, view=self)
            else:
                await interaction.response.edit_message(**kwargs, view=self)

    def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        if self.compact:
            max_pages = self.source.get_max_pages()
            self.go_to_last_page.disabled = (
                max_pages is None or (page_number + 1) >= max_pages
            )
            self.go_to_next_page.disabled = (
                max_pages is not None and (page_number + 1) >= max_pages
            )
            self.go_to_previous_page.disabled = page_number == 0
            return

        self.go_to_current_page.label = str(page_number + 1)
        self.go_to_previous_page.label = str(page_number)
        self.go_to_next_page.label = str(page_number + 2)
        self.go_to_next_page.disabled = False
        self.go_to_previous_page.disabled = False
        self.go_to_first_page.disabled = False

        max_pages = self.source.get_max_pages()
        if max_pages is not None:
            self.go_to_last_page.disabled = (page_number + 1) >= max_pages
            if (page_number + 1) >= max_pages:
                self.go_to_next_page.disabled = True
                self.go_to_next_page.label = "..."
            if page_number == 0:
                self.go_to_previous_page.disabled = True
                self.go_to_previous_page.label = "..."

    async def show_checked_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        max_pages = self.source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(interaction, page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id in (
            self.ctx.bot.owner_id,
            self.ctx.author.id,
        ):
            return True
        await interaction.response.send_message(
            "This pagination menu cannot be controlled by you, sorry!", ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def on_error(
        self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction
    ) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(
                "An unknown error occurred, sorry", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An unknown error occurred, sorry", ephemeral=True
            )

    async def start(self) -> None:
        if (
            self.check_embeds
            and not self.ctx.channel.permissions_for(self.ctx.me).embed_links
        ):
            await self.ctx.send(
                "Bot does not have embed links permission in this channel."
            )
            return

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        self.message = await self.ctx.send(**kwargs, view=self)

    @discord.ui.button(label="<<<", style=discord.ButtonStyle.grey)
    async def go_to_first_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """go to the first page"""
        await self.show_page(interaction, 0)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """go to the previous page"""
        await self.show_checked_page(interaction, self.current_page - 1)

    @discord.ui.button(label="Current", style=discord.ButtonStyle.grey, disabled=True)
    async def go_to_current_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def go_to_next_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """go to the next page"""
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label=">>>", style=discord.ButtonStyle.grey)
    async def go_to_last_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(interaction, self.source.get_max_pages() - 1)

    @discord.ui.button(label="Skip to page...", style=discord.ButtonStyle.grey)
    async def numbered_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """lets you type a page number to go to"""
        if self.input_lock.locked():
            await interaction.response.send_message(
                "Already waiting for your response...", ephemeral=True
            )
            return

        if self.message is None:
            return

        async with self.input_lock:
            channel = self.message.channel
            author_id = interaction.user and interaction.user.id
            await interaction.response.send_message(
                "What page do you want to go to?", ephemeral=True
            )

            def message_check(m):
                return (
                    m.author.id == author_id
                    and channel == m.channel
                    and m.content.isdigit()
                )

            try:
                msg = await self.ctx.bot.wait_for(
                    "message", check=message_check, timeout=30.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("Took too long.", ephemeral=True)
                await asyncio.sleep(5)
            else:
                page = int(msg.content)
                await msg.delete()
                await self.show_checked_page(interaction, page - 1)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red)
    async def stop_pages(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """stops the pagination session."""
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()


class FieldPageSource(menus.ListPageSource):
    """A page source that requires (field_name, field_value) tuple items."""

    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.embed = discord.Embed(colour=discord.Colour.blurple())

    async def format_page(self, menu, entries):
        self.embed.clear_fields()
        self.embed.description = discord.Embed.Empty

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            self.embed.set_footer(text=text)

        return self.embed


class TextPageSource(menus.ListPageSource):
    def __init__(self, text, *, prefix="```", suffix="```", max_size=2000):
        pages = CommandPaginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split("\n"):
            pages.add_line(line)

        super().__init__(entries=pages.pages, per_page=1)

    async def format_page(self, menu, content):
        maximum = self.get_max_pages()
        if maximum > 1:
            return f"{content}\nPage {menu.current_page + 1}/{maximum}"
        return content


class SimplePageSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.initial_page = True

    async def format_page(self, menu, entries):
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            menu.embed.set_footer(text=footer)

        if self.initial_page and self.is_paginating():
            pages.append("")
            pages.append("Confused? React with \N{INFORMATION SOURCE} for more info.")
            self.initial_page = False

        menu.embed.description = "\n".join(pages)
        return menu.embed


class SimplePages(edoCPages):
    """A simple pagination session reminiscent of the old Pages interface.
    Basically an embed with some normal formatting.
    """

    def __init__(self, entries, *, per_page=12):
        super().__init__(SimplePageSource(entries, per_page=per_page))
        self.embed = discord.Embed(colour=discord.Colour.blurple())


class Paginator(discord.ui.View):
    def __init__(self, ctx, embeds: List[discord.Embed]):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embeds = embeds
        self.current = 0
        self.LeaveIn = 240
        self.pages = len(embeds)

    async def edit(self, msg, pos):
        em = self.embeds[pos]
        em.set_footer(text=f"Page: {pos + 1}/{self.pages} ")
        await msg.edit(embed=em)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back(self, b, i):
        if self.current == 0:
            return
        await self.edit(i.message, self.current - 1)
        self.current -= 1

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.blurple)
    async def stop(self, b, i):
        await i.message.delete()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next(self, b, i):
        if self.current + 1 == len(self.embeds):
            return
        await self.edit(i.message, self.current + 1)
        self.current += 1

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        await interaction.response.send_message("Not your command ._.", ephemeral=True)


class UrbanSource(menus.ListPageSource):
    BRACKETED = re.compile(r"(\[(.+?)\])")

    def __init__(self, data):
        super().__init__(data, per_page=1)

    def cleanup_definition(self, definition, *, regex=BRACKETED):
        def repl(m):
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + " [...]"
        return ret

    async def format_page(self, menu, entries):
        definition = self.cleanup_definition(entries["definition"])

        permalink = entries["permalink"]
        up = entries["thumbs_up"]
        author = entries["author"]
        example = self.cleanup_definition(entries["example"])

        em = Embed(
            title="\N{BOOKS} Definition of " + str(entries["word"]),
            url=permalink,
            description=f"**Definition:**\n{definition}\n\n**Examples:**\n{example}\n<:UpVote:878877980003270686> {up} By {author}",
        )
        em.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")

        try:
            date = discord.utils.parse_time(entries["written_on"][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            em.timestamp = date

        return em


class CatchAllMenu(menus.MenuPages, inherit_buttons=False):
    """
    Lines 16-40 used from Rapptz' discord-ext-menus GitHub repository
    Provided by the MIT License
    https://github.com/Rapptz/discord-ext-menus
    Copyright (c) 2015-2021 Danny Y. (Rapptz)
    """

    def __init__(self, source, **kwargs):
        super().__init__(source, **kwargs)
        self._info_page = f"Info:\n< Go back one page\n> Go forward one page\n<<< Go the the first page\n>>> Go to the last page\nStop Stop the paginator\n<:save:882749805703618590> Go to a page of your choosing\n:<:Info:879146778291744848> Brings you here"

    @menus.button("<<<", position=menus.First(0))
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @menus.button("<", position=menus.Position(0))
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @menus.button("Quit", position=menus.Position(3))
    async def stop_pages(self, payload):
        """stops the pagination session."""
        self.stop()
        await self.message.delete()
        await self.ctx.message.add_reaction(self.ctx.tick())

    @menus.button(">", position=menus.Position(5))
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @menus.button(">>>", position=menus.Position(6))
    async def go_to_last_page(self, payload):
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button("<:save:882749805703618590>", position=menus.Position(4))
    async def _1234(self, payload):
        i = await self.ctx.success("What page would you like to go to?")
        msg = await self.ctx.bot.wait_for(
            "message", check=lambda m: m.author == self.ctx.author
        )
        page = 0
        try:
            page += int(msg.content)
        except ValueError:
            return await self.ctx.send(
                f"**{self.ctx.author.name}**, **{msg.content}** could not be turned into an integer! Please try again!",
                delete_after=3,
            )

        if page > (self._source.get_max_pages()):
            await self.ctx.warn(
                f"There are only **{self._source.get_max_pages()}** pages!",
                delete_after=3,
            )
        elif page < 1:
            await self.ctx.error(f"There is no **{page}th** page!", delete_after=3)
        else:
            index = page - 1
            await self.show_checked_page(index)
            await i.edit(content=f"Transported to page **{page}**!", delete_after=3)

    @menus.button("<:Info:879146778291744848>", position=menus.Position(1))
    async def on_info(self, payload):
        await self.message.edit(
            embed=discord.Embed(description=self.info_page, colour=self.ctx.bot.colour)
        )

    @property
    def info_page(self):
        return self._info_page

    def add_info_fields(self, fields: dict):
        for key, value in fields.items():
            self._info_page += f"\n{key} {value}"


class IndexedListSource(menus.ListPageSource):
    def __init__(
        self,
        data: list,
        embed: discord.Embed,
        per_page: int = 10,
        show_index: bool = True,
        title: str = "Entries",
    ):
        super().__init__(per_page=per_page, entries=data)
        self.embed = embed
        self._show_index = show_index
        self._title = title

    async def format_page(self, menu, entries: list):
        offset = menu.current_page * self.per_page + 1
        embed = self.embed
        if not embed.fields:
            if not entries:
                embed.add_field(name=f"{self._title}", value="No Entries")
                index = 0
            else:
                if self._show_index:
                    embed.add_field(
                        name=f"{self._title}",
                        value="\n".join(
                            f"`[{i:,}]` {v}"
                            for i, v in enumerate(entries, start=offset)
                        ),
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{self._title}",
                        value="\n".join(
                            f"{v}" for i, v in enumerate(entries, start=offset)
                        ),
                        inline=False,
                    )
                index = 0
        else:
            index = len(embed.fields) - 1
        embed.set_footer(
            text=f"({menu.current_page + 1}/{menu._source.get_max_pages()})"
        )
        if not entries:
            embed.set_field_at(index=index, name=f"{self._title}", value="No Entries")
        else:
            if self._show_index:
                embed.set_field_at(
                    index=index,
                    name=f"{self._title}",
                    value="\n".join(
                        f"`[{i:,}]` {v}" for i, v in enumerate(entries, start=offset)
                    ),
                )
            else:
                embed.set_field_at(
                    index=index,
                    name=f"{self._title}",
                    value="\n".join(
                        f"{v}" for i, v in enumerate(entries, start=offset)
                    ),
                )
        return embed


# class PersistentRespondView(ui.View):
#        def __init__(self, bot):
#            super().__init__(timeout=None)
#            self.bot = bot
#
#        class ConfirmationView(ConfirmView):
#            def __init__(self, ctx):
#                super().__init__(ctx, delete_after=True)
#
#            async def confirmed(self, button: ui.Button, interaction: discord.Interaction):
#                await interaction.response.send_message("Message has been sent.", ephemeral=True)
#
#            async def denied(self, button: ui.Button, interaction: discord.Interaction):
#                msg = "Message was not sent, please click on Respond button again to respond."
#                await interaction.response.send_message(msg, ephemeral=True)
#
#        @ui.button(label="Respond", style=discord.ButtonStyle.primary, custom_id="persistent_report_reply")
#        async def res_action(self, button: ui.Button, interaction: discord.Interaction):
#            message = interaction.message
#            bot = self.bot
#            #if bot.tester:
#            #    return
#
#            msg = await interaction.user.send("Please enter your message to respond. You have 60 seconds.")
#            await self.clean_up(message)
#            try:
#                respond = await bot.wait_for("message", check=lambda m: m.channel.id == msg.channel.id, timeout=60)
#            except asyncio.TimeoutError:
#                await msg.edit(content="Timeout. Please click Respond if you want to respond again.", delete_after=60)
#                return await message.edit(view=self)
#            else:
#                await msg.delete()
#            ctx = await bot.get_context(respond)
#            data = await self.get_interface_data(interaction)
#            report_id = data["report_id"]
#            destination = await self.get_destination(interaction, report_id)
#
#            usure = f"Are you sure, you want to send this message to `{destination}`?"
#            if await self.ConfirmationView(ctx).send(usure):
#                # Send to the opposite person
#                dm = await destination.create_dm()
#                msg = dm.get_partial_message(data["message_id"])
#                embed = .default(ctx, title=f"Respond from {ctx.author}", description=respond.content)
#                interface_msg = await msg.reply(embed=embed, view=self)
#
#                query_insert = "INSERT INTO report_respond VALUES($1, $2, $3, $4, $5)"
#                values = (report_id, respond.author.id, interface_msg.id, respond.id, respond.content)
#                await bot.pool.execute(query_insert, *values)
#                await self.clean_up(message)
#            else:
#                await message.edit(view=self)
#
#        @ui.button(label="End Report", style=discord.ButtonStyle.danger, custom_id="persistent_end_report")
#        async def end_action(self, button: ui.Button, interaction: discord.Interaction):
#            message = interaction.message
#            bot = self.bot
#            if bot.tester:
#                return
#
#            interaction_data = await self.get_interface_data(interaction)
#            report_id = interaction_data["report_id"]
#            # Update to database
#            query = "UPDATE reports SET finish=True WHERE report_id=$1"
#            await bot.pool.execute(query, report_id)
#
#            # Send to author
#            desc_user = "You will no longer receive any respond nor able to respond."
#            embed = StellaEmbed.to_error(title="End of Report", description=desc_user)
#            channel = await interaction.user.create_dm()
#            pmessage = channel.get_partial_message(message.id)
#            await pmessage.reply(embed=embed)
#            destination = await self.get_destination(interaction, report_id)
#
#            # Send to the opposite person
#            query_m = "SELECT message_id FROM report_respond WHERE interface_id=$1"
#            data = await bot.pool.fetchval(query_m, message.id, column='message_id')
#            desc_opposite = f"{interaction.user} has ended the report."
#            embed = StellaEmbed.to_error(title="End of Report", description=desc_opposite)
#
#            dm = await destination.create_dm()
#            msg = dm.get_partial_message(data)
#            await msg.reply(embed=embed)
#            await self.clean_up(message)
#
#        async def get_destination(self, interaction, report_id):
#            bot = self.bot
#            stella = bot.stella
#            if interaction.user == stella:
#                report = await bot.pool.fetchrow("SELECT user_id FROM reports WHERE report_id=$1", report_id)
#                return bot.get_user(report["user_id"])
#            return stella
#
#        async def get_interface_data(self, interaction: discord.Interaction) -> Dict[str, int]:
#            old_query = "SELECT report_id, interface_id, message_id FROM report_respond WHERE interface_id=$1"
#            return await self.bot.pool.fetchrow(old_query, interaction.message.id)
#
#        async def clean_up(self, message: discord.Message) -> None:
#            await message.edit(view=None)
#
