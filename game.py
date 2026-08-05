import pygame
import sys
import random
import os
import math

# --- INICIALIZÁCIA ---
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadows & Steel - Visual Enhanced Edition")

# --- MODERNÁ PALETA FARIEB ---
COLOR_BG = (12, 14, 20)           # Tmavé pozadie
COLOR_PANEL = (20, 24, 34)        # Hlavné panely
COLOR_CARD = (28, 34, 48)         # Vnútro kariet
COLOR_SLOT_EMPTY = (18, 22, 30)   # Prázdny slot
COLOR_BORDER = (45, 55, 75)       # Jemné okraje
COLOR_ACCENT = (236, 179, 101)    # Zlatý akcent
COLOR_CYAN = (64, 201, 255)       # Sekundárny akcent
COLOR_PURPLE = (180, 130, 255)    # Utilitné predmety
COLOR_TEXT = (240, 244, 248)      # Text
COLOR_MUTED = (120, 130, 150)     # Vedľajší text

COLOR_HP = (46, 213, 115)
COLOR_HP_BG = (20, 60, 35)
COLOR_MANA = (52, 152, 219)
COLOR_MANA_BG = (20, 45, 70)
COLOR_ENEMY_HP = (255, 71, 87)
COLOR_MISS = (241, 196, 15)

COLOR_BTN = (34, 42, 58)
COLOR_BTN_HOVER = (50, 62, 86)

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
    except Exception:
        enemy_images[enemy_key] = None

# --- PÍSMA ---
FONT_TITLE = pygame.font.SysFont("Segoe UI", 22, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Segoe UI", 15, bold=True)
FONT_BODY = pygame.font.SysFont("Segoe UI", 13)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 11, bold=True)
FONT_POPUP = pygame.font.SysFont("Segoe UI", 20, bold=True)

# --- MIESTNOSTI ---
rooms = {
    "hall": {"title": "Vstupná hala", "east": "dining room", "west": "library", "item": None, "bg_color": (22, 25, 35)},
    "dining room": {"title": "Jedáleň", "south": "kitchen", "north": "bedroom", "west": "hall", "item": "key", "bg_color": (28, 25, 32)},
    "kitchen": {"title": "Kuchyňa", "north": "dining room", "west": "garden", "south": "basement", "item": "sword", "bg_color": (32, 26, 24)},
    "garden": {"title": "Záhrada", "north": "shed", "east": "kitchen", "item": None, "enemy": "lion", "bg_color": (18, 30, 24)},
    "shed": {"title": "Kôlňa", "south": "garden", "item": "axe", "enemy": "panther", "bg_color": (22, 22, 20)},
    "library": {"title": "Knižnica", "east": "hall", "north": "tower", "item": "ancient book", "enemy": "ghost", "bg_color": (20, 25, 34)},
    "bedroom": {"title": "Panská spálňa", "south": "dining room", "north": "balcony", "item": "armor", "bg_color": (28, 22, 28)},
    "balcony": {"title": "Balkón", "south": "bedroom", "item": None, "bg_color": (20, 28, 36)},
    "basement": {"title": "Temná pivnica", "north": "kitchen", "item": "shield", "enemy": "zombie", "bg_color": (16, 16, 20)},
    "tower": {"title": "Vysoká veža", "south": "library", "item": "magic staff", "enemy": "dragon", "bg_color": (26, 20, 32)}
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
player_mana = 10
player_max_mana = 10
FIREBOLT_MANA_COST = 3

base_player_ac = 11
armor_bonus = 0
shield_bonus = 0

# Plynulé zobrazenie barov
display_hp = float(player_hp)
display_mana = float(player_mana)
display_enemy_hp = 0.0

# Bojový stav
combat_active = False
current_enemy = None
current_enemy_hp = 0

floating_texts = []
status_message = None
status_timer = 0
anim_ticks = 0

class DamageText:
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
    status_timer = 90

def get_player_ac():
    return base_player_ac + armor_bonus + shield_bonus

# --- MODERNÉ TLAČIDLO S HOVER GLOW ---
class Button:
    def __init__(self, x, y, w, h, text, callback, enabled=True, accent=False, badge=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.accent = accent
        self.badge = badge

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled

        bg_color = COLOR_BTN_HOVER if is_hovered else COLOR_BTN
        if not self.enabled:
            bg_color = (20, 24, 32)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)

        border_color = COLOR_ACCENT if (self.accent and self.enabled) else (COLOR_CYAN if is_hovered else COLOR_BORDER)
        if not self.enabled:
            border_color = (35, 40, 50)

        pygame.draw.rect(surface, border_color, self.rect, 2 if not is_hovered else 3, border_radius=10)

        text_color = COLOR_TEXT if self.enabled else COLOR_MUTED
        text_surf = FONT_SUBTITLE.render(self.text, True, text_color)
        
        if self.badge and self.enabled:
            badge_surf = FONT_SMALL.render(self.badge, True, COLOR_ACCENT)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 8))
            badge_rect = badge_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
            surface.blit(text_surf, text_rect)
            surface.blit(badge_surf, badge_rect)
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                self.callback()

