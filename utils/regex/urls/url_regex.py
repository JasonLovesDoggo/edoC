# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import re

from . import tlds

tlds_sort = "|".join([g for g in sorted(tlds.tlds_list)])


class Url:
    def __init__(self, full: str, full_domain: str, domain: str, protocol: str = None):
        self.full = full
        self.full_domain = full_domain
        self.domain = domain
        self.protocol = protocol

    def __repr__(self):
        return '<Url full={0.full} full_domain={0.full_domain} domain={0.domain} protocol={0.protocol}'.format(self)


class UrlRegex:
    def __init__(self, text: str, strict: bool = True, real_tld: bool = True):
        self.strict = strict
        self.text = text
        self.real_tld = real_tld

        buildReg = self.build_regex
        self.regex = buildReg
        self.links_found = {}

    @property
    def build_regex(self):
        protocol = f"(?:(?:[a-z]+:)?//){'?' if self.strict else ''}"
        auth = "(?:\\S+(?::\\S*)?@)?"
        host = "(?:(?:[a-z\\u00a1-\\uffff0-9][-_]*)*[a-z\\u00a1-\\uffff0-9]+)"
        domain = "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)*"
        tld = "(?:\\.{})\\.?".format('(?:[a-z\\u00a1-\\uffff]{2,})')
        port = "(?::\\d{2,5})?"
        path = '(?:[/?#][^\\s,.\"]*)?'

        regex = f"(?:({protocol}|www\\.)){auth}(?:(localhost|{host}{domain}{tld}))({port}{path})"
        return regex

    @property
    def detect(self):
        """ Checks if string includes one or more links """
        if self.real_tld:
            found_anything = False
            for entry in re.findall(self.regex, self.text.lower()):
                get_last = entry[1].split(".")
                if get_last and get_last[-1] in tlds.tlds_list:
                    found_anything = True
            return found_anything
        else:
            return re.search(self.regex, self.text.lower()) is not None

    @property
    def links(self):
        """ Displays links in a pretty format """
        regex = re.findall(self.regex, self.text.lower())

        for i, g in enumerate(regex):
            get_last = g[1].split(".")
            self.links_found[i] = Url(
                f"{g[0]}{g[1]}{g[2]}",  # Full domain
                g[1],  # Full domain
                f"{get_last[-2]}.{get_last[-1]}",  # Domain
                g[0] if g[0] else None  # Protocol
            )

        return list(self.links_found.values())
