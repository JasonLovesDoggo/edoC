# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import pathlib


def fetch_info():
    lines = 0

    python_class = 0
    python_functions = 0
    python_coroutines = 0
    python_comments = 0

    file_amount = 0
    python_file_amount = 0

    p = pathlib.Path('./')
    for f in p.rglob('*.py'):
        if str(f).startswith("venv"):
            continue
        elif str(f).startswith("node_modules"):
            continue
        elif str(f).startswith("ffmpeg"):
            continue
        file_amount += 1
        python_file_amount += 1
        with open(f, 'rb') as of:
            for line in of.read().decode().splitlines():
                line = line.strip()
                if line.startswith('class'):
                    python_class += 1
                if line.startswith('def'):
                    python_functions += 1
                if line.startswith('async def'):
                    python_coroutines += 1
                if '#' in line:
                    python_comments += 1
                lines += 1
    for f in p.rglob('*.txt'):
        if str(f).startswith("venv"):
            continue
        elif str(f).startswith("node_modules"):
            continue
        file_amount += 1
    for f in p.rglob('*.json'):
        if str(f).startswith("venv"):
            continue
        elif str(f).startswith("node_modules"):
            continue
        file_amount += 1
    return {
        "total_lines": lines - 1110,
        "total_python_class": python_class,
        "total_python_functions": python_functions,
        "total_python_coroutines": python_coroutines,
        "total_python_comments": python_comments,
        "file_amount": file_amount,
        "python_file_amount": python_file_amount,
    }
