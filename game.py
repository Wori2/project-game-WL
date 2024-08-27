import random

# Expanded Text Adventure Game with weapon-specific damage bonuses and combat details

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
        "enemy": "lion"
    },
    "shed": {
        "description": "You are in the shed. It's dark and there are tools everywhere.",
        "south": "garden",
        "item": "axe",
        "enemy": "panther"
    },
    "library": {
        "description": "You are in a library filled with dusty books. There is a strange sense of calm here.",
        "east": "hall",
        "north": "tower",
        "item": "ancient book",
        "enemy": "ghost"
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
        "enemy": "zombie"
    },
    "tower": {
        "description": "You are in a high tower. The view from the window stretches far into the horizon.",
        "south": "library",
        "item": "magic staff",
        "enemy": "dragon"
    }
}

# Enemy stats
enemy_stats = {
    "dragon": {"hp": 20, "ac": 18, "damage_range": (1, 15)},
    "zombie": {"hp": 8, "ac": 8, "damage_range": (1, 5)},
    "lion": {"hp": 12, "ac": 15, "damage_range": (1, 7)},
    "panther": {"hp": 10, "ac": 13, "damage_range": (1, 5)},
    "ghost": {"hp": 2, "ac": 5, "damage_range": (1, 2)}
}

# Initialize the game
inventory = []
current_room = "hall"
player_hp = 10  # Player starts with 10 hit points
base_player_ac = 11  # Player's base Armor Class
armor_bonus = 0
shield_bonus = 0
game_over = False

def calculate_player_ac():
    return base_player_ac + armor_bonus + shield_bonus

def print_description():
    print(rooms[current_room]["description"])
    if "enemy" in rooms[current_room]:
        enemy = rooms[current_room]["enemy"]
        enemy_hp = enemy_stats[enemy]["hp"]
        enemy_ac = enemy_stats[enemy]["ac"]
        print(f"There is a {enemy} here with {enemy_hp} HP and {enemy_ac} AC!")
    if rooms[current_room]["item"]:
        print(f"You see a {rooms[current_room]['item']} here.")
    print(f"Your current HP: {player_hp}")
    print(f"Your Armor Class (AC): {calculate_player_ac()}")

def move(direction):
    global current_room
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        print_description()
        check_for_enemy()
    else:
        print("You can't go that way.")

def take_item(item_name):
    global armor_bonus, shield_bonus
    item = rooms[current_room]["item"]
    if item and item.lower() == item_name.lower():
        inventory.append(item)
        rooms[current_room]["item"] = None
        print(f"You took the {item}.")
        if item == "armor":
            armor_bonus = 3  # Armor increases AC by 3
            print(f"Your Armor Class has increased by 3! Your new AC is {calculate_player_ac()}.")
        elif item == "shield":
            shield_bonus = 1  # Shield increases AC by 1
            print(f"Your Armor Class has increased by 1! Your new AC is {calculate_player_ac()}.")
    else:
        print(f"There is no {item_name} here to take.")

def show_inventory():
    if inventory:
        print("You have:", ", ".join(inventory))
    else:
        print("Your inventory is empty.")

def roll_attack(weapon_bonus=0):
    roll = random.randint(1, 20)
    print(f"You rolled an attack of {roll} (with a +{weapon_bonus} bonus).")
    return roll + weapon_bonus

def enemy_roll_attack():
    roll = random.randint(1, 20)
    print(f"The enemy rolled an attack of {roll}.")
    return roll

def roll_damage(damage_range, damage_bonus=0):
    damage = random.randint(*damage_range) + damage_bonus
    print(f"Damage roll: {damage} (including bonus of {damage_bonus})")
    return damage

def choose_weapon():
    print("Choose a weapon from your inventory:")
    weapons = [item for item in inventory if item in ["sword", "axe", "magic staff"]]
    if not weapons:
        print("You have no weapons to choose from!")
        return None
    for i, weapon in enumerate(weapons, 1):
        print(f"{i}. {weapon}")
    choice = input("Enter the number of the weapon you want to use: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(weapons):
            return weapons[choice - 1]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Please enter a number.")
        return None

def check_for_enemy():
    global game_over, player_hp
    if "enemy" in rooms[current_room]:
        enemy = rooms[current_room]["enemy"]
        enemy_hp = enemy_stats[enemy]["hp"]
        enemy_ac = enemy_stats[enemy]["ac"]
        enemy_damage_range = enemy_stats[enemy]["damage_range"]
        
        if any(weapon in inventory for weapon in ["sword", "axe", "magic staff"]):
            action = input(f"A {enemy} attacks! Do you want to fight or run? ").lower()
            if action == "fight":
                chosen_weapon = choose_weapon()
                if chosen_weapon:
                    weapon_bonus = {"sword": 1, "axe": 4, "magic staff": 2}.get(chosen_weapon, 0)
                    weapon_damage_bonus = {"sword": 2, "axe": 4, "magic staff": 3}.get(chosen_weapon, 0)
                    while player_hp > 0 and enemy_hp > 0:
                        # Player's attack roll
                        final_roll = roll_attack(weapon_bonus)
                        if final_roll >= enemy_ac:
                            damage = roll_damage((1, 5), weapon_damage_bonus)
                            enemy_hp -= damage
                            print(f"You hit the {enemy} for {damage} damage! It now has {enemy_hp} HP left.")
                            if enemy_hp <= 0:
                                print(f"You defeated the {enemy}!")
                                if random.random() < 0.5:
                                    inventory.remove(chosen_weapon)
                                    print(f"But your {chosen_weapon} broke!")
                                break
                        else:
                            print(f"You missed the {enemy}!")

                        # Enemy's attack roll
                        enemy_roll = enemy_roll_attack()
                        if enemy_roll >= calculate_player_ac():
                            damage = roll_damage(enemy_stats[enemy]["damage_range"])
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
                print(f"Invalid action. The {enemy} attacks!")
                player_hp -= roll_damage((1, 5))  # Damage on failed action
                if player_hp <= 0:
                    print("You have been defeated.")
                    game_over = True
        else:
            print(f"A {enemy} attacks! You have no weapon to defend yourself.")
            action = input("Do you want to run or fight? ").lower()
            if action == "run":
                print("You managed to escape!")
            elif action == "fight":
                print(f"You tried to fight the {enemy} without a weapon and were defeated.")
                game_over = True
            else:
                print(f"Invalid action. The {enemy} attacks!")
                player_hp -= roll_damage((1, 5))  # Damage on failed action
                if player_hp <= 0:
                    print("You have been defeated.")
                    game_over = True

def main():
    global game_over
    print("Welcome to the Text Adventure Game!")
    print_description()

    while not game_over:
        command = input("> ").lower().split()

        if len(command) == 0:
            continue

        if command[0] in ["w", "a", "s", "d"]:
            if command[0] == "w":
                move("north")
            elif command[0] == "s":
                move("south")
            elif command[0] == "d":
                move("east")
            elif command[0] == "a":
                move("west")
        elif command[0] == "take":
            if len(command) > 1:
                take_item(" ".join(command[1:]))
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
