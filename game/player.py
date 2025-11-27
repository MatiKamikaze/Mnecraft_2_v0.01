from ursina import camera, Entity, Text, Vec3, color, raycast
from ursina.prefabs.first_person_controller import FirstPersonController

# Inicjalizacja kontrolera
player = FirstPersonController()
player.gravity = 0.3
player.cursor.visible = False
player.speed = 5
player.enabled = False

color_sky = color.blue

# Prosty crosshair
crosshair = Text('|', origin=(0,0), scale=2, position=(0,0))

# Text UI: wybór slotu i HP gracza
selected_text = Text('Selected: 1', parent=camera.ui, position=(-0.85,0.45), scale=1.2)
hp_text = Text('HP: 100', parent=camera.ui, position=(-0.85,0.40), scale=1.2, color=color.red)

# Highlight
highlight = Entity(model='cube', color=color.rgba(1,1,0,0.3),
                   scale=Vec3(1.05,1.05,1.05), collider=None, enabled=False)

# HP gracza
player_hp = 100
player_max_hp = 100

# Atak
attack_cooldown = 0.3  # sekund między atakami
last_attack_time = 0
attack_range = 5.0
attack_damage = 5

def get_hit(ignore_list=None, traverse_target=None):
    ig = [player]
    if ignore_list:
        ig += ignore_list
    return raycast(camera.world_position, camera.forward, distance=8, ignore=ig, traverse_target=traverse_target)

# Hotbar
HOTBAR_COLORS = [
    color.green, color.blue, color.rgb(0.5,0,0.5),
    color.red, color.rgb(1,0.5,0), color.cyan,
    color.yellow, color.rgb(1,0,1), color.white
]
hotbar_slots = []
selected_slot = 0

def select_slot(index):
    global selected_slot
    if 0 <= index < len(hotbar_slots):
        try:
            hotbar_slots[selected_slot].color = color.gray
            selected_slot = index
            hotbar_slots[selected_slot].color = color.orange
        except Exception:
            selected_slot = index

def take_damage(damage):
    """Gracz bierze obrażenia."""
    global player_hp
    player_hp = max(0, player_hp - damage)
    hp_text.text = f'HP: {player_hp}/{player_max_hp}'
    if player_hp <= 0:
        on_player_death()

def heal(amount):
    """Gracz się leczy."""
    global player_hp
    player_hp = min(player_max_hp, player_hp + amount)
    hp_text.text = f'HP: {player_hp}/{player_max_hp}'

def on_player_death():
    """Gracz umiera."""
    player.enabled = False
    hp_text.text = 'DEAD - Nacisnij ESC'

def try_attack():
    """Gracz próbuje atakować — zwraca czy trafił."""
    global last_attack_time
    from ursina import time
    if time.time() - last_attack_time >= attack_cooldown:
        last_attack_time = time.time()
        return True
    return False