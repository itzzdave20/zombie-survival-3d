"""
ZOMBIE SURVIVAL 3D - Complete Enhanced Version
3D First-Person Survival Game with Textures, Weapon Model, and Sound
"""

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
import kivy.core.audio
import math
import random
import io

# Window settings
kivy.core.window.Window.size = (1280, 720)
kivy.core.window.Window.clear_color = (0.02, 0.02, 0.05, 1)


# ============== SOUND MANAGER ==============
class SoundManager:
    """Generate and manage game sounds using synthesizer"""
    
    def __init__(self):
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        self.sample_rate = 44100
        
    def generate_tone(self, frequency, duration, volume=0.5, wave_type='sine'):
        """Generate a tone as bytes"""
        import struct
        samples = int(self.sample_rate * duration)
        data = []
        for i in range(samples):
            t = i / self.sample_rate
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = math.sin(2 * math.pi * frequency * t)
            data.append(int(value * volume * 32767))
        return struct.pack('<' + 'h' * len(data), *data)
    
    def play_shoot(self):
        """Play shoot sound"""
        try:
            # Generate gunshot-like sound
            data = self.generate_tone(150, 0.1, 0.8, 'square')
            data += self.generate_tone(100, 0.15, 0.6, 'noise')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume
                sound.play()
        except:
            pass
            
    def play_hit(self):
        """Play hit sound"""
        try:
            data = self.generate_tone(800, 0.1, 0.4, 'sine')
            data += self.generate_tone(600, 0.15, 0.3, 'sine')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume
                sound.play()
        except:
            pass
            
    def play_pickup(self):
        """Play pickup sound"""
        try:
            data = self.generate_tone(1200, 0.08, 0.3, 'sine')
            data += self.generate_tone(1800, 0.12, 0.3, 'sine')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume
                sound.play()
        except:
            pass
            
    def play_zombie_groan(self):
        """Play zombie groan"""
        try:
            data = self.generate_tone(200, 0.3, 0.2, 'sawtooth')
            data += self.generate_tone(150, 0.4, 0.15, 'noise')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume * 0.5
                sound.play()
        except:
            pass
            
    def play_reload(self):
        """Play reload sound"""
        try:
            data = self.generate_tone(400, 0.1, 0.3, 'square')
            data += self.generate_tone(500, 0.15, 0.3, 'square')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume
                sound.play()
        except:
            pass
            
    def play_damage(self):
        """Play damage taken sound"""
        try:
            data = self.generate_tone(150, 0.2, 0.5, 'sawtooth')
            data += self.generate_tone(100, 0.3, 0.4, 'noise')
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(data))
            if sound:
                sound.volume = self.sfx_volume
                sound.play()
        except:
            pass


