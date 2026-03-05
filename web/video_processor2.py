import subprocess
import sys
import os
from datetime import datetime
import random

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
# 🎨 BORDER RADIUS CONFIGURATION
# ========================================
MAIN_BORDER_RADIUS = 30              # Radius untuk main content box (0-50)
GAMER_BORDER_RADIUS = 25             # Radius untuk gamer box (0-50)
BORDER_THICKNESS = 5                 # Ketebalan border

# ========================================
# 🌈 COLOR PRESET LIBRARY - 8 PILIHAN WARNA PREMIUM!
# ========================================
COLOR_PRESETS = {
    1: {
        'name': 'ROYAL GOLD',
        'desc': '👑 Gold premium - paling elegant di background hitam',
        'main': '#D4AF37',
        'gamer': '#B8962E'
    },
    2: {
        'name': 'DEEP CRIMSON',
        'desc': '🩸 Merah gelap - cinematic & horror classy',
        'main': '#8B0000',
        'gamer': '#6A0000'
    },
    3: {
        'name': 'ROYAL PURPLE',
        'desc': '🔮 Ungu kerajaan - mysterious & luxury',
        'main': '#6A0DAD',
        'gamer': '#4B0082'
    },
    4: {
        'name': 'EMERALD ELEGANT',
        'desc': '💚 Hijau emerald - premium & calm',
        'main': '#046307',
        'gamer': '#034A05'
    },
    5: {
        'name': 'NEON CYAN PREMIUM',
        'desc': '💎 Cyan modern - glow elegant',
        'main': '#00C2D1',
        'gamer': '#0097A7'
    },
    6: {
        'name': 'ROYAL BLUE',
        'desc': '🔷 Biru royal - clean & professional',
        'main': '#0B3D91',
        'gamer': '#072A66'
    },
    7: {
        'name': 'MAGENTA ROYAL',
        'desc': '🌌 Magenta luxury - elegant & cinematic',
        'main': '#8B008B',
        'gamer': '#5A005A'
    },
    8: {
        'name': 'AMBER GOLD',
        'desc': '🔥 Gold amber - warm premium',
        'main': '#FF8F00',
        'gamer': '#C67100'
    },
    9: {
        'name': 'BLOOD RED NEON',
        'desc': '🧛 Horror premium - merah horror elegant',
        'main': '#B11226',
        'gamer': '#7A0C1A'
    },
    10: {
        'name': 'PLATINUM PURPLE',
        'desc': '💠 Luxury ultra - paling mahal looknya',
        'main': '#A020F0',
        'gamer': '#6A0DAD'
    }
}
# ========================================
# 🎨 BORDER COLOR CONFIGURATION
# ========================================
# MODE: True = Random per scene, False = Manual pilih nomor
USE_RANDOM_COLOR = True

# Kalau USE_RANDOM_COLOR = False, pilih nomor preset (1-8)
SELECTED_COLOR_PRESET = 5

# Fungsi untuk get warna
def get_border_colors():
    """Ambil warna border sesuai setting"""
    if USE_RANDOM_COLOR:
        preset_num = random.randint(1, 8)
        print(f"\n🎲 RANDOM COLOR: #{preset_num} - {COLOR_PRESETS[preset_num]['name']}")
    else:
        preset_num = SELECTED_COLOR_PRESET
        if preset_num not in COLOR_PRESETS:
            print(f"\n⚠️  Warning: Preset #{preset_num} tidak ada, pakai preset #1")
            preset_num = 1
        print(f"\n🎨 SELECTED COLOR: #{preset_num} - {COLOR_PRESETS[preset_num]['name']}")
    
    preset = COLOR_PRESETS[preset_num]
    print(f"   {preset['desc']}")
    return preset['main'], preset['gamer'], preset['name']

# Get warna default (hanya aktif kalau USE_RANDOM_COLOR = False)
BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME = get_border_colors()

# ========================================
# 💧 WATERMARK CONFIGURATION
# ========================================
WATERMARK_TEXT = "inibilal999"
WATERMARK_FONT = "Impact"
WATERMARK_FONT_SIZE = 80
WATERMARK_COLOR = "white"
WATERMARK_OPACITY = "0.15"

# ========================================
# ✍️ TEXT CONFIGURATION
# ========================================
TEXT_GAMER_SIDE = "LIVE WINDAH BASUDARA"
TEXT_ABOVE_CONTENT = "Streamer Betingkah wkwk"
TEXT_FONT = "Impact"
TEXT_FONT_SIZE_GAMER = 35
TEXT_FONT_SIZE_CONTENT = 45
TEXT_COLOR = "white"
TEXT_OUTLINE_COLOR = "White"
TEXT_OUTLINE_WIDTH = 1

