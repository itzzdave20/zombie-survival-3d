# world_renderer.py
# Doom-style Enemies, Quests, Loot Boxes, and Particle System

import math
import random
import kivy.clock
from texture import TextureGenerator
from settings import ENEMY_AGGRO_RANGE, ENEMY_ATTACK_RANGE, ENEMY_RADIUS, MAX_PARTICLES, GRAVITY


class Zombie:
    """
    Doom-style enemy with sprite-based rendering and AI.
    Features different zombie types with unique behaviors.
    """

    def __init__(self, x, y, zombie_type="normal"):
        self.x = x
        self.y = y
        self.z = 0
        self.type = zombie_type
        self.alive = True
        self.attack_cooldown = 0
        self.walk_frame = 0
        self.death_time = 0
        self.hit_flash = 0
        self.step_timer = 0
        self.stuck_timer = 0
        self.last_x = x
        self.last_y = y
        self.knockback_x = 0
        self.knockback_y = 0
        self.attack_anim = 0
        self.visible = True
        
        # Reference to game map
        self.game_map = None
        
        # Doom-style enemy stats
        self.stats = {
            "normal": {
                "health": 60,
                "speed": 2.0,
                "damage": 12,
                "color": (0.35, 0.7, 0.35),
                "height": 1.0,
                "pain_chance": 0.5
            },
            "fast": {
                "health": 40,
                "speed": 4.0,
                "damage": 8,
                "color": (0.8, 0.3, 0.3),
                "height": 0.9,
                "pain_chance": 0.3
            },
            "tank": {
                "health": 180,
                "speed": 1.0,
                "damage": 30,
                "color": (0.3, 0.3, 0.7),
                "height": 1.5,
                "pain_chance": 0.2
            },
            "burnt": {
                "health": 80,
                "speed": 2.2,
                "damage": 18,
                "color": (0.6, 0.3, 0.2),
                "height": 1.0,
                "pain_chance": 0.4
            },
            "boss": {
                "health": 600,
                "speed": 0.8,
                "damage": 50,
                "color": (0.2, 0.5, 0.2),
                "height": 2.2,
                "pain_chance": 0.1
            },
            "demon": {
                "health": 100,
                "speed": 3.0,
                "damage": 20,
                "color": (0.7, 0.4, 0.2),
                "height": 1.1,
                "pain_chance": 0.35
            },
            "cacodemon": {
                "health": 120,
                "speed": 2.5,
                "damage": 25,
                "color": (0.8, 0.2, 0.2),
                "height": 1.0,
                "pain_chance": 0.4,
                "flying": True
            }
        }

        stats = self.stats.get(zombie_type, self.stats["normal"])
        self.health = stats["health"]
        self.max_health = self.health
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.color = stats["color"]
        self.height_mult = stats["height"]
        self.pain_chance = stats.get("pain_chance", 0.5)
        self.flying = stats.get("flying", False)
        
        self.aggro_range = ENEMY_AGGRO_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.zombie_size = ENEMY_RADIUS
        
        # Generate texture
        self.tex_gen = TextureGenerator()
        self.texture = self.tex_gen.generate_zombie_texture(32, self.color, zombie_type)
        
        # Animation frames
        self.frame_count = 5
        self.frames_per_second = 8

    def set_map(self, game_map):
        """Set reference to the game map."""
        self.game_map = game_map

    def check_collision(self, x, y):
        """Check if position collides with walls."""
        if self.game_map is None:
            return False
        
        for dx in [-self.zombie_size, 0, self.zombie_size]:
            for dy in [-self.zombie_size, 0, self.zombie_size]:
                check_x = int(x + dx)
                check_y = int(y + dy)
                
                if check_x < 0 or check_y < 0 or check_x >= 32 or check_y >= 32:
                    return True
                if self.game_map[check_y][check_x] > 0:
                    return True
        return False

    def update(self, player_x, player_y, dt, game_map=None):
        """
        Update zombie AI and animation.
        
        Returns True if zombie attacks player.
        """
        if not self.alive:
            self.death_time += dt
            return False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.attack_anim > 0:
            self.attack_anim -= dt

        # Apply knockback decay
        self.x += self.knockback_x * dt
        self.y += self.knockback_y * dt
        self.knockback_x *= 0.8
        self.knockback_y *= 0.8

        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # AI behavior
        if distance < self.aggro_range:
            if distance > self.attack_range:
                # Move towards player
                angle = math.atan2(dy, dx)
                move_speed = self.speed * dt
                
                # Add some randomness to movement (more Doom-like)
                if random.random() < 0.1:
                    angle += random.uniform(-0.3, 0.3)
                
                move_x = math.cos(angle) * move_speed
                move_y = math.sin(angle) * move_speed

                new_x = self.x + move_x
                new_y = self.y + move_y

                # Collision detection with sliding
                can_move_x = not self.check_collision(new_x, self.y)
                can_move_y = not self.check_collision(self.x, new_y)

                moved = False
                if can_move_x and can_move_y:
                    self.x = new_x
                    self.y = new_y
                    moved = True
                elif can_move_x:
                    self.x = new_x
                    moved = True
                elif can_move_y:
                    self.y = new_y
                    moved = True
                else:
                    # Try to find alternative path
                    self.stuck_timer += dt
                    if self.stuck_timer > 0.5:
                        perp_angle = angle + math.pi / 2
                        perp_x = self.x + math.cos(perp_angle) * move_speed * 0.5
                        perp_y = self.y + math.sin(perp_angle) * move_speed * 0.5
                        if not self.check_collision(perp_x, perp_y):
                            self.x = perp_x
                            self.y = perp_y
                        self.stuck_timer = 0
                    else:
                        self.stuck_timer = 0

                # Update animation
                if moved:
                    self.step_timer += dt * self.speed * 2
                    self.walk_frame = math.sin(self.step_timer) * self.frames_per_second
                    self.last_x = self.x
                    self.last_y = self.y

            elif self.attack_cooldown <= 0:
                # Attack player
                self.attack_cooldown = 1.5
                self.attack_anim = 0.3
                return True
        
        return False

    def take_damage(self, damage, headshot=False):
        """
        Apply damage to zombie.
        
        Returns True if zombie died.
        """
        if headshot:
            damage *= 2.5
        
        self.health -= damage
        self.hit_flash = 0.15
        
        # Pain chance check (Doom-style)
        if random.random() < self.pain_chance:
            # Stagger animation
            self.walk_frame = -2
        
        # Knockback
        self.knockback_x = random.uniform(-2, 2)
        self.knockback_y = random.uniform(-2, 2)
        
        if self.health <= 0:
            self.alive = False
            self.death_time = 0
            return True
        return False

    def get_display_size(self, distance):
        """Get display dimensions based on distance."""
        base_height = 120 / max(distance, 0.5) * self.height_mult
        return max(20, base_height), max(10, base_height * 0.55)

    def get_frame_index(self):
        """Get current animation frame index."""
        if not self.alive:
            return min(4, int(self.death_time * 4))  # Death frames
        return int(abs(self.walk_frame)) % self.frame_count


