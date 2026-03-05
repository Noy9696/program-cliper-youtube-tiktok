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
FFMPEG     = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
SOURCE     = r"D:\CLIP\hasil\Mentah.mp4"
OUTPUT_DIR = r"D:\CLIP\hasil\dasar"

TRANSITION_DURATION = 0.8
BLINK_SPEED         = 0.5
GAMER_WIDTH         = 0.16
GAMER_HEIGHT        = 0.28
GAMER_X_POS         = 0.80
GAMER_Y_POS         = 0.70

# ========================================
# 🎨 BORDER RADIUS CONFIGURATION
# ========================================
MAIN_BORDER_RADIUS  = 30
GAMER_BORDER_RADIUS = 25
BORDER_THICKNESS    = 5

# ========================================
# 🌈 COLOR PRESET LIBRARY
# ========================================
COLOR_PRESETS = {
    1:  {'name': 'ROYAL GOLD',        'desc': '👑 Gold premium',           'main': '#D4AF37', 'gamer': '#B8962E'},
    2:  {'name': 'DEEP CRIMSON',      'desc': '🩸 Merah gelap cinematic',  'main': '#8B0000', 'gamer': '#6A0000'},
    3:  {'name': 'ROYAL PURPLE',      'desc': '🔮 Ungu mysterious',        'main': '#6A0DAD', 'gamer': '#4B0082'},
    4:  {'name': 'EMERALD ELEGANT',   'desc': '💚 Hijau emerald premium',  'main': '#046307', 'gamer': '#034A05'},
    5:  {'name': 'NEON CYAN PREMIUM', 'desc': '💎 Cyan modern glow',       'main': '#00C2D1', 'gamer': '#0097A7'},
    6:  {'name': 'ROYAL BLUE',        'desc': '🔷 Biru royal clean',       'main': '#0B3D91', 'gamer': '#072A66'},
    7:  {'name': 'MAGENTA ROYAL',     'desc': '🌌 Magenta luxury',         'main': '#8B008B', 'gamer': '#5A005A'},
    8:  {'name': 'AMBER GOLD',        'desc': '🔥 Gold amber warm',        'main': '#FF8F00', 'gamer': '#C67100'},
    9:  {'name': 'BLOOD RED NEON',    'desc': '🧛 Horror premium',         'main': '#B11226', 'gamer': '#7A0C1A'},
    10: {'name': 'PLATINUM PURPLE',   'desc': '💠 Luxury ultra',           'main': '#A020F0', 'gamer': '#6A0DAD'},
}

# ========================================
# 🎨 BORDER COLOR CONFIGURATION
# ========================================
USE_RANDOM_COLOR      = True
SELECTED_COLOR_PRESET = 5

def get_border_colors():
    if USE_RANDOM_COLOR:
        preset_num = random.randint(1, 10)
        print(f"\n🎲 RANDOM COLOR: #{preset_num} - {COLOR_PRESETS[preset_num]['name']}")
    else:
        preset_num = SELECTED_COLOR_PRESET
        if preset_num not in COLOR_PRESETS:
            print(f"\n⚠️  Preset #{preset_num} tidak ada, pakai #1")
            preset_num = 1
        print(f"\n🎨 SELECTED COLOR: #{preset_num} - {COLOR_PRESETS[preset_num]['name']}")
    p = COLOR_PRESETS[preset_num]
    print(f"   {p['desc']}")
    return p['main'], p['gamer'], p['name']

BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME = get_border_colors()

# ========================================
# 💧 WATERMARK CONFIGURATION
# ========================================
WATERMARK_TEXT      = "inibilal999"
WATERMARK_FONT_SIZE = 80
WATERMARK_COLOR     = "white"
WATERMARK_OPACITY   = "0.15"

# ========================================
# ✍️ TEXT CONFIGURATION
# ========================================
TEXT_GAMER_SIDE        = "LIVE WINDAH BASUDARA"
TEXT_ABOVE_CONTENT     = "Streamer Betingkah wkwk"
TEXT_FONT_SIZE_GAMER   = 35
TEXT_FONT_SIZE_CONTENT = 45
TEXT_COLOR             = "white"
TEXT_OUTLINE_COLOR     = "White"
TEXT_OUTLINE_WIDTH     = 1

