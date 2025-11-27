import math
from . import terrain

CHUNK_SIZE = 16
VIEW_DISTANCE = 3  # zwiększone z 2 na 3 (dalej widoczny teren, ale optymalizacja)

def chunk_coords_from_world(x, z):
    cx = math.floor(x / CHUNK_SIZE)
    cz = math.floor(z / CHUNK_SIZE)
    return cx, cz

class ChunkManager:
    def __init__(self):
        # mapping (cx,cz) -> set of block positions spawned for that chunk
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
                    terrain.spawn_block(pos, height=y)
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
        # player_position is a Vec3 or tuple (x,y,z)
        px, pz = player_position[0], player_position[2]
        pcx, pcz = chunk_coords_from_world(px, pz)
        # ensure view-distance chunks loaded
        desired = set()
        for dx in range(-VIEW_DISTANCE, VIEW_DISTANCE+1):
            for dz in range(-VIEW_DISTANCE, VIEW_DISTANCE+1):
                desired.add((pcx+dx, pcz+dz))
        # load missing
        for key in desired:
            if key not in self.loaded:
                self.generate_chunk(key[0], key[1], terrain_type=terrain_type)
        # unload far chunks
        for key in list(self.loaded.keys()):
            if key not in desired:
                self.unload_chunk(key[0], key[1])

    # helper for saving chunk map (optional)
    def export_loaded_map(self):
        return {f"{cx}_{cz}": list(positions) for (cx,cz), positions in self.loaded.items()}
