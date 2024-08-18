import random

# Simple Text Adventure Game with Two Enemies and Combat Rolls

# Room data
rooms = {
    "hall": {
        "description": "You are in a hall. There is a dining room to the east.",
        "east": "dining room",
        "item": None
    },
    "dining room": {
        "description": "You are in the dining room. There is a kitchen to the south.",
        "south": "kitchen",
        "west": "hall",
        "item": "key"
    },
    "kitchen": {
        "description": "You are in the kitchen. There is a garden to the west.",
        "north": "dining room",
        "west": "garden",
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
    }
}

# Initialize the game
inventory = []
current_room = "hall"
game_over = False

def print_description():
    print(rooms[current_room]["description"])
    if "enemy" in rooms[current_room]:
        print(f"There is a {rooms[current_room]['enemy']} here!")
    if rooms[current_room]["item"]:
        print(f"You see a {rooms[current_room]['item']} here.")

def move(direction):
    global current_room
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        print_description()
        check_for_enemy()
    else:
        print("You can't go that way.")

def take_item():
    item = rooms[current_room]["item"]
    if item:
        inventory.append(item)
        rooms[current_room]["item"] = None
        print(f"You took the {item}.")
    else:
        print("There's nothing to take here.")

def show_inventory():
    if inventory:
        print("You have:", ", ".join(inventory))
    else:
        print("Your inventory is empty.")

def weapon_breaks():
    return random.random() < 0.5  # 50% chance

def roll_attack(weapon_bonus):
    roll = random.randint(1, 20)
    print(f"You rolled a {roll} (with a +{weapon_bonus} bonus).")
    return roll + weapon_bonus

def check_for_enemy():
    global game_over
    if "enemy" in rooms[current_room]:
        enemy = rooms[current_room]["enemy"]
        if "sword" in inventory or "axe" in inventory:
            weapon_bonus = 1 if "sword" in inventory else 4
            action = input(f"A {enemy} attacks! Do you want to fight or run? ").lower()
            if action == "fight":
                final_roll = roll_attack(weapon_bonus)
                if final_roll >= 11:
                    print(f"You fought the {enemy} and won!")
                    if weapon_breaks():
                        used_weapon = "sword" if "sword" in inventory else "axe"
                        inventory.remove(used_weapon)
                        print(f"But your {used_weapon} broke!")
                    del rooms[current_room]["enemy"]  # Remove the enemy from the game
                else:
                    print(f"You fought the {enemy} and lost!")
                    game_over = True
            elif action == "run":
                print("You managed to escape!")
            else:
                print(f"Invalid action. The {enemy} attacks you!")
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
                print(f"Invalid action. The {enemy} attacks you!")
                game_over = True

def main():
    global game_over
    print("Welcome to the Text Adventure Game!")
    print_description()

    while not game_over:
        command = input("> ").lower().split()

        if len(command) == 0:
            continue

        if command[0] in ["go", "move"]:
            if len(command) > 1:
                move(command[1])
            else:
                print("Go where?")
        elif command[0] == "take":
            take_item()
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