# ========================================
# 🎨 ICON CONFIGURATION
# ========================================
USE_CUSTOM_ICONS    = False
ICON_LIVE_PATH      = r"D:\CLIP\icons\red_dot.png"
ICON_HIGHLIGHT_PATH = r"D:\CLIP\icons\laugh.png"
ICON_SIZE_LIVE      = 35
ICON_SIZE_HIGHLIGHT = 45

# ========================================
# 😅 EMOJI CONFIGURATION
# ========================================
USE_EMOJI   = False
EMOJI_BLINK = False
EMOJI_PATH  = r"D:\CLIP\web\moi.png"
EMOJI_SIZE  = 85
EMOJI_X     = "475"
EMOJI_Y     = "100"

# ========================================
# 🎬 INTRO VIDEO CONFIGURATION
# ========================================
USE_INTRO  = True
INTRO_PATH = r"D:\CLIP\hasil\TV.mp4"

# ========================================
# ⚡ GPU / CPU BALANCE CONFIGURATION
# ========================================
#
# Intel HD 5500 (Broadwell Gen 5) TIDAK support Intel QSV MFX session.
# Solusi optimal untuk hardware ini:
#
#   DECODE → D3D11VA  : GPU Intel handle decode H.264 → hemat CPU ~15-25%
#   FILTER → CPU      : geq/drawbox/drawtext belum ada versi GPU-native
#   ENCODE → libx264  : CPU encode, tapi DIBATASI threadnya agar tidak 100%
#
# ----------------------------------------------------------------
# USE_D3D11VA_DECODE:
#   True  = GPU Intel decode video source (hemat CPU saat baca frame)
#   False = CPU full decode (fallback aman jika D3D11VA bermasalah)
# ----------------------------------------------------------------
USE_D3D11VA_DECODE = False  # AV1 source: D3D11VA tidak support AV1 di Intel HD 5500

# ----------------------------------------------------------------
# CPU_ENCODE_THREADS:
#   Jumlah CPU thread untuk libx264 encode.
#   Rekomendasi = setengah logical core.
#   Misal: 4 core / 4 thread → set 2
#          2 core / 4 thread (HT) → set 2
#   Set 0 = auto (ffmpeg pakai semua core → CPU bisa 100%)
# ----------------------------------------------------------------
CPU_ENCODE_THREADS = 2

# ----------------------------------------------------------------
# X264_CRF: kualitas encode
#   18 = hampir lossless (file besar)
#   23 = default (balance)
#   28 = file lebih kecil (kualitas turun)
# ----------------------------------------------------------------
X264_CRF = 18

# ----------------------------------------------------------------
# X264_PRESET: kecepatan encode vs ukuran file
#   ultrafast → superfast → veryfast → faster → fast → medium → slow
#   Makin cepat = CPU lebih ringan, file lebih besar
#   Rekomendasi untuk laptop: "faster" atau "fast"
# ----------------------------------------------------------------
X264_PRESET = "faster"


# ============================================================
# 🔧 INTERNAL HELPERS
# ============================================================

def _decode_flags():
    """
    Decode flags sebelum -i input utama.
    
    Intel HD 5500 support D3D11VA hanya untuk H.264/H.265/VP8/VP9.
    AV1 TIDAK support D3D11VA di GPU ini — harus CPU software decode.
    
    Kalau source H.264 → set USE_D3D11VA_DECODE = True untuk hemat CPU.
    Kalau source AV1   → set USE_D3D11VA_DECODE = False (default aman).
    """
    if USE_D3D11VA_DECODE:
        return ["-hwaccel", "d3d11va"]
    return []


def _encode_flags():
    """
    libx264 encode dengan thread limit agar CPU tidak 100%.
    """
    return [
        "-c:v",     "libx264",
        "-preset",  X264_PRESET,
        "-crf",     str(X264_CRF),
        "-threads", str(CPU_ENCODE_THREADS),
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
    ]


