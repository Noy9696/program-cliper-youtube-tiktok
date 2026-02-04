import yt_dlp
import time
from datetime import datetime, timedelta

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        downloaded = d.get('_downloaded_bytes_str', '').strip()
        print(f"\r⬇ {percent} | ⚡ {speed} | ⏳ ETA {eta} | 📦 {downloaded}", end='')
    elif d['status'] == 'finished':
        print("\n✅ Download selesai, sedang merge...")

def get_scheduled_time(info):
    """Ambil waktu jadwal live dari info video"""
    release_timestamp = info.get('release_timestamp')
    if release_timestamp:
        return datetime.fromtimestamp(release_timestamp)
    return None

def check_live_status(channel_url):
    """Cek status live: live, upcoming, atau tidak ada"""
    ydl_opts_check = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'playlistend': 5,
        'ignoreerrors': True,  # TAMBAHAN: Ignore error untuk upcoming
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_check) as ydl:
            info = ydl.extract_info(f"{channel_url}/streams", download=False)
            
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        # CEK LIVE SEKARANG
                        if entry.get('is_live'):
                            return {
                                'status': 'live',
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'title': entry.get('title', 'Unknown'),
                                'info': entry
                            }
                        
                        # CEK UPCOMING/SCHEDULED
                        elif entry.get('live_status') == 'is_upcoming':
                            scheduled_time = get_scheduled_time(entry)
                            return {
                                'status': 'upcoming',
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'title': entry.get('title', 'Unknown'),
                                'scheduled_time': scheduled_time,
                                'info': entry
                            }
        
        return {'status': 'none'}
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {'status': 'error'}

def wait_for_live_start(url, title=None, scheduled_time=None):
    """Tunggu sampai live stream dimulai"""
    print(f"\n⏰ WAITING FOR LIVE STREAM")
    print(f"🔗 URL: {url}")
    if title:
        print(f"📺 Title: {title}")
    
    if scheduled_time:
        print(f"⏰ Jadwal: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        time_until = (scheduled_time - datetime.now()).total_seconds()
        
        if time_until > 0:
            print(f"⏳ Waktu tersisa: {int(time_until/60)} menit {int(time_until%60)} detik")
    
    print("\n🔄 Menunggu live stream dimulai...")
    print("💡 Program akan cek setiap 15 detik")
    print("=" * 60)
    
    check_count = 0
    
    while True:
        check_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"\r[{check_count}] {current_time} - Mengecek status... ", end='')
        
        try:
            # PENTING: Tambahkan ignoreerrors untuk bypass upcoming error
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'ignoreerrors': True,  # Bypass error upcoming
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Cek apakah sudah live
                if info and info.get('is_live'):
                    print("\n\n🔴 LIVE SUDAH DIMULAI!")
                    return True, info
                
                # Masih upcoming
                elif info and info.get('live_status') == 'is_upcoming':
                    scheduled = get_scheduled_time(info)
                    if scheduled:
                        remaining = (scheduled - datetime.now()).total_seconds()
                        if remaining > 0:
                            mins = int(remaining / 60)
                            secs = int(remaining % 60)
                            print(f"⏳ Sisa: {mins}m {secs}s  ", end='')
                        else:
                            print("⏳ Sebentar lagi...  ", end='')
                    else:
                        print("⏳ Menunggu...  ", end='')
                
                # Error tapi mungkin masih upcoming
                elif info is None:
                    print("⏳ Belum mulai...  ", end='')
                
                else:
                    print("⚠ Status berubah  ", end='')
        
        except Exception as e:
            error_msg = str(e)
            
            # Deteksi error "will begin in X minutes"
            if "will begin in" in error_msg.lower():
                # Extract menit dari error message
                try:
                    import re
                    match = re.search(r'(\d+)\s*minute', error_msg)
                    if match:
                        mins = int(match.group(1))
                        print(f"⏳ Mulai dalam ~{mins} menit  ", end='')
                    else:
                        print("⏳ Belum mulai...  ", end='')
                except:
                    print("⏳ Menunggu...  ", end='')
            else:
                print(f"⚠ {error_msg[:30]}...  ", end='')
        
        time.sleep(15)

