# main.py
from core.player import Player
from core.game_logic import game_menu
from database.db_manager import create_tables, save_player, load_player

def main():
    create_tables()
    
    player_name = input("ใส่ชื่อของผู้เล่น: ")
    player = load_player(player_name)
    
    if not player:
        player = Player(player_name)
        print(f"ยินดีต้อนรับ, {player.name}! เริ่มการผจญภัยใน The Lost Kingdom.")
    else:
        print(f"ยินดีต้อนรับกลับ, {player.name}! กำลังโหลดการผจญภัยของคุณ.")
    
    try:
        game_menu(player)
    finally:
        save_player(player)
        print("บันทึกความคืบหน้าของคุณแล้ว.")

if __name__ == "__main__":
    main()
