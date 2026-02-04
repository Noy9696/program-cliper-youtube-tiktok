import subprocess
import os
import sys
from datetime import datetime

# ========================================
# 📱 TIKTOK VIDEO OPTIMIZER - DEBUG VERSION
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
    
    for line in info.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = time_str.split(':')
            duration = float(h) * 3600 + float(m) * 60 + float(s)
        
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
        'bitrate': bitrate
    }

def optimize_for_tiktok(input_path, output_path, preset='insane', target_resolution='2k'):
    """
    Optimize video untuk TikTok - FIXED VERSION
    """
    
    print(f"\n🔍 Analyzing video...")
    info = get_video_info(input_path)
    
    print(f"\n📊 Video Info:")
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   Duration: {info['duration']:.2f}s")
    print(f"   FPS: {info['fps']}")
    print(f"   Current bitrate: {info['bitrate']} kb/s")
    
    # ========================================
    # 🎯 SETTINGS - FIXED VERSION
    # ========================================
    
    settings = {
        'godmode': {
            'video_bitrate': '60M',
            'maxrate': '80M',
            'bufsize': '120M',
            'crf': '10',
            'preset': 'veryslow',
            'audio_bitrate': '320k',
            'tune': 'film',
            'description': '👑 GOD MODE - 60 Mbps',
            'color_depth': '8bit'  # CHANGED: 10bit bikin error di beberapa build ffmpeg
        },
        'insane': {
            'video_bitrate': '40M',
            'maxrate': '50M',
            'bufsize': '80M',
            'crf': '12',
            'preset': 'veryslow',
            'audio_bitrate': '256k',
            'tune': 'film',
            'description': '🔥 INSANE - 40 Mbps',
            'color_depth': '8bit'  # CHANGED
        },
        'extreme': {
            'video_bitrate': '30M',
            'maxrate': '40M',
            'bufsize': '60M',
            'crf': '13',
            'preset': 'slower',
            'audio_bitrate': '256k',
            'tune': 'film',
            'description': '💎 EXTREME - 30 Mbps',
            'color_depth': '8bit'
        },
        'ultra': {
            'video_bitrate': '20M',
            'maxrate': '25M',
            'bufsize': '40M',
            'crf': '14',
            'preset': 'slow',
            'audio_bitrate': '192k',
            'tune': 'film',
            'description': '⭐ ULTRA - 20 Mbps',
            'color_depth': '8bit'
        },
        'high': {
            'video_bitrate': '12M',
            'maxrate': '15M',
            'bufsize': '24M',
            'crf': '17',
            'preset': 'medium',
            'audio_bitrate': '192k',
            'tune': None,
            'description': '✅ HIGH - 12 Mbps',
            'color_depth': '8bit'
        }
    }
    
    # Resolution settings
    resolutions = {
        '4k': {
            'width': 2160,
            'height': 3840,
            'description': '4K UHD (2160x3840)'
        },
        '2k': {
            'width': 1440,
            'height': 2560,
            'description': '2K QHD (1440x2560)'
        },
        '1080p': {
            'width': 1080,
            'height': 1920,
            'description': 'Full HD (1080x1920)'
        }
    }
    
    s = settings[preset]
    r = resolutions[target_resolution]
    
    print(f"\n🎨 Using preset: {preset.upper()}")
    print(f"   {s['description']}")
    print(f"   Target resolution: {r['description']}")
    print(f"   Target bitrate: {s['video_bitrate']}")
    
    # ========================================
    # 🎬 SIMPLIFIED FILTER CHAIN (FIXED)
    # ========================================
    
    vf = [
        # Upscale dengan Lanczos
        f"scale={r['width']}:{r['height']}:flags=lanczos:force_original_aspect_ratio=decrease",
        f"pad={r['width']}:{r['height']}:(ow-iw)/2:(oh-ih)/2:black",
        
        # Sharpening
        "unsharp=5:5:1.5:5:5:0.0",
        
        # Color enhancement
        "eq=contrast=1.15:brightness=0.03:saturation=1.2",
        
        # Denoise
        "hqdn3d=1.5:1.5:6:6"
    ]
    
    # REMOVED: edgedetect dan dblur karena bisa bikin error
    
    # Pixel format
    pix_fmt = 'yuv420p'  # Always use 8-bit untuk compatibility
    profile = 'high'
    
    cmd = [
        FFMPEG,
        "-y",
        "-i", input_path,
        
        # Filter video
        "-vf", ",".join(vf),
        
        # Video codec settings
        "-c:v", "libx264",
        "-preset", s['preset'],
        "-crf", s['crf'],
        "-b:v", s['video_bitrate'],
        "-maxrate", s['maxrate'],
        "-bufsize", s['bufsize'],
        
        # Pixel format
        "-pix_fmt", pix_fmt,
        
        # Profile & level
        "-profile:v", profile,
        "-level", "5.1",  # Changed from 5.2 untuk compatibility
        
        # FPS
        "-r", "60" if info['fps'] >= 30 else "30",
        
        # GOP settings
        "-g", "120",
        "-keyint_min", "60",
        "-sc_threshold", "40",
        
        # B-frames
        "-bf", "3",
        "-b_strategy", "2",
        
        # Motion estimation
        "-me_method", "umh",
        "-subq", "10",
        "-trellis", "2",
    ]
    
    # Tambahkan tune jika ada
    if s['tune']:
        cmd.extend(["-tune", s['tune']])
    
    # Audio settings
    cmd.extend([
        "-c:a", "aac",
        "-b:a", s['audio_bitrate'],
        "-ar", "48000",
        "-ac", "2",
        
        # Metadata
        "-movflags", "+faststart",
        "-metadata", f"comment=Optimized for TikTok - {preset.upper()} @ {target_resolution.upper()}",
        
        output_path
    ])
    
    print(f"\n⚙️  Processing...")
    print(f"   Input: {os.path.basename(input_path)}")
    print(f"   Output: {os.path.basename(output_path)}")
    print(f"\n🔍 DEBUG: Showing full ffmpeg output...\n")
    
    # CHANGED: Show full output untuk debug
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # CHANGED: capture stderr
        universal_newlines=True
    )
    
    # Show output real-time
    import threading
    
    def print_output(pipe, prefix=''):
        for line in pipe:
            print(f"{prefix}{line.rstrip()}")
    
    stdout_thread = threading.Thread(target=print_output, args=(process.stdout, ''))
    stderr_thread = threading.Thread(target=print_output, args=(process.stderr, '⚠️  '))
    
    stdout_thread.start()
    stderr_thread.start()
    
    process.wait()
    stdout_thread.join()
    stderr_thread.join()
    
    if process.returncode == 0:
        print(f"\n✅ Optimization complete!")
        
        input_size = os.path.getsize(input_path) / (1024 * 1024)
        output_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n📦 File Size:")
        print(f"   Before: {input_size:.2f} MB")
        print(f"   After: {output_size:.2f} MB")
        
        return True
    else:
        print(f"\n❌ Optimization failed! (Exit code: {process.returncode})")
        return False

