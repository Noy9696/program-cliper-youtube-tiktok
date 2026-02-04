import subprocess
import os
import sys
from datetime import datetime

# ========================================
# 📱 TIKTOK VIDEO OPTIMIZER - ANTI-COMPRESS VERSION
# 🎵 WITH ADVANCED AUDIO MIXING
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

def get_audio_config():
    """Konfigurasi audio mixing"""
    print("\n" + "="*70)
    print("🎵 AUDIO CONFIGURATION")
    print("="*70)
    
    # Tanya mau tambah audio atau tidak
    print("\n📢 Apakah ingin menambahkan audio/musik eksternal?")
    print("1. Ya - Tambahkan audio MP3")
    print("2. Tidak - Gunakan audio video asli saja")
    
    while True:
        choice = input("\nPilih (1-2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ Pilihan tidak valid!")
    
    if choice == '2':
        return {
            'use_external_audio': False,
            'keep_original': True,
            'original_volume': 100,
            'external_volume': 0
        }
    
    # Minta path audio eksternal
    while True:
        audio_path = input("\n🎵 Path file MP3/audio eksternal: ").strip().strip('"')
        if os.path.exists(audio_path):
            break
        print("❌ File tidak ditemukan!")
    
    # Tanya mau keep audio asli atau tidak
    print("\n" + "="*70)
    print("🔊 AUDIO MIXING OPTIONS")
    print("="*70)
    print("1. Ganti Total - Hapus audio asli, gunakan audio baru saja")
    print("2. Mix Audio - Campurkan audio asli + audio baru")
    
    while True:
        mix_choice = input("\nPilih (1-2): ").strip()
        if mix_choice in ['1', '2']:
            break
        print("❌ Pilihan tidak valid!")
    
    if mix_choice == '1':
        return {
            'use_external_audio': True,
            'external_audio_path': audio_path,
            'keep_original': False,
            'original_volume': 0,
            'external_volume': 100
        }
    
    # Mix audio - tanya volume masing-masing
    print("\n" + "="*70)
    print("🎚️ VOLUME MIXING")
    print("="*70)
    print("Atur volume untuk audio asli dan audio tambahan")
    print("(Total tidak harus 100%, bisa lebih atau kurang)")
    
    while True:
        try:
            orig_vol = input("\n🎬 Volume audio ASLI video (0-200%) [50]: ").strip() or '50'
            orig_vol = int(orig_vol)
            if 0 <= orig_vol <= 200:
                break
            print("❌ Volume harus 0-200%")
        except:
            print("❌ Input tidak valid!")
    
    while True:
        try:
            ext_vol = input("🎵 Volume audio TAMBAHAN (0-200%) [100]: ").strip() or '100'
            ext_vol = int(ext_vol)
            if 0 <= ext_vol <= 200:
                break
            print("❌ Volume harus 0-200%")
        except:
            print("❌ Input tidak valid!")
    
    return {
        'use_external_audio': True,
        'external_audio_path': audio_path,
        'keep_original': True,
        'original_volume': orig_vol,
        'external_volume': ext_vol
    }

