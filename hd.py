import subprocess
import os
import sys
from datetime import datetime

# ========================================
# 📱 TIKTOK VIDEO OPTIMIZER
# =================================d=======
# Program ini akan odptimize video dengan settings
# yang cocok untuk TikTok agar tetap jernih
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

def optimize_for_tiktok(input_path, output_path, preset='high'):
    """
    Optimize video untuk TikTok
    
    Presets:
    - ultra: Kualitas tertinggi (file besar, paling jernih)
    - high: Kualitas tinggi (recommended untuk >30 detik)
    - medium: Balanced (recommended untuk <30 detik)
    """
    
    print(f"\n🔍 Analyzing video...")
    info = get_video_info(input_path)
    
    print(f"\n📊 Video Info:")
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   Duration: {info['duration']:.2f}s")
    print(f"   FPS: {info['fps']}")
    print(f"   Current bitrate: {info['bitrate']} kb/s")
    
    # ========================================
    # 🎯 SETTINGS OPTIMAL UNTUK TIKTOK
    # ========================================
    
    # TikTok specs:
    # - Max resolution: 1080x1920 (9:16)
    # - Recommended bitrate: 8000-16000 kbps (video <60s)
    # - Max bitrate: 25000 kbps
    # - FPS: 30 atau 60
    # - Codec: H.264
    # - Audio: AAC, 128-192 kbps
    
    settings = {
        'ultra': {
            'video_bitrate': '16M',  # 16000 kbps
            'maxrate': '20M',
            'bufsize': '32M',
            'crf': '15',  # Lower = better quality
            'preset': 'slow',
            'audio_bitrate': '192k',
            'description': '🔥 Ultra Quality (Best for <60s videos)'
        },
        'high': {
            'video_bitrate': '12M',  # 12000 kbps
            'maxrate': '15M',
            'bufsize': '24M',
            'crf': '17',
            'preset': 'medium',
            'audio_bitrate': '192k',
            'description': '⭐ High Quality (Recommended for most videos)'
        },
        'medium': {
            'video_bitrate': '8M',  # 8000 kbps
            'maxrate': '10M',
            'bufsize': '16M',
            'crf': '19',
            'preset': 'fast',
            'audio_bitrate': '128k',
            'description': '✅ Balanced (Good for longer videos)'
        }
    }
    
    s = settings[preset]
    
    print(f"\n🎨 Using preset: {preset.upper()}")
    print(f"   {s['description']}")
    print(f"   Target bitrate: {s['video_bitrate']}")
    
    # Build filter_complex untuk sharpening & color enhancement
    vf = [
        # Pastikan resolusi pas 1080x1920
        "scale=1080:1920:force_original_aspect_ratio=decrease",
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        
        # Sharpening (bikin lebih tajam)
        "unsharp=5:5:1.0:5:5:0.0",
        
        # Color enhancement (bikin warna lebih 'pop')
        "eq=contrast=1.1:brightness=0.02:saturation=1.15",
        
        # Denoise ringan (kurangi noise tanpa blur)
        "hqdn3d=1.5:1.5:6:6"
    ]
    
    cmd = [
        FFMPEG,
        "-y",
        "-i", input_path,
        "-vf", ",".join(vf),
        
        # Video codec settings
        "-c:v", "libx264",
        "-preset", s['preset'],
        "-crf", s['crf'],
        "-b:v", s['video_bitrate'],
        "-maxrate", s['maxrate'],
        "-bufsize", s['bufsize'],
        
        # Pixel format (penting!)
        "-pix_fmt", "yuv420p",
        
        # Profile & level (compatibility)
        "-profile:v", "high",
        "-level", "4.2",
        
        # FPS (lock ke 30 atau 60)
        "-r", "60" if info['fps'] > 50 else "30",
        
        # GOP size (keyframe interval)
        "-g", "60",  # Keyframe tiap 2 detik (60fps) atau 1 detik (30fps)
        "-keyint_min", "60",
        
        # Audio settings
        "-c:a", "aac",
        "-b:a", s['audio_bitrate'],
        "-ar", "48000",  # Sample rate 48kHz
        "-ac", "2",  # Stereo
        
        # Metadata
        "-movflags", "+faststart",  # Optimasi untuk streaming
        "-metadata", "comment=Optimized for TikTok",
        
        # Progress
        "-progress", "pipe:1",
        "-nostats",
        
        output_path
    ]
    
    print(f"\n⚙️  Processing...")
    print(f"   Input: {os.path.basename(input_path)}")
    print(f"   Output: {os.path.basename(output_path)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )
    
    # Show progress
    for line in process.stdout:
        line = line.strip()
        if line.startswith("out_time_ms="):
            value = line.split("=")[1]
            if value != "N/A":
                ms = int(value)
                current_time = ms / 1_000_000
                pct = min(current_time / info['duration'] * 100, 100)
                sys.stdout.write(
                    f"\r   ⏳ Progress: {pct:6.2f}% | {current_time:5.1f}s / {info['duration']:.1f}s"
                )
                sys.stdout.flush()
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\n   ✅ Optimization complete!")
        
        # Show file size comparison
        input_size = os.path.getsize(input_path) / (1024 * 1024)
        output_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n📦 File Size:")
        print(f"   Before: {input_size:.2f} MB")
        print(f"   After: {output_size:.2f} MB")
        
        if output_size < input_size:
            saved = ((input_size - output_size) / input_size) * 100
            print(f"   💾 Saved: {saved:.1f}%")
        else:
            increased = ((output_size - input_size) / input_size) * 100
            print(f"   📈 Size increased: {increased:.1f}% (Better quality!)")
        
        return True
    else:
        print(f"\n   ❌ Optimization failed!")
        return False

# ========================================
# 🚀 MAIN PROGRAM
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("📱 TIKTOK VIDEO OPTIMIZER")
    print("="*60)
    print("Program ini akan optimize video agar tetap jernih di TikTok")
    print("dengan menambah bitrate, sharpening, dan color enhancement")
    print("="*60)
    
    # Input file
    while True:
        input_file = input("\n📂 Path video input: ").strip().strip('"')
        if os.path.exists(input_file):
            break
        print("❌ File tidak ditemukan!")
    
    # Generate output filename
    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Pilih preset
    print("\n" + "="*60)
    print("🎨 PILIH QUALITY PRESET")
    print("="*60)
    print("1. Ultra   - 16 Mbps (Terbaik untuk video <60 detik)")
    print("2. High    - 12 Mbps (Recommended, balance quality & size)")
    print("3. Medium  - 8 Mbps  (Untuk video lebih panjang)")
    print("="*60)
    print("💡 Tips:")
    print("   - Video <30s: Gunakan Ultra atau High")
    print("   - Video 30-60s: Gunakan High")
    print("   - Video >60s: Gunakan Medium atau High")
    print("="*60)
    
    while True:
        choice = input("\nPilih preset (1-3) [2]: ").strip() or '2'
        if choice in ['1', '2', '3']:
            break
        print("❌ Pilihan tidak valid!")
    
    preset_map = {'1': 'ultra', '2': 'high', '3': 'medium'}
    preset = preset_map[choice]
    
    # Output filename
    default_output = os.path.join(input_dir, f"{input_name}_tiktok_{preset}.mp4")
    output_file = input(f"\n📁 Output path [{default_output}]: ").strip().strip('"') or default_output
    
    # Confirm
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Preset: {preset.upper()}")
    print("="*60)
    
    confirm = input("\nLanjutkan? (y/n) [y]: ").strip().lower() or 'y'
    
    if confirm != 'y':
        print("❌ Dibatalkan!")
        sys.exit(0)
    
    # Process
    success = optimize_for_tiktok(input_file, output_file, preset)
    
    if success:
        print("\n" + "="*60)
        print("🎉 SELESAI!")
        print("="*60)
        print(f"📁 File tersimpan di: {output_file}")
        print("\n📱 Tips Upload TikTok:")
        print("   1. Upload dari WiFi (jangan pakai data seluler)")
        print("   2. Jangan crop/edit lagi di TikTok")
        print("   3. Tunggu proses 'HD' selesai sebelum publish")
        print("   4. Pastikan 'Allow HD Uploads' aktif di settings")
        print("="*60)
    else:
        print("\n❌ Proses gagal!")
        sys.exit(1)
 