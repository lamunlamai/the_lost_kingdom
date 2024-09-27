# core/combat.py
from random import randint
from core.monster import Monster

def player_vs_player(player1, player2):
    print(f"{player1.name} vs {player2.name} - การต่อสู้เริ่มต้น!")
    while player1.hp > 0 and player2.hp > 0:
        damage_to_p2 = randint(5, 20)
        player2.hp -= damage_to_p2
        print(f"{player1.name} ทำความเสียหาย {damage_to_p2} ถึง {player2.name}. {player2.name} มี HP เหลือ {player2.hp}")

        if player2.hp <= 0:
            print(f"{player1.name} ชนะการต่อสู้!")
            break

        damage_to_p1 = randint(5, 20)
        player1.hp -= damage_to_p1
        print(f"{player2.name} ทำความเสียหาย {damage_to_p1} ถึง {player1.name}. {player1.name} มี HP เหลือ {player1.hp}")

        if player1.hp <= 0:
            print(f"{player2.name} ชนะการต่อสู้!")
            break

def player_vs_monster(player, monster):
    print(f"{player.name} กำลังต่อสู้กับ {monster.name}!")
    while player.hp > 0 and monster.hp > 0:
        damage_to_monster = randint(10, 30)
        monster.hp -= damage_to_monster
        print(f"{player.name} ทำความเสียหาย {damage_to_monster} ถึง {monster.name}. {monster.name} มี HP เหลือ {monster.hp}")

        if monster.hp <= 0:
            print(f"{player.name} ชนะการต่อสู้กับ {monster.name}!")
            break

        damage_to_player = randint(5, 15)
        player.hp -= damage_to_player
        print(f"{monster.name} ทำความเสียหาย {damage_to_player} ถึง {player.name}. {player.name} มี HP เหลือ {player.hp}")

        if player.hp <= 0:
            print(f"{player.name} ถูกพ่ายแพ้โดย {monster.name}.")
            break

def initiate_pvp(player1, player2):
    player_vs_player(player1, player2)

def initiate_pvm(player, monster):
    player_vs_monster(player, monster)
