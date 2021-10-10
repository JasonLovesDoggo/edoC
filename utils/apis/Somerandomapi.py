# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from urllib.parse import quote

import aiohttp


class Invalid_endpoint(BaseException):
    pass


class SRA:
    def __init__(self, key=None, session=None):
        """Wrapper for some-random-api's API.
        Parameter
        ---------
        key = Your SRA api key
        """
        self.apiKey = key
        self.session = session or aiohttp.ClientSession()
        self.baseUrl = "https://some-random-api.ml/"

    async def check_endpoint(self, endpoints: list, endpoint, type):
        endpoint = endpoint.lower()
        if endpoint not in endpoints:
            raise Invalid_endpoint(
                f"{endpoint} isnt an valid endpoint\nthe list of valid {type} ones are {endpoints}"
            )

    async def _get(self, url, *args, **kwargs):
        async with self.session.get(url, *args, **kwargs) as ses:
            if ses.status == 200:
                json = await ses.json()
            else:
                print(ses.status)
                json = await ses.json()
        return json

    async def bot_token(self, id: int = None):
        js = await self._get(f"{self.baseUrl}bottoken?id={id}")
        return js["token"]

    async def its_so_stupid(self, text: quote, avatar: str):
        # text = quote(text)
        return f"{self.baseUrl}canvas/its-so-stupid?avatar={avatar}?dog={text}"

    async def binary_encode(self, text: quote):
        js = await self._get(f"{self.baseUrl}binary?encode={text}")
        return js["text"]

    async def binary_decode(self, text: quote):
        js = await self._get(f"{self.baseUrl}binary?decode={text}")
        return js["text"]

    async def animal(self, type: str):
        availible_endpoints = [
            "panda",
            "dog",
            "cat",
            "fox",
            "red_panda",
            "koala",
            "birb",
            "raccoon",
            "kangaroo",
            "whale",
        ]
        await self.check_endpoint(availible_endpoints, type, "animal")
        js = await self._get(f"{self.baseUrl}animal/{type}")
        return Img(js)


class Img:
    __slots__ = (
        "panda",
        "dog",
        "cat",
        "fox",
        "red_panda",
        "koala",
        "birb",
        "raccoon",
        "kangaroo",
        "whale",
    )

    def __init__(self, data):
        self.image = data["image"]
        self.fact = data["fact"]

    def __str__(self):
        return self.fact

    @property
    def img(self):
        return self.image

    @property
    def fact(self):
        return self.fact
