import random
import discord

# EMOJIS
emojis = {
    "green_checkmark": "✔",
    "red_x": "❌"
}

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
ColorsList = [green, blue, purple, orange, magenta, dark_blue, white]

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

# SKYBLOCK STUFF
SbColors = {
    "ErrorColor": 0xff0000,
    "TamingColor": 0x89CFF0,
    "FishingColor": 0x1b95e0,
    "FarmingColor": 0xc3db79,
    "CombatColor": 0xd4af37,
    "ForagingColor": 0x006400,
    "EnchantingColor": 0xaf7cac,
    "RunecraftingColor": 0xffb6c1,
    "AlchemyColor": 0xdd143d,
    "CarpentryColor": 0xc6a27e,
    "MiningColor": 0x000000
}

separator = '{:,}'
SkyShiiyuApi = 'https://sky.shiiyu.moe/api/v2/profile/'
SkyShiiyuStats = 'https://sky.shiiyu.moe/stats/'
NameApiUrl = 'https://api.mojang.com/users/profiles/minecraft/'
mcheads = 'https://mc-heads.net/head/'

EMBED_FOOTER = 'With the helps of StickyRunnerTR#9676 and VxnomRandom#6495.'


# END OF SKYBLOCK STUFF
def picture(image_name=None):
    images = {
        "SUCCESS": "https://i.imgur.com/sp2zmN9.png",
        "ERROR": "https://i.imgur.com/lLlHVPq.png",
        "GSHEET": "https://i.imgur.com/u9PgNkk.png",
        "Warning": 'https://media.giphy.com/media/uljItOrPUGYfXrgAhO/giphy.gif'
    }
    return images[image_name]


def random_color():
    return discord.Color.from_rgb(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))


embedfooter = "https://www.buymeacoffee.com/edoC Creating edoC is a tough task, if you would like me to continue with it, please consider donating!"

version_info = {
    "info": "Yeah we got ~lizard why you askin?",
    "version": 0.89,
}


async def ErrorEmbed(ctx, error):
    emb = discord.Embed(title=f"Error with your command",
                        color=red,
                        description=error)
    emb.set_footer(text=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=emb)


# Bot replies
NEGATIVE_REPLIES = [
    "Noooooo!!",
    "Nope.",
    "I'm sorry Dave, I'm afraid I can't do that.",
    "I don't think so.",
    "Not gonna happen.",
    "Out of the question.",
    "Huh? No.",
    "Nah.",
    "Naw.",
    "Not likely.",
    "No way, José.",
    "Not in a million years.",
    "Fat chance.",
    "Certainly not.",
    "NEGATORY.",
    "Nuh-uh.",
    "Not in my house!",
]

POSITIVE_REPLIES = [
    "Yep.",
    "Absolutely!",
    "Can do!",
    "Affirmative!",
    "Yeah okay.",
    "Sure.",
    "Sure thing!",
    "You're the boss!",
    "Okay.",
    "No problem.",
    "I got you.",
    "Alright.",
    "You got it!",
    "ROGER THAT",
    "Of course!",
    "Aye aye, cap'n!",
    "I'll allow it.",
]

ERROR_REPLIES = [
    "Please don't do that.",
    "You have to stop.",
    "Do you mind?",
    "In the future, don't do that.",
    "That was a mistake.",
    "You blew it.",
    "You're bad at computers.",
    "Are you trying to kill me?",
    "Noooooo!!",
    "I can't believe you've done this",
]

