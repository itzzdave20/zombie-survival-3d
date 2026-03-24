[app]
title = Doom Zombie Survival 3D
package.name = zombiesurvival3d
package.domain = org.yourname

source.dir = .
source.include_exts = py,png,jpeg,kv,atlas
source.exclude_exts = spec
source.exclude_dirs = docs,tests,__pycache__,.venv,.idea,.compass

orientation = landscape

primary_cpu = arm64-v8a
secondary_cpu = armeabi-v7a

requirements = python3,kivy==2.3.1,Pillow

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = False
android.supports_rtl = False

# Version
version = 1.0.0

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
