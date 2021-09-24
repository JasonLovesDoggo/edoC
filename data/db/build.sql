/*
 * Copyright (c) 2021. Jason Cameron
 * All rights reserved.
 * This file is part of the edoC discord bot project ,
 * and is released under the "MIT License Agreement". Please see the LICENSE
 * file that should have been included as part of this package.
 */
CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "~",
	LogChannel integer,
	GuildMods integer,
	GuildAdmins integer,
	WelcomeMessage TEXT DEFAULT "Welcome to",
	WelcomeChannel integer,
	OnJoinRole integer
);

CREATE TABLE IF NOT EXISTS User (
	UserID integer PRIMARY KEY,
	WantsFooterOrTag text DEFAULT "True",
	Level integer DEFAULT 0,
	XPLock TEXT DEFAULT CURRENT_TIMESTAMP,
``);

CREATE TABLE IF NOT EXISTS warns (
	UserID integer PRIMARY KEY,
	GuildID integer,
	warningMessage TEXT
);

CREATE TABLE IF NOT EXISTS botban (
	UserID integer PRIMARY KEY,
	Reason TEXT DEFAULT None
);

CREATE TABLE "todo" (
	"todo"	TEXT,
	"id"	NUMERIC,
	"time"	NUMERIC,
	"message_url"	TEXT,
	"user_id"	NUMERIC
);