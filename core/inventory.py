# core/inventory.py

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        print(f"เพิ่ม {item.name} เข้า Inventory แล้ว!")

    def remove_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                print(f"ลบ {item.name} ออกจาก Inventory แล้ว!")
                return item
        print(f"ไม่พบไอเท็มชื่อ {item_name} ใน Inventory")
        return None

    def show_inventory(self):
        if not self.items:
            print("Inventory ว่างเปล่า!")
        else:
            print("Inventory ของคุณ:")
            for idx, item in enumerate(self.items, start=1):
                print(f"{idx}. {item.name} - {item.description}")
