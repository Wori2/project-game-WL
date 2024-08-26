import random

# Expanded Text Adventure Game with Armor and Visible Enemy Rolls

# Room data
rooms = {
    "hall": {
        "description": "You are in a hall. There is a dining room to the east and a library to the west.",
        "east": "dining room",
        "west": "library",
        "item": None
    },
    "dining room": {
        "description": "You are in the dining room. There is a kitchen to the south and a bedroom to the north.",
        "south": "kitchen",
        "north": "bedroom",
        "west": "hall",
        "item": "key"
    },
    "kitchen": {
        "description": "You are in the kitchen. There is a garden to the west and a basement to the south.",
        "north": "dining room",
        "west": "garden",
        "south": "basement",
        "item": "sword"
    },
    "garden": {
        "description": "You are in the garden. There is a shed to the north.",
        "north": "shed",
        "east": "kitchen",
        "item": None,
        "enemy": "lion",
        "enemy_hp": 8
    },
    "shed": {
        "description": "You are in the shed. It's dark and there are tools everywhere.",
        "south": "garden",
        "item": "axe",
        "enemy": "panther",
        "enemy_hp": 6
    },
    "library": {
        "description": "You are in a library filled with dusty books. There is a strange sense of calm here.",
        "east": "hall",
        "north": "tower",  # Connect library to tower to the north
        "item": "ancient book",
        "enemy": "ghost",
        "enemy_hp": 5
    },
    "bedroom": {
        "description": "You are in a grand bedroom with a large bed and a balcony to the north.",
        "south": "dining room",
        "north": "balcony",
        "item": "armor"
    },
    "balcony": {
        "description": "You are on a balcony overlooking the vast garden below. A cool breeze is blowing.",
        "south": "bedroom",
        "item": None
    },
    "basement": {
        "description": "You are in a dark and cold basement. You can hear faint noises echoing around you.",
        "north": "kitchen",
        "item": "shield",
        "enemy": "zombie",
        "enemy_hp": 10
    },
    "tower": {
        "description": "You are in a high tower. The view from the window stretches far into the horizon.",
        "south": "library",  # Connect tower to library to the south
        "item": "magic staff",
        "enemy": "dragon",
        "enemy_hp": 20
    }
}

# Initialize the game
inventory = []
current_room = "hall"
player_hp = 10  # Player starts with 10 hit points
player_armor = False  # Player doesn't start with armor
game_over = False

def print_description():
    print(rooms[current_room]["description"])
    if "enemy" in rooms[current_room]:
        print(f"There is a {rooms[current_room]['enemy']} here with {rooms[current_room]['enemy_hp']} HP!")
    if rooms[current_room]["item"]:
        print(f"You see a {rooms[current_room]['item']} here.")
    print(f"Your current HP: {player_hp}")

def move(direction):
    global current_room
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        print_description()
        check_for_enemy()
    else:
        print("You can't go that way.")

def take_item(item_name):
    item = rooms[current_room]["item"]
    if item and item.lower() == item_name.lower():
        if item.lower() == "armor":
            global player_armor
            player_armor = True
            print("You put on the armor. You are now harder to hit.")
        inventory.append(item)
        rooms[current_room]["item"] = None
        print(f"You took the {item}.")
    else:
        print(f"There is no {item_name} here to take.")

def show_inventory():
    if inventory:
        print("You have:", ", ".join(inventory))
    else:
        print("Your inventory is empty.")

def weapon_breaks():
    return random.random() < 0.5  # 50% chance

def roll_attack(weapon_bonus=0):
    roll = random.randint(1, 20)
    print(f"You rolled a {roll} (with a +{weapon_bonus} bonus).")
    return roll + weapon_bonus

def enemy_roll_attack():
    roll = random.randint(1, 20)
    print(f"The enemy rolled a {roll}.")
    return roll

