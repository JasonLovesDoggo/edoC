import discord

ballresponse = [
    "Yes", "No", "Take a wild guess...", "Very doubtful",
    "Sure", "Without a doubt", "Most likely", "Might be possible",
    "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
    "senpai, pls no ;-;", "Ask again later"
]
CoolColorResponse = [
    "0x2CCC74", "0x04A4EC", "0x142434", "0xFFFFFF"
]

# COLORS
green = 0x2CCC74  # SUCCESS

blue = 0x04A4EC  # NORMAL?

purple = 0x9B40D2  # TWITCH OUTPUT / IDK?

orange = 0xDA8115  # NOTE / SMALL ERROR / LOGS?

magenta = 0xE81354  # ERROR

red = 0xf00  # LARGE ERROR / YOUTUBE OUTPUT

dark_blue = 0x142434  # Looks nice lol

white = 0xFFFFFF  # white

embedfooter = "https://www.buymeacoffee.com/edoC Creating edoC is a tough task, if you would like me to continue with it, please consider donating!"


def ErrorEmbed(ctx, error):
    emb = discord.Embed(title=f"Error with your command",
                        color=red,
                        timestamp=ctx.message.created_at,
                        description=error)
    return emb
