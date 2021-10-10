# from utils.colors import Colors

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def hex_to_rgb(value):
    value = value.replace("#", "")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def convert_all_to_hex(inputcolor, colortypeisknown=None):
    """try:
        color = rgb2hex(inputcolor, force_long=True)
    except ValueError:
        pass
    try:
        color = hsl2hex(inputcolor)
    except ValueError:
        pass"""
    inputcolor.get_hex()


print(convert_all_to_hex())
