# server.py
import socket
import threading
from database.db_manager import create_tables, load_player, save_player, hash_password
from core.player import Player
from core.game_logic import game_menu
from core.item import healing_potion, Weapon, Armor, Item

# กำหนดที่อยู่และพอร์ตสำหรับเซิร์ฟเวอร์
HOST = '127.0.0.1'  # localhost
PORT = 65432        # พอร์ตที่ไม่ใช้แล้ว

# เก็บผู้เล่นทั้งหมดที่เชื่อมต่ออยู่
connected_players = {}

def handle_client(conn, addr):
    print(f"เชื่อมต่อกับ {addr} แล้ว")
    conn.sendall(b"Welcome to The Lost Kingdom!\n")
    
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print(f"ได้รับคำสั่งจาก {addr}: {data}")
            response = process_command(conn, data)
            conn.sendall(response.encode())
        except ConnectionResetError:
            break
    
    # เมื่อผู้เล่นตัดการเชื่อมต่อ
    print(f"{addr} ออกจากเกม")
    conn.close()

def process_command(conn, command):
    tokens = command.split()
    if not tokens:
        return "Invalid command.\n"
    
    cmd = tokens[0].lower()
    
    if cmd == "login":
        if len(tokens) != 3:
            return "Usage: login <username> <password>\n"
        username = tokens[1]
        password = tokens[2]
        player = load_player(username, password)
        if player:
            connected_players[conn] = player
            return f"Login successful. Welcome back, {player.name}!\n"
        else:
            return "Login failed. Check your username and password.\n"
    
    elif cmd == "register":
        if len(tokens) != 3:
            return "Usage: register <username> <password>\n"
        username = tokens[1]
        password = tokens[2]
        hashed_pw = hash_password(password)
        player = load_player(username)
        if player:
            return "Username already exists. Please choose another one.\n"
        else:
            new_player = Player(username)
            new_player.password = hashed_pw
            # เพิ่มไอเท็มเริ่มต้น
            potion = Item("Healing Potion", "ฟื้นฟู HP ได้ 50", healing_potion)
            new_player.inventory.add_item(potion, 1)
            sword = Weapon("Iron Sword", "อาวุธพื้นฐานที่เพิ่มพลังโจมตี", 5)
            new_player.inventory.add_item(sword, 1)
            armor = Armor("Leather Armor", "เกราะพื้นฐานที่เพิ่มพลังป้องกัน", 3)
            new_player.inventory.add_item(armor, 1)
            save_player(new_player)
            return f"Registration successful. Welcome, {new_player.name}!\n"
    
    elif cmd == "status":
        player = connected_players.get(conn)
        if player:
            status = f"Player: {player.name} | Level: {player.level} | XP: {player.xp} | Gold: {player.gold} | HP: {player.hp}\n"
            status += f"Attack Power: {player.attack_power} | Defense: {player.defense}\n"
            inventory = "Inventory:\n"
            if not player.inventory.items:
                inventory += " - ว่างเปล่า\n"
            else:
                for item_name, details in player.inventory.items.items():
                    inventory += f" - {item_name} x{details['quantity']}\n"
            return status + inventory
        else:
            return "Please login first.\n"
    
    elif cmd == "idle":
        player = connected_players.get(conn)
        if player:
            # เรียกใช้ฟังก์ชัน idle_progress
            player.collect_gold(10)
            player.gain_xp(20)
            save_player(player)
            return "You have idled and collected 10 gold and gained 20 XP.\n"
        else:
            return "Please login first.\n"
    
    elif cmd == "fight":
        player = connected_players.get(conn)
        if player:
            if len(tokens) != 2:
                return "Usage: fight <username>\n"
            opponent_name = tokens[1]
            if opponent_name == player.name:
                return "You cannot fight yourself.\n"
            opponent = load_player(opponent_name)
            if not opponent:
                return "Opponent not found.\n"
            # เริ่มการต่อสู้
            fight_result = initiate_pvp(player, opponent)
            save_player(player)
            save_player(opponent)
            return fight_result + "\n"
        else:
            return "Please login first.\n"
    
    elif cmd == "use":
        player = connected_players.get(conn)
        if player:
            if len(tokens) < 2:
                return "Usage: use <item_name>\n"
            item_name = ' '.join(tokens[1:])
            item = player.inventory.remove_item(item_name, 1)
            if item:
                item.use(player)
                save_player(player)
                return f"You used {item_name}.\n"
            else:
                return f"You don't have {item_name} in your inventory.\n"
        else:
            return "Please login first.\n"
    
    elif cmd == "logout":
        player = connected_players.pop(conn, None)
        if player:
            return f"{player.name} has been logged out.\n"
        else:
            return "You are not logged in.\n"
    
    elif cmd == "help":
        help_text = (
            "Available commands:\n"
            " - register <username> <password>: Register a new account.\n"
            " - login <username> <password>: Login to your account.\n"
            " - status: Show your current status.\n"
            " - idle: Collect gold and gain XP.\n"
            " - fight <username>: Fight another player.\n"
            " - use <item_name>: Use an item from your inventory.\n"
            " - logout: Logout from your account.\n"
            " - help: Show this help message.\n"
        )
        return help_text
    
    else:
        return "Unknown command. Type 'help' for a list of commands.\n"

def initiate_pvp(player1, player2):
    """ฟังก์ชันสำหรับการต่อสู้ PvP ระหว่างผู้เล่นสองคน"""
    result = f"{player1.name} vs {player2.name} - Battle begins!\n"
    while player1.hp > 0 and player2.hp > 0:
        damage_to_p2 = player1.attack_power
        player2.hp -= damage_to_p2
        result += f"{player1.name} deals {damage_to_p2} damage to {player2.name}. {player2.name} HP: {player2.hp}\n"
        
        if player2.hp <= 0:
            result += f"{player1.name} wins the battle!\n"
            player1.gain_xp(50)
            player2.gold += 10
            break
        
        damage_to_p1 = player2.attack_power
        player1.hp -= damage_to_p1
        result += f"{player2.name} deals {damage_to_p1} damage to {player1.name}. {player1.hp}\n"
        
        if player1.hp <= 0:
            result += f"{player2.name} wins the battle!\n"
            player2.gain_xp(50)
            player1.gold += 10
            break
    return result

def start_server():
    create_tables()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server started on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"Active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
