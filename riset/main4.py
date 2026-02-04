import subprocess, sys, os

def to_sec(t):
    parts = list(map(int, t.split(":")))
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    raise ValueError("Format waktu salah")

FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
SOURCE = r"D:\CLIP\hasil\konten.mp4"
OUTPUT = r"D:\CLIP\hasil\final.mp4"

START = to_sec("46:00")
DURATION = 60

# ========================================
# 🔴 PENGATURAN BORDER MERAH BERKEDIP
# ========================================
BLINK_START = 26      # Mulai kedip di detik ke-berapa (relatif dari START)
BLINK_END = 29       # Berhenti kedip di detik ke-berapa
BLINK_SPEED = 0.5    # Kecepatan kedip (0.5 = 2x per detik, 0.2 = 5x per detik, 1 = 1x per detik)
# ========================================

if not os.path.exists(SOURCE):
    raise FileNotFoundError("Video sumber tidak ditemukan")

vf = (
    # === BACKGROUND BLUR (FULL 9:16) ===
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,boxblur=40:1[bg];"

    # === VIDEO UTAMA (CROP TENGAH -> SCALE + BORDER HITAM) ===
    "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
    "scale=1080:1500:force_original_aspect_ratio=decrease,"
    "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6[main];"

    # === CROP GAMER (GESER KE KANAN DIKIT + BORDER HITAM + BORDER MERAH BERKEDIP) ===
    "[0:v]crop=iw*0.25:ih*0.25:iw*0.73:ih*0.70,"
    "scale=450:450,"
    "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=6,"
    f"drawbox=x=0:y=0:w=iw:h=ih:color=red:t=8:enable='between(t,{BLINK_START},{BLINK_END})*gte(mod(t,{BLINK_SPEED}),{BLINK_SPEED/2})'[gamer];"

    # === COMPOSE ===
    # 1. Overlay main video ke background blur (tengah horizontal, lebih ke atas)
    "[bg][main]overlay=(W-w)/2:80[tmp];"
    
    # 2. Overlay gamer ke pojok kanan bawah (di area blur, lebih ke atas)
    "[tmp][gamer]overlay=W-w-40:H-h-80[v]"
)

cmd = [
    FFMPEG,
    "-y",
    "-ss", str(START),
    "-i", SOURCE,
    "-t", str(DURATION),
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
    OUTPUT
]

print("🚀 Encoding started...")
print(f"🔴 Border merah berkedip: detik {BLINK_START}-{BLINK_END} (speed: {BLINK_SPEED}s)\n")

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
    pct = min(ms / (DURATION * 1_000_000) * 100, 100)
    sys.stdout.write(
        f"\r⏳ Progress: {pct:6.2f}% | {ms/1_000_000:5.1f}s / {DURATION}s"
    )
    sys.stdout.flush()

process.wait()
print("\n\n✅ DONE:", OUTPUT)
