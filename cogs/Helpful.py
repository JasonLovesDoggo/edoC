# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from discord.ext.commands import *


class Helpful(Cog, description="Some helpful stuff.."):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_report = CooldownMapping.from_cooldown(5, 30, BucketType.user)

    # @command(help="Reports to the owner through the bot. Automatic blacklist if abuse.")
    # @cooldown(1, 60, BucketType.user)
    # async def report(self, ctx, *, message: str):
    #    usure = f"Are you sure you wanna send this message to `{self.bot.stella}`?"
    #    if not await ConfirmView(ctx).send(usure):
    #        return


#
#    try:
#        embed = Embed(
#            title=f"Report sent to {self.bot.owner}",
#            description=f"**You sent:** {message}"
#        )
#        embed.set_author(name=f"Any respond from {self.bot.stella} will be through DM.")
#        interface = await ctx.author.send(embed=embed)
#    except discord.Forbidden:
#        died = "Unable to send a DM, please enable DM as it is crucial for the report."
#        raise CommandError(died)
#    else:
#        query = "INSERT INTO reports VALUES(DEFAULT, $1, False, $2) RETURNING report_id"
#        created_at = ctx.message.created_at.replace(tzinfo=None)
#        report_id = await self.bot.pool.fetchval(query, ctx.author.id, created_at, column='report_id')
#
#        embed = BaseEmbed.default(ctx, title=f"Reported from {ctx.author} ({report_id})", description=message)
#        msg = await self.bot.send(embed=embed, view=PersistentRespondView(self.bot))
#        await ctx.confirmed()
#
#        query_msg = "INSERT INTO report_respond VALUES($1, $2, $3, $4, $5)"
#        msg_values = (report_id, ctx.author.id, msg.id, interface.id, message)
#        await self.bot.pool.execute(query_msg, *msg_values)
#
# @report.error
# async def report_error(self, ctx, error):
#    if isinstance(error, CommandOnCooldown):
#        if self.cooldown_report.update_rate_limit(ctx.message):
#            r = "Spamming cooldown report message."
#            await self.bot.add_blacklist(ctx.author.id, r)
#            await ctx.error(f'You have been added to the blacklist for {r}\nPlease Join the support server to appeal')
#
def setup(bot):
    bot.add_cog(Helpful(bot))
