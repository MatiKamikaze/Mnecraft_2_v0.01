# Projekt: Minecraft_2_Ursina — zannotowany przegląd plików
Krótki opis: Projekt podzielony na moduły: game/terrain.py, game/player.py, game/ui.py, game/chunks.py, game/save.py, plus main.py, assets i narzędzia CI. Ten plik zawiera skomentowane wersje plików które powinieneś dodać do repo.

Instrukcja uruchomienia:
1. Zainstaluj zależności: pip install -r requirements.txt
2. Uruchom: python main.py

---


## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\main.py

Punkt wejścia aplikacji. Inicjalizuje Ursina i podłącza moduły.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\main.py
from ursina import Ursina, window, Sky

# Tworzymy aplikację Ursina — musi być przed utworzeniem niektórych obiektów UI/entitów.
app = Ursina()
window.title = "Minecraft 2 - Ursina"
window.exit_button.visible = False

# Importujemy moduły z katalogu game (moduły zakładają, że app istnieje)
# ...existing code...
from game import terrain, player, ui  # moduły: terrain, player, ui

# Inicjalizacja UI i powiązań między modułami.
# Funkcja setup_ui ustawia UI i rejestruje input/update w module ui.
ui.setup_ui(terrain=terrain, player=player, styles_module=None)

# Ursina wywołuje globalne funkcje input/update z miejsca, w którym uruchamiany jest app.run.
# Mapujemy je tutaj na funkcje modułu ui.
input = ui.input
update = ui.update

# Tworzymy niebo — kolor pobieramy z player.color_sky (eksportowane w player.py)
Sky(color=player.color_sky)

# Uruchamiamy pętlę gry.
app.run()
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\__init__.py

Ułatwia importy.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\__init__.py
# ...existing code...
from . import terrain, player, ui, chunks, save

__all__ = ["terrain", "player", "ui", "chunks", "save"]
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\terrain.py

Perlin, definicje bloczków, spawn/remove, oraz generate_terrain. Komentarze tłumaczą co robią funkcje i gdzie rozwijać (np. textury).

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\terrain.py
from ursina import Entity, Vec3, color
import random, math

# Permutacja dla Perlin noise — ta sama permutacja przy starcie daje deterministyczne wyniki.
_perm = list(range(256))
random.seed(0)  # stałe ziarno dla powtarzalności terenu
random.shuffle(_perm)
_perm += _perm

# Fade, lerp i grad to standardowe pomocnicze funkcje Perlin'a.
def _fade(t): return t*t*t*(t*(t*6-15)+10)
def _lerp(a,b,t): return a + t*(b-a)
def _grad(hash,x,y):
    h = hash & 3
    # wybieramy jedną z 4 możliwych kombinacji do gradientu
    return [x+y, -x+y, x-y, -x-y][h]

def perlin2(x,y):
    # ...existing code...
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = _fade(xf)
    v = _fade(yf)
    aa = _perm[_perm[X]+Y]
    ab = _perm[_perm[X]+Y+1]
    ba = _perm[_perm[X+1]+Y]
    bb = _perm[_perm[X+1]+Y+1]
    x1 = _lerp(_grad(aa,xf,yf), _grad(ba,xf-1,yf), u)
    x2 = _lerp(_grad(ab,xf,yf-1), _grad(bb,xf-1,yf-1), u)
    return _lerp(x1,x2,v)

def perlin2_octaves(x,y,octaves=4,persistence=0.5,lacunarity=2.0):
    # Mieszanie oktaw daje bardziej interesujący teren.
    total = 0
    frequency = 1
    amplitude = 1
    max_value = 0
    for _ in range(octaves):
        total += perlin2(x*frequency, y*frequency)*amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total/max_value

# ---------------------------
# Ustawienia terenu i storage bloczków
TERRAIN_SIZE = 32
SCALE = 10.0
MAX_HEIGHT = 8
BLOCK_SCALE = 1

# Słownik pozycji -> Entity dla szybkiego dostępu i usuwania
blocks = {}
world_parent = Entity()  # parent dla wszystkich bloków (łatwiejsze ignorowanie kolizji i grupowanie)
BLOCK_SHADES = [color.rgb(0,0.5,0), color.rgb(0,0.6,0), color.rgb(0,0.7,0), color.rgb(0,0.8,0)]