def _probe_duration(filepath):
    """Probe durasi file video, return float seconds."""
    result = subprocess.run(
        [FFMPEG, "-i", filepath],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    for line in result.stderr.split('\n'):
        if 'Duration:' in line:
            try:
                ts = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = ts.split(':')
                return float(h)*3600 + float(m)*60 + float(s)
            except Exception:
                pass
    return 10.0


# ============================================================
# 🎬 PROCESS SCENE
# ============================================================

def process_scene(scene_num, start_time, duration, output_path,
                  blink_config, gamer_position, source_video=None):
    """
    Proses satu scene.
    - Decode : D3D11VA GPU (Intel HD 5500) — opsional
    - Filter : CPU software (geq, drawbox, drawtext)
    - Encode : libx264 CPU dengan thread limit
    """

    global BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME
    if USE_RANDOM_COLOR:
        BORDER_COLOR_MAIN, BORDER_COLOR_GAMER, THEME_NAME = get_border_colors()

    video_source = source_video if source_video else SOURCE

    # Rounded corner helper strings
    rounded_gamer = (
        f"format=yuva420p,"
        f"geq=lum='p(X,Y)':a='if("
        f"gt(abs(W/2-X),W/2-{GAMER_BORDER_RADIUS})*gt(abs(H/2-Y),H/2-{GAMER_BORDER_RADIUS}),"
        f"if(lte(hypot({GAMER_BORDER_RADIUS}-(W/2-abs(W/2-X)),"
        f"{GAMER_BORDER_RADIUS}-(H/2-abs(H/2-Y))),{GAMER_BORDER_RADIUS}),255,0),255)'"
    )
    rounded_main = (
        f"format=yuva420p,"
        f"geq=lum='p(X,Y)':a='if("
        f"gt(abs(W/2-X),W/2-{MAIN_BORDER_RADIUS})*gt(abs(H/2-Y),H/2-{MAIN_BORDER_RADIUS}),"
        f"if(lte(hypot({MAIN_BORDER_RADIUS}-(W/2-abs(W/2-X)),"
        f"{MAIN_BORDER_RADIUS}-(H/2-abs(H/2-Y))),{MAIN_BORDER_RADIUS}),255,0),255)'"
    )

    # Gamer box filter
    if blink_config['enabled']:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            f"scale=450:500,{rounded_gamer},"
            f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_GAMER}:t={BORDER_THICKNESS},"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=red:t=8:"
            f"enable='between(t,{blink_config['start']},{blink_config['end']})"
            f"*gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[gamer];"
        )
    else:
        gamer_filter = (
            f"[0:v]crop=iw*{GAMER_WIDTH}:ih*{GAMER_HEIGHT}:iw*{GAMER_X_POS}:ih*{GAMER_Y_POS},"
            f"scale=450:500,{rounded_gamer},"
            f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_GAMER}:t={BORDER_THICKNESS}[gamer];"
        )

    # Posisi gamer
    if gamer_position == 'atas':
        gamer_y        = "40"
        main_y         = "H-h-80"
        text_gamer_x   = "15"
        text_gamer_y   = "40"
        text_content_y = "H-1800"
    else:
        gamer_y        = "H-h-40"
        main_y         = "80"
        text_gamer_x   = "15"
        text_gamer_y   = "H-h-15"
        text_content_y = "20"

    text_gamer_esc   = TEXT_GAMER_SIDE.replace(':', r'\:').replace("'", r"\'")
    text_content_esc = TEXT_ABOVE_CONTENT.replace(':', r'\:').replace("'", r"\'")
    watermark_esc    = WATERMARK_TEXT.replace(':', r'\:').replace("'", r"\'")

    vf = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,boxblur=40:1[bg];"

        f"[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        f"scale=1080:1500:force_original_aspect_ratio=decrease,"
        f"{rounded_main},"
        f"drawbox=x=0:y=0:w=iw:h=ih:color={BORDER_COLOR_MAIN}:t={BORDER_THICKNESS}[main];"

        + gamer_filter +

        f"[bg][main]overlay=(W-w)/2:{main_y}[tmp];"
        f"[tmp][gamer]overlay=W-w-40:{gamer_y}[tmp2];"

        f"[tmp2]drawtext=text='{watermark_esc}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={WATERMARK_FONT_SIZE}:"
        f"fontcolor={WATERMARK_COLOR}@{WATERMARK_OPACITY}:"
        f"x=(w-text_w)/2:y=(h-text_h)/2[tmp2w];"

        f"[tmp2w]drawbox=x={text_gamer_x}:y={text_gamer_y}:w=25:h=25:color=red:t=fill:"
        f"enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[tmp2b];"

        f"[tmp2b]drawtext=text='{text_gamer_esc}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_GAMER}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x={int(text_gamer_x)+35}:y={text_gamer_y}[tmp3];"

        f"[tmp3]drawtext=text='{text_content_esc}':"
        f"fontfile=/Windows/Fonts/impact.ttf:"
        f"fontsize={TEXT_FONT_SIZE_CONTENT}:"
        f"fontcolor={TEXT_COLOR}:"
        f"borderw={TEXT_OUTLINE_WIDTH}:"
        f"bordercolor={TEXT_OUTLINE_COLOR}:"
        f"x=10:y={text_content_y}[v]"
    )

    # Emoji opsional
    inputs = _decode_flags() + ["-i", video_source]

    if USE_EMOJI and os.path.exists(EMOJI_PATH):
        inputs.extend(["-i", EMOJI_PATH])
        vf = vf.replace("[v]", "[vtmp]")
        vf += f";[1:v]scale={EMOJI_SIZE}:{EMOJI_SIZE}[emoji];"
        if EMOJI_BLINK:
            vf += (f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}:"
                   f"enable='gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[v]")
            print(f"   😎 Emoji: {os.path.basename(EMOJI_PATH)} [BLINKING]")
        else:
            vf += f"[vtmp][emoji]overlay={EMOJI_X}:{EMOJI_Y}[v]"
            print(f"   😎 Emoji: {os.path.basename(EMOJI_PATH)} [ALWAYS ON]")

    if USE_CUSTOM_ICONS:
        if os.path.exists(ICON_LIVE_PATH):
            inputs.extend(["-i", ICON_LIVE_PATH])
        if os.path.exists(ICON_HIGHLIGHT_PATH):
            inputs.extend(["-i", ICON_HIGHLIGHT_PATH])

    cmd = (
        [FFMPEG, "-y", "-ss", str(start_time)]
        + inputs
        + ["-t", str(duration),
           "-filter_complex", vf,
           "-map", "[v]",
           "-map", "0:a:0?",
           ]
        + _encode_flags()
        + ["-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart",
           "-progress", "pipe:1",
           output_path,
           ]
    )

    print(f"\n🎬 Processing Scene {scene_num}...")
    print(f"   Start: {sec_to_time(start_time)} | Duration: {duration}s")
    print(f"   🎮 Gamer position  : Pojok kanan {gamer_position}")
    print(f"   🎨 Border radius   : Main={MAIN_BORDER_RADIUS}px, Gamer={GAMER_BORDER_RADIUS}px")
    print(f"   🌈 Border theme    : {THEME_NAME}")
    print(f"   🎨 Border colors   : Main={BORDER_COLOR_MAIN}, Gamer={BORDER_COLOR_GAMER}")
    print(f"   💧 Watermark       : '{WATERMARK_TEXT}' (opacity {WATERMARK_OPACITY})")
    print(f"   ✍️  Text gamer      : '{TEXT_GAMER_SIDE}'")
    print(f"   ✍️  Text content    : '{TEXT_ABOVE_CONTENT}'")
    print(f"   ⚡ Decode          : {'D3D11VA GPU (Intel HD 5500)' if USE_D3D11VA_DECODE else 'CPU software'}")
    print(f"   ⚡ Encode          : libx264 | crf={X264_CRF} | preset={X264_PRESET} | threads={CPU_ENCODE_THREADS}")
    if blink_config['enabled']:
        print(f"   🔴 Border merah   : detik {blink_config['start']}-{blink_config['end']}")
    else:
        print(f"   ⚫ Tanpa border merah")

    def _run_cmd(run_cmd):
        import threading as _th
        proc = subprocess.Popen(
            run_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        # FIX DEADLOCK: baca stderr di thread terpisah.
        # FFmpeg nulis log besar ke stderr -> pipe buffer OS (~64KB) penuh ->
        # FFmpeg nunggu buffer kosong -> kita nunggu FFmpeg selesai -> freeze.
        stderr_lines = []
        def _drain():
            try:
                for ln in proc.stderr:
                    stderr_lines.append(ln)
                    s = ln.strip()
                    if any(k in s for k in ("Error","error","Invalid","Failed","failed","No such")):
                        try:
                            sys.stderr.write(f"\n   [ffmpeg] {s}\n")
                            sys.stderr.flush()
                        except Exception:
                            pass  # Abaikan error I/O saat shutdown
            except Exception:
                pass  # Pipe sudah ditutup, abaikan
        t = _th.Thread(target=_drain, daemon=True)
        t.start()

        for line in proc.stdout:
            line = line.strip()
            if not line.startswith("out_time_ms="):
                continue
            value = line.split("=")[1]
            if value == "N/A":
                continue
            ms  = int(value)
            pct = min(ms / (duration * 1_000_000) * 100, 100)
            sys.stdout.write(f"\r   ⏳ Progress: {pct:6.2f}% | {ms/1_000_000:5.1f}s / {duration}s")
            sys.stdout.flush()
        proc.wait()
        t.join(timeout=5)
        return proc.returncode, "".join(stderr_lines)

    returncode, stderr_output = _run_cmd(cmd)

    if returncode != 0:
        print("\n❌ ENCODING FAILED!")
        print("\n📋 FFmpeg Error:")
        print(stderr_output[-1500:])

        # Auto-fallback: retry tanpa D3D11VA jika hwaccel yang bermasalah
        if USE_D3D11VA_DECODE and "-hwaccel" in cmd:
            print("\n🔄 Auto-fallback: Retry dengan CPU decode (D3D11VA dinonaktifkan)...")
            cmd_fallback = []
            skip_next = False
            for token in cmd:
                if skip_next:
                    skip_next = False
                    continue
                if token == "-hwaccel":
                    skip_next = True   # buang juga nilai "d3d11va" setelahnya
                    continue
                cmd_fallback.append(token)

            returncode2, stderr2 = _run_cmd(cmd_fallback)
            if returncode2 == 0:
                print(f"\n   ✅ Scene {scene_num} done! (via CPU fallback)")
                print(f"   💡 Tip: Set USE_D3D11VA_DECODE = False agar tidak retry tiap scene")
                return True
            else:
                print("\n❌ CPU FALLBACK JUGA GAGAL!")
                print(stderr2[-800:])
                return False

        return False

    print(f"\n   ✅ Scene {scene_num} done!")
    return True


# ============================================================
# 🎬 INTRO
# ============================================================

def add_intro_to_video(main_video, output_path, output_dir=None):
    """Gabungkan video intro dengan video utama (stream copy)."""
    out_dir = output_dir if output_dir else OUTPUT_DIR

    if not os.path.exists(INTRO_PATH):
        print(f"\n   ⚠️  Intro file not found: {INTRO_PATH}")
        import shutil
        shutil.copy(main_video, output_path)
        return True

    print(f"\n🎬 Adding intro to video...")
    print(f"   📹 Intro: {os.path.basename(INTRO_PATH)}")
    print(f"   📹 Main : {os.path.basename(main_video)}")

    list_file = os.path.join(out_dir, "intro_concat.txt")
    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(INTRO_PATH)}'\n")
        f.write(f"file '{os.path.abspath(main_video)}'\n")

    cmd    = [FFMPEG, "-y", "-f", "concat", "-safe", "0",
              "-i", list_file, "-c", "copy", "-movflags", "+faststart", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try: os.remove(list_file)
    except Exception: pass

    if result.returncode == 0:
        print("   ✅ Video with intro saved!")
        return True
    else:
        print(f"   ❌ Failed to add intro!\n{result.stderr[-500:]}")
        return False


# ============================================================
# 🔗 MERGE — Simple concat (stream copy)
# ============================================================

def merge_videos_simple(scene_files, output_path, output_dir=None):
    """Gabungkan semua scene tanpa transisi (stream copy — sangat ringan)."""
    out_dir = output_dir if output_dir else OUTPUT_DIR
    print(f"\n🔗 Merging {len(scene_files)} scenes (simple concat / stream copy)...")

    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        if USE_INTRO:
            tmp = os.path.join(out_dir, "temp_no_intro.mp4")
            os.rename(output_path, tmp)
            add_intro_to_video(tmp, output_path, out_dir)
            try: os.remove(tmp)
            except Exception: pass
        return True

    list_file = os.path.join(out_dir, "filelist.txt")
    with open(list_file, "w") as f:
        for sf in scene_files:
            f.write(f"file '{os.path.abspath(sf)}'\n")

    final_out = os.path.join(out_dir, "temp_no_intro.mp4") if USE_INTRO else output_path
    cmd       = [FFMPEG, "-y", "-f", "concat", "-safe", "0",
                 "-i", list_file, "-c", "copy", "-movflags", "+faststart", final_out]
    result    = subprocess.run(cmd, capture_output=True, text=True)

    try: os.remove(list_file)
    except Exception: pass

    if result.returncode == 0:
        print("   ✅ Merged!")
        if USE_INTRO:
            add_intro_to_video(final_out, output_path, out_dir)
            try: os.remove(final_out)
            except Exception: pass
        return True
    else:
        print(f"   ❌ Merge failed!\n{result.stderr[-500:]}")
        return False


# ============================================================
# 🔗 MERGE — Stepwise dengan transisi (re-encode, thread-limited)
# ============================================================

def merge_videos_with_transition_stepwise(scene_files, output_path,
                                          transition_type, output_dir=None):
    """METODE BERTAHAP — Merge 2 video sekaligus, encode via libx264 thread-limited."""
    out_dir = output_dir if output_dir else OUTPUT_DIR
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (stepwise)...")
    print(f"   ⚡ Encode: libx264 | crf={X264_CRF} | preset={X264_PRESET} | threads={CPU_ENCODE_THREADS}")

    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        if USE_INTRO:
            tmp = os.path.join(out_dir, "temp_no_intro.mp4")
            os.rename(output_path, tmp)
            add_intro_to_video(tmp, output_path, out_dir)
            try: os.remove(tmp)
            except Exception: pass
        return True

    transitions = {
        '1': 'fade', '2': 'fadeblack', '3': 'wipeleft',
        '4': 'wiperight', '5': 'slidedown', '6': 'slideup',
    }
    effect = transitions.get(transition_type, 'fade')
    print(f"   🎨 Effect: {effect} | ⏱️ Duration: {TRANSITION_DURATION}s")

    temp_files    = []
    current_input = scene_files[0]

    for i in range(1, len(scene_files)):
        print(f"\n   🔗 Merging part {i}/{len(scene_files)-1}...")
        temp_output = os.path.join(out_dir, f"temp_merge_{i}.mp4")
        temp_files.append(temp_output)

        duration = _probe_duration(current_input)
        offset   = max(0.0, duration - TRANSITION_DURATION)
        print(f"      📊 Input duration: {duration:.1f}s | Offset: {offset:.1f}s")

        cmd = (
            [FFMPEG, "-y",
             "-i", current_input,
             "-i", scene_files[i],
             "-filter_complex",
             (f"[0:v][1:v]xfade=transition={effect}:"
              f"duration={TRANSITION_DURATION}:offset={offset}[vout];"
              f"[0:a][1:a]acrossfade=d={TRANSITION_DURATION}[aout]"),
             "-map", "[vout]",
             "-map", "[aout]",
             ]
            + _encode_flags()
            + ["-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart",
               "-progress", "pipe:1", "-nostats",
               temp_output,
               ]
        )

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                v = line.split("=")[1]
                if v != "N/A":
                    sys.stdout.write(f"\r      ⏳ {int(v)/1_000_000:5.1f}s")
                    sys.stdout.flush()

        stderr_output = process.stderr.read()
        process.wait()

        if process.returncode != 0:
            print(f"\n      ❌ Failed at merge {i}\n{stderr_output[-800:]}")
            for tmp in temp_files:
                try: os.remove(tmp)
                except Exception: pass
            return False

        print(f"\n      ✅ Part {i} merged!")
        current_input = temp_output

    final_out = os.path.join(out_dir, "temp_no_intro.mp4") if USE_INTRO else output_path
    import shutil
    shutil.move(current_input, final_out)

    for tmp in temp_files[:-1]:
        try: os.remove(tmp)
        except Exception: pass

    if USE_INTRO:
        add_intro_to_video(final_out, output_path, out_dir)
        try: os.remove(final_out)
        except Exception: pass

    print("\n   ✅ Merged video saved!")
    return True


# ============================================================
# 🔗 MERGE — Batch dengan transisi (re-encode, thread-limited)
# ============================================================

def merge_videos_with_transition_batch(scene_files, output_path, transition_type):
    """METODE BATCH — Process semua sekaligus, encode via libx264 thread-limited."""
    print(f"\n🔗 Merging {len(scene_files)} scenes with transition (batch)...")
    print(f"   ⚡ Encode: libx264 | crf={X264_CRF} | preset={X264_PRESET} | threads={CPU_ENCODE_THREADS}")

    if len(scene_files) == 1:
        import shutil
        shutil.copy(scene_files[0], output_path)
        if USE_INTRO:
            tmp = os.path.join(OUTPUT_DIR, "temp_no_intro.mp4")
            os.rename(output_path, tmp)
            add_intro_to_video(tmp, output_path, OUTPUT_DIR)
            try: os.remove(tmp)
            except Exception: pass
        return True

    inputs = []
    for sf in scene_files:
        inputs.extend(["-i", sf])

    transitions = {
        '1': 'fade', '2': 'fadeblack', '3': 'wipeleft',
        '4': 'wiperight', '5': 'slidedown', '6': 'slideup',
    }
    effect = transitions.get(transition_type, 'fade')
    print(f"   🎨 Effect: {effect} | ⏱️ Duration: {TRANSITION_DURATION}s")

    durations = []
    for sf in scene_files:
        dur = _probe_duration(sf)
        durations.append(dur)
        print(f"   📹 Scene {len(durations)}: {dur:.2f}s")

    # Build xfade filter chain
    filter_parts = []
    if len(scene_files) == 2:
        offset = durations[0] - TRANSITION_DURATION
        filter_parts.append(
            f"[0:v][1:v]xfade=transition={effect}:"
            f"duration={TRANSITION_DURATION}:offset={offset}[vout]"
        )
    else:
        offset = durations[0] - TRANSITION_DURATION
        filter_parts.append(
            f"[0:v][1:v]xfade=transition={effect}:"
            f"duration={TRANSITION_DURATION}:offset={offset}[vt1]"
        )
        for i in range(2, len(scene_files)):
            offset   += durations[i-1] - TRANSITION_DURATION
            prev      = f"[vt{i-1}]"
            curr_in   = f"[{i}:v]"
            curr_out  = "[vout]" if i == len(scene_files)-1 else f"[vt{i}]"
            filter_parts.append(
                f"{prev}{curr_in}xfade=transition={effect}:"
                f"duration={TRANSITION_DURATION}:offset={offset}{curr_out}"
            )

    audio_in = "".join([f"[{i}:a]" for i in range(len(scene_files))])
    filter_parts.append(f"{audio_in}concat=n={len(scene_files)}:v=0:a=1[aout]")
    filter_complex = ";".join(filter_parts)

    final_out = os.path.join(OUTPUT_DIR, "temp_no_intro.mp4") if USE_INTRO else output_path

    cmd = (
        [FFMPEG, "-y"]
        + inputs
        + ["-filter_complex", filter_complex,
           "-map", "[vout]",
           "-map", "[aout]",
           ]
        + _encode_flags()
        + ["-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart",
           "-progress", "pipe:1", "-nostats",
           final_out,
           ]
    )

    print("\n   🎞️  Processing transition...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)

    total_dur = sum(durations) - (len(durations)-1) * TRANSITION_DURATION
    for line in process.stdout:
        line = line.strip()
        if line.startswith("out_time_ms="):
            v = line.split("=")[1]
            if v != "N/A":
                sec = int(v) / 1_000_000
                pct = min((sec / total_dur) * 100, 100)
                sys.stdout.write(f"\r   ⏳ Progress: {pct:5.1f}% | {sec:5.1f}s / {total_dur:.1f}s")
                sys.stdout.flush()

    stderr_output = process.stderr.read()
    process.wait()

    if process.returncode == 0:
        print("\n   ✅ Merged video saved!")
        if USE_INTRO:
            add_intro_to_video(final_out, output_path, OUTPUT_DIR)
            try: os.remove(final_out)
            except Exception: pass
        return True
    else:
        print(f"\n   ❌ Merge failed!\n{stderr_output[-1200:]}")
        return False