random_facts = [
    "The amount of time almost equal to 69% of a week is 4 days and 20 hours",
    "Our auditory reaction time is twice as fast as our visual reaction time",
    "If you have 3 quarters, 4 dimes, and 4 pennies, you have $1.19. You also have the largest amount of money in coins without being able to make change for a dollar.",
    "The numbers '172' can be found on the back of the U.S. $5 dollar bill in the bushes at the base of the Lincoln Memorial.",
    "President Kennedy was the fastest random speaker in the world with upwards of 350 words per minute.",
    "In the average lifetime, a person will walk the equivalent of 5 times around the equator.",
    "Odontophobia is the fear of teeth.",
    "The 57 on Heinz ketchup bottles represents the number of varieties of pickles the company once had.",
    'In the early days of the telephone, operators would pick up a call and use the phrase, "Well, are you there?". It wasn\'t until 1895 that someone suggested answering the phone with the phrase "number please?"'
    "The surface area of an average-sized brick is 79 cm squared.",
    "According to suicide statistics, Monday is the favored day for self-destruction.",
    "Cats sleep 16 to 18 hours per day.",
    "The most common name in the world is Mohammed.",
    "It is believed that Shakespeare was 46 around the time that the King James Version of the Bible was written. In Psalms 46, the 46th word from the first word is shake and the 46th word from the last word is spear.",
    'Karoke means "empty orchestra" in Japanese.',
    "The Eisenhower interstate system requires that one mile in every five must be straight. These straight sections are usable as airstrips in times of war or other emergencies.",
    "The first known contraceptive was crocodile dung, used by Egyptians in 2000 B.C.",
    'Rhode Island is the smallest state with the longest name. The official name, used on all state documents, is "Rhode Island and Providence Plantations."',
    "When you die your hair still grows for a couple of months.",
    "There are two credit cards for every person in the United States.",
    "Isaac Asimov is the only author to have a book in every Dewey-decimal category.",
    "The newspaper serving Frostbite Falls, Minnesota, the home of Rocky and Bullwinkle, is the Picayune Intellegence.",
    "It would take 11 Empire State Buildings, stacked one on top of the other, to measure the Gulf of Mexico at its deepest point.",
    "The first person selected as the Time Magazine Man of the Year - Charles Lindbergh in 1927.",
    "The most money ever paid for a cow in an auction was $1.3 million.",
    'It took Leo Tolstoy six years to write "War & Peace".',
    "The Neanderthal's brain was bigger than yours is.",
    "On the new hundred dollar bill the time on the clock tower of Independence Hall is 4:10.",
    "Each of the suits on a deck of cards represents the four major pillars of the economy in the middle ages: heart represented the Church, spades represented the military, clubs represented agriculture, and diamonds represented the merchant class.",
    "The names of the two stone lions in front of the New York Public Library are Patience and Fortitude. They were named by then-mayor Fiorello LaGuardia.",
    "The Main Library at Indiana University sinks over an inch every year because when it was built, engineers failed to take into account the weight of all the books that would occupy the building.",
    "The sound of E.T. walking was made by someone squishing her hands in jelly.",
    "Lucy and Linus (who where brother and sister) had another little brother named Rerun. (He sometimes played left-field on Charlie Brown's baseball team, [when he could find it!]).",
    "The pancreas produces Insulin.",
    "1 in 5,000 north Atlantic lobsters are born bright blue.",
    "There are 10 human body parts that are only 3 letters long (eye hip arm leg ear toe jaw rib lip gum).",
    "A skunk's smell can be detected by a human a mile away.",
    'The word "lethologica" describes the state of not being able to remember the word you want.',
    "The king of hearts is the only king without a moustache.",
    "Henry Ford produced the model T only in black because the black paint available at the time was the fastest to dry.",
    "Mario, of Super Mario Bros. fame, appeared in the 1981 arcade game, Donkey Kong. His original name was Jumpman, but was changed to Mario to honor the Nintendo of America's landlord, Mario Segali.",
    "The three best-known western names in China: Jesus Christ, Richard Nixon, and Elvis Presley.",
    "Every year about 98% of the atoms in your body are replaced.",
    "Elephants are the only mammals that can't jump.",
    "The international telephone dialing code for Antarctica is 672.",
    "World Tourist day is observed on September 27.",
    "Women are 37% more likely to go to a psychiatrist than men are.",
    "The human heart creates enough pressure to squirt blood 30 feet (9 m).",
    "Diet Coke was only invented in 1982.",
    "There are more than 1,700 references to gems and precious stones in the King James translation of the Bible.",
    "When snakes are born with two heads, they fight each other for food.",
    "American car horns beep in the tone of F.",
    "Turning a clock's hands counterclockwise while setting it is not necessarily harmful. It is only damaging when the timepiece contains a chiming mechanism.",
    "There are twice as many kangaroos in Australia as there are people. The kangaroo population is estimated at about 40 million.",

    "Police dogs are trained to react to commands in a foreign language; commonly German but more recently Hungarian.",
    "The Australian $5 to $100 notes are made of plastic.",
    "St. Stephen is the patron saint of bricklayers.",
    "The average person makes about 1,140 telephone calls each year.",
    "Stressed is Desserts spelled backwards.",
    "If you had enough water to fill one million goldfish bowls, you could fill an entire stadium.",
    "Mary Stuart became Queen of Scotland when she was only six days old.",
    "Charlie Brown's father was a barber.",
    "Flying from London to New York by Concord, due to the time zones crossed, you can arrive 2 hours before you leave.",
    "Dentists have recommended that a toothbrush be kept at least 6 feet (2 m) away from a toilet to avoid airborne particles resulting from the flush.",
    "You burn more calories sleeping than you do watching TV.",
    "A lion's roar can be heard from five miles away.",
    'The citrus soda 7-UP was created in 1929; "7" was selected because the original containers were 7 ounces. "UP" indicated the direction of the bubbles.',
    "Canadian researchers have found that Einstein's brain was 15% wider than normal.",
    "The average person spends about 2 years on the phone in a lifetime.",
    "The fist product to have a bar code was Wrigleys gum.",
    "The largest number of children born to one woman is recorded at 69. From 1725-1765, a Russian peasant woman gave birth to 16 sets of twins, 7 sets of triplets, and 4 sets of quadruplets.",
    'Beatrix Potter created the first of her legendary "Peter Rabbit" children\'s stories in 1902.',
    "In ancient Rome, it was considered a sign of leadership to be born with a crooked nose.",
    'The word "nerd" was first coined by Dr. Seuss in "If I Ran the Zoo."',
    "A 41-gun salute is the traditional salute to a royal birth in Great Britain.",
    "The bagpipe was originally made from the whole skin of a dead sheep.",
    "The roar that we hear when we place a seashell next to our ear is not the ocean, but rather the sound of blood surging through the veins in the ear. Any cup-shaped object placed over the ear produces the same effect.",
    "Revolvers cannot be silenced because of all the noisy gasses which escape the cylinder gap at the rear of the barrel.",
    "Liberace Museum has a mirror-plated Rolls Royce; jewel-encrusted capes, and the largest rhinestone in the world, weighing 59 pounds and almost a foot in diameter.",
    "A car that shifts manually gets 2 miles more per gallon of gas than a car with automatic shift.",
    "Cats can hear ultrasound.",
    "Dueling is legal in Paraguay as long as both parties are registered blood donors.",
    "The highest point in Pennsylvania is lower than the lowest point in Colorado.",
    "The United States has never lost a war in which mules were used.",
    "Children grow faster in the springtime.",
    "On average, there are 178 sesame seeds on each McDonalds BigMac bun.",
    "Paul Revere rode on a horse that belonged to Deacon Larkin.",
    "The Baby Ruth candy bar was actually named after Grover Cleveland's baby daughter, Ruth.",
    "Minus 40 degrees Celsius is exactly the same as minus 40 degrees Fahrenheit.",
    'Clans of long ago that wanted to get rid of unwanted people without killing them used to burn their houses down -- hence the expression "to get fired"',
    "Nobody knows who built the Taj Mahal. The names of the architects, masons, and designers that have come down to us have all proved to be latter-day inventions, and there is no evidence to indicate who the real creators were.",
    "Every human spent about half an hour as a single cell.",
    "7.5 million toothpicks can be created from a cord of wood.",
    "The plastic things on the end of shoelaces are called aglets.",
    "A 41-gun salute is the traditional salute to a royal birth in Great Britain.",
    'The earliest recorded case of a man giving up smoking was on April 5, 1679, when Johan Katsu, Sheriff of Turku, Finland, wrote in his diary "I quit smoking tobacco." He died one month later.',
    'Goodbye" came from "God bye" which came from "God be with you."',
    "February is Black History Month.",
    "Jane Barbie was the woman who did the voice recordings for the Bell System.",
    "The first drive-in service station in the United States was opened by Gulf Oil Company - on December 1, 1913, in Pittsburgh, Pennsylvania.",
    "The elephant is the only animal with 4 knees.",
    "Kansas state law requires pedestrians crossing the highways at night to wear tail lights."
]