# --- POMOCNÉ KRESLIACE FUNKCIE ---
def draw_card(surface, rect, border_color=COLOR_BORDER, accent_top=False):
    pygame.draw.rect(surface, COLOR_PANEL, rect, border_radius=12)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)
    
    if accent_top:
        accent_rect = pygame.Rect(rect.x + 12, rect.y, rect.w - 24, 3)
        pygame.draw.rect(surface, COLOR_ACCENT, accent_rect, border_radius=2)

def draw_bar(surface, x, y, w, h, val, max_val, color, bg_color=(20, 24, 32)):
    pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=6)
    ratio = max(0.0, val) / max_val
    fill_w = int(w * ratio)
    if fill_w > 0:
        pygame.draw.rect(surface, color, (x, y, fill_w, h), border_radius=6)
    pygame.draw.rect(surface, COLOR_BORDER, (x, y, w, h), 1, border_radius=6)

# --- HERNÁ LOGIKA ---
def move(direction):
    global current_room, combat_active, current_enemy, current_enemy_hp, display_enemy_hp
    if direction in rooms[current_room]:
        current_room = rooms[current_room][direction]
        if "enemy" in rooms[current_room]:
            enemy_type = rooms[current_room]["enemy"]
            current_enemy = enemy_type
            current_enemy_hp = enemy_stats[enemy_type]["hp"]
            display_enemy_hp = float(current_enemy_hp)
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

