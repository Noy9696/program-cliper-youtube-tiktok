import yt_dlp

url = input("Masukkan link YouTube: ").strip()

ydl_opts = {
    'format': '299+251',
    'outtmpl': 'D:/Clip/hasil/%(title)s.%(ext)s',
    
    # ✅ Ganti merge strategy
    'merge_output_format': 'mp4',
    
    'cookiefile': 'D:/Clip/cookies.txt',
    
    # ✅ Postprocessor yang LEBIH AGRESIF
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    
    # ✅ JANGAN keep video - otomatis delete setelah merge
    'keepvideo': False,
}

print("⏬ Download + AUTO MERGE...")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("\n✅ SELESAI!")
except Exception as e:
    print(f"\n❌ ERROR: {e}")