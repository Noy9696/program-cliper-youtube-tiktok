import subprocess
import sys
import os
from datetime import datetime

def to_sec(t):
    """Convert time string to seconds"""
    parts = list(map(int, t.split(":")))
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    raise ValueError("Format waktu salah")

def sec_to_time(sec):
    """Convert seconds to time string"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

# ========================================
# 🎬 CONFIGURATION (akan di-override dari app.py)
# ========================================
FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
SOURCE = r"D:\CLIP\hasil\Mentah.mp4"
OUTPUT_DIR = r"D:\CLIP\hasil\dasar"

TRANSITION_DURATION = 0.8
BLINK_SPEED = 0.5
GAMER_WIDTH = 0.16
GAMER_HEIGHT = 0.28
GAMER_X_POS = 0.80
GAMER_Y_POS = 0.70

# ========================================
# 💧 WATERMARK CONFIGURATION
# ========================================
WATERMARK_TEXT = "inibilal999"
WATERMARK_FONT = "Impact"  # Bisa ganti font
WATERMARK_FONT_SIZE = 80  # Ukuran font watermark
WATERMARK_COLOR = "white"  # Warna watermark
WATERMARK_OPACITY = "0.15"  # Transparansi (0.1 = sangat tipis, 0.3 = agak terang)

# ========================================
# ✍️ TEXT CONFIGURATION (ubah sesukamu!)
#
# ========================================
TEXT_GAMER_SIDE = "LIVE WINDAH BASUDARA"  # Simbol bulat hitam (akan keliatan putih)
TEXT_ABOVE_CONTENT = ""  # Simbol arrow
TEXT_FONT = "Impact"  # Font yang dipakai
TEXT_FONT_SIZE_GAMER = 35  # Ukuran font teks samping gamer
TEXT_FONT_SIZE_CONTENT = 45  # Ukuran font teks atas content
TEXT_COLOR = "white"  # Warna teks
TEXT_OUTLINE_COLOR = "White"  # Warna outline/border teks
TEXT_OUTLINE_WIDTH = 1  # Ketebalan outline


# ========================================
# 🎨 ICON CONFIGURATION ADVANCED (opsional - pakai gambar custom)
# ========================================
USE_CUSTOM_ICONS = False  # Set True kalau mau pakai gambar icon sendiri
# Path ke file icon (PNG dengan background transparan recommended)
ICON_LIVE_PATH = r"D:\CLIP\icons\red_dot.png"  # Icon bulat merah untuk LIVE
ICON_HIGHLIGHT_PATH = r"D:\CLIP\icons\laugh.png"  # Icon ketawa untuk HIGHLIGHT
ICON_SIZE_LIVE = 35  # Ukuran icon LIVE dalam pixel
ICON_SIZE_HIGHLIGHT = 45  # Ukuran icon HIGHLIGHT dalam pixel


# ========================================
# 😅 EMOJI CONFIGURATION (bisa ubah sesuka hati!)
# ========================================
USE_EMOJI = False # Set False kalau ga mau emoji
EMOJI_BLINK = False  # Set True kalau mau emoji kedip-kedip, False = always on
EMOJI_PATH = r"D:\CLIP\web\moi.png"  # Path emoji PNG
EMOJI_SIZE = 85  # Ukuran emoji

# Posisi emoji (ubah sesuka hati!)
EMOJI_X = "475"   # Kiri-kanan (0-1080)
EMOJI_Y = "100"    # Atas-bawah (0-1920)

def process_scene(scene_num, start_time, duration, output_path, blink_config, gamer_position, source_video=None):
    """Proses satu scene dengan optional border merah berkedip dan posisi gamer"""
    
    # ✅ FIX: Gunakan SOURCE global jika source_video tidak diberikan
    video_source = source_video if source_video else SOURCE
    
    # Build filter untuk gamer dengan atau tanpa border merah
    if blink_config['enabled']:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            "scale=450:500,"
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6,"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=red:t=8:enable='between(t,{blink_config['start']},{blink_config['end']})*gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[gamer];"
        )
    else:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            "scale=450:500,"
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6[gamer];"
        )
    
    # Tentukan posisi gamer berdasarkan pilihan
    if gamer_position == 'atas':
        gamer_y = "40"
        main_y = "H-h-80"
        # Posisi teks samping gamer (lebih ke kiri dan ke atas)
        text_gamer_x = "15"
        text_gamer_y = "40"  # Lebih ke atas dari gamer box
        # Posisi teks atas content
        text_content_y = "H-1800"  # Lebih ke atas dari content
        # Posisi icon (jika pakai custom icon)
        icon_live_x = "20"
        icon_live_y = "40"
        icon_highlight_x = "10"
        icon_highlight_y = "H-1645"
    else:
        gamer_y = "H-h-40"
        main_y = "80"
        # Posisi teks samping gamer (lebih ke kiri dan sejajar atas gamer)
        text_gamer_x = "15"
        text_gamer_y = "H-h-15"  # Sejajar dengan top gamer box
        # Posisi teks atas content
        text_content_y = "20"  # Lebih ke atas sedikit dari sebelumnya
        # Posisi icon (jika pakai custom icon)
        icon_live_x = "10"
        icon_live_y = "H-h-30"
        icon_highlight_x = "10"
        icon_highlight_y = "35"
    
    # Escape teks untuk ffmpeg (ganti : dengan \:)
    text_gamer_escaped = TEXT_GAMER_SIDE.replace(':', r'\:').replace("'", r"\'")
    text_content_escaped = TEXT_ABOVE_CONTENT.replace(':', r'\:').replace("'", r"\'")
    watermark_escaped = WATERMARK_TEXT.replace(':', r'\:').replace("'", r"\'")
    
    # Build filter chain
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=40:1[bg];"
        
        "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        "scale=1080:1500:force_original_aspect_ratio=decrease,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6[main];"
        
        + gamer_filter +
        
        f"[bg][main]overlay=(W-w)/2:{main_y}[tmp];"
        f"[tmp][gamer]overlay=W-w-40:{gamer_y}[tmp2];"
    )
    
    # ========================================
    # 💧 TAMBAHKAN WATERMARK DI TENGAH (PERTAMA!)
    # ========================================
    vf += (
        f"[tmp2]drawtext=text='{watermark_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={WATERMARK_FONT_SIZE}:"
        f"fontcolor={WATERMARK_COLOR}@{WATERMARK_OPACITY}:"  # @ untuk alpha/opacity
        f"x=(w-text_w)/2:"  # Tengah horizontal
        f"y=(h-text_h)/2[tmp2w];"  # Tengah vertikal
    )
    
    # Tambahkan teks dengan efek kedip-kedip untuk emoji 🔴
    # Emoji akan otomatis muncul di teks, tapi kita bisa bikin efek kedip
    vf += (
        # Gambar bulat merah kedip-kedip untuk LIVE CAM
        f"[tmp2w]drawbox=x={text_gamer_x}:y={text_gamer_y}:w=25:h=25:color=red:t=fill:"
        f"enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[tmp2b];"
        
        # Teks LIVE CAM (tanpa efek kedip di teks)
        f"[tmp2b]drawtext=text='{text_gamer_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_GAMER}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x={int(text_gamer_x)+35}:y={text_gamer_y}[tmp3];"
        
        # Teks HIGHLIGHT (tanpa kedip)
        f"[tmp3]drawtext=text='{text_content_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_CONTENT}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x=10:y={text_content_y}[v]"
    )
    
    # Input files
    inputs = ["-i", video_source]
    
    # ✅ FIX: Tambahkan emoji sebagai input jika diaktifkan
    emoji_input_index = None
    if USE_EMOJI and os.path.exists(EMOJI_PATH):
        inputs.extend(["-i", EMOJI_PATH])
        emoji_input_index = 1  # Index input emoji (setelah video source)
        
        # Tambahkan overlay emoji ke filter
        # PENTING: Ganti output [v] menjadi [vtmp], lalu overlay emoji, hasilnya [v]
        vf = vf.replace("[v]", "[vtmp]")  # Rename output terakhir
        vf += f";[{emoji_input_index}:v]scale={EMOJI_SIZE}:{EMOJI_SIZE}[emoji];"
        
        # Pilih mode: kedip atau always on
        if EMOJI_BLINK:
            # Mode KEDIP-KEDIP (on/off)
            vf += f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}:enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[v]"
            print(f"   😎 Emoji enabled: {os.path.basename(EMOJI_PATH)} @ ({EMOJI_X},{EMOJI_Y}) [BLINKING]")
        else:
            # Mode ALWAYS ON (ga kedip)
            vf += f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}[v]"
            print(f"   😎 Emoji enabled: {os.path.basename(EMOJI_PATH)} @ ({EMOJI_X},{EMOJI_Y}) [ALWAYS ON]")
    
    # Jika pakai custom icon (gambar)
    if USE_CUSTOM_ICONS:
        if os.path.exists(ICON_LIVE_PATH):
            inputs.extend(["-i", ICON_LIVE_PATH])
        if os.path.exists(ICON_HIGHLIGHT_PATH):
            inputs.extend(["-i", ICON_HIGHLIGHT_PATH])
        
        # NOTE: Kalau mau pakai custom icon, perlu modifikasi filter_complex
        # untuk overlay gambar icon. Ini lebih kompleks, jadi lebih simpel pakai emoji.
    
    cmd = [
        FFMPEG,
        "-y",
        "-ss", str(start_time)
    ] + inputs + [
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
    print(f"   🎮 Gamer position: Pojok kanan {gamer_position}")
    print(f"   💧 Watermark: '{WATERMARK_TEXT}' @ center (opacity: {WATERMARK_OPACITY})")
    print(f"   ✍️  Text gamer: '{TEXT_GAMER_SIDE}' (dengan efek kedip)")
    print(f"   ✍️  Text content: '{TEXT_ABOVE_CONTENT}'")
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


def merge_videos_simple(scene_files, output_path, output_dir=None):
    """Gabungkan semua scene tanpa transisi (simple concat) - lebih cepat & stabil"""
    # ✅ FIX: Gunakan OUTPUT_DIR global jika tidak diberikan
    out_dir = output_dir if output_dir else OUTPUT_DIR
    
    print(f"\n🔗 Merging {len(scene_files)} scenes (simple concat)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        return True
    
    # Buat file list untuk concat
    list_file = os.path.join(out_dir, "filelist.txt")
    with open(list_file, "w") as f:
        for scene_file in scene_files:
            f.write(f"file '{os.path.abspath(scene_file)}'\n")
    
    cmd = [
        FFMPEG,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        "-movflags", "+faststart",
        output_path
    ]
    
    print("   🎞️  Concatenating videos...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Hapus file temporary list
    try:
        os.remove(list_file)
    except:
        pass
    
    if result.returncode == 0:
        print(f"   ✅ Merged video saved!")
        return True
    else:
        print(f"   ❌ Merge failed!")
        print(result.stderr[-500:])
        return False


def merge_videos_with_transition_stepwise(scene_files, output_path, transition_type, output_dir=None):
    """
    METODE BERTAHAP - Merge 2 video at a time (PALING STABIL!)
    Cocok untuk banyak scene dan transisi kompleks
    """
    # ✅ FIX: Gunakan OUTPUT_DIR global jika tidak diberikan
    out_dir = output_dir if output_dir else OUTPUT_DIR
    
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (stepwise method)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        return True
    
    # Pilih efek transisi
    transitions = {
        '1': 'fade',
        '2': 'fadeblack',
        '3': 'wipeleft',
        '4': 'wiperight',
        '5': 'slidedown',
        '6': 'slideup',
    }
    
    effect = transitions.get(transition_type, 'fade')
    print(f"   🎨 Effect: {effect}")
    print(f"   ⏱️  Duration: {TRANSITION_DURATION}s")
    
    # Merge secara bertahap (2 file at a time)
    temp_files = []
    current_input = scene_files[0]
    
    for i in range(1, len(scene_files)):
        print(f"\n   🔗 Merging part {i}/{len(scene_files)-1}...")
        
        temp_output = os.path.join(out_dir, f"temp_merge_{i}.mp4")
        temp_files.append(temp_output)
        
        # Get duration dari current input
        probe_cmd = [FFMPEG, "-i", current_input]
        probe_result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        duration = 10  # default fallback
        for line in probe_result.stderr.split('\n'):
            if 'Duration:' in line:
                try:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    duration = float(h) * 3600 + float(m) * 60 + float(s)
                    break
                except:
                    pass
        
        offset = max(0, duration - TRANSITION_DURATION)
        
        print(f"      📊 Input duration: {duration:.1f}s | Offset: {offset:.1f}s")
        
        cmd = [
            FFMPEG, "-y",
            "-i", current_input,
            "-i", scene_files[i],
            "-filter_complex",
            f"[0:v][1:v]xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}[vout];"
            f"[0:a][1:a]acrossfade=d={TRANSITION_DURATION}[aout]",
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-progress", "pipe:1",
            "-nostats",
            temp_output
        ]
        
        # Run dengan progress
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                value = line.split("=")[1]
                if value != "N/A":
                    ms = int(value)
                    sys.stdout.write(f"\r      ⏳ Progress: {ms/1_000_000:5.1f}s")
                    sys.stdout.flush()
        
        stderr_output = process.stderr.read()
        process.wait()
        
        if process.returncode != 0:
            print(f"\n      ❌ Failed at merge {i}")
            print("      Error details:")
            print(stderr_output[-800:])
            # Cleanup temp files only
            for temp in temp_files:
                try: os.remove(temp)
                except: pass
            return False
        
        print(f"\n      ✅ Part {i} merged!")
        current_input = temp_output
    
    # Rename final temp file to output
    print(f"\n   📦 Finalizing output...")
    import shutil
    shutil.move(current_input, output_path)
    
    # Cleanup temp files (kecuali yang terakhir yang sudah di-rename)
    print(f"   🗑️  Cleaning up temporary merge files...")
    for temp in temp_files[:-1]:
        try:
            os.remove(temp)
            print(f"      Deleted: {os.path.basename(temp)}")
        except:
            pass
    
    print(f"\n   ✅ Merged video saved!")
    return True


def merge_videos_with_transition_batch(scene_files, output_path, transition_type):
    """
    METODE BATCH - Process semua sekaligus (lebih cepat tapi kurang stabil untuk banyak scene)
    Cocok untuk 2-4 scene
    """
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (batch method)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        return True
    
    # Build inputs
    inputs = []
    for scene_file in scene_files:
        inputs.extend(["-i", scene_file])
    
    # Pilih efek transisi
    transitions = {
        '1': 'fade',
        '2': 'fadeblack',
        '3': 'wipeleft',
        '4': 'wiperight',
        '5': 'slidedown',
        '6': 'slideup',
    }
    
    effect = transitions.get(transition_type, 'fade')
    print(f"   🎨 Effect: {effect}")
    print(f"   ⏱️  Duration: {TRANSITION_DURATION}s")
    
    # Get duration untuk setiap file
    durations = []
    for scene_file in scene_files:
        probe_cmd = [FFMPEG, "-i", scene_file]
        probe_result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        duration = 0
        for line in probe_result.stderr.split('\n'):
            if 'Duration:' in line:
                try:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    duration = float(h) * 3600 + float(m) * 60 + float(s)
                    break
                except:
                    pass
        
        if duration == 0:
            print(f"   ⚠️  Warning: Could not get duration for {os.path.basename(scene_file)}")
            duration = 10
        
        durations.append(duration)
        print(f"   📹 Scene {len(durations)}: {duration:.2f}s")
    
    # Build xfade chain
    filter_parts = []
    
    if len(scene_files) == 2:
        # Untuk 2 file saja
        offset = durations[0] - TRANSITION_DURATION
        filter_parts.append(f"[0:v][1:v]xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}[vout]")
    else:
        # Untuk 3+ file
        offset = durations[0] - TRANSITION_DURATION
        
        # First xfade
        filter_parts.append(f"[0:v][1:v]xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}[vt1]")
        
        # Middle xfades
        for i in range(2, len(scene_files)):
            offset += durations[i-1] - TRANSITION_DURATION
            prev_label = f"[vt{i-1}]"
            curr_input = f"[{i}:v]"
            
            # Label terakhir harus [vout]
            if i == len(scene_files) - 1:
                curr_label = "[vout]"
            else:
                curr_label = f"[vt{i}]"
            
            filter_parts.append(f"{prev_label}{curr_input}xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}{curr_label}")
    
    # Audio concat
    audio_inputs = "".join([f"[{i}:a]" for i in range(len(scene_files))])
    filter_parts.append(f"{audio_inputs}concat=n={len(scene_files)}:v=0:a=1[aout]")
    
    filter_complex = ";".join(filter_parts)
    
    # Debug: tampilkan filter
    print(f"\n   🔍 Filter chain:")
    for fp in filter_parts:
        print(f"      {fp}")
    
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
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]
    
    print(f"\n   🎞️  Processing transition...")
    
    # Show progress
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    total_duration = sum(durations) - (len(durations) - 1) * TRANSITION_DURATION
    
    for line in process.stdout:
        line = line.strip()
        if line.startswith("out_time_ms="):
            value = line.split("=")[1]
            if value != "N/A":
                ms = int(value)
                current_sec = ms / 1_000_000
                pct = min((current_sec / total_duration) * 100, 100)
                sys.stdout.write(f"\r   ⏳ Progress: {pct:5.1f}% | {current_sec:5.1f}s / {total_duration:.1f}s")
                sys.stdout.flush()
    
    stderr_output = process.stderr.read()
    process.wait()
    
    if process.returncode == 0:
        print(f"\n   ✅ Merged video saved!")
        return True
    else:
        print(f"\n   ❌ Merge failed!")
        print("\n📋 Error details:")
        print(stderr_output[-1000:])
        return False