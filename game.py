import pygame
import sys
import random
import os

# --- INICIALIZÁCIA ---
pygame.init()
pygame.font.init()

# Rozmery okna
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadows & Steel - Text Adventure")

# --- MODERNÁ PALETA FARIEB ---
COLOR_BG = (15, 17, 23)           # Tmavé pozadie
COLOR_PANEL = (24, 28, 38)        # Hlavné panely
COLOR_CARD = (32, 38, 52)         # Vnútro kariet
COLOR_SLOT_EMPTY = (22, 26, 35)   # Prázdny slot
COLOR_BORDER = (55, 65, 85)       # Jemné okraje
COLOR_ACCENT = (236, 179, 101)    # Zlatý akcent (Zbrane)
COLOR_CYAN = (64, 201, 255)       # Sekundárny akcent (Brnenie)
COLOR_PURPLE = (180, 130, 255)     # Utilitné predmety
COLOR_TEXT = (240, 244, 248)      # Text
COLOR_MUTED = (130, 140, 160)     # Vedľajší text

COLOR_HP = (46, 213, 115)         # Žiarivá zelená
COLOR_ENEMY_HP = (255, 71, 87)    # Žiarivá červená
COLOR_MISS = (241, 196, 15)       # Žltá pre minutie

COLOR_BTN = (40, 48, 66)
COLOR_BTN_HOVER = (60, 72, 98)

# --- NAČÍTANIE OBRÁZKOV NEPRIATEĽOV ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENEMY_IMG_DIR = os.path.join(SCRIPT_DIR, "pictures_enemy")

enemy_images = {}
enemy_file_map = {
    "dragon": "drak.png",
    "ghost": "ghost.png",
    "lion": "lion.png",
    "panther": "panther.png",
    "zombie": "zombie.png"
}

for enemy_key, filename in enemy_file_map.items():
    img_path = os.path.join(ENEMY_IMG_DIR, filename)
    try:
        img = pygame.image.load(img_path).convert_alpha()
        enemy_images[enemy_key] = pygame.transform.scale(img, (140, 140))
    except Exception as e:
        enemy_images[enemy_key] = None

# --- PÍSMA ---
FONT_TITLE = pygame.font.SysFont("Segoe UI", 22, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Segoe UI", 16, bold=True)
FONT_BODY = pygame.font.SysFont("Segoe UI", 14)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 11)
FONT_POPUP = pygame.font.SysFont("Segoe UI", 20, bold=True)

# --- MIESTNOSTI ---
rooms = {
    "hall": {
        "title": "Vstupná hala",
        "east": "dining room", "west": "library", "item": None, "bg_color": (25, 28, 38)
    },
    "dining room": {
        "title": "Jedáleň",
        "south": "kitchen", "north": "bedroom", "west": "hall", "item": "key", "bg_color": (32, 28, 35)
    },
    "kitchen": {
        "title": "Kuchyňa",
        "north": "dining room", "west": "garden", "south": "basement", "item": "sword", "bg_color": (35, 30, 28)
    },
    "garden": {
        "title": "Záhrada",
        "north": "shed", "east": "kitchen", "item": None, "enemy": "lion", "bg_color": (20, 35, 28)
    },
    "shed": {
        "title": "Kôlňa",
        "south": "garden", "item": "axe", "enemy": "panther", "bg_color": (25, 25, 22)
    },
    "library": {
        "title": "Knižnica",
        "east": "hall", "north": "tower", "item": "ancient book", "enemy": "ghost", "bg_color": (22, 28, 38)
    },
    "bedroom": {
        "title": "Panská spálňa",
        "south": "dining room", "north": "balcony", "item": "armor", "bg_color": (32, 24, 32)
    },
    "balcony": {
        "title": "Balkón",
        "south": "bedroom", "item": None, "bg_color": (22, 32, 40)
    },
    "basement": {
        "title": "Temná pivnica",
        "north": "kitchen", "item": "shield", "enemy": "zombie", "bg_color": (18, 18, 22)
    },
    "tower": {
        "title": "Vysoká veža",
        "south": "library", "item": "magic staff", "enemy": "dragon", "bg_color": (30, 22, 35)
    }
}

