# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import asyncio
import json
import os
import uuid

from utils import db


def _create_encoder(cls):
    def _default(self, o):
        if isinstance(o, cls):
            return o.to_json()
        return super().default(o)

    return type('_Encoder', (json.JSONEncoder,), {'default': _default})


class Config:
    """The "database" object. Internally based on ``json``."""

    def __init__(self, name, **options):
        self.name = name
        self.object_hook = options.pop('object_hook', None)
        self.encoder = options.pop('encoder', None)

        try:
            hook = options.pop('hook')
        except KeyError:
            pass
        else:
            self.object_hook = hook.from_json
            self.encoder = _create_encoder(hook)

        self.loop = options.pop('loop', asyncio.get_event_loop())
        self.lock = asyncio.Lock()
        if options.pop('load_later', False):
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.name, 'r') as f:
                self._db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self._db = {}

    async def load(self):
        async with self.lock:
            await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self):
        temp = '%s-%s.tmp' % (uuid.uuid4(), self.name)
        with open(temp, 'w', encoding='utf-8') as tmp:
            json.dump(self._db.copy(), tmp, ensure_ascii=True, cls=self.encoder, separators=(',', ':'))

        # atomically move the file
        os.replace(temp, self.name)

    async def save(self):
        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    def get(self, key, *args):
        """Retrieves a config entry."""
        return self._db.get(str(key), *args)

    async def put(self, key, value, *args):
        """Edits a config entry."""
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key):
        """Removes a config entry."""
        del self._db[str(key)]
        await self.save()

    def __contains__(self, item):
        return str(item) in self._db

    def __getitem__(self, item):
        return self._db[str(item)]

    def __len__(self):
        return len(self._db)

    def all(self):
        return self._db


class Plonks(db.Table):
    id = db.PrimaryKeyColumn()
    guild_id = db.Column(db.Integer(big=True), index=True)
    # this can either be a channel_id or an author_id
    entity_id = db.Column(db.Integer(big=True), index=True, unique=True)


class CommandConfig(db.Table, table_name="command_config"):
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
        return statement + "\n" + sql

# class users(db.Table):
#    id = db.Column('INT', nullable=False, primary_key=True)
#    premium = db.Column('BOOL', nullable=False, default=False)
#    banned = db.Column('BOOL', nullable=False, default=False)
#
#
# class guilds(db.Table):
#    id = db.Column("INT", nullable=False, primary_key=True)
#    logchannel = db.Column('INT', nullable=True)
#    welcomechannel = db.Column('INT', nullable=True)
#    joinrole = db.Column('INT', nullable=True)
#    welcomemessage = db.Column('TEXT', nullable=True)
#    premium = db.Column('BOOL', nullable=False, default=False)
#    captcha = db.Column('BOOL', nullable=False, default=False)
#    captchadifficulty = db.Column('INT', nullable=False, default=2)
#
#
# class guild_perms(db.Table):
#    id = db.Column("INT", nullable=False, primary_key=True)
#    mods = db.Column('INT', nullable=True)
#    admins = db.Column('INT', nullable=True)
#
#
# class prefixs(db.Table):
#    id = db.Column("INT", nullable=False, primary_key=True)
#    prefix = db.Column('TEXT', nullable=False, default=default_prefix)
#    author = db.Column('INT', nullable=False, default=845186772698923029)
#    timestamp = db.Column('timestamp', nullable=False, default=time())
#
#
# class info(db.Table):
#    cmds_ran = db.Column('INT', nullable=False, default=0)
#    msgsseen = db.Column('INT', nullable=False, default=0)
#
#
# class cmd_stats(db.Table):
#    author = db.Column('INT', nullable=False)
#    server = db.Column('INT', nullable=False)
#    cmdName = db.Column('TEXT', nullable=False)
#    timestamp = db.Column('timestamp', nullable=False, default=time())
#
#
# class todo(db.Table):
#    todo = db.Column('TEXT', nullable=False)
#    id = db.Column('int', nullable=False, primary_key=True)  # message id
#    timestamp = db.Column('timestamp', nullable=False, default=time())
#    message_url = db.Column('TEXT', nullable=False)
#    user_id = db.Column('INT', nullable=False)
#
# class Feeds(db.Table):
#    id = db.Column('BIGINT', nullable=False, primary_key=True)
#    channel_id = db.Column('BIGINT', nullable=False)
#    role_id = db.Column('BIGINT', nullable=False)
#    name = db.Column('TEXT', nullable=False)
#
# class RTFM(db.Table):
#    id = db.Column('INT', nullable=False, primary_key=True)
#    user_id = db.Column('INT', unique=True, index=True)
#    count = db.Column('INT', default=1)
# todo remove them/replace them with postgres
