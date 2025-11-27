import json
from . import terrain

def _color_to_tuple(col):
    # ursina Color has .r .g .b attributes in 0..1
    try:
        return (col.r, col.g, col.b)
    except Exception:
        return (1.0, 1.0, 1.0)

def _tuple_to_color(t):
    from ursina import color
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
    # clear existing
    for pos in list(terrain.blocks.keys()):
        terrain.remove_block(pos)
    for b in obj.get('blocks', []):
        pos = tuple(b['pos'])
        col = b.get('color', (0,1,0))
        # spawn_block currently picks color by index or random; spawn and override color
        ent = terrain.spawn_block(pos)
        try:
            ent.color = _tuple_to_color(col)
        except Exception:
            pass
    return True
