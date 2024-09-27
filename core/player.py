# core/player.py

from core.inventory import Inventory

class Player:
    def __init__(self, name):
        self.id = None  # เพิ่ม attribute id
        self.name = name
        self.password = None  # เพิ่ม attribute password
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.hp = 100  # เพิ่มพลังชีวิต (HP)
        self.inventory = Inventory()  # เพิ่ม Inventory
        self.attack_power = 10  # พลังโจมตีเริ่มต้น
        self.defense = 5        # พลังป้องกันเริ่มต้น

    def gain_xp(self, amount):
        self.xp += amount
        print(f"{self.name} ได้รับ {amount} XP!")
        self.level_up()

    def level_up(self):
        xp_needed = self.level * 100
        if self.xp >= xp_needed:
            self.level += 1
            self.xp -= xp_needed
            self.hp = 100  # ฟื้นฟู HP เมื่อเลเวลอัป
            print(f"ยินดีด้วย! {self.name} เลเวลอัปเป็น Level {self.level}!")

    def collect_gold(self, amount):
        self.gold += amount
        print(f"{self.name} เก็บ {amount} gold. รวมทั้งหมด: {self.gold} gold.")

    def show_status(self):
        print(f"Player: {self.name} | Level: {self.level} | XP: {self.xp} | Gold: {self.gold} | HP: {self.hp}")
        print(f"Attack Power: {self.attack_power} | Defense: {self.defense}")
        self.inventory.show_inventory()
