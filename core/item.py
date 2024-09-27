# core/item.py

class Item:
    def __init__(self, name, description, effect=None, type_='consumable'):
        self.name = name
        self.description = description
        self.effect = effect
        self.type = type_

    def use(self, player):
        print(f"{player.name} ใช้ {self.name}!")
        if self.effect:
            self.effect(player)

def healing_potion(player):
    player.hp += 50
    print(f"{player.name} ฟื้นฟู HP ได้ 50! HP ปัจจุบัน: {player.hp}")

class Weapon(Item):
    def __init__(self, name, description, attack_bonus):
        super().__init__(name, description, None, type_='weapon')
        self.attack_bonus = attack_bonus

    def use(self, player):
        print(f"{player.name} ใช้ {self.name}! เพิ่มพลังโจมตี {self.attack_bonus}")
        player.attack_power += self.attack_bonus
        # ไม่ต้องลบไอเท็มจาก Inventory เพราะอาวุธมักจะติดตั้ง
        # สามารถเพิ่มระบบการติดตั้งอาวุธได้ในอนาคต

class Armor(Item):
    def __init__(self, name, description, defense_bonus):
        super().__init__(name, description, None, type_='armor')
        self.defense_bonus = defense_bonus

    def use(self, player):
        print(f"{player.name} ใช้ {self.name}! เพิ่มพลังป้องกัน {self.defense_bonus}")
        player.defense += self.defense_bonus
        # ไม่ต้องลบไอเท็มจาก Inventory เพราะเกราะมักจะติดตั้ง
        # สามารถเพิ่มระบบการติดตั้งเกราะได้ในอนาคต