# ========================================
# 🚀 MAIN PROGRAM
# ========================================
if __name__ == "__main__":
    print("="*70)
    print("📱 TIKTOK VIDEO OPTIMIZER - DEBUG VERSION")
    print("="*70)
    
    # Input file
    while True:
        input_file = input("\n📂 Path video input: ").strip().strip('"')
        if os.path.exists(input_file):
            break
        print("❌ File tidak ditemukan!")
    
    # Generate output filename
    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Pilih resolusi target
    print("\n" + "="*70)
    print("📐 PILIH TARGET RESOLUTION")
    print("="*70)
    print("1. 4K    - 2160x3840")
    print("2. 2K    - 1440x2560")
    print("3. 1080p - 1080x1920")
    print("="*70)
    
    while True:
        res_choice = input("\nPilih resolusi (1-3) [3]: ").strip() or '3'
        if res_choice in ['1', '2', '3']:
            break
        print("❌ Pilihan tidak valid!")
    
    res_map = {'1': '4k', '2': '2k', '3': '1080p'}
    target_resolution = res_map[res_choice]
    
    # Pilih preset
    print("\n" + "="*70)
    print("🎨 PILIH QUALITY PRESET")
    print("="*70)
    print("1. GOD MODE - 60 Mbps")
    print("2. INSANE   - 40 Mbps")
    print("3. EXTREME  - 30 Mbps")
    print("4. ULTRA    - 20 Mbps")
    print("5. HIGH     - 12 Mbps")
    print("="*70)
    
    while True:
        choice = input("\nPilih preset (1-5) [4]: ").strip() or '4'
        if choice in ['1', '2', '3', '4', '5']:
            break
        print("❌ Pilihan tidak valid!")
    
    preset_map = {'1': 'godmode', '2': 'insane', '3': 'extreme', '4': 'ultra', '5': 'high'}
    preset = preset_map[choice]
    
    # Output filename
    default_output = os.path.join(input_dir, f"{input_name}_tiktok_{preset}_{target_resolution}.mp4")
    output_file = input(f"\n📁 Output path [{default_output}]: ").strip().strip('"') or default_output
    
    # Process
    success = optimize_for_tiktok(input_file, output_file, preset, target_resolution)
    
    if not success:
        print("\n" + "="*70)
        print("❌ ERROR OCCURRED!")
        print("="*70)
        print("Kemungkinan penyebab:")
        print("1. Filter video tidak kompatibel dengan ffmpeg build Anda")
        print("2. Resolusi input terlalu kecil untuk di-upscale")
        print("3. Video corrupt atau format tidak didukung")
        print("="*70)
        sys.exit(1)