class Quest:
    """Doom-style mission system."""

    def __init__(self, quest_type, description, target, reward_score):
        self.quest_type = quest_type
        self.description = description
        self.target = target
        self.current = 0
        self.reward_score = reward_score
        self.completed = False
        self.time_elapsed = 0

    def update(self, amount=1):
        """Update quest progress."""
        if not self.completed:
            self.current += amount
            if self.current >= self.target:
                self.completed = True
                return True
        return False

    def update_time(self, dt):
        """Update time-based quest."""
        if self.quest_type == "survive":
            self.time_elapsed += dt
            if self.time_elapsed >= self.target:
                self.completed = True
                return True
        return False

    def get_progress(self):
        """Get quest progress as 0-1 value."""
        if self.quest_type == "survive":
            return min(1.0, self.time_elapsed / self.target)
        return min(1.0, self.current / self.target)


class LootBox:
    """Doom-style pickup items."""

    TYPES = {
        "common": {"color": (0.9, 0.7, 0.2), "chance": 60},
        "rare": {"color": (0.2, 0.5, 0.9), "chance": 30},
        "legendary": {"color": (0.8, 0.2, 0.9), "chance": 10},
    }

    def __init__(self, x, y, box_type=None):
        self.x = x
        self.y = y
        self.opened = False
        self.float_offset = random.uniform(0, math.pi * 2)
        self.rotate_angle = 0
        self.bob_height = 0
        self.glow_intensity = 0
        self.pickup_sound_played = False

        if box_type is None:
            roll = random.uniform(0, 100)
            if roll < 10:
                box_type = "legendary"
            elif roll < 40:
                box_type = "rare"
            else:
                box_type = "common"
        self.box_type = box_type
        self.color = self.TYPES[box_type]["color"]
        self.rewards = self._generate_rewards()

    def _generate_rewards(self):
        """Generate rewards based on box type."""
        rewards = []
        tier = {"common": 1, "rare": 2, "legendary": 3}[self.box_type]
        
        if tier >= 1:
            rewards.append(("health", random.randint(15, 35)))
            rewards.append(("ammo", random.randint(10, 25)))
        if tier >= 2:
            rewards.append(("armor", random.randint(20, 40)))
            rewards.append(("score", random.randint(100, 200)))
        if tier >= 3:
            rewards.append(("health", 50))
            rewards.append(("score", random.randint(300, 500)))
        
        return rewards

    def update(self, time):
        """Update box animation."""
        if not self.opened:
            self.float_offset = math.sin(time * 2) * 0.15
            self.rotate_angle = time * 0.5
            self.bob_height = abs(math.sin(time * 3)) * 0.2
            self.glow_intensity = 0.5 + math.sin(time * 4) * 0.2

    def open(self, player, weapon):
        """Open box and apply rewards."""
        if self.opened:
            return []
        self.opened = True
        applied = []
        
        for reward_type, value in self.rewards:
            if reward_type == "health":
                player.heal(value)
                applied.append(f"+{value} Health")
            elif reward_type == "armor":
                player.add_armor(value)
                applied.append(f"+{value} Armor")
            elif reward_type == "ammo":
                weapon.reserve_ammo += value
                applied.append(f"+{value} Ammo")
            elif reward_type == "score":
                player.score += value
                applied.append(f"+{value} Score")
        
        return applied


