# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import datetime
from random import randint

from discord.ext.commands import Cog, command
from faker import Faker

from utils.apis.Somerandomapi import SRA


class Profile(Cog, description="A cog that generates fake profile info"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.sra = SRA(session=self.bot.session)

    def fake_profile(self):
        fake = Faker()
        base = fake.profile()
        from decimal import Decimal

        prof = {
            "job": "Acupuncturist",
            "company": "Howard, Reed and Peters",
            "ssn": "014-36-1839",
            "residence": "93557 Moreno Coves\nNancyborough, PA 96910",
            "current_location": (Decimal("-20.479780"), Decimal("112.773438")),
            "blood_group": "A+",
            "website": [
                "https://kelly.com/",
                "https://www.frederick-hudson.info/",
                "https://www.lee-garcia.info/",
            ],
            "username": "hartmantrevor",
            "name": "Alyssa Wallace",
            "sex": "F",
            "address": "49844 Amanda Common\nBlackwellstad, WI 49655",
            "mail": "patriciamiller@gmail.com",
            "birthdate": datetime.date(1927, 12, 8),
        }

        del base["website"]

        return fake.profile()

    async def generate_profile(self, seed):
        fake = Faker(Faker.locales)
        us = fake["en-US"]
        Faker.seed(seed)
        info = {}
        info["address"] = fake.address
        info["automotive"] = fake.automotive
        info["barcode"] = fake.barcode
        info["color"] = fake.color
        info["company"] = fake.company
        info["credit_card"] = fake.credit_card
        info["currency"] = fake.currency
        info["date_time"] = fake.date_time
        info["file"] = fake.file
        info["geo"] = fake.geo
        info["isbn"] = fake.isbn
        info["job"] = fake.job
        info["lorem"] = fake.lorem
        info["misc"] = fake.misc
        info["person"] = fake.person
        info["phone_number"] = fake.phone_number
        info["profile"] = fake.profile
        info["python"] = fake.python
        info["ssn"] = fake.ssn
        info["user_agent"] = fake.user_agent
        if seed > 4000:
            info["building_number"] = fake.building_number()
        return info

    @command(brief="Gives you a random profile.", aliases=["rprof", "randprof"])
    async def randomprofile(self, ctx, seed=randint(1, 9999)):
        await ctx.invis(self.fake_profile())


def setup(bot):
    bot.add_cog(Profile(bot))
