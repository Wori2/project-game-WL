import pygame
import sys
import random
import os

# Inicializácia Pygame
pygame.init()
pygame.font.init()

# Rozmery okna
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Text Adventure Refactored")

# Paleta farieb
COLOR_BG = (24, 28, 36)
COLOR_PANEL = (38, 45, 58)
COLOR_ACCENT = (212, 175, 55)
COLOR_TEXT = (235, 240, 245)
COLOR_HP = (46, 204, 113)
COLOR_ENEMY_HP = (231, 76, 60)
COLOR_BUTTON = (52, 73, 94)
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_LOG = (15, 20, 28)

# --- NAČÍTANIE OBRÁZKOV ---
# Zistenie presnej zložky, v ktorej sa nachádza tento kód
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRAK_PATH = os.path.join(SCRIPT_DIR, "drak.png")

# Načítanie obrázka draka
try:
    drak_img = pygame.image.load(DRAK_PATH).convert_alpha()
    drak_img = pygame.transform.scale(drak_img, (120, 120))
    print("-> Obrázok draka sa ÚSPEŠNE načítal!")
except Exception as e:
    print(f"-> UPOZORNENIE: Obrázok sa nenašiel na ceste: {DRAK_PATH}")
    print(f"-> Detail chyby: {e}")
    drak_img = None

# Písma
FONT_TITLE = pygame.font.SysFont("Verdana", 20, bold=True)
FONT_BODY = pygame.font.SysFont("Verdana", 14)
FONT_SMALL = pygame.font.SysFont("Verdana", 12)

# --- MIESTNOSTI ---
rooms = {
    "hall": {
        "title": "Vstupná hala",
        "description": "Nachádzaš sa vo veľkej vstupnej hale. Na východ je jedáleň, na západ knižnica.",
        "east": "dining room",
        "west": "library",
        "item": None,
        "bg_color": (50, 40, 60)
    },
    "dining room": {
        "title": "Jedáleň",
        "description": "Si v priestornej jedálni. Na juhu je kuchyňa, na severe spálňa a na západ je hala.",
        "south": "kitchen",
        "north": "bedroom",
        "west": "hall",
        "item": "key",
        "bg_color": (60, 45, 40)
    },
    "kitchen": {
        "title": "Kuchyňa",
        "description": "Stará kuchyňa. Na západ je záhrada a na juhu vstup do pivnice.",
        "north": "dining room",
        "west": "garden",
        "south": "basement",
        "item": "sword",
        "bg_color": (70, 50, 40)
    },
    "garden": {
        "title": "Záhrada",
        "description": "Si v zarastenej záhrade. Na severe stojí stará kôlňa.",
        "north": "shed",
        "east": "kitchen",
        "item": None,
        "enemy": "lion",
        "bg_color": (30, 60, 40)
    },
    "shed": {
        "title": "Kôlňa",
        "description": "Tmavá kôlňa plná hrdzavého náradia.",
        "south": "garden",
        "item": "axe",
        "enemy": "panther",
        "bg_color": (40, 40, 30)
    },
    "library": {
        "title": "Knižnica",
        "description": "Tiché miesto plné zaprášených kníh. Na severe sa tíši vysoká veža.",
        "east": "hall",
        "north": "tower",
        "item": "ancient book",
        "enemy": "ghost",
        "bg_color": (35, 45, 65)
    },
    "bedroom": {
        "title": "Panská spálňa",
        "description": "Veľká spálňa s dominantnou posteľou. Na severe je balkón.",
        "south": "dining room",
        "north": "balcony",
        "item": "armor",
        "bg_color": (60, 35, 50)
    },
    "balcony": {
        "title": "Balkón",
        "description": "Balkón s výhľadom na celú záhradu. Fúka tu príjemný chladný vánok.",
        "south": "bedroom",
        "item": None,
        "bg_color": (40, 55, 70)
    },
    "basement": {
        "title": "Temná pivnica",
        "description": "Chladná a temná pivnica. Počuť tu čudné zvuky.",
        "north": "kitchen",
        "item": "shield",
        "enemy": "zombie",
        "bg_color": (25, 25, 30)
    },
    "tower": {
        "title": "Vysoká veža",
        "description": "Vrchol veže s výhľadom na šíre okolie.",
        "south": "library",
        "item": "magic staff",
        "enemy": "dragon",
        "bg_color": (45, 30, 55)
    }
}

# --- NEPRIATELIA ---
enemy_stats = {
    "dragon": {"name": "Drak", "hp": 20, "max_hp": 20, "ac": 18, "damage_range": (1, 15), "color": (220, 50, 50)},
    "zombie": {"name": "Zombie", "hp": 8, "max_hp": 8, "ac": 8, "damage_range": (1, 5), "color": (100, 140, 80)},
    "lion": {"name": "Lev", "hp": 12, "max_hp": 12, "ac": 15, "damage_range": (1, 7), "color": (210, 150, 50)},
    "panther": {"name": "Panter", "hp": 10, "max_hp": 10, "ac": 13, "damage_range": (1, 5), "color": (70, 70, 90)},
    "ghost": {"name": "Duch", "hp": 2, "max_hp": 2, "ac": 5, "damage_range": (1, 2), "color": (180, 220, 240)}
}

