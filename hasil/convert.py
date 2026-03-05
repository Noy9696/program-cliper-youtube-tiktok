import subprocess
import os
from pathlib import Path

# ✅ Folder input & output
INPUT_FOLDER = r'D:\Clip\hasil'
OUTPUT_FOLDER = r'D:\Clip\hasil'  # bisa ganti folder lain kalau mau pisah

FFMPEG = r'C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe'

def convert_webm_to_mp4(input_path, output_path):
    cmd = [
        FFMPEG,
        '-i', input_path,
        '-c:v', 'copy',   # ✅ tanpa re-encode video (lossless & cepat)
        '-c:a', 'aac',    # ✅ convert audio ke aac (kompatibel mp4)
        '-y',             # overwrite kalau sudah ada
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    folder = Path(INPUT_FOLDER)
    webm_files = list(folder.glob('*.webm'))

    if not webm_files:
        print("❌ Tidak ada file .webm ditemukan di folder.")
        return

    print(f"🔍 Ditemukan {len(webm_files)} file .webm\n")

    success = 0
    failed = 0

    for webm in webm_files:
        output = Path(OUTPUT_FOLDER) / (webm.stem + '.mp4')
        print(f"⏳ Converting: {webm.name}")

        if convert_webm_to_mp4(str(webm), str(output)):
            print(f"   ✅ Selesai → {output.name}")
            success += 1
        else:
            print(f"   ❌ Gagal: {webm.name}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"✅ Berhasil : {success} file")
    print(f"❌ Gagal    : {failed} file")
    print(f"📁 Output   : {OUTPUT_FOLDER}")

if __name__ == '__main__':
    main()