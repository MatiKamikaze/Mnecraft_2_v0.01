from ursina import Ursina, window, Sky

app = Ursina()
window.title = "Minecraft 2 - Ursina"
window.exit_button.visible = False

from game import terrain, player, ui, chunks
from game.enemy import EnemyManager

# Inicjalizacja UI
ui.setup_ui(terrain=terrain, player=player, styles_module=None)

# Chunk manager — NOWY
chunk_manager = chunks.ChunkManager()
current_terrain_type = "Natural"

# Mapuję input/update
input = ui.input
update_base = ui.update  # zachowaj referencję

def update():
    """Rozszerzony update z chunk loading."""
    update_base()  # uruchom istniejący update z ui
    
    # NOWY: Chunk loading — aktualizuj chunky na podstawie pozycji gracza
    if player.player.enabled:
        chunk_manager.update(player.player.position, terrain_type=current_terrain_type)

# Mapuję nowy update
update = update

Sky(color=player.color_sky if hasattr(player, 'color_sky') else (0,0.5,1))
app.run()