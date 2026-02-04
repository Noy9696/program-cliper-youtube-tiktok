import subprocess, sys, os
from datetime import datetime

def to_sec(t):
    parts = list(map(int, t.split(":")))
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    raise ValueError("Format waktu salah")

def sec_to_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
SOURCE = r"D:\CLIP\hasil\konten.mp4"
OUTPUT_DIR = r"D:\CLIP\hasil"
FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "final_merged.mp4")

# ========================================
# 🎬 PENGATURAN TRANSISI
# ========================================
TRANSITION_DURATION = 0.8  # Durasi transisi dalam detik
BLINK_SPEED = 0.5          # Kecepatan kedip border merah
# ========================================

if not os.path.exists(SOURCE):
    raise FileNotFoundError("Video sumber tidak ditemukan")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_scene(scene_num, start_time, duration, output_path, blink_config):
    """Proses satu scene dengan optional border merah berkedip"""
    
    # Build filter untuk gamer dengan atau tanpa border merah
    if blink_config['enabled']:
        gamer_filter = (
            "[0:v]crop=iw*0.25:ih*0.25:iw*0.73:ih*0.70,"
            "scale=450:450,"
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6,"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=red:t=8:enable='between(t,{blink_config['start']},{blink_config['end']})*gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[gamer];"
        )
    else:
        gamer_filter = (
            "[0:v]crop=iw*0.25:ih*0.25:iw*0.73:ih*0.70,"
            "scale=450:450,"
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6[gamer];"
        )
    
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=40:1[bg];"
        
        "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        "scale=1080:1500:force_original_aspect_ratio=decrease,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6[main];"
        
        + gamer_filter +
        
        "[bg][main]overlay=(W-w)/2:80[tmp];"
        "[tmp][gamer]overlay=W-w-40:H-h-80[v]"
    )
    
    cmd = [
        FFMPEG,
        "-y",
        "-ss", str(start_time),
        "-i", SOURCE,
        "-t", str(duration),
        "-filter_complex", vf,
        "-map", "[v]",
        "-map", "0:a:0?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]
    
    print(f"\n🎬 Processing Scene {scene_num}...")
    print(f"   Start: {sec_to_time(start_time)} | Duration: {duration}s")
    if blink_config['enabled']:
        print(f"   🔴 Border merah: detik {blink_config['start']}-{blink_config['end']}")
    else:
        print(f"   ⚫ Tanpa border merah")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )
    
    for line in process.stdout:
        line = line.strip()
        if not line.startswith("out_time_ms="):
            continue
        value = line.split("=")[1]
        if value == "N/A":
            continue
        ms = int(value)
        pct = min(ms / (duration * 1_000_000) * 100, 100)
        sys.stdout.write(
            f"\r   ⏳ Progress: {pct:6.2f}% | {ms/1_000_000:5.1f}s / {duration}s"
        )
        sys.stdout.flush()
    
    process.wait()
    print(f"\n   ✅ Scene {scene_num} done!")
    return process.returncode == 0

def merge_videos_with_transition(scene_files, output_path, transition_type):
    """Gabungkan semua scene dengan efek transisi"""
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition...")
    
    if len(scene_files) == 1:
        # Kalau cuma 1 scene, copy aja
        import shutil
        shutil.copy(scene_files[0], output_path)
        return True
    
    # Build filter complex untuk xfade
    inputs = []
    filter_parts = []
    
    for i, scene_file in enumerate(scene_files):
        inputs.extend(["-i", scene_file])
    
    # Pilih efek transisi
    transitions = {
        '1': 'fade',
        '2': 'fadeblack',
        '3': 'wipeleft',
        '4': 'wiperight',
        '5': 'slidedown',
        '6': 'slideup',
        '7': 'smoothleft',
        '8': 'smoothright',
        '9': 'circleopen',
        '10': 'circleclose',
        '11': 'dissolve',
        '12': 'pixelize'
    }
    
    effect = transitions.get(transition_type, 'fade')
    
    # Build xfade chain
    current_label = "[0:v]"
    offset = 0
    
    for i in range(len(scene_files) - 1):
        next_input = f"[{i+1}:v]"
        output_label = f"[v{i}]" if i < len(scene_files) - 2 else "[vout]"
        
        if i == 0:
            offset = get_video_duration(scene_files[i]) - TRANSITION_DURATION
        else:
            offset += get_video_duration(scene_files[i]) - TRANSITION_DURATION
        
        filter_parts.append(
            f"{current_label}{next_input}xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}{output_label}"
        )
        current_label = output_label
    
    # Audio mixing
    audio_mix = ""
    for i in range(len(scene_files)):
        audio_mix += f"[{i}:a]"
    audio_mix += f"concat=n={len(scene_files)}:v=0:a=1[aout]"
    
    filter_complex = ";".join(filter_parts) + ";" + audio_mix
    
    cmd = [
        FFMPEG,
        "-y"
    ] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    
    print("   🎞️  Applying transitions...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✅ Merged video saved!")
        return True
    else:
        print(f"   ❌ Merge failed!")
        print(result.stderr[-500:])
        return False