def check_for_enemy():
    global game_over, player_hp
    if "enemy" in rooms[current_room]:
        enemy = rooms[current_room]["enemy"]
        enemy_hp = rooms[current_room]["enemy_hp"]
        
        if "sword" in inventory or "axe" in inventory:
            weapon_bonus = 1 if "sword" in inventory else 4
            action = input(f"A {enemy} attacks! Do you want to fight or run? ").lower()
            if action == "fight":
                while player_hp > 0 and enemy_hp > 0:
                    # Player's attack roll
                    final_roll = roll_attack(weapon_bonus)
                    if final_roll >= 11:
                        damage = random.randint(1, 5)
                        enemy_hp -= damage
                        print(f"You hit the {enemy} for {damage} damage! It now has {enemy_hp} HP left.")
                        if enemy_hp <= 0:
                            print(f"You defeated the {enemy}!")
                            if weapon_breaks():
                                used_weapon = "sword" if "sword" in inventory else "axe"
                                inventory.remove(used_weapon)
                                print(f"But your {used_weapon} broke!")
                            del rooms[current_room]["enemy"]  # Remove the enemy from the game
                            del rooms[current_room]["enemy_hp"]
                            break
                    else:
                        print(f"You missed the {enemy}!")

                    # Enemy's attack roll
                    enemy_roll = enemy_roll_attack()
                    hit_threshold = 11 - (2 if player_armor else 0)  # Armor reduces enemy hit threshold
                    if enemy_roll >= hit_threshold:
                        damage = random.randint(1, 5)
                        player_hp -= damage
                        print(f"The {enemy} hit you for {damage} damage! You now have {player_hp} HP.")
                        if player_hp <= 0:
                            print("You have been defeated.")
                            game_over = True
                            break
                    else:
                        print(f"The {enemy} missed you!")
            elif action == "run":
                print("You managed to escape!")
            else:
                print(f"Invalid action. The {enemy} attacks you!")
                player_hp -= random.randint(1, 5)  # Damage on failed action
                if player_hp <= 0:
                    print("You have been defeated.")
                    game_over = True
        else:
            print(f"A {enemy} attacks! You have no weapon to defend yourself.")
            action = input("Do you want to run or fight? ").lower()
            if action == "run":
                print("You managed to escape!")
            elif action == "fight":
                weapon_bonus = -2  # Penalty for fighting without a weapon
                while player_hp > 0 and enemy_hp > 0:
                    # Player attacks without a weapon (with -2 modifier)
                    final_roll = roll_attack(weapon_bonus)
                    if final_roll >= 11:
                        damage = random.randint(1, 3)
                        enemy_hp -= damage
                        print(f"You hit the {enemy} for {damage} damage! It now has {enemy_hp} HP left.")
                        if enemy_hp <= 0:
                            print(f"You defeated the {enemy}!")
                            del rooms[current_room]["enemy"]
                            del rooms[current_room]["enemy_hp"]
                            break
                    else:
                        print(f"You missed the {enemy}!")

                    # Enemy's attack
                    enemy_roll = enemy_roll_attack()
                    hit_threshold = 11 - (2 if player_armor else 0)  # Armor reduces enemy hit threshold
                    if enemy_roll >= hit_threshold:
                        damage = random.randint(1, 5)
                        player_hp -= damage
                        print(f"The {enemy} hit you for {damage} damage! You now have {player_hp} HP.")
                        if player_hp <= 0:
                            print("You have been defeated.")
                            game_over = True
                            break
                    else:
                        print(f"The {enemy} missed you!")
            else:
                print(f"Invalid action. The {enemy} attacks you!")
                player_hp -= random.randint(1, 5)  # Damage on failed action
                if player_hp <= 0:
                    print("You have been defeated.")
                    game_over = True

def main():
    global game_over
    print("Welcome to the Expanded Text Adventure Game!")
    print_description()

    while not game_over:
        command = input("> ").lower().split()

        if len(command) == 0:
            continue

        if command[0] == "w":
            move("north")
        elif command[0] == "a":
            move("west")
        elif command[0] == "s":
            move("south")
        elif command[0] == "d":
            move("east")
        elif command[0] == "take":
            if len(command) > 1:
                item_name = " ".join(command[1:])
                take_item(item_name)
            else:
                print("Take what?")
        elif command[0] == "inventory":
            show_inventory()
        elif command[0] == "quit":
            print("Thanks for playing!")
            break
        else:
            print("Invalid command.")

    if game_over:
        print("Game Over. You died.")

if __name__ == "__main__":
    main()