class ParticleSystem:
    """
    Doom-style particle effects system.
    Supports blood, sparks, smoke, and explosion particles.
    """

    def __init__(self, max_particles=MAX_PARTICLES):
        self.particles = []
        self.max_particles = max_particles
        self.tex_gen = TextureGenerator()

    def emit(self, x, y, z, vx, vy, vz, color, lifetime, count=1, size=5, 
             particle_type='square', gravity=True):
        """
        Emit particles.
        
        Args:
            x, y, z: Starting position
            vx, vy, vz: Velocity
            color: RGB color tuple
            lifetime: Particle lifetime in seconds
            count: Number of particles to emit
            size: Particle size
            particle_type: 'square', 'blood', 'spark', 'smoke'
            gravity: Whether gravity affects particles
        """
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                # Remove oldest particles
                self.particles = self.particles[-self.max_particles+1:]
            
            self.particles.append({
                'x': x + random.uniform(-0.2, 0.2),
                'y': y + random.uniform(-0.2, 0.2),
                'z': z,
                'vx': vx + random.uniform(-1, 1),
                'vy': vy + random.uniform(-1, 1),
                'vz': vz + random.uniform(-0.5, 0.5),
                'color': color,
                'lifetime': lifetime + random.uniform(-0.1, 0.1),
                'max_lifetime': lifetime,
                'size': size + random.uniform(-1, 2),
                'type': particle_type,
                'gravity': gravity,
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-2, 2)
            })

    def emit_blood(self, x, y, z, direction_x, direction_y, amount=15):
        """Emit blood particles."""
        for _ in range(amount):
            if len(self.particles) >= self.max_particles:
                self.particles = self.particles[-self.max_particles+1:]
            
            self.particles.append({
                'x': x + random.uniform(-0.2, 0.2),
                'y': y + random.uniform(-0.2, 0.2),
                'z': z + random.uniform(0, 0.5),
                'vx': direction_x * 3 + random.uniform(-2, 2),
                'vy': direction_y * 3 + random.uniform(-2, 2),
                'vz': random.uniform(1, 4),
                'color': (0.8, 0.1, 0.1),
                'lifetime': 1.5 + random.uniform(-0.3, 0.3),
                'max_lifetime': 1.5,
                'size': 4 + random.uniform(-1, 3),
                'type': 'blood',
                'gravity': True,
                'rotation': 0,
                'rotation_speed': 0
            })

    def emit_sparks(self, x, y, z, amount=10):
        """Emit spark particles."""
        for _ in range(amount):
            if len(self.particles) >= self.max_particles:
                self.particles = self.particles[-self.max_particles+1:]
            
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            
            self.particles.append({
                'x': x,
                'y': y,
                'z': z + random.uniform(0, 0.3),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'vz': random.uniform(1, 3),
                'color': (1.0, 0.8, 0.3),
                'lifetime': 0.5 + random.uniform(-0.1, 0.2),
                'max_lifetime': 0.5,
                'size': 3 + random.uniform(-1, 2),
                'type': 'spark',
                'gravity': True,
                'rotation': 0,
                'rotation_speed': 0
            })

    def emit_smoke(self, x, y, z, amount=8):
        """Emit smoke particles."""
        for _ in range(amount):
            if len(self.particles) >= self.max_particles:
                self.particles = self.particles[-self.max_particles+1:]
            
            self.particles.append({
                'x': x + random.uniform(-0.3, 0.3),
                'y': y + random.uniform(-0.3, 0.3),
                'z': z + random.uniform(0.5, 1.0),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'vz': random.uniform(0.5, 2),
                'color': (0.3, 0.3, 0.3),
                'lifetime': 1.0 + random.uniform(-0.2, 0.4),
                'max_lifetime': 1.0,
                'size': 8 + random.uniform(-2, 4),
                'type': 'smoke',
                'gravity': False,
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-1, 1)
            })

    def update(self, dt):
        """Update all particles."""
        for p in self.particles[:]:
            # Update position
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['z'] += p['vz'] * dt
            
            # Apply gravity
            if p['gravity']:
                p['vz'] -= GRAVITY * dt
            
            # Apply friction
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            
            # Update rotation
            p['rotation'] += p['rotation_speed'] * dt
            
            # Update lifetime
            p['lifetime'] -= dt
            
            # Remove dead particles
            if p['lifetime'] <= 0 or p['z'] < 0:
                if p in self.particles:
                    self.particles.remove(p)

    def clear(self):
        """Clear all particles."""
        self.particles = []