def get_video_duration(video_path):
    """Dapatkan durasi video dalam detik"""
    cmd = [
        FFMPEG,
        "-i", video_path,
        "-f", "null",
        "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.STDOUT)
    
    for line in result.stdout.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = time_str.split(':')
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0

# ========================================
# 📝 INPUT SCENES
# ========================================
print("="*60)
print("🎥 VIDEO SCENE PROCESSOR WITH TRANSITIONS")
print("="*60)
print("Format input waktu: MM:SS atau HH:MM:SS")
print("Contoh: 7:30 atau 1:07:30")
print("="*60)

scenes = []
scene_num = 1

while True:
    print(f"\n{'='*60}")
    print(f"--- Scene {scene_num} ---")
    
    # Input start time
    while True:
        start_input = input(f"Start time scene {scene_num} (atau 'done' untuk selesai): ").strip()
        if start_input.lower() == 'done':
            break
        try:
            start_sec = to_sec(start_input)
            break
        except:
            print("❌ Format salah! Gunakan MM:SS atau HH:MM:SS")
    
    if start_input.lower() == 'done':
        break
    
    # Input duration
    while True:
        try:
            duration = int(input(f"Duration (detik): ").strip())
            if duration > 0:
                break
            print("❌ Duration harus lebih dari 0!")
        except:
            print("❌ Input harus angka!")
    
    # ========================================
    # 🔴 INPUT BORDER MERAH PER SCENE
    # ========================================
    print(f"\n🔴 Border merah berkedip untuk scene {scene_num}?")
    blink_enabled = input("   Ada border merah? (y/n) [n]: ").strip().lower()
    
    blink_config = {'enabled': False}
    
    if blink_enabled == 'y':
        print(f"   (Durasi scene: {duration} detik)")
        
        while True:
            try:
                blink_start = int(input(f"   Mulai kedip di detik ke-: ").strip())
                if 0 <= blink_start < duration:
                    break
                print(f"   ❌ Harus antara 0-{duration-1}")
            except:
                print("   ❌ Input harus angka!")
        
        while True:
            try:
                blink_end = int(input(f"   Berhenti kedip di detik ke-: ").strip())
                if blink_start < blink_end <= duration:
                    break
                print(f"   ❌ Harus antara {blink_start+1}-{duration}")
            except:
                print("   ❌ Input harus angka!")
        
        blink_config = {
            'enabled': True,
            'start': blink_start,
            'end': blink_end
        }
        print(f"   ✅ Border merah: detik {blink_start}-{blink_end}")
    else:
        print(f"   ⚫ Tanpa border merah")
    
    scenes.append({
        'num': scene_num,
        'start': start_sec,
        'duration': duration,
        'blink': blink_config
    })
    
    print(f"\n✅ Scene {scene_num} ditambahkan!")
    print(f"   📍 {sec_to_time(start_sec)} → {duration}s")
    if blink_config['enabled']:
        print(f"   🔴 Border merah: detik {blink_config['start']}-{blink_config['end']}")
    
    scene_num += 1

if not scenes:
    print("\n❌ Tidak ada scene yang diinput!")
    sys.exit(1)

# ========================================
# 🎬 PILIH EFEK TRANSISI
# ========================================
if len(scenes) > 1:
    print("\n" + "="*60)
    print("🎬 PILIH EFEK TRANSISI ANTAR SCENE")
    print("="*60)
    print("1.  Fade (Smooth fade)")
    print("2.  Fade Black (Fade through black)")
    print("3.  Wipe Left (Geser kiri)")
    print("4.  Wipe Right (Geser kanan)")
    print("5.  Slide Down (Turun)")
    print("6.  Slide Up (Naik)")
    print("7.  Smooth Left (Smooth geser kiri)")
    print("8.  Smooth Right (Smooth geser kanan)")
    print("9.  Circle Open (Buka lingkaran)")
    print("10. Circle Close (Tutup lingkaran)")
    print("11. Dissolve (Blur transition)")
    print("12. Pixelize (Pixel effect)")
    print("="*60)
    
    while True:
        transition_choice = input("Pilih transisi (1-12) [default: 1]: ").strip() or '1'
        if transition_choice in [str(i) for i in range(1, 13)]:
            break
        print("❌ Pilihan tidak valid! Pilih 1-12")
else:
    transition_choice = '1'

# ========================================
# 🚀 PROSES SEMUA SCENES
# ========================================
print("\n" + "="*60)
print(f"📋 Total {len(scenes)} scene(s) akan diproses")
print("="*60)

# Tampilkan summary
for scene in scenes:
    blink_info = ""
    if scene['blink']['enabled']:
        blink_info = f" | 🔴 Kedip: {scene['blink']['start']}-{scene['blink']['end']}s"
    else:
        blink_info = " | ⚫ No blink"
    print(f"Scene {scene['num']}: {sec_to_time(scene['start'])} → {scene['duration']}s{blink_info}")

input("\nTekan ENTER untuk mulai proses...")

scene_files = []
for scene in scenes:
    output_file = os.path.join(OUTPUT_DIR, f"scene_{scene['num']:03d}.mp4")
    success = process_scene(
        scene['num'], 
        scene['start'], 
        scene['duration'], 
        output_file,
        scene['blink']
    )
    
    if success:
        scene_files.append(output_file)
    else:
        print(f"\n❌ Scene {scene['num']} gagal diproses!")
        sys.exit(1)

# ========================================
# 🔗 GABUNGKAN SEMUA SCENES DENGAN TRANSISI
# ========================================
success = merge_videos_with_transition(scene_files, FINAL_OUTPUT, transition_choice)

if success:
    # Hapus file scene individual
    print("\n🗑️  Membersihkan file temporary...")
    for scene_file in scene_files:
        try:
            os.remove(scene_file)
            print(f"   Deleted: {os.path.basename(scene_file)}")
        except:
            pass
    
    print(f"\n🎉 SEMUA SELESAI!")
    print(f"📁 Final video: {FINAL_OUTPUT}")
    print(f"⏱️  Durasi transisi: {TRANSITION_DURATION}s")
else:
    print("\n❌ Proses merge gagal!")

print("\n" + "="*60)
