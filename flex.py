import yt_dlp
import sys

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        print(f"\r⬇ {percent} | ⚡ {speed} | ⏳ ETA {eta}", end='')
    elif d['status'] == 'finished':
        print("\n✅ Download selesai, sedang merge...")

url = input("Masukkan link YouTube: ").strip()

# =============================
# 🔍 CEK INFO VIDEO
# =============================
print("\n🔍 Menganalisis video...")

# ✅ Dari cookie file: VISITOR_INFO1_LIVE = 33qYMKx9stQ
VISITOR_DATA = "33qYMKx9stQ"

ydl_check = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'visitor_data': VISITOR_DATA,  # ← Cookie dari YouTube
        }
    },
    'cookiefile': 'www.youtube.com_cookies.txt',
}

try:
    with yt_dlp.YoutubeDL(ydl_check) as ydl:
        info = ydl.extract_info(url, download=False)

        print(f"🎬 Judul: {info.get('title', 'Unknown')}")
        
        duration = info.get('duration', 0)
        if duration:
            print(f"⏱ Durasi: {duration // 60} menit {duration % 60} detik")
        
        is_live = info.get('is_live', False)
        was_live = info.get('was_live', False)
        
        if is_live:
            print("🔴 Status: LIVE (sedang berlangsung)")
        elif was_live:
            print("⏺ Status: VOD (replay)")
        
        # Check available formats
        formats = info.get('formats', [])
        
        video_formats = [
            f for f in formats
            if f.get('vcodec') != 'none'
            and f.get('height')
            and 'storyboard' not in f.get('format_id', '').lower()
        ]
        
        audio_formats = [
            f for f in formats
            if f.get('acodec') != 'none'
            and f.get('vcodec') == 'none'
        ]
        
        if video_formats:
            heights = sorted(set(f.get('height', 0) for f in video_formats), reverse=True)
            max_height = heights[0] if heights else 0
            
            print(f"📺 Kualitas tersedia: {', '.join(str(h) + 'p' for h in heights)}")
            
            max_height_formats = [f for f in video_formats if f.get('height') == max_height]
            max_fps = max(f.get('fps', 30) for f in max_height_formats)
            
            print(f"✅ Akan download: {max_height}p @ {max_fps}fps")
        else:
            print("❌ Tidak ada format video yang tersedia!")
            sys.exit(1)
        
        if audio_formats:
            max_abr = max(f.get('abr', 0) for f in audio_formats if f.get('abr'))
            print(f"🔊 Audio: {int(max_abr)}kbps")

except Exception as e:
    print(f"⚠ Error saat analisis: {e}")
    sys.exit(1)

# =============================
# ⏬ DOWNLOAD
# =============================
ydl_opts = {
    # Try best quality dengan fallback
    'format': 'bv*+ba/b',
    
    'outtmpl': 'D:/CLIP/hasil/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    'ffmpeg_location': r'C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin',
    'noplaylist': True,
    'progress_hooks': [progress_hook],
    
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'visitor_data': VISITOR_DATA,
        }
    },
    
    'cookiefile': 'www.youtube.com_cookies.txt',
    
    'retries': 15,
    'fragment_retries': 15,
    'concurrent_fragment_downloads': 3,
    
    # Sleep to avoid rate limiting
    'sleep_interval': 1,
    'max_sleep_interval': 3,
}

print("\n⏬ Mulai download...")
print("=" * 50)

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print("\n" + "=" * 50)
    print("✅ SELESAI! File ada di D:/CLIP/hasil/")
    
except Exception as e:
    print(f"\n❌ Download gagal: {e}")
    print("\n💡 Jika error 403:")
    print("   1. Coba download_360p.py (selalu work)")
    print("   2. Update cookie file (export lagi dari browser)")
    print("   3. Tunggu beberapa menit lalu coba lagi")