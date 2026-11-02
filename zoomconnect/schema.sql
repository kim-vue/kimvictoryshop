PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS lenses (
 uid TEXT PRIMARY KEY CHECK(length(uid) BETWEEN 1 AND 128 AND instr(uid,'/')=0 AND instr(uid,char(0))=0 AND instr(uid,char(31))=0),
 label TEXT NOT NULL CHECK(length(label) BETWEEN 1 AND 256),
 kind TEXT NOT NULL CHECK(length(kind) BETWEEN 1 AND 64),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS actors (
 id TEXT PRIMARY KEY, name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 128),
 key_digest TEXT NOT NULL UNIQUE, role TEXT NOT NULL DEFAULT 'USER', active INTEGER NOT NULL DEFAULT 1,
 root TEXT NOT NULL REFERENCES lenses(uid)
);
CREATE TABLE IF NOT EXISTS settings (
 id INTEGER PRIMARY KEY CHECK(id=1), root TEXT NOT NULL REFERENCES lenses(uid),
 master_actor TEXT NOT NULL REFERENCES actors(id), head_hash TEXT NOT NULL DEFAULT '', event_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS grants (
 actor TEXT NOT NULL REFERENCES actors(id), lens TEXT NOT NULL REFERENCES lenses(uid),
 right TEXT NOT NULL CHECK(right IN ('move','read','write','execute')),
 PRIMARY KEY(actor,lens,right)
);
CREATE TABLE IF NOT EXISTS connections (
 ordinal INTEGER PRIMARY KEY AUTOINCREMENT,
 uid TEXT NOT NULL UNIQUE CHECK(length(uid) BETWEEN 1 AND 128),
 source TEXT NOT NULL REFERENCES lenses(uid), target TEXT NOT NULL REFERENCES lenses(uid),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE INDEX IF NOT EXISTS connections_source ON connections(source,active,ordinal);
CREATE TABLE IF NOT EXISTS sessions (
 id TEXT PRIMARY KEY CHECK(length(id) BETWEEN 1 AND 256),
 actor TEXT NOT NULL REFERENCES actors(id), root TEXT NOT NULL REFERENCES lenses(uid)
);
CREATE TABLE IF NOT EXISTS frames (
 session TEXT NOT NULL REFERENCES sessions(id), position INTEGER NOT NULL CHECK(position>=0),
 lens TEXT NOT NULL REFERENCES lenses(uid), entry TEXT REFERENCES connections(uid),
 PRIMARY KEY(session,position)
);
CREATE TABLE IF NOT EXISTS bookmarks (
 uid TEXT PRIMARY KEY, actor TEXT NOT NULL REFERENCES actors(id),
 name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 256),
 target TEXT NOT NULL REFERENCES lenses(uid), UNIQUE(actor,name)
);
CREATE TABLE IF NOT EXISTS objects (
 hash TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES lenses(uid), body TEXT NOT NULL,
 created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contracts (
 base_pin TEXT NOT NULL, common_action TEXT NOT NULL,
 inner_lens TEXT NOT NULL REFERENCES lenses(uid), unique_action TEXT NOT NULL,
 version INTEGER NOT NULL CHECK(version>0), algorithm TEXT NOT NULL, input_type TEXT NOT NULL,
 descriptor TEXT NOT NULL,
 PRIMARY KEY(base_pin,common_action,inner_lens,unique_action,version)
);
CREATE TABLE IF NOT EXISTS events (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT NOT NULL,
 session TEXT, kind TEXT NOT NULL, body TEXT NOT NULL, timestamp TEXT NOT NULL,
 previous_hash TEXT NOT NULL, hash TEXT NOT NULL UNIQUE
);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
 BEGIN SELECT RAISE(ABORT,'HISTORY_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
 BEGIN SELECT RAISE(ABORT,'HISTORY_APPEND_ONLY'); END;
