# main.py
from core.player import Player
from core.game_logic import game_menu
from database.db_manager import create_tables, save_player, load_player, hash_password
from core.item import healing_potion, Weapon, Armor, Item

def register():
    """ฟังก์ชันสำหรับการสมัครสมาชิก"""
    print("\n=== สมัครสมาชิก ===")
    name = input("ใส่ชื่อผู้เล่น: ")
    while True:
        password = input("ใส่รหัสผ่าน: ")
        confirm_password = input("ยืนยันรหัสผ่าน: ")
        if password == confirm_password:
            break
        else:
            print("รหัสผ่านไม่ตรงกัน กรุณาลองใหม่อีกครั้ง")
    hashed_pw = hash_password(password)
    player = Player(name)
    player.password = hashed_pw
    print(f"ยินดีต้อนรับ, {player.name}! เริ่มการผจญภัยใน The Lost Kingdom.")
    # เพิ่มไอเท็มเริ่มต้นให้กับผู้เล่นใหม่
    potion = Item("Healing Potion", "ฟื้นฟู HP ได้ 50", healing_potion)
    player.inventory.add_item(potion, 1)
    sword = Weapon("Iron Sword", "อาวุธพื้นฐานที่เพิ่มพลังโจมตี", 5)
    player.inventory.add_item(sword, 1)
    armor = Armor("Leather Armor", "เกราะพื้นฐานที่เพิ่มพลังป้องกัน", 3)
    player.inventory.add_item(armor, 1)
    save_player(player)

def login():
    """ฟังก์ชันสำหรับการเข้าสู่ระบบ"""
    print("\n=== เข้าสู่ระบบ ===")
    name = input("ใส่ชื่อผู้เล่น: ")
    password = input("ใส่รหัสผ่าน: ")
    hashed_pw = hash_password(password)
    player = load_player(name, hashed_pw)
    if player:
        print(f"ยินดีต้อนรับกลับ, {player.name}! กำลังโหลดการผจญภัยของคุณ.")
        return player
    else:
        print("ชื่อผู้เล่นหรือรหัสผ่านไม่ถูกต้อง")
        return None

def main():
    create_tables()
    
    while True:
        print("\n=== The Lost Kingdom ===")
        print("1. เข้าสู่ระบบ")
        print("2. สมัครสมาชิก")
        print("3. ออกจากเกม")
        choice = input("เลือกตัวเลือก: ")
        
        if choice == '1':
            player = login()
            if player:
                break
        elif choice == '2':
            register()
        elif choice == '3':
            print("ลาก่อน!")
            return
        else:
            print("ตัวเลือกไม่ถูกต้อง!")

    try:
        game_menu(player)
    finally:
        save_player(player)
        print("บันทึกความคืบหน้าของคุณแล้ว.")

if __name__ == "__main__":
    main()
