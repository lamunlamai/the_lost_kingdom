# core/game_logic.py
import time
from core.combat import initiate_pvp, initiate_pvm
from core.monster import Monster
from utils.helpers import get_random_monster
from core.player import Player

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
        print("5. ออกจากเกม")

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
            print("ลาก่อน!")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง!")

        time.sleep(1)  # เพิ่มการหน่วงเวลาเพื่อความสมจริง
