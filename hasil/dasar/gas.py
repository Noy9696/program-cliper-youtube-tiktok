import subprocess, sys, os
from pathlib import Path

# ========================================
# ⚙️ PENGATURAN - EDIT DI SINI
# ========================================
FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
VIDEO_FOLDER = r"D:\CLIP\hasil\dasar"  # Folder isi potongan video
TRANSITION_VIDEO = r"D:\CLIP\hasil\dasar\TV.mp4"  # Video transisi 1 detik
OUTPUT_FILE = r"D:\CLIP\hasil\onlday1.mp4"

# ========================================
# 💧 WATERMARK - EDIT DI SINI
# ========================================
WATERMARK_TEXT = "inibilal999"
WATERMARK_FONT = "Impact"  # Bisa ganti font
WATERMARK_FONT_SIZE = 80  # Ukuran font watermark
WATERMARK_COLOR = "white"  # Warna watermark
WATERMARK_OPACITY = "0.15"  # Transparansi (0.1 = sangat tipis, 0.3 = agak terang)
# Posisi: (w-text_w)/2 = tengah horizontal, (h-text_h)/2 = tengah vertikal

# ========================================
# 📝 TEKS TETAP (MUNCUL DI SEMUA VIDEO)
# ========================================
LIVE_TEXT = ""  # Baris paling atas (kosongkan jika ga mau)
HEADER_TEXT = "ALL JUMPSCARE WINDAH"    # Judul utama

# ========================================
# 📝 TEKS PER SCENE - EDIT DI SINI
# ========================================
SCENE_DESCRIPTIONS = [
    "Terpojok..",
    "Dilabrak mertua",
    "Kaget Brutall",
]

# ========================================
# 🎨 STYLING TEKS - EDIT DI SINI
# ========================================
# FONT SETTINGS
FONT_FILE = "Impact"  # Font meme klasik

# Live text (paling atas, kecil)
LIVE_FONT_SIZE = 35
LIVE_COLOR = "white"

# Header (judul utama)
HEADER_FONT_SIZE = 55
HEADER_COLOR = "yellow"

# Scene list styling
SCENE_FONT_SIZE = 38
SCENE_ACTIVE_COLOR = "white"        # Scene yang lagi main (terang)
SCENE_DONE_COLOR = "#EEEEEE"        # Scene yang udah lewat (abu-abu medium)
SCENE_UPCOMING_COLOR = "#8D8C8C"    # Scene yang belum (abu-abu terang, lebih keliatan)

# Outline untuk semua teks
OUTLINE_COLOR = "black"
OUTLINE_WIDTH = 3

# Posisi dan spacing - EDIT DI SINI UNTUK ADJUST POSISI!
TEXT_X = 30  # 30px dari kiri
TEXT_Y_START = 80  # Mulai dari atas (naik/turun judul - makin besar makin turun)
LIVE_TO_HEADER_GAP = 15  # Jarak Live ke Header
HEADER_TO_SCENE_GAP = 35  # Jarak Header ke Scene List (makin besar, list makin turun)
SCENE_LINE_SPACING = 48  # Jarak antar baris scene

# Jumlah scene yang ditampilkan dalam list
MAX_VISIBLE_SCENES = 5  # Maksimal 5 baris scene yang keliatan

# ========================================
# 🎬 PROGRAM MULAI
# ========================================
print("="*60)
print("🎬 VIDEO MERGER - PROGRESSIVE SCENE LIST + WATERMARK")
print("="*60)
print(f"📁 Video folder: {VIDEO_FOLDER}")
print(f"🎞️  Transition: {TRANSITION_VIDEO}")
print(f"💾 Output: {OUTPUT_FILE}")
print(f"🎨 Font: {FONT_FILE}")
print(f"📊 Max visible scenes: {MAX_VISIBLE_SCENES}")
print(f"💧 Watermark: {WATERMARK_TEXT} (opacity: {WATERMARK_OPACITY})")
print("="*60)

