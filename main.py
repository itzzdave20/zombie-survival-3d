# main.py
# Doom-Style 3D Zombie Survival Game
# A retro FPS experience with raycasting, textured walls, and classic gameplay

import kivy.app
import kivy.clock
import kivy.core.window
import kivy.graphics
import kivy.uix.widget
import kivy.uix.screenmanager
import kivy.uix.floatlayout
import kivy.uix.label
import kivy.uix.button
import kivy.uix.scrollview
import math
import random

# Import game modules
from settings import *
from sound import SoundManager
from texture import TextureGenerator
from player import Player, Weapon
from map_renderer import Raycaster
from world_renderer import Zombie, Quest, LootBox, ParticleSystem, PickupItem

# Window configuration
kivy.core.window.Window.size = (1280, 720)
kivy.core.window.Window.clear_color = (0.0, 0.0, 0.0, 1)
kivy.core.window.Window.title = "DOOM-STYLE ZOMBIE SURVIVAL 3D"


class Game3DWidget(kivy.uix.widget.Widget):
    """Main Doom-style 3D Game Widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = kivy.core.window.Window.size
        self.size_hint = (1, 1)
        self.keyboard = None
        
        # Bind to size changes
        self.bind(size=self._on_size_change)

        # Game state
        self.level = 1
        self.score = 0
        self.kills = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        self.keys_pressed = set()
        self.mouse_down = False
        self.mouse_sensitivity = 0.6
        self.last_mouse_x = None
        self.mouse_accumulator = 0.0
        
        # Touch controls for mobile
        self.touch_joystick = None  # (start_x, start_y, current_x, current_y)
        self.touch_look_id = None
        self.touch_look_start = None
        self.fire_button_rect = None
        self.reload_button_rect = None
        self.joystick_base_pos = (100, 100)
        self.joystick_radius = 60

        # Player & Weapon
        self.player = Player()
        self.weapon = Weapon("assault_rifle")
        self.player.weapons = ["pistol", "assault_rifle"]

        # Notifications (Doom-style message bar)
        self.notifications = []
        self.notification_timer = 0
        self.message_bar_text = ""
        self.message_bar_time = 0

        # Create map
        self.map = self._create_map()
        self.raycaster = Raycaster(self.map)

        # Systems
        self.particles = ParticleSystem()
        self.sound = SoundManager()

        # Enemies
        self.enemies = []
        self._spawn_enemies(10)

        # Quests
        self.active_quest = None
        self.quest_history = []
        self._generate_quest()

        # Loot boxes and pickups
        self.loot_boxes = []
        self.pickups = []
        self._spawn_loot_boxes(5)
        self._spawn_pickups(3)

        # Setup
        self._setup_keyboard()
        self._setup_ui()

        # Game loop at 60 FPS
        kivy.clock.Clock.schedule_interval(self.update, 1.0 / 60.0)

        # Welcome message
        self._notify("WELCOME TO DOOM-STYLE SURVIVAL!", 3.0)

    def _create_map(self):
        """Create game map with Doom-style layout."""
        size = 32
        world = [[0] * size for _ in range(size)]

        # Outer walls
        for i in range(size):
            world[0][i] = 1
            world[size-1][i] = 1
            world[i][0] = 1
            world[i][size-1] = 1

        # Random pillars and obstacles
        for i in range(6, size-6, 3):
            for j in range(6, size-6, 3):
                if random.random() < 0.2:
                    world[i][j] = random.randint(2, 5)

        # Wall patterns
        for i in range(8, size-8, 4):
            world[i][8] = random.randint(1, 4)
            world[i][size-9] = random.randint(1, 4)
            world[8][i] = random.randint(1, 4)
            world[size-9][i] = random.randint(1, 4)

        # Central arena (starting area)
        for i in range(12, 21):
            for j in range(12, 21):
                world[i][j] = 0

        # Add some hell walls for variety
        for i in range(5, size-5, 8):
            for j in range(5, size-5, 8):
                if random.random() < 0.3:
                    world[i][j] = 7
                    world[i+1][j] = 7
                    world[i][j+1] = 7

        return world

    def _spawn_enemies(self, count):
        """Spawn enemies around the map."""
        types = ["normal", "normal", "normal", "fast", "tank", "burnt", "demon"]

        for i in range(count):
            attempts = 0
            while attempts < 20:
                x, y = random.uniform(4, 28), random.uniform(4, 28)

                # Check not in wall
                if self.map[int(y)][int(x)] != 0:
                    attempts += 1
                    continue

                # Check not too close to center (spawn area)
                if abs(x - 16.5) < 5 and abs(y - 16.5) < 5:
                    attempts += 1
                    continue

                # Check not too close to other enemies
                too_close = False
                for enemy in self.enemies:
                    if math.sqrt((enemy.x - x)**2 + (enemy.y - y)**2) < 3:
                        too_close = True
                        break

                if too_close:
                    attempts += 1
                    continue

                # Determine enemy type
                if self.level % 5 == 0 and i == 0:
                    z_type = "boss"
                elif random.random() < 0.05:
                    z_type = "boss"
                elif random.random() < 0.15:
                    z_type = random.choice(["fast", "tank", "burnt", "demon"])
                else:
                    z_type = random.choice(types)

                enemy = Zombie(x, y, z_type)
                enemy.set_map(self.map)
                self.enemies.append(enemy)
                break

    def _spawn_loot_boxes(self, count):
        """Spawn loot boxes."""
        for _ in range(count):
            attempts = 0
            while attempts < 10:
                x, y = random.uniform(4, 28), random.uniform(4, 28)
                if self.map[int(y)][int(x)] == 0:
                    self.loot_boxes.append(LootBox(x, y))
                    break
                attempts += 1

    def _spawn_pickups(self, count):
        """Spawn pickup items."""
        pickup_types = ["health_potion", "medkit", "ammo_clip", "armor_shard"]

        for _ in range(count):
            attempts = 0
            while attempts < 10:
                x, y = random.uniform(4, 28), random.uniform(4, 28)
                if self.map[int(y)][int(x)] == 0:
                    item_type = random.choice(pickup_types)
                    self.pickups.append(PickupItem(x, y, item_type))
                    break
                attempts += 1

    def _generate_quest(self):
        """Generate a new quest."""
        quest_types = [
            ("kill", f"Eliminate {5 + self.level * 2} Zombies", 5 + self.level * 2, 200),
            ("survive", f"Survive {30 + self.level * 10} Seconds", 30 + self.level * 10, 150),
        ]
        q_type, desc, target, reward = random.choice(quest_types)
        self.active_quest = Quest(q_type, desc, target, reward)
        self._notify(f"NEW QUEST: {desc}", 3.0)

    def _notify(self, text, duration=2.0):
        """Add notification message."""
        self.notifications.append((text, duration))
        self.message_bar_text = text
        self.message_bar_time = duration

    def _setup_keyboard(self):
        """Setup keyboard input."""
        self.keyboard = kivy.core.window.Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_key_down)
        self.keyboard.bind(on_key_up=self._on_key_up)
        try:
            kivy.core.window.Window.bind(on_mouse_move=self.on_mouse_move)
        except:
            pass

    def _keyboard_closed(self):
        """Cleanup keyboard."""
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_key_down)
            self.keyboard.unbind(on_key_up=self._on_key_up)
            kivy.core.window.Window.unbind(on_mouse_move=self.on_mouse_move)
            self.keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle key press."""
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)

        if key in ('w', 'up'):
            self.keys_pressed.add('w')
        if key in ('s', 'down'):
            self.keys_pressed.add('s')
        if key in ('a', 'left'):
            self.keys_pressed.add('a')
        if key in ('d', 'right'):
            self.keys_pressed.add('d')
        if key == 'r':
            self.keys_pressed.add('r')
            self.weapon.try_reload()
        if key == 'shift':
            self.keys_pressed.add('shift')
        if key == 'p':
            self.paused = not self.paused
        if key == 'escape':
            self.paused = not self.paused
        if key == '1':
            self._switch_weapon(0)
        if key == '2':
            self._switch_weapon(1)
        if key == '3':
            self._switch_weapon(2)

    def _switch_weapon(self, index):
        """Switch to weapon at index."""
        if index < len(self.player.weapons):
            weapon_type = self.player.weapons[index]
            self.weapon = Weapon(weapon_type)
            self._notify(f"Switched to {self.weapon.name}", 1.0)

    def _on_key_up(self, keyboard, keycode):
        """Handle key release."""
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        for k in ('w', 's', 'a', 'd', 'r', 'shift'):
            if key == k and k in self.keys_pressed:
                self.keys_pressed.remove(k)

    def _setup_ui(self):
        """Setup initial UI elements."""
        with self.canvas:
            kivy.graphics.Color(1, 1, 1, 0.9)
            self.crosshair_h = kivy.graphics.Line(
                points=[self.width/2-12, self.height/2, self.width/2+12, self.height/2], width=2)
            self.crosshair_v = kivy.graphics.Line(
                points=[self.width/2, self.height/2-12, self.width/2, self.height/2+12], width=2)

    def _on_size_change(self, instance, new_size):
        """Handle widget size changes."""
        self.size = new_size

    def _update_crosshair(self):
        """Update crosshair position with recoil."""
        if hasattr(self, 'crosshair_h'):
            recoil_offset = self.weapon.recoil_y * 0.5
            spread = (1.0 - self.weapon.ammo / self.weapon.max_ammo) * 3

            self.crosshair_h.points = [
                self.width/2-12-spread, self.height/2+recoil_offset,
                self.width/2+12+spread, self.height/2+recoil_offset
            ]
            self.crosshair_v.points = [
                self.width/2, self.height/2-12-spread+recoil_offset,
                self.width/2, self.height/2+12+spread+recoil_offset
            ]

    def on_mouse_move(self, window, x, y, *args):
        """Handle mouse movement for looking around."""
        if self.game_over or self.paused:
            return

        if self.last_mouse_x is None:
            self.last_mouse_x = x
            return

        dx = x - self.last_mouse_x
        self.mouse_accumulator += dx * self.mouse_sensitivity * 0.002

        if abs(self.mouse_accumulator) >= 0.001:
            if self.mouse_accumulator > 0:
                self.raycaster.rotate_right(self.mouse_accumulator)
            else:
                self.raycaster.rotate_left(-self.mouse_accumulator)
            self.mouse_accumulator = 0

        self.last_mouse_x = x

    def on_touch_down(self, touch):
        """Handle touch/mouse click - including mobile controls."""
        if self.game_over or self.paused:
            return
        
        x, y = touch.pos
        
        # Check sprint button (top right)
        sprint_x = self.width - 60
        sprint_y = self.height - 60
        sprint_r = 35
        if math.sqrt((x - sprint_x)**2 + (y - sprint_y)**2) < sprint_r:
            self.keys_pressed.add('shift')
            touch.grab(self)
            return
        
        # Check fire button (bottom right)
        fire_btn_x = self.width - 120
        fire_btn_y = 80
        fire_btn_r = 50
        if math.sqrt((x - fire_btn_x)**2 + (y - fire_btn_y)**2) < fire_btn_r:
            self.mouse_down = True
            self._shoot()
            touch.grab(self)
            return
        
        # Check reload button (above fire button)
        reload_btn_x = self.width - 120
        reload_btn_y = 180
        reload_btn_r = 40
        if math.sqrt((x - reload_btn_x)**2 + (y - reload_btn_y)**2) < reload_btn_r:
            self.keys_pressed.add('r')
            self.weapon.try_reload()
            self.sound.play_reload(self.weapon.weapon_type)
            touch.grab(self)
            return
        
        # Left side of screen = virtual joystick for movement
        if x < self.width / 2:
            self.touch_joystick = (x, y, x, y)
            self._update_joystick_movement()
            touch.grab(self)
            return
        
        # Right side = look control
        self.touch_look_id = touch.id
        self.touch_look_start = (x, y)
        self.last_mouse_x = x
        touch.grab(self)

    def on_touch_up(self, touch):
        """Handle touch/mouse release."""
        # Release fire button
        self.mouse_down = False
        
        # Release reload button
        if 'r' in self.keys_pressed:
            self.keys_pressed.discard('r')
        
        # Release sprint button
        if 'shift' in self.keys_pressed:
            self.keys_pressed.discard('shift')
        
        # Release joystick
        if self.touch_joystick:
            self.touch_joystick = None
            # Clear movement keys
            for k in ('w', 's', 'a', 'd'):
                if k in self.keys_pressed:
                    self.keys_pressed.discard(k)
        
        # Release look control
        if self.touch_look_id == touch.id:
            self.touch_look_id = None
            self.touch_look_start = None
        
        self.last_mouse_x = None
        
        # Ungrab touch
        if touch.grab_current is self:
            touch.ungrab(self)

    def on_touch_move(self, touch):
        """Handle touch movement - for joystick and look."""
        if self.game_over or self.paused:
            return
        
        x, y = touch.pos
        
        # Update joystick position
        if self.touch_joystick and touch.grab_current is self:
            # Check if this touch is the joystick touch
            start_x, start_y, _, _ = self.touch_joystick
            # Update the current position
            self.touch_joystick = (start_x, start_y, x, y)
            self._update_joystick_movement()
        
        # Update look control
        if self.touch_look_id == touch.id and self.touch_look_start:
            start_x, start_y = self.touch_look_start
            dx = x - start_x
            
            # Rotate view based on horizontal movement
            self.mouse_accumulator += dx * self.mouse_sensitivity * 0.002
            
            if abs(self.mouse_accumulator) >= 0.001:
                if self.mouse_accumulator > 0:
                    self.raycaster.rotate_right(self.mouse_accumulator)
                else:
                    self.raycaster.rotate_left(-self.mouse_accumulator)
                self.mouse_accumulator = 0
            
            # Update start position for continuous looking
            self.touch_look_start = (x, y)

    def _update_joystick_movement(self):
        """Update movement keys based on joystick position."""
        if not self.touch_joystick:
            return
        
        start_x, start_y, curr_x, curr_y = self.touch_joystick
        
        # Calculate offset from center
        dx = curr_x - start_x
        dy = curr_y - start_y
        
        # Clamp to radius
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > self.joystick_radius:
            scale = self.joystick_radius / distance
            dx *= scale
            dy *= scale
        
        # Determine direction (with deadzone)
        deadzone = 10
        self.keys_pressed.discard('w')
        self.keys_pressed.discard('s')
        self.keys_pressed.discard('a')
        self.keys_pressed.discard('d')
        
        if dy < -deadzone:
            self.keys_pressed.add('w')  # Forward
        if dy > deadzone:
            self.keys_pressed.add('s')  # Backward
        if dx < -deadzone:
            self.keys_pressed.add('a')  # Left
        if dx > deadzone:
            self.keys_pressed.add('d')  # Right

    def _shoot(self):
        """Fire weapon."""
        if self.weapon.shoot():
            weapon_type = self.weapon.weapon_type
            self.sound.play_shoot(weapon_type)

            self.player.shots_fired += 1

            # Muzzle flash particles
            self.particles.emit(
                self.raycaster.pos_x + self.raycaster.dir_x * 0.5,
                self.raycaster.pos_y + self.raycaster.dir_y * 0.5,
                1.5,
                self.raycaster.dir_x * 2,
                self.raycaster.dir_y * 2,
                random.uniform(2, 5),
                (1, 0.9, 0.5), 0.08, count=5, size=6
            )

            # Hitscan hit detection
            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                dx = enemy.x - self.raycaster.pos_x
                dy = enemy.y - self.raycaster.pos_y
                dist = math.sqrt(dx*dx + dy*dy)

                angle = math.atan2(dy, dx)
                player_angle = math.atan2(self.raycaster.dir_y, self.raycaster.dir_x)
                angle_diff = abs(angle - player_angle)

                if angle_diff > math.pi:
                    angle_diff = 2*math.pi - angle_diff

                # Hit check with weapon spread
                hit_threshold = 0.25 + self.weapon.spread * dist
                if angle_diff < hit_threshold and dist < 25:
                    # Headshot chance
                    headshot = random.random() < 0.12
                    if headshot:
                        self.player.headshots += 1

                    killed = enemy.take_damage(self.weapon.damage, headshot)

                    if killed:
                        self.kills += 1
                        self.player.kills += 1
                        self.score += 50
                        self._notify(f"ENEMY DOWN! +50", 1.0)
                        self.sound.play_hit('flesh')
                        self.sound.play_enemy_death(enemy.type)

                        # Blood spray
                        self.particles.emit_blood(
                            enemy.x, enemy.y, 1.0,
                            self.raycaster.dir_x, self.raycaster.dir_y,
                            amount=25
                        )

                        if self.active_quest and self.active_quest.quest_type == "kill":
                            if self.active_quest.update():
                                self._complete_quest()
                    else:
                        self._notify(f"HIT! ({int(enemy.health)} HP)", 0.5)
                        self.sound.play_hit('flesh')

                        # Blood splatter
                        self.particles.emit_blood(
                            enemy.x, enemy.y, 1.2,
                            self.raycaster.dir_x, self.raycaster.dir_y,
                            amount=8
                        )

                    self.player.shots_hit += 1
                    break

    def _complete_quest(self):
        """Complete current quest."""
        q = self.active_quest
        self._notify(f"QUEST COMPLETE! +{q.reward_score}", 3.0)
        self.score += q.reward_score
        self.quest_history.append(q)
        self.sound.play_level_up()
        self._generate_quest()

    def update(self, dt):
        """Main game update loop."""
        if self.game_over or self.paused:
            return

        dt = min(dt, MAX_FRAME_TIME)
        time = kivy.clock.Clock.get_time()

        # Mouse look (alternative method)
        try:
            mouse_x, mouse_y = kivy.core.window.Window.mouse_pos
            if self.last_mouse_x is not None:
                dx = mouse_x - self.last_mouse_x
                self.mouse_accumulator += dx * self.mouse_sensitivity * 0.002

                if abs(self.mouse_accumulator) >= 0.001:
                    if self.mouse_accumulator > 0:
                        self.raycaster.rotate_right(self.mouse_accumulator)
                    else:
                        self.raycaster.rotate_left(-self.mouse_accumulator)
                    self.mouse_accumulator = 0
            self.last_mouse_x = mouse_x
        except:
            pass

        # Player movement
        moving = False
        can_sprint = 'shift' in self.keys_pressed and self.player.stamina > 10
        self.player.sprinting = can_sprint

        if 'w' in self.keys_pressed:
            self.raycaster.move_forward(dt, can_sprint)
            moving = True
        if 's' in self.keys_pressed:
            self.raycaster.move_backward(dt)
            moving = True
        if 'a' in self.keys_pressed:
            self.raycaster.strafe_left(dt)
            moving = True
        if 'd' in self.keys_pressed:
            self.raycaster.strafe_right(dt)
            moving = True

        # Reload
        if 'r' in self.keys_pressed:
            if self.weapon.try_reload():
                self.sound.play_reload(self.weapon.weapon_type)
                self.keys_pressed.discard('r')

        # Update player
        self.player.update(dt, moving)
        self.weapon.update(dt, moving)

        # Auto-fire
        if self.mouse_down and self.weapon.automatic:
            self._shoot()

        # Update enemies
        for enemy in self.enemies:
            if enemy.update(self.raycaster.pos_x, self.raycaster.pos_y, dt):
                # Enemy attack
                if self.player.take_damage(enemy.damage):
                    self.game_over = True
                    self.sound.play_damage()
                    self._notify("YOU DIED", 5.0)

        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Spawn more enemies if needed
        if len(self.enemies) < 5 + self.level:
            self._spawn_enemies(2)

        # Update loot boxes
        for lb in self.loot_boxes:
            lb.update(time)

        # Check loot box pickup
        for lb in self.loot_boxes:
            if not lb.opened:
                dist = math.sqrt((lb.x - self.raycaster.pos_x)**2 + (lb.y - self.raycaster.pos_y)**2)
                if dist < 1.5:
                    rewards = lb.open(self.player, self.weapon)
                    for r in rewards:
                        self._notify(r, 1.0)
                    self.sound.play_pickup('item')

        # Update pickups
        for pickup in self.pickups:
            pickup.update(time)

        # Check pickup collection
        for pickup in self.pickups:
            if not pickup.opened:
                dist = math.sqrt((pickup.x - self.raycaster.pos_x)**2 + (pickup.y - self.raycaster.pos_y)**2)
                if dist < 1.2:
                    msg = pickup.collect(self.player, self.weapon)
                    if msg:
                        self._notify(msg, 1.0)
                        self.sound.play_pickup(pickup.item_type)

        # Update particles
        self.particles.update(dt)

        # Update notifications
        for n in self.notifications[:]:
            text, time_left = n
            new_time = time_left - dt
            if new_time <= 0:
                self.notifications.remove(n)
            else:
                self.notifications[self.notifications.index(n)] = (text, new_time)

        # Update quest
        if self.active_quest:
            if self.active_quest.quest_type == "survive":
                if self.active_quest.update_time(dt):
                    self._complete_quest()

        # Level progression
        if self.kills >= self.level * 10:
            self.level += 1
            self.player.heal(30)
            self._notify(f"LEVEL {self.level}!", 2.0)
            self.sound.play_level_up()
            self._spawn_loot_boxes(2)
            self._spawn_pickups(2)

        # Update message bar timer
        if self.message_bar_time > 0:
            self.message_bar_time -= dt

        # Render
        self.canvas.clear()
        self._draw_3d()
        self._draw_hud()
        self._draw_minimap()
        self._draw_weapon()
        self._update_crosshair()
        self._draw_touch_controls()

    def _draw_3d(self):
        """Draw 3D view using raycasting."""
        segments, z_buffer = self.raycaster.cast_rays()
        scale_x = self.width / self.raycaster.screen_width
        scale_y = self.height / self.raycaster.screen_height
        head_bob = self.player.head_bob
        time = kivy.clock.Clock.get_time()

        with self.canvas:
            # Draw sky (gradient)
            for sky_y in range(0, self.height // 2, 4):
                gradient = 1.0 - (sky_y / (self.height // 2))
                r = 0.02 + 0.02 * gradient
                g = 0.02 + 0.03 * gradient
                b = 0.05 + 0.08 * gradient
                kivy.graphics.Color(r, g, b, 1)
                kivy.graphics.Rectangle(pos=(0, self.height // 2 + sky_y), size=(self.width, 4))

            # Draw floor (gradient)
            for floor_y in range(0, self.height // 2, 4):
                gradient = floor_y / (self.height // 2)
                r = 0.06 + 0.03 * gradient
                g = 0.05 + 0.02 * gradient
                b = 0.04 + 0.02 * gradient
                kivy.graphics.Color(r, g, b, 1)
                kivy.graphics.Rectangle(pos=(0, floor_y), size=(self.width, 4))

            # Draw walls
            for seg in segments:
                x = seg['x']
                ds = seg['draw_start']
                de = seg['draw_end']
                wall_type = seg['wall_type']
                wall_x = seg['wall_x']
                side = seg['side']
                dist = seg['distance']

                texture = self.raycaster.get_texture_for_wall(wall_type)
                tex_x = seg['tex_x']

                # Get light level
                light = self.raycaster.get_light_level(dist, side)

                # Draw textured wall column
                for draw_y in range(ds, de, 4):
                    tex_y = int((draw_y - ds) / max(de - ds, 1) * (TEXTURE_SIZE - 1))
                    tex_y = max(0, min(TEXTURE_SIZE - 1, tex_y))

                    if texture and tex_y < len(texture) and tex_x < len(texture[tex_y]):
                        color = texture[tex_y][tex_x]
                    else:
                        color = (0.5, 0.5, 0.5)

                    # Apply lighting
                    color = tuple(c * light for c in color)

                    kivy.graphics.Color(*color, 1)
                    sx = int(x * scale_x)
                    sy = int(draw_y * scale_y) + head_bob
                    sh = min(4 * scale_y, (de - draw_y) * scale_y)
                    kivy.graphics.Rectangle(pos=(sx, sy), size=(max(2, scale_x), sh))

            # Draw enemies (sprite projection)
            enemy_list = []
            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                dx = enemy.x - self.raycaster.pos_x
                dy = enemy.y - self.raycaster.pos_y
                dist = math.sqrt(dx*dx + dy*dy)

                angle, distance, visible = self.raycaster.get_sprite_angle(enemy.x, enemy.y)

                if visible and dist < 25 and abs(angle) < 1.3:
                    enemy_list.append((enemy, dist, angle))

            # Sort by distance (far to near)
            enemy_list.sort(key=lambda e: -e[1])

            for enemy, dist, angle in enemy_list:
                self._draw_enemy(enemy, dist, angle, head_bob)

            # Draw loot boxes
            for lb in self.loot_boxes:
                if lb.opened:
                    continue
                angle_lb, dist_lb, visible_lb = self.raycaster.get_sprite_angle(lb.x, lb.y)

                if visible_lb and dist_lb < 18 and abs(angle_lb) < 1.2:
                    sx = self.width//2 + int(angle_lb * self.width//2 / (FOV * 2))
                    sy = self.height//2 + int(dist_lb * 10) + head_bob
                    size = max(15, int(50 / dist_lb))
                    float_y = lb.float_offset * size

                    kivy.graphics.Color(*lb.color, 1)
                    kivy.graphics.Rectangle(pos=(int(sx-size/2), int(sy-size/2+float_y)), 
                                           size=(int(size), int(size)))
                    kivy.graphics.Color(1, 1, 1, 0.4)
                    kivy.graphics.Rectangle(pos=(int(sx-size/2+3), int(sy-size/2+float_y+3)), 
                                           size=(int(size*0.3), int(size*0.3)))

            # Draw particles
            for p in self.particles.particles:
                angle_p, dist_p, visible_p = self.raycaster.get_sprite_angle(p['x'], p['y'])

                if visible_p and dist_p < 15 and dist_p > 0.3:
                    sx = self.width//2 + int(angle_p * self.width//2 / (FOV * 2))
                    sy = self.height//2 + int(dist_p * 12) - int(p['z'] * 40) + head_bob
                    alpha = p['lifetime'] / p['max_lifetime']
                    kivy.graphics.Color(*p['color'], alpha)
                    kivy.graphics.Rectangle(pos=(int(sx-p['size']/2), int(sy-p['size']/2)), 
                                           size=(int(p['size']), int(p['size'])))

    def _draw_enemy(self, enemy, dist, angle, head_bob):
        """Draw a single enemy with Doom-style textures."""
        h, w = enemy.get_display_size(dist)
        sx = self.width//2 + int(angle * self.width//2 / (FOV * 2))
        sy = self.height//2 + int(h * 0.5)

        walk_offset = enemy.walk_frame
        body_sway = walk_offset * 3
        arm_swing = walk_offset * 8
        leg_swing = walk_offset * 10
        head_bob_enemy = abs(math.sin(walk_offset * 3)) * 2

        base_color = enemy.color
        if enemy.hit_flash > 0:
            base_color = (1, 1, 1)

        # Dim based on distance
        dim_factor = max(0.4, 1.0 - dist / 30.0)
        
        # Get Doom-style colors based on enemy type
        if enemy.type == "normal":
            head_color = (0.35 * dim_factor, 0.65 * dim_factor, 0.3 * dim_factor)
            torso_color = (0.35 * dim_factor, 0.35 * dim_factor, 0.25 * dim_factor)
            leg_color = (0.18 * dim_factor, 0.2 * dim_factor, 0.25 * dim_factor)
            eye_color = (0.1, 0.05, 0.05)
        elif enemy.type == "fast":
            head_color = (0.75 * dim_factor, 0.65 * dim_factor, 0.6 * dim_factor)
            torso_color = (0.45 * dim_factor, 0.45 * dim_factor, 0.5 * dim_factor)
            leg_color = (0.25 * dim_factor, 0.3 * dim_factor, 0.35 * dim_factor)
            eye_color = (0.15, 0.1, 0.15)
        elif enemy.type == "tank":
            head_color = (0.25 * dim_factor, 0.3 * dim_factor, 0.35 * dim_factor)
            torso_color = (0.2 * dim_factor, 0.25 * dim_factor, 0.3 * dim_factor)
            leg_color = (0.15 * dim_factor, 0.18 * dim_factor, 0.22 * dim_factor)
            eye_color = (0.9, 0.15, 0.1)
        elif enemy.type == "burnt":
            head_color = (0.45 * dim_factor, 0.35 * dim_factor, 0.25 * dim_factor)
            torso_color = (0.3 * dim_factor, 0.18 * dim_factor, 0.15 * dim_factor)
            leg_color = (0.25 * dim_factor, 0.18 * dim_factor, 0.15 * dim_factor)
            eye_color = (0.9, 0.4, 0.1)
        elif enemy.type == "demon":
            head_color = (0.65 * dim_factor, 0.35 * dim_factor, 0.2 * dim_factor)
            torso_color = (0.6 * dim_factor, 0.3 * dim_factor, 0.18 * dim_factor)
            leg_color = (0.55 * dim_factor, 0.28 * dim_factor, 0.15 * dim_factor)
            eye_color = (1.0, 0.8, 0.1)
        elif enemy.type == "boss":
            head_color = (0.4 * dim_factor, 0.55 * dim_factor, 0.35 * dim_factor)
            torso_color = (0.35 * dim_factor, 0.5 * dim_factor, 0.3 * dim_factor)
            leg_color = (0.3 * dim_factor, 0.45 * dim_factor, 0.25 * dim_factor)
            eye_color = (1.0, 0.2, 0.05)
        elif enemy.type == "cacodemon":
            head_color = (0.85 * dim_factor, 0.2 * dim_factor, 0.2 * dim_factor)
            torso_color = (0.8 * dim_factor, 0.15 * dim_factor, 0.15 * dim_factor)
            leg_color = (0.5 * dim_factor, 0.1 * dim_factor, 0.1 * dim_factor)
            eye_color = (1.0, 0.9, 0.2)
        else:
            head_color = torso_color = leg_color = tuple(c * dim_factor for c in base_color)
            eye_color = (0.5, 0.5, 0.5)

        # Draw enemy based on type
        if enemy.type == "cacodemon":
            self._draw_cacodemon(sx, sy, w, h, head_color, eye_color)
        else:
            self._draw_humanoid_enemy(sx, sy, w, h, head_color, torso_color, leg_color, 
                                      eye_color, body_sway, leg_swing, arm_swing, head_bob_enemy, dist)

        # Health bar
        self._draw_enemy_health_bar(sx, sy, w, h, enemy)

    def _draw_humanoid_enemy(self, sx, sy, w, h, head_color, torso_color, leg_color,
                             eye_color, body_sway, leg_swing, arm_swing, head_bob_enemy, dist):
        """Draw humanoid enemy (zombie/demon)."""
        leg_w = w * 0.35
        leg_h = h * 0.45

        # Legs
        leg_shadow = tuple(c * 0.6 for c in leg_color)

        left_leg_x = int(sx - w/2 - leg_w/2 + math.sin(leg_swing) * 5)
        left_leg_y = int(sy - leg_h)
        kivy.graphics.Color(*leg_shadow, 0.95)
        kivy.graphics.Rectangle(pos=(left_leg_x, left_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
        kivy.graphics.Color(*leg_color, 0.95)
        kivy.graphics.Rectangle(pos=(left_leg_x + int(leg_w * 0.5), left_leg_y), size=(int(leg_w * 0.5), int(leg_h)))

        right_leg_x = int(sx + w/2 - leg_w/2 - math.sin(leg_swing) * 5)
        right_leg_y = int(sy - leg_h)
        kivy.graphics.Color(*leg_shadow, 0.95)
        kivy.graphics.Rectangle(pos=(right_leg_x, right_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
        kivy.graphics.Color(*leg_color, 0.95)
        kivy.graphics.Rectangle(pos=(right_leg_x + int(leg_w * 0.5), right_leg_y), size=(int(leg_w * 0.5), int(leg_h)))

        # Body/Torso
        body_w = w * 0.9
        body_h = h * 0.55
        body_x = int(sx - body_w/2 + body_sway * 0.3)
        body_y = int(sy - leg_h)

        kivy.graphics.Color(*tuple(c * 0.6 for c in torso_color), 1)
        kivy.graphics.Rectangle(pos=(body_x, body_y), size=(int(body_w * 0.2), int(body_h)))
        kivy.graphics.Color(*torso_color, 1)
        kivy.graphics.Rectangle(pos=(int(body_x + body_w * 0.2), body_y), size=(int(body_w * 0.6), int(body_h)))
        kivy.graphics.Color(*tuple(c * 0.75 for c in torso_color), 1)
        kivy.graphics.Rectangle(pos=(int(body_x + body_w * 0.8), body_y), size=(int(body_w * 0.2), int(body_h)))

        # Head
        head_size = w * 0.55
        head_x = int(sx - head_size/2 + body_sway * 0.3)
        head_y = int(sy - leg_h - body_h - head_size*0.15 + head_bob_enemy)

        kivy.graphics.Color(*tuple(c * 0.7 for c in head_color), 1)
        kivy.graphics.Rectangle(pos=(head_x, int(head_y + head_size * 0.5)), size=(int(head_size), int(head_size * 0.5)))
        kivy.graphics.Color(*head_color, 1)
        kivy.graphics.Rectangle(pos=(head_x, head_y), size=(int(head_size), int(head_size * 0.5)))

        # Glowing eyes
        eye_glow = min(1.0, 10.0 / max(dist, 1))
        es = max(5, int(head_size/5))
        ey = int(head_y + head_size*0.52)
        eye_offset_x = int(0 * 3)

        kivy.graphics.Color(*eye_color, min(1, 0.7 + eye_glow * 0.3))
        kivy.graphics.Rectangle(pos=(int(sx - head_size/5 + eye_offset_x), ey), size=(es, es))
        kivy.graphics.Rectangle(pos=(int(sx + head_size/10 + eye_offset_x), ey), size=(es, es))

    def _draw_cacodemon(self, sx, sy, w, h, body_color, eye_color):
        """Draw floating cacodemon sphere."""
        # Main sphere body
        kivy.graphics.Color(*body_color, 1)
        sphere_x = int(sx - w/2)
        sphere_y = int(sy - h/2)
        kivy.graphics.Rectangle(pos=(sphere_x, sphere_y), size=(int(w), int(h)))
        
        # Large central eye
        eye_size = int(w * 0.35)
        eye_x = int(sx - eye_size/2)
        eye_y = int(sy - eye_size/2)
        kivy.graphics.Color(*eye_color, 1)
        kivy.graphics.Rectangle(pos=(eye_x, eye_y), size=(eye_size, eye_size))

    def _draw_enemy_health_bar(self, sx, sy, w, h, enemy):
        """Draw enemy health bar."""
        hp_pct = enemy.health / enemy.max_health
        bar_x = int(sx - w/2)
        bar_y = int(sy - h/2 - 20)
        
        kivy.graphics.Color(0.2, 0.2, 0.2, 0.9)
        kivy.graphics.Rectangle(pos=(bar_x, bar_y), size=(int(w), 6))
        
        if hp_pct > 0.6:
            hp_color = (0.2, 0.8, 0.2, 1)
        elif hp_pct > 0.3:
            hp_color = (0.9, 0.7, 0.1, 1)
        else:
            hp_color = (0.9, 0.15, 0.15, 1)
        
        kivy.graphics.Color(*hp_color, 1)
        kivy.graphics.Rectangle(pos=(bar_x, bar_y), size=(max(2, int(w*hp_pct)), 6))

    def _draw_weapon(self):
        """Draw weapon in FPS view (Doom-style)."""
        recoil_x, recoil_y = self.weapon.get_recoil_offset()
        bob_x, bob_y = self.weapon.get_bob_offset()

        # Position weapon at bottom center of screen
        base_x = int(self.width / 2)
        base_y = int(self.height - 80)

        rx = int(recoil_x)
        ry = int(recoil_y)

        with self.canvas:
            gun_w = 220
            gun_h = 55

            gx = base_x + rx + int(bob_x)
            gy = base_y + ry + int(bob_y)

            # Gun body
            kivy.graphics.Color(0.22, 0.22, 0.28, 1)
            kivy.graphics.Rectangle(pos=(gx - 70, gy), size=(gun_w, gun_h))

            # Top rail
            kivy.graphics.Color(0.18, 0.18, 0.24, 1)
            kivy.graphics.Rectangle(pos=(gx - 60, gy - 10), size=(gun_w - 30, 10))

            # Barrel
            barrel_w = 120
            barrel_h = 18
            barrel_x = gx - 70 - barrel_w
            barrel_y = gy + 18
            kivy.graphics.Color(0.16, 0.16, 0.22, 1)
            kivy.graphics.Rectangle(pos=(barrel_x, barrel_y), size=(barrel_w, barrel_h))

            # Magazine
            mag_w = 40
            mag_h = 50
            mag_x = gx + 15
            mag_y = gy + gun_h
            kivy.graphics.Color(0.12, 0.12, 0.18, 1)
            kivy.graphics.Rectangle(pos=(mag_x, mag_y), size=(mag_w, mag_h))

            # Pistol grip
            grip_w = 35
            grip_h = 48
            grip_x = gx + 75
            grip_y = gy + gun_h - 10
            kivy.graphics.Color(0.28, 0.22, 0.16, 1)
            kivy.graphics.Rectangle(pos=(grip_x, grip_y), size=(grip_w, grip_h))

            # Stock
            stock_w = 100
            stock_h = 55
            stock_x = gx + gun_w - 60
            stock_y = gy - 8
            kivy.graphics.Color(0.38, 0.30, 0.20, 1)
            kivy.graphics.Rectangle(pos=(stock_x, stock_y), size=(stock_w, stock_h))

            # Right hand
            rhand_x = grip_x + 8
            rhand_y = grip_y + grip_h
            kivy.graphics.Color(0.78, 0.58, 0.48, 1)
            kivy.graphics.Rectangle(pos=(rhand_x - 8, rhand_y), size=(45, 55))

            # Left hand (on foregrip)
            lhand_x = barrel_x + 40
            lhand_y = barrel_y + barrel_h + 8
            kivy.graphics.Color(0.78, 0.58, 0.48, 1)
            kivy.graphics.Rectangle(pos=(lhand_x - 10, lhand_y), size=(50, 58))

            # Sleeves
            kivy.graphics.Color(0.10, 0.13, 0.16, 1)
            kivy.graphics.Rectangle(pos=(rhand_x - 5, rhand_y + 50), size=(55, 130))
            kivy.graphics.Rectangle(pos=(lhand_x - 8, lhand_y + 52), size=(58, 135))

            # Muzzle flash
            if self.weapon.muzzle_flash > 0:
                fs = random.randint(60, 90)
                fx = barrel_x - 25
                fy = barrel_y + barrel_h // 2 - fs // 2
                kivy.graphics.Color(1.0, 0.9, 0.4, 0.95)
                kivy.graphics.Rectangle(pos=(fx, fy), size=(fs, fs))
                kivy.graphics.Color(1.0, 0.5, 0.2, 0.6)
                kivy.graphics.Rectangle(pos=(fx - 15, fy - 15), size=(fs + 30, fs + 30))

    def _draw_hud(self):
        """Draw Doom-style HUD."""
        with self.canvas:
            # Health bar
            kivy.graphics.Color(0.2, 0.2, 0.2, HUD_ALPHA)
            kivy.graphics.Rectangle(pos=(20, self.height-50), size=(240, 30))
            kivy.graphics.Color(*DOOM_COLORS['blood_red'], 1)
            kivy.graphics.Rectangle(pos=(20, self.height-50), size=(240 * self.player.health/100, 30))
            kivy.graphics.Color(1, 1, 1, 1)

            # Armor bar
            kivy.graphics.Color(0.2, 0.2, 0.2, HUD_ALPHA)
            kivy.graphics.Rectangle(pos=(20, self.height-80), size=(240, 25))
            kivy.graphics.Color(*DOOM_COLORS['armor_blue'], 1)
            kivy.graphics.Rectangle(pos=(20, self.height-80), size=(240 * self.player.armor/100, 25))

            # Ammo display
            kivy.graphics.Color(0.2, 0.2, 0.2, HUD_ALPHA)
            kivy.graphics.Rectangle(pos=(self.width-270, self.height-50), size=(250, 30))
            ammo_pct = self.weapon.ammo / self.weapon.max_ammo
            kivy.graphics.Color(*DOOM_COLORS['ammo_yellow'], 1)
            kivy.graphics.Rectangle(pos=(self.width-270, self.height-50), size=(250 * ammo_pct, 30))

            # Stamina bar
            kivy.graphics.Color(0.2, 0.2, 0.2, HUD_ALPHA)
            kivy.graphics.Rectangle(pos=(20, self.height-20), size=(180, 15))
            kivy.graphics.Color(*DOOM_COLORS['health_green'], 1)
            kivy.graphics.Rectangle(pos=(20, self.height-20), size=(180 * self.player.stamina/100, 15))

            # Quest bar
            if self.active_quest:
                kivy.graphics.Color(0.1, 0.1, 0.2, 0.9)
                kivy.graphics.Rectangle(pos=(self.width//2-220, self.height-40), size=(440, 30))
                kivy.graphics.Color(*DOOM_COLORS['warning_orange'], 1)
                prog = self.active_quest.get_progress()
                kivy.graphics.Rectangle(pos=(self.width//2-215, self.height-35), size=(430*prog, 20))

            # Notifications
            for i, (text, time_left) in enumerate(self.notifications[-5:]):
                alpha = min(1, time_left)
                y = self.height//2 + 100 - i*40
                kivy.graphics.Color(0, 0, 0, 0.7*alpha)
                kivy.graphics.Rectangle(pos=(self.width//2-200, y-20), size=(400, 32))
                kivy.graphics.Color(1, 1, 1, alpha)

            # Message bar (Doom-style)
            if self.message_bar_time > 0:
                kivy.graphics.Color(0, 0, 0, 0.8)
                kivy.graphics.Rectangle(pos=(self.width//2-300, 20), size=(600, 35))
                kivy.graphics.Color(1, 1, 0.3, 1)

            # Damage flash
            if self.player.damage_flash > 0:
                kivy.graphics.Color(0.9, 0.1, 0.1, self.player.damage_flash * 0.35)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))

            # Pause overlay
            if self.paused:
                kivy.graphics.Color(0, 0, 0, 0.7)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))
                kivy.graphics.Color(1, 1, 0.3, 1)

            # Game over
            if self.game_over:
                kivy.graphics.Color(0, 0, 0, 0.85)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))
                kivy.graphics.Color(0.9, 0.1, 0.1, 1)

    def _draw_minimap(self):
        """Draw minimap in corner."""
        cell = MINIMAP_CELL_SIZE
        map_w = 32 * cell
        map_h = 32 * cell

        with self.canvas:
            # Background
            kivy.graphics.Color(0, 0, 0, 0.85)
            kivy.graphics.Rectangle(pos=(MINIMAP_PADDING-5, MINIMAP_PADDING-5), size=(map_w+10, map_h+10))
            kivy.graphics.Color(0.05, 0.05, 0.08, 1)
            kivy.graphics.Rectangle(pos=(MINIMAP_PADDING, MINIMAP_PADDING), size=(map_w, map_h))

            # Walls
            for y, row in enumerate(self.map):
                for x, cell_val in enumerate(row):
                    if cell_val > 0:
                        shade = 0.3 + cell_val * 0.15
                        kivy.graphics.Color(shade, shade, shade, 0.9)
                        kivy.graphics.Rectangle(pos=(MINIMAP_PADDING+x*cell, MINIMAP_PADDING+y*cell), size=(cell-1, cell-1))

            # Enemies
            for enemy in self.enemies:
                if enemy.alive:
                    kivy.graphics.Color(0.9, 0.2, 0.2, 0.9)
                    kivy.graphics.Rectangle(pos=(MINIMAP_PADDING+int(enemy.x*cell)-2, MINIMAP_PADDING+int(enemy.y*cell)-2), size=(4, 4))

            # Loot boxes
            for lb in self.loot_boxes:
                if not lb.opened:
                    kivy.graphics.Color(*lb.color, 1)
                    kivy.graphics.Rectangle(pos=(MINIMAP_PADDING+int(lb.x*cell)-2, MINIMAP_PADDING+int(lb.y*cell)-2), size=(4, 4))

            # Player
            px = MINIMAP_PADDING + int(self.raycaster.pos_x * cell)
            py = MINIMAP_PADDING + int(self.raycaster.pos_y * cell)
            kivy.graphics.Color(0.2, 0.95, 0.3, 1)
            kivy.graphics.Rectangle(pos=(px-4, py-4), size=(8, 8))

            # Direction indicator
            kivy.graphics.Color(0.2, 0.95, 0.3, 0.8)
            dir_len = 15
            kivy.graphics.Line(points=[px, py, px+self.raycaster.dir_x*dir_len, py+self.raycaster.dir_y*dir_len], width=2)

    def _draw_touch_controls(self):
        """Draw mobile touch controls."""
        with self.canvas:
            # Virtual Joystick (left side)
            if self.touch_joystick:
                start_x, start_y, curr_x, curr_y = self.touch_joystick
                
                # Joystick base (semi-transparent)
                kivy.graphics.Color(0.2, 0.2, 0.3, 0.4)
                kivy.graphics.Ellipse(pos=(start_x - self.joystick_radius, start_y - self.joystick_radius),
                                     size=(self.joystick_radius * 2, self.joystick_radius * 2))
                
                # Joystick stick (follows touch)
                dx = curr_x - start_x
                dy = curr_y - start_y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance > self.joystick_radius:
                    scale = self.joystick_radius / distance
                    dx *= scale
                    dy *= scale
                
                stick_x = start_x + dx
                stick_y = start_y + dy
                kivy.graphics.Color(0.4, 0.5, 0.6, 0.8)
                kivy.graphics.Ellipse(pos=(stick_x - 25, stick_y - 25), size=(50, 50))
                
                # Direction indicator lines
                kivy.graphics.Color(0.6, 0.7, 0.8, 0.3)
                kivy.graphics.Line(points=[start_x - self.joystick_radius, start_y, 
                                          start_x + self.joystick_radius, start_y], width=2)
                kivy.graphics.Line(points=[start_x, start_y - self.joystick_radius,
                                          start_x, start_y + self.joystick_radius], width=2)
            else:
                # Show joystick hint when not touched
                hint_x = 100
                hint_y = self.height - 100
                kivy.graphics.Color(0.3, 0.3, 0.4, 0.2)
                kivy.graphics.Ellipse(pos=(hint_x - self.joystick_radius, hint_y - self.joystick_radius),
                                     size=(self.joystick_radius * 2, self.joystick_radius * 2))
                kivy.graphics.Color(0.5, 0.6, 0.7, 0.4)
                kivy.graphics.Line(points=[hint_x - self.joystick_radius, hint_y,
                                          hint_x + self.joystick_radius, hint_y], width=2)
                kivy.graphics.Line(points=[hint_x, hint_y - self.joystick_radius,
                                          hint_x, hint_y + self.joystick_radius], width=2)
            
            # Fire button (bottom right, large)
            fire_x = self.width - 120
            fire_y = 80
            fire_r = 50
            
            # Button background
            kivy.graphics.Color(0.7, 0.15, 0.15, 0.5 if not self.mouse_down else 0.8)
            kivy.graphics.Ellipse(pos=(fire_x - fire_r, fire_y - fire_r), size=(fire_r * 2, fire_r * 2))
            
            # Button border
            kivy.graphics.Color(0.9, 0.3, 0.3, 0.9)
            kivy.graphics.Line(ellipse=[fire_x, fire_y, fire_r, fire_r], width=3)
            
            # Fire icon (crosshair)
            kivy.graphics.Color(1, 1, 1, 0.9)
            kivy.graphics.Line(points=[fire_x - 20, fire_y, fire_x + 20, fire_y], width=3)
            kivy.graphics.Line(points=[fire_x, fire_y - 20, fire_x, fire_y + 20], width=3)
            
            # FIRE label
            kivy.graphics.Color(1, 1, 1, 1)
            
            # Reload button (above fire button)
            reload_x = self.width - 120
            reload_y = 180
            reload_r = 40
            
            # Button background
            kivy.graphics.Color(0.2, 0.4, 0.7, 0.5 if 'r' not in self.keys_pressed else 0.8)
            kivy.graphics.Ellipse(pos=(reload_x - reload_r, reload_y - reload_r), size=(reload_r * 2, reload_r * 2))
            
            # Button border
            kivy.graphics.Color(0.4, 0.6, 0.9, 0.9)
            kivy.graphics.Line(ellipse=[reload_x, reload_y, reload_r, reload_r], width=3)
            
            # Reload icon (circular arrow)
            kivy.graphics.Color(1, 1, 1, 0.9)
            kivy.graphics.Line(ellipse=[reload_x, reload_y, 20, 20], width=3)
            
            # Sprint button (top right corner, small)
            sprint_x = self.width - 60
            sprint_y = self.height - 60
            sprint_r = 35
            
            kivy.graphics.Color(0.3, 0.6, 0.3, 0.5 if 'shift' not in self.keys_pressed else 0.8)
            kivy.graphics.Ellipse(pos=(sprint_x - sprint_r, sprint_y - sprint_r), size=(sprint_r * 2, sprint_r * 2))
            kivy.graphics.Color(0.5, 0.8, 0.5, 0.9)
            kivy.graphics.Line(ellipse=[sprint_x, sprint_y, sprint_r, sprint_r], width=2)


class Game3DScreen(kivy.uix.screenmanager.Screen):
    """Game screen container."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = None

    def on_enter(self):
        self.game_widget = Game3DWidget(size=self.size, size_hint=(1, 1))
        self.add_widget(self.game_widget)

    def on_leave(self):
        if self.game_widget:
            if self.game_widget.keyboard:
                self.game_widget.keyboard.release()
            self.remove_widget(self.game_widget)
            self.game_widget = None


class MainMenuScreen(kivy.uix.screenmanager.Screen):
    """Main menu with Doom-style aesthetics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = kivy.uix.floatlayout.FloatLayout()

        self.bg_color = kivy.graphics.Color(0.05, 0.05, 0.1, 1)
        with layout.canvas.before:
            self.bg_rect = kivy.graphics.Rectangle(pos=(0, 0), size=kivy.core.window.Window.size)
        layout.bind(size=lambda w, s: setattr(self.bg_rect, 'size', s))

        # Title
        layout.add_widget(kivy.uix.label.Label(
            text="[b][color=#ff3333]DOOM[/color] [color=#ff8844]SURVIVAL[/color] [color=#44ff66]3D[/color][/b]",
            font_size=68, markup=True, size_hint=(1, None), height=100,
            pos_hint={"center_x": 0.5, "top": 0.75}
        ))

        # Subtitle
        layout.add_widget(kivy.uix.label.Label(
            text="[i]Classic FPS Experience[/i]",
            font_size=24, markup=True, size_hint=(1, None), height=40,
            pos_hint={"center_x": 0.5, "top": 0.68}, color=(0.7, 0.7, 0.8, 1)
        ))

        # Menu buttons
        for text, callback, y in [
            ("START GAME", self.start_game, 0.52),
            ("HOW TO PLAY", self.show_help, 0.42),
            ("QUIT", self.quit_game, 0.32)
        ]:
            btn = kivy.uix.button.Button(
                text=text, size_hint=(None, None), size=(380, 70),
                pos_hint={"center_x": 0.5, "center_y": y},
                font_size=28, background_normal='',
                background_color=(0.15, 0.15, 0.25, 1), color=(1, 1, 1, 1)
            )
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        # Controls hint
        layout.add_widget(kivy.uix.label.Label(
            text="WASD - Move | Mouse - Look | Click - Shoot | R - Reload | Shift - Run",
            font_size=18, size_hint=(1, None), height=35,
            pos_hint={"center_x": 0.5, "y": 0.05}, color=(0.5, 0.5, 0.6, 1)
        ))

        self.add_widget(layout)
        self.anim_t = 0
        kivy.clock.Clock.schedule_interval(self._animate, 1/60)

    def _animate(self, dt):
        self.anim_t += dt
        r = 0.05 + math.sin(self.anim_t * 0.3) * 0.02
        g = 0.05 + math.cos(self.anim_t * 0.2) * 0.02
        b = 0.1 + math.sin(self.anim_t * 0.4) * 0.03
        self.bg_color.r, self.bg_color.g, self.bg_color.b = r, g, b

    def start_game(self, *args):
        self.manager.current = "game"

    def show_help(self, *args):
        self.manager.current = "help"

    def quit_game(self, *args):
        kivy.app.App.get_running_app().stop()


class HelpScreen(kivy.uix.screenmanager.Screen):
    """Help screen with game instructions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = kivy.uix.floatlayout.FloatLayout()

        with layout.canvas.before:
            kivy.graphics.Color(0.05, 0.05, 0.1, 1)
            kivy.graphics.Rectangle(pos=(0, 0), size=kivy.core.window.Window.size)

        # Title
        layout.add_widget(kivy.uix.label.Label(
            text="[b]GAME GUIDE[/b]", font_size=52, markup=True,
            size_hint=(1, None), height=70, pos_hint={"center_x": 0.5, "top": 0.95}
        ))

        # Help text
        help_text = """
[color=#44ff66][b]CONTROLS:[/b][/color]
• WASD / Arrows - Move & Strafe
• Mouse Move - Look Around
• Mouse Click - Shoot (hold for auto)
• R - Reload
• Shift - Sprint/Run
• 1, 2, 3 - Switch Weapons

[color=#44ff66][b]ENEMIES:[/b][/color]
• Green - Normal Zombie (balanced)
• Pale - Fast Zombie (quick but weak)
• Dark - Tank Zombie (slow but tough)
• Burnt - Charred Zombie (aggressive)
• Red/Brown - Demon (dangerous)
• Green Large - Boss Demon (very dangerous)
• Red Sphere - Cacodemon (floating demon)

[color=#44ff66][b]TIPS:[/b][/color]
• Aim for headshots (2.5x damage)
• Watch your ammo - reload when safe
• Use sprint to escape danger
• Collect loot boxes for supplies
• Complete quests for bonus points
• Watch for glowing eyes in the dark!
"""

        scroll = kivy.uix.scrollview.ScrollView(size_hint=(0.85, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})
        content = kivy.uix.label.Label(
            text=help_text, font_size=20, markup=True,
            size_hint_y=None, halign="left", valign="top",
            color=(0.9, 0.9, 0.95, 1), padding=(40, 40)
        )
        content.bind(texture_size=lambda w, v: setattr(w, 'height', v[1] + 80))
        scroll.add_widget(content)
        layout.add_widget(scroll)

        # Back button
        back = kivy.uix.button.Button(
            text="BACK", size_hint=(None, None), size=(250, 55),
            pos_hint={"center_x": 0.5, "y": 0.05}, font_size=22,
            background_normal='', background_color=(0.15, 0.15, 0.25, 1)
        )
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(back)

        self.add_widget(layout)


class ZombieSurvival3DApp(kivy.app.App):
    """Main application class."""

    def build(self):
        self.title = "DOOM-STYLE ZOMBIE SURVIVAL 3D"
        sm = kivy.uix.screenmanager.ScreenManager()
        sm.add_widget(MainMenuScreen(name="menu"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(Game3DScreen(name="game"))
        return sm


if __name__ == "__main__":
    ZombieSurvival3DApp().run()