def spawn_block(pos, shade_idx=None):
    # Tworzy blok w pozycji pos jeśli go jeszcze nie ma.
    if pos in blocks: return
    x,y,z = pos
    if shade_idx is None:
        color_to_use = random.choice(BLOCK_SHADES)
    else:
        # Jeśli podano indeks z hotbar, mapujemy na kolor
        HOTBAR_COLORS = [
            color.green, color.blue, color.rgb(0.5,0,0.5),
            color.red, color.rgb(1,0.5,0), color.cyan,
            color.yellow, color.rgb(1,0,1), color.white
        ]
        color_to_use = HOTBAR_COLORS[shade_idx % len(HOTBAR_COLORS)]
    e = Entity(model='cube', scale=BLOCK_SCALE, position=Vec3(x,y,z),
               color=color_to_use, parent=world_parent, collider='box')
    blocks[pos] = e
    return e

def remove_block(pos):
    # Usuń blok jeśli istnieje.
    if pos in blocks:
        from ursina import destroy
        destroy(blocks[pos])
        del blocks[pos]

def generate_terrain(terrain_type="Natural"):
    # Generuje prosty terrain w obrębie TERRAIN_SIZE x TERRAIN_SIZE.
    global blocks
    blocks = {}
    world_parent.enabled = True
    for x in range(TERRAIN_SIZE):
        for z in range(TERRAIN_SIZE):
            nx = x/SCALE
            nz = z/SCALE
            if terrain_type == "Natural":
                h = perlin2_octaves(nx,nz)
                h = (h+1)/2
                height = max(1,int(h*MAX_HEIGHT))
            else:
                height = 3
            for y in range(height):
                # Pozycjonujemy środek planszy tak, by świat był centrowany na (0,0)
                spawn_block((x-TERRAIN_SIZE//2,y,z-TERRAIN_SIZE//2))
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\player.py

Kontroler gracza i obiekty UI powiązane z graczem. Komentarze opisują API które eksportujemy.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\player.py
from ursina import camera, Entity, Text, Vec3, color, raycast
from ursina.prefabs.first_person_controller import FirstPersonController

# Inicjalizacja kontrolera pierwszoosobowego.
player = FirstPersonController()
player.gravity = 0.3
player.cursor.visible = False
player.speed = 5
player.enabled = False  # zostanie włączony po starcie gry z menu

# Kolor nieba eksportowany do main.py
color_sky = color.blue

# Prosty crosshair i tekst wybranego slotu w UI
crosshair = Text('|', origin=(0,0), scale=2, position=(0,0))
selected_text = Text('Selected: 1', parent=camera.ui, position=(-0.85,0.45), scale=1.2)

# Highlight (przezroczysty żółty sześcian), pokazuje obecnie celowany blok
highlight = Entity(model='cube', color=color.rgba(1,1,0,0.3),
                   scale=Vec3(1.05,1.05,1.05), collider=None, enabled=False)

def get_hit(ignore_list=None, traverse_target=None):
    # Wykonuje raycast z kamery w przód i zwraca wynik.
    ig = [player]
    if ignore_list:
        ig += ignore_list
    return raycast(camera.world_position, camera.forward, distance=8, ignore=ig, traverse_target=traverse_target)

# Hotbar: kolory, sloty UI i wybrany index
HOTBAR_COLORS = [
    color.green, color.blue, color.rgb(0.5,0,0.5),
    color.red, color.rgb(1,0.5,0), color.cyan,
    color.yellow, color.rgb(1,0,1), color.white
]
hotbar_slots = []
selected_slot = 0

def select_slot(index):
    # Zmienia wybrany slot: aktualizuje kolor poprzedniego i nowego slotu.
    global selected_slot
    if 0 <= index < len(hotbar_slots):
        try:
            hotbar_slots[selected_slot].color = color.gray
            selected_slot = index
            hotbar_slots[selected_slot].color = color.orange
        except Exception:
            # Jeśli UI jeszcze nie jest stworzony, ustaw tylko index.
            selected_slot = index
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\ui.py

Obsługa menu startowego, ESC overlay, hotbar oraz funkcje input/update wywoływane przez Ursina.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\ui.py
from ursina import Button, Entity, color, mouse, camera, application, Text

# Flaga pauzy globalna w module UI
paused = False

def setup_ui(terrain, player, styles_module=None):
    """
    Inicjalizuje wszystkie elementy UI: hotbar, menu, ESC overlay.
    - terrain: moduł terrain (referencja)
    - player: moduł player (referencja)
    - styles_module: opcjonalny moduł z kolorami/stylami
    """
    # --- HOTBAR UI ---
    for i, col in enumerate(player.HOTBAR_COLORS):
        slot = Button(parent=camera.ui, model='quad', color=color.gray, highlight_color=color.light_gray,
                      scale=(0.07,0.07), x=-0.3 + i*0.07, y=-0.45)
        # Wstawiamy mały cube jako podgląd bloku w slocie
        Entity(parent=slot, model='cube', scale=(0.8,0.8,0.8), color=col)
        player.hotbar_slots.append(slot)
    try:
        player.hotbar_slots[player.selected_slot].color = color.orange
    except Exception:
        pass  # UI jeszcze nie w pełni zainicjalizowane

    # --- ESC overlay ---
    global esc_overlay
    esc_overlay = Entity(parent=camera.ui, enabled=False)
    Entity(parent=esc_overlay, model='quad', scale=(2,2), color=color.rgba(0,0,0,0.6))
    resume_button = Button(text='Resume', parent=esc_overlay, scale=(0.2,0.1), y=0.1, color=color.azure)
    quit_button = Button(text='Quit', parent=esc_overlay, scale=(0.2,0.1), y=-0.1, color=color.red)
    resume_button.on_click = lambda: toggle_pause()
    quit_button.on_click = application.quit

    # --- Pre-game menu (Flat/Natural) ---
    menu_overlay = Entity(parent=camera.ui)
    Entity(parent=menu_overlay, model='quad', scale=(2,2), color=color.rgba(0,0,0,0.7))
    flat_button = Button(text='Flat', scale=(0.3,0.1), y=0.1, parent=menu_overlay, color=color.azure)
    natural_button = Button(text='Natural', scale=(0.3,0.1), y=-0.1, parent=menu_overlay, color=color.green)

    mouse.locked = False  # odblokuj kursor gdy jesteśmy w menu

    def start(terrain_type):
        # Rozpoczynamy grę: generujemy teren i ustawiamy pozycję gracza.
        menu_overlay.enabled = False
        terrain.generate_terrain(terrain_type)
        player.player.position = (0, terrain.MAX_HEIGHT+5, -terrain.TERRAIN_SIZE//2)
        player.player.enabled = True
        mouse.locked = True

    flat_button.on_click = lambda: start("Flat")
    natural_button.on_click = lambda: start("Natural")

# --- Funkcje input/update wywoływane przez Ursina z globalnego scope ---
def input(key):
    # Funkcja powinna być przypisana do globalnego input w main.py: input = ui.input
    from game import terrain, player
    global paused
    if key == 'escape':
        toggle_pause()
    if paused or not player.player.enabled:
        return

    # Hotbar: klawisze 1-9 oraz scroll
    if key in list('123456789'):
        player.select_slot(int(key)-1)
    if key == 'scroll up': player.select_slot((player.selected_slot+1)%len(player.hotbar_slots))
    if key == 'scroll down': player.select_slot((player.selected_slot-1)%len(player.hotbar_slots))

    # Break (lewy przycisk myszy)
    if key == 'left mouse down':
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit:
            pos = hit.entity.position
            terrain.remove_block((int(round(pos.x)), int(round(pos.y)), int(round(pos.z))))
    # Place (prawy przycisk myszy)
    if key == 'right mouse down':
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit:
            pos = hit.entity.position
            normal = hit.normal
            place_pos = (int(round(pos.x+normal.x)), int(round(pos.y+normal.y)), int(round(pos.z+normal.z)))
            player_pos = (int(round(player.player.x)), int(round(player.player.y)), int(round(player.player.z)))
            if place_pos != player_pos:
                terrain.spawn_block(place_pos, shade_idx=player.selected_slot)

def update():
    # Aktualizacje per-frame: podświetlenie bloku i tekst wybranego slotu.
    from game import terrain, player
    if player.player.enabled:
        player.selected_text.text = f'Selected: {player.selected_slot+1}'
        hit = player.get_hit(traverse_target=terrain.world_parent)
        if hit.hit and hit.entity in terrain.blocks.values():
            player.highlight.position = hit.entity.position
            player.highlight.enabled = True
        else:
            player.highlight.enabled = False

def toggle_pause():
    # Przełącz pauzę i blokadę myszy.
    global paused, esc_overlay
    paused = not paused
    esc_overlay.enabled = paused
    mouse.locked = not paused
    application.paused = paused
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\chunks.py

Manager chunków — pozwala składać świat z kawałków (ułatwia ładowanie i optymalizację).

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\chunks.py
import math
from . import terrain

CHUNK_SIZE = 16
VIEW_DISTANCE = 2  # w chunkach; zwiększ, aby załadować dalej widoczny teren

def chunk_coords_from_world(x, z):
    cx = math.floor(x / CHUNK_SIZE)
    cz = math.floor(z / CHUNK_SIZE)
    return cx, cz

class ChunkManager:
    def __init__(self):
        # mapping (cx,cz) -> set of położeń bloków wczytanych dla tego chunka
        self.loaded = {}

    def generate_chunk(self, cx, cz, terrain_type="Natural"):
        key = (cx, cz)
        if key in self.loaded:
            return
        positions = set()
        x0 = cx * CHUNK_SIZE
        z0 = cz * CHUNK_SIZE
        for x in range(x0, x0 + CHUNK_SIZE):
            for z in range(z0, z0 + CHUNK_SIZE):
                nx = x / terrain.SCALE
                nz = z / terrain.SCALE
                if terrain_type == "Natural":
                    h = terrain.perlin2_octaves(nx, nz)
                    h = (h + 1) / 2
                    height = max(1, int(h * terrain.MAX_HEIGHT))
                else:
                    height = 3
                for y in range(height):
                    pos = (x - terrain.TERRAIN_SIZE//2, y, z - terrain.TERRAIN_SIZE//2)
                    terrain.spawn_block(pos)
                    positions.add(pos)
        self.loaded[key] = positions

    def unload_chunk(self, cx, cz):
        key = (cx, cz)
        if key not in self.loaded:
            return
        for pos in list(self.loaded[key]):
            terrain.remove_block(pos)
        del self.loaded[key]

    def update(self, player_position, terrain_type="Natural"):
        # Wywołuj tę funkcję okresowo (np. w update()) by ładować/zwalniać chunky
        px, pz = player_position[0], player_position[2]
        pcx, pcz = chunk_coords_from_world(px, pz)
        desired = set()
        for dx in range(-VIEW_DISTANCE, VIEW_DISTANCE+1):
            for dz in range(-VIEW_DISTANCE, VIEW_DISTANCE+1):
                desired.add((pcx+dx, pcz+dz))
        # Load missing
        for key in desired:
            if key not in self.loaded:
                self.generate_chunk(key[0], key[1], terrain_type=terrain_type)
        # Unload far chunks
        for key in list(self.loaded.keys()):
            if key not in desired:
                self.unload_chunk(key[0], key[1])
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\save.py

Proste zapisywanie/ładowanie świata do JSON. Przydatne do testów i dalszego rozwoju.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\save.py
import json
from . import terrain

def _color_to_tuple(col):
    # Ursina Color ma r,g,b w zakresie 0..1 — konwertujemy na tuple
    try:
        return (col.r, col.g, col.b)
    except Exception:
        return (1.0, 1.0, 1.0)

def _tuple_to_color(t):
    from ursina import color
    # Uwaga: jeśli wartości są 0..1, można użyć color.rgb(...*255) lub color.tint
    return color.rgb(t[0], t[1], t[2])

def save_world(path):
    data = []
    for pos, ent in terrain.blocks.items():
        col = _color_to_tuple(ent.color)
        data.append({'pos': pos, 'color': col})
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'blocks': data}, f)
    return True

def load_world(path):
    with open(path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    # Usuń bieżące bloki
    for pos in list(terrain.blocks.keys()):
        terrain.remove_block(pos)
    # Wczytaj zapisane bloki
    for b in obj.get('blocks', []):
        pos = tuple(b['pos'])
        col = b.get('color', (0,1,0))
        ent = terrain.spawn_block(pos)
        try:
            ent.color = _tuple_to_color(col)
        except Exception:
            pass
    return True
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\config.py

Centralny plik konfiguracyjny projektu.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\config.py
PROJECT_NAME = "Minecraft_2_Ursina"
VERSION = "0.1.0"
AUTHOR = "You"

# Game defaults (możesz nadpisać w runtime)
DEFAULT_TERRAIN_SIZE = 32
DEFAULT_MAX_HEIGHT = 8

# Ścieżki
SAVE_DIR = "saves"
DEFAULT_SAVE_FILE = SAVE_DIR + "/world.json"
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\assets\styles.py

Prosty moduł z paletą kolorów i stylem UI — używaj zamiast hardcodowanych kolorów.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\assets\styles.py
from ursina import color

UI = {
    'bg_overlay': color.rgba(0,0,0,0.7),
    'menu_button': color.azure,
    'hotbar_slot': color.gray,
    'hotbar_selected': color.orange
}
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\requirements.txt

Wymagania.

````text
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\requirements.txt
ursina>=0.7.0
pytest
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\README.md

Krótka instrukcja i roadmap.

````text
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\README.md
Minecraft 2 - Ursina (annotated)

Run:
1. pip install -r requirements.txt
2. python main.py

Roadmap:
- chunking (done basic)
- save/load (done)
- async chunk generation
- textures & asset pipeline
- unit tests for perlin/terrain
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\.gitignore

Standardowe ignorowane pliki.

````text
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\.gitignore
__pycache__/
*.pyc
.env/
.vscode/
.idea/
.DS_Store
dist/
build/
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\.github\workflows\python-app.yml

Prosty CI: instaluje zależności i uruchamia pytest.

````yaml
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\.github\workflows\python-app.yml
name: Python package

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Run tests
        run: |
          pip install pytest
          pytest -q
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\tests\test_imports.py

Prosty test, czy moduły importują się poprawnie.

````python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\tests\test_imports.py
def test_imports():
    import importlib
    importlib.import_module('game.terrain')
    importlib.import_module('game.player')
    importlib.import_module('game.ui')
    importlib.import_module('game.chunks')
    importlib.import_module('game.save')
    assert True
````

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\run_game.bat

Opis: skrypt uruchamiający grę w Windowsie. Automatycznie tworzy venv, instaluje zależności i uruchamia grę. Przydatne do szybkiego startu.

```bat
REM filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\run_game.bat
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

title Minecraft_2_Ursina - Launcher
color 0A

echo.
echo ======================================
echo  Minecraft_2_Ursina - Game Launcher
echo ======================================
echo.

REM --- Sprawdzenie czy Python jest zainstalowany ---
echo Sprawdzam czy Python jest zainstalowany...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [BLAD] Python nie znaleziony w PATH!
    echo Zainstaluj Python 3.8+ ze strony https://www.python.org/
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Python znaleziony.
    python --version
    echo.
)

REM --- Sprawdzenie czy requirements.txt istnieje ---
if not exist "requirements.txt" (
    color 0C
    echo [BLAD] requirements.txt nie znaleziony!
    echo Upewnij sie ze jestes w katalogu projektu.
    echo.
    pause
    exit /b 1
)
echo [OK] requirements.txt znaleziony.
echo.

REM --- Tworzenie/aktywacja venv ---
echo Krok 1: Sprawdzam wirtualne srodowisko (venv)...
if exist "venv\Scripts\activate.bat" (
    echo [OK] venv juz istnieje. Aktywuję...
    call "venv\Scripts\activate.bat"
    if errorlevel 1 (
        color 0C
        echo [BLAD] Nie udalo sie aktywowac venv.
        pause
        exit /b 1
    )
    echo [OK] venv aktywowany.
) else (
    echo [INFO] venv nie istnieje. Tworzę nowy (moze zajac 10-30 sekund)...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo [BLAD] Nie udalo sie utworzyc venv.
        pause
        exit /b 1
    )
    echo [OK] venv utworzony. Aktywuję...
    call "venv\Scripts\activate.bat"
    if errorlevel 1 (
        color 0C
        echo [BLAD] Nie udalo sie aktywowac venv.
        pause
        exit /b 1
    )
    echo [OK] venv aktywowany.
)
echo.

REM --- Instalacja zaleznosci ---
echo Krok 2: Instaluję zaleznosci (moze zajac kilka minut)...
pip install --upgrade pip
if errorlevel 1 (
    color 0C
    echo [BLAD] Nie udalo sie zaktualizowac pip.
    pause
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo [BLAD] Nie udalo sie zainstalowac zaleznosci z requirements.txt.
    echo Sprawdz czy wszystkie pakiety sa dostepne.
    pause
    exit /b 1
)
echo [OK] Zaleznosci zainstalowane.
echo.

REM --- Sprawdzenie czy main.py istnieje ---
if not exist "main.py" (
    color 0C
    echo [BLAD] main.py nie znaleziony!
    echo Upewnij sie ze jestes w katalogu projektu.
    pause
    exit /b 1
)
echo [OK] main.py znaleziony.
echo.

REM --- Uruchomienie gry ---
echo Krok 3: Uruchamiam grę...
echo ======================================
echo.
python main.py
set GAME_EXIT=%ERRORLEVEL%
echo.
echo ======================================

REM --- Wynik uruchomienia ---
if %GAME_EXIT% equ 0 (
    color 0A
    echo [OK] Gra zakonczyla sie bezblednie.
) else (
    color 0C
    echo [BLAD] Gra zakonczyla sie z kodem bledu: %GAME_EXIT%
)
echo.
echo Nacisnij dowolny klawisz aby zamknac okno...
pause >nul

ENDLOCAL
exit /b %GAME_EXIT%
```

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\run_game_simple.bat

Opis: alternatywna wersja bez venv — instaluje pakiety globalnie. Szybka do testów jeśli chcesz uniknąć venv.

```bat
REM filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\run_game_simple.bat
@echo off
title Minecraft_2_Ursina - Simple Launcher
color 0A

echo.
echo ======================================
echo  Minecraft_2_Ursina (Simple - bez venv)
echo ======================================
echo.

echo Sprawdzam Python...
python --version
if errorlevel 1 (
    color 0C
    echo [BLAD] Python nie zainstalowany!
    pause
    exit /b 1
)

echo.
echo Instaluję zaleznosci (bez venv)...
pip install -r requirements.txt --user
if errorlevel 1 (
    color 0C
    echo [BLAD] Instalacja nie powiodła sie.
    pause
    exit /b 1
)

echo.
echo Uruchamiam grę...
echo ======================================
echo.
python main.py
set RESULT=%ERRORLEVEL%
echo.
echo ======================================
echo Gra zakonczyla sie (kod: %RESULT%)
echo Nacisnij dowolny klawisz aby zamknac okno...
pause >nul

ENDLOCAL
exit /b %RESULT%
```

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\enemy.py

Opis: Moduł wrogów z AI — ściganie gracza, atak, HP. Każdy wróg to Entity z logicą ataku i zdrowiem.

```python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\game\enemy.py
# Moduł Enemy — wrogowie, AI, HP, atak

from ursina import Entity, color, Vec3, raycast
from math import sin, cos, radians
import random

# Klasa bazowa dla wrogów
class Enemy(Entity):
    def __init__(self, position=(0,0,0), target=None, **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1,1,1),
            position=position,
            collider='box',
            **kwargs
        )
        self.target = target  # Cel (gracz)
        self.speed = 2  # Prędkość poruszania się
        self.hp = 100  # Punkty życia
        self.attack_damage = 10  # Obrażenia ataku
        self.attack_range = 1.5  # Zasięg ataku
        self.agro_range = 10  # Zasięg dostrzegania gracza
        self.path = []  # Ścieżka do gracza (lista pozycji)
        self.patrol_points = []  # Punkty patrolowe (lista pozycji)
        self.current_patrol_index = 0  # Indeks aktualnego punktu patrolowego

    def update(self):
        # Główna logika wroga: ściganie gracza, atak, patrolowanie
        if self.target:
            distance = self.distance_to(self.target)
            if distance < self.agro_range:
                # Jeśli gracz w zasięgu aggro, ścigaj go
                self.chase_target()
            else:
                # W przeciwnym razie patroluj między punktami
                self.patrol()

    def chase_target(self):
        # Ścigaj cel (gracza)
        direction = (self.target.position - self.position).normalized()
        self.position += direction * self.speed * time.dt
        self.look_at(self.target)  # Obróć się w stronę celu

        # Sprawdź atak
        if self.distance_to(self.target) < self.attack_range:
            self.attack()

    def attack(self):
        # Atakuj cel (zadaj obrażenia)
        if self.target.hp > 0:
            self.target.hp -= self.attack_damage
            print(f'Zaatakowano gracza! Pozostałe HP: {self.target.hp}')

    def patrol(self):
        # Patroluj między punktami
        if not self.patrol_points:
            return
        target_point = self.patrol_points[self.current_patrol_index]
        direction = (target_point - self.position).normalized()
        self.position += direction * self.speed * time.dt
        self.look_at(target_point)  # Obróć się w stronę punktu patrolowego

        # Sprawdź, czy dotarłeś do punktu patrolowego
        if self.distance_to(target_point) < 0.5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

    def set_patrol_points(self, points):
        # Ustaw punkty patrolowe
        self.patrol_points = points

# Przykładowy wróg
enemy = Enemy(position=(5,0,5))
enemy.set_patrol_points([
    Vec3(5,0,5),
    Vec3(10,0,10),
    Vec3(5,0,15),
    Vec3(0,0,10),
])
```

---

## c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\assets\generate_textures.py

Opis: Skrypt generujący proste PNG tekstury. Uruchom raz: `python assets/generate_textures.py`

```python
# filepath: c:\Users\MatiKamikaze\Documents\GitHub\Mnecraft_2_v0.01\assets\generate_textures.py
from PIL import Image
import noise
import numpy as np

# Ustawienia
TEXTURE_SIZE = 16
TERRAIN_TYPES = ['grass', 'dirt', 'stone', 'sand']

def generate_texture(terrain_type):
    # Generuje teksturę w zależności od typu terenu
    if terrain_type == 'grass':
        return generate_grass_texture()
    elif terrain_type == 'dirt':
        return generate_dirt_texture()
    elif terrain_type == 'stone':
        return generate_stone_texture()
    elif terrain_type == 'sand':
        return generate_sand_texture()
    else:
        raise ValueError(f'Nieznany typ terenu: {terrain_type}')

def generate_grass_texture():
    # Przykładowa tekstura trawy (zielony kolor)
    data = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
    data[..., 0] = 34
    data[..., 1] = 139
    data[..., 2] = 34
    return Image.fromarray(data)

def generate_dirt_texture():
    # Przykładowa tekstura brudu (brązowy kolor)
    data = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
    data[..., 0] = 139
    data[..., 1] = 69
    data[..., 2] = 19
    return Image.fromarray(data)

def generate_stone_texture():
    # Przykładowa tekstura kamienia (szary kolor)
    data = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
    data[..., 0] = 169
    data[..., 1] = 169
    data[..., 2] = 169
    return Image.fromarray(data)

def generate_sand_texture():
    # Przykładowa tekstura piasku (żółty kolor)
    data = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
    data[..., 0] = 194
    data[..., 1] = 178
    data[..., 2] = 128
    return Image.fromarray(data)

# Generowanie tekstur dla wszystkich typów terenu
for terrain_type in TERRAIN_TYPES:
    texture = generate_texture(terrain_type)
    texture.save(f'assets/textures/{terrain_type}_texture.png')
    print(f'Wygenerowano teksturę: {terrain_type}_texture.png')
```

---

Koniec pliku ANNOTATED_PROJECT.md

Uwagi końcowe:
- Wklej powyższe sekcje do ANNOTATED_PROJECT.md i obu plików .bat do repo.  
- Jeśli chcesz, mogę wygenerować te pliki bezpośrednio do working set — dodaj pliki do working set lub użyj `#codebase` w następnym żądaniu.  
- Dalsze rekomendacje: dodać asynchroniczne ładowanie chunków, mapę materiałów (tekstury), i system eventów dla zapisu/ładowania.