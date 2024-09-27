# database/db_manager.py
import sqlite3
from core.player import Player
from core.item import Item, Weapon, Armor
import json
import hashlib  # สำหรับการแฮชรหัสผ่าน

def connect_db(db_name="game.db"):
    """เชื่อมต่อกับฐานข้อมูล SQLite"""
    conn = sqlite3.connect(db_name)
    return conn

def create_tables():
    """สร้างตารางผู้เล่น ไอเท็ม และ Inventory ถ้ายังไม่มี"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # สร้างตาราง players
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            password TEXT,  -- เพิ่มฟิลด์ password
            level INTEGER,
            xp INTEGER,
            gold INTEGER,
            hp INTEGER,
            attack_power INTEGER,
            defense INTEGER
        )
    ''')
    
    # สร้างตาราง friends
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        user1 TEXT,
        user2 TEXT,
        status TEXT,  -- 'pending', 'accepted', 'blocked'
        PRIMARY KEY (user1, user2),
        FOREIGN KEY (user1) REFERENCES players(name),
        FOREIGN KEY (user2) REFERENCES players(name)
    )
    """)
    
    # สร้างตาราง items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            type TEXT,  -- 'weapon', 'armor', 'consumable', etc.
            effect TEXT  -- JSON หรือรูปแบบอื่นๆ เพื่อเก็บรายละเอียดของผลกระทบ
        )
    ''')
    
    # สร้างตาราง inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            player_id INTEGER,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            PRIMARY KEY (player_id, item_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """แฮชรหัสผ่านด้วย SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_player(player):
    """บันทึกข้อมูลผู้เล่นลงฐานข้อมูล รวมถึง Inventory"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # บันทึกข้อมูลผู้เล่น
    if player.id:
        # ผู้เล่นมีอยู่แล้วในฐานข้อมูล, ทำการอัปเดตข้อมูล
        cursor.execute('''
            UPDATE players
            SET name = ?, password = ?, level = ?, xp = ?, gold = ?, hp = ?, attack_power = ?, defense = ?
            WHERE id = ?
        ''', (player.name, player.password, player.level, player.xp, player.gold, player.hp, player.attack_power, player.defense, player.id))
    else:
        # ผู้เล่นใหม่, ทำการแทรกข้อมูล
        cursor.execute('''
            INSERT INTO players (name, password, level, xp, gold, hp, attack_power, defense)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player.name, player.password, player.level, player.xp, player.gold, player.hp, player.attack_power, player.defense))
        player.id = cursor.lastrowid
    
    # บันทึกข้อมูล Inventory
    # ลบข้อมูล Inventory เดิมก่อนเพื่อป้องกันการซ้ำซ้อน
    cursor.execute('DELETE FROM inventory WHERE player_id = ?', (player.id,))
    
    for item_name, details in player.inventory.items.items():
        item = details['item']
        quantity = details['quantity']
        
        # ตรวจสอบว่าไอเท็มนั้นมีอยู่ในตาราง items หรือยัง
        cursor.execute('SELECT id FROM items WHERE name = ?', (item.name,))
        item_row = cursor.fetchone()
        if item_row:
            item_id = item_row[0]
        else:
            # เพิ่มไอเท็มใหม่ลงในตาราง items
            effect_json = json.dumps(item.effect.__name__) if item.effect else None
            cursor.execute('INSERT INTO items (name, description, type, effect) VALUES (?, ?, ?, ?)',
                           (item.name, item.description, item.type, effect_json))
            item_id = cursor.lastrowid
        
        # เพิ่มไอเท็มลงในตาราง inventory
        cursor.execute('INSERT INTO inventory (player_id, item_id, quantity) VALUES (?, ?, ?)',
                       (player.id, item_id, quantity))
    
    conn.commit()
    conn.close()

def load_player(name, password=None):
    """โหลดข้อมูลผู้เล่นและ Inventory จากฐานข้อมูล"""
    conn = connect_db()
    cursor = conn.cursor()
    
    if password:
        hashed_password = hash_password(password)
        cursor.execute('SELECT id, name, level, xp, gold, hp, attack_power, defense FROM players WHERE name = ? AND password = ?', (name, hashed_password))
    else:
        cursor.execute('SELECT id, name, level, xp, gold, hp, attack_power, defense FROM players WHERE name = ?', (name,))
    
    result = cursor.fetchone()
    
    if result:
        player = Player(result[1])
        player.id = result[0]  # เพิ่ม attribute id ให้กับ Player
        player.level = result[2]
        player.xp = result[3]
        player.gold = result[4]
        player.hp = result[5]
        player.attack_power = result[6]
        player.defense = result[7]
        player.password = result[1]  # Placeholder, actual password handling in main.py
        
        # โหลด Inventory
        cursor.execute('SELECT item_id, quantity FROM inventory WHERE player_id = ?', (player.id,))
        inventory_items = cursor.fetchall()
        
        for item_id, quantity in inventory_items:
            cursor.execute('SELECT name, description, type, effect FROM items WHERE id = ?', (item_id,))
            item_data = cursor.fetchone()
            if item_data:
                name, description, type_, effect = item_data
                # แปลง effect จาก JSON เป็นฟังก์ชันจริง
                effect_func = globals().get(effect) if effect else None
                
                if type_ == 'consumable':
                    item = Item(name, description, effect_func)
                elif type_ == 'weapon':
                    attack_bonus = int(effect) if effect else 0
                    item = Weapon(name, description, attack_bonus)
                elif type_ == 'armor':
                    defense_bonus = int(effect) if effect else 0
                    item = Armor(name, description, defense_bonus)
                else:
                    item = Item(name, description, None)
                
                player.inventory.add_item(item, quantity)
        
        conn.close()
        return player
    else:
        conn.close()
        return None

def add_friend(user1, user2):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO friends (user1, user2, status) VALUES (?, ?, 'pending')", (user1, user2))
    conn.commit()
    conn.close()

def accept_friend(user1, user2):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE friends SET status = 'accepted' WHERE user1 = ? AND user2 = ?", (user2, user1))
    cursor.execute("INSERT OR IGNORE INTO friends (user1, user2, status) VALUES (?, ?, 'accepted')", (user1, user2))
    conn.commit()
    conn.close()

def remove_friend(user1, user2):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM friends WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)", (user1, user2, user2, user1))
    conn.commit()
    conn.close()

def list_friends(user):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user2 FROM friends WHERE user1 = ? AND status = 'accepted'
    UNION
    SELECT user1 FROM friends WHERE user2 = ? AND status = 'accepted'
    """, (user, user))
    friends = cursor.fetchall()
    conn.close()
    return [f[0] for f in friends]