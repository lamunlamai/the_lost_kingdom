# core/game_logic.py
import time
from core.combat import initiate_pvp, initiate_pvm
from core.monster import Monster
from utils.helpers import get_random_monster
from core.player import Player
from core.item import healing_potion, Weapon, Armor, Item

def idle_progress(player):
    print(f"{player.name} กำลัง idle และเก็บทรัพยากร...")
    player.collect_gold(10)
    player.gain_xp(20)

def game_menu(player):
    while True:
        print("\nคุณต้องการทำอะไรต่อไป?")
        print("1. Idle")
        print("2. ตรวจสอบสถานะ")
        print("3. ต่อสู้กับผู้เล่นอื่น")
        print("4. ต่อสู้กับมอนสเตอร์")
        print("5. ใช้ไอเท็ม")
        print("6. อัปเกรดอาวุธ/เกราะ")
        print("7. ออกจากเกม")

        choice = input("เลือกตัวเลือก: ")

        if choice == '1':
            idle_progress(player)
        elif choice == '2':
            player.show_status()
        elif choice == '3':
            opponent_name = input("ใส่ชื่อของผู้เล่นที่ต้องการต่อสู้: ")
            opponent = Player(opponent_name)  # ในกรณีนี้สร้างผู้เล่นใหม่ชั่วคราว
            initiate_pvp(player, opponent)
        elif choice == '4':
            monster = get_random_monster()
            initiate_pvm(player, monster)
        elif choice == '5':
            use_item_menu(player)
        elif choice == '6':
            upgrade_menu(player)
        elif choice == '7':
            print("ลาก่อน!")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง!")

        time.sleep(1)  # เพิ่มการหน่วงเวลาเพื่อความสมจริง

def use_item_menu(player):
    while True:
        print("\nInventory ของคุณ:")
        player.inventory.show_inventory()
        print("เลือกไอเท็มที่ต้องการใช้ หรือพิมพ์ 'back' เพื่อกลับเมนูหลัก")
        choice = input("ใส่ชื่อไอเท็ม: ")

        if choice.lower() == 'back':
            break

        item_details = player.inventory.items.get(choice)
        if item_details:
            item = item_details['item']
            player.inventory.remove_item(choice, 1)
            item.use(player)
        else:
            print(f"ไม่พบไอเท็มชื่อ {choice} ใน Inventory")

def upgrade_menu(player):
    while True:
        print("\nอัปเกรดอาวุธหรือเกราะ:")
        print("1. อัปเกรดอาวุธ")
        print("2. อัปเกรดเกราะ")
        print("3. กลับเมนูหลัก")

        choice = input("เลือกตัวเลือก: ")

        if choice == '1':
            weapon_name = input("ใส่ชื่ออาวุธที่ต้องการอัปเกรด: ")
            player.inventory.upgrade_item(weapon_name, upgrade_type='attack')
        elif choice == '2':
            armor_name = input("ใส่ชื่อเกราะที่ต้องการอัปเกรด: ")
            player.inventory.upgrade_item(armor_name, upgrade_type='defense')
        elif choice == '3':
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง!")
