# core/inventory.py
from core.item import Weapon, Armor
class Inventory:
    def __init__(self):
        self.items = {}  # เปลี่ยนจาก list เป็น dict เพื่อเก็บปริมาณ

    def add_item(self, item, quantity=1):
        if item.name in self.items:
            self.items[item.name]['quantity'] += quantity
        else:
            self.items[item.name] = {'item': item, 'quantity': quantity}
        print(f"เพิ่ม {item.name} จำนวน {quantity} เข้า Inventory แล้ว!")

    def remove_item(self, item_name, quantity=1):
        if item_name in self.items:
            if self.items[item_name]['quantity'] > quantity:
                self.items[item_name]['quantity'] -= quantity
                print(f"ลบ {item_name} จำนวน {quantity} ออกจาก Inventory แล้ว!")
                return self.items[item_name]['item']
            elif self.items[item_name]['quantity'] == quantity:
                removed_item = self.items.pop(item_name)['item']
                print(f"ลบ {item_name} ออกจาก Inventory แล้ว!")
                return removed_item
            else:
                print(f"จำนวน {item_name} ไม่เพียงพอใน Inventory")
                return None
        else:
            print(f"ไม่พบไอเท็มชื่อ {item_name} ใน Inventory")
            return None

    def show_inventory(self):
        if not self.items:
            print("Inventory ว่างเปล่า!")
        else:
            print("Inventory ของคุณ:")
            for idx, (item_name, details) in enumerate(self.items.items(), start=1):
                print(f"{idx}. {item_name} - {details['item'].description} x{details['quantity']}")

    def upgrade_item(self, item_name, upgrade_type='attack'):
        if item_name in self.items:
            item = self.items[item_name]['item']
            if isinstance(item, Weapon) and upgrade_type == 'attack':
                item.attack_bonus += 2  # ตัวอย่างการเพิ่ม
                print(f"{item.name} ถูกอัปเกรด! พลังโจมตีเพิ่มเป็น {item.attack_bonus}")
            elif isinstance(item, Armor) and upgrade_type == 'defense':
                item.defense_bonus += 2  # ตัวอย่างการเพิ่ม
                print(f"{item.name} ถูกอัปเกรด! พลังป้องกันเพิ่มเป็น {item.defense_bonus}")
            else:
                print(f"ไม่สามารถอัปเกรด {item.name} ได้ในประเภทนี้")
        else:
            print(f"ไม่พบไอเท็มชื่อ {item_name} ใน Inventory")    