# --- NEPRIATELIA ---
enemy_stats = {
    "dragon": {"name": "Drak", "hp": 20, "max_hp": 20, "ac": 18, "damage_range": (1, 15), "color": (231, 76, 60)},
    "zombie": {"name": "Zombie", "hp": 8, "max_hp": 8, "ac": 8, "damage_range": (1, 5), "color": (46, 204, 113)},
    "lion": {"name": "Lev", "hp": 12, "max_hp": 12, "ac": 15, "damage_range": (1, 7), "color": (241, 196, 15)},
    "panther": {"name": "Panter", "hp": 10, "max_hp": 10, "ac": 13, "damage_range": (1, 5), "color": (155, 89, 182)},
    "ghost": {"name": "Duch", "hp": 2, "max_hp": 2, "ac": 5, "damage_range": (1, 2), "color": (52, 152, 219)}
}

# Hráčové štatistiky
inventory = []
MAX_INVENTORY_SLOTS = 10
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

# --- LIETAJÚCI BATTLE TEXT & NOTIFIKÁCIE ---
floating_texts = []
status_message = None
status_timer = 0

class DamageText:
    """Plávajúce číselné poškodenie alebo text nad cieľom."""
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 60
        self.alpha = 255

    def update(self):
        self.y -= 0.8
        self.lifetime -= 1
        self.alpha = max(0, int((self.lifetime / 60) * 255))

    def draw(self, surface):
        if self.lifetime > 0:
            surf = FONT_POPUP.render(self.text, True, self.color)
            surf.set_alpha(self.alpha)
            rect = surf.get_rect(center=(self.x, self.y))
            surface.blit(surf, rect)

def spawn_popup(x, y, text, color):
    floating_texts.append(DamageText(x, y, text, color))

def show_status(msg):
    global status_message, status_timer
    status_message = msg
    status_timer = 90  # 3 sekundy pri 30 FPS

def get_player_ac():
    return base_player_ac + armor_bonus + shield_bonus

# --- MODERNÉ TLAČIDLO ---
class Button:
    def __init__(self, x, y, w, h, text, callback, enabled=True, accent=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.accent = accent

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled

        bg_color = COLOR_BTN_HOVER if is_hovered else COLOR_BTN
        if not self.enabled:
            bg_color = (25, 29, 38)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)

        border_color = COLOR_ACCENT if (self.accent and self.enabled) else (COLOR_CYAN if is_hovered else COLOR_BORDER)
        if not self.enabled:
            border_color = (40, 45, 55)

        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        text_color = COLOR_TEXT if self.enabled else COLOR_MUTED
        text_surf = FONT_SUBTITLE.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                self.callback()

# --- POMOCNÉ KRESLIACE FUNKCIE ---
def draw_card(surface, rect, border_color=COLOR_BORDER):
    pygame.draw.rect(surface, COLOR_PANEL, rect, border_radius=12)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)

def draw_bar(surface, x, y, w, h, val, max_val, color):
    pygame.draw.rect(surface, (20, 24, 32), (x, y, w, h), border_radius=6)
    ratio = max(0, val) / max_val
    fill_w = int(w * ratio)
    if fill_w > 0:
        pygame.draw.rect(surface, color, (x, y, fill_w, h), border_radius=6)
    pygame.draw.rect(surface, COLOR_BORDER, (x, y, w, h), 1, border_radius=6)

# --- HERNÁ LOGIKA ---
def move(direction):
    global current_room, combat_active, current_enemy, current_enemy_hp
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        if "enemy" in rooms[current_room]:
            enemy_type = rooms[current_room]["enemy"]
            current_enemy = enemy_type
            current_enemy_hp = enemy_stats[enemy_type]["hp"]
            combat_active = True
            show_status(f"⚠️ Útočí na teba {enemy_stats[enemy_type]['name']}!")