rules = """
        **Main Rules**
        
        **[ 1. ] »** Always abide by Discord [Terms of Services](https://discord.com/terms) & [Guidelines.](https://discord.com/guidelines)
        
        **[ 2. ] »** No harassment or cyberbullying - this includes bullying members though DMs.
        
        **[ 3. ] »** No discrimination of any kind - this includes but is not limited to racism, homophobia and bigotry.
        
        **[ 4. ] »** No spam, toxicity, NSFW (this includes PFP's/Nicks )or excessive swearing (light swearing is acceptable).
        
        **[ 5. ] »** Don’t mention people without reason (including ghost pinging) - this includes all members as well as staff.
        
        **[ 6. ] »** Don’t mini-mod - you can point people in the right direction or inform them of the rules but don’t impersonate a mod, members with Trusted role are exempt from this.
                
        **[ 7. ] »** No Abusing alternate accounts.
        
        **[ 8. ] »** Use the channels for their correct purpose.
        
        **[ 9. ] »** Treat everyone with respect. Absolutely no harassment, witch hunting, sexism, racism, or hate speech will be tolerated.
        
        **[ 10. ] »** Always obey staff, do not argue with them.
        
        **[ 11. ] »** Don't release personal information.
        
        **[ 12. ] »** Don't ask for roles.
        
        **[ 13. ] »** Our rules aren't perfect, if a mod/admin thinks you broke a rule that isn't here, they have the permission to warn/mute/ban/kick you accordingly.
        
        **[ 14. ] »** Treat everyone with respect. Absolutely no harassment, witch hunting, sexism, racism, or hate speech will be tolerated.
        
        **[ 15. ] »** No spam or self-promotion (server invites, advertisements, etc) without permission from a staff member. This includes DMing fellow members.
        
        **Voice Chat Rules**
        **[ 1 ] »** All the above rules still apply in voice chats.
        
        **[ 2 ] »** Don't Earrape.
        
        **[ 3 ] »** Don’t play music/videos through your mic - use the appropriate bots. 
        
        **[ 4 ] »** No audible eating, chewing and shouting.
        
        **[ 5 ] »** Be aware of your background noise.
        """
"""
Types of permission checks you can run
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
