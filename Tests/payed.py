# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import urllib
import urllib.request
from asyncio import run, get_event_loop
from datetime import datetime
from urllib.error import HTTPError

import aiohttp
from utils.http import HTTPSession
from bs4 import BeautifulSoup
import arrow


class Good:
    def __init__(self):
        self.value = "+"
        self.name = "good"

    def __repr__(self):
        return "<Good(value='%s')>" % self.value


class Bad:
    def __init__(self):
        self.value = "-"
        self.name = "bad"

    def __repr__(self):
        return "<Bad(value='%s')>" % self.value


class Unknow:
    def __init__(self):
        self.value = "?"
        self.name = "unknow"

    def __repr__(self):
        return "<Unknow(value='%s')>" % self.value


class Investing:
    def __init__(self, uri='https://investing.com/economic-calendar'):
        self.uri = uri
        self.req = urllib.request.Request(uri)
        self.req.add_header('User-Agent',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        self.result = []
        self._session_id_ = None
        self._email = 'thebosssg19@gmail.com'
        self._password = '3dD2j3zHQmELfaL'
        self.session = HTTPSession()

    async def _get_session(self):
        c = await self.session.get(url=f'https://www.myfxbook.com/api/login.json?email={self._email}&password={self._password}')
        data = await c.json()
        # next up get clientid from that
        self._session_id_ = data['session']

    async def get_outlook(self):
        if self._session_id_ is None:
            await self._get_session()
        async with self.session.get(
                f'https://www.myfxbook.com/api/get-community-outlook-by-country.json?session={self._session_id_}&symbol=eurusd') as c:
            data = await c.json()
        l = []
        for country in data['countries']:
            print(country)
        return l

    def news(self):
        try:
            response = urllib.request.urlopen(self.req)

            html = response.read()

            soup = BeautifulSoup(html, "html.parser")

            # Find event item fields
            table = soup.find('table', {"id": "economicCalendarData"})
            tbody = table.find('tbody')
            rows = tbody.findAll('tr', {"class": "js-event-item"})

            news = {'timestamp': None,
                    'country': 'USA',
                    'impact': 3,
                    'url': None,
                    'name': None,
                    'bold': None,
                    'fore': None,
                    'prev': None,
                    'signal': None,
                    'type': None}

            for row in rows:
                # print (row.attrs['data-event-datetime'])
                _datetime = row.attrs['data-event-datetime']
                news['timestamp'] = datetime.strftime(_datetime, "YYYY/MM/DD HH:mm:ss")

            for tr in rows:
                cols = tr.find('td', {"class": "flagCur"})
                flag = cols.find('span')

                news['country'] = flag.get('title')

                impact = tr.find('td', {"class": "sentiment"})
                bull = impact.findAll('i', {"class": "grayFullBullishIcon"})

                news['impact'] = len(bull)

                event = tr.find('td', {"class": "event"})
                a = event.find('a')

                news['url'] = "{}{}".format(self.uri, a['href'])
                news['name'] = a.text.strip()

                # Determite type of event
                legend = event.find('span', {"class": "smallGrayReport"})
                if legend:
                    news['type'] = "report"

                legend = event.find('span', {"class": "audioIconNew"})
                if legend:
                    news['type'] = "speech"

                legend = event.find('span', {"class": "smallGrayP"})
                if legend:
                    news['type'] = "release"

                legend = event.find('span', {"class": "sandClock"})
                if legend:
                    news['type'] = "retrieving data"

                bold = tr.find('td', {"class": "bold"})

                if bold.text != '':
                    news['bold'] = bold.text.strip()
                else:
                    news['bold'] = ''

                fore = tr.find('td', {"class": "fore"})
                news['fore'] = fore.text.strip()

                prev = tr.find('td', {"class": "prev"})
                news['prev'] = prev.text.strip()

                if "blackFont" in bold['class']:
                    # print ('?')
                    # news['signal'] = '?'
                    news['signal'] = Unknow()

                elif "redFont" in bold['class']:
                    # print ('-')
                    # news['signal'] = '-'
                    news['signal'] = Bad()

                elif "greenFont" in bold['class']:
                    # print ('+')
                    # news['signal'] = '+'
                    news['signal'] = Good()

                else:
                    news['signal'] = Unknow()

                self.result.append(news)

        except HTTPError as error:
            print(f"Oops... Get error HTTP {error.code}")

        return self.result

async def main():
    i = Investing('https://investing.com/economic-calendar/')
    await i.get_outlook()

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    loop = get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