# Stav Hráča
inventory = []
current_room = "hall"
player_hp = 10
player_max_hp = 10
base_player_ac = 11
armor_bonus = 0
shield_bonus = 0

# Bojový stav
combat_active = False
current_enemy = None
current_enemy_hp = 0
combat_logs = []

def get_player_ac():
    return base_player_ac + armor_bonus + shield_bonus

def add_log(msg):
    combat_logs.append(msg)
    if len(combat_logs) > 6:
        combat_logs.pop(0)

# Trieda pre UI Tlačidlá
class Button:
    def __init__(self, x, y, w, h, text, callback, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.enabled = enabled

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = COLOR_BUTTON_HOVER if (self.rect.collidepoint(mouse_pos) and self.enabled) else COLOR_BUTTON
        if not self.enabled:
            color = (60, 60, 65)

        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT if self.enabled else (90, 90, 90), self.rect, 2, border_radius=6)

        text_surf = FONT_BODY.render(self.text, True, COLOR_TEXT if self.enabled else (120, 120, 120))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                self.callback()

# Herná logika
def move(direction):
    global current_room, combat_active, current_enemy, current_enemy_hp
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        if "enemy" in rooms[current_room]:
            enemy_type = rooms[current_room]["enemy"]
            current_enemy = enemy_type
            current_enemy_hp = enemy_stats[enemy_type]["hp"]
            combat_active = True
            add_log(f"Útočí na teba {enemy_stats[enemy_type]['name']}!")

def take_item():
    global armor_bonus, shield_bonus
    item = rooms[current_room].get("item")
    if item:
        inventory.append(item)
        rooms[current_room]["item"] = None
        add_log(f"Zozbieral si: {item}")
        if item == "armor":
            armor_bonus = 3
            add_log("Tvoje Brnenie zvýšilo AC o +3!")
        elif item == "shield":
            shield_bonus = 1
            add_log("Tvoj Štít zvýšil AC o +1!")

def execute_attack(weapon):
    global current_enemy_hp, player_hp, combat_active
    if not combat_active or not current_enemy:
        return

    e_data = enemy_stats[current_enemy]
    e_name = e_data["name"]

    weapon_bonus = {"sword": 1, "axe": 4, "magic staff": 2}.get(weapon, 0)
    weapon_damage_bonus = {"sword": 2, "axe": 4, "magic staff": 3}.get(weapon, 0)

    # 1. Ťah hráča
    roll = random.randint(1, 20)
    total_attack = roll + weapon_bonus
    add_log(f"Útok zbraňou ({weapon}): hod {roll} + {weapon_bonus} = {total_attack} vs AC {e_data['ac']}")

    if total_attack >= e_data["ac"]:
        damage = random.randint(1, 5) + weapon_damage_bonus
        current_enemy_hp -= damage
        add_log(f"Zásah! Spôsobil si {damage} poškodenia.")
        
        if current_enemy_hp <= 0:
            add_log(f"Porazil si {e_name}!")
            del rooms[current_room]["enemy"]
            combat_active = False
            
            # Šanca na zničenie zbrane
            if random.random() < 0.5:
                inventory.remove(weapon)
                add_log(f"Tvoja zbraň ({weapon}) sa pri úderu zničila!")
            return
    else:
        add_log("Auu! Netrafil si!")

    # 2. Ťah nepriateľa
    enemy_roll = random.randint(1, 20)
    p_ac = get_player_ac()
    add_log(f"{e_name} útočí: hod {enemy_roll} vs Tvoje AC {p_ac}")

    if enemy_roll >= p_ac:
        e_dmg = random.randint(*e_data["damage_range"])
        player_hp -= e_dmg
        add_log(f"{e_name} ťa zasiahol za {e_dmg} HP!")
        if player_hp <= 0:
            add_log("Bol si porazený... Koniec hry!")
    else:
        add_log(f"{e_name} minul!")

def run_away():
    global combat_active
    if combat_active:
        add_log("Podarilo sa ti úspešne utiecť!")
        combat_active = False