# ========================================
# 🎨 ICON CONFIGURATION ADVANCED
# ========================================
USE_CUSTOM_ICONS = False
ICON_LIVE_PATH = r"D:\CLIP\icons\red_dot.png"
ICON_HIGHLIGHT_PATH = r"D:\CLIP\icons\laugh.png"
ICON_SIZE_LIVE = 35
ICON_SIZE_HIGHLIGHT = 45

# ========================================
# 😅 EMOJI CONFIGURATION
# ========================================
USE_EMOJI = False
EMOJI_BLINK = False
EMOJI_PATH = r"D:\CLIP\web\moi.png"
EMOJI_SIZE = 85
EMOJI_X = "475"
EMOJI_Y = "100"

# ========================================
# 🎬 INTRO VIDEO CONFIGURATION
# ========================================
USE_INTRO = True
INTRO_PATH = r"D:\CLIP\hasil\TV.mp4"

def process_scene(scene_num, start_time, duration, output_path, blink_config, gamer_position, source_video=None):
    """Proses satu scene dengan optional border merah berkedip dan posisi gamer"""

    # ✅ FIX: Kalau random mode, tiap scene dapet warna random sendiri-sendiri
    global BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME
    if USE_RANDOM_COLOR:
        BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME = get_border_colors()

    video_source = source_video if source_video else SOURCE
    
    # Build filter untuk gamer dengan border radius premium + WARNA DARI PRESET
    if blink_config['enabled']:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            "scale=450:500,"
            # Rounded corners untuk gamer box
            f"format=yuva420p,geq=lum='p(X,Y)':a='if(gt(abs(W/2-X),W/2-{GAMER_BORDER_RADIUS})*gt(abs(H/2-Y),H/2-{GAMER_BORDER_RADIUS}),if(lte(hypot({GAMER_BORDER_RADIUS}-(W/2-abs(W/2-X)),{GAMER_BORDER_RADIUS}-(H/2-abs(H/2-Y))),{GAMER_BORDER_RADIUS}),255,0),255)',"
            f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_GAMER}:t={BORDER_THICKNESS},"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=red:t=8:enable='between(t,{blink_config['start']},{blink_config['end']})*gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[gamer];"
        )
    else:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            "scale=450:500,"
            # Rounded corners untuk gamer box
            f"format=yuva420p,geq=lum='p(X,Y)':a='if(gt(abs(W/2-X),W/2-{GAMER_BORDER_RADIUS})*gt(abs(H/2-Y),H/2-{GAMER_BORDER_RADIUS}),if(lte(hypot({GAMER_BORDER_RADIUS}-(W/2-abs(W/2-X)),{GAMER_BORDER_RADIUS}-(H/2-abs(H/2-Y))),{GAMER_BORDER_RADIUS}),255,0),255)',"
            f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_GAMER}:t={BORDER_THICKNESS}[gamer];"
        )
    
    # Tentukan posisi gamer
    if gamer_position == 'atas':
        gamer_y = "40"
        main_y = "H-h-80"
        text_gamer_x = "15"
        text_gamer_y = "40"
        text_content_y = "H-1800"
        icon_live_x = "20"
        icon_live_y = "40"
        icon_highlight_x = "10"
        icon_highlight_y = "H-1645"
    else:
        gamer_y = "H-h-40"
        main_y = "80"
        text_gamer_x = "15"
        text_gamer_y = "H-h-15"
        text_content_y = "20"
        icon_live_x = "10"
        icon_live_y = "H-h-30"
        icon_highlight_x = "10"
        icon_highlight_y = "35"
    
    text_gamer_escaped = TEXT_GAMER_SIDE.replace(':', r'\:').replace("'", r"\'")
    text_content_escaped = TEXT_ABOVE_CONTENT.replace(':', r'\:').replace("'", r"\'")
    watermark_escaped = WATERMARK_TEXT.replace(':', r'\:').replace("'", r"\'")
    
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=40:1[bg];"
        
        # Main content dengan rounded corners premium + WARNA DARI PRESET
        "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        "scale=1080:1500:force_original_aspect_ratio=decrease,"
        # Rounded corners untuk main content
        f"format=yuva420p,geq=lum='p(X,Y)':a='if(gt(abs(W/2-X),W/2-{MAIN_BORDER_RADIUS})*gt(abs(H/2-Y),H/2-{MAIN_BORDER_RADIUS}),if(lte(hypot({MAIN_BORDER_RADIUS}-(W/2-abs(W/2-X)),{MAIN_BORDER_RADIUS}-(H/2-abs(H/2-Y))),{MAIN_BORDER_RADIUS}),255,0),255)',"
        f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_MAIN}:t={BORDER_THICKNESS}[main];"
        
        + gamer_filter +
        
        f"[bg][main]overlay=(W-w)/2:{main_y}[tmp];"
        f"[tmp][gamer]overlay=W-w-40:{gamer_y}[tmp2];"
    )
    
    # Watermark
    vf += (
        f"[tmp2]drawtext=text='{watermark_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={WATERMARK_FONT_SIZE}:"
        f"fontcolor={WATERMARK_COLOR}@{WATERMARK_OPACITY}:"
        f"x=(w-text_w)/2:"
        f"y=(h-text_h)/2[tmp2w];"
    )
    
    # Teks dengan efek kedip-kedip
    vf += (
        f"[tmp2w]drawbox=x={text_gamer_x}:y={text_gamer_y}:w=25:h=25:color=red:t=fill:"
        f"enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[tmp2b];"
        
        f"[tmp2b]drawtext=text='{text_gamer_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_GAMER}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x={int(text_gamer_x)+35}:y={text_gamer_y}[tmp3];"
        
        f"[tmp3]drawtext=text='{text_content_escaped}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_CONTENT}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x=10:y={text_content_y}[v]"
    )
    
    inputs = ["-i", video_source]
    
    # Emoji handling
    emoji_input_index = None
    if USE_EMOJI and os.path.exists(EMOJI_PATH):
        inputs.extend(["-i", EMOJI_PATH])
        emoji_input_index = 1
        
        vf = vf.replace("[v]", "[vtmp]")
        vf += f";[{emoji_input_index}:v]scale={EMOJI_SIZE}:{EMOJI_SIZE}[emoji];"
        
        if EMOJI_BLINK:
            vf += f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}:enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[v]"
            print(f"   😎 Emoji enabled: {os.path.basename(EMOJI_PATH)} @ ({EMOJI_X},{EMOJI_Y}) [BLINKING]")
        else:
            vf += f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}[v]"
            print(f"   😎 Emoji enabled: {os.path.basename(EMOJI_PATH)} @ ({EMOJI_X},{EMOJI_Y}) [ALWAYS ON]")
    
    if USE_CUSTOM_ICONS:
        if os.path.exists(ICON_LIVE_PATH):
            inputs.extend(["-i", ICON_LIVE_PATH])
        if os.path.exists(ICON_HIGHLIGHT_PATH):
            inputs.extend(["-i", ICON_HIGHLIGHT_PATH])
    
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
    print(f"   🎨 Border radius: Main={MAIN_BORDER_RADIUS}px, Gamer={GAMER_BORDER_RADIUS}px")
    print(f"   🌈 Border theme: {THEME_NAME}")
    print(f"   🎨 Border colors: Main={BORDER_COLOR_MAIN}, Gamer={BORDER_COLOR_GAMER}")
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


