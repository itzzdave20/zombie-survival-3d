# player.py
# Doom-style Player and Weapon Classes

import math
import kivy.clock
from texture import TextureGenerator
from settings import (
    PLAYER_WALK_SPEED, PLAYER_RUN_SPEED, PLAYER_STRAFE_SPEED, PLAYER_BACK_SPEED,
    PLAYER_RADIUS, WEAPON_BOB_AMOUNT, WEAPON_BOB_SPEED,
    RECOIL_RECOVERY, RECOIL_Y_RECOVERY
)


class Weapon:
    """
    Doom-style weapon with realistic handling, recoil, and visual feedback.
    Features multiple weapon types with unique characteristics.
    """

    def __init__(self, weapon_type="assault_rifle"):
        self.weapon_type = weapon_type
        self.tex_gen = TextureGenerator()
        
        # Weapon definitions - Doom-style balance
        self.weapons = {
            "pistol": {
                "damage": 35,
                "ammo": 12,
                "fire_rate": 0.25,
                "reserve": 48,
                "recoil": 8,
                "spread": 0.02,
                "reload_time": 1.0,
                "automatic": False,
                "name": "Pistol"
            },
            "assault_rifle": {
                "damage": 25,
                "ammo": 30,
                "fire_rate": 0.1,
                "reserve": 90,
                "recoil": 5,
                "spread": 0.04,
                "reload_time": 1.8,
                "automatic": True,
                "name": "Assault Rifle"
            },
            "shotgun": {
                "damage": 18,
                "ammo": 8,
                "fire_rate": 0.6,
                "reserve": 32,
                "recoil": 15,
                "spread": 0.12,
                "reload_time": 2.5,
                "automatic": False,
                "pellets": 8,
                "name": "Shotgun"
            },
            "sniper": {
                "damage": 100,
                "ammo": 5,
                "fire_rate": 1.2,
                "reserve": 20,
                "recoil": 20,
                "spread": 0.001,
                "reload_time": 2.0,
                "automatic": False,
                "name": "Sniper Rifle"
            },
            "chaingun": {
                "damage": 20,
                "ammo": 50,
                "fire_rate": 0.06,
                "reserve": 150,
                "recoil": 4,
                "spread": 0.06,
                "reload_time": 2.5,
                "automatic": True,
                "name": "Chaingun"
            }
        }

        # Initialize weapon stats
        stats = self.weapons.get(weapon_type, self.weapons["assault_rifle"])
        self.damage = stats["damage"]
        self.max_ammo = stats["ammo"]
        self.ammo = self.max_ammo
        self.fire_rate = stats["fire_rate"]
        self.reserve_ammo = stats["reserve"]
        self.base_recoil = stats["recoil"]
        self.spread = stats["spread"]
        self.reload_duration = stats["reload_time"]
        self.automatic = stats.get("automatic", False)
        self.pellets = stats.get("pellets", 1)
        self.name = stats.get("name", weapon_type)
        
        # Dynamic state
        self.reload_time = 0
        self.reload_progress = 0
        self.shoot_cooldown = 0
        self.recoil = 0
        self.recoil_y = 0
        self.recoil_target = 0
        self.weapon_bob = 0
        self.muzzle_flash = 0
        self.last_shot_time = 0
        
        # Generate weapon texture
        self.weapon_texture = self.tex_gen.generate_weapon_texture(32, weapon_type)

    def shoot(self):
        """
        Attempt to fire the weapon.
        Returns True if shot was fired, False otherwise.
        """
        if self.reload_time > 0 or self.shoot_cooldown > 0:
            if self.ammo <= 0 and self.reload_time <= 0:
                self.try_reload()
            return False
        
        if self.ammo <= 0:
            self.try_reload()
            return False
        
        self.ammo -= 1
        self.shoot_cooldown = self.fire_rate
        
        # Apply recoil
        self.recoil = self.base_recoil
        self.recoil_y = self.base_recoil * 0.7
        self.muzzle_flash = 0.05
        
        return True

    def try_reload(self):
        """
        Start reload sequence.
        Returns True if reload started, False otherwise.
        """
        if (self.reload_time <= 0 and 
            self.reserve_ammo > 0 and 
            self.ammo < self.max_ammo):
            self.reload_time = self.reload_duration
            self.reload_progress = 0
            return True
        return False

    def update(self, dt, moving=False):
        """
        Update weapon state.
        
        Args:
            dt: Delta time in seconds
            moving: Whether player is moving (for weapon bob)
        """
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        
        # Update reload
        if self.reload_time > 0:
            self.reload_time -= dt
            self.reload_progress = 1.0 - (self.reload_time / self.reload_duration)
            
            if self.reload_time <= 0:
                # Complete reload
                needed = self.max_ammo - self.ammo
                take = min(needed, self.reserve_ammo)
                self.ammo += take
                self.reserve_ammo -= take
                self.reload_progress = 0
        
        # Recover from recoil (Doom-style smooth recovery)
        if self.recoil > 0:
            self.recoil -= RECOIL_RECOVERY * dt
            if self.recoil < 0:
                self.recoil = 0
        
        if self.recoil_y > 0:
            self.recoil_y -= RECOIL_Y_RECOVERY * dt
            if self.recoil_y < 0:
                self.recoil_y = 0
        
        # Update muzzle flash
        if self.muzzle_flash > 0:
            self.muzzle_flash -= dt
        
        # Weapon bob when moving (Doom-style walking animation)
        if moving:
            self.weapon_bob += WEAPON_BOB_SPEED * dt
        else:
            # Return to center when idle (with slight breathing motion)
            idle_time = kivy.clock.Clock.get_time()
            self.weapon_bob = math.sin(idle_time * 2) * 0.5

    def get_bob_offset(self):
        """Get current weapon bob offset for rendering."""
        bob_x = math.sin(self.weapon_bob) * WEAPON_BOB_AMOUNT * 0.5
        bob_y = abs(math.sin(self.weapon_bob)) * WEAPON_BOB_AMOUNT * 0.3
        return bob_x, bob_y

    def get_recoil_offset(self):
        """Get current recoil offset for rendering."""
        return self.recoil * 0.5, self.recoil_y

    def is_ready(self):
        """Check if weapon is ready to fire."""
        return (self.reload_time <= 0 and 
                self.shoot_cooldown <= 0 and 
                self.ammo > 0)

    def switch_to(self, weapon_type):
        """Switch to a different weapon type."""
        if weapon_type in self.weapons:
            self.__init__(weapon_type)