# ============== TEXTURE GENERATOR ==============
class TextureGenerator:
    """Generate procedural textures"""
    
    @staticmethod
    def generate_wall_texture(size=64, texture_type='brick'):
        """Generate enhanced wall texture with better details and lighting"""
        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                if texture_type == 'brick':
                    # Enhanced brick pattern with depth
                    brick_h, brick_w = 16, 32
                    brick_y = y % brick_h
                    brick_x = (x + (y // brick_h) * 16) % brick_w
                    mortar = brick_y < 2 or brick_x < 2
                    if mortar:
                        # Mortar with variation
                        noise = random.uniform(-0.05, 0.05)
                        r, g, b = 0.35+noise, 0.35+noise, 0.38+noise
                    else:
                        # Brick with color variation and depth
                        noise = random.uniform(-0.08, 0.08)
                        # Add brick surface variation
                        center_dist = abs(8 - brick_y) / 8
                        depth = 0.85 + 0.15 * center_dist
                        r = (0.62 + noise) * depth
                        g = (0.28 + noise * 0.8) * depth
                        b = (0.22 + noise * 0.5) * depth
                        # Add wear and tear
                        if random.random() < 0.03:
                            r, g, b = r * 0.7, g * 0.7, b * 0.7
                elif texture_type == 'stone':
                    # Enhanced stone with cracks and variation
                    noise = random.uniform(-0.12, 0.12)
                    # Perlin-like noise simulation
                    stone_pattern = math.sin(x * 0.15) * math.cos(y * 0.15) * 0.1
                    crack = 1.0
                    if random.random() < 0.02:
                        crack = 0.6
                    base = 0.45 + noise + stone_pattern
                    r = g = b = base * crack
                    # Add mineral veins
                    if random.random() < 0.05:
                        r += 0.1
                        g += 0.05
                        b += 0.15
                elif texture_type == 'wood':
                    # Enhanced wood with grain patterns
                    grain = math.sin(x * 0.4) * 0.08 + math.sin(x * 0.1 + y * 0.05) * 0.05
                    knot = 1.0
                    if random.random() < 0.02:
                        knot = 0.5
                        grain = 0
                    r = (0.55 + grain) * knot
                    g = (0.32 + grain * 0.7) * knot
                    b = (0.18 + grain * 0.3) * knot
                    # Add wood rings
                    ring = math.sin((x + y) * 0.1) * 0.03
                    r += ring
                    g += ring * 0.8
                    b += ring * 0.5
                elif texture_type == 'metal':
                    # Enhanced metal with scratches and panels
                    noise = random.uniform(-0.08, 0.08)
                    panel = 0.95 + 0.05 * math.sin(x * 0.2) * math.cos(y * 0.2)
                    r = (0.42 + noise) * panel
                    g = (0.42 + noise) * panel
                    b = (0.52 + noise) * panel
                    # Add scratches
                    if random.random() < 0.04:
                        scratch = random.uniform(0.6, 0.8)
                        r, g, b = r * scratch, g * scratch, b * scratch
                    # Add rivets
                    if x % 16 < 3 and y % 16 < 3:
                        r, g, b = r * 0.7, g * 0.7, b * 0.7
                else:  # concrete
                    noise = random.uniform(-0.1, 0.1)
                    r = g = b = 0.55 + noise
                    # Add concrete aggregate
                    if random.random() < 0.08:
                        agg = random.uniform(0.7, 0.9)
                        r, g, b = agg, agg, agg
                row.append((r, g, b))
            texture.append(row)
        return texture
    
    @staticmethod
    def generate_zombie_texture(size=32, color=(0.3, 0.7, 0.3), zombie_type="normal"):
        """Generate enhanced zombie body texture with detailed features"""
        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                # Base skin color with variation
                noise = random.uniform(-0.08, 0.08)
                
                # Calculate body regions for better detail placement
                center_x = size // 2
                center_y = size // 2
                dist_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                is_upper_body = y < size // 2
                is_torso = size // 4 < x < 3 * size // 4 and size // 4 < y < 3 * size // 4
                
                # Add detailed rotting/decomposition features
                is_rotted = random.random() < 0.12
                is_bruise = random.random() < 0.08
                is_blood = random.random() < 0.06
                is_wound = random.random() < 0.04
                is_vein = random.random() < 0.1
                
                if is_wound:
                    # Open wounds with flesh details
                    wound_depth = random.uniform(0.3, 0.6)
                    r = 0.6 + noise * wound_depth
                    g = 0.15 + noise * wound_depth
                    b = 0.15 + noise * wound_depth
                elif is_rotted:
                    # Rotten patches (darker, greenish-black)
                    rot_intensity = random.uniform(0.3, 0.6)
                    r = color[0] * rot_intensity + noise
                    g = color[1] * rot_intensity * 0.8 + noise
                    b = color[2] * rot_intensity * 0.5 + noise
                elif is_bruise:
                    # Bruises (purple/dark red with yellow edges)
                    bruise_age = random.uniform(0, 1)
                    if bruise_age < 0.5:
                        r = 0.5 + noise
                        g = 0.2 + noise
                        b = 0.4 + noise
                    else:
                        r = 0.6 + noise
                        g = 0.5 + noise
                        b = 0.2 + noise
                elif is_blood:
                    # Blood stains (dark red with variation)
                    blood_fresh = random.uniform(0, 1)
                    if blood_fresh < 0.3:
                        r = 0.7 + noise
                        g = 0.05 + noise
                        b = 0.05 + noise
                    else:
                        r = 0.4 + noise
                        g = 0.05 + noise
                        b = 0.05 + noise
                elif is_vein:
                    # Visible veins (dark green/purple under skin)
                    r = color[0] * 0.5 + 0.1 + noise
                    g = color[1] * 0.4 + noise
                    b = color[2] * 0.5 + 0.1 + noise
                else:
                    # Normal skin with clothes variation - centered body texture
                    # Clothing area (shirt/torso) - centered and larger
                    clothing_left = size // 4
                    clothing_right = 3 * size // 4
                    clothing_top = size // 3
                    if x > clothing_left and x < clothing_right and y > clothing_top:
                        # Clothing area (shirt) - darker, fabric texture with details
                        fabric_noise = random.uniform(-0.05, 0.05)
                        # Add fabric weave pattern
                        weave = math.sin(x * 0.5) * 0.02 + math.cos(y * 0.5) * 0.02
                        r = color[0] * 0.45 + fabric_noise + weave
                        g = color[1] * 0.45 + fabric_noise + weave
                        b = color[2] * 0.45 + fabric_noise + weave
                        # Add dirt/stains on clothes
                        if random.random() < 0.1:
                            r, g, b = r * 0.7, g * 0.7, b * 0.6
                    else:
                        # Exposed skin (head, arms, legs)
                        # Add skin texture variation
                        skin_texture = math.sin(x * 0.3) * math.cos(y * 0.3) * 0.05
                        r = color[0] + noise + skin_texture
                        g = color[1] + noise + skin_texture
                        b = color[2] + noise + skin_texture
                        # Add bone prominence on thin areas
                        if dist_from_center > size // 3:
                            bone = 0.9 + random.uniform(-0.05, 0.05)
                            r *= bone
                            g *= bone
                            b *= bone

                # Add depth shading (edges darker for 3D effect)
                edge_dist = min(x, y, size-x, size-y) / size
                shade = 0.75 + 0.25 * edge_dist
                r *= shade
                g *= shade
                b *= shade
                
                # Add overall zombie type variation
                if zombie_type == "fast":
                    # Pale, emaciated look
                    r = r * 0.8 + 0.1
                    g = g * 0.7
                    b = b * 0.8 + 0.1
                elif zombie_type == "tank":
                    # Darker, tougher looking
                    r = r * 0.7
                    g = g * 0.6
                    b = b * 0.9
                elif zombie_type == "burnt":
                    # Charred, ashen appearance
                    char = random.uniform(0.3, 0.5)
                    r = r * (0.5 + char) + char * 0.3
                    g = g * (0.3 + char) + char * 0.2
                    b = b * (0.2 + char) + char * 0.1

                # Clamp values
                r = max(0, min(1, r))
                g = max(0, min(1, g))
                b = max(0, min(1, b))

                row.append((r, g, b))
            texture.append(row)
        return texture
    
    @staticmethod
    def generate_weapon_texture(size=32, weapon_type='rifle'):
        """Generate enhanced weapon texture with realistic details"""
        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                if weapon_type == 'rifle':
                    # Enhanced metal gun texture with details
                    noise = random.uniform(-0.03, 0.03)
                    
                    # Different parts of the weapon
                    is_barrel = y < size // 6 or y > 5 * size // 6
                    is_receiver = size // 4 < y < 3 * size // 4
                    is_grip_area = x > size // 2 and size // 4 < y < 3 * size // 4
                    is_rail = size // 3 < y < 2 * size // 3 and x < size // 3
                    
                    if is_rail:
                        # Picatinny rail (textured grip surface)
                        rail_groove = (x // 2) % 4 < 2
                        if rail_groove:
                            r = g = b = 0.25 + noise  # Darker grooves
                        else:
                            r = g = b = 0.35 + noise  # Rail ridges
                    elif is_barrel:
                        # Barrel with heat discoloration and wear
                        wear = random.uniform(0.8, 1.0)
                        heat_stain = 1.0 + math.sin(x * 0.3) * 0.1
                        r = (0.22 + noise) * wear * heat_stain
                        g = (0.22 + noise) * wear * heat_stain
                        b = (0.28 + noise) * wear * heat_stain
                        # Add barrel fluting lines
                        if y % 4 == 0:
                            r, g, b = r * 0.8, g * 0.8, b * 0.8
                    elif is_grip_area:
                        # Polymer grip with texture pattern
                        grip_pattern = math.sin(x * 0.5) * math.cos(y * 0.5) * 0.05
                        r = 0.18 + noise + grip_pattern
                        g = 0.18 + noise + grip_pattern
                        b = 0.20 + noise + grip_pattern
                        # Add grip stippling
                        if random.random() < 0.15:
                            r, g, b = r * 0.9, g * 0.9, b * 0.9
                    elif is_receiver:
                        # Main receiver with wear patterns
                        center_wear = abs(y - size // 2) / (size // 2)
                        wear = 0.85 + 0.15 * center_wear
                        r = (0.28 + noise) * wear
                        g = (0.28 + noise) * wear
                        b = (0.33 + noise) * wear
                        # Add serial number area (lighter patch)
                        if size // 2 < x < 3 * size // 4 and size // 3 < y < 2 * size // 3:
                            if random.random() < 0.3:
                                r, g, b = r * 1.1, g * 1.1, b * 1.1
                    else:
                        # General metal surface
                        r = (0.30 + noise)
                        g = (0.30 + noise)
                        b = (0.35 + noise)
                    
                    # Add scratches and wear across all areas
                    if random.random() < 0.03:
                        scratch = random.uniform(0.5, 0.7)
                        r, g, b = r * scratch, g * scratch, b * scratch
                    
                    # Add oil sheen
                    if random.random() < 0.02:
                        r, g, b = r * 1.1, g * 1.05, b * 1.15
                        
                elif weapon_type == 'pistol':
                    # Pistol texture
                    noise = random.uniform(-0.03, 0.03)
                    is_slide = y < size // 3
                    is_grip = y > size // 2
                    
                    if is_slide:
                        # Blued steel slide
                        r = (0.20 + noise)
                        g = (0.22 + noise)
                        b = (0.28 + noise)
                        # Add slide serrations
                        if x % 6 < 2:
                            r, g, b = r * 0.7, g * 0.7, b * 0.7
                    elif is_grip:
                        # Textured grip
                        grip_tex = math.sin(x * 0.6) * math.cos(y * 0.6) * 0.05
                        r = 0.15 + noise + grip_tex
                        g = 0.15 + noise + grip_tex
                        b = 0.17 + noise + grip_tex
                    else:
                        # Frame
                        r = (0.25 + noise)
                        g = (0.25 + noise)
                        b = (0.30 + noise)
                else:
                    # Default weapon texture
                    noise = random.uniform(-0.05, 0.05)
                    r = g = b = 0.35 + noise
                
                row.append((r, g, b))
            texture.append(row)
        return texture


# ============== GAME CLASSES ==============

class Raycaster:
    """3D Raycasting Engine"""

    def __init__(self, map_data):
        self.map = map_data
        self.map_width = len(map_data[0])
        self.map_height = len(map_data)
        self.screen_width = 320
        self.screen_height = 200

        self.pos_x = 16.0
        self.pos_y = 16.0
        self.dir_x = -1.0
        self.dir_y = 0.0
        self.plane_x = 0.0
        self.plane_y = 0.66

        self.move_speed = 4.0
        self.rot_speed = 2.5
        self.sprint_multiplier = 1.8
        
        # Generate textures
        self.tex_gen = TextureGenerator()
        self.wall_textures = {
            1: self.tex_gen.generate_wall_texture(64, 'brick'),
            2: self.tex_gen.generate_wall_texture(64, 'stone'),
            3: self.tex_gen.generate_wall_texture(64, 'wood'),
            4: self.tex_gen.generate_wall_texture(64, 'metal'),
            5: self.tex_gen.generate_wall_texture(64, 'stone'),
        }

    def move_forward(self, dt, sprint=False):
        speed = self.move_speed * dt * (self.sprint_multiplier if sprint else 1.0)
        new_x = self.pos_x + self.dir_x * speed
        new_y = self.pos_y + self.dir_y * speed
        if 0 <= int(new_y) < self.map_height and 0 <= int(new_x) < self.map_width:
            if self.map[int(new_y)][int(new_x)] == 0:
                self.pos_x, self.pos_y = new_x, new_y

    def move_backward(self, dt):
        speed = self.move_speed * dt * 0.7
        new_x = self.pos_x - self.dir_x * speed
        new_y = self.pos_y - self.dir_y * speed
        if 0 <= int(new_y) < self.map_height and 0 <= int(new_x) < self.map_width:
            if self.map[int(new_y)][int(new_x)] == 0:
                self.pos_x, self.pos_y = new_x, new_y

    def strafe_left(self, dt):
        speed = self.move_speed * dt
        new_x = self.pos_x + self.plane_x * speed
        new_y = self.pos_y + self.plane_y * speed
        if 0 <= int(new_y) < self.map_height and 0 <= int(new_x) < self.map_width:
            if self.map[int(new_y)][int(new_x)] == 0:
                self.pos_x, self.pos_y = new_x, new_y

    def strafe_right(self, dt):
        speed = self.move_speed * dt
        new_x = self.pos_x - self.plane_x * speed
        new_y = self.pos_y - self.plane_y * speed
        if 0 <= int(new_y) < self.map_height and 0 <= int(new_x) < self.map_width:
            if self.map[int(new_y)][int(new_x)] == 0:
                self.pos_x, self.pos_y = new_x, new_y

    def rotate_left(self, dt):
        speed = self.rot_speed * dt
        old_dir = self.dir_x
        self.dir_x = self.dir_x * math.cos(speed) - self.dir_y * math.sin(speed)
        self.dir_y = old_dir * math.sin(speed) + self.dir_y * math.cos(speed)
        old_plane = self.plane_x
        self.plane_x = self.plane_x * math.cos(speed) - self.plane_y * math.sin(speed)
        self.plane_y = old_plane * math.sin(speed) + self.plane_y * math.cos(speed)

    def rotate_right(self, dt):
        self.rotate_left(-dt)

    def cast_rays(self):
        """Cast rays and return wall segments with texture coordinates"""
        segments = []
        z_buffer = []

        for x in range(self.screen_width):
            camera_x = 2 * x / self.screen_width - 1
            ray_dir_x = self.dir_x + self.plane_x * camera_x
            ray_dir_y = self.dir_y + self.plane_y * camera_x

            map_x, map_y = int(self.pos_x), int(self.pos_y)
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30
            step_x = 1 if ray_dir_x > 0 else -1
            step_y = 1 if ray_dir_y > 0 else -1
            side_dist_x = (map_x + 1.0 - self.pos_x) * delta_dist_x if ray_dir_x > 0 else (self.pos_x - map_x) * delta_dist_x
            side_dist_y = (map_y + 1.0 - self.pos_y) * delta_dist_y if ray_dir_y > 0 else (self.pos_y - map_y) * delta_dist_y

            hit, side = False, 0
            while not hit and side_dist_x < 50 and side_dist_y < 50:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                if map_x < 0 or map_y < 0 or map_x >= self.map_width or map_y >= self.map_height:
                    break
                if self.map[map_y][map_x] > 0:
                    hit = True

            if hit:
                perp_dist = side_dist_x - delta_dist_x if side == 0 else side_dist_y - delta_dist_y
                line_height = int(self.screen_height / perp_dist) if perp_dist > 0 else self.screen_height * 2
                draw_start = max(0, -line_height // 2 + self.screen_height // 2)
                draw_end = min(self.screen_height - 1, line_height // 2 + self.screen_height // 2)

                wall_type = self.map[map_y][map_x]
                wall_x = self.pos_y + perp_dist * ray_dir_y if side == 0 else self.pos_x + perp_dist * ray_dir_x
                wall_x -= math.floor(wall_x)
                
                segments.append({
                    'x': x,
                    'draw_start': draw_start,
                    'draw_end': draw_end,
                    'wall_type': wall_type,
                    'wall_x': wall_x,
                    'side': side,
                    'distance': perp_dist
                })
                z_buffer.append(perp_dist)
            else:
                z_buffer.append(1000)

        return segments, z_buffer


class Weapon:
    """Enhanced weapon with model"""
    
    def __init__(self, weapon_type="assault_rifle"):
        self.weapon_type = weapon_type
        self.ammo = 30
        self.max_ammo = 30
        self.reserve_ammo = 90
        self.reload_time = 0
        self.shoot_cooldown = 0
        self.recoil = 0
        self.recoil_y = 0
        self.damage = 25
        self.automatic = True
        self.fire_rate = 0.12
        self.reload_progress = 0
        
        self.weapons = {
            "pistol": {"damage": 35, "ammo": 12, "fire_rate": 0.25, "reserve": 48},
            "assault_rifle": {"damage": 25, "ammo": 30, "fire_rate": 0.12, "reserve": 90},
            "shotgun": {"damage": 15, "ammo": 8, "fire_rate": 0.5, "reserve": 32},
            "sniper": {"damage": 80, "ammo": 5, "fire_rate": 1.0, "reserve": 20},
        }
        
        if weapon_type in self.weapons:
            stats = self.weapons[weapon_type]
            self.damage = stats["damage"]
            self.max_ammo = stats["ammo"]
            self.ammo = self.max_ammo
            self.fire_rate = stats["fire_rate"]
            self.reserve_ammo = stats["reserve"]
        
        # Generate weapon texture
        self.tex_gen = TextureGenerator()
        self.weapon_texture = self.tex_gen.generate_weapon_texture(32, 'rifle')
        
    def shoot(self):
        if self.reload_time > 0 or self.shoot_cooldown > 0 or self.ammo <= 0:
            if self.ammo <= 0:
                self.try_reload()
            return False
        self.ammo -= 1
        self.shoot_cooldown = self.fire_rate
        self.recoil = 12
        self.recoil_y = 8
        return True
    
    def try_reload(self):
        if self.reload_time <= 0 and self.reserve_ammo > 0 and self.ammo < self.max_ammo:
            self.reload_time = 1.5
            self.reload_progress = 0
            return True
        return False
    
    def update(self, dt):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.reload_time > 0:
            self.reload_time -= dt
            self.reload_progress = 1.0 - (self.reload_time / 1.5)
            if self.reload_time <= 0:
                needed = self.max_ammo - self.ammo
                take = min(needed, self.reserve_ammo)
                self.ammo += take
                self.reserve_ammo -= take
        if self.recoil > 0:
            self.recoil -= dt * 30
        if self.recoil_y > 0:
            self.recoil_y -= dt * 25


class Player:
    """Enhanced player character"""
    
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.max_armor = 100
        self.stamina = 100
        self.max_stamina = 100
        self.score = 0
        self.sprinting = False
        self.head_bob = 0
        self.head_bob_timer = 0
        self.taking_damage = False
        self.damage_flash = 0
        self.breathing = 0
        
    def take_damage(self, amount):
        if self.armor > 0:
            armor_absorb = min(self.armor, amount * 0.5)
            self.armor -= armor_absorb
            amount -= armor_absorb
        self.health -= amount
        self.taking_damage = True
        self.damage_flash = 0.4
        return self.health <= 0
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def add_armor(self, amount):
        self.armor = min(self.max_armor, self.armor + amount)
        
    def update(self, dt, moving=False):
        if not self.sprinting and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + dt * 15)
        elif self.sprinting and self.stamina > 0:
            self.stamina -= dt * 25
        else:
            self.sprinting = False
            
        if moving:
            self.head_bob_timer += dt * 12
            self.head_bob = math.sin(self.head_bob_timer) * 4
            self.breathing = math.sin(self.head_bob_timer * 0.5) * 0.5
        else:
            self.head_bob = 0
            self.breathing = math.sin(kivy.clock.Clock.get_time() * 2) * 0.3
            
        if self.damage_flash > 0:
            self.damage_flash -= dt
            
        return self.stamina > 0


class Zombie:
    """Enhanced zombie with body parts and walking animation"""
    
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
        
        self.stats = {
            "normal": {"health": 50, "speed": 1.8, "damage": 10, "color": (0.35, 0.75, 0.35), "height": 1.0},
            "fast": {"health": 35, "speed": 3.2, "damage": 8, "color": (0.85, 0.35, 0.35), "height": 0.9},
            "tank": {"health": 150, "speed": 0.9, "damage": 25, "color": (0.35, 0.35, 0.75), "height": 1.4},
            "burnt": {"health": 70, "speed": 1.6, "damage": 15, "color": (0.65, 0.35, 0.25), "height": 1.0},
            "boss": {"health": 500, "speed": 0.6, "damage": 40, "color": (0.25, 0.55, 0.25), "height": 2.0},
        }
        
        stats = self.stats.get(zombie_type, self.stats["normal"])
        self.health = stats["health"]
        self.max_health = self.health
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.color = stats["color"]
        self.height_mult = stats["height"]
        self.aggro_range = 12.0
        self.attack_range = 1.2
        
        # Generate enhanced texture
        self.tex_gen = TextureGenerator()
        self.texture = self.tex_gen.generate_zombie_texture(32, self.color, zombie_type)
        
    def update(self, player_x, player_y, dt):
        if not self.alive:
            self.death_time += dt
            return False
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
            
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.aggro_range:
            if distance > self.attack_range:
                # Walk towards player with natural gait
                angle = math.atan2(dy, dx)
                
                # Calculate movement
                move_x = math.cos(angle) * self.speed * dt
                move_y = math.sin(angle) * self.speed * dt
                
                # Simple collision avoidance - slide along walls
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # Check if can move
                if self.map_collision_check(new_x, self.y):
                    self.x = new_x
                if self.map_collision_check(self.x, new_y):
                    self.y = new_y
                
                # Update walk animation based on movement
                self.step_timer += dt * self.speed * 2
                self.walk_frame = math.sin(self.step_timer)
                
            elif self.attack_cooldown <= 0:
                self.attack_cooldown = 1.2
                return True
        return False
    
    def map_collision_check(self, x, y):
        """Check if position is walkable"""
        map_x, map_y = int(x), int(y)
        if map_x < 0 or map_y < 0 or map_x >= 32 or map_y >= 32:
            return False
        return True  # Simplified - can move through open areas
    
    def take_damage(self, damage, headshot=False):
        if headshot:
            damage *= 2.5
        self.health -= damage
        self.hit_flash = 0.2
        # Knockback slightly
        self.walk_frame = -0.5  # Stagger animation
        if self.health <= 0:
            self.alive = False
            self.death_time = 0
            return True
        return False
    
    def get_display_size(self, distance):
        base_height = 100 / max(distance, 0.5) * self.height_mult
        return max(20, base_height), max(10, base_height * 0.45)


class Quest:
    """Quest system"""
    
    def __init__(self, quest_type, description, target, reward_score):
        self.quest_type = quest_type
        self.description = description
        self.target = target
        self.current = 0
        self.reward_score = reward_score
        self.completed = False
        
    def update(self, amount=1):
        if not self.completed:
            self.current += amount
            if self.current >= self.target:
                self.completed = True
                return True
        return False
    
    def get_progress(self):
        return min(1.0, self.current / self.target)


class LootBox:
    """Loot box with rewards"""
    
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
        if not self.opened:
            self.float_offset = math.sin(time * 2) * 0.15
            self.rotate_angle = time * 0.5
            
    def open(self, player, weapon):
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
    """Particle effects"""
    
    def __init__(self):
        self.particles = []
        
    def emit(self, x, y, z, vx, vy, vz, color, lifetime, count=1, size=5):
        for _ in range(count):
            self.particles.append({
                'x': x + random.uniform(-0.3, 0.3),
                'y': y + random.uniform(-0.3, 0.3),
                'z': z,
                'vx': vx + random.uniform(-1, 1),
                'vy': vy + random.uniform(-1, 1),
                'vz': vz,
                'color': color,
                'lifetime': lifetime + random.uniform(-0.2, 0.2),
                'max_lifetime': lifetime,
                'size': size + random.uniform(-2, 2)
            })
            
    def update(self, dt):
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['z'] += p['vz'] * dt
            p['vz'] -= dt * 2
            p['lifetime'] -= dt
            if p['lifetime'] <= 0:
                self.particles.remove(p)


# ============== MAIN GAME WIDGET ==============

class Game3DWidget(kivy.uix.widget.Widget):
    """Main 3D Game Widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = kivy.core.window.Window.size
        self.size_hint = (1, 1)
        self.keyboard = None

        # Game state
        self.level = 1
        self.score = 0
        self.kills = 0
        self.game_over = False
        self.paused = False
        self.victory = False
        self.keys_pressed = set()
        self.mouse_down = False
        self.mouse_sensitivity = 0.5  # Smoother mouse
        self.last_mouse_x = None  # Will be set on first mouse move
        
        # Player & Weapon
        self.player = Player()
        self.weapon = Weapon("assault_rifle")
        
        # Notifications first
        self.notifications = []
        self.notification_timer = 0
        
        # Create map
        self.map = self._create_map()
        self.raycaster = Raycaster(self.map)
        
        # Systems
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        
        # Enemies
        self.enemies = []
        self._spawn_enemies(8)
        
        # Quests
        self.active_quest = None
        self.quest_history = []
        self._generate_quest()
        
        # Loot boxes
        self.loot_boxes = []
        self._spawn_loot_boxes(4)
        
        # Setup
        self._setup_keyboard()
        self._setup_ui()
        
        # Game loop at 60 FPS
        kivy.clock.Clock.schedule_interval(self.update, 1.0 / 60.0)

    def _create_map(self):
        size = 32
        world = [[0] * size for _ in range(size)]
        for i in range(size):
            world[0][i] = 1
            world[size-1][i] = 1
            world[i][0] = 1
            world[i][size-1] = 1
        for i in range(6, size-6, 3):
            for j in range(6, size-6, 3):
                if random.random() < 0.25:
                    world[i][j] = random.randint(2, 4)
        for i in range(8, size-8, 4):
            world[i][8] = 2
            world[i][size-9] = 2
            world[8][i] = 3
            world[size-9][i] = 3
        for i in range(13, 20):
            for j in range(13, 20):
                world[i][j] = 0
        return world

    def _spawn_enemies(self, count):
        types = ["normal", "normal", "normal", "fast", "tank", "burnt"]
        for i in range(count):
            x, y = random.uniform(4, 28), random.uniform(4, 28)
            while (self.map[int(y)][int(x)] != 0 or 
                   (abs(x - 16.5) < 6 and abs(y - 16.5) < 6)):
                x, y = random.uniform(4, 28), random.uniform(4, 28)
            # Spawn boss every 5 levels or randomly with low chance
            if self.level % 5 == 0 and i == 0:
                z_type = "boss"  # Boss on level 5, 10, 15...
            elif random.random() < 0.03:  # 3% chance for boss
                z_type = "boss"
            else:
                z_type = random.choice(types)
            self.enemies.append(Zombie(x, y, z_type))

    def _spawn_loot_boxes(self, count):
        for _ in range(count):
            x, y = random.uniform(4, 28), random.uniform(4, 28)
            if self.map[int(y)][int(x)] == 0:
                self.loot_boxes.append(LootBox(x, y))

    def _generate_quest(self):
        quest_types = [
            ("kill", f"Eliminate {5 + self.level * 2} Zombies", 5 + self.level * 2, 200),
            ("survive", f"Survive {30 + self.level * 10} Seconds", 30 + self.level * 10, 150),
        ]
        q_type, desc, target, reward = random.choice(quest_types)
        self.active_quest = Quest(q_type, desc, target, reward)
        self._notify(f"Quest: {desc}", 3.0)

    def _notify(self, text, duration=2.0):
        self.notifications.append((text, duration))

    def _setup_keyboard(self):
        self.keyboard = kivy.core.window.Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_key_down)
        self.keyboard.bind(on_key_up=self._on_key_up)
        # Bind mouse move for looking around
        try:
            kivy.core.window.Window.bind(on_mouse_move=self.on_mouse_move)
        except:
            pass  # Fallback if binding fails

    def _keyboard_closed(self):
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_key_down)
            self.keyboard.unbind(on_key_up=self._on_key_up)
            kivy.core.window.Window.unbind(on_mouse_move=self.on_mouse_move)
            self.keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        if key in ('w', 'up'): self.keys_pressed.add('w')
        if key in ('s', 'down'): self.keys_pressed.add('s')
        if key in ('a', 'left'): self.keys_pressed.add('a')
        if key in ('d', 'right'): self.keys_pressed.add('d')
        # Q/E rotation disabled - using mouse instead
        if key == 'r': self.keys_pressed.add('r')
        if key == 'shift': self.keys_pressed.add('shift')
        if key == 'p': self.paused = not self.paused
        if key == 'escape': self.game_over = True

    def _on_key_up(self, keyboard, keycode):
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        for k in ('w', 's', 'a', 'd', 'r', 'shift'):
            if key == k and k in self.keys_pressed:
                self.keys_pressed.remove(k)

    def _setup_ui(self):
        with self.canvas:
            kivy.graphics.Color(1, 1, 1, 0.9)
            self.crosshair_h = kivy.graphics.Line(
                points=[self.width/2-15, self.height/2, self.width/2+15, self.height/2], width=2)
            self.crosshair_v = kivy.graphics.Line(
                points=[self.width/2, self.height/2-15, self.width/2, self.height/2+15], width=2)

    def _update_crosshair(self):
        if hasattr(self, 'crosshair_h'):
            recoil_offset = self.weapon.recoil_y * 0.8
            spread = (1.0 - self.weapon.ammo / self.weapon.max_ammo) * 5
            self.crosshair_h.points = [
                self.width/2-15-spread, self.height/2+recoil_offset,
                self.width/2+15+spread, self.height/2+recoil_offset
            ]
            self.crosshair_v.points = [
                self.width/2, self.height/2-15-spread+recoil_offset,
                self.width/2, self.height/2+15+spread+recoil_offset
            ]

    def on_mouse_move(self, window, x, y, *args):
        """Handle mouse movement for looking around"""
        if self.game_over or self.paused:
            return
        if self.last_mouse_x is None:
            self.last_mouse_x = x
            return
        dx = x - self.last_mouse_x
        if abs(dx) > 1:
            if dx > 0:
                self.raycaster.rotate_right(0.016 * dx * self.mouse_sensitivity)
            else:
                self.raycaster.rotate_left(0.016 * abs(dx) * self.mouse_sensitivity)
        self.last_mouse_x = x
    
    def on_touch_down(self, touch):
        if not self.game_over and not self.paused:
            self.mouse_down = True
            self._shoot()

    def on_touch_up(self, touch):
        self.mouse_down = False
        self.last_mouse_x = None

    def _shoot(self):
        if self.weapon.shoot():
            self.sound.play_shoot()
            # Muzzle flash particles
            self.particles.emit(
                self.raycaster.pos_x + self.raycaster.dir_x * 0.5,
                self.raycaster.pos_y + self.raycaster.dir_y * 0.5,
                1.5,
                self.raycaster.dir_x * 2,
                self.raycaster.dir_y * 2,
                random.uniform(2, 5),
                (1, 0.8, 0.3), 0.1, count=8, size=8
            )
            
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
                if angle_diff < 0.3 and dist < 20:
                    headshot = random.random() < 0.15
                    killed = enemy.take_damage(self.weapon.damage, headshot)
                    if killed:
                        self.kills += 1
                        self.score += 50
                        self._notify(f"Kill! +50", 1.0)
                        self.sound.play_hit()
                        # Blood
                        self.particles.emit(enemy.x, enemy.y, 1.0, 
                            random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(2, 5),
                            (0.7, 0.1, 0.1), 1.0, count=20, size=6)
                        if self.active_quest and self.active_quest.quest_type == "kill":
                            if self.active_quest.update():
                                self._complete_quest()
                    else:
                        self._notify(f"Hit! ({int(enemy.health)} HP)", 0.8)
                        # Hit sparks
                        self.particles.emit(enemy.x, enemy.y, 1.2,
                            random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(1, 3),
                            (1, 1, 0.5), 0.4, count=8, size=4)
                    break

    def _complete_quest(self):
        q = self.active_quest
        self._notify(f"Quest Complete! +{q.reward_score}", 3.0)
        self.score += q.reward_score
        self.quest_history.append(q)
        self._generate_quest()

    def update(self, dt):
        if self.game_over or self.paused:
            return

        dt = min(dt, 0.05)
        time = kivy.clock.Clock.get_time()
        
        # Mouse look (backup method - check mouse position directly)
        try:
            mouse_x, mouse_y = kivy.core.window.Window.mouse_pos
            if self.last_mouse_x is not None:
                dx = mouse_x - self.last_mouse_x
                if abs(dx) > 2:
                    if dx > 0:
                        self.raycaster.rotate_right(0.016 * dx * self.mouse_sensitivity)
                    else:
                        self.raycaster.rotate_left(0.016 * abs(dx) * self.mouse_sensitivity)
            self.last_mouse_x = mouse_x
        except:
            pass

        # Movement
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
        # Mouse rotation enabled
        if 'r' in self.keys_pressed:
            if self.weapon.try_reload():
                self.sound.play_reload()
        
        self.player.update(dt, moving)
        self.weapon.update(dt)
        
        if self.mouse_down and self.weapon.automatic:
            self._shoot()
        
        # Enemies
        for enemy in self.enemies:
            if enemy.update(self.raycaster.pos_x, self.raycaster.pos_y, dt):
                if self.player.take_damage(enemy.damage):
                    self.game_over = True
                    self.sound.play_damage()
                    self._notify("YOU DIED", 5.0)
                    
        self.enemies = [e for e in self.enemies if e.alive]
        if len(self.enemies) < 5 + self.level:
            self._spawn_enemies(3)
            
        # Loot
        for lb in self.loot_boxes:
            lb.update(time)
        for lb in self.loot_boxes:
            if not lb.opened:
                dist = math.sqrt((lb.x - self.raycaster.pos_x)**2 + (lb.y - self.raycaster.pos_y)**2)
                if dist < 1.5:
                    rewards = lb.open(self.player, self.weapon)
                    for r in rewards:
                        self._notify(r, 1.5)
                    self.sound.play_pickup()
                    
        self.particles.update(dt)
        
        for n in self.notifications[:]:
            n_list = list(n)
            n_list[1] -= dt
            if n_list[1] <= 0:
                self.notifications.remove(n)
                
        if self.active_quest and self.active_quest.quest_type == "survive":
            if self.active_quest.update(dt):
                self._complete_quest()
                
        if self.kills >= self.level * 10:
            self.level += 1
            self.player.heal(25)
            self._notify(f"Level {self.level}!", 2.0)
            self._spawn_loot_boxes(2)
            
        # Render
        self.canvas.clear()
        self._draw_3d()
        self._draw_hud()
        self._draw_minimap()
        self._draw_weapon()
        self._update_crosshair()

    def _draw_3d(self):
        segments, z_buffer = self.raycaster.cast_rays()
        scale_x = self.width / self.raycaster.screen_width
        scale_y = self.height / self.raycaster.screen_height
        head_bob = self.player.head_bob
        time = kivy.clock.Clock.get_time()

        with self.canvas:
            # Enhanced sky with gradient
            for sky_y in range(0, self.height // 2, 8):
                gradient = 1.0 - (sky_y / (self.height // 2))
                r = 0.02 + 0.03 * gradient
                g = 0.02 + 0.04 * gradient
                b = 0.08 + 0.12 * gradient
                kivy.graphics.Color(r, g, b, 1)
                kivy.graphics.Rectangle(pos=(0, self.height // 2 + sky_y), size=(self.width, 8))
            
            # Enhanced floor with gradient
            for floor_y in range(0, self.height // 2, 8):
                gradient = floor_y / (self.height // 2)
                r = 0.08 + 0.04 * gradient
                g = 0.06 + 0.03 * gradient
                b = 0.04 + 0.03 * gradient
                kivy.graphics.Color(r, g, b, 1)
                kivy.graphics.Rectangle(pos=(0, floor_y), size=(self.width, 8))
            
            # Walls with enhanced textures and lighting
            for seg in segments:
                x = seg['x']
                ds = seg['draw_start']
                de = seg['draw_end']
                wall_type = seg['wall_type']
                wall_x = seg['wall_x']
                side = seg['side']
                dist = seg['distance']
                
                # Get texture color
                texture = self.raycaster.wall_textures.get(wall_type, self.raycaster.wall_textures[1])
                tex_x = int(wall_x * 63)
                tex_x = max(0, min(63, tex_x))
                
                # Enhanced lighting model
                base_light = 0.5
                side_shadow = 0.75 if side == 1 else 1.0
                
                # Sample texture at multiple heights with better lighting
                for draw_y in range(ds, de, 4):
                    tex_y = int((draw_y - ds) / max(de - ds, 1) * 63)
                    tex_y = max(0, min(63, tex_y))
                    color = texture[tex_y][tex_x]
                    
                    # Apply side shadow
                    color = tuple(c * side_shadow for c in color)
                    
                    # Enhanced distance fog with color tinting
                    fog = min(1.0, dist / 50.0)
                    fog_color = (0.02, 0.03, 0.05)  # Slightly blue-tinted fog
                    color = tuple(
                        c * (1 - fog * 0.85) + fog_color[i] * fog * 0.85 
                        for i, c in enumerate(color)
                    )
                    
                    # Vertical lighting gradient (top brighter)
                    height_factor = 0.7 + 0.3 * (1 - (draw_y - ds) / max(de - ds, 0.001))
                    color = tuple(c * height_factor for c in color)
                    
                    # Distance-based brightness reduction
                    brightness = max(0.3, 1.0 - dist / 60.0)
                    color = tuple(c * brightness for c in color)
                    
                    kivy.graphics.Color(*color, 1)
                    sx = int(x * scale_x)
                    sy = int(draw_y * scale_y) + head_bob
                    sh = min(4 * scale_y, (de - draw_y) * scale_y)
                    kivy.graphics.Rectangle(pos=(sx, sy), size=(max(2, scale_x), sh))
                
            # Enemies with enhanced 3D bodies and walking animation
            enemy_list = []
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - self.raycaster.pos_x
                dy = enemy.y - self.raycaster.pos_y
                dist = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx)
                player_angle = math.atan2(self.raycaster.dir_y, self.raycaster.dir_x)
                angle_diff = angle - player_angle
                if abs(angle_diff) > math.pi:
                    angle_diff -= 2*math.pi * (1 if angle_diff > 0 else -1)
                if abs(angle_diff) < 1.3 and dist < 25:
                    enemy_list.append((enemy, dist, angle_diff))
                    
            enemy_list.sort(key=lambda e: -e[1])
            
            for enemy, dist, angle_diff in enemy_list:
                sx = self.width//2 + int(angle_diff * self.width//2)
                sy = self.height//2 + int(dist * 8) + head_bob
                h, w = enemy.get_display_size(dist)
                
                # Walking animation offsets with smoother motion
                walk_offset = enemy.walk_frame
                body_sway = walk_offset * 3
                arm_swing = walk_offset * 8
                leg_swing = walk_offset * 10
                head_bob_enemy = abs(math.sin(walk_offset * 3)) * 2
                
                # Enhanced body color with texture sampling and lighting
                base_color = enemy.color
                if enemy.hit_flash > 0:
                    base_color = (1, 1, 1)  # Flash white when hit
                
                # Sample multiple texture points for variation
                tex_x = int(16 + math.sin(walk_offset) * 8)
                tex_y = int(16 + math.cos(walk_offset) * 8)
                if 0 <= tex_x < 32 and 0 <= tex_y < 32:
                    tex_color = enemy.texture[tex_y][tex_x]
                    body_color = tuple(base_color[i] * 0.6 + tex_color[i] * 0.4 for i in range(3))
                else:
                    body_color = base_color
                
                # Distance-based dimming
                dim_factor = max(0.4, 1.0 - dist / 30.0)
                body_color = tuple(c * dim_factor for c in body_color)
                
                # === LEGS (with enhanced pants texture and 3D shading) ===
                leg_w = w * 0.35
                leg_h = h * 0.45
                # Enhanced pants color with wear patterns
                pants_base = (0.22, 0.23, 0.28)
                pants_shadow = tuple(c * 0.7 for c in pants_base)
                
                # Left leg with shading
                left_leg_x = int(sx - w/2 - leg_w/2 + math.sin(leg_swing) * 5)
                left_leg_y = int(sy - leg_h)
                kivy.graphics.Color(*pants_shadow, 0.95)
                kivy.graphics.Rectangle(pos=(left_leg_x, left_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
                kivy.graphics.Color(*pants_base, 0.95)
                kivy.graphics.Rectangle(pos=(left_leg_x + int(leg_w * 0.5), left_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
                
                # Right leg with shading
                right_leg_x = int(sx + w/2 - leg_w/2 - math.sin(leg_swing) * 5)
                right_leg_y = int(sy - leg_h)
                kivy.graphics.Color(*pants_shadow, 0.95)
                kivy.graphics.Rectangle(pos=(right_leg_x, right_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
                kivy.graphics.Color(*pants_base, 0.95)
                kivy.graphics.Rectangle(pos=(right_leg_x + int(leg_w * 0.5), right_leg_y), size=(int(leg_w * 0.5), int(leg_h)))
                
                # Enhanced shoe details
                shoe_color = (0.12, 0.1, 0.08, 1)
                kivy.graphics.Color(*shoe_color, 1)
                kivy.graphics.Rectangle(pos=(left_leg_x, int(sy - leg_h - 6)), size=(int(leg_w), int(6)))
                kivy.graphics.Rectangle(pos=(right_leg_x, int(sy - leg_h - 6)), size=(int(leg_w), int(6)))
                
                # === BODY (with enhanced shirt texture and 3D shading) ===
                body_w = w * 0.9
                body_h = h * 0.55
                body_x = int(sx - body_w/2 + body_sway * 0.3)
                body_y = int(sy - leg_h)
                
                # Body with gradient shading (sides darker)
                kivy.graphics.Color(*tuple(c * 0.6 for c in body_color), 1)
                kivy.graphics.Rectangle(pos=(body_x, body_y), size=(int(body_w * 0.2), int(body_h)))
                kivy.graphics.Color(*body_color, 1)
                kivy.graphics.Rectangle(pos=(int(body_x + body_w * 0.2), body_y), size=(int(body_w * 0.6), int(body_h)))
                kivy.graphics.Color(*tuple(c * 0.75 for c in body_color), 1)
                kivy.graphics.Rectangle(pos=(int(body_x + body_w * 0.8), body_y), size=(int(body_w * 0.2), int(body_h)))
                
                # Enhanced shirt detail (torn, dirty, with texture)
                shirt_color = tuple(body_color[i] * 0.55 for i in range(3))
                kivy.graphics.Color(*shirt_color, 0.95)
                shirt_x = int(sx - body_w/3 + body_sway * 0.3)
                shirt_y = int(sy - leg_h - body_h*0.3)
                kivy.graphics.Rectangle(pos=(shirt_x, shirt_y), size=(int(body_w*0.66), int(body_h*0.45)))
                
                # Blood stains and damage on shirt
                for i in range(3):
                    stain_alpha = 0.5 + random.random() * 0.3
                    kivy.graphics.Color(0.55, 0.08, 0.08, stain_alpha)
                    stain_x = int(sx - body_w/4 + body_sway * 0.3 + math.sin(i * 2.5) * 15)
                    stain_y = int(sy - leg_h - body_h*0.25 + math.cos(i * 1.8) * 10)
                    kivy.graphics.Rectangle(pos=(stain_x, stain_y), size=(int(body_w*0.15), int(body_h*0.12)))
                
                # === HEAD (with enhanced face details and 3D shading) ===
                head_size = w * 0.55
                head_x = int(sx - head_size/2 + body_sway * 0.3)
                head_y = int(sy - leg_h - body_h - head_size*0.15 + head_bob_enemy)
                
                # Head with gradient (top darker, face lighter)
                kivy.graphics.Color(*tuple(c * 0.7 for c in body_color), 1)
                kivy.graphics.Rectangle(pos=(head_x, int(head_y + head_size * 0.5)), size=(int(head_size), int(head_size * 0.5)))
                kivy.graphics.Color(*body_color, 1)
                kivy.graphics.Rectangle(pos=(head_x, head_y), size=(int(head_size), int(head_size * 0.5)))
                
                # Enhanced face details
                # Eye sockets (deep, dark)
                kivy.graphics.Color(0.08, 0.05, 0.05, 0.9)
                eye_socket_y = int(head_y + head_size*0.45)
                kivy.graphics.Rectangle(pos=(int(sx - head_size/3 - 3), eye_socket_y), size=(int(head_size*0.28), int(head_size*0.22)))
                kivy.graphics.Rectangle(pos=(int(sx + head_size/6 - 3), eye_socket_y), size=(int(head_size*0.28), int(head_size*0.22)))
                
                # Glowing eyes with intensity based on distance
                eye_glow = min(1.0, 8.0 / max(dist, 1))
                kivy.graphics.Color(1, 0.1 + eye_glow * 0.1, 0.05, min(1, 0.7 + eye_glow * 0.3))
                es = max(4, int(head_size/4.5))
                ey = int(head_y + head_size*0.52)
                eye_offset_x = int(angle_diff * 3)
                kivy.graphics.Rectangle(pos=(int(sx - head_size/4 + eye_offset_x), ey), size=(es, es))
                kivy.graphics.Rectangle(pos=(int(sx + head_size/8 + eye_offset_x), ey), size=(es, es))
                
                # Enhanced mouth (open, snarling with detail)
                kivy.graphics.Color(0.1, 0.05, 0.05, 0.95)
                mouth_y = int(head_y + head_size*0.75)
                kivy.graphics.Rectangle(pos=(int(sx - head_size/5), mouth_y), size=(int(head_size*0.45), int(head_size*0.18)))
                # Teeth (yellowed, broken)
                kivy.graphics.Color(0.65, 0.58, 0.45, 0.85)
                kivy.graphics.Rectangle(pos=(int(sx - head_size/7), mouth_y + 2), size=(int(head_size*0.35), int(head_size*0.08)))
                # Individual tooth details
                for t in range(4):
                    kivy.graphics.Color(0.55, 0.5, 0.4, 0.7)
                    kivy.graphics.Rectangle(pos=(int(sx - head_size/7 + t * int(head_size*0.09)), mouth_y + 4), size=(int(head_size*0.07), int(head_size*0.06)))
                
                # === ARMS (enhanced with 3D shading and decay details) ===
                arm_w = w * 0.22
                arm_h = h * 0.5
                # Left arm (reaching forward with shading)
                left_arm_x = int(sx - w/2 - arm_w + math.sin(arm_swing) * 8)
                left_arm_y = int(sy - leg_h - arm_h*0.3)
                kivy.graphics.Color(*tuple(c * 0.65 for c in body_color), 0.95)
                kivy.graphics.Rectangle(pos=(left_arm_x, left_arm_y), size=(int(arm_w * 0.4), int(arm_h)))
                kivy.graphics.Color(*body_color, 0.95)
                kivy.graphics.Rectangle(pos=(int(left_arm_x + arm_w * 0.4), left_arm_y), size=(int(arm_w * 0.6), int(arm_h)))
                
                # Right arm with shading
                right_arm_x = int(sx + w/2 - math.sin(arm_swing) * 8 - arm_w)
                right_arm_y = int(sy - leg_h - arm_h*0.3)
                kivy.graphics.Color(*tuple(c * 0.65 for c in body_color), 0.95)
                kivy.graphics.Rectangle(pos=(right_arm_x, right_arm_y), size=(int(arm_w * 0.4), int(arm_h)))
                kivy.graphics.Color(*body_color, 0.95)
                kivy.graphics.Rectangle(pos=(int(right_arm_x + arm_w * 0.4), right_arm_y), size=(int(arm_w * 0.6), int(arm_h)))
                
                # Enhanced hand details (clawed, decayed)
                # Left hand
                left_hand_x = int(sx - w/2 - arm_w*0.5 + math.sin(arm_swing) * 10)
                left_hand_y = int(sy - leg_h - arm_h*0.3 - arm_h*0.25)
                kivy.graphics.Color(*tuple(c * 0.7 for c in body_color), 0.9)
                kivy.graphics.Rectangle(pos=(left_hand_x, left_hand_y), size=(int(arm_w*1.3), int(arm_h*0.28)))
                # Fingers
                kivy.graphics.Color(*tuple(c * 0.55 for c in body_color), 0.9)
                for f in range(4):
                    kivy.graphics.Rectangle(pos=(int(left_hand_x + f * int(arm_w*0.3)), int(left_hand_y - arm_h*0.1)), size=(int(arm_w*0.25), int(arm_h*0.15)))
                
                # Right hand
                right_hand_x = int(sx + w/2 - arm_w*0.7 - math.sin(arm_swing) * 10)
                right_hand_y = int(sy - leg_h - arm_h*0.3 - arm_h*0.25)
                kivy.graphics.Color(*tuple(c * 0.7 for c in body_color), 0.9)
                kivy.graphics.Rectangle(pos=(right_hand_x, right_hand_y), size=(int(arm_w*1.3), int(arm_h*0.28)))
                # Fingers
                for f in range(4):
                    kivy.graphics.Rectangle(pos=(int(right_hand_x + f * int(arm_w*0.3)), int(right_hand_y - arm_h*0.1)), size=(int(arm_w*0.25), int(arm_h*0.15)))
                
                # === HEALTH BAR (enhanced with glow) ===
                hp_pct = enemy.health / enemy.max_health
                bar_x = int(sx - w/2)
                bar_y = int(sy - leg_h - body_h - head_size - 20)
                kivy.graphics.Color(0.2, 0.2, 0.2, 0.9)
                kivy.graphics.Rectangle(pos=(bar_x, bar_y), size=(int(w), 8))
                # Health bar gradient
                if hp_pct > 0.6:
                    hp_color = (0.2, 0.8, 0.2, 1)
                elif hp_pct > 0.3:
                    hp_color = (0.9, 0.7, 0.1, 1)
                else:
                    hp_color = (0.9, 0.15, 0.15, 1)
                kivy.graphics.Color(*hp_color, 1)
                kivy.graphics.Rectangle(pos=(bar_x, bar_y), size=(max(2, int(w*hp_pct)), 8))
                
            # Loot boxes with 3D effect
            for lb in self.loot_boxes:
                if lb.opened:
                    continue
                dx = lb.x - self.raycaster.pos_x
                dy = lb.y - self.raycaster.pos_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 18:
                    angle = math.atan2(dy, dx)
                    player_angle = math.atan2(self.raycaster.dir_y, self.raycaster.dir_x)
                    angle_diff = angle - player_angle
                    if abs(angle_diff) < 1.3:
                        sx = self.width//2 + int(angle_diff * self.width//2)
                        sy = self.height//2 + int(dist * 10) + head_bob
                        size = max(15, int(60 / dist))
                        float_y = lb.float_offset * size
                        
                        # Box with shine
                        kivy.graphics.Color(*lb.color, 1)
                        kivy.graphics.Rectangle(pos=(int(sx-size/2), int(sy-size+float_y)), 
                                               size=(int(size), int(size)))
                        # Shine effect
                        kivy.graphics.Color(1, 1, 1, 0.4)
                        kivy.graphics.Rectangle(pos=(int(sx-size/2+3), int(sy-size+float_y+3)), 
                                               size=(int(size*0.3), int(size*0.3)))
                        # Glow
                        kivy.graphics.Color(*lb.color, 0.3)
                        kivy.graphics.Rectangle(pos=(int(sx-size/2-3), int(sy-size+float_y-3)), 
                                               size=(int(size+6), int(size+6)))
                        
            # Particles
            for p in self.particles.particles:
                dx = p['x'] - self.raycaster.pos_x
                dy = p['y'] - self.raycaster.pos_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 15 and dist > 0.3:
                    angle = math.atan2(dy, dx)
                    player_angle = math.atan2(self.raycaster.dir_y, self.raycaster.dir_x)
                    angle_diff = angle - player_angle
                    if abs(angle_diff) < 1.2:
                        sx = self.width//2 + int(angle_diff * self.width//2)
                        sy = self.height//2 + int(dist * 12) - int(p['z'] * 30) + head_bob
                        alpha = p['lifetime'] / p['max_lifetime']
                        kivy.graphics.Color(*p['color'], alpha)
                        kivy.graphics.Rectangle(pos=(int(sx-p['size']/2), int(sy-p['size']/2)), 
                                               size=(int(p['size']), int(p['size'])))

    def _draw_weapon(self):
        """Draw weapon at BOTTOM of screen"""
        recoil = self.weapon.recoil
        reload_progress = self.weapon.reload_progress
        
        # Weapon position - BOTTOM CENTER (Y=0 is bottom in Kivy)
        base_x = int(self.width * 0.50)
        base_y = int(self.height * 0.15)  # BOTTOM of screen
        
        # Apply recoil
        wx = base_x - int(recoil * 10)
        wy = base_y + int(recoil * 8)
        
        if reload_progress > 0:
            wx = int(self.width * 0.42) + int(reload_progress * 80)
            wy = int(self.height * 0.20) + int(reload_progress * 60)
        
        with self.canvas:
            # === RIGHT ARM (from bottom right) ===
            kivy.graphics.Color(0.10, 0.13, 0.17, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.62), 2), size=(140, 100))
            kivy.graphics.Color(0.12, 0.15, 0.19, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.58), 50), size=(100, 80))
            kivy.graphics.Color(0.82, 0.62, 0.52, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.55), 80), size=(90, 70))
            kivy.graphics.Color(0.12, 0.15, 0.19, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.55), 85), size=(30, 55))
            
            # Right hand
            rhx = wx - 55
            rhy = wy + 5
            kivy.graphics.Color(0.82, 0.62, 0.52, 1)
            kivy.graphics.Rectangle(pos=(rhx, rhy), size=(50, 48))
            kivy.graphics.Color(0.75, 0.55, 0.45, 1)
            for i in range(4):
                kivy.graphics.Rectangle(pos=(rhx + 10 + i*10, rhy - 16), size=(8, 18))
            kivy.graphics.Rectangle(pos=(rhx - 12, rhy + 10), size=(14, 18))
            
            # === LEFT ARM (from bottom left) ===
            kivy.graphics.Color(0.10, 0.13, 0.17, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.24), 2), size=(140, 100))
            kivy.graphics.Color(0.12, 0.15, 0.19, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.30), 50), size=(100, 80))
            kivy.graphics.Color(0.82, 0.62, 0.52, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.36), 80), size=(90, 70))
            kivy.graphics.Color(0.12, 0.15, 0.19, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.42), 85), size=(30, 55))
            kivy.graphics.Color(0.15, 0.15, 0.18, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.415), 75), size=(24, 20))
            kivy.graphics.Color(0.25, 0.45, 0.25, 1)
            kivy.graphics.Rectangle(pos=(int(self.width * 0.42), 78), size=(16, 14))
            
            # Left hand
            lhx = wx + 75
            lhy = wy + 5
            kivy.graphics.Color(0.82, 0.62, 0.52, 1)
            kivy.graphics.Rectangle(pos=(lhx, lhy), size=(52, 48))
            kivy.graphics.Color(0.75, 0.55, 0.45, 1)
            for i in range(4):
                kivy.graphics.Rectangle(pos=(lhx + 8 + i*10, lhy - 16), size=(8, 18))
            kivy.graphics.Rectangle(pos=(lhx + 50, lhy + 10), size=(14, 18))
            
            # === GUN (horizontal) ===
            gun_w = 200
            gun_h = 48
            gx = wx - gun_w // 2
            gy = wy - 18
            
            # Body
            kivy.graphics.Color(0.30, 0.30, 0.36, 1)
            kivy.graphics.Rectangle(pos=(gx, gy), size=(gun_w, gun_h))
            
            # Rail
            kivy.graphics.Color(0.24, 0.24, 0.30, 1)
            kivy.graphics.Rectangle(pos=(gx + 20, gy + gun_h - 6), size=(gun_w - 50, 6))
            
            # Barrel (LEFT)
            barrel_w = 95
            barrel_y = gy + 12
            kivy.graphics.Color(0.20, 0.20, 0.26, 1)
            kivy.graphics.Rectangle(pos=(gx - barrel_w, barrel_y), size=(barrel_w, 16))
            kivy.graphics.Color(0.14, 0.14, 0.20, 1)
            kivy.graphics.Rectangle(pos=(gx - barrel_w + 5, barrel_y + 2), size=(barrel_w - 15, 2))
            kivy.graphics.Rectangle(pos=(gx - barrel_w + 5, barrel_y + 10), size=(barrel_w - 15, 2))
            
            # Handguard
            kivy.graphics.Color(0.32, 0.28, 0.22, 1)
            kivy.graphics.Rectangle(pos=(gx - 35, gy + 8), size=(50, 24))
            kivy.graphics.Color(0.22, 0.18, 0.14, 1)
            for i in range(4):
                kivy.graphics.Rectangle(pos=(gx - 30 + i*12, gy + 12), size=(8, 14))
            
            # Stock (RIGHT)
            kivy.graphics.Color(0.42, 0.34, 0.26, 1)
            kivy.graphics.Rectangle(pos=(gx + gun_w - 12, gy - 5), size=(95, 52))
            kivy.graphics.Color(0.32, 0.26, 0.20, 1)
            kivy.graphics.Rectangle(pos=(gx + gun_w, gy), size=(75, 3))
            kivy.graphics.Rectangle(pos=(gx + gun_w, gy + 12), size=(75, 3))
            kivy.graphics.Rectangle(pos=(gx + gun_w, gy + 25), size=(75, 3))
            kivy.graphics.Color(0.12, 0.12, 0.16, 1)
            kivy.graphics.Rectangle(pos=(gx + gun_w + 78, gy + 3), size=(12, 38))
            
            # Magazine
            mag_x = gx + 38
            mag_y = gy - 48 + int(reload_progress * 40)
            kivy.graphics.Color(0.14, 0.14, 0.20, 1)
            kivy.graphics.Rectangle(pos=(mag_x, mag_y), size=(36, 46))
            kivy.graphics.Color(0.20, 0.20, 0.26, 1)
            for i in range(4):
                kivy.graphics.Rectangle(pos=(mag_x + 4, mag_y + 8 + i*10), size=(28, 3))
            
            # Pistol grip
            grip_x = gx + 58
            grip_y = gy - 28
            kivy.graphics.Color(0.30, 0.26, 0.22, 1)
            kivy.graphics.Rectangle(pos=(grip_x, grip_y), size=(28, 34))
            kivy.graphics.Color(0.20, 0.18, 0.14, 1)
            for i in range(3):
                kivy.graphics.Rectangle(pos=(grip_x + 5, grip_y + 7 + i*7), size=(18, 2))
            
            # Trigger
            kivy.graphics.Color(0.18, 0.18, 0.24, 1)
            kivy.graphics.Rectangle(pos=(grip_x + 28, grip_y - 5), size=(22, 15))
            kivy.graphics.Color(0.22, 0.22, 0.28, 1)
            kivy.graphics.Rectangle(pos=(grip_x + 35, grip_y - 1), size=(5, 9))
            
            # Sights
            kivy.graphics.Color(0.14, 0.14, 0.20, 1)
            kivy.graphics.Rectangle(pos=(gx + gun_w - 42, gy + gun_h - 10), size=(14, 10))
            kivy.graphics.Rectangle(pos=(gx - barrel_w + 22, gy + gun_h - 10), size=(12, 10))
            
            # Muzzle flash
            if recoil > 3:
                fs = random.randint(55, 95)
                fx = gx - barrel_w - 20
                fy = barrel_y + 8 - fs // 2
                kivy.graphics.Color(1.0, 0.92, 0.5, 1.0)
                kivy.graphics.Rectangle(pos=(fx, fy + int(fs*0.25)), size=(int(fs*0.55), int(fs*0.55)))
                kivy.graphics.Color(1.0, 0.80, 0.15, 0.92)
                kivy.graphics.Rectangle(pos=(fx - 6, fy), size=(int(fs*0.75), fs))
                kivy.graphics.Color(1.0, 0.45, 0.1, 0.55)
                kivy.graphics.Rectangle(pos=(fx - int(fs*0.35), fy - int(fs*0.2)), size=(int(fs*1.15), int(fs*1.35)))

    def _draw_hud(self):
        with self.canvas:
            # Health bar
            kivy.graphics.Color(0.25, 0.25, 0.25, 0.9)
            kivy.graphics.Rectangle(pos=(25, self.height-55), size=(220, 28))
            kivy.graphics.Color(0.85, 0.15, 0.15, 1)
            kivy.graphics.Rectangle(pos=(25, self.height-55), size=(220 * self.player.health/100, 28))
            kivy.graphics.Color(1, 1, 1, 1)
            
            # Armor bar
            kivy.graphics.Color(0.25, 0.25, 0.25, 0.9)
            kivy.graphics.Rectangle(pos=(25, self.height-85), size=(220, 22))
            kivy.graphics.Color(0.15, 0.45, 0.85, 1)
            kivy.graphics.Rectangle(pos=(25, self.height-85), size=(220 * self.player.armor/100, 22))
            
            # Ammo with numbers
            kivy.graphics.Color(0.25, 0.25, 0.25, 0.9)
            kivy.graphics.Rectangle(pos=(self.width-250, self.height-55), size=(230, 28))
            ammo_pct = self.weapon.ammo / self.weapon.max_ammo
            kivy.graphics.Color(0.85, 0.75, 0.15, 1)
            kivy.graphics.Rectangle(pos=(self.width-250, self.height-55), size=(230 * ammo_pct, 28))
            kivy.graphics.Color(1, 1, 1, 1)
            
            # Stamina
            kivy.graphics.Color(0.25, 0.25, 0.25, 0.9)
            kivy.graphics.Rectangle(pos=(25, self.height-25), size=(150, 15))
            kivy.graphics.Color(0.25, 0.75, 0.45, 1)
            kivy.graphics.Rectangle(pos=(25, self.height-25), size=(150 * self.player.stamina/100, 15))
            
            # Quest bar
            if self.active_quest:
                kivy.graphics.Color(0.15, 0.15, 0.25, 0.85)
                kivy.graphics.Rectangle(pos=(self.width//2-200, self.height-45), size=(400, 35))
                kivy.graphics.Color(0.9, 0.85, 0.3, 1)
                prog = self.active_quest.get_progress()
                kivy.graphics.Rectangle(pos=(self.width//2-195, self.height-40), size=(390*prog, 25))
                
            # Notifications
            for i, (text, time_left) in enumerate(self.notifications[-4:]):
                alpha = min(1, time_left)
                kivy.graphics.Color(0, 0, 0, 0.7*alpha)
                y = self.height//2 + 80 - i*35
                kivy.graphics.Rectangle(pos=(self.width//2-180, y-18), size=(360, 28))
                kivy.graphics.Color(1, 1, 1, alpha)
                
            # Damage flash
            if self.player.damage_flash > 0:
                kivy.graphics.Color(0.9, 0.1, 0.1, self.player.damage_flash * 0.4)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))
                
            # Reload indicator
            if self.weapon.reload_time > 0:
                kivy.graphics.Color(1, 1, 0.3, 1)
                
            # Pause/Game Over
            if self.paused:
                kivy.graphics.Color(0, 0, 0, 0.7)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))
                kivy.graphics.Color(1, 1, 0.3, 1)
            if self.game_over:
                kivy.graphics.Color(0, 0, 0, 0.85)
                kivy.graphics.Rectangle(pos=(0, 0), size=(self.width, self.height))
                kivy.graphics.Color(0.9, 0.1, 0.1, 1)

    def _draw_minimap(self):
        cell = 4
        map_w = 32 * cell
        map_h = 32 * cell
        
        with self.canvas:
            kivy.graphics.Color(0, 0, 0, 0.8)
            kivy.graphics.Rectangle(pos=(15, 15), size=(map_w+10, map_h+10))
            kivy.graphics.Color(0.05, 0.05, 0.08, 1)
            kivy.graphics.Rectangle(pos=(20, 20), size=(map_w, map_h))
            
            for y, row in enumerate(self.map):
                for x, cell_val in enumerate(row):
                    if cell_val > 0:
                        shade = 0.35 + cell_val * 0.1
                        kivy.graphics.Color(shade, shade, shade, 0.9)
                        kivy.graphics.Rectangle(pos=(20+x*cell, 20+y*cell), size=(cell-1, cell-1))
                        
            for enemy in self.enemies:
                if enemy.alive:
                    kivy.graphics.Color(0.9, 0.2, 0.2, 0.9)
                    kivy.graphics.Rectangle(pos=(20+int(enemy.x*cell)-2, 20+int(enemy.y*cell)-2), size=(4, 4))
                    
            for lb in self.loot_boxes:
                if not lb.opened:
                    kivy.graphics.Color(*lb.color, 1)
                    kivy.graphics.Rectangle(pos=(20+int(lb.x*cell)-2, 20+int(lb.y*cell)-2), size=(4, 4))
                    
            px = 20 + int(self.raycaster.pos_x * cell)
            py = 20 + int(self.raycaster.pos_y * cell)
            kivy.graphics.Color(0.2, 0.95, 0.3, 1)
            kivy.graphics.Rectangle(pos=(px-3, py-3), size=(6, 6))
            kivy.graphics.Color(0.2, 0.95, 0.3, 0.6)
            kivy.graphics.Line(points=[px, py, px+self.raycaster.dir_x*10, py+self.raycaster.dir_y*10], width=2)


# ============== MENU SCREENS ==============

class Game3DScreen(kivy.uix.screenmanager.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = None
        
    def on_enter(self):
        self.game_widget = Game3DWidget()
        self.add_widget(self.game_widget)
        
    def on_leave(self):
        if self.game_widget:
            if self.game_widget.keyboard:
                self.game_widget.keyboard.release()
            self.remove_widget(self.game_widget)
            self.game_widget = None


class MainMenuScreen(kivy.uix.screenmanager.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = kivy.uix.floatlayout.FloatLayout()
        
        self.bg_color = kivy.graphics.Color(0.05, 0.05, 0.12, 1)
        with layout.canvas.before:
            self.bg_rect = kivy.graphics.Rectangle(pos=(0, 0), size=kivy.core.window.Window.size)
        layout.bind(size=lambda w, s: setattr(self.bg_rect, 'size', s))
        
        layout.add_widget(kivy.uix.label.Label(
            text="[b][color=#ff4444]ZOMBIE[/color] [color=#ffaa44]SURVIVAL[/color] [color=#44ff88]3D[/color][/b]",
            font_size=72, markup=True, size_hint=(1, None), height=100,
            pos_hint={"center_x": 0.5, "top": 0.75}
        ))
        
        layout.add_widget(kivy.uix.label.Label(
            text="[i]Complete Edition - Textures, Sound, Weapons[/i]",
            font_size=22, markup=True, size_hint=(1, None), height=40,
            pos_hint={"center_x": 0.5, "top": 0.68}, color=(0.7, 0.7, 0.8, 1)
        ))
        
        for text, callback, y in [
            ("▶ START GAME", self.start_game, 0.52),
            ("📖 HOW TO PLAY", self.show_help, 0.42),
            ("✖ QUIT", self.quit_game, 0.32)
        ]:
            btn = kivy.uix.button.Button(
                text=text, size_hint=(None, None), size=(350, 65),
                pos_hint={"center_x": 0.5, "center_y": y},
                font_size=26, background_normal='',
                background_color=(0.15, 0.15, 0.25, 1), color=(1, 1, 1, 1)
            )
            btn.bind(on_press=callback)
            layout.add_widget(btn)
            
        layout.add_widget(kivy.uix.label.Label(
            text="WASD - Move | Q/E - Rotate | Click - Shoot | R - Reload | Shift - Sprint",
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
        b = 0.12 + math.sin(self.anim_t * 0.4) * 0.03
        self.bg_color.r, self.bg_color.g, self.bg_color.b = r, g, b
        
    def start_game(self, *args):
        self.manager.current = "game"
        
    def show_help(self, *args):
        self.manager.current = "help"
        
    def quit_game(self, *args):
        kivy.app.App.get_running_app().stop()


class HelpScreen(kivy.uix.screenmanager.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = kivy.uix.floatlayout.FloatLayout()
        
        with layout.canvas.before:
            kivy.graphics.Color(0.05, 0.05, 0.1, 1)
            kivy.graphics.Rectangle(pos=(0, 0), size=kivy.core.window.Window.size)
            
        layout.add_widget(kivy.uix.label.Label(
            text="[b]📖 GAME GUIDE[/b]", font_size=52, markup=True,
            size_hint=(1, None), height=70, pos_hint={"center_x": 0.5, "top": 0.95}
        ))
        
        help_text = """
[color=#44ff88][b]CONTROLS:[/b][/color]
• [color=#88ccff]WASD / Arrows[/color] - Move & Strafe
• [color=#88ccff]Q / E[/color] - Rotate View
• [color=#88ccff]Mouse Click[/color] - Shoot (hold for auto)
• [color=#88ccff]R[/color] - Reload
• [color=#88ccff]Shift[/color] - Sprint
• [color=#88ccff]P[/color] - Pause

[color=#44ff88][b]FEATURES:[/b][/color]
• [color=#88ccff]Textured Walls[/color] - Brick, Stone, Wood, Metal
• [color=#88ccff]Zombie Bodies[/color] - Head, Body, Arms with animation
• [color=#88ccff]Weapon Model[/color] - Visible assault rifle with recoil
• [color=#88ccff]Sound Effects[/color] - Shooting, hits, pickups
• [color=#88ccff]Particle Effects[/color] - Blood, muzzle flash, sparks

[color=#44ff88][b]ENEMIES:[/b][/color]
• [color=#88ff88]Green[/color] - Normal (balanced)
• [color=#ff8888]Red[/color] - Fast (quick but weak)
• [color=#8888ff]Blue[/color] - Tank (slow but tough)
• [color=#ff8844]Orange[/color] - Burnt (aggressive)

[color=#44ff88][b]TIPS:[/b][/color]
• Aim for headshots (2.5x damage)
• Watch your ammo - reload when safe
• Use sprint to escape dangerous situations
• Collect loot boxes for supplies
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
        
        back = kivy.uix.button.Button(
            text="◀ BACK", size_hint=(None, None), size=(250, 55),
            pos_hint={"center_x": 0.5, "y": 0.05}, font_size=22,
            background_normal='', background_color=(0.15, 0.15, 0.25, 1)
        )
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(back)
        
        self.add_widget(layout)


# ============== MAIN APP ==============

class ZombieSurvival3DApp(kivy.app.App):
    def build(self):
        self.title = "ZOMBIE SURVIVAL 3D - Complete Edition"
        sm = kivy.uix.screenmanager.ScreenManager()
        sm.add_widget(MainMenuScreen(name="menu"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(Game3DScreen(name="game"))
        return sm


if __name__ == "__main__":
    ZombieSurvival3DApp().run()
