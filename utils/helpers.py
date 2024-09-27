# utils/helpers.py
from core.monster import Monster
from random import choice

def get_random_monster():
    monsters = [
        Monster("Goblin", 50, 10),
        Monster("Orc", 80, 15),
        Monster("Dragon", 200, 30)
    ]
    return choice(monsters)
