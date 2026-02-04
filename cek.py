import yt_dlp

url = "https://www.youtube.com/live/C8wTDV03OMU?si=JwOgo_ze4SBxkBe9"

ydl_opts = {
    'cookiefile': 'www.youtube.com_cookies.txt',
    'listformats': True,
    'quiet': False,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web']
        }
    },
}

print("🔍 Checking available formats...\n")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    
    print(f"\n📺 Title: {info.get('title')}")
    print(f"🔴 Is Live: {info.get('is_live', False)}")
    print(f"⏺ Was Live: {info.get('was_live', False)}")
    print(f"⏱ Duration: {info.get('duration', 'N/A')}")
    
    formats = info.get('formats', [])
    
    print(f"\n📋 Total formats available: {len(formats)}\n")
    
    # Group by type
    video_only = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') == 'none']
    audio_only = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
    combined = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
    
    print("=" * 80)
    print("VIDEO ONLY:")
    print("=" * 80)
    for f in video_only[:10]:  # Show first 10
        print(f"ID: {f.get('format_id'):10} | {f.get('height', 'N/A'):4}p | "
              f"FPS: {f.get('fps', 'N/A'):5} | Codec: {f.get('vcodec', 'N/A'):15} | "
              f"Size: {f.get('filesize_approx', 0) / 1024 / 1024:.1f} MB")
    
    print("\n" + "=" * 80)
    print("AUDIO ONLY:")
    print("=" * 80)
    for f in audio_only[:5]:
        print(f"ID: {f.get('format_id'):10} | Bitrate: {f.get('abr', 'N/A'):6} kbps | "
              f"Codec: {f.get('acodec', 'N/A'):15}")
    
    print("\n" + "=" * 80)
    print("COMBINED (VIDEO + AUDIO):")
    print("=" * 80)
    for f in combined[:5]:
        print(f"ID: {f.get('format_id'):10} | {f.get('height', 'N/A'):4}p | "
              f"FPS: {f.get('fps', 'N/A'):5} | Codec: {f.get('vcodec', 'N/A'):15}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED FORMAT SELECTORS:")
    print("=" * 80)
    
    if info.get('is_live'):
        print("🔴 LIVE STREAM detected!")
        print("   Use: 'best' or 'bestvideo+bestaudio/best'")
    else:
        print("   Use: 'bv*+ba/b' (best video + best audio)")
        print("   Or:  'bestvideo[height<=1080]+bestaudio/best[height<=1080]'")