# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from time import time

from utils import db
from utils.vars import default_prefix


class Plonks(db.Table):
    id = db.PrimaryKeyColumn()
    guild_id = db.Column(db.Integer(big=True), index=True)
    # this can either be a channel_id or an author_id
    entity_id = db.Column(db.Integer(big=True), index=True, unique=True)

class CommandConfig(db.Table, table_name='command_config'):
    id = db.PrimaryKeyColumn()

    guild_id = db.Column(db.Integer(big=True), index=True)
    channel_id = db.Column(db.Integer(big=True))

    name = db.Column(db.String)
    whitelist = db.Column(db.Boolean)

    @classmethod
    def create_table(cls, *, exists_ok=True):
        statement = super().create_table(exists_ok=exists_ok)
        # create the unique index
        sql = "CREATE UNIQUE INDEX IF NOT EXISTS command_config_uniq_idx ON command_config (channel_id, name, whitelist);"
        return statement + '\n' + sql

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
    captcha = db.Column('BOOL', nullable=False, default=False)
    captchadifficulty = db.Column('INT', nullable=False, default=2)


class guild_perms(db.Table):
    id = db.Column("INT", nullable=False, primary_key=True)
    mods = db.Column('INT', nullable=True)
    admins = db.Column('INT', nullable=True)


class prefixs(db.Table):
    id = db.Column("INT", nullable=False, primary_key=True)
    prefix = db.Column('TEXT', nullable=False, default=default_prefix)
    author = db.Column('INT', nullable=False, default=845186772698923029)
    timestamp = db.Column('timestamp', nullable=False, default=time())


class info(db.Table):
    cmds_ran = db.Column('INT', nullable=False, default=0)
    msgsseen = db.Column('INT', nullable=False, default=0)


class cmd_stats(db.Table):
    author = db.Column('INT', nullable=False)
    server = db.Column('INT', nullable=False)
    cmdName = db.Column('TEXT', nullable=False)
    timestamp = db.Column('timestamp', nullable=False, default=time())


class todo(db.Table):
    todo = db.Column('TEXT', nullable=False)
    id = db.Column('int', nullable=False, primary_key=True)  # message id
    timestamp = db.Column('timestamp', nullable=False, default=time())
    message_url = db.Column('TEXT', nullable=False)
    user_id = db.Column('INT', nullable=False)

class Feeds(db.Table):
    id = db.Column('BIGINT', nullable=False, primary_key=True)
    channel_id = db.Column('BIGINT', nullable=False)
    role_id = db.Column('BIGINT', nullable=False)
    name = db.Column('TEXT', nullable=False)

class RTFM(db.Table):
    id = db.Column('INT', nullable=False, primary_key=True)
    user_id = db.Column('INT', unique=True, index=True)
    count = db.Column('INT', default=1)
