from ursina import Entity, Vec3, color, Texture
import random, math, os

# Perlin permutation
_perm = list(range(256))
random.seed(0)
random.shuffle(_perm)
_perm += _perm

def _fade(t): return t*t*t*(t*(t*6-15)+10)
def _lerp(a,b,t): return a + t*(b-a)
def _grad(hash,x,y):
    h = hash & 3
    return [x+y, -x+y, x-y, -x-y][h]

def perlin2(x,y):
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = _fade(xf); v = _fade(yf)
    aa = _perm[_perm[X]+Y]; ab = _perm[_perm[X]+Y+1]
    ba = _perm[_perm[X+1]+Y]; bb = _perm[_perm[X+1]+Y+1]
    x1 = _lerp(_grad(aa,xf,yf), _grad(ba,xf-1,yf), u)
    x2 = _lerp(_grad(ab,xf,yf-1), _grad(bb,xf-1,yf-1), u)
    return _lerp(x1,x2,v)

def perlin2_octaves(x,y,octaves=4,persistence=0.5,lacunarity=2.0):
    total=0; freq=1; amp=1; maxv=0
    for _ in range(octaves):
        total += perlin2(x*freq,y*freq)*amp
        maxv += amp; amp *= persistence; freq *= lacunarity
    return total/maxv

# ---------------------------
# Ustawienia terenu — POWIĘKSZONE
TERRAIN_SIZE = 64  # zwiększone z 32 na 64 (2x większy świat)
SCALE = 10.0
MAX_HEIGHT = 12  # zwiększone z 8 na 12 (wyższe góry)
BLOCK_SCALE = 1

# Storage
blocks = {}
world_parent = Entity()

# Ładowanie tekstur (jeśli dostępne)
TEXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "textures")

def get_texture(name):
    """Zwróć teksturę jeśli istnieje, inaczej None."""
    path = os.path.join(TEXTURE_DIR, f"{name}.png")
    if os.path.exists(path):
        return Texture(path)
    return None

# Cache tekstur
texture_cache = {
    'grass': get_texture('grass'),
    'dirt': get_texture('dirt'),
    'stone': get_texture('stone'),
    'sand': get_texture('sand'),
    'wood': get_texture('wood'),
}

# Warstwy terenu i ich kolory
BLOCK_SHADES = [
    color.rgb(0,0.5,0),    # zielona trawa
    color.rgb(0.4,0.3,0),  # brązowa gleba
    color.rgb(0.6,0.6,0.6), # szara skała
    color.rgb(1,0.8,0.4),  # piaskowy
]

def spawn_block(pos, shade_idx=None, height=0):
    """
    Tworzy blok — now: obsługuje tekstury i warstwy.
    height: wysokość bloku (do wyboru tekstury)
    """
    if pos in blocks: return
    x,y,z = pos
    if shade_idx is None:
        color_to_use = random.choice(BLOCK_SHADES)
        texture = None
    else:
        HOTBAR_COLORS = [
            color.green, color.blue, color.rgb(0.5,0,0.5),
            color.red, color.rgb(1,0.5,0), color.cyan,
            color.yellow, color.rgb(1,0,1), color.white
        ]
        color_to_use = HOTBAR_COLORS[shade_idx % len(HOTBAR_COLORS)]
        texture = None
    
    # Wybierz teksturę na podstawie wysokości
    if height is None or height < 0:
        texture = texture_cache.get('sand')
        if not texture:
            color_to_use = color.rgb(1,0.8,0.4)
    elif height < 3:
        texture = texture_cache.get('dirt')
        if not texture:
            color_to_use = color.rgb(0.4,0.3,0)
    elif height < 8:
        texture = texture_cache.get('grass')
        if not texture:
            color_to_use = color.rgb(0,0.5,0)
    else:
        texture = texture_cache.get('stone')
        if not texture:
            color_to_use = color.rgb(0.6,0.6,0.6)
    
    e = Entity(model='cube', scale=BLOCK_SCALE, position=Vec3(x,y,z),
               color=color_to_use, texture=texture, parent=world_parent, collider='box')
    blocks[pos] = e
    return e

def remove_block(pos):
    if pos in blocks:
        from ursina import destroy
        destroy(blocks[pos])
        del blocks[pos]

def generate_terrain(terrain_type="Natural"):
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
                spawn_block((x-TERRAIN_SIZE//2,y,z-TERRAIN_SIZE//2), height=y)