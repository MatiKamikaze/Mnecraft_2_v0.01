"""
Moduł enemy.py: Wrogowie (Botowie) z AI.
- ściganie gracza jeśli blisko
- losowy ruch jeśli daleko
- system zdrowia (HP)
- atak na gracza
"""
from ursina import Entity, Vec3, color, distance, time
import random, math

class Enemy:
    def __init__(self, pos, player_entity, enemy_id=0):
        """
        Tworzy wroga.
        - pos: tuple (x,y,z) startowa pozycja
        - player_entity: Entity gracza do ścigania
        - enemy_id: unikalny ID
        """
        self.id = enemy_id
        self.player = player_entity
        
        # Fiyka i HP
        self.entity = Entity(model='cube', scale=0.8, position=Vec3(*pos), 
                            color=color.red, collider='box')
        self.hp = 20  # punkty zdrowia
        self.max_hp = 20
        
        # AI
        self.speed = 3.0
        self.chase_distance = 20.0  # dystans na którym zaczyna ścigać
        self.attack_distance = 2.0  # dystans do ataku
        self.attack_cooldown = 1.0  # sekund między atakami
        self.last_attack_time = 0
        
        # Losowy ruch jeśli daleko
        self.wander_time = random.uniform(2, 5)
        self.wander_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.wander_timer = 0
        
        # Healthbar (wizualna)
        self.healthbar = Entity(parent=self.entity, model='quad', scale=(0.9, 0.1, 0.1), 
                               position=(0, 0.6, 0), color=color.green)

    def update(self, dt):
        """Aktualizuj AI wroga co klatkę."""
        if self.hp <= 0:
            return  # martwy
        
        # Dystans do gracza
        player_pos = self.player.position
        dist = distance(self.entity.position, player_pos)
        
        # Ściganie lub losowy ruch
        if dist < self.chase_distance:
            # Chase: poruszaj się w kierunku gracza
            direction = (player_pos - self.entity.position).normalized()
            self.entity.position += direction * self.speed * dt
            
            # Atak jeśli blisko
            if dist < self.attack_distance:
                self.attack()
        else:
            # Wander: losowy ruch
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.wander_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
                self.wander_timer = self.wander_time
            
            self.entity.position += self.wander_direction * self.speed * 0.3 * dt
        
        # Cooldown ataku
        self.last_attack_time -= dt
        
        # Aktualizuj healthbar
        health_ratio = max(0, self.hp / self.max_hp)
        self.healthbar.scale = (0.9 * health_ratio, 0.1, 0.1)
        self.healthbar.color = color.interpolate(color.red, color.green, health_ratio)

    def attack(self):
        """Atak na gracza (jeśli cooldown minął)."""
        if self.last_attack_time <= 0:
            # Zadaj obrażenia graczowi (importujemy player module do tego)
            # TO BĘDZIE POŁĄCZONE W game/player.py
            self.last_attack_time = self.attack_cooldown

    def take_damage(self, damage):
        """Weź obrażenia."""
        self.hp -= damage
        if self.hp <= 0:
            self.die()

    def die(self):
        """Śmierć wroga."""
        from ursina import destroy
        destroy(self.entity)
        self.entity = None


class EnemyManager:
    def __init__(self, player_entity, spawn_distance=25.0):
        """
        Manager wrogów.
        - player_entity: Entity gracza
        - spawn_distance: dystans od gracza do spawnu wrogów
        """
        self.player = player_entity
        self.enemies = []
        self.spawn_distance = spawn_distance
        self.spawn_timer = 0
        self.spawn_interval = 10.0  # co 10 sekund próbuj spawować wroga
        self.max_enemies = 5  # max wrogów na mapie

    def update(self, dt):
        """Aktualizuj wszystkich wrogów."""
        # Aktualizuj każdego wroga
        for enemy in list(self.enemies):
            if enemy.entity is None:
                self.enemies.remove(enemy)
            else:
                enemy.update(dt)
        
        # Spawn nowych wrogów
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.enemies) < self.max_enemies:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_interval

    def spawn_enemy(self):
        """Spawn wroga w losowej pozycji wokół gracza."""
        player_pos = self.player.position
        angle = random.uniform(0, 2 * 3.14159)
        x = player_pos.x + math.cos(angle) * self.spawn_distance
        z = player_pos.z + math.sin(angle) * self.spawn_distance
        y = player_pos.y + 2
        
        enemy = Enemy((x, y, z), self.player, enemy_id=len(self.enemies))
        self.enemies.append(enemy)

    def player_attack(self, damage_range=5.0, damage=5):
        """Gracz atakuje — sprawdź czy trafił jakiegoś wroga w zasięgu."""
        from ursina import camera
        player_pos = self.player.position
        attacked = []
        for enemy in self.enemies:
            if enemy.entity is not None:
                dist = distance(player_pos, enemy.entity.position)
                if dist < damage_range:
                    enemy.take_damage(damage)
                    attacked.append(enemy.id)
        return attacked