def optimize_for_tiktok(input_path, output_path, preset='standard', audio_config=None):
    """
    Optimize video untuk TikTok - ANTI-COMPRESS VERSION
    Dengan advanced audio mixing
    """
    
    print(f"\n🔍 Analyzing video...")
    info = get_video_info(input_path)
    
    print(f"\n📊 Video Info:")
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   Duration: {info['duration']:.2f}s")
    print(f"   FPS: {info['fps']}")
    print(f"   Current bitrate: {info['bitrate']} kb/s")
    print(f"   Has audio: {'✓ Yes' if info['has_audio'] else '✗ No'}")
    
    # Default audio config
    if audio_config is None:
        audio_config = {
            'use_external_audio': False,
            'keep_original': True,
            'original_volume': 100,
            'external_volume': 0
        }
    
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
            print(f"   🎵 Audio Tambahan: {audio_config['external_volume']}%")
        else:
            print(f"   🔊 Mode: REPLACE")
            print(f"   🎵 Audio baru akan menggantikan audio asli")
    else:
        print(f"   🔊 Mode: ORIGINAL")
        print(f"   🎬 Menggunakan audio video asli")
    
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
    
    # Input audio eksternal jika ada
    if audio_config['use_external_audio']:
        cmd.extend(["-i", audio_config['external_audio_path']])
    
    # Video filters
    cmd.extend(["-vf", ",".join(vf)])
    
    # ========================================
    # 🎚️ AUDIO FILTER COMPLEX
    # ========================================
    
    if audio_config['use_external_audio']:
        if audio_config['keep_original']:
            # MIX MODE - campurkan 2 audio
            orig_vol = audio_config['original_volume'] / 100.0
            ext_vol = audio_config['external_volume'] / 100.0
            
            # Filter complex untuk mixing
            filter_complex = (
                f"[0:a]volume={orig_vol}[a1];"
                f"[1:a]volume={ext_vol},aloop=loop=-1:size=2e+09[a2];"
                f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[aout]"
            ])
        else:
            # REPLACE MODE - ganti audio
            cmd.extend([
                "-map", "0:v",
                "-map", "1:a",
                "-shortest"  # Potong sesuai durasi video
            ])
    else:
        # ORIGINAL MODE - audio asli saja
        cmd.extend([
            "-map", "0:v",
            "-map", "0:a?" if info['has_audio'] else "0:a"
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
        "-metadata", f"comment=TikTok Optimized - {preset.upper()}",
        output_path
    ])
    
    # ========================================
    # ⚙️ PROCESS
    # ========================================
    
    print(f"\n⚙️  Processing...")
    print(f"   Input: {os.path.basename(input_path)}")
    if audio_config['use_external_audio']:
        print(f"   Audio: {os.path.basename(audio_config['external_audio_path'])}")
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
                print(f"   ✓ External: {audio_config['external_volume']}%")
            else:
                print(f"\n🎵 Audio Replaced with external audio")
        
        print(f"\n💡 TIP: Video ini sudah dioptimasi untuk menghindari")
        print(f"   rekompresi TikTok. Upload langsung untuk hasil terbaik!")
        
        return True
    else:
        print(f"\n❌ Optimization failed! (Exit code: {process.returncode})")
        return False

# ========================================
# 🚀 MAIN PROGRAM
# ========================================
if __name__ == "__main__":
    print("="*70)
    print("📱 TIKTOK VIDEO OPTIMIZER - ANTI-COMPRESS VERSION")
    print("🎵 WITH ADVANCED AUDIO MIXING")
    print("="*70)
    print("\n🎯 Optimized for TikTok specs:")
    print("   • 1080×1920 resolution (portrait)")
    print("   • 30 FPS (or keep original if lower)")
    print("   • 8-12 Mbps bitrate")
    print("   • H.264 High Profile @ Level 4.1")
    print("   • SDR color (Rec.709)")
    print("   • AAC audio @ 48kHz")
    print("\n🎵 Audio Features:")
    print("   • Keep original audio")
    print("   • Replace with external audio")
    print("   • Mix original + external audio")
    print("   • Adjustable volume for each audio source (0-200%)")
    print("="*70)
    
    # Input file
    while True:
        input_file = input("\n📂 Path video input: ").strip().strip('"')
        if os.path.exists(input_file):
            break
        print("❌ File tidak ditemukan!")
    
    # Audio configuration
    audio_config = get_audio_config()
    
    # Generate output filename
    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Pilih preset
    print("\n" + "="*70)
    print("🎨 PILIH QUALITY PRESET")
    print("="*70)
    print("1. MAXIMUM  - 12 Mbps (Best quality, slower upload)")
    print("2. STANDARD - 10 Mbps (Recommended, balanced)")
    print("3. BALANCED - 8 Mbps  (Fast upload, good quality)")
    print("="*70)
    
    while True:
        choice = input("\nPilih preset (1-3) [2]: ").strip() or '2'
        if choice in ['1', '2', '3']:
            break
        print("❌ Pilihan tidak valid!")
    
    preset_map = {'1': 'maximum', '2': 'standard', '3': 'balanced'}
    preset = preset_map[choice]
    
    # Output filename
    audio_suffix = ""
    if audio_config['use_external_audio']:
        if audio_config['keep_original']:
            audio_suffix = "_mixed"
        else:
            audio_suffix = "_replaced"
    
    default_output = os.path.join(input_dir, f"{input_name}_tiktok_{preset}{audio_suffix}.mp4")
    output_file = input(f"\n📁 Output path [{default_output}]: ").strip().strip('"') or default_output
    
    # Process
    success = optimize_for_tiktok(input_file, output_file, preset, audio_config)
    
    if success:
        print("\n" + "="*70)
        print("🎉 SUCCESS!")
        print("="*70)
        print(f"Output: {output_file}")
        print("\n📤 Ready to upload to TikTok!")
    else:
        print("\n" + "="*70)
        print("❌ ERROR!")
        print("="*70)
        print("Cek:")
        print("1. Format video/audio input didukung")
        print("2. FFmpeg terinstall dengan benar")
        print("3. Ada space di drive untuk output")
        sys.exit(1)
