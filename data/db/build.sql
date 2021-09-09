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

CREATE TABLE playlists (
    user_id BIGINT NOT NULL,
    playlist_name VARTEXT(32) NOT NULL,
    playlist_id INT NOT NULL PRIMARY KEY
);

CREATE TABLE playlist_songs (
    playlist_id INT NOT NULL,
    playlist_song TEXT NOT NULL,
    playlist_url TEXT NOT NULL,
    song_id INT NOT NULL DEFAULT -1
);