def execute_attack(action_type):
    global current_enemy_hp, player_hp, player_mana, combat_active
    if not combat_active or not current_enemy:
        return

    e_data = enemy_stats[current_enemy]

    if action_type == "firebolt":
        if player_mana < FIREBOLT_MANA_COST:
            show_status("⚠️ Nemáš dostatok many na Firebolt!")
            return
        player_mana -= FIREBOLT_MANA_COST
        weapon_bonus = 4
        weapon_damage_bonus = 6
        is_spell = True
    else:
        weapon_bonus = {"sword": 1, "axe": 4, "magic staff": 2, "warhammer": 6}.get(action_type, 0)
        weapon_damage_bonus = {"sword": 2, "axe": 4, "magic staff": 3, "warhammer": 10}.get(action_type, 0)
        is_spell = False

    enemy_x_center = 350
    player_x_center = 750

    roll = random.randint(1, 20)
    total_attack = roll + weapon_bonus

    if total_attack >= e_data["ac"]:
        damage = random.randint(1, 5) + weapon_damage_bonus
        current_enemy_hp -= damage
        spawn_popup(enemy_x_center, 280, f"-{damage}", COLOR_ENEMY_HP)
        
        if current_enemy_hp <= 0:
            show_status(f"⚔️ Porazil si {e_data['name']}!")
            defeated_enemy = current_enemy
            del rooms[current_room]["enemy"]
            combat_active = False

            if defeated_enemy == "panther":
                if random.random() < 0.5:
                    rooms[current_room]["item"] = "warhammer"
                    show_status("✨ Z Pantera vypadla vzácna zbraň Warhammer!")

            if not is_spell and random.random() < 0.5:
                inventory.remove(action_type)
                show_status(f"💥 Tvoja zbraň ({action_type}) sa zničila!")
            return
    else:
        spawn_popup(enemy_x_center, 280, "MISSED!", COLOR_MISS)

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
    global player_hp, status_timer, display_hp, display_mana, display_enemy_hp, anim_ticks
    clock = pygame.time.Clock()
    
    running = True
    while running:
        anim_ticks += 1
        screen.fill(COLOR_BG)

        # Smooth Bar Interpolation (Damping)
        display_hp += (player_hp - display_hp) * 0.15
        display_mana += (player_mana - display_mana) * 0.15
        if combat_active:
            display_enemy_hp += (current_enemy_hp - display_enemy_hp) * 0.15

        # -------------------------------------------------------------
        # 1. TOP HEADER (PLAYER STATS)
        # -------------------------------------------------------------
        draw_card(screen, pygame.Rect(20, 20, 960, 75), COLOR_BORDER, accent_top=True)
        
        title_surf = FONT_TITLE.render(rooms[current_room]["title"].upper(), True, COLOR_ACCENT)
        screen.blit(title_surf, (40, 32))
        
        sub_title = FONT_SMALL.render("MIESTNOST", True, COLOR_MUTED)
        screen.blit(sub_title, (40, 60))

        ac_badge = pygame.Rect(400, 32, 110, 48)
        pygame.draw.rect(screen, COLOR_CARD, ac_badge, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, ac_badge, 1, border_radius=8)
        
        ac_val = FONT_SUBTITLE.render(f"AC {get_player_ac()}", True, COLOR_CYAN)
        ac_lbl = FONT_SMALL.render("OCHRANA", True, COLOR_MUTED)
        screen.blit(ac_val, (415, 37))
        screen.blit(ac_lbl, (415, 58))

        hp_lbl = FONT_SMALL.render(f"HP {max(0, player_hp)} / {player_max_hp}", True, COLOR_TEXT)
        screen.blit(hp_lbl, (530, 28))
        draw_bar(screen, 530, 44, 210, 14, display_hp, player_max_hp, COLOR_HP, COLOR_HP_BG)

        mana_lbl = FONT_SMALL.render(f"MANA {max(0, player_mana)} / {player_max_mana}", True, COLOR_TEXT)
        screen.blit(mana_lbl, (760, 28))
        draw_bar(screen, 760, 44, 210, 14, display_mana, player_max_mana, COLOR_MANA, COLOR_MANA_BG)

        # -------------------------------------------------------------
        # 2. MAIN VIEWPORT
        # -------------------------------------------------------------
        view_rect = pygame.Rect(20, 110, 660, 435)
        room_bg = rooms[current_room].get("bg_color", COLOR_PANEL)
        
        pygame.draw.rect(screen, room_bg, view_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BORDER, view_rect, 2, border_radius=12)

        room_item = rooms[current_room].get("item")
        if room_item:
            item_box = pygame.Rect(40, 465, 220, 60)
            pygame.draw.rect(screen, COLOR_CARD, item_box, border_radius=8)
            pygame.draw.rect(screen, COLOR_ACCENT, item_box, 1, border_radius=8)
            
            lbl = FONT_SMALL.render("NÁJDENÝ PREDMET", True, COLOR_ACCENT)
            val = FONT_SUBTITLE.render(room_item.capitalize(), True, COLOR_TEXT)
            screen.blit(lbl, (50, 470))
            screen.blit(val, (50, 490))

        if combat_active and current_enemy:
            e_info = enemy_stats[current_enemy]

            e_name = FONT_SUBTITLE.render(e_info["name"].upper(), True, COLOR_TEXT)
            screen.blit(e_name, e_name.get_rect(center=(350, 185)))

            draw_bar(screen, 220, 210, 260, 14, display_enemy_hp, e_info["max_hp"], COLOR_ENEMY_HP)

            # Floating Bobbing Animation for Enemy
            bob_offset = int(math.sin(anim_ticks * 0.08) * 4)
            enemy_center_y = 325 + bob_offset

            # Soft Ground Shadow under sprite
            shadow_rect = pygame.Rect(0, 0, 110, 22)
            shadow_rect.center = (350, 395)
            pygame.draw.ellipse(screen, (10, 12, 16), shadow_rect)

            enemy_img = enemy_images.get(current_enemy)
            if enemy_img:
                img_rect = enemy_img.get_rect(center=(350, enemy_center_y))
                screen.blit(enemy_img, img_rect)
            else:
                pygame.draw.circle(screen, e_info["color"], (350, enemy_center_y), 50)
                pygame.draw.circle(screen, COLOR_CARD, (350, enemy_center_y), 44)
                e_initial = FONT_TITLE.render(e_info["name"][0], True, COLOR_TEXT)
                screen.blit(e_initial, e_initial.get_rect(center=(350, enemy_center_y)))

        # -------------------------------------------------------------
        # 3. INVENTORY PANEL (RIGHT SIDE)
        # -------------------------------------------------------------
        inv_rect = pygame.Rect(700, 110, 280, 435)
        draw_card(screen, inv_rect, accent_top=True)

        inv_title = FONT_SUBTITLE.render("INVENTÁR A VÝBAVA", True, COLOR_CYAN)
        screen.blit(inv_title, (715, 125))
        
        slot_count_txt = FONT_SMALL.render(f"{len(inventory)}/{MAX_INVENTORY_SLOTS}", True, COLOR_MUTED)
        screen.blit(slot_count_txt, (935, 128))

        pygame.draw.line(screen, COLOR_BORDER, (715, 150), (965, 150), 1)

        for i in range(MAX_INVENTORY_SLOTS):
            col = i % 2
            row = i // 2
            
            x_pos = 715 + col * 128
            y_pos = 160 + row * 52
            
            slot_rect = pygame.Rect(x_pos, y_pos, 120, 44)
            
            if i < len(inventory):
                item = inventory[i]
                pygame.draw.rect(screen, COLOR_CARD, slot_rect, border_radius=8)
                pygame.draw.rect(screen, COLOR_BORDER, slot_rect, 1, border_radius=8)
                
                if item in ["sword", "axe", "magic staff", "warhammer"]:
                    dot_color = COLOR_ACCENT
                elif item in ["armor", "shield"]:
                    dot_color = COLOR_CYAN
                else:
                    dot_color = COLOR_PURPLE
                    
                pygame.draw.circle(screen, dot_color, (x_pos + 15, y_pos + 22), 5)
                
                name_txt = FONT_SMALL.render(item.capitalize(), True, COLOR_TEXT)
                screen.blit(name_txt, (x_pos + 28, y_pos + 15))
            else:
                pygame.draw.rect(screen, COLOR_SLOT_EMPTY, slot_rect, border_radius=8)
                pygame.draw.rect(screen, (30, 36, 48), slot_rect, 1, border_radius=8)
                empty_lbl = FONT_SMALL.render(f"Slot {i+1}", True, (45, 52, 68))
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
            weapons = [w for w in inventory if w in ["sword", "axe", "magic staff", "warhammer"]]
            btn_offset_x = 40
            
            weapon_badges = {
                "sword": "+1 ATK / +2 DMG",
                "axe": "+4 ATK / +4 DMG",
                "magic staff": "+2 ATK / +3 DMG",
                "warhammer": "+6 ATK / +10 DMG"
            }

            if weapons:
                for w in weapons:
                    btn = Button(
                        btn_offset_x, 590, 140, 55, 
                        f"Útok {w.capitalize()}", 
                        lambda w=w: execute_attack(w), 
                        accent=True,
                        badge=weapon_badges.get(w)
                    )
                    buttons.append(btn)
                    btn_offset_x += 150
            else:
                btn_no_wep = Button(btn_offset_x, 590, 150, 55, "Bez zbrane", lambda: show_status("⚠️ Nemáš zbraň!"), enabled=False)
                buttons.append(btn_no_wep)
                btn_offset_x += 160

            has_enough_mana = player_mana >= FIREBOLT_MANA_COST
            btn_firebolt = Button(
                btn_offset_x, 590, 160, 55, 
                "🔥 Firebolt (3 MP)", 
                lambda: execute_attack("firebolt"), 
                enabled=has_enough_mana, 
                accent=True,
                badge="+4 ATK / +6 DMG"
            )
            buttons.append(btn_firebolt)

            btn_run = Button(800, 590, 140, 55, "Útek", run_away)
            buttons.append(btn_run)
        else:
            cur = rooms[current_room]
            btn_n = Button(130, 570, 80, 42, "▲ N", lambda: move("north"), enabled="north" in cur)
            btn_s = Button(130, 620, 80, 42, "▼ S", lambda: move("south"), enabled="south" in cur)
            btn_w = Button(45, 595, 80, 42, "◀ W", lambda: move("west"), enabled="west" in cur)
            btn_e = Button(215, 595, 80, 42, "▶ E", lambda: move("east"), enabled="east" in cur)

            buttons.extend([btn_n, btn_s, btn_w, btn_e])

            if cur.get("item"):
                btn_take = Button(340, 590, 240, 55, f"Zobrať: {cur['item'].capitalize()}", take_item, accent=True)
                buttons.append(btn_take)

        for btn in buttons:
            btn.draw(screen)

        # -------------------------------------------------------------
        # 5. FLOATING TEXTS & STATUS TOAST
        # -------------------------------------------------------------
        for pop in floating_texts[:]:
            pop.update()
            pop.draw(screen)
            if pop.lifetime <= 0:
                floating_texts.remove(pop)

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