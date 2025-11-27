from ursina import Button, Entity, color, mouse, camera, application, time
from ursina import Entity as E

paused = False
enemy_manager = None  # będzie ustawione w setup_ui

def setup_ui(terrain, player, styles_module=None):
    # hotbar
    for i, col in enumerate(player.HOTBAR_COLORS):
        slot = Button(parent=camera.ui, model='quad', color=color.gray, highlight_color=color.light_gray,
                      scale=(0.07,0.07), x=-0.3 + i*0.07, y=-0.45)
        E(parent=slot, model='cube', scale=(0.8,0.8,0.8), color=col)
        player.hotbar_slots.append(slot)
    try:
        player.hotbar_slots[player.selected_slot].color = color.orange
    except Exception:
        pass

    # ESC overlay
    global esc_overlay
    esc_overlay = Entity(parent=camera.ui, enabled=False)
    Entity(parent=esc_overlay, model='quad', scale=(2,2), color=color.rgba(0,0,0,0.6))
    resume_button = Button(text='Resume', parent=esc_overlay, scale=(0.2,0.1), y=0.1, color=color.azure)
    quit_button = Button(text='Quit', parent=esc_overlay, scale=(0.2,0.1), y=-0.1, color=color.red)
    resume_button.on_click = lambda: toggle_pause()
    quit_button.on_click = application.quit

    # pre-game menu
    menu_overlay = Entity(parent=camera.ui)
    Entity(parent=menu_overlay, model='quad', scale=(2,2), color=color.rgba(0,0,0,0.7))
    flat_button = Button(text='Flat', scale=(0.3,0.1), y=0.1, parent=menu_overlay, color=color.azure)
    natural_button = Button(text='Natural', scale=(0.3,0.1), y=-0.1, parent=menu_overlay, color=color.green)

    mouse.locked = False

    def start(terrain_type):
        menu_overlay.enabled = False
        terrain.generate_terrain(terrain_type)
        player.player.position = (0, terrain.MAX_HEIGHT+5, -terrain.TERRAIN_SIZE//2)
        player.player.enabled = True
        mouse.locked = True

    flat_button.on_click = lambda: start("Flat")
    natural_button.on_click = lambda: start("Natural")

    # Zamiast starego kodu, poniżej integruję wrogi
    global esc_overlay, enemy_manager
    from game.enemy import EnemyManager
    enemy_manager = EnemyManager(player.player, spawn_distance=25.0)

# input and update functions (Ursina will call functions bound in main)
def input(key):
    from game import terrain, player
    from ursina import time as ursina_time
    global paused
    if key == 'escape':
        toggle_pause()
    if paused or not player.player.enabled:
        return

    # Hotbar selection
    if key in list('123456789'):
        player.select_slot(int(key)-1)
    if key == 'scroll up': player.select_slot((player.selected_slot+1)%len(player.hotbar_slots))
    if key == 'scroll down': player.select_slot((player.selected_slot-1)%len(player.hotbar_slots))

    # Break block
    if key == 'left mouse down':
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit:
            pos = hit.entity.position
            terrain.remove_block((int(round(pos.x)), int(round(pos.y)), int(round(pos.z))))

    # Place block
    if key == 'right mouse down':
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit:
            pos = hit.entity.position
            normal = hit.normal
            place_pos = (int(round(pos.x+normal.x)), int(round(pos.y+normal.y)), int(round(pos.z+normal.z)))
            player_pos = (int(round(player.player.x)), int(round(player.player.y)), int(round(player.player.z)))
            if place_pos != player_pos:
                terrain.spawn_block(place_pos, shade_idx=player.selected_slot)

    # NOWY: Atak (spacja)
    if key == 'space':
        if player.try_attack():
            attacked = enemy_manager.player_attack(damage_range=5.0, damage=5)
            # Opcjonalnie: print(f"Trafiono wrogów: {attacked}")

def update():
    from game import terrain, player
    global enemy_manager
    
    if player.player.enabled:
        player.selected_text.text = f'Selected: {player.selected_slot+1}'
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit and hit.entity in terrain.blocks.values():
            player.highlight.position = hit.entity.position
            player.highlight.enabled = True
        else:
            player.highlight.enabled = False
    
    # NOWY: Aktualizacja wrogów
    if enemy_manager and player.player.enabled:
        from ursina import time as ursina_time
        enemy_manager.update(ursina_time.dt())
        
        # Wrogowie atakują gracza (co sekundę, przykład)
        for enemy in enemy_manager.enemies:
            if enemy.entity is not None:
                from ursina import distance
                dist = distance(player.player.position, enemy.entity.position)
                if dist < 2.0 and ursina_time.time() % 1.0 < 0.1:  # co 1 sek
                    player.take_damage(1)

def toggle_pause():
    global paused, esc_overlay
    paused = not paused
    esc_overlay.enabled = paused
    mouse.locked = not paused
    application.paused = paused