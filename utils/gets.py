import datetime
import re

from colour import Color
from discord import utils

# Get time difference obviously
def getTimeDiff(t, now=None):
    if now is None:
        now = datetime.datetime.utcnow()
    delta = now - t
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return '{d}:{h}:{m}:{s}'.format(d=days, h=hours, m=minutes, s=seconds)


# Returns time that has passed since the given time(datetime) in seconds, minuts, hours or days
# Fuck Years, who cars, days is more intersting for comparison.
def getAgo(time):
    sec = int((datetime.datetime.utcnow() - time).total_seconds())
    if 120 > sec:
        return f'{sec} seconds ago'
    elif 3600 > sec:
        return '{} minutes ago'.format(sec // 60)
    elif 86400 > sec:
        return '{} hour ago'.format(sec // 60 // 60) if 7200 > sec else '{} hours ago'.format(sec // 60 // 60)
    else:
        return '{} day ago'.format(sec // 60 // 60 // 24) if 7200 > sec else '{} days ago'.format(sec // 60 // 60 // 24)


# Find User on server
def getUser(ctx, msg):
    if '' is msg:
        return ctx.message.author
    elif 1 == len(ctx.message.mentions):
        return ctx.message.mentions[0]
    elif not ctx.guild:
        if utils.find(lambda m: msg.lower() in m.name.lower(), ctx.bot.users):
            return utils.find(lambda m: msg.lower() in m.name.lower(), ctx.bot.users)
        elif ctx.get_user(int(msg)):
            return ctx.get_user(int(msg))
    elif msg.isdigit():
        return ctx.guild.get_member(int(msg))
    elif ctx.message.guild.get_member_named(msg):
        return ctx.message.guild.get_member_named(msg)
    elif utils.find(lambda m: msg.lower() in m.name.lower(), ctx.message.guild.members):
        return utils.find(lambda m: msg.lower() in m.name.lower(), ctx.message.guild.members)
    else:
        for member in ctx.message.guild.members:
            if member.nick:
                if msg.lower() in member.nick.lower():
                    return member
    return None


# Find Guild
def getGuild(ctx, msg):
    if msg == '':
        return ctx.guild
    elif msg.isdigit():
        return ctx.bot.get_guild(int(msg))
    else:
        return utils.find(lambda g: msg.lower() in g.name.lower(), ctx.bot.guilds)


# Find Channel
def getChannel(ctx, msg):
    if msg == '':
        return ctx.channel
    elif 1 == len(ctx.message.channel_mentions):
        return ctx.message.channel_mentions[0]
    elif msg.isdigit():
        return ctx.bot.get_channel(int(msg))
    elif utils.find(lambda c: msg.lower() in c.name.lower(), ctx.guild.text_channels):
        return utils.find(lambda c: msg.lower() in c.name.lower(), ctx.guild.text_channels)
    else:
        return utils.find(lambda c: msg.lower() in c.name.lower(), ctx.bot.get_all_channels())


# Find Role
def getRole(ctx, msg):
    if msg == '':
        return ctx.guild.default_role
    if 1 == len(ctx.message.role_mentions):
        return ctx.message.role_mentions[0]
    elif msg.isdigit():
        return utils.find(lambda r: msg.strip() == r.id, ctx.guild.roles)
    else:
        return utils.find(lambda r: msg.strip().lower() in r.name.lower(), ctx.guild.roles)

def getEmote(ctx, content):
    emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>').findall(content)
    if emoji_reg:
        return ctx.bot.get_emoji(int(emoji_reg[0]))
    elif content.strip().isdigit():
        return ctx.bot.get_emoji(int(content.strip()))
    return None

def getColor(incolor):
    if len(incolor.split(',')) == 3:
        try:
            incolor = incolor.strip("()").split(',')
            if float(incolor[0]) > 1.0 or float(incolor[1]) > 1.0 or float(incolor[2]) > 1.0:
                red = float(int(incolor[0]) / 255)
                blue = float(int(incolor[1]) / 255)
                green = float(int(incolor[2]) / 255)
            else:
                red = incolor[0]
                blue = incolor[1]
                green = incolor[2]
            outcolor = Color(rgb=(float(red), float(green), float(blue)))
        except:
            outcolor = None
    else:
        try:
            outcolor = Color(incolor)
        except:
            outcolor = None

        if outcolor is None:
            try:
                outcolor = Color('#' + incolor)
            except:
                outcolor = None

        if outcolor is None:
            try:
                outcolor = Color('#' + incolor[2:])
            except:
                outcolor = None
    return outcolor