def add_intro_to_video(main_video, output_path, output_dir=None):
    """🎬 Gabungkan video intro dengan video utama"""
    out_dir = output_dir if output_dir else OUTPUT_DIR
    
    if not os.path.exists(INTRO_PATH):
        print(f"\n   ⚠️  Intro file not found: {INTRO_PATH}")
        print(f"   📋 Copying main video without intro...")
        import shutil
        shutil.copy(main_video, output_path)
        return True
    
    print(f"\n🎬 Adding intro to video...")
    print(f"   📹 Intro: {os.path.basename(INTRO_PATH)}")
    print(f"   📹 Main video: {os.path.basename(main_video)}")
    
    list_file = os.path.join(out_dir, "intro_concat.txt")
    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(INTRO_PATH)}'\n")
        f.write(f"file '{os.path.abspath(main_video)}'\n")
    
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
    
    print("   🔗 Concatenating intro + main video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        os.remove(list_file)
    except:
        pass
    
    if result.returncode == 0:
        print(f"   ✅ Video with intro saved!")
        return True
    else:
        print(f"   ❌ Failed to add intro!")
        print(result.stderr[-500:])
        return False


def merge_videos_simple(scene_files, output_path, output_dir=None):
    """Gabungkan semua scene tanpa transisi"""
    out_dir = output_dir if output_dir else OUTPUT_DIR
    
    print(f"\n🔗 Merging {len(scene_files)} scenes (simple concat)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        
        if USE_INTRO:
            temp_output = os.path.join(out_dir, "temp_no_intro.mp4")
            os.rename(output_path, temp_output)
            add_intro_to_video(temp_output, output_path, out_dir)
            try:
                os.remove(temp_output)
            except:
                pass
        
        return True
    
    list_file = os.path.join(out_dir, "filelist.txt")
    with open(list_file, "w") as f:
        for scene_file in scene_files:
            f.write(f"file '{os.path.abspath(scene_file)}'\n")
    
    final_output = output_path
    if USE_INTRO:
        final_output = os.path.join(out_dir, "temp_no_intro.mp4")
    
    cmd = [
        FFMPEG,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        "-movflags", "+faststart",
        final_output
    ]
    
    print("   🎞️  Concatenating videos...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        os.remove(list_file)
    except:
        pass
    
    if result.returncode == 0:
        print(f"   ✅ Merged video saved!")
        
        if USE_INTRO:
            add_intro_to_video(final_output, output_path, out_dir)
            try:
                os.remove(final_output)
            except:
                pass
        
        return True
    else:
        print(f"   ❌ Merge failed!")
        print(result.stderr[-500:])
        return False


def merge_videos_with_transition_stepwise(scene_files, output_path, transition_type, output_dir=None):
    """METODE BERTAHAP - Merge 2 video at a time"""
    out_dir = output_dir if output_dir else OUTPUT_DIR
    
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (stepwise method)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        
        if USE_INTRO:
            temp_output = os.path.join(out_dir, "temp_no_intro.mp4")
            os.rename(output_path, temp_output)
            add_intro_to_video(temp_output, output_path, out_dir)
            try:
                os.remove(temp_output)
            except:
                pass
        
        return True
    
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
    
    temp_files = []
    current_input = scene_files[0]
    
    for i in range(1, len(scene_files)):
        print(f"\n   🔗 Merging part {i}/{len(scene_files)-1}...")
        
        temp_output = os.path.join(out_dir, f"temp_merge_{i}.mp4")
        temp_files.append(temp_output)
        
        probe_cmd = [FFMPEG, "-i", current_input]
        probe_result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        duration = 10
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
            for temp in temp_files:
                try: os.remove(temp)
                except: pass
            return False
        
        print(f"\n      ✅ Part {i} merged!")
        current_input = temp_output
    
    final_output = output_path
    if USE_INTRO:
        final_output = os.path.join(out_dir, "temp_no_intro.mp4")
    
    print(f"\n   📦 Finalizing output...")
    import shutil
    shutil.move(current_input, final_output)
    
    print(f"   🗑️  Cleaning up temporary merge files...")
    for temp in temp_files[:-1]:
        try:
            os.remove(temp)
            print(f"      Deleted: {os.path.basename(temp)}")
        except:
            pass
    
    if USE_INTRO:
        add_intro_to_video(final_output, output_path, out_dir)
        try:
            os.remove(final_output)
        except:
            pass
    
    print(f"\n   ✅ Merged video saved!")
    return True


def merge_videos_with_transition_batch(scene_files, output_path, transition_type):
    """METODE BATCH - Process semua sekaligus"""
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (batch method)...")
    
    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        
        if USE_INTRO:
            temp_output = os.path.join(OUTPUT_DIR, "temp_no_intro.mp4")
            os.rename(output_path, temp_output)
            add_intro_to_video(temp_output, output_path, OUTPUT_DIR)
            try:
                os.remove(temp_output)
            except:
                pass
        
        return True
    
    inputs = []
    for scene_file in scene_files:
        inputs.extend(["-i", scene_file])
    
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
    
    filter_parts = []
    
    if len(scene_files) == 2:
        offset = durations[0] - TRANSITION_DURATION
        filter_parts.append(f"[0:v][1:v]xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}[vout]")
    else:
        offset = durations[0] - TRANSITION_DURATION
        
        filter_parts.append(f"[0:v][1:v]xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}[vt1]")
        
        for i in range(2, len(scene_files)):
            offset += durations[i-1] - TRANSITION_DURATION
            prev_label = f"[vt{i-1}]"
            curr_input = f"[{i}:v]"
            
            if i == len(scene_files) - 1:
                curr_label = "[vout]"
            else:
                curr_label = f"[vt{i}]"
            
            filter_parts.append(f"{prev_label}{curr_input}xfade=transition={effect}:duration={TRANSITION_DURATION}:offset={offset}{curr_label}")
    
    audio_inputs = "".join([f"[{i}:a]" for i in range(len(scene_files))])
    filter_parts.append(f"{audio_inputs}concat=n={len(scene_files)}:v=0:a=1[aout]")
    
    filter_complex = ";".join(filter_parts)
    
    print(f"\n   🔍 Filter chain:")
    for fp in filter_parts:
        print(f"      {fp}")
    
    final_output = output_path
    if USE_INTRO:
        final_output = os.path.join(OUTPUT_DIR, "temp_no_intro.mp4")
    
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
        final_output
    ]
    
    print(f"\n   🎞️  Processing transition...")
    
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
        
        if USE_INTRO:
            add_intro_to_video(final_output, output_path, OUTPUT_DIR)
            try:
                os.remove(final_output)
            except:
                pass
        
        return True
    else:
        print(f"\n   ❌ Merge failed!")
        print("\n📋 Error details:")
        print(stderr_output[-1000:])
        return False