# Cek folder ada
if not os.path.exists(VIDEO_FOLDER):
    print(f"❌ Folder tidak ditemukan: {VIDEO_FOLDER}")
    input("Tekan ENTER untuk keluar...")
    sys.exit(1)

# Cek transition video ada
if not os.path.exists(TRANSITION_VIDEO):
    print(f"❌ Video transisi tidak ditemukan: {TRANSITION_VIDEO}")
    input("Tekan ENTER untuk keluar...")
    sys.exit(1)

# Ambil semua video di folder KECUALI transition video
video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
video_files = []
transition_path_normalized = os.path.normpath(TRANSITION_VIDEO).lower()

for file in sorted(os.listdir(VIDEO_FOLDER)):
    if any(file.lower().endswith(ext) for ext in video_extensions):
        full_path = os.path.join(VIDEO_FOLDER, file)
        full_path_normalized = os.path.normpath(full_path).lower()
        
        if full_path_normalized == transition_path_normalized:
            print(f"⏭️  Skipping transition file: {file}")
            continue
        
        video_files.append(full_path)

if not video_files:
    print(f"❌ Tidak ada video di folder: {VIDEO_FOLDER}")
    input("Tekan ENTER untuk keluar...")
    sys.exit(1)

# Tampilkan video yang ditemukan
print(f"\n📹 Ditemukan {len(video_files)} video:")
for i, vf in enumerate(video_files, 1):
    file_size = os.path.getsize(vf) / (1024*1024)
    print(f"   {i}. {os.path.basename(vf)} ({file_size:.1f} MB)")

# Cek jumlah deskripsi vs video
if len(SCENE_DESCRIPTIONS) < len(video_files):
    print(f"\n⚠️  WARNING: Deskripsi cuma ada {len(SCENE_DESCRIPTIONS)}, tapi video ada {len(video_files)}")
    while len(SCENE_DESCRIPTIONS) < len(video_files):
        SCENE_DESCRIPTIONS.append(f"SCENE {len(SCENE_DESCRIPTIONS)+1}")

print(f"\n📝 Preview progressive list:")
print(f"   Total scenes: {len(video_files)}")
print(f"\n   Contoh Video 1:")
print(f"      1. {SCENE_DESCRIPTIONS[0]} ← ACTIVE (putih terang)")
if len(SCENE_DESCRIPTIONS) > 1:
    print(f"      2. {SCENE_DESCRIPTIONS[1]} ← upcoming (abu terang)")
if len(SCENE_DESCRIPTIONS) > 2:
    print(f"      3. {SCENE_DESCRIPTIONS[2]} ← upcoming (abu terang)")

print(f"\n   Contoh Video 2:")
print(f"      1. {SCENE_DESCRIPTIONS[0]} ← done (abu medium)")
if len(SCENE_DESCRIPTIONS) > 1:
    print(f"      2. {SCENE_DESCRIPTIONS[1]} ← ACTIVE (putih terang)")
if len(SCENE_DESCRIPTIONS) > 2:
    print(f"      3. {SCENE_DESCRIPTIONS[2]} ← upcoming (abu terang)")

# Konfirmasi
input("\nTekan ENTER untuk mulai proses...")

# ========================================
# 🎨 PROSES: Tambah Teks ke Semua Scene
# ========================================
print("\n🎨 Step 1: Menambahkan progressive list + watermark ke semua scene...")
print("="*60)

temp_videos_with_text = []

