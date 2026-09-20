import sqlite3
from pathlib import Path
from typing import Optional

class Database:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.init()

    def init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS players(
            guid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            country_key TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_income_turn INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS countries(
            key TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            emoji TEXT NOT NULL,
            economy INTEGER NOT NULL,
            industry INTEGER NOT NULL,
            population INTEGER NOT NULL,
            power INTEGER NOT NULL,
            territory INTEGER NOT NULL,
            treasury INTEGER NOT NULL,
            research INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS relations(
            a TEXT NOT NULL,
            b TEXT NOT NULL,
            relation TEXT NOT NULL,
            PRIMARY KEY(a,b)
        );

        CREATE TABLE IF NOT EXISTS game_state(
            id INTEGER PRIMARY KEY CHECK(id=1),
            turn INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS wars(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attacker TEXT NOT NULL,
            defender TEXT NOT NULL,
            attacker_score INTEGER NOT NULL,
            defender_score INTEGER NOT NULL,
            winner TEXT NOT NULL,
            turn INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.execute("INSERT OR IGNORE INTO game_state(id,turn) VALUES(1,1)")
        self.conn.commit()

    def execute(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def fetchone(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()

    def fetchall(self, sql, params=()):
        return self.conn.execute(sql, params).fetchall()
