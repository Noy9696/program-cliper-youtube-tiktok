from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import threading

app = Flask(__name__)

DOWNLOAD_FOLDER = 'D:/Clip/hasil'
COOKIES_FILE = 'D:/Clip/cookies.txt'

# Status download
download_status = {}


def get_channel_videos(channel_url):
    """Ambil semua video dari channel"""
    
    # ✅ Clean URL (hapus parameter ?si=xxx)
    if '?' in channel_url:
        channel_url = channel_url.split('?')[0]
    
    # ✅ Pastikan ada https://www
    if not channel_url.startswith('http'):
        channel_url = 'https://' + channel_url
    if 'youtube.com' in channel_url and not channel_url.startswith('https://www.'):
        channel_url = channel_url.replace('https://youtube.com', 'https://www.youtube.com')
    
    # ✅ Otomatis tambahkan /videos kalau belum ada
    if '@' in channel_url or '/c/' in channel_url or '/user/' in channel_url or '/channel/' in channel_url:
        if not channel_url.endswith(('/videos', '/streams', '/shorts', '/live')):
            channel_url = channel_url.rstrip('/') + '/videos'
    
    print(f"🔍 Final URL: {channel_url}")  # Debug
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'playlistend': 100,
        'cookiefile': COOKIES_FILE,
        'ignoreerrors': True,
        'no_warnings': False,
        
        # Bypass proteksi
        'extractor_args': {
            'youtube': {
                'player_skip': ['webpage'],
                'player_client': ['android', 'web'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            
            if not info:
                return {'success': False, 'error': 'Tidak dapat mengakses channel'}
            
            videos = []
            entries = info.get('entries', [])
            
            if not entries:
                return {'success': False, 'error': 'Tidak ada video ditemukan'}
            
            for entry in entries:
                if entry and entry.get('id'):
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Unknown Title'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'thumbnail': entry.get('thumbnail') or f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg",
                        'duration': entry.get('duration'),
                        'view_count': entry.get('view_count'),
                        'upload_date': entry.get('upload_date'),
                    })
            
            channel_name = info.get('uploader') or info.get('channel') or info.get('title') or 'Unknown Channel'
            
            print(f"✅ Found {len(videos)} videos from {channel_name}")  # Debug
            
            return {
                'success': True,
                'channel_name': channel_name,
                'videos': videos
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        
        if 'unavailable' in error_msg.lower():
            return {'success': False, 'error': 'Channel tidak tersedia. Pastikan cookies.txt valid.'}
        elif 'private' in error_msg.lower():
            return {'success': False, 'error': 'Channel private. Update cookies.txt dengan akun yang punya akses.'}
        else:
            return {'success': False, 'error': f'Error: {error_msg}'}
    """Ambil semua video dari channel"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'playlistend': 100,
        'cookiefile': COOKIES_FILE,
        'ignoreerrors': True,  # Skip video yang error
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            
            videos = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        videos.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'thumbnail': entry.get('thumbnail') or f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg",
                            'duration': entry.get('duration'),
                            'view_count': entry.get('view_count'),
                            'upload_date': entry.get('upload_date'),
                        })
            
            return {
                'success': True,
                'channel_name': info.get('uploader') or info.get('channel') or info.get('title'),
                'videos': videos
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_video_formats(video_url):
    """Ambil format video yang tersedia (untuk quality picker)"""
    ydl_opts = {
        'quiet': True,
        'cookiefile': COOKIES_FILE,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            formats = []
            seen = set()
            
            # Prioritas format (sama kayak script kamu)
            priority_formats = [
                ('301', '1080p60 (Recommended)'),
                ('300', '720p60'),
                ('299+251', '1080p60 (Best Quality)'),
                ('298+251', '720p60 (Best Quality)'),
                ('best', 'Auto (Best Available)'),
            ]
            
            for fmt_id, label in priority_formats:
                formats.append({
                    'format_id': fmt_id,
                    'label': label,
                    'recommended': fmt_id == '301'
                })
            
            return {
                'success': True,
                'formats': formats,
                'title': info.get('title')
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def download_video(video_url, video_id, format_id=None):
    """Download video - METODE SAMA kayak script kamu"""
    
    # Default ke format 301 (sama kayak script kamu)
    format_str = format_id if format_id else '301/bestvideo+bestaudio/best'
    
    ydl_opts = {
        'format': format_str,
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': COOKIES_FILE,
        'noplaylist': True,
        'retries': 10,
        'fragment_retries': 10,
        
        # Progress hook
        'progress_hooks': [lambda d: update_progress(video_id, d)],
        
        # Postprocessor (sama kayak script kamu)
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        download_status[video_id] = {
            'status': 'downloading', 
            'progress': 0,
            'speed': '',
            'eta': ''
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        download_status[video_id] = {'status': 'completed', 'progress': 100}
        
    except Exception as e:
        download_status[video_id] = {'status': 'error', 'error': str(e)}


def update_progress(video_id, d):
    """Update progress download"""
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)
        
        if total > 0:
            progress = int((downloaded / total) * 100)
            speed_mb = round(speed / (1024*1024), 2) if speed else 0
            
            download_status[video_id].update({
                'progress': progress,
                'speed': f"{speed_mb} MB/s" if speed_mb else '',
                'eta': f"{eta}s" if eta else ''
            })


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_videos', methods=['POST'])
def get_videos():
    """API: Get channel videos"""
    channel_url = request.json.get('channel_url')
    
    if not channel_url:
        return jsonify({'success': False, 'error': 'URL tidak boleh kosong'})
    
    result = get_channel_videos(channel_url)
    return jsonify(result)


@app.route('/get_formats', methods=['POST'])
def get_formats():
    """API: Get available formats"""
    video_url = request.json.get('video_url')
    
    if not video_url:
        return jsonify({'success': False, 'error': 'URL tidak boleh kosong'})
    
    result = get_video_formats(video_url)
    return jsonify(result)


@app.route('/download', methods=['POST'])
def start_download():
    """API: Start download"""
    video_url = request.json.get('video_url')
    video_id = request.json.get('video_id')
    format_id = request.json.get('format_id', '301/bestvideo+bestaudio/best')
    
    if not video_url or not video_id:
        return jsonify({'success': False, 'error': 'Data tidak lengkap'})
    
    # Download di background thread
    thread = threading.Thread(
        target=download_video, 
        args=(video_url, video_id, format_id),
        daemon=True
    )
    thread.start()
    
    return jsonify({'success': True, 'message': 'Download dimulai'})


@app.route('/download_status/<video_id>')
def get_download_status(video_id):
    """API: Check download status"""
    status = download_status.get(video_id, {'status': 'not_found'})
    return jsonify(status)


@app.route('/check_cookies')
def check_cookies():
    """API: Check if cookies.txt exists"""
    exists = os.path.exists(COOKIES_FILE)
    return jsonify({
        'exists': exists,
        'path': COOKIES_FILE
    })


if __name__ == '__main__':
    # Pastikan folder ada
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # Check cookies
    cookies_exists = os.path.exists(COOKIES_FILE)
    
    print("\n" + "="*60)
    print("🚀 YouTube Downloader Server - READY!")
    print("="*60)
    print(f"📂 Download folder: {DOWNLOAD_FOLDER}")
    print(f"🍪 Cookies file: {COOKIES_FILE}")
    print(f"   Status: {'✅ FOUND' if cookies_exists else '❌ NOT FOUND'}")
    if not cookies_exists:
        print("   ⚠️  WARNING: Cookies tidak ditemukan!")
        print("   💡 Buat cookies.txt dulu dengan browser extension")
    print(f"🌐 Akses di: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, threaded=True)