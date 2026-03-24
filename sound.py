# sound.py
# Doom-style Sound Manager with synthesized retro sound effects

import kivy.core.audio
import math
import random
import io
import struct
from settings import AUDIO_SAMPLE_RATE, SFX_VOLUME


class SoundManager:
    """
    Doom-style sound manager using procedural audio synthesis.
    Generates retro-style sound effects similar to classic FPS games.
    """

    def __init__(self):
        self.sfx_volume = SFX_VOLUME
        self.sample_rate = AUDIO_SAMPLE_RATE
        self.enabled = True
        
        # Cache for generated sounds
        self._sound_cache = {}

    def _generate_wave(self, frequency, duration, volume=0.5, wave_type='sine', 
                       attack=0.01, decay=0.1, sustain=0.5, release=0.1):
        """
        Generate a wave with ADSR envelope for more realistic sounds.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            volume: Volume level (0-1)
            wave_type: 'sine', 'square', 'sawtooth', 'triangle', 'noise'
            attack: Attack time in seconds
            decay: Decay time in seconds
            sustain: Sustain level (0-1)
            release: Release time in seconds
        """
        samples = int(self.sample_rate * duration)
        data = []
        
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        sustain_samples = int(sustain * duration * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        for i in range(samples):
            t = i / self.sample_rate
            
            # Generate base waveform
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'sawtooth':
                value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            elif wave_type == 'triangle':
                value = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = math.sin(2 * math.pi * frequency * t)
            
            # Apply frequency modulation for more interesting sounds
            if wave_type in ['sawtooth', 'square']:
                # Add harmonics for richer sound
                value += 0.5 * math.sin(4 * math.pi * frequency * t)
                value += 0.25 * math.sin(6 * math.pi * frequency * t)
            
            # Apply ADSR envelope
            if i < attack_samples:
                envelope = i / attack_samples
            elif i < attack_samples + decay_samples:
                envelope = 1 - (1 - sustain) * ((i - attack_samples) / decay_samples)
            elif i < samples - release_samples:
                envelope = sustain
            else:
                envelope = sustain * (1 - (i - (samples - release_samples)) / release_samples)
            
            # Apply low-pass filter effect (simulate old hardware)
            if i > 0:
                value = value * 0.8 + data[-1] * 0.2 if data else value
            
            data.append(int(value * volume * envelope * 32767))
        
        return struct.pack('<' + 'h' * len(data), *data)

    def _generate_explosion(self, duration=0.4, volume=0.8):
        """Generate explosion/impact sound with noise and frequency sweep."""
        samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(samples):
            t = i / self.sample_rate
            
            # Noise base
            noise = random.uniform(-1, 1)
            
            # Low frequency rumble
            rumble = math.sin(2 * math.pi * 50 * t) * 0.5
            rumble += math.sin(2 * math.pi * 30 * t) * 0.3
            
            # Frequency sweep down (explosion effect)
            sweep_freq = 200 * math.exp(-t * 8)
            sweep = math.sin(2 * math.pi * sweep_freq * t) * 0.4
            
            # Combine
            value = noise * 0.5 + rumble * 0.3 + sweep * 0.2
            
            # Envelope
            envelope = math.exp(-t * 5)
            
            data.append(int(value * volume * envelope * 32767))
        
        return struct.pack('<' + 'h' * len(data), *data)

    def _generate_impact(self, frequency=150, duration=0.2, volume=0.6):
        """Generate impact/hit sound."""
        samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(samples):
            t = i / self.sample_rate
            
            # Square wave with frequency drop
            freq = frequency * math.exp(-t * 15)
            square = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            
            # Noise burst
            noise = random.uniform(-1, 1) * math.exp(-t * 20)
            
            # Combine
            value = square * 0.6 + noise * 0.4
            
            # Envelope
            envelope = math.exp(-t * 10)
            
            data.append(int(value * volume * envelope * 32767))
        
        return struct.pack('<' + 'h' * len(data), *data)

    def _play_sound(self, sound_data, volume=None):
        """Play a generated sound."""
        if not self.enabled:
            return
            
        try:
            # Create WAV file in memory
            wav_data = self._create_wav(sound_data, self.sample_rate)
            sound = kivy.core.audio.SoundLoader.load(io.BytesIO(wav_data))
            if sound:
                sound.volume = volume if volume else self.sfx_volume
                sound.play()
        except Exception as e:
            pass

    def _create_wav(self, data, sample_rate):
        """Create WAV file bytes from raw audio data."""
        import wave
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(data)
        
        return buffer.getvalue()

    def play_shoot(self, weapon_type='rifle'):
        """Play weapon fire sound - Doom-style gunshot."""
        try:
            if weapon_type == 'shotgun':
                # Shotgun: louder, deeper, longer
                data = self._generate_explosion(0.5, 0.9)
                data += self._generate_impact(80, 0.3, 0.7)
            elif weapon_type == 'pistol':
                # Pistol: sharper, shorter
                data = self._generate_impact(200, 0.15, 0.5)
                data += self._generate_wave(150, 0.1, 0.4, 'square')
            elif weapon_type == 'sniper':
                # Sniper: loud crack with echo
                data = self._generate_impact(250, 0.2, 0.8)
                data += self._generate_wave(100, 0.3, 0.3, 'sine')
            else:
                # Assault rifle: rapid fire sound
                data = self._generate_impact(150, 0.12, 0.6)
                data += self._generate_wave(120, 0.08, 0.4, 'square')
            
            self._play_sound(data, self.sfx_volume)
        except:
            pass

    def play_hit(self, hit_type='flesh'):
        """Play enemy hit sound - Doom-style meat impact."""
        try:
            if hit_type == 'flesh':
                # Wet meat impact
                data = self._generate_impact(180, 0.15, 0.5)
                # Add squish effect
                noise_samples = int(self.sample_rate * 0.1)
                noise_data = struct.pack('<' + 'h' * noise_samples, 
                    *[int(random.uniform(-1, 1) * 0.3 * 32767) for _ in range(noise_samples)])
                data += noise_data
            elif hit_type == 'headshot':
                # Crisper sound for headshot
                data = self._generate_wave(600, 0.08, 0.4, 'square')
                data += self._generate_impact(300, 0.1, 0.5)
            else:
                data = self._generate_impact(200, 0.12, 0.5)
            
            self._play_sound(data, self.sfx_volume * 0.8)
        except:
            pass

    def play_pickup(self, pickup_type='item'):
        """Play item pickup sound - Doom-style bonus sound."""
        try:
            if pickup_type == 'health':
                # Rising arpeggio for health
                data = self._generate_wave(440, 0.1, 0.3, 'sine')
                data += self._generate_wave(554, 0.1, 0.3, 'sine')
                data += self._generate_wave(659, 0.15, 0.3, 'sine')
            elif pickup_type == 'ammo':
                # Metallic clink for ammo
                data = self._generate_wave(800, 0.05, 0.25, 'triangle')
                data += self._generate_wave(1200, 0.08, 0.2, 'triangle')
            elif pickup_type == 'armor':
                # Power-up sound
                data = self._generate_wave(300, 0.1, 0.3, 'sawtooth')
                data += self._generate_wave(400, 0.1, 0.3, 'sawtooth')
                data += self._generate_wave(600, 0.2, 0.3, 'sawtooth')
            else:
                # Generic pickup
                data = self._generate_wave(1000, 0.08, 0.3, 'sine')
                data += self._generate_wave(1500, 0.12, 0.3, 'sine')
            
            self._play_sound(data, self.sfx_volume * 0.6)
        except:
            pass

    def play_enemy_death(self, zombie_type='normal'):
        """Play enemy death sound - Doom-style death scream."""
        try:
            # Base groan with pitch variation
            base_freq = random.uniform(120, 200)
            
            # Generate death scream
            data = self._generate_wave(base_freq, 0.3, 0.4, 'sawtooth')
            
            # Add noise for grit
            noise_samples = int(self.sample_rate * 0.3)
            noise_data = struct.pack('<' + 'h' * noise_samples,
                *[int(random.uniform(-1, 1) * 0.2 * 32767) for _ in range(noise_samples)])
            data += noise_data
            
            # Add frequency modulation for scream effect
            mod_samples = int(self.sample_rate * 0.25)
            for i in range(mod_samples):
                t = i / self.sample_rate
                freq = base_freq * math.exp(-t * 3) * (1 + 0.3 * math.sin(20 * math.pi * t))
                sample = int(math.sin(2 * math.pi * freq * t) * 0.3 * 32767 * math.exp(-t * 4))
                data += struct.pack('<h', sample)
            
            self._play_sound(data, self.sfx_volume * 0.7)
        except:
            pass

    def play_reload(self, weapon_type='rifle'):
        """Play reload sound - Doom-style mechanical sounds."""
        try:
            if weapon_type == 'shotgun':
                # Pump action
                data = self._generate_impact(200, 0.1, 0.5)
                data += self._generate_impact(180, 0.15, 0.4)
            elif weapon_type == 'pistol':
                # Slide and magazine
                data = self._generate_impact(300, 0.08, 0.4)
                data += self._generate_impact(250, 0.1, 0.35)
            else:
                # Rifle: magazine out/in, bolt
                data = self._generate_impact(250, 0.08, 0.4)
                data += self._generate_impact(280, 0.1, 0.35)
                data += self._generate_impact(320, 0.12, 0.4)
            
            self._play_sound(data, self.sfx_volume * 0.5)
        except:
            pass

    def play_damage(self):
        """Play player damage sound - Doom-style pain sound."""
        try:
            # Low grunt with noise
            data = self._generate_wave(100, 0.2, 0.5, 'sawtooth')
            
            # Add noise burst
            noise_samples = int(self.sample_rate * 0.15)
            noise_data = struct.pack('<' + 'h' * noise_samples,
                *[int(random.uniform(-1, 1) * 0.3 * 32767) for _ in range(noise_samples)])
            data += noise_data
            
            self._play_sound(data, self.sfx_volume * 0.8)
        except:
            pass

    def play_step(self, surface_type='concrete', is_player=True):
        """Play footstep sound."""
        try:
            if surface_type == 'concrete':
                # Hard click
                data = self._generate_impact(400, 0.05, 0.3)
            elif surface_type == 'metal':
                # Metallic clang
                data = self._generate_wave(600, 0.08, 0.25, 'triangle')
            elif surface_type == 'flesh':
                # Squishy step (zombie)
                data = self._generate_impact(150, 0.06, 0.25)
                noise_samples = int(self.sample_rate * 0.05)
                noise_data = struct.pack('<' + 'h' * noise_samples,
                    *[int(random.uniform(-1, 1) * 0.2 * 32767) for _ in range(noise_samples)])
                data += noise_data
            else:
                data = self._generate_impact(300, 0.05, 0.25)
            
            self._play_sound(data, self.sfx_volume * 0.3)
        except:
            pass

    def play_door(self):
        """Play door opening sound - classic Doom door."""
        try:
            # Mechanical grind
            data = self._generate_wave(80, 0.3, 0.4, 'sawtooth')
            
            # Add mechanical noise
            noise_samples = int(self.sample_rate * 0.3)
            noise_data = struct.pack('<' + 'h' * noise_samples,
                *[int(random.uniform(-1, 1) * 0.15 * 32767) for _ in range(noise_samples)])
            data += noise_data
            
            self._play_sound(data, self.sfx_volume * 0.4)
        except:
            pass

    def play_secret(self):
        """Play secret found sound - Doom-style secret jingle."""
        try:
            # Rising fanfare
            notes = [523, 659, 784, 1047]  # C major arpeggio
            data = b''
            for freq in notes:
                data += self._generate_wave(freq, 0.15, 0.35, 'square')
            
            self._play_sound(data, self.sfx_volume * 0.5)
        except:
            pass

    def play_low_ammo(self):
        """Play low ammo warning click."""
        try:
            data = self._generate_impact(800, 0.05, 0.4)
            self._play_sound(data, self.sfx_volume * 0.4)
        except:
            pass

    def play_level_up(self):
        """Play level up sound."""
        try:
            # Triumphant sound
            notes = [523, 659, 784, 1047, 1319]
            data = b''
            for i, freq in enumerate(notes):
                data += self._generate_wave(freq, 0.2, 0.35, 'square')
            
            self._play_sound(data, self.sfx_volume * 0.5)
        except:
            pass

    def disable(self):
        """Disable sound."""
        self.enabled = False

    def enable(self):
        """Enable sound."""
        self.enabled = True

    def set_volume(self, volume):
        """Set master volume."""
        self.sfx_volume = max(0, min(1, volume))
