CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "~",
	GuildName TEXT,
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
	Banned text DEFAULT "False"
);

CREATE TABLE IF NOT EXISTS warns (
	UserID integer PRIMARY KEY,
	GuildID integer,
	warningMessage TEXT
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS botban (
	UserID integer PRIMARY KEY,
	Reason TEXT DEFAULT None
);

CREATE TABLE IF NOT EXISTS todo (
	TodoID integer PRIMARY KEY,
	TodoText TEXT
);

CREATE TABLE IF NOT EXISTS tag (
	TagName TEXT     PRIMARY KEY,
	TagText TEXT,
	TagCreator TEXT
)
