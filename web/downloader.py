import yt_dlp
import os

DOWNLOAD_DIR = "static/videos"
progress_data = {
    "percent": "0%",
    "speed": "-",
    "eta": "-"
}

def progress_hook(d):
    global progress_data
    if d['status'] == 'downloading':
        progress_data["percent"] = d.get('_percent_str', '').strip()
        progress_data["speed"] = d.get('_speed_str', '').strip()
        progress_data["eta"] = d.get('_eta_str', '').strip()
    elif d['status'] == 'finished':
        progress_data["percent"] = "100%"
        progress_data["speed"] = "Done"
        progress_data["eta"] = "0s"

def analyze_video(url):
    ydl_check = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_check) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'merge_output_format': 'mkv',  # biarin default mkv
        'ffmpeg_location': r'C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin',
        'noplaylist': True,
        'progress_hooks': [progress_hook],

        # 🔥 cuma nambah ini
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4'
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
