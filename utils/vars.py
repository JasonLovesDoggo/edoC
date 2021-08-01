import discord
ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'

ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

digits = '0123456789'

hexdigits = '0123456789abcdefABCDEF'

octdigits = '01234567'

printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

whitespace = ' \t\n\r\x0b\x0c'
MorseCode = {'A': '.-', 'B': '-...', 'C': '-.-.',
             'D': '-..', 'E': '.', 'F': '..-.',
             'G': '--.', 'H': '....', 'I': '..',
             'J': '.---', 'K': '-.-', 'L': '.-..',
             'M': '--', 'N': '-.', 'O': '---',
             'P': '.--.', 'Q': '--.-', 'R': '.-.',
             'S': '...', 'T': '-', 'U': '..-',
             'V': '...-', 'W': '.--', 'X': '-..-',
             'Y': '-.--', 'Z': '--..',

             '0': '-----', '1': '.----', '2': '..---',
             '3': '...--', '4': '....-', '5': '.....',
             '6': '-....', '7': '--...', '8': '---..',
             '9': '----.', ' ': '/'
             }
MorseCodeReversed = {'..-.': 'f', '-..-': 'x', '/': ' ',
                     '.--.': 'p', '-': 't', '..---': '2',
                     '....-': '4', '-----': '0', '--...': '7',
                     '...-': 'v', '-.-.': 'c', '.': 'e', '.---': 'j',
                     '---': 'o', '-.-': 'k', '----.': '9', '..': 'i ',
                     '.-..': 'l', '.....': '5', '...--': '3', '-.--': 'y',
                     '-....': '6', '.--': 'w', '....': 'h', '-.': 'n', '.-.': 'r',
                     '-...': 'b', '---..': '8', '--..': 'z', '-..': 'd', '--.-': 'q',
                     '--.': 'g', '--': 'm', '..-': 'u', '.-': 'a', '...': 's', '.----': '1'}
random_facts = [
    "The amount of time almost equal to 69% of a week is 4 days and 20 hours", "Our auditory reaction time is twice as fast as our visual reaction time"
]

ballresponse = [
    "Yes", "No", "Take a wild guess...", "Very doubtful",
    "Sure", "Without a doubt", "Most likely", "Might be possible",
    "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
    "senpai, pls no ;-;", "Reply hazy try again."
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

red = 0xff0000  # LARGE ERROR / YOUTUBE OUTPUT

dark_blue = 0x142434  # Looks nice lol

white = 0xFFFFFF  # white
ColorsList = [green, blue, purple, orange, magenta, red, dark_blue, white]

colors = {
    "green": green,
    "blue": blue,
    "purple": purple,
    "orange": orange,
    "magenta": magenta,
    "red": red,
    "dark_blue": dark_blue,
    "white": white,
}

embedfooter = "https://www.buymeacoffee.com/edoC Creating edoC is a tough task, if you would like me to continue with it, please consider donating!"

version_info = {
    "info": "Updates and fixes",
    "version": 0.86,
}


def ErrorEmbed(ctx, error):
    emb = discord.Embed(title=f"Error with your command",
                        color=red,
                        timestamp=ctx.message.created_at,
                        description=error)
    return emb


"""  Types of permission checks you can run
add_reactions
administrator
attach_files
ban_members
change_nickname
connect
create_instant_invite
deafen_members
embed_links
external_emojis
kick_members
manage_channels
manage_emojis
manage_guild
manage_messages
manage_nicknames
manage_permissions Just renamed managed roles can use both
manage_roles 
manage_webhooks
mention_everyone
move_members
mute_members
priority_speaker
read_message_history
read_messages
request_to_speak
send_messages
send_tts_messages
speak
stream
use_external_emojis
use_slash_commands
use_voice_activation
value
view_audit_log
view_channel
view_guild_insights
Methods
"""
