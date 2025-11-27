from ursina import camera, Entity, Text, Vec3, color, raycast
from ursina.prefabs.first_person_controller import FirstPersonController

# Player setup
player = FirstPersonController()
player.gravity = 0.3
player.cursor.visible = False
player.speed = 5
player.enabled = False

color_sky = color.blue
crosshair = Text('|', origin=(0,0), scale=2, position=(0,0))
selected_text = Text('Selected: 1', parent=camera.ui, position=(-0.85,0.45), scale=1.2)

# highlight cube
highlight = Entity(model='cube', color=color.rgba(1,1,0,0.3), scale=Vec3(1.05,1.05,1.05), collider=None, enabled=False)

def get_hit(ignore_list=None, traverse_target=None):
    ig = [player]
    if ignore_list:
        ig += ignore_list
    return raycast(camera.world_position, camera.forward, distance=8, ignore=ig, traverse_target=traverse_target)

# hotbar state
HOTBAR_COLORS = [color.green, color.blue, color.rgb(0.5,0,0.5), color.red, color.rgb(1,0.5,0), color.cyan, color.yellow, color.rgb(1,0,1), color.white]
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