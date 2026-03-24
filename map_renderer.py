# map_renderer.py
# Doom-style Raycasting Engine

import math
from texture import TextureGenerator
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FOV, MAX_DEPTH, TEXTURE_SIZE,
    PLAYER_WALK_SPEED, PLAYER_RUN_SPEED, PLAYER_STRAFE_SPEED, PLAYER_BACK_SPEED,
    PLAYER_ROT_SPEED, PLAYER_RADIUS
)


class Raycaster:
    """
    Doom-style 3D Raycasting Engine.
    Implements classic Wolfenstein 3D / Doom raycasting with textures,
    floor/ceiling rendering, and sprite projection.
    """

    def __init__(self, map_data):
        self.map = map_data
        self.map_width = len(map_data[0]) if map_data else 32
        self.map_height = len(map_data) if map_data else 32
        
        # Screen dimensions
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        # Player position (start in center of map)
        self.pos_x = self.map_width / 2.0
        self.pos_y = self.map_height / 2.0
        
        # Direction and plane vectors (for ray casting)
        self.dir_x = -1.0
        self.dir_y = 0.0
        self.plane_x = 0.0
        self.plane_y = FOV  # Field of view
        
        # Movement speeds
        self.move_speed = PLAYER_WALK_SPEED
        self.rot_speed = PLAYER_ROT_SPEED
        self.sprint_multiplier = PLAYER_RUN_SPEED / PLAYER_WALK_SPEED
        
        # Generate wall textures
        self.tex_gen = TextureGenerator()
        self.wall_textures = {
            1: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'brick'),
            2: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'stone'),
            3: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'wood'),
            4: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'metal'),
            5: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'concrete'),
            6: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'tech'),
            7: self.tex_gen.generate_wall_texture(TEXTURE_SIZE, 'hell'),
        }
        
        # Generate floor and ceiling textures
        self.floor_texture = self.tex_gen.generate_floor_texture(TEXTURE_SIZE, 'tile')
        self.ceiling_texture = self.tex_gen.generate_ceiling_texture(TEXTURE_SIZE, 'tiles')
        
        # Z-buffer for sprite occlusion
        self.z_buffer = []

    def set_position(self, x, y):
        """Set player position."""
        self.pos_x = x
        self.pos_y = y

    def set_direction(self, dir_x, dir_y):
        """Set player direction vector."""
        self.dir_x = dir_x
        self.dir_y = dir_y
        # Recalculate plane vector (perpendicular to direction)
        self.plane_x = -dir_y * FOV
        self.plane_y = dir_x * FOV

    def move_forward(self, dt, sprint=False):
        """Move player forward."""
        speed = self.move_speed * dt * (self.sprint_multiplier if sprint else 1.0)
        new_x = self.pos_x + self.dir_x * speed
        new_y = self.pos_y + self.dir_y * speed
        
        # Collision detection with sliding
        if self._can_move_to(new_x, self.pos_y):
            self.pos_x = new_x
        if self._can_move_to(self.pos_x, new_y):
            self.pos_y = new_y

    def move_backward(self, dt):
        """Move player backward."""
        speed = self.move_speed * dt * 0.6
        new_x = self.pos_x - self.dir_x * speed
        new_y = self.pos_y - self.dir_y * speed
        
        if self._can_move_to(new_x, self.pos_y):
            self.pos_x = new_x
        if self._can_move_to(self.pos_x, new_y):
            self.pos_y = new_y

    def strafe_left(self, dt):
        """Strafe left (perpendicular to view direction)."""
        speed = PLAYER_STRAFE_SPEED * dt
        # Perpendicular vector
        perp_x = -self.dir_y
        perp_y = self.dir_x
        
        new_x = self.pos_x + perp_x * speed
        new_y = self.pos_y + perp_y * speed
        
        if self._can_move_to(new_x, self.pos_y):
            self.pos_x = new_x
        if self._can_move_to(self.pos_x, new_y):
            self.pos_y = new_y

    def strafe_right(self, dt):
        """Strafe right (perpendicular to view direction)."""
        speed = PLAYER_STRAFE_SPEED * dt
        perp_x = self.dir_y
        perp_y = -self.dir_x
        
        new_x = self.pos_x + perp_x * speed
        new_y = self.pos_y + perp_y * speed
        
        if self._can_move_to(new_x, self.pos_y):
            self.pos_x = new_x
        if self._can_move_to(self.pos_x, new_y):
            self.pos_y = new_y

    def rotate_left(self, dt):
        """Rotate view to the left."""
        angle = self.rot_speed * dt
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Rotate direction vector
        new_dir_x = self.dir_x * cos_a - self.dir_y * sin_a
        new_dir_y = self.dir_x * sin_a + self.dir_y * cos_a
        self.dir_x = new_dir_x
        self.dir_y = new_dir_y
        
        # Rotate plane vector
        new_plane_x = self.plane_x * cos_a - self.plane_y * sin_a
        new_plane_y = self.plane_x * sin_a + self.plane_y * cos_a
        self.plane_x = new_plane_x
        self.plane_y = new_plane_y

    def rotate_right(self, dt):
        """Rotate view to the right."""
        self.rotate_left(-dt)

    def _can_move_to(self, x, y):
        """Check if position is valid (not inside a wall)."""
        # Check player radius for collision
        for dx in [-PLAYER_RADIUS, 0, PLAYER_RADIUS]:
            for dy in [-PLAYER_RADIUS, 0, PLAYER_RADIUS]:
                check_x = int(x + dx)
                check_y = int(y + dy)
                
                if check_x < 0 or check_y < 0:
                    return False
                if check_x >= self.map_width or check_y >= self.map_height:
                    return False
                if self.map[check_y][check_x] > 0:
                    return False
        return True

    def cast_rays(self):
        """
        Cast rays for all screen columns.
        
        Returns:
            segments: List of wall segments to draw
            z_buffer: Depth buffer for sprite occlusion
        """
        segments = []
        self.z_buffer = []
        
        for x in range(self.screen_width):
            # Calculate ray position and direction
            camera_x = 2 * x / self.screen_width - 1
            ray_dir_x = self.dir_x + self.plane_x * camera_x
            ray_dir_y = self.dir_y + self.plane_y * camera_x
            
            # Which box of the map we're in
            map_x = int(self.pos_x)
            map_y = int(self.pos_y)
            
            # Length of ray from one x or y-side to next x or y-side
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30
            
            # Direction to step in x and y
            step_x = 1 if ray_dir_x > 0 else -1
            step_y = 1 if ray_dir_y > 0 else -1
            
            # Length of ray from current position to next x or y-side
            if ray_dir_x > 0:
                side_dist_x = (map_x + 1.0 - self.pos_x) * delta_dist_x
            else:
                side_dist_x = (self.pos_x - map_x) * delta_dist_x
            
            if ray_dir_y > 0:
                side_dist_y = (map_y + 1.0 - self.pos_y) * delta_dist_y
            else:
                side_dist_y = (self.pos_y - map_y) * delta_dist_y
            
            # Perform DDA
            hit = False
            side = 0  # 0 for NS, 1 for EW
            wall_type = 0
            
            while not hit:
                # Jump to next map square
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                
                # Check if ray has hit a wall
                if map_x < 0 or map_y < 0 or map_x >= self.map_width or map_y >= self.map_height:
                    hit = True
                    wall_type = 0
                elif self.map[map_y][map_x] > 0:
                    hit = True
                    wall_type = self.map[map_y][map_x]
                
                # Check max depth
                if side_dist_x > MAX_DEPTH and side_dist_y > MAX_DEPTH:
                    hit = True
                    wall_type = 0
            
            # Calculate distance projected on camera direction
            if side == 0:
                perp_wall_dist = side_dist_x - delta_dist_x
            else:
                perp_wall_dist = side_dist_y - delta_dist_y
            
            # Store in z-buffer
            self.z_buffer.append(perp_wall_dist)
            
            # Calculate height of line to draw on screen
            if perp_wall_dist > 0:
                line_height = int(self.screen_height / perp_wall_dist)
            else:
                line_height = self.screen_height * 2
            
            # Calculate lowest and highest pixel to fill in current stripe
            draw_start = max(0, -line_height // 2 + self.screen_height // 2)
            draw_end = min(self.screen_height - 1, line_height // 2 + self.screen_height // 2)
            
            # Calculate texture coordinates
            if wall_type > 0:
                if side == 0:
                    wall_x = self.pos_y + perp_wall_dist * ray_dir_y
                else:
                    wall_x = self.pos_x + perp_wall_dist * ray_dir_x
                
                wall_x -= math.floor(wall_x)
                
                # Texture coordinates
                tex_x = int(wall_x * (TEXTURE_SIZE - 1))
                tex_x = max(0, min(TEXTURE_SIZE - 1, tex_x))
            else:
                tex_x = 0
            
            # Add segment
            if wall_type > 0:
                segments.append({
                    'x': x,
                    'draw_start': draw_start,
                    'draw_end': draw_end,
                    'wall_type': wall_type,
                    'wall_x': wall_x,
                    'tex_x': tex_x,
                    'side': side,
                    'distance': perp_wall_dist,
                    'line_height': line_height
                })
        
        return segments, self.z_buffer

    def cast_floor_ceiling(self):
        """
        Cast rays for floor and ceiling rendering.
        Returns floor and ceiling pixel data.
        """
        floor_pixels = []
        ceiling_pixels = []
        
        for y in range(self.screen_height // 2, self.screen_height):
            row_pixels = []
            
            # Ray direction for this row
            ray_dir_y = (y - self.screen_height / 2) / (self.screen_height / 2)
            
            for x in range(self.screen_width):
                camera_x = 2 * x / self.screen_width - 1
                ray_dir_x = self.dir_x + self.plane_x * camera_x
                
                # Normalize
                length = math.sqrt(ray_dir_x * ray_dir_x + ray_dir_y * ray_dir_y)
                ray_dir_x /= length
                ray_dir_y /= length
                
                # Calculate floor position
                if ray_dir_y > 0:
                    dist_to_floor = (self.pos_y - int(self.pos_y)) / ray_dir_y
                else:
                    dist_to_floor = (int(self.pos_y) + 1 - self.pos_y) / (-ray_dir_y)
                
                if dist_to_floor > 0 and dist_to_floor < MAX_DEPTH:
                    floor_x = self.pos_x + dist_to_floor * ray_dir_x
                    floor_y = self.pos_y + dist_to_floor * ray_dir_y
                    
                    # Texture coordinates
                    tex_x = int((floor_x * 2) % TEXTURE_SIZE)
                    tex_y = int((floor_y * 2) % TEXTURE_SIZE)
                    tex_x = max(0, min(TEXTURE_SIZE - 1, tex_x))
                    tex_y = max(0, min(TEXTURE_SIZE - 1, tex_y))
                    
                    row_pixels.append((tex_x, tex_y, dist_to_floor))
                else:
                    row_pixels.append(None)
            
            floor_pixels.append(row_pixels)
        
        return floor_pixels

    def get_light_level(self, distance, side):
        """
        Calculate light level based on distance and wall side.
        Doom-style lighting with distance fog.
        """
        # Base light level
        base_light = 1.0
        
        # Distance fog (exponential)
        fog_factor = math.exp(-distance * 0.08)
        
        # Side shading (walls facing different directions are darker)
        side_shade = 0.85 if side == 1 else 1.0
        
        # Combine
        light = base_light * fog_factor * side_shade
        
        return max(0.15, min(1.0, light))

    def get_texture_for_wall(self, wall_type):
        """Get texture for wall type."""
        return self.wall_textures.get(wall_type, self.wall_textures.get(1))

    def get_sprite_angle(self, sprite_x, sprite_y):
        """
        Calculate angle to sprite relative to player direction.
        
        Returns:
            angle: Angle in radians (positive = right, negative = left)
            distance: Distance to sprite
            visible: Whether sprite is in front of player
        """
        dx = sprite_x - self.pos_x
        dy = sprite_y - self.pos_y
        
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1:
            return 0, 0, False
        
        # Angle to sprite
        sprite_angle = math.atan2(dy, dx)
        player_angle = math.atan2(self.dir_y, self.dir_x)
        
        # Angle difference
        angle_diff = sprite_angle - player_angle
        
        # Normalize to -pi to pi
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        visible = abs(angle_diff) < math.pi / 2
        
        return angle_diff, distance, visible

    def project_sprite(self, sprite_x, sprite_y, sprite_height=1.0):
        """
        Project a sprite onto the screen.
        
        Returns:
            screen_x: X position on screen
            screen_y: Y position on screen (top)
            width: Sprite width in pixels
            height: Sprite height in pixels
            distance: Distance to sprite
            visible: Whether sprite is visible
        """
        angle, distance, visible = self.get_sprite_angle(sprite_x, sprite_y)
        
        if not visible or distance > MAX_DEPTH:
            return 0, 0, 0, 0, distance, False
        
        # Screen position
        screen_x = self.screen_width // 2 + int(angle * self.screen_width / (FOV * 2))
        
        # Sprite dimensions
        base_height = self.screen_height / distance * sprite_height
        height = int(base_height)
        width = int(base_height * 0.6)  # Sprites are narrower than tall
        
        # Position (centered vertically, adjusted for sprite height)
        screen_y = self.screen_height // 2 - height // 2
        
        return screen_x, screen_y, width, height, distance, True
