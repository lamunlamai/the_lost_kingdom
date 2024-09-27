# main.py
from core.player import Player
from core.game_logic import game_menu
from database.db_manager import create_tables, save_player, load_player
from core.item import healing_potion, Weapon, Armor, Item

def main():
    create_tables()
    
    player_name = input("ใส่ชื่อของผู้เล่น: ")
    player = load_player(player_name)
    
    if not player:
        player = Player(player_name)
        print(f"ยินดีต้อนรับ, {player.name}! เริ่มการผจญภัยใน The Lost Kingdom.")
        # เพิ่มไอเท็มเริ่มต้นให้กับผู้เล่นใหม่
        potion = Item("Healing Potion", "ฟื้นฟู HP ได้ 50", healing_potion)
        player.inventory.add_item(potion, 1)
        sword = Weapon("Iron Sword", "อาวุธพื้นฐานที่เพิ่มพลังโจมตี", 5)
        player.inventory.add_item(sword, 1)
        armor = Armor("Leather Armor", "เกราะพื้นฐานที่เพิ่มพลังป้องกัน", 3)
        player.inventory.add_item(armor, 1)
    else:
        print(f"ยินดีต้อนรับกลับ, {player.name}! กำลังโหลดการผจญภัยของคุณ.")
    
    try:
        game_menu(player)
    finally:
        save_player(player)
        print("บันทึกความคืบหน้าของคุณแล้ว.")

if __name__ == "__main__":
    main()
