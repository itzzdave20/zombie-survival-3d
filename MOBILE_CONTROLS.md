# Mobile Controls for Doom Zombie Survival 3D

## Touch Controls Added

The game now has full mobile touch controls:

### Left Side - Virtual Joystick
- **Touch anywhere on the left half** of the screen to activate the virtual joystick
- **Drag up/down/left/right** to move (WASD)
- The joystick shows a visual indicator with direction lines

### Right Side - Look Control
- **Swipe horizontally** on the right side to look around
- Touch and drag left/right to rotate the view

### Action Buttons (Right Side)

1. **Fire Button** (Large red button, bottom right)
   - Tap to shoot
   - Hold for automatic fire (with automatic weapons)

2. **Reload Button** (Blue button, above fire button)
   - Tap to reload your weapon

3. **Sprint Button** (Green button, top right corner)
   - Hold to sprint (faster movement, drains stamina)

## Building for Android

### Prerequisites

1. **Linux or macOS** (Buildozer doesn't work natively on Windows)
2. **Python 3.7+**
3. **Git**
4. **Java JDK 8+**
5. **Android SDK & NDK** (Buildozer can download these automatically)

### Installation

```bash
# Navigate to project directory
cd /Users/stuartjamesrichkeane/PycharmProjects/survival-game

# Activate virtual environment
source .venv/bin/activate

# Install buildozer
pip install buildozer

# Install additional dependencies
pip install Pillow

# Initialize buildozer (creates buildozer.spec)
buildozer init
```

### Build APK

```bash
# Debug build (for testing)
buildozer -v android debug

# Release build (for publishing)
buildozer -v android release
```

The APK will be in the `bin/` folder.

### Deploy to Device

```bash
# Connect your Android device via USB (with USB debugging enabled)
# Then run:
buildozer android deploy run
```

Or manually copy the APK from `bin/` to your phone and install it.

## Building for iOS

### Prerequisites

1. **macOS** (required)
2. **Xcode** (latest version)
3. **Apple Developer Account** (for device deployment)

### Installation

```bash
cd /Users/stuartjamesrichkeane/PycharmProjects/survival-game
source .venv/bin/activate

# Install kivy-ios
pip install kivy-ios

# Build toolchain
toolchain build python3 kivy pillow
```

### Create Xcode Project

```bash
toolchain create ZombieSurvival3D /Users/stuartjamesrichkeane/PycharmProjects/survival-game
```

### Deploy to iOS

1. Open the generated Xcode project
2. Select your development team
3. Connect your iPhone/iPad
4. Build and run (Cmd+R)

## Testing on Desktop

The touch controls work on desktop too! You can test them:

```bash
cd /Users/stuartjamesrichkeane/PycharmProjects/survival-game
source .venv/bin/activate
python main.py
```

- **Mouse click on left side** = Virtual joystick
- **Mouse drag on right side** = Look around
- **Mouse click buttons** = Fire/Reload/Sprint

## Troubleshooting

### Build fails with "SDK not found"
```bash
buildozer android sdk
```

### App crashes on startup
Check logcat:
```bash
buildozer android logcat
```

### Touch controls not responding
- Make sure the game window is in focus
- Try restarting the app
- Check that touch input is enabled on your device

## Performance Tips

1. **Lower screen resolution** in `settings.py` for better FPS
2. **Reduce SCREEN_WIDTH/SCREEN_HEIGHT** for faster rendering
3. **Disable minimap** if performance is poor
4. **Reduce particle count** in `ParticleSystem`

## Next Steps

1. Test the touch controls on desktop first
2. Build debug APK
3. Test on your Android device
4. Adjust control positions/sizes if needed
5. Build release APK for distribution
