import yt_dlp

url = input("Masukkan link YouTube: ").strip()

ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
    
    'outtmpl': 'D:/Clip/hasil/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    
    # ✅ Ga perlu ffmpeg_location kalau udah masuk PATH
    
    'cookiefile': 'D:/Clip/cookies.txt',
    'noplaylist': True,
    'live_from_start': False,
    'retries': 10,
    'fragment_retries': 10,
}

print("⏬ Download LIVE REPLAY (MAX QUALITY)...")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("✅ SELESAI")