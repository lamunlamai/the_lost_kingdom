# core/monster.py
from random import randint

class Monster:
    def __init__(self, name, hp, attack_power):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power

    def attack(self, player):
        damage = randint(5, self.attack_power)
        player.hp -= damage
        print(f"{self.name} โจมตี {player.name} ทำให้ได้รับความเสียหาย {damage} HP!")