for current_scene_idx, (video_file, description) in enumerate(zip(video_files, SCENE_DESCRIPTIONS), 1):
    temp_output = os.path.join(os.path.dirname(OUTPUT_FILE), f"temp_text_{current_scene_idx:03d}.mp4")
    temp_videos_with_text.append(temp_output)
    
    print(f"   [{current_scene_idx}/{len(video_files)}] {os.path.basename(video_file)}...", end=" ", flush=True)
    
    # Escape teks untuk ffmpeg
    live_escaped = LIVE_TEXT.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    header_escaped = HEADER_TEXT.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    watermark_escaped = WATERMARK_TEXT.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    
    # Hitung posisi Y mulai
    current_y = TEXT_Y_START
    
    # Build drawtext filter
    filters = []
    
    # ========================================
    # 💧 WATERMARK DI TENGAH (PERTAMA KALI!)
    # ========================================
    filters.append(
        f"drawtext=text='{watermark_escaped}':"
        f"font={WATERMARK_FONT}:"
        f"fontsize={WATERMARK_FONT_SIZE}:"
        f"fontcolor={WATERMARK_COLOR}@{WATERMARK_OPACITY}:"  # @ untuk alpha/opacity
        f"x=(w-text_w)/2:"  # Tengah horizontal
        f"y=(h-text_h)/2"   # Tengah vertikal
    )
    
    # BARIS 1: Live info (opsional)
    if LIVE_TEXT:
        filters.append(
            f"drawtext=text='{live_escaped}':"
            f"font={FONT_FILE}:"
            f"fontsize={LIVE_FONT_SIZE}:"
            f"fontcolor={LIVE_COLOR}:"
            f"bordercolor={OUTLINE_COLOR}:"
            f"borderw={OUTLINE_WIDTH}:"
            f"x={TEXT_X}:"
            f"y={current_y}"
        )
        current_y += LIVE_FONT_SIZE + LIVE_TO_HEADER_GAP
    
    # BARIS 2: Header/Judul
    filters.append(
        f"drawtext=text='{header_escaped}':"
        f"font={FONT_FILE}:"
        f"fontsize={HEADER_FONT_SIZE}:"
        f"fontcolor={HEADER_COLOR}:"
        f"bordercolor={OUTLINE_COLOR}:"
        f"borderw={OUTLINE_WIDTH}:"
        f"x={TEXT_X}:"
        f"y={current_y}"
    )
    current_y += HEADER_FONT_SIZE + HEADER_TO_SCENE_GAP
    
    # BARIS 3+: Scene list (progressive)
    # Tentukan range scene yang mau ditampilkan
    start_idx = max(0, current_scene_idx - 1)  # Mulai dari scene sekarang
    end_idx = min(len(SCENE_DESCRIPTIONS), start_idx + MAX_VISIBLE_SCENES)
    
    for scene_idx in range(start_idx, end_idx):
        scene_num = scene_idx + 1
        scene_desc = SCENE_DESCRIPTIONS[scene_idx]
        scene_text = f"{scene_num}. {scene_desc}"
        scene_escaped = scene_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        
        # Tentukan warna berdasarkan status
        if scene_num < current_scene_idx:
            # Scene yang udah lewat
            color = SCENE_DONE_COLOR
        elif scene_num == current_scene_idx:
            # Scene yang lagi main (ACTIVE)
            color = SCENE_ACTIVE_COLOR
        else:
            # Scene yang belum
            color = SCENE_UPCOMING_COLOR
        
        filters.append(
            f"drawtext=text='{scene_escaped}':"
            f"font={FONT_FILE}:"
            f"fontsize={SCENE_FONT_SIZE}:"
            f"fontcolor={color}:"
            f"bordercolor={OUTLINE_COLOR}:"
            f"borderw={OUTLINE_WIDTH}:"
            f"x={TEXT_X}:"
            f"y={current_y}"
        )
        current_y += SCENE_LINE_SPACING
    
    drawtext_filter = ",".join(filters)
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_file,
        "-vf", drawtext_filter,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-c:a", "copy",
        temp_output
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FAILED")
        print(f"\n📋 Error:")
        print(result.stderr[-500:])
        # Cleanup
        for temp in temp_videos_with_text:
            try: os.remove(temp)
            except: pass
        sys.exit(1)
    
    print(f"✅")

# ========================================
# 🔗 MERGE: Gabung dengan Transisi
# ========================================
print(f"\n🔗 Step 2: Menggabung semua video dengan transisi...")
print("="*60)

