import yt_dlp
import os
import re
DOWNLOAD_DIR = r"D:\CLIP\hasil"

progress = {
    "status": "idle",
    "percent": "0%",
    "speed": "-",
    "eta": "-"
}
ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
def clean_ansi(text):
    if not text:
        return ''
    return ANSI_ESCAPE.sub('', text)

def safe_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name.strip('_')

def progress_hook(d):
    if d['status'] == 'downloading':
        progress["status"] = "downloading"
        progress["percent"] = clean_ansi(d.get('_percent_str', '')).strip()
        progress["speed"] = clean_ansi(d.get('_speed_str', '')).strip()
        progress["eta"] = clean_ansi(d.get('_eta_str', '')).strip()

    elif d['status'] == 'finished':
        progress["status"] = "done"
        progress["percent"] = "100%"
        progress["speed"] = "Done"
        progress["eta"] = "0s"


def download_youtube(url):
    ydl_opts_info = {
        'quiet': True,
        'no_warnings': True
    }

    # Ambil info video dulu
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'youtube_video')

    safe_title = safe_filename(title)
    output_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'ffmpeg_location': r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin",
        'progress_hooks': [progress_hook],
        'noplaylist': True
    }

    progress["status"] = "starting"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_file = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")
    return final_file

