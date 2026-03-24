# texture.py
# Doom-style Procedural Texture Generator

import math
import random
import os

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from settings import TEXTURE_SIZE


class TextureGenerator:
    """
    Doom-style procedural texture generator.
    Creates retro-style textures with pixelated aesthetics.
    """

    # Pre-generated texture cache
    _texture_cache = {}

    @staticmethod
    def _noise(x, y, seed=0):
        """Simple deterministic noise function."""
        n = math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453
        return n - math.floor(n)

    @staticmethod
    def _smooth_noise(x, y, size, seed=0):
        """Smooth noise using interpolation."""
        int_x, int_y = int(x), int(y)
        frac_x, frac_y = x - int_x, y - int_y
        
        # Get corner values
        v1 = TextureGenerator._noise(int_x, int_y, seed)
        v2 = TextureGenerator._noise(int_x + 1, int_y, seed)
        v3 = TextureGenerator._noise(int_x, int_y + 1, seed)
        v4 = TextureGenerator._noise(int_x + 1, int_y + 1, seed)
        
        # Smooth interpolation
        fx = frac_x * frac_x * (3 - 2 * frac_x)
        fy = frac_y * frac_y * (3 - 2 * frac_y)
        
        i1 = v1 * (1 - fx) + v2 * fx
        i2 = v3 * (1 - fx) + v4 * fx
        
        return i1 * (1 - fy) + i2 * fy

    @classmethod
    def clear_cache(cls):
        """Clear texture cache."""
        cls._texture_cache.clear()

    @classmethod
    def get_cached_texture(cls, key):
        """Get texture from cache."""
        return cls._texture_cache.get(key)

    @classmethod
    def cache_texture(cls, key, texture):
        """Cache a texture."""
        cls._texture_cache[key] = texture

    @staticmethod
    def load_boss_texture():
        """Load boss zombie texture from image file."""
        if not PIL_AVAILABLE:
            return None

        script_dir = os.path.dirname(os.path.abspath(__file__))
        boss_texture_path = os.path.join(script_dir, 'assets', 'boss_zombie.png')

        if not os.path.exists(boss_texture_path):
            return None

        try:
            img = Image.open(boss_texture_path)
            img = img.convert('RGB')
            img = img.resize((32, 32))

            texture = []
            for y in range(32):
                row = []
                for x in range(32):
                    r, g, b = img.getpixel((x, y))
                    row.append((r / 255.0, g / 255.0, b / 255.0))
                texture.append(row)

            img.close()
            return texture
        except Exception as e:
            print(f"Error loading boss texture: {e}")
            return None

    @staticmethod
    def load_normal_zombie_texture():
        """Load normal zombie texture from image file."""
        if not PIL_AVAILABLE:
            return None

        script_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(script_dir, 'assets', 'normal_zombie.jpeg')

        if not os.path.exists(texture_path):
            return None

        try:
            img = Image.open(texture_path)
            img = img.convert('RGB')
            img = img.resize((32, 32))

            texture = []
            for y in range(32):
                row = []
                for x in range(32):
                    r, g, b = img.getpixel((x, y))
                    row.append((r / 255.0, g / 255.0, b / 255.0))
                texture.append(row)

            img.close()
            return texture
        except Exception as e:
            print(f"Error loading normal zombie texture: {e}")
            return None

    @staticmethod
    def load_fat_zombie_texture():
        """Load fat/tank zombie texture from image file."""
        if not PIL_AVAILABLE:
            return None

        script_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(script_dir, 'assets', 'fat_zombie.jpeg')

        if not os.path.exists(texture_path):
            return None

        try:
            img = Image.open(texture_path)
            img = img.convert('RGB')
            img = img.resize((32, 32))

            texture = []
            for y in range(32):
                row = []
                for x in range(32):
                    r, g, b = img.getpixel((x, y))
                    row.append((r / 255.0, g / 255.0, b / 255.0))
                texture.append(row)

            img.close()
            return texture
        except Exception as e:
            print(f"Error loading fat zombie texture: {e}")
            return None

    @classmethod
    def generate_wall_texture(cls, size=64, texture_type='brick'):
        """Generate Doom-style wall texture with retro aesthetics."""
        cache_key = f"wall_{texture_type}_{size}"
        cached = cls.get_cached_texture(cache_key)
        if cached:
            return cached

        texture = []
        
        for y in range(size):
            row = []
            for x in range(size):
                color = cls._generate_wall_pixel(x, y, size, texture_type)
                row.append(color)
            texture.append(row)
        
        cls.cache_texture(cache_key, texture)
        return texture

    @classmethod
    def _generate_wall_pixel(cls, x, y, size, texture_type):
        """Generate a single wall pixel."""
        if texture_type == 'brick':
            return cls._brick_pixel(x, y, size)
        elif texture_type == 'stone':
            return cls._stone_pixel(x, y, size)
        elif texture_type == 'wood':
            return cls._wood_pixel(x, y, size)
        elif texture_type == 'metal':
            return cls._metal_pixel(x, y, size)
        elif texture_type == 'concrete':
            return cls._concrete_pixel(x, y, size)
        elif texture_type == 'tech':
            return cls._tech_pixel(x, y, size)
        elif texture_type == 'hell':
            return cls._hell_pixel(x, y, size)
        else:
            return cls._brick_pixel(x, y, size)

    @classmethod
    def _brick_pixel(cls, x, y, size):
        """Generate brick texture pixel - Doom E1 style."""
        brick_h, brick_w = size // 4, size // 2
        offset = (y // brick_h) * (brick_w // 2)
        
        brick_x = (x + offset) % brick_w
        brick_y = y % brick_h
        
        # Mortar
        if brick_y < 2 or brick_x < 2:
            noise = cls._noise(x, y, 1) * 0.1
            return (0.3 + noise, 0.28 + noise, 0.32 + noise)
        
        # Brick body with variation
        noise = cls._smooth_noise(x * 0.15, y * 0.15, size, 2) * 0.2
        
        # Classic Doom brick color (reddish-brown)
        base_r = 0.55 + noise
        base_g = 0.25 + noise * 0.5
        base_b = 0.2 + noise * 0.3
        
        # Add wear patterns
        if cls._noise(x, y, 5) > 0.92:
            base_r *= 0.7
            base_g *= 0.7
            base_b *= 0.7
        
        # Add highlights
        if cls._noise(x, y, 8) > 0.95:
            base_r = min(1, base_r * 1.3)
            base_g = min(1, base_g * 1.2)
            base_b = min(1, base_b * 1.1)
        
        return (base_r, base_g, base_b)

    @classmethod
    def _stone_pixel(cls, x, y, size):
        """Generate stone texture pixel."""
        noise = cls._smooth_noise(x * 0.12, y * 0.12, size, 3)
        
        # Base stone color (gray)
        base = 0.4 + noise * 0.3
        
        # Add cracks
        crack = 1.0
        if cls._noise(x * 0.3, y * 0.3, 10) > 0.85:
            crack = 0.6
        
        # Add mineral veins
        vein = 0
        if cls._noise(x * 0.2, y * 0.25, 15) > 0.9:
            vein = 0.1
        
        r = base * crack + vein * 0.1
        g = base * crack + vein * 0.05
        b = base * crack + vein * 0.15
        
        return (r, g, b)

    @classmethod
    def _wood_pixel(cls, x, y, size):
        """Generate wood texture pixel - classic brown wood."""
        # Wood grain pattern
        grain = math.sin(x * 0.3) * 0.08
        grain += math.sin(x * 0.15 + y * 0.05) * 0.05
        
        # Knots
        knot = 1.0
        if cls._noise(x * 0.25, y * 0.25, 20) > 0.92:
            knot = 0.4
            grain = 0
        
        # Ring pattern
        ring = math.sin((x + y) * 0.08) * 0.04
        
        base_r = 0.5 + grain + ring
        base_g = 0.3 + grain * 0.6 + ring * 0.5
        base_b = 0.15 + grain * 0.3 + ring * 0.2
        
        r = base_r * knot
        g = base_g * knot
        b = base_b * knot
        
        return (r, g, b)

    @classmethod
    def _metal_pixel(cls, x, y, size):
        """Generate metal texture pixel - industrial look."""
        noise = cls._noise(x, y, 4) * 0.15
        
        # Panel effect
        panel_x = 1.0 if (x // 16) % 2 == 0 else 0.95
        panel_y = 1.0 if (y // 16) % 2 == 0 else 0.95
        
        # Base metal color (gray-blue)
        base_r = (0.35 + noise) * panel_x * panel_y
        base_g = (0.38 + noise) * panel_x * panel_y
        base_b = (0.45 + noise) * panel_x * panel_y
        
        # Scratches
        if cls._noise(x * 0.5, y, 25) > 0.9:
            scratch = 0.5 + cls._noise(x, y, 26) * 0.3
            base_r *= scratch
            base_g *= scratch
            base_b *= scratch
        
        # Rivets
        if x % 16 < 3 and y % 16 < 3:
            base_r = base_r * 0.6
            base_g = base_g * 0.6
            base_b = base_b * 0.6
        
        # Oil stains
        if cls._noise(x * 0.2, y * 0.2, 30) > 0.93:
            base_r *= 0.85
            base_g *= 0.85
            base_b *= 0.9
        
        return (base_r, base_g, base_b)

    @classmethod
    def _concrete_pixel(cls, x, y, size):
        """Generate concrete texture pixel."""
        noise = cls._smooth_noise(x * 0.2, y * 0.2, size, 5) * 0.2
        
        base = 0.5 + noise
        
        # Aggregate spots
        if cls._noise(x * 0.3, y * 0.3, 35) > 0.85:
            agg = 0.7 + cls._noise(x, y, 36) * 0.2
            base = base * 0.7 + agg * 0.3
        
        # Cracks
        if cls._noise(x * 0.15, y * 0.15, 40) > 0.94:
            base *= 0.6
        
        return (base, base, base)

    @classmethod
    def _tech_pixel(cls, x, y, size):
        """Generate tech/sci-fi wall texture."""
        # Grid pattern
        grid = 0
        if x % 8 < 2 or y % 8 < 2:
            grid = 0.3
        
        # Base tech color (blue-green)
        noise = cls._noise(x, y, 50) * 0.1
        
        base_r = 0.2 + noise + grid
        base_g = 0.35 + noise * 0.8 + grid
        base_b = 0.4 + noise * 0.5 + grid
        
        # Light panels
        if (x // 12) % 3 == 0 and (y // 12) % 3 == 0:
            if cls._noise(x, y, 55) > 0.7:
                base_r = 0.5
                base_g = 0.7
                base_b = 0.8
        
        return (base_r, base_g, base_b)

    @classmethod
    def _hell_pixel(cls, x, y, size):
        """Generate hell/demon texture - Doom E2/E3 style."""
        noise = cls._smooth_noise(x * 0.15, y * 0.15, size, 60) * 0.3
        
        # Base hell color (red-brown)
        base_r = 0.5 + noise
        base_g = 0.15 + noise * 0.3
        base_b = 0.1 + noise * 0.2
        
        # Add organic patterns
        if cls._noise(x * 0.2, y * 0.2, 65) > 0.8:
            base_r = min(1, base_r + 0.2)
            base_g *= 0.8
            base_b *= 0.8
        
        # Add dark spots
        if cls._noise(x * 0.25, y * 0.25, 70) > 0.9:
            base_r *= 0.5
            base_g *= 0.3
            base_b *= 0.3
        
        return (base_r, base_g, base_b)

    @classmethod
    def generate_zombie_texture(cls, size=32, color=(0.3, 0.7, 0.3), zombie_type="normal"):
        """Generate Doom-style zombie/demon texture."""
        cache_key = f"zombie_{zombie_type}_{size}"
        cached = cls.get_cached_texture(cache_key)
        if cached:
            return cached

        # Load textures from image files
        if zombie_type == "boss":
            boss_tex = cls.load_boss_texture()
            if boss_tex:
                cls.cache_texture(cache_key, boss_tex)
                return boss_tex
        elif zombie_type == "normal":
            normal_tex = cls.load_normal_zombie_texture()
            if normal_tex:
                cls.cache_texture(cache_key, normal_tex)
                return normal_tex
        elif zombie_type == "tank":
            fat_tex = cls.load_fat_zombie_texture()
            if fat_tex:
                cls.cache_texture(cache_key, fat_tex)
                return fat_tex

        # Generate procedural texture if image not available
        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                color_val = cls._generate_zombie_pixel(x, y, size, color, zombie_type)
                row.append(color_val)
            texture.append(row)

        cls.cache_texture(cache_key, texture)
        return texture

    @classmethod
    def _generate_zombie_pixel(cls, x, y, size, base_color, zombie_type):
        """Generate a single zombie texture pixel - Doom-style demon/zombie."""
        noise = cls._noise(x, y, 100) * 0.12
        
        # Calculate body regions for detailed rendering
        center_x = size // 2
        is_upper_body = y < size // 2
        is_head = y < size // 4
        is_torso = size // 4 <= y < size * 3 // 4
        
        # Horizontal regions
        is_center = size // 3 < x < size * 2 // 3
        is_left = x < size // 3
        is_right = x > size * 2 // 3
        
        if zombie_type == "normal":
            # Classic green zombie with tattered shirt
            if is_head:
                # Green decaying face
                r = 0.35 + noise * 0.2
                g = 0.65 + noise * 0.25
                b = 0.3 + noise * 0.15
                # Dark eye sockets
                if (y > size // 8 and y < size // 5) and (is_left or is_right):
                    r, g, b = 0.1, 0.05, 0.05
                # Open mouth area
                if y > size // 5 and is_center:
                    r, g, b = 0.4, 0.1, 0.1
            elif is_torso:
                # Tattered brown/green shirt
                if is_center:
                    r = 0.35 + noise * 0.15
                    g = 0.35 + noise * 0.12
                    b = 0.25 + noise * 0.1
                    # Blood stains on shirt
                    if cls._noise(x, y, 105) > 0.75:
                        r = 0.55 + noise
                        g = 0.15 + noise
                        b = 0.15 + noise
                else:
                    # Exposed rotting arms
                    r = 0.32 + noise * 0.2
                    g = 0.58 + noise * 0.2
                    b = 0.28 + noise * 0.15
            else:
                # Dark pants
                r = 0.18 + noise * 0.1
                g = 0.2 + noise * 0.1
                b = 0.25 + noise * 0.12
            
            # Add rotting spots
            if cls._noise(x * 0.4, y * 0.4, 110) > 0.88:
                r *= 0.7
                g *= 0.8
                b *= 0.6
            
            return (r, g, b)
        
        elif zombie_type == "fast":
            # Pale, emaciated runner zombie
            if is_head:
                # Gaunt pale face
                r = 0.75 + noise * 0.15
                g = 0.65 + noise * 0.12
                b = 0.6 + noise * 0.1
                # Sunken black eyes
                if (y > size // 8 and y < size // 5) and (is_left or is_right):
                    r, g, b = 0.15, 0.1, 0.15
            elif is_torso:
                # Torn gray tank top
                if is_center:
                    r = 0.45 + noise * 0.1
                    g = 0.45 + noise * 0.1
                    b = 0.5 + noise * 0.12
                else:
                    # Bony arms
                    r = 0.7 + noise * 0.15
                    g = 0.6 + noise * 0.12
                    b = 0.55 + noise * 0.1
            else:
                # Torn shorts
                r = 0.25 + noise * 0.1
                g = 0.3 + noise * 0.1
                b = 0.35 + noise * 0.12
            
            return (r, g, b)
        
        elif zombie_type == "tank":
            # Large, dark armored zombie
            if is_head:
                # Thick dark skin
                r = 0.25 + noise * 0.1
                g = 0.3 + noise * 0.12
                b = 0.35 + noise * 0.15
                # Glowing red eyes
                if (y > size // 8 and y < size // 5):
                    if is_left:
                        r, g, b = 0.9, 0.15, 0.1
                    elif is_right:
                        r, g, b = 0.9, 0.15, 0.1
            elif is_torso:
                # Heavy armored vest
                r = 0.2 + noise * 0.08
                g = 0.25 + noise * 0.1
                b = 0.3 + noise * 0.12
                # Metal plates
                if x % 6 < 2:
                    r += 0.1
                    g += 0.1
                    b += 0.15
            else:
                # Heavy dark pants
                r = 0.15 + noise * 0.08
                g = 0.18 + noise * 0.1
                b = 0.22 + noise * 0.12
            
            return (r, g, b)
        
        elif zombie_type == "burnt":
            # Charred, ashen zombie
            if is_head:
                # Burnt skull visible
                r = 0.45 + noise * 0.15
                g = 0.35 + noise * 0.12
                b = 0.25 + noise * 0.1
                # Glowing orange eyes
                if (y > size // 8 and y < size // 5):
                    if is_left or is_right:
                        r, g, b = 0.9, 0.4, 0.1
            elif is_torso:
                # Charred remains with exposed muscle
                if cls._noise(x, y, 115) > 0.6:
                    # Burnt black areas
                    r = 0.2 + noise * 0.1
                    g = 0.15 + noise * 0.08
                    b = 0.12 + noise * 0.08
                else:
                    # Exposed red muscle
                    r = 0.55 + noise * 0.15
                    g = 0.2 + noise * 0.1
                    b = 0.15 + noise * 0.08
            else:
                # Burnt legs
                r = 0.25 + noise * 0.1
                g = 0.18 + noise * 0.08
                b = 0.15 + noise * 0.08
            
            return (r, g, b)
        
        elif zombie_type == "demon":
            # Hell demon - brown/red creature
            if is_head:
                # Demonic face with horns suggestion
                r = 0.65 + noise * 0.15
                g = 0.35 + noise * 0.1
                b = 0.2 + noise * 0.08
                # Glowing yellow eyes
                if (y > size // 8 and y < size // 5):
                    if is_left:
                        r, g, b = 1.0, 0.8, 0.1
                    elif is_right:
                        r, g, b = 1.0, 0.8, 0.1
            elif is_torso:
                # Muscular demon body
                r = 0.6 + noise * 0.12
                g = 0.3 + noise * 0.1
                b = 0.18 + noise * 0.08
                # Dark markings/tattoos
                if cls._noise(x * 0.3, y * 0.3, 120) > 0.7:
                    r *= 0.6
                    g *= 0.5
                    b *= 0.4
            else:
                # Digitigrade legs suggestion
                r = 0.55 + noise * 0.12
                g = 0.28 + noise * 0.1
                b = 0.15 + noise * 0.08
            
            return (r, g, b)
        
        elif zombie_type == "boss":
            # Boss demon - larger, more detailed
            if is_head:
                # Massive demon head
                r = 0.4 + noise * 0.15
                g = 0.55 + noise * 0.18
                b = 0.35 + noise * 0.12
                # Large glowing eyes
                if (y > size // 6 and y < size // 3):
                    if is_left:
                        r, g, b = 1.0, 0.2, 0.05
                    elif is_right:
                        r, g, b = 1.0, 0.2, 0.05
                # Horn bases at top
                if y < size // 6:
                    r = 0.3 + noise * 0.1
                    g = 0.25 + noise * 0.08
                    b = 0.2 + noise * 0.08
            elif is_torso:
                # Armored demon chest
                r = 0.35 + noise * 0.12
                g = 0.5 + noise * 0.15
                b = 0.3 + noise * 0.1
                # Rib-like armor plates
                if y % 5 < 2:
                    r += 0.15
                    g += 0.1
                    b += 0.05
            else:
                # Heavy lower body
                r = 0.3 + noise * 0.1
                g = 0.45 + noise * 0.12
                b = 0.25 + noise * 0.08
            
            # Scar patterns
            if cls._noise(x * 0.25, y * 0.25, 125) > 0.8:
                r *= 0.7
                g *= 0.6
                b *= 0.5
            
            return (r, g, b)
        
        elif zombie_type == "cacodemon":
            # Floating ball demon - red sphere with face
            # Circular pattern
            dist_from_center = math.sqrt((x - center_x)**2 + (y - size//2)**2) / (size // 2)
            
            if dist_from_center > 0.9:
                # Outer red edge
                r = 0.8 + noise * 0.15
                g = 0.15 + noise * 0.08
                b = 0.15 + noise * 0.08
            elif dist_from_center > 0.7:
                # Main red body
                r = 0.85 + noise * 0.1
                g = 0.2 + noise * 0.08
                b = 0.2 + noise * 0.08
            elif dist_from_center > 0.4:
                # Face area - darker
                r = 0.5 + noise * 0.15
                g = 0.1 + noise * 0.05
                b = 0.1 + noise * 0.05
                # Single large eye in center
                if dist_from_center < 0.25:
                    r, g, b = 1.0, 0.9, 0.2
            else:
                # Mouth area
                r = 0.3 + noise * 0.1
                g = 0.05 + noise * 0.03
                b = 0.05 + noise * 0.03
            
            return (r, g, b)
        
        else:
            # Default zombie
            return (base_color[0] + noise, base_color[1] + noise, base_color[2] + noise)

    @classmethod
    def generate_weapon_texture(cls, size=32, weapon_type='rifle'):
        """Generate Doom-style weapon texture."""
        cache_key = f"weapon_{weapon_type}_{size}"
        cached = cls.get_cached_texture(cache_key)
        if cached:
            return cached

        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                color_val = cls._generate_weapon_pixel(x, y, size, weapon_type)
                row.append(color_val)
            texture.append(row)
        
        cls.cache_texture(cache_key, texture)
        return texture

    @classmethod
    def _generate_weapon_pixel(cls, x, y, size, weapon_type):
        """Generate a single weapon texture pixel."""
        noise = cls._noise(x, y, 200) * 0.08
        
        if weapon_type == 'rifle':
            # Assault rifle - dark metal
            is_barrel = y < size // 6 or y > 5 * size // 6
            is_receiver = size // 4 < y < 3 * size // 4
            
            if is_barrel:
                # Barrel with wear
                r = 0.18 + noise
                g = 0.18 + noise
                b = 0.22 + noise
            elif is_receiver:
                # Main body
                r = 0.25 + noise
                g = 0.25 + noise
                b = 0.30 + noise
            else:
                # Other parts
                r = 0.22 + noise
                g = 0.22 + noise
                b = 0.27 + noise
            
            # Scratches
            if cls._noise(x, y, 205) > 0.92:
                r *= 0.6
                g *= 0.6
                b *= 0.6
            
            return (r, g, b)
        
        elif weapon_type == 'pistol':
            # Pistol - darker
            r = 0.20 + noise
            g = 0.22 + noise
            b = 0.28 + noise
            return (r, g, b)
        
        elif weapon_type == 'shotgun':
            # Shotgun - worn metal and wood
            if y > size * 0.6:
                # Wood stock
                r = 0.45 + noise
                g = 0.28 + noise
                b = 0.15 + noise
            else:
                # Metal barrel
                r = 0.15 + noise
                g = 0.15 + noise
                b = 0.20 + noise
            return (r, g, b)
        
        elif weapon_type == 'sniper':
            # Sniper rifle
            r = 0.12 + noise * 0.5
            g = 0.12 + noise * 0.5
            b = 0.15 + noise * 0.5
            return (r, g, b)
        
        else:
            return (0.25 + noise, 0.25 + noise, 0.30 + noise)

    @classmethod
    def generate_floor_texture(cls, size=64, texture_type='tile'):
        """Generate floor texture."""
        cache_key = f"floor_{texture_type}_{size}"
        cached = cls.get_cached_texture(cache_key)
        if cached:
            return cached

        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                color_val = cls._generate_floor_pixel(x, y, size, texture_type)
                row.append(color_val)
            texture.append(row)
        
        cls.cache_texture(cache_key, texture)
        return texture

    @classmethod
    def _generate_floor_pixel(cls, x, y, size, texture_type):
        """Generate a single floor pixel."""
        noise = cls._noise(x, y, 300) * 0.1
        
        if texture_type == 'tile':
            # Grid pattern for tiles
            grid_x = 1.0 if (x // 8) % 2 == 0 else 0.9
            grid_y = 1.0 if (y // 8) % 2 == 0 else 0.9
            
            # Grout lines
            if x % 8 < 2 or y % 8 < 2:
                return (0.25, 0.25, 0.28)
            
            base = (0.45 + noise) * grid_x * grid_y
            return (base, base, base)
        
        elif texture_type == 'metal':
            # Metal floor with grating
            if x % 4 < 2:
                base = 0.35 + noise
            else:
                base = 0.25 + noise
            
            return (base, base, base + 0.05)
        
        elif texture_type == 'blood':
            # Blood-stained floor
            base = 0.3 + noise * 0.2
            
            # Blood splatters
            if cls._noise(x * 0.15, y * 0.15, 310) > 0.8:
                return (0.5, 0.1, 0.1)
            
            return (base, base * 0.9, base * 0.9)
        
        else:
            # Default concrete
            base = 0.4 + noise
            return (base, base, base)

    @classmethod
    def generate_ceiling_texture(cls, size=64, texture_type='ceiling'):
        """Generate ceiling texture."""
        cache_key = f"ceiling_{texture_type}_{size}"
        cached = cls.get_cached_texture(cache_key)
        if cached:
            return cached

        texture = []
        for y in range(size):
            row = []
            for x in range(size):
                noise = cls._noise(x, y, 400) * 0.08
                base = 0.15 + noise
                
                if texture_type == 'tiles':
                    # Ceiling tiles
                    if x % 16 < 2 or y % 16 < 2:
                        base = 0.1
                
                row.append((base, base, base + 0.05))
            texture.append(row)
        
        cls.cache_texture(cache_key, texture)
        return texture

    @classmethod
    def generate_particle_texture(cls, size=16, particle_type='blood'):
        """Generate particle texture with soft edges."""
        texture = []
        center = size // 2
        
        for y in range(size):
            row = []
            for x in range(size):
                dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                max_dist = size / 2
                
                if dist > max_dist:
                    alpha = 0
                else:
                    alpha = 1 - (dist / max_dist)
                    alpha = alpha ** 0.5  # Soft edge
                
                if particle_type == 'blood':
                    color = (0.8, 0.1, 0.1, alpha)
                elif particle_type == 'spark':
                    color = (1.0, 0.8, 0.3, alpha)
                elif particle_type == 'smoke':
                    gray = 0.3 + cls._noise(x, y, 500) * 0.2
                    color = (gray, gray, gray, alpha * 0.5)
                else:
                    color = (1.0, 1.0, 1.0, alpha)
                
                row.append(color)
            texture.append(row)
        
        return texture
