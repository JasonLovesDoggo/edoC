# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from utils.Context import edoCContext

flags = {
    "staff": "<:staff:895480890296242206>",
    "partner": "<a:partner:895481226348101642>",
    "hypesquad": "<:DiscordHypeSquad:895481636823646228>",
    "bug_hunter": "<:BugHunter:879146654014529576>",
    "hypesquad_bravery": "<:DiscordHypeSquadBravery:895481724081954866>",
    "hypesquad_brilliance": "<:DiscordHypeSquadBrilliance:895481770991030282>",
    "hypesquad_balance": "<:DiscordHypeSquadBalance:895481676875042836>",
    "early_supporter": "<:DiscordEarlySupporter:895482684523053056>",
    "team_user": "<:ownerthinglol:895483528148566017>",
    "system": "",
    "bug_hunter_level_2": "<:bughunterlvl2:895488751072067595>",
    "verified_bot": "<:verifiedbot:895489006823944192>",
    "verified_bot_developer": "<:DiscordDeveloper:879146778031697981>",
    "discord_certified_moderator": "<:discordmod:895489339214168074>",
    "premium": "<:nitroboost:895491405139554385>",
}


# flags = {}
# flags['staff'] = '<:staff:895480890296242206>'
# flags['partner'] = '<a:partner:895481226348101642>'
# flags['hypesquad'] = '<:DiscordHypeSquad:895481636823646228>'
# flags['bug_hunter'] = '<:BugHunter:879146654014529576>'
# flags['hypesquad_bravery'] = '<:DiscordHypeSquadBravery:895481724081954866>'
# flags['hypesquad_brilliance'] = '<:DiscordHypeSquadBrilliance:895481770991030282>'
# flags['hypesquad_balance'] = '<:DiscordHypeSquadBalance:895481676875042836>'
# flags['early_supporter'] = '<:DiscordEarlySupporter:895482684523053056>'
# flags['team_user'] = '<:ownerthinglol:895483528148566017>'
# flags['system'] = ''  # not used but i dont want an error
# flags['bug_hunter_level_2'] = '<:bughunterlvl2:895488751072067595>'
# flags['verified_bot'] = '<:verifiedbot:895489006823944192>'
# flags['verified_bot_developer'] = '<:DiscordDeveloper:879146778031697981>'
# flags['discord_certified_moderator'] = '<:discordmod:895489339214168074>'
# flags['premium'] = '<:nitroboost:895491405139554385>'


# flags[''] = ''
async def userflagtoicon(ctx: edoCContext):
    allflags = []
    useflags = dict(ctx.author.public_flags)
    for flagname, flag in useflags.items():
        if flag:
            allflags.append(flags[flagname])
    if bool(ctx.author.premium_since):
        allflags.append(flags["premium"])
    await ctx.invis(allflags)
    return allflags
