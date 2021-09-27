# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from time import time

from utils import sqlite as db
from utils.vars import default_prefix


class users(db.Table):
    id = db.Column('INT', nullable=False, primary_key=True)
    premium = db.Column('BOOL', nullable=False, default=False)
    banned = db.Column('BOOL', nullable=False, default=False)

class guilds(db.Table):
    id = db.Column("INT", nullable=False, primary_key=True)
    logchannel = db.Column('INT', nullable=True)
    welcomechannel = db.Column('INT', nullable=True)
    joinrole = db.Column('INT', nullable=True)
    welcomemessage = db.Column('TEXT', nullable=True)
    premium = db.Column('BOOL', nullable=False, default=False)

class guild_perms(db.Table):
    id = db.Column("INT", nullable=False, primary_key=True)
    mods = db.Column('INT', nullable=True)
    admins = db.Column('INT', nullable=True)

class prefixs(db.Table):
    id = db.Column("INT", nullable=False, primary_key=True)
    prefix = db.Column('TEXT', nullable=False, default=default_prefix)
    author = db.Column('INT', nullable=False, default=845186772698923029)
    timestamp = db.Column('timestamp', nullable=False, default=time())

class stats(db.Table):
    cmds_ran = db.Column('INT', nullable=False, default=0)
    msgsseen = db.Column('INT', nullable=False, default=0)

class cmd_stats(db.Table):
    author = db.Column('INT', nullable=False)
    server = db.Column('INT', nullable=False)
    cmdName = db.Column('TEXT', nullable=False)
    timestamp = db.Column('timestamp', nullable=False, default=time())



