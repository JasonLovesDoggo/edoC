from colour import *


# from utils.colors import Colors
def hex_to_rgb(value):
    value = value.replace('#', '')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


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