# Buat concat list: video1 -> trans -> video2 -> trans -> ...
concat_list = []
for i, temp_video in enumerate(temp_videos_with_text):
    concat_list.append(temp_video)
    if i < len(temp_videos_with_text) - 1:
        concat_list.append(TRANSITION_VIDEO)

print(f"   Total item untuk digabung: {len(concat_list)}")

# Re-encode semua dulu biar sama format
print(f"\n📦 Step 3: Re-encoding untuk kompatibilitas...")
final_temp_list = []

# Re-encode transition
temp_trans = os.path.join(os.path.dirname(OUTPUT_FILE), "temp_transition_norm.mp4")
print(f"   Re-encoding transition...", end=" ", flush=True)
cmd = [
    FFMPEG, "-y",
    "-i", TRANSITION_VIDEO,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "25",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "48000",
    "-ac", "2",
    temp_trans
]
subprocess.run(cmd, capture_output=True, text=True)
print("✅")

# Re-encode scenes with text
for i, temp_video in enumerate(temp_videos_with_text, 1):
    temp_norm = os.path.join(os.path.dirname(OUTPUT_FILE), f"temp_norm_{i:03d}.mp4")
    final_temp_list.append(temp_norm)
    
    print(f"   Re-encoding scene {i}/{len(temp_videos_with_text)}...", end=" ", flush=True)
    
    cmd = [
        FFMPEG, "-y",
        "-i", temp_video,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "25",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        temp_norm
    ]
    
    subprocess.run(cmd, capture_output=True, text=True)
    print("✅")

# Update concat list dengan file normalized
concat_list_final = []
for i, temp_norm in enumerate(final_temp_list):
    concat_list_final.append(temp_norm)
    if i < len(final_temp_list) - 1:
        concat_list_final.append(temp_trans)

# Tulis list file
list_file = os.path.join(os.path.dirname(OUTPUT_FILE), "merge_list.txt")
with open(list_file, "w", encoding="utf-8") as f:
    for video in concat_list_final:
        escaped_path = video.replace("\\", "/")
        f.write(f"file '{escaped_path}'\n")

# Final merge
print(f"\n🎬 Step 4: Final merge...")
cmd_merge = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", list_file,
    "-c", "copy",
    "-movflags", "+faststart",
    OUTPUT_FILE
]

result = subprocess.run(cmd_merge, capture_output=True, text=True)

# Cleanup
print(f"\n🗑️  Cleaning up temporary files...")
try: os.remove(list_file)
except: pass
try: os.remove(temp_trans)
except: pass
for temp in temp_videos_with_text:
    try: os.remove(temp)
    except: pass
for temp in final_temp_list:
    try: os.remove(temp)
    except: pass

if result.returncode == 0:
    output_size = os.path.getsize(OUTPUT_FILE) / (1024*1024)
    print(f"\n✅ SELESAI!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print(f"📊 Size: {output_size:.1f} MB")
    print(f"\n💧 Watermark Settings:")
    print(f"   ✅ Text: {WATERMARK_TEXT}")
    print(f"   ✅ Position: CENTER")
    print(f"   ✅ Opacity: {WATERMARK_OPACITY}")
    print(f"\n📝 Progressive List Features:")
    print(f"   ✅ Scene active: PUTIH TERANG")
    print(f"   ✅ Scene done: ABU-ABU MEDIUM")
    print(f"   ✅ Scene upcoming: ABU-ABU TERANG (lebih keliatan)")
    print(f"   ✅ Max {MAX_VISIBLE_SCENES} scenes visible per video")
    print(f"\n🎨 Kalau mau adjust watermark:")
    print(f"   - WATERMARK_OPACITY (transparansi: 0.1-0.5)")
    print(f"   - WATERMARK_FONT_SIZE (ukuran font)")
    print(f"   - WATERMARK_COLOR (warna)")
else:
    print(f"\n❌ GAGAL!")
    print(f"\n📋 Error:")
    print(result.stderr[-800:])

print(f"\n🎉 PROGRAM SELESAI!")
print("="*60)
input("\nTekan ENTER untuk keluar...")