# core/item.py

class Item:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

    def use(self, player):
        print(f"{player.name} ใช้ {self.name}!")
        self.effect(player)

def healing_potion(player):
    player.hp += 50
    print(f"{player.name} ฟื้นฟู HP ได้ 50!")

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, None)
        self.attack_bonus = attack_bonus
