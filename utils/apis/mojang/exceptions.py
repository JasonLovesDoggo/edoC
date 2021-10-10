"""
The MIT License (MIT)

Copyright (c) 2020 https://github.com/summer

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

"""
# THIS IS A MODIFIED VERSION OF summer's wrapper
# This one is async

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Optional


class MojangError(Exception):
    """Base error class for all library-related exceptions in this file
    Essentially, this could be caught to handle any exceptions thrown from this library.
    """

    def __init__(self, message: Optional[str] = None):
        self.message = message if message else self.__class__.__doc__
        super().__init__(self.message)
