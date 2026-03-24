# settings.py
# Doom-style 3D Engine Settings and Configuration

import kivy.core.window

# ============== WINDOW SETTINGS ==============
kivy.core.window.Window.size = (1280, 720)
kivy.core.window.Window.clear_color = (0.0, 0.0, 0.0, 1)
kivy.core.window.Window.title = "DOOM-STYLE SURVIVAL 3D"

# ============== RENDERING SETTINGS ==============
# Screen resolution for raycasting (lower = more retro, faster)
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200

# Field of view (0.66 is classic Doom-style)
FOV = 0.66

# Maximum ray distance
MAX_DEPTH = 50

# Texture resolution
TEXTURE_SIZE = 64

# ============== PLAYER SETTINGS ==============
# Movement speeds (units per second)
PLAYER_WALK_SPEED = 5.0
PLAYER_RUN_SPEED = 9.0
PLAYER_STRAFE_SPEED = 4.5
PLAYER_BACK_SPEED = 3.0

# Rotation speed (radians per second)
PLAYER_ROT_SPEED = 3.0

# Player collision radius
PLAYER_RADIUS = 0.3

# ============== WEAPON SETTINGS ==============
# Weapon bob amount (for walking animation)
WEAPON_BOB_AMOUNT = 8.0
WEAPON_BOB_SPEED = 10.0

# Recoil settings
RECOIL_RECOVERY = 35.0
RECOIL_Y_RECOVERY = 30.0

# ============== ENEMY SETTINGS ==============
# Enemy activation range
ENEMY_AGGRO_RANGE = 18.0
ENEMY_ATTACK_RANGE = 1.2

# Enemy collision radius
ENEMY_RADIUS = 0.35

# ============== PARTICLE SETTINGS ==============
MAX_PARTICLES = 200
GRAVITY = 8.0

# ============== AUDIO SETTINGS ==============
AUDIO_SAMPLE_RATE = 44100
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.5
MUSIC_VOLUME = 0.3

# ============== GAME SETTINGS ==============
TARGET_FPS = 60
MAX_FRAME_TIME = 0.05  # Prevent spiral of death

# ============== HUD SETTINGS ==============
HUD_ALPHA = 0.85
MINIMAP_CELL_SIZE = 4
MINIMAP_PADDING = 20

# Doom-style color palette
DOOM_COLORS = {
    'blood_red': (0.85, 0.15, 0.15),
    'armor_blue': (0.15, 0.45, 0.85),
    'ammo_yellow': (0.85, 0.75, 0.15),
    'health_green': (0.25, 0.75, 0.45),
    'hud_gray': (0.25, 0.25, 0.25),
    'text_white': (1.0, 1.0, 1.0),
    'warning_orange': (0.9, 0.55, 0.15),
}
