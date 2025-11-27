from ursina import Ursina, window, Sky

app = Ursina()
window.title = "Minecraft 2 - Ursina"
window.exit_button.visible = False

from game import terrain, player, ui  # modular game parts

# setup UI and wire modules together
ui.setup_ui(terrain=terrain, player=player, styles_module=None)

# expose ui handlers so Ursina calls them from main module
input = ui.input
update = ui.update

Sky(color=player.color_sky if hasattr(player, 'color_sky') else (0,0.5,1))
app.run()