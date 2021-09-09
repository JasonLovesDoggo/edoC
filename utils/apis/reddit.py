# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import aiohttp


class Post:
    __slots__ = (
        "isStickied",
        "title",
        "content",
        "author",
        "is18",
        "isVideo",
        "url",
        "upvotes",
        "downvotes",
        "score",
        "commentCount",
    )

    def __init__(self, data):
        self.isStickied = data["data"]["stickied"]
        self.title = data["data"]["title"]
        self.content = data["data"]["selftext"]
        self.author = data["data"]["author"]
        self.is18 = data["data"]["over_18"]
        self.isVideo = data["data"]["is_video"]
        self.url = data["data"]["url"]
        self.upvotes = data["data"]["ups"]
        self.downvotes = data["data"]["downs"]
        self.score = data["data"]["score"]
        self.commentCount = data["data"]["num_comments"]

    def __str__(self):
        return self.title


class Subreddit:
    def __init__(self, data):
        self.name = data["data"]["children"][0]["data"]["subreddit_name_prefixed"]
        self.posts = [Post(post) for post in data["data"]["children"]]

    def __str__(self):
        return self.name


class Reddit:
    def __init__(self, session=aiohttp.ClientSession(), defaultLimit: int = 100):
        """
        Wrapper for Reddit read-only API
        API Key not required, used to replace praw
        """
        self.baseUrl = (
            "https://www.reddit.com/r/{subreddit}/{listingType}.json?limit={limit}"
        )
        self.defaultLimit = defaultLimit
        self.session = session

    async def get(self, subreddit: str, _type: str, limit: int = None):
        """
        Get posts from a subreddit
        """
        if not limit:
            limit = self.defaultLimit
        async with self.session.get(
                self.baseUrl.format(subreddit=subreddit, listingType=_type, limit=limit)
        ) as res:
            return Subreddit(await res.json())

    async def hot(self, subreddit: str):
        """
        Get hot posts from Reddit
        """
        return await self.get(subreddit, "hot")

    async def top(self, subreddit: str):
        """
        Get hot posts from Reddit
        """
        return await self.get(subreddit, "top")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    reddit = Reddit()
    res = loop.run_until_complete(reddit.top("meme"))
    print(res.posts[1].url)
