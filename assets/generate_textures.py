"""
Generator prostych tekstur (PNG) do assets/textures/.
Uruchom raz aby wygenerować podstawowe tekstury dla bloków i wrogów.
"""
import os
from PIL import Image, ImageDraw
import random

TEXTURES_DIR = os.path.join(os.path.dirname(__file__), "textures")
os.makedirs(TEXTURES_DIR, exist_ok=True)

# Helper do losowego szumu
def noise_pattern(size, scale=1):
    img = Image.new('RGB', (size, size), 'white')
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            val = random.randint(0, 255)
            pixels[x, y] = (val, val, val)
    return img

def create_grass_texture(size=64):
    # Zielona trawa z szumem
    img = Image.new('RGB', (size, size), (34, 139, 34))
    draw = ImageDraw.Draw(img)
    for _ in range(100):
        x = random.randint(0, size)
        y = random.randint(0, size)
        col = random.randint(20, 150)
        draw.point((x, y), fill=(col, 139+col//2, col))
    img.save(os.path.join(TEXTURES_DIR, "grass.png"))
    print("[OK] grass.png")

def create_dirt_texture(size=64):
    # Brązowa gleba
    img = Image.new('RGB', (size, size), (101, 67, 33))
    draw = ImageDraw.Draw(img)
    for _ in range(150):
        x = random.randint(0, size)
        y = random.randint(0, size)
        col = random.randint(50, 100)
        draw.point((x, y), fill=(101+col//2, 67+col//3, 33+col//4))
    img.save(os.path.join(TEXTURES_DIR, "dirt.png"))
    print("[OK] dirt.png")

def create_stone_texture(size=64):
    # Szara skała
    img = Image.new('RGB', (size, size), (128, 128, 128))
    draw = ImageDraw.Draw(img)
    for _ in range(200):
        x = random.randint(0, size)
        y = random.randint(0, size)
        col = random.randint(30, 80)
        draw.point((x, y), fill=(128+col, 128+col, 128+col))
    img.save(os.path.join(TEXTURES_DIR, "stone.png"))
    print("[OK] stone.png")

def create_sand_texture(size=64):
    # Piaskowy kolor
    img = Image.new('RGB', (size, size), (238, 214, 175))
    draw = ImageDraw.Draw(img)
    for _ in range(150):
        x = random.randint(0, size)
        y = random.randint(0, size)
        col = random.randint(-20, 20)
        draw.point((x, y), fill=(238+col, 214+col, 175+col))
    img.save(os.path.join(TEXTURES_DIR, "sand.png"))
    print("[OK] sand.png")

def create_wood_texture(size=64):
    # Brązowe drewno
    img = Image.new('RGB', (size, size), (139, 69, 19))
    draw = ImageDraw.Draw(img)
    for _ in range(120):
        x = random.randint(0, size)
        y = random.randint(0, size)
        col = random.randint(20, 60)
        draw.point((x, y), fill=(139+col, 69+col, 19+col))
    img.save(os.path.join(TEXTURES_DIR, "wood.png"))
    print("[OK] wood.png")

def create_enemy_texture(size=32):
    # Czerwony wróg (prosty kwadrat)
    img = Image.new('RGB', (size, size), (200, 30, 30))
    draw = ImageDraw.Draw(img)
    # oczy
    draw.ellipse([5, 5, 15, 15], fill='white')
    draw.ellipse([18, 5, 28, 15], fill='white')
    img.save(os.path.join(TEXTURES_DIR, "enemy.png"))
    print("[OK] enemy.png")

def create_healthbar_texture(size=16):
    # Zielony healthbar
    img = Image.new('RGBA', (size, size), (0, 255, 0, 255))
    img.save(os.path.join(TEXTURES_DIR, "healthbar.png"))
    print("[OK] healthbar.png")

if __name__ == "__main__":
    print("Generuję tekstury...")
    create_grass_texture()
    create_dirt_texture()
    create_stone_texture()
    create_sand_texture()
    create_wood_texture()
    create_enemy_texture()
    create_healthbar_texture()
    print("[OK] Wszystkie tekstury wygenerowane w assets/textures/")