def analyze_video(url, force_info=None):
    """Analisis kualitas video/stream yang tersedia"""
    print("\n🔍 Menganalisis video...")
    
    # Kalau sudah punya info (dari wait), langsung pakai
    if force_info:
        info = force_info
    else:
        ydl_check = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_check) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    print("⚠ Tidak bisa mendapatkan info video")
                    return None
        
        except Exception as e:
            error_msg = str(e)
            
            # Jika upcoming, return info minimal
            if "will begin in" in error_msg.lower():
                print(f"⏰ Live stream dijadwalkan")
                print(f"💡 {error_msg}")
                return {'is_upcoming': True, 'url': url}
            else:
                print(f"⚠ Error saat analisis: {e}")
                return None
    
    # Analisis format
    try:
        formats = info.get('formats', [])
        
        # Filter video formats
        video_formats = [
            f for f in formats 
            if f.get('vcodec') != 'none' 
            and f.get('height')
        ]
        
        # Filter audio formats
        audio_formats = [
            f for f in formats
            if f.get('acodec') != 'none'
            and f.get('vcodec') == 'none'
        ]
        
        if video_formats:
            max_height = max(f.get('height', 0) for f in video_formats)
            max_height_formats = [f for f in video_formats if f.get('height') == max_height]
            max_fps = max(f.get('fps', 30) for f in max_height_formats)
            
            print(f"📺 Resolusi tertinggi: {max_height}p @ {max_fps}fps")
        
        if audio_formats:
            max_abr = max(f.get('abr', 0) for f in audio_formats)
            print(f"🔊 Audio terbaik: {int(max_abr)}kbps")
        
        print(f"🎬 Judul: {info.get('title', 'Unknown')}")
        
        # Cek jika live
        if info.get('is_live'):
            print(f"🔴 Status: LIVE SEKARANG")
        elif info.get('live_status') == 'is_upcoming':
            print(f"⏰ Status: SCHEDULED LIVE")
            scheduled = get_scheduled_time(info)
            if scheduled:
                print(f"📅 Jadwal: {scheduled.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            duration = info.get('duration', 0)
            if duration:
                print(f"⏱ Durasi: {duration // 60} menit {duration % 60} detik")
        
        print(f"✅ Download kualitas maksimal + AUDIO\n")
        
        return info
    
    except Exception as e:
        print(f"⚠ Error saat analisis detail: {e}")
        return info

def download_video(url, is_live=False):
    """Download video atau live stream"""
    
    # Tentukan format sesuai jenis konten
    if is_live:
        format_string = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        output_template = 'D:/CLIP/hasil/[LIVE]_%(title)s_%(upload_date)s.%(ext)s'
    else:
        format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        output_template = 'D:/CLIP/hasil/%(title)s.%(ext)s'
    
    ydl_opts = {
        'format': format_string,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'ffmpeg_location': r'C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin',
        'noplaylist': True,
        'progress_hooks': [progress_hook],
    }
    
    # Tambahan khusus untuk live stream
    if is_live:
        ydl_opts.update({
            'live_from_start': True,
            'wait_for_video': (10, 60),
            'concurrent_fragment_downloads': 5,
        })
    
    print("⏬ Mulai download...")
    print("=" * 50)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("\n" + "=" * 50)
        print("✅ SELESAI! File sudah ada di D:/CLIP/hasil/")
        return True
    
    except Exception as e:
        print(f"\n❌ Error saat download: {e}")
        return False

# ============= MAIN PROGRAM =============

print("=" * 60)
print("🎥 YOUTUBE DOWNLOADER + LIVE STREAM (SMART)")
print("=" * 60)

mode = input("\nPilih mode:\n1. Monitor channel (auto-detect live + upcoming)\n2. Download link langsung (video/live/upcoming)\n3. Wait & download scheduled live\n\nPilih (1/2/3): ")

if mode == "1":
    # MODE MONITOR CHANNEL
    channel_url = input("\nMasukkan URL channel YouTube\n(contoh: https://www.youtube.com/@namachannel): ").strip()
    check_interval = int(input("Cek setiap berapa detik? (rekomendasi: 30-60): "))
    
    print(f"\n🔍 Monitoring channel: {channel_url}")
    print(f"⏱ Interval check: {check_interval} detik")
    print("⛔ Tekan CTRL+C untuk berhenti")
    print("=" * 60)
    
    try:
        checked_count = 0
        while True:
            checked_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n[{checked_count}] {current_time} - Mengecek status...", end='')
            
            result = check_live_status(channel_url)
            
            if result['status'] == 'live':
                print(f"\n🔴 LIVE NOW: {result['title']}")
                print(f"🔗 {result['url']}")
                
                analyze_video(result['url'])
                download_video(result['url'], is_live=True)
                
                lanjut = input("\n\nLanjut monitor? (y/n): ")
                if lanjut.lower() != 'y':
                    break
            
            elif result['status'] == 'upcoming':
                print(f"\n⏰ UPCOMING: {result['title']}")
                if result.get('scheduled_time'):
                    print(f"📅 Jadwal: {result['scheduled_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                tunggu = input("\nTunggu dan auto-download saat mulai? (y/n): ")
                if tunggu.lower() == 'y':
                    is_started, live_info = wait_for_live_start(result['url'], result['title'], result.get('scheduled_time'))
                    if is_started:
                        analyze_video(result['url'], force_info=live_info)
                        download_video(result['url'], is_live=True)
                    
                    lanjut = input("\n\nLanjut monitor? (y/n): ")
                    if lanjut.lower() != 'y':
                        break
            
            else:
                print(" ❌ Belum ada live/upcoming")
            
            # Countdown
            for i in range(check_interval, 0, -1):
                print(f"\r⏳ Check berikutnya dalam {i} detik...  ", end='')
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⛔ Monitoring dihentikan oleh user!")

elif mode == "2":
    # MODE DOWNLOAD LANGSUNG
    url = input("\nMasukkan link YouTube: ").strip()
    
    info = analyze_video(url)
    
    if info:
        is_live = info.get('is_live', False)
        is_upcoming = info.get('live_status') == 'is_upcoming' or info.get('is_upcoming', False)
        
        if is_upcoming:
            tunggu = input("\nStream dijadwalkan. Tunggu sampai mulai? (y/n): ")
            
            if tunggu.lower() == 'y':
                is_started, live_info = wait_for_live_start(url, info.get('title'))
                if is_started:
                    analyze_video(url, force_info=live_info)
                    download_video(url, is_live=True)
            else:
                print("\n⛔ Download dibatalkan")
        else:
            download_video(url, is_live=is_live)

elif mode == "3":
    # MODE WAIT SCHEDULED - LANGSUNG WAIT TANPA ANALISIS DULU
    url = input("\nMasukkan link scheduled live stream: ").strip()
    
    print("\n💡 Mode: Wait for scheduled live")
    print("🔗 URL:", url)
    
    # LANGSUNG MASUK WAITING MODE
    confirm = input("\nMulai waiting mode? (y/n): ")
    
    if confirm.lower() == 'y':
        is_started, live_info = wait_for_live_start(url)
        
        if is_started:
            # Setelah live, baru analisis dan download
            analyze_video(url, force_info=live_info)
            download_video(url, is_live=True)
        else:
            print("\n⛔ Waiting dibatalkan")
    else:
        print("\n⛔ Dibatalkan")

else:
    print("❌ Pilihan tidak valid!")

print("\n" + "=" * 60)
print("Program selesai!")