# Hlavná slučka
def main():
    global player_hp
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill(COLOR_BG)

        # --- PANEL HLAVIČKY (STATISTIKY) ---
        panel_rect = pygame.Rect(20, 20, 860, 70)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_ACCENT, panel_rect, 2, border_radius=8)

        title_surf = FONT_TITLE.render(rooms[current_room]["title"], True, COLOR_ACCENT)
        screen.blit(title_surf, (40, 32))

        # Životy (HP Bar)
        hp_text = FONT_BODY.render(f"HP: {max(0, player_hp)} / {player_max_hp}", True, COLOR_TEXT)
        screen.blit(hp_text, (550, 32))
        
        pygame.draw.rect(screen, (80, 80, 80), (660, 35, 120, 16), border_radius=4)
        hp_ratio = max(0, player_hp) / player_max_hp
        pygame.draw.rect(screen, COLOR_HP, (660, 35, int(120 * hp_ratio), 16), border_radius=4)

        # Ochrana (AC)
        ac_text = FONT_BODY.render(f"Ochrana (AC): {get_player_ac()}", True, COLOR_TEXT)
        screen.blit(ac_text, (400, 32))

        # --- HLAVNÉ OKNO / MIESTNOSŤ ---
        view_rect = pygame.Rect(20, 105, 500, 300)
        room_bg = rooms[current_room].get("bg_color", (40, 40, 50))
        pygame.draw.rect(screen, room_bg, view_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL, view_rect, 3, border_radius=8)

        # Predmet na zemi
        room_item = rooms[current_room].get("item")
        if room_item:
            pygame.draw.circle(screen, COLOR_ACCENT, (100, 250), 20)
            item_txt = FONT_SMALL.render(f"Predmet: {room_item}", True, COLOR_TEXT)
            screen.blit(item_txt, (70, 280))

        # Vykreslenie nepriateľa
        if combat_active and current_enemy:
            e_info = enemy_stats[current_enemy]
            
            # Ak je to drak A obrázok sa podarilo načítať
            if current_enemy == "dragon" and drak_img:
                screen.blit(drak_img, (320, 180))
            else:
                # Ostatní nepriatelia (alebo drak bez načítaného obrázka)
                pygame.draw.rect(screen, e_info["color"], (320, 180, 120, 120), border_radius=8)
            
            e_title = FONT_TITLE.render(e_info["name"], True, COLOR_TEXT)
            screen.blit(e_title, (330, 140))
            
            # HP nepriateľa
            e_hp_ratio = max(0, current_enemy_hp) / e_info["max_hp"]
            pygame.draw.rect(screen, (80, 80, 80), (320, 310, 120, 12), border_radius=3)
            pygame.draw.rect(screen, COLOR_ENEMY_HP, (320, 310, int(120 * e_hp_ratio), 12), border_radius=3)

        # Popis miestnosti
        desc_rect = pygame.Rect(20, 420, 500, 90)
        pygame.draw.rect(screen, COLOR_PANEL, desc_rect, border_radius=8)
        
        words = rooms[current_room]["description"].split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if FONT_BODY.size(test_line)[0] < 470:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        for i, line in enumerate(lines):
            line_surf = FONT_BODY.render(line, True, COLOR_TEXT)
            screen.blit(line_surf, (35, 430 + i * 22))

        # --- BOJOVÝ LOG ---
        log_rect = pygame.Rect(540, 105, 340, 405)
        pygame.draw.rect(screen, COLOR_LOG, log_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL, log_rect, 2, border_radius=8)
        
        log_title = FONT_TITLE.render("Herný Denník", True, COLOR_ACCENT)
        screen.blit(log_title, (555, 115))

        for idx, log_entry in enumerate(combat_logs):
            log_surf = FONT_SMALL.render(f"> {log_entry}", True, COLOR_TEXT)
            screen.blit(log_surf, (555, 150 + idx * 38))

        # --- OVLÁDACIE TLAČIDLÁ ---
        buttons = []

        if player_hp <= 0:
            game_over_surf = FONT_TITLE.render("KONIEC HRY - BOL SI PORAZENÝ", True, COLOR_ENEMY_HP)
            screen.blit(game_over_surf, (200, 560))
        elif combat_active:
            # Bojové tlačidlá
            weapons = [w for w in inventory if w in ["sword", "axe", "magic staff"]]
            if weapons:
                for idx, w in enumerate(weapons):
                    btn = Button(30 + idx * 130, 535, 120, 45, f"Útok {w}", lambda w=w: execute_attack(w))
                    buttons.append(btn)
            else:
                btn_no_wep = Button(30, 535, 200, 45, "Nemáš zbraň", lambda: add_log("Nemáš zbraň!"), enabled=False)
                buttons.append(btn_no_wep)

            btn_run = Button(400, 535, 110, 45, "Útek", run_away)
            buttons.append(btn_run)
        else:
            # Tlačidlá pohybu
            cur = rooms[current_room]
            btn_n = Button(110, 520, 80, 35, "Sever (W)", lambda: move("north"), enabled="north" in cur)
            btn_s = Button(110, 580, 80, 35, "Juh (S)", lambda: move("south"), enabled="south" in cur)
            btn_w = Button(20, 550, 80, 35, "Západ (A)", lambda: move("west"), enabled="west" in cur)
            btn_e = Button(200, 550, 80, 35, "Východ (D)", lambda: move("east"), enabled="east" in cur)

            buttons.extend([btn_n, btn_s, btn_w, btn_e])

            # Tlačidlo na zozbieranie predmetu
            if cur.get("item"):
                btn_take = Button(320, 550, 160, 40, f"Zobrať: {cur['item']}", take_item)
                buttons.append(btn_take)

        for btn in buttons:
            btn.draw(screen)

        # Spracovanie udalostí
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Ovládanie klávesnicou (WASD)
            if not combat_active and player_hp > 0 and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    move("north")
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    move("south")
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    move("west")
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    move("east")

            for btn in buttons:
                btn.handle_event(event)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()