class Player:
    """
    Doom-style player character with health, armor, and movement.
    Features classic FPS player mechanics.
    """

    def __init__(self):
        # Core stats
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.max_armor = 100
        
        # Stamina for sprinting
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen = 20
        self.stamina_drain = 35
        
        # Movement state
        self.sprinting = False
        self.moving = False
        self.strafing = False
        
        # Visual effects
        self.head_bob = 0
        self.head_bob_timer = 0
        self.damage_flash = 0
        self.death_time = 0
        
        # Combat stats
        self.score = 0
        self.kills = 0
        self.headshots = 0
        self.shots_fired = 0
        self.shots_hit = 0
        
        # Inventory
        self.weapons = []
        self.current_weapon = 0
        self.ammo_picked = 0
        
        # Power-ups (Doom-style)
        self.invincible = False
        self.invincible_time = 0
        self.berserk = False
        self.berserk_time = 0
        self.infrared = False
        self.infrared_time = 0
        
        # Step counter for sound
        self.step_distance = 0
        self.last_step_time = 0

    def take_damage(self, amount):
        """
        Apply damage to player.
        Armor absorbs 50% of damage.
        
        Returns True if player died.
        """
        if self.invincible:
            return False
        
        # Armor absorption
        if self.armor > 0:
            armor_absorb = min(self.armor, amount * 0.5)
            self.armor -= armor_absorb
            amount -= armor_absorb
        
        self.health -= amount
        self.damage_flash = 0.4
        
        return self.health <= 0

    def heal(self, amount):
        """Heal the player."""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health

    def add_armor(self, amount):
        """Add armor to the player."""
        old_armor = self.armor
        self.armor = min(self.max_armor, self.armor + amount)
        return self.armor - old_armor

    def add_weapon(self, weapon_type):
        """Add a weapon to inventory."""
        if weapon_type not in self.weapons:
            self.weapons.append(weapon_type)
            return True
        return False

    def switch_weapon(self, index):
        """Switch to weapon at index."""
        if 0 <= index < len(self.weapons):
            self.current_weapon = index
            return True
        return False

    def get_current_weapon(self):
        """Get current weapon type."""
        if self.weapons:
            return self.weapons[self.current_weapon]
        return "pistol"

    def apply_powerup(self, powerup_type, duration=30):
        """Apply a power-up effect."""
        if powerup_type == "invincibility":
            self.invincible = True
            self.invincible_time = duration
        elif powerup_type == "berserk":
            self.berserk = True
            self.berserk_time = duration
        elif powerup_type == "infrared":
            self.infrared = True
            self.infrared_time = duration

    def update(self, dt, moving=False):
        """
        Update player state.
        
        Args:
            dt: Delta time in seconds
            moving: Whether player is currently moving
        """
        self.moving = moving
        
        # Stamina management
        if self.sprinting and moving:
            self.stamina -= self.stamina_drain * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.sprinting = False
        elif not self.sprinting and self.stamina < self.max_stamina:
            self.stamina += self.stamina_regen * dt
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina
        
        # Head bob (Doom-style walking animation)
        if moving:
            bob_speed = WEAPON_BOB_SPEED * (1.5 if self.sprinting else 1.0)
            self.head_bob_timer += dt * bob_speed
            self.head_bob = math.sin(self.head_bob_timer) * 4
            
            # Step sound timing
            self.step_distance += dt * (PLAYER_RUN_SPEED if self.sprinting else PLAYER_WALK_SPEED)
            if self.step_distance >= 0.8:  # Step every 0.8 units
                self.step_distance = 0
                self.last_step_time = kivy.clock.Clock.get_time()
        else:
            self.head_bob = 0
            # Idle breathing motion
            idle_time = kivy.clock.Clock.get_time()
            self.head_bob = math.sin(idle_time * 2) * 1
        
        # Damage flash
        if self.damage_flash > 0:
            self.damage_flash -= dt
        
        # Power-up timers
        if self.invincible:
            self.invincible_time -= dt
            if self.invincible_time <= 0:
                self.invincible = False
        
        if self.berserk:
            self.berserk_time -= dt
            if self.berserk_time <= 0:
                self.berserk = False
        
        if self.infrared:
            self.infrared_time -= dt
            if self.infrared_time <= 0:
                self.infrared = False
        
        # Death timer
        if self.health <= 0:
            self.death_time += dt

    def is_alive(self):
        """Check if player is alive."""
        return self.health > 0

    def get_accuracy(self):
        """Get shooting accuracy percentage."""
        if self.shots_fired == 0:
            return 0
        return (self.shots_hit / self.shots_fired) * 100

    def reset(self):
        """Reset player to initial state."""
        self.health = 100
        self.armor = 0
        self.stamina = 100
        self.score = 0
        self.kills = 0
        self.headshots = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.weapons = ["pistol"]
        self.current_weapon = 0
        self.invincible = False
        self.berserk = False
        self.infrared = False
        self.death_time = 0
