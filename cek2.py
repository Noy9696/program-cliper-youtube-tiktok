import yt_dlp

url = input("Masukkan link YouTube: ").strip()

ydl_opts = {
    # ✅ Format disesuaikan dengan format tersedia (avc1 1080p60 + mp4a)
    'format': '(bestvideo[vcodec^=avc1][height<=1080]+bestaudio[acodec^=mp4a])/(bestvideo[height<=1080]+bestaudio)/best',
    
    'outtmpl': 'D:/Clip/hasil/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    
    'cookiefile': 'D:/Clip/cookies.txt',
    'noplaylist': True,
    'retries': 10,
    'fragment_retries': 10,
    
    # ✅ Fix JS challenge solver — setara --remote-components ejs:github
    'remote_components': ['ejs:github'],

    # ✅ Tunjuk lokasi ffmpeg
    'ffmpeg_location': r'C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin',

    # ✅ Postprocessor untuk merge tanpa re-encode (lebih cepat & lossless)
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    
    # ✅ Pastikan dapet kualitas terbaik
    'prefer_free_formats': False,
}

print("⏬ Downloading dengan kualitas optimal...")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # ✅ Tampilkan format yang akan didownload
        print(f"\n📹 Video: {info.get('format_note', 'N/A')}")
        print(f"🎵 Audio: {info.get('abr', 'N/A')} kbps")
        print(f"📦 Size: ~{info.get('filesize_approx', 0) / 1024 / 1024:.1f} MB\n")
        
        ydl.download([url])
    print("\n✅ SELESAI dengan kualitas terbaik!")
except Exception as e:
    print(f"\n❌ ERROR: {e}")