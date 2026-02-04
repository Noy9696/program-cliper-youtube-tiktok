import subprocess
import os
from datetime import datetime

# ========================================
# 📱 TIKTOK VIDEO OPTIMIZER - CORE ENGINE
# 🎵 WITH ADVANCED AUDIO MIXING + SOUND EFFECTS
# ========================================

FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"

def get_video_info(video_path):
    """Ambil info video (durasi, resolusi, fps)"""
    cmd = [
        FFMPEG,
        "-i", video_path,
        "-hide_banner"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = result.stderr
    
    # Parse info
    duration = 0
    width = 0
    height = 0
    fps = 0
    bitrate = 0
    has_audio = False
    
    for line in info.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = time_str.split(':')
            duration = float(h) * 3600 + float(m) * 60 + float(s)
        
        if 'Audio:' in line:
            has_audio = True
        
        if 'Video:' in line:
            # Cari resolusi
            if 'x' in line:
                parts = line.split(',')
                for part in parts:
                    if 'x' in part and not 'max' in part:
                        try:
                            res = part.strip().split()[0]
                            width, height = map(int, res.split('x'))
                            break
                        except:
                            pass
            
            # Cari FPS
            if 'fps' in line or 'tbr' in line:
                parts = line.split(',')
                for part in parts:
                    if 'fps' in part or 'tbr' in part:
                        try:
                            fps = float(part.strip().split()[0])
                            break
                        except:
                            pass
        
        if 'bitrate:' in line and 'Duration:' in line:
            try:
                bitrate_str = line.split('bitrate:')[1].split()[0]
                bitrate = int(bitrate_str)
            except:
                pass
    
    return {
        'duration': duration,
        'width': width,
        'height': height,
        'fps': fps,
        'bitrate': bitrate,
        'has_audio': has_audio
    }

def optimize_for_tiktok(input_path, output_path, preset='standard', audio_config=None, sound_effects=None):
    """
    Optimize video untuk TikTok - ANTI-COMPRESS VERSION
    Dengan advanced audio mixing + sound effects
    """
    
    print(f"\n🔍 Analyzing video...")
    info = get_video_info(input_path)
    
    print(f"\n📊 Video Info:")
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   Duration: {info['duration']:.2f}s")
    print(f"   FPS: {info['fps']}")
    print(f"   Current bitrate: {info['bitrate']} kb/s")
    print(f"   Has audio: {'✓ Yes' if info['has_audio'] else '✗ No'}")
    
    # Default configs
    if audio_config is None:
        audio_config = {
            'use_external_audio': False,
            'keep_original': True,
            'original_volume': 100,
            'external_volume': 0
        }
    
    if sound_effects is None:
        sound_effects = []
    
    # ========================================
    # 🎯 TIKTOK-OPTIMIZED SETTINGS
    # ========================================
    
    settings = {
        'maximum': {
            'video_bitrate': '12M',
            'maxrate': '14M',
            'bufsize': '24M',
            'crf': '18',
            'preset': 'slow',
            'audio_bitrate': '192k',
            'description': '💎 MAXIMUM - 12 Mbps (Best Quality)',
            'sharpness': 1.2
        },
        'standard': {
            'video_bitrate': '10M',
            'maxrate': '12M',
            'bufsize': '20M',
            'crf': '19',
            'preset': 'slow',
            'audio_bitrate': '192k',
            'description': '⭐ STANDARD - 10 Mbps (Recommended)',
            'sharpness': 1.0
        },
        'balanced': {
            'video_bitrate': '8M',
            'maxrate': '10M',
            'bufsize': '16M',
            'crf': '20',
            'preset': 'medium',
            'audio_bitrate': '128k',
            'description': '✅ BALANCED - 8 Mbps (Fast Upload)',
            'sharpness': 0.8
        }
    }
    
    s = settings[preset]
    
    print(f"\n🎨 Using preset: {preset.upper()}")
    print(f"   {s['description']}")
    print(f"   Target: 1080x1920 @ 30fps")
    print(f"   Bitrate: {s['video_bitrate']}")
    
    # ========================================
    # 🎵 AUDIO CONFIGURATION SUMMARY
    # ========================================
    print(f"\n🎵 Audio Configuration:")
    if audio_config['use_external_audio']:
        if audio_config['keep_original']:
            print(f"   🔊 Mode: MIXING")
            print(f"   🎬 Audio Asli: {audio_config['original_volume']}%")
            print(f"   🎵 Background: {audio_config['external_volume']}%")
        else:
            print(f"   🔊 Mode: REPLACE")
            print(f"   🎵 Background baru menggantikan audio asli")
    else:
        print(f"   🔊 Mode: ORIGINAL")
        print(f"   🎬 Menggunakan audio video asli")
    
    if sound_effects:
        print(f"\n🎬 Sound Effects: {len(sound_effects)} effects")
        for i, sfx in enumerate(sound_effects, 1):
            print(f"   {i}. {sfx['name']}")
            print(f"      ⏱️  At {sfx['timestamp']}s, Vol: {sfx['volume']}%")
    
    # ========================================
    # 🎬 TIKTOK-SAFE FILTER CHAIN
    # ========================================
    
    # Deteksi orientasi video
    if info['width'] > info['height']:
        print("   ⚠️  Landscape detected, will rotate to portrait")
        base_filters = [
            "transpose=1",
            f"scale=1080:1920:flags=lanczos:force_original_aspect_ratio=decrease",
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
        ]
    else:
        base_filters = [
            f"scale=1080:1920:flags=lanczos:force_original_aspect_ratio=decrease",
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
        ]
    
    # Enhancement filters
    enhancement_filters = [
        f"unsharp=5:5:{s['sharpness']}:5:5:0.0",
        "eq=contrast=1.05:brightness=0.01:saturation=1.05",
        "hqdn3d=1.0:1.0:4:4"
    ]
    
    vf = base_filters + enhancement_filters
    
    # Deteksi FPS
    target_fps = "30"
    if info['fps'] > 0:
        if info['fps'] <= 30:
            target_fps = str(int(info['fps']))
            print(f"   📹 Keeping original FPS: {target_fps}")
        else:
            print(f"   📹 Converting {info['fps']}fps → 30fps")
    
    # ========================================
    # 🎵 BUILD FFMPEG COMMAND
    # ========================================
    
    cmd = [FFMPEG, "-y"]
    
    # Input video
    cmd.extend(["-i", input_path])
    
    # Input audio background jika ada
    if audio_config['use_external_audio']:
        cmd.extend(["-i", audio_config['external_audio_path']])
    
    # Input sound effects
    for sfx in sound_effects:
        cmd.extend(["-i", sfx['path']])
    
    # Video filters
    cmd.extend(["-vf", ",".join(vf)])
    
    # ========================================
    # 🎚️ AUDIO FILTER COMPLEX - ADVANCED
    # ========================================
    
    # Hitung total input audio
    total_inputs = 1  # Video
    if audio_config['use_external_audio']:
        total_inputs += 1  # Background audio
    sfx_start_index = total_inputs
    total_inputs += len(sound_effects)
    
    # Build filter complex
    filter_parts = []
    audio_streams = []
    
    # 1. Process original video audio
    if info['has_audio']:
        orig_vol = audio_config['original_volume'] / 100.0
        filter_parts.append(f"[0:a]volume={orig_vol}[a_orig]")
        audio_streams.append("[a_orig]")
    
    # 2. Process background audio
    if audio_config['use_external_audio'] and audio_config['keep_original']:
        ext_vol = audio_config['external_volume'] / 100.0
        filter_parts.append(f"[1:a]volume={ext_vol},aloop=loop=-1:size=2e+09[a_bg]")
        audio_streams.append("[a_bg]")
    elif audio_config['use_external_audio'] and not audio_config['keep_original']:
        # Replace mode
        filter_parts.append(f"[1:a]aloop=loop=-1:size=2e+09[a_bg]")
        audio_streams = ["[a_bg]"]  # Reset, hanya background
    
    # 3. Process sound effects
    for i, sfx in enumerate(sound_effects):
        input_idx = sfx_start_index + i
        sfx_vol = sfx['volume'] / 100.0
        sfx_label = f"sfx{i}"
        
        # Build adelay untuk timing
        delay_ms = int(sfx['timestamp'] * 1000)
        
        # Filters untuk sound effect
        sfx_filters = []
        
        # Volume
        sfx_filters.append(f"volume={sfx_vol}")
        
        # Trim duration jika ada
        if sfx['duration']:
            sfx_filters.append(f"atrim=duration={sfx['duration']}")
        
        # Fade in/out jika ada
        if sfx['fade_duration'] > 0:
            fade = sfx['fade_duration']
            if sfx['duration']:
                # Fade in di awal, fade out di akhir
                sfx_filters.append(f"afade=t=in:st=0:d={fade}")
                fade_out_start = sfx['duration'] - fade
                if fade_out_start > 0:
                    sfx_filters.append(f"afade=t=out:st={fade_out_start}:d={fade}")
            else:
                # Hanya fade in
                sfx_filters.append(f"afade=t=in:st=0:d={fade}")
        
        # Delay untuk timing
        sfx_filters.append(f"adelay={delay_ms}|{delay_ms}")
        
        # Combine filters
        filter_str = f"[{input_idx}:a]{','.join(sfx_filters)}[{sfx_label}]"
        filter_parts.append(filter_str)
        audio_streams.append(f"[{sfx_label}]")
    
    # 4. Mix semua audio streams
    if len(audio_streams) > 1:
        mix_inputs = len(audio_streams)
        mix_str = f"{''.join(audio_streams)}amix=inputs={mix_inputs}:duration=first:dropout_transition=2,dynaudnorm=f=150:g=15[aout]"
        filter_parts.append(mix_str)
        
        filter_complex = ";".join(filter_parts)
        
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]"
        ])
    elif len(audio_streams) == 1:
        # Hanya 1 audio stream
        if filter_parts:
            filter_complex = ";".join(filter_parts)
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", audio_streams[0]
            ])
        else:
            cmd.extend([
                "-map", "0:v",
                "-map", "0:a?" if info['has_audio'] else "0:a"
            ])
    else:
        # No audio
        cmd.extend([
            "-map", "0:v"
        ])
    
    # ========================================
    # 📹 VIDEO CODEC SETTINGS
    # ========================================
    
    cmd.extend([
        # Video codec - H.264 High Profile
        "-c:v", "libx264",
        "-preset", s['preset'],
        "-crf", s['crf'],
        "-b:v", s['video_bitrate'],
        "-maxrate", s['maxrate'],
        "-bufsize", s['bufsize'],
        
        # TIKTOK SPECS
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.1",
        "-colorspace", "bt709",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        
        # FPS
        "-r", target_fps,
        
        # GOP settings
        "-g", "60",
        "-keyint_min", "30",
        "-sc_threshold", "40",
        
        # B-frames
        "-bf", "2",
        "-b_strategy", "1",
        
        # Motion estimation
        "-me_method", "hex",
        "-subq", "7",
        "-trellis", "1",
    ])
    
    # ========================================
    # 🔊 AUDIO CODEC SETTINGS
    # ========================================
    
    if len(audio_streams) > 0:
        cmd.extend([
            "-c:a", "aac",
            "-b:a", s['audio_bitrate'],
            "-ar", "48000",
            "-ac", "2",
        ])
    
    # ========================================
    # 📦 CONTAINER OPTIMIZATION
    # ========================================
    
    cmd.extend([
        "-movflags", "+faststart",
        "-metadata", f"comment=TikTok Optimized - {preset.upper()} with SFX",
        output_path
    ])
    
    # ========================================
    # ⚙️ PROCESS
    # ========================================
    
    print(f"\n⚙️  Processing...")
    print(f"   Input: {os.path.basename(input_path)}")
    if audio_config['use_external_audio']:
        print(f"   Background: {os.path.basename(audio_config['external_audio_path'])}")
    if sound_effects:
        print(f"   Sound FX: {len(sound_effects)} effects")
    print(f"   Output: {os.path.basename(output_path)}")
    print(f"\n{'='*70}")
    
    # Show progress
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    for line in process.stdout:
        line = line.rstrip()
        if 'frame=' in line or 'error' in line.lower() or 'warning' in line.lower():
            print(f"   {line}")
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\n{'='*70}")
        print(f"✅ OPTIMIZATION COMPLETE!")
        print(f"{'='*70}")
        
        input_size = os.path.getsize(input_path) / (1024 * 1024)
        output_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n📦 File Size:")
        print(f"   Before: {input_size:.2f} MB")
        print(f"   After:  {output_size:.2f} MB")
        
        print(f"\n📋 Video Specs:")
        print(f"   ✓ Resolution: 1080 × 1920")
        print(f"   ✓ FPS: {target_fps}")
        print(f"   ✓ Bitrate: {s['video_bitrate']}")
        print(f"   ✓ Profile: High @ Level 4.1")
        print(f"   ✓ Color: SDR (Rec.709)")
        print(f"   ✓ Audio: AAC {s['audio_bitrate']} @ 48kHz")
        
        if audio_config['use_external_audio']:
            if audio_config['keep_original']:
                print(f"\n🎵 Audio Mixed:")
                print(f"   ✓ Original: {audio_config['original_volume']}%")
                print(f"   ✓ Background: {audio_config['external_volume']}%")
            else:
                print(f"\n🎵 Audio Replaced with background")
        
        if sound_effects:
            print(f"\n🎬 Sound Effects Applied: {len(sound_effects)}")
            for i, sfx in enumerate(sound_effects, 1):
                print(f"   {i}. {sfx['name']} @ {sfx['timestamp']}s ({sfx['volume']}%)")
        
        print(f"\n💡 TIP: Video ini sudah dioptimasi untuk menghindari")
        print(f"   rekompresi TikTok. Upload langsung untuk hasil terbaik!")
        
        return True
    else:
        print(f"\n❌ Optimization failed! (Exit code: {process.returncode})")
        return False

