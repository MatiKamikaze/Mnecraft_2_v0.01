from ursina import Entity, Vec3, color
import random, math

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

# Settings / storage
TERRAIN_SIZE = 32
SCALE = 10.0
MAX_HEIGHT = 8
BLOCK_SCALE = 1

blocks = {}
world_parent = Entity()
BLOCK_SHADES = [color.rgb(0,0.5,0), color.rgb(0,0.6,0), color.rgb(0,0.7,0), color.rgb(0,0.8,0)]

def spawn_block(pos, shade_idx=None):
    if pos in blocks: return
    x,y,z = pos
    if shade_idx is None:
        color_to_use = random.choice(BLOCK_SHADES)
    else:
        HOTBAR_COLORS = [color.green,color.blue,color.rgb(0.5,0,0.5),color.red,color.rgb(1,0.5,0),color.cyan,color.yellow,color.rgb(1,0,1),color.white]
        color_to_use = HOTBAR_COLORS[shade_idx % len(HOTBAR_COLORS)]
    e = Entity(model='cube', scale=BLOCK_SCALE, position=Vec3(x,y,z), color=color_to_use, parent=world_parent, collider='box')
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
            nx = x/SCALE; nz = z/SCALE
            if terrain_type == "Natural":
                h = perlin2_octaves(nx,nz); h = (h+1)/2
                height = max(1, int(h*MAX_HEIGHT))
            else:
                height = 3
            for y in range(height):
                spawn_block((x-TERRAIN_SIZE//2, y, z-TERRAIN_SIZE//2))