class PickupItem:
    """Doom-style pickup items (health, ammo, armor, powerups)."""
    
    TYPES = {
        "health_potion": {"color": (0.2, 0.8, 0.2), "value": 25, "sprite": "+"},
        "medkit": {"color": (0.9, 0.1, 0.1), "value": 50, "sprite": "++"},
        "ammo_clip": {"color": (0.9, 0.9, 0.2), "value": 20, "sprite": "||"},
        "ammo_box": {"color": (0.8, 0.7, 0.2), "value": 50, "sprite": "|||"},
        "armor_shard": {"color": (0.2, 0.4, 0.9), "value": 15, "sprite": "[]"},
        "armor_plate": {"color": (0.3, 0.5, 0.8), "value": 40, "sprite": "[[]]"},
        "invincibility": {"color": (1.0, 1.0, 0.0), "value": 30, "sprite": "*"},
        "berserk": {"color": (1.0, 0.0, 0.0), "value": 30, "sprite": "B"},
    }
    
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.opened = False
        self.float_offset = random.uniform(0, math.pi * 2)
        
        item_data = self.TYPES.get(item_type, self.TYPES["health_potion"])
        self.color = item_data["color"]
        self.value = item_data["value"]
        self.sprite = item_data["sprite"]
    
    def update(self, time):
        """Update pickup animation."""
        self.float_offset = math.sin(time * 2) * 0.1
    
    def collect(self, player, weapon):
        """Collect the item."""
        if self.opened:
            return ""
        self.opened = True
        
        if self.item_type in ["health_potion", "medkit"]:
            player.heal(self.value)
            return f"+{self.value} Health"
        elif self.item_type in ["ammo_clip", "ammo_box"]:
            weapon.reserve_ammo += self.value
            return f"+{self.value} Ammo"
        elif self.item_type in ["armor_shard", "armor_plate"]:
            player.add_armor(self.value)
            return f"+{self.value} Armor"
        elif self.item_type == "invincibility":
            player.apply_powerup("invincibility", self.value)
            return "Invincibility!"
        elif self.item_type == "berserk":
            player.apply_powerup("berserk", self.value)
            return "Berserk!"
        
        return ""
