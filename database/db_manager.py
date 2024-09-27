# database/db_manager.py
import sqlite3
from core.player import Player

def connect_db(db_name="game.db"):
    conn = sqlite3.connect(db_name)
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            level INTEGER,
            xp INTEGER,
            gold INTEGER,
            hp INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_player(player):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO players (name, level, xp, gold, hp)
        VALUES (?, ?, ?, ?, ?)
    ''', (player.name, player.level, player.xp, player.gold, player.hp))
    conn.commit()
    conn.close()

def load_player(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, level, xp, gold, hp FROM players WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        player = Player(result[0])
        player.level = result[1]
        player.xp = result[2]
        player.gold = result[3]
        player.hp = result[4]
        return player
    else:
        return None