def take_item():
    global armor_bonus, shield_bonus
    item = rooms[current_room].get("item")
    if item:
        if len(inventory) >= MAX_INVENTORY_SLOTS:
            show_status("⚠️ Tvoj inventár je plný!")
            return

        inventory.append(item)
        rooms[current_room]["item"] = None
        show_status(f"✨ Zozbieral si: {item.capitalize()}")
        if item == "armor":
            armor_bonus = 3
            spawn_popup(750, 60, "+3 AC (Brnenie)", COLOR_CYAN)
        elif item == "shield":
            shield_bonus = 1
            spawn_popup(750, 60, "+1 AC (Štít)", COLOR_CYAN)

def execute_attack(weapon):
    global current_enemy_hp, player_hp, combat_active
    if not combat_active or not current_enemy:
        return

    e_data = enemy_stats[current_enemy]
    
    weapon_bonus = {"sword": 1, "axe": 4, "magic staff": 2}.get(weapon, 0)
    weapon_damage_bonus = {"sword": 2, "axe": 4, "magic staff": 3}.get(weapon, 0)

    enemy_x_center = 350
    player_x_center = 750

    # 1. Hráčov útok
    roll = random.randint(1, 20)
    total_attack = roll + weapon_bonus

    if total_attack >= e_data["ac"]:
        damage = random.randint(1, 5) + weapon_damage_bonus
        current_enemy_hp -= damage
        spawn_popup(enemy_x_center, 280, f"-{damage}", COLOR_ENEMY_HP)
        
        if current_enemy_hp <= 0:
            show_status(f"⚔️ Porazil si {e_data['name']}!")
            del rooms[current_room]["enemy"]
            combat_active = False
            
            if random.random() < 0.5:
                inventory.remove(weapon)
                show_status(f"💥 Tvoja zbraň ({weapon}) sa zničila!")
            return
    else:
        spawn_popup(enemy_x_center, 280, "MISSED!", COLOR_MISS)

    # 2. Nepriateľov útok
    enemy_roll = random.randint(1, 20)
    p_ac = get_player_ac()

    if enemy_roll >= p_ac:
        e_dmg = random.randint(*e_data["damage_range"])
        player_hp -= e_dmg
        spawn_popup(player_x_center, 60, f"-{e_dmg} HP", COLOR_ENEMY_HP)
        if player_hp <= 0:
            show_status("☠️ Bol si porazený... Koniec hry!")
    else:
        spawn_popup(player_x_center, 60, "BLOCKED!", COLOR_CYAN)

def run_away():
    global combat_active
    if combat_active:
        show_status("🏃 Podarilo sa ti utiecť!")
        combat_active = False

