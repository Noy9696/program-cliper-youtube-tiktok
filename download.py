import yt_dlp

url = input("Masukkan link YouTube: ").strip()

ydl_opts = {
    'format': '299+251/303+251/bestvideo[height<=1080]+bestaudio/best',
    'outtmpl': 'D:/Clip/hasil/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',  # ✅ Ini sudah cukup buat merge
    
    'cookiefile': 'D:/Clip/cookies.txt',
    'noplaylist': True,
    'retries': 10,
    'fragment_retries': 10,
}

print("⏬ Download LIVE REPLAY (1080p + AUDIO)...")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("\n✅ SELESAI dengan AUDIO! Cek D:/Clip/hasil/")
except Exception as e:
    print(f"\n❌ ERROR: {e}")