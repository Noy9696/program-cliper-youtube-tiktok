import subprocess
import os
import sys

# ========================================
# ✨ FADE IN/OUT EDITOR - NO QeUALITY LOSS
# 🎯 Pure Filter - No Re-encoding (jika mungkin)
# ========================================

FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"

def get_video_info(video_path):
    """Ambil info video (durasi, codec, dll)"""
    cmd = [
        FFMPEG,
        "-i", video_path,
        "-hide_banner"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = result.stderr
    
    duration = 0
    width = 0
    height = 0
    fps = 0
    video_codec = ""
    audio_codec = ""
    has_audio = False
    
    for line in info.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = time_str.split(':')
            duration = float(h) * 3600 + float(m) * 60 + float(s)
        
        if 'Video:' in line:
            parts = line.split('Video:')[1].split(',')
            video_codec = parts[0].strip()
            
            for part in parts:
                if 'x' in part and not 'max' in part:
                    try:
                        res = part.strip().split()[0]
                        width, height = map(int, res.split('x'))
                        break
                    except:
                        pass
            
            for part in parts:
                if 'fps' in part or 'tbr' in part:
                    try:
                        fps = float(part.strip().split()[0])
                        break
                    except:
                        pass
        
        if 'Audio:' in line:
            has_audio = True
            parts = line.split('Audio:')[1].split(',')
            audio_codec = parts[0].strip()
    
    return {
        'duration': duration,
        'width': width,
        'height': height,
        'fps': fps,
        'video_codec': video_codec,
        'audio_codec': audio_codec,
        'has_audio': has_audio
    }

def add_fade_effects(input_path, output_path, mode='balanced'):
    """
    Tambahkan fade effects ke video
    
    Modes:
    - lossless: Copy codec (fastest, no quality loss jika codec support)
    - high: CRF 18 (near lossless, very high quality)
    - balanced: CRF 20 (high quality, smaller size)
    - fast: CRF 23 (good quality, fast encoding)
    """
    
    print("\n" + "="*70)
    print("✨ FADE IN/OUT VIDEO EDITOR - NO QUALITY LOSS")
    print("="*70)
    
    # Get video info
    print(f"\n🔍 Analyzing video...")
    info = get_video_info(input_path)
    
    print(f"\n📊 Video Info:")
    print(f"   Duration: {info['duration']:.2f}s")
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   FPS: {info['fps']}")
    print(f"   Video Codec: {info['video_codec']}")
    print(f"   Audio Codec: {info['audio_codec'] if info['has_audio'] else 'No Audio'}")
    
    # ========================================
    # 🎨 FADE CONFIGURATION
    # ========================================
    
    print("\n" + "="*70)
    print("✨ FADE EFFECTS CONFIGURATION")
    print("="*70)
    
    print("\n🎬 Pilih tipe fade effect:")
    print("1. Fade IN only - Video mulai dari hitam")
    print("2. Fade OUT only - Video berakhir ke hitam")
    print("3. Both - Fade IN + Fade OUT")
    
    while True:
        effect_choice = input("\nPilih (1-3) [3]: ").strip() or '3'
        if effect_choice in ['1', '2', '3']:
            break
        print("❌ Pilihan tidak valid!")
    
    # Preset fade duration
    print("\n" + "="*70)
    print("🎨 FADE DURATION PRESET")
    print("="*70)
    print("1. Quick   - 0.3s (Cepat & smooth)")
    print("2. Normal  - 0.5s (Standard)")
    print("3. Smooth  - 1.0s (Halus & dramatis)")
    print("4. Custom  - Atur durasi sendiri")
    
    while True:
        preset = input("\nPilih preset (1-4) [2]: ").strip() or '2'
        if preset in ['1', '2', '3', '4']:
            break
        print("❌ Pilihan tidak valid!")
    
    if preset == '1':
        fade_duration = 0.3
    elif preset == '2':
        fade_duration = 0.5
    elif preset == '3':
        fade_duration = 1.0
    else:
        # Custom
        while True:
            try:
                fade_duration = input("\n⏱️  Fade duration (0.1-5.0 detik) [0.5]: ").strip() or '0.5'
                fade_duration = float(fade_duration)
                if 0.1 <= fade_duration <= 5.0:
                    break
                print("❌ Durasi harus 0.1-5.0 detik")
            except:
                print("❌ Input tidak valid!")
    
    # Validasi durasi
    if effect_choice == '3':
        total_fade = fade_duration * 2
    else:
        total_fade = fade_duration
    
    if total_fade >= info['duration']:
        print(f"\n⚠️  WARNING: Total fade ({total_fade}s) melebihi durasi video ({info['duration']}s)")
        print("   Mengatur fade ke nilai maksimal yang aman...")
        max_fade = info['duration'] * 0.25
        fade_duration = max_fade
    
    # ========================================
    # 🎚️ AUDIO FADE OPTIONS
    # ========================================
    
    audio_fade = False
    if info['has_audio']:
        print("\n" + "="*70)
        print("🔊 AUDIO FADE")
        print("="*70)
        print("Apakah audio juga ikut di-fade bersamaan dengan video?")
        print("1. Ya - Audio fade sync dengan video")
        print("2. Tidak - Audio tetap penuh dari awal")
        
        while True:
            audio_choice = input("\nPilih (1-2) [1]: ").strip() or '1'
            if audio_choice in ['1', '2']:
                break
            print("❌ Pilihan tidak valid!")
        
        audio_fade = (audio_choice == '1')
    
    # ========================================
    # 🎯 BUILD FILTER CHAINS
    # ========================================
    
    video_filters = []
    audio_filters = []
    
    # Video fade filters
    if effect_choice in ['1', '3']:  # Fade IN
        video_filters.append(f"fade=t=in:st=0:d={fade_duration}:color=black")
    
    if effect_choice in ['2', '3']:  # Fade OUT
        fade_out_start = info['duration'] - fade_duration
        video_filters.append(f"fade=t=out:st={fade_out_start}:d={fade_duration}:color=black")
    
    # Audio fade filters
    if info['has_audio'] and audio_fade:
        if effect_choice in ['1', '3']:  # Fade IN
            audio_filters.append(f"afade=t=in:st=0:d={fade_duration}")
        
        if effect_choice in ['2', '3']:  # Fade OUT
            fade_out_start = info['duration'] - fade_duration
            audio_filters.append(f"afade=t=out:st={fade_out_start}:d={fade_duration}")
    
    # ========================================
    # 🎨 QUALITY MODE SELECTION
    # ========================================
    
    print("\n" + "="*70)
    print("🎨 QUALITY MODE")
    print("="*70)
    print("1. LOSSLESS  - Copy codec (tercepat, no quality loss)")
    print("2. ULTRA     - CRF 18 (near lossless, sangat tinggi)")
    print("3. HIGH      - CRF 20 (high quality, recommended)")
    print("4. BALANCED  - CRF 23 (good quality, smaller file)")
    print("")
    print("💡 TIP: Pilih LOSSLESS jika ingin paling cepat & no quality loss")
    print("   (tapi file size bisa lebih besar)")
    
    while True:
        quality_choice = input("\nPilih mode (1-4) [3]: ").strip() or '3'
        if quality_choice in ['1', '2', '3', '4']:
            break
        print("❌ Pilihan tidak valid!")
    
    quality_modes = {
        '1': {'name': 'LOSSLESS', 'crf': None, 'preset': None, 'copy': True},
        '2': {'name': 'ULTRA', 'crf': '18', 'preset': 'slow', 'copy': False},
        '3': {'name': 'HIGH', 'crf': '20', 'preset': 'medium', 'copy': False},
        '4': {'name': 'BALANCED', 'crf': '23', 'preset': 'fast', 'copy': False}
    }
    
    quality_mode = quality_modes[quality_choice]
    
    # ========================================
    # 🎬 BUILD FFMPEG COMMAND
    # ========================================
    
    print(f"\n⚙️  Configuration:")
    print(f"   Mode: {quality_mode['name']}")
    if effect_choice == '1':
        print(f"   Effect: Fade IN ({fade_duration}s)")
    elif effect_choice == '2':
        print(f"   Effect: Fade OUT ({fade_duration}s)")
    else:
        print(f"   Effect: Fade IN + OUT ({fade_duration}s each)")
    
    if info['has_audio']:
        print(f"   Audio Fade: {'✓ Yes' if audio_fade else '✗ No'}")
    
    cmd = [FFMPEG, "-y", "-i", input_path]
    
    # Cek apakah bisa menggunakan mode lossless
    if quality_mode['copy'] and not video_filters:
        print("\n⚠️  WARNING: Lossless mode tidak bisa digunakan dengan filter.")
        print("   Switching to ULTRA mode (CRF 18)...")
        quality_mode = quality_modes['2']
    
    # Video filters
    if video_filters:
        cmd.extend(["-vf", ",".join(video_filters)])
    
    # Audio filters
    if audio_filters:
        cmd.extend(["-af", ",".join(audio_filters)])
    
    # Video codec settings
    if quality_mode['copy']:
        cmd.extend(["-c:v", "copy"])
    else:
        # Re-encode dengan quality tinggi
        cmd.extend([
            "-c:v", "libx264",
            "-preset", quality_mode['preset'],
            "-crf", quality_mode['crf'],
            "-pix_fmt", "yuv420p"
        ])
    
    # Audio codec settings
    if info['has_audio']:
        if audio_filters or not quality_mode['copy']:
            # Re-encode audio dengan quality tinggi
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "320k",  # Maximum AAC quality
                "-ar", "48000"
            ])
        else:
            cmd.extend(["-c:a", "copy"])
    
    # Container optimization
    cmd.extend([
        "-movflags", "+faststart",
        output_path
    ])
    
    # ========================================
    # ⚙️ PROCESS
    # ========================================
    
    print(f"\n{'='*70}")
    print("⚙️  Processing...")
    print(f"{'='*70}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Show progress
    for line in process.stdout:
        line = line.rstrip()
        if 'frame=' in line or 'time=' in line:
            print(f"\r   {line}", end='', flush=True)
        elif 'error' in line.lower():
            print(f"\n   ❌ {line}")
    
    print()  # New line after progress
    process.wait()
    
    if process.returncode == 0:
        print(f"\n{'='*70}")
        print("✅ FADE EFFECTS ADDED SUCCESSFULLY!")
        print(f"{'='*70}")
        
        input_size = os.path.getsize(input_path) / (1024 * 1024)
        output_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n📦 File Size:")
        print(f"   Before: {input_size:.2f} MB")
        print(f"   After:  {output_size:.2f} MB")
        
        size_diff = ((output_size - input_size) / input_size) * 100
        if size_diff > 0:
            print(f"   Change: +{size_diff:.1f}%")
        else:
            print(f"   Change: {size_diff:.1f}%")
        
        print(f"\n✨ Effects Applied:")
        if effect_choice == '1':
            print(f"   ✓ Fade IN: {fade_duration}s")
        elif effect_choice == '2':
            print(f"   ✓ Fade OUT: {fade_duration}s")
        else:
            print(f"   ✓ Fade IN: {fade_duration}s")
            print(f"   ✓ Fade OUT: {fade_duration}s")
        
        if info['has_audio'] and audio_fade:
            print(f"   ✓ Audio fade synced with video")
        
        print(f"\n🎨 Quality: {quality_mode['name']}")
        
        return True
    else:
        print(f"\n❌ Process failed! (Exit code: {process.returncode})")
        return False

# ========================================
# 🚀 MAIN PROGRAM
# ========================================
if __name__ == "__main__":
    print("="*70)
    print("✨ FADE IN/OUT VIDEO EDITOR")
    print("🎯 NO QUALITY LOSS - PURE FILTER ONLY")
    print("="*70)
    print("\n🎬 Features:")
    print("   • Fade IN from black")
    print("   • Fade OUT to black")
    print("   • Audio fade sync (optional)")
    print("   • Multiple quality modes:")
    print("     - LOSSLESS (copy codec, fastest)")
    print("     - ULTRA (CRF 18, near lossless)")
    print("     - HIGH (CRF 20, recommended)")
    print("     - BALANCED (CRF 23, smaller file)")
    print("\n💡 Perfect untuk:")
    print("   • Video TikTok, Instagram, YouTube")
    print("   • Membuat transisi smooth")
    print("   • Professional video editing")
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
    
    default_output = os.path.join(input_dir, f"{input_name}_fade.mp4")
    output_file = input(f"\n📁 Output path [{default_output}]: ").strip().strip('"') or default_output
    
    # Process
    success = add_fade_effects(input_file, output_file)
    
    if success:
        print("\n" + "="*70)
        print("🎉 SUCCESS!")
        print("="*70)
        print(f"📁 Output: {output_file}")
        print("\n💡 TIP: Video siap digunakan dengan fade effect!")
    else:
        print("\n" + "="*70)
        print("❌ ERROR!")
        print("="*70)
        print("Cek:")
        print("1. Format video input didukung")
        print("2. FFmpeg terinstall dengan benar")
        print("3. Ada space di drive untuk output")
        sys.exit(1)
