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

START = to_sec("02:00")
DURATION = 60

if not os.path.exists(SOURCE):
    raise FileNotFoundError("Video sumber tidak ditemukan")

vf = (
    # === BACKGROUND BLUR (FULL 9:16) ===
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,boxblur=40:1[bg];"

    # === GAMEPLAY (ZOOM OUT, CENTER, NO STRETCH) ===
    "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,"
    "pad=1080:608:(ow-iw)/2:(oh-ih)/2[game];"

    # === FACECAM (KANAN BAWAH) ===
    "[0:v]crop=iw*0.3:ih*0.3:iw*0.65:ih*0.65,"
    "scale=420:420[face];"

    # === COMPOSE ===
    "[bg][game]overlay=0:(1920-608)/2[tmp];"
    "[tmp][face]overlay=640:1420[v]"
)



cmd = [
    FFMPEG,
    "-y",

    # ⚠️ SEEK WAJIB SEBELUM INPUT
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

    # ⬇️ WAJIB UNTUK PROGRESS
    "-progress", "pipe:1",
    "-nostats",

    OUTPUT
]

print("🚀 Encoding started...\n")

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
