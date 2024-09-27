# server_twisted.py
from twisted.internet import reactor, protocol
from database.db_manager import create_tables, load_player, save_player, hash_password
from database.db_manager import accept_friend, add_friend, remove_friend, list_friends
from core.player import Player
from core.game_logic import initiate_pvp
from core.item import healing_potion, Weapon, Armor, Item
import signal
import logging
import sqlite3
HOST = '127.0.0.1'
PORT = 65432

def shutdown(signum, frame):
    print("Shutting down server...")
    reactor.stop()

signal.signal(signal.SIGINT, shutdown)

class GameProtocol(protocol.Protocol):
    def connectionMade(self):
        logging.debug(f"New connection from {self.transport.getPeer()}")
        # ตรวจสอบว่า factory ถูกกำหนดให้กับโปรโตคอลแล้ว
        if self.factory is None:
            print("Factory is not set for this protocol instance!")
            return

        print(f"Factory is: {self.factory}")
        self.player = None
        self.factory.clients.append(self)
        self.transport.write(b"Welcome to The Lost Kingdom!\n")
        print(f"New connection from {self.transport.getPeer()}")

    def connectionLost(self, reason):
        if self.player and self.player.name in self.factory.logged_in_players:
            del self.factory.logged_in_players[self.player.name]
            print(f"{self.player.name} has disconnected.")
        if self in self.factory.clients:
            self.factory.clients.remove(self)
        print(f"Connection lost from {self.transport.getPeer()}")

    def dataReceived(self, data):
        message = data.decode().strip()
        print(f"Received from {self.transport.getPeer()}: {message}")
        response = self.process_command(message)
        if response:
            self.transport.write(response.encode())

    def process_command(self, command):
        logging.debug(f"Processing command: {command}")
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
                self.player = player
                self.factory.logged_in_players[player.name] = self
                return f"Login successful. Welcome back, {player.name}!\n"
            else:
                return "Login failed. Check your username and password.\n"

        elif cmd == "register":
            if len(tokens) != 3:
                return "Usage: register <username> <password>\n"
            username = tokens[1]
            password = tokens[2]
            hashed_pw = hash_password(password)
            existing_player = load_player(username)
            if existing_player:
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
            if self.player:
                status = f"Player: {self.player.name} | Level: {self.player.level} | XP: {self.player.xp} | Gold: {self.player.gold} | HP: {self.player.hp}\n"
                status += f"Attack Power: {self.player.attack_power} | Defense: {self.player.defense}\n"
                inventory = "Inventory:\n"
                if not self.player.inventory.items:
                    inventory += " - ว่างเปล่า\n"
                else:
                    for item_name, details in self.player.inventory.items.items():
                        inventory += f" - {item_name} x{details['quantity']}\n"
                return status + inventory
            else:
                return "Please login first.\n"

        elif cmd == "idle":
            if self.player:
                self.player.collect_gold(10)
                self.player.gain_xp(20)
                save_player(self.player)
                return "You have idled and collected 10 gold and gained 20 XP.\n"
            else:
                return "Please login first.\n"

        elif cmd == "fight":
            if self.player:
                if len(tokens) != 2:
                    return "Usage: fight <username>\n"
                opponent_name = tokens[1]
                if opponent_name == self.player.name:
                    return "You cannot fight yourself.\n"
                opponent_protocol = self.factory.logged_in_players.get(opponent_name)
                if not opponent_protocol:
                    return "Opponent not found or not online.\n"
                opponent = opponent_protocol.player
                # เริ่มการต่อสู้
                fight_result = initiate_pvp(self.player, opponent)
                save_player(self.player)
                save_player(opponent)
                return fight_result + "\n"
            else:
                return "Please login first.\n"

        elif cmd == "use":
            if self.player:
                if len(tokens) < 2:
                    return "Usage: use <item_name>\n"
                item_name = ' '.join(tokens[1:])
                item = self.player.inventory.remove_item(item_name, 1)
                if item:
                    item.use(self.player)
                    save_player(self.player)
                    return f"You used {item_name}.\n"
                else:
                    return f"You don't have {item_name} in your inventory.\n"
            else:
                return "Please login first.\n"

        elif cmd == "logout":
            if self.player:
                del self.factory.logged_in_players[self.player.name]
                response = f"{self.player.name} has been logged out.\n"
                self.player = None
                return response
            else:
                return "You are not logged in.\n"

        elif cmd == "chat":
            if len(tokens) < 2:
                return "Usage: chat <message>\n"
            if self.player:
                message = ' '.join(tokens[1:])
                self.factory.broadcast(f"{self.player.name}: {message}\n", exclude=self)
                return ""
            else:
                return "Please login first.\n"

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
                " - chat <message>: Send a message to all players.\n"
                " - help: Show this help message.\n"
            )
            return help_text

        elif cmd == "addfriend":
            if not self.player:
                return "Please login first.\n"
            if len(tokens) != 2:
                return "Usage: addfriend <username>\n"
            friend_username = tokens[1]
            if friend_username == self.player.name:
                return "You cannot add yourself as a friend.\n"
            friend = load_player(friend_username)
            if not friend:
                return "User not found.\n"
            add_friend(self.player.name, friend_username)
            return f"Friend request sent to {friend_username}.\n"
        
        elif cmd == "acceptfriend":
            if not self.player:
                return "Please login first.\n"
            if len(tokens) != 2:
                return "Usage: acceptfriend <username>\n"
            friend_username = tokens[1]
            # ตรวจสอบว่ามีคำขอเป็นเพื่อนจาก friend_username หรือไม่
            conn = sqlite3.connect('game.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM friends WHERE user1 = ? AND user2 = ? AND status = 'pending'", (friend_username, self.player.name))
            row = cursor.fetchone()
            conn.close()
            if row:
                accept_friend(self.player.name, friend_username)
                return f"You are now friends with {friend_username}.\n"
            else:
                return "No pending friend request from that user.\n"
            
        elif cmd == "removefriend":
            if not self.player:
                return "Please login first.\n"
            if len(tokens) != 2:
                return "Usage: removefriend <username>\n"
            friend_username = tokens[1]
            remove_friend(self.player.name, friend_username)
            return f"Removed {friend_username} from your friends.\n"
        
        elif cmd == "listfriends":
            if not self.player:
                return "Please login first.\n"
            friends = list_friends(self.player.name)
            if not friends:
                return "You have no friends.\n"
            else:
                return "Your friends:\n" + "\n".join(friends) + "\n"
        
        elif cmd == "pm":
            if not self.player:
                return "Please login first.\n"
            if len(tokens) < 3:
                return "Usage: pm <username> <message>\n"
            recipient = tokens[1]
            message = ' '.join(tokens[2:])
            friends = list_friends(self.player.name)
            if recipient not in friends:
                return "You can only send messages to your friends.\n"
            recipient_protocol = self.factory.logged_in_players.get(recipient)
            if not recipient_protocol:
                return "Recipient is not online.\n"
            recipient_protocol.transport.write(f"{self.player.name} (private): {message}\n".encode())
            return "Message sent.\n"


        else:
            return "Unknown command. Type 'help' for a list of commands.\n"

class GameFactory(protocol.Factory):
    def __init__(self):
        self.clients = []
        self.logged_in_players = {}  # เก็บผู้เล่นที่ล็อกอินแล้ว
        create_tables()

    def buildProtocol(self, addr):
        proto = GameProtocol()
        proto.factory = self  # กำหนด factory ให้กับโปรโตคอล
        self.clients.append(proto)  # เพิ่มไคลเอนต์ใน factory.clients
        print(f"Added new client from {addr}")
        return proto

    def broadcast(self, message, exclude=None):
        for client in self.clients:
            if client != exclude and client.player:
                try:
                    client.transport.write(message.encode())
                except Exception as e:
                    print(f"Failed to send message to {client.transport.getPeer()}: {e}")

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
        result += f"{player2.name} deals {damage_to_p1} damage to {player1.name}. {player1.name} HP: {player1.hp}\n"
        
        if player1.hp <= 0:
            result += f"{player2.name} wins the battle!\n"
            player2.gain_xp(50)
            player1.gold += 10
            break
    return result


def main():
    factory = GameFactory()
    reactor.listenTCP(PORT, factory)
    print(f"Server started on {HOST}:{PORT}")
    reactor.run()

if __name__ == "__main__":
    main()