# --- HLAVNÝ HERNÝ CYKLUS ---
def main():
    global player_hp, status_timer
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill(COLOR_BG)

        # -------------------------------------------------------------
        # 1. TOP HEADER (PLAYER STATS)
        # -------------------------------------------------------------
        draw_card(screen, pygame.Rect(20, 20, 960, 75), COLOR_BORDER)
        
        # Názov miestnosti
        title_surf = FONT_TITLE.render(rooms[current_room]["title"].upper(), True, COLOR_ACCENT)
        screen.blit(title_surf, (40, 32))
        
        sub_title = FONT_SMALL.render("MIESTNOST", True, COLOR_MUTED)
        screen.blit(sub_title, (40, 60))

        # Ochrana (AC Badge)
        ac_badge = pygame.Rect(480, 35, 120, 45)
        pygame.draw.rect(screen, COLOR_CARD, ac_badge, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, ac_badge, 1, border_radius=8)
        
        ac_val = FONT_SUBTITLE.render(f"AC {get_player_ac()}", True, COLOR_CYAN)
        ac_lbl = FONT_SMALL.render("OCHRANA", True, COLOR_MUTED)
        screen.blit(ac_val, (495, 42))
        screen.blit(ac_lbl, (495, 60))

        # HP Bar Hráča
        hp_lbl = FONT_SMALL.render(f"HP {max(0, player_hp)} / {player_max_hp}", True, COLOR_TEXT)
        screen.blit(hp_lbl, (630, 32))
        draw_bar(screen, 630, 52, 330, 18, player_hp, player_max_hp, COLOR_HP)

        # -------------------------------------------------------------
        # 2. MAIN VIEWPORT
        # -------------------------------------------------------------
        view_rect = pygame.Rect(20, 110, 660, 435)
        room_bg = rooms[current_room].get("bg_color", COLOR_PANEL)
        
        pygame.draw.rect(screen, room_bg, view_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BORDER, view_rect, 2, border_radius=12)

        # Predmet na zemi v miestnosti
        room_item = rooms[current_room].get("item")
        if room_item:
            item_box = pygame.Rect(40, 465, 220, 60)
            pygame.draw.rect(screen, COLOR_CARD, item_box, border_radius=8)
            pygame.draw.rect(screen, COLOR_ACCENT, item_box, 1, border_radius=8)
            
            lbl = FONT_SMALL.render("NÁJDENÝ PREDMET", True, COLOR_ACCENT)
            val = FONT_SUBTITLE.render(room_item.capitalize(), True, COLOR_TEXT)
            screen.blit(lbl, (50, 470))
            screen.blit(val, (50, 490))

        # Kreslenie nepriateľa
        if combat_active and current_enemy:
            e_info = enemy_stats[current_enemy]

            # 1. Meno nepriateľa nad HP barom
            e_name = FONT_SUBTITLE.render(e_info["name"].upper(), True, COLOR_TEXT)
            screen.blit(e_name, e_name.get_rect(center=(350, 185)))

            # 2. Ukazovateľ života (HP Bar) nad nepriateľom (skryté číselné HP)
            draw_bar(screen, 220, 210, 260, 14, current_enemy_hp, e_info["max_hp"], COLOR_ENEMY_HP)

            # 3. Obrázok / Avatar nepriateľa pod HP barom
            enemy_img = enemy_images.get(current_enemy)
            if enemy_img:
                img_rect = enemy_img.get_rect(center=(350, 325))
                screen.blit(enemy_img, img_rect)
            else:
                # Náhradný avatar ak obrázok chýba
                pygame.draw.circle(screen, e_info["color"], (350, 325), 50)
                pygame.draw.circle(screen, COLOR_CARD, (350, 325), 44)
                e_initial = FONT_TITLE.render(e_info["name"][0], True, COLOR_TEXT)
                screen.blit(e_initial, e_initial.get_rect(center=(350, 325)))

        # -------------------------------------------------------------
        # 3. FIXED SLOTS INVENTORY PANEL (RIGHT SIDE)
        # -------------------------------------------------------------
        inv_rect = pygame.Rect(700, 110, 280, 435)
        pygame.draw.rect(screen, COLOR_PANEL, inv_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BORDER, inv_rect, 2, border_radius=12)

        inv_title = FONT_SUBTITLE.render("INVENTÁR A VÝBAVA", True, COLOR_CYAN)
        screen.blit(inv_title, (715, 125))
        
        slot_count_txt = FONT_SMALL.render(f"{len(inventory)}/{MAX_INVENTORY_SLOTS}", True, COLOR_MUTED)
        screen.blit(slot_count_txt, (935, 128))

        pygame.draw.line(screen, COLOR_BORDER, (715, 150), (965, 150), 1)

        # Mriežka 10 samostatných slotov (2 stĺpce x 5 riadkov)
        for i in range(MAX_INVENTORY_SLOTS):
            col = i % 2
            row = i // 2
            
            x_pos = 715 + col * 128
            y_pos = 160 + row * 52
            
            slot_rect = pygame.Rect(x_pos, y_pos, 120, 44)
            
            if i < len(inventory):
                # Obsadený slot
                item = inventory[i]
                pygame.draw.rect(screen, COLOR_CARD, slot_rect, border_radius=8)
                pygame.draw.rect(screen, COLOR_BORDER, slot_rect, 1, border_radius=8)
                
                # Farebný indikátor typu
                if item in ["sword", "axe", "magic staff"]:
                    dot_color = COLOR_ACCENT
                elif item in ["armor", "shield"]:
                    dot_color = COLOR_CYAN
                else:
                    dot_color = COLOR_PURPLE
                    
                pygame.draw.circle(screen, dot_color, (x_pos + 15, y_pos + 22), 5)
                
                name_txt = FONT_SMALL.render(item.capitalize(), True, COLOR_TEXT)
                screen.blit(name_txt, (x_pos + 28, y_pos + 15))
            else:
                # Prázdny slot
                pygame.draw.rect(screen, COLOR_SLOT_EMPTY, slot_rect, border_radius=8)
                pygame.draw.rect(screen, (35, 42, 55), slot_rect, 1, border_radius=8)
                empty_lbl = FONT_SMALL.render(f"Slot {i+1}", True, (50, 60, 80))
                screen.blit(empty_lbl, empty_lbl.get_rect(center=slot_rect.center))

        # -------------------------------------------------------------
        # 4. CONTROLS AREA
        # -------------------------------------------------------------
        ctrl_rect = pygame.Rect(20, 560, 960, 115)
        draw_card(screen, ctrl_rect)

        buttons = []

        if player_hp <= 0:
            game_over_surf = FONT_TITLE.render("BOL SI PORAZENÝ - KONIEC HRY", True, COLOR_ENEMY_HP)
            screen.blit(game_over_surf, game_over_surf.get_rect(center=(500, 615)))
        elif combat_active:
            # Bojové tlačidlá
            weapons = [w for w in inventory if w in ["sword", "axe", "magic staff"]]
            if weapons:
                for idx, w in enumerate(weapons):
                    btn = Button(40 + idx * 160, 590, 150, 55, f"Útok {w.capitalize()}", lambda w=w: execute_attack(w), accent=True)
                    buttons.append(btn)
            else:
                btn_no_wep = Button(40, 590, 200, 55, "Nemáš zbraň", lambda: show_status("⚠️ Nemáš zbraň!"), enabled=False)
                buttons.append(btn_no_wep)

            btn_run = Button(800, 590, 140, 55, "Útek", run_away)
            buttons.append(btn_run)
        else:
            # Pohybové tlačidlá
            cur = rooms[current_room]
            btn_n = Button(130, 570, 80, 42, "▲ N", lambda: move("north"), enabled="north" in cur)
            btn_s = Button(130, 620, 80, 42, "▼ S", lambda: move("south"), enabled="south" in cur)
            btn_w = Button(45, 595, 80, 42, "◀ W", lambda: move("west"), enabled="west" in cur)
            btn_e = Button(215, 595, 80, 42, "▶ E", lambda: move("east"), enabled="east" in cur)

            buttons.extend([btn_n, btn_s, btn_w, btn_e])

            # Tlačidlo vyzdvihnutia predmetu
            if cur.get("item"):
                btn_take = Button(340, 590, 240, 55, f"Zobrať: {cur['item'].capitalize()}", take_item, accent=True)
                buttons.append(btn_take)

        for btn in buttons:
            btn.draw(screen)

        # -------------------------------------------------------------
        # 5. DRAW FLOATING COMBAT TEXTS & NOTIFICATIONS
        # -------------------------------------------------------------
        for pop in floating_texts[:]:
            pop.update()
            pop.draw(screen)
            if pop.lifetime <= 0:
                floating_texts.remove(pop)

        # Status Banner
        if status_timer > 0 and status_message:
            status_timer -= 1
            toast_rect = pygame.Rect(300, 120, 400, 40)
            pygame.draw.rect(screen, COLOR_CARD, toast_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_ACCENT, toast_rect, 1, border_radius=8)
            
            t_surf = FONT_SUBTITLE.render(status_message, True, COLOR_TEXT)
            screen.blit(t_surf, t_surf.get_rect(center=toast_rect.center))

        # -------------------------------------------------------------
        # EVENT HANDLING
        # -------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Klávesové skratky (WASD / Šípky)
            if not combat_active and player_hp > 0 and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    move("north")
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    move("south")
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    move("west")
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    move("east")

            for btn in buttons:
                btn.handle_event(event)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()