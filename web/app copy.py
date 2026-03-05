from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import json
import threading
import time
from yt_downloader import download_youtube, progress as yt_progress

from video_processor import (
    process_scene, 
    merge_videos_simple, 
    merge_videos_with_transition_stepwise,
    merge_videos_with_transition_batch,
    to_sec,
    sec_to_time
)

app = Flask(__name__)
CORS(app)

# Configuration
FFMPEG = r"C:\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-essentials_build\bin\ffmpeg.exe"
SOURCE = r"D:\CLIP\hasil\Mentah.mp4"
OUTPUT_DIR = r"D:\CLIP\hasil"
FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "final_merged.mp4")

# Global variables untuk tracking progress
processing_status = {
    'is_processing': False,
    'current_scene': 0,
    'total_scenes': 0,
    'progress': 0,
    'status': 'idle',
    'message': '',
    'scene_files': [],
    'final_output': None,
    'error': None
}

@app.route('/')
def index():
    """Render halaman utama"""
    return render_template('index.html', video_source=SOURCE)

@app.route('/api/video-info')
def video_info():
    """Get video duration dan info lainnya"""
    import subprocess
    
    probe_cmd = [FFMPEG, "-i", SOURCE]
    result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    duration = 0
    for line in result.stderr.split('\n'):
        if 'Duration:' in line:
            try:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = time_str.split(':')
                duration = float(h) * 3600 + float(m) * 60 + float(s)
                break
            except:
                pass
    
    return jsonify({
        'duration': duration,
        'duration_formatted': sec_to_time(int(duration)),
        'path': SOURCE,
        'exists': os.path.exists(SOURCE)
    })

@app.route('/api/process', methods=['POST'])
def process_videos():
    """Process video dengan scenes yang diinput"""
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({'error': 'Already processing'}), 400
    
    data = request.json
    scenes = data.get('scenes', [])
    transition_type = data.get('transition_type', '0')
    merge_method = data.get('merge_method', 'stepwise')
    
    if not scenes:
        return jsonify({'error': 'No scenes provided'}), 400
    
    # Reset status
    processing_status = {
        'is_processing': True,
        'current_scene': 0,
        'total_scenes': len(scenes),
        'progress': 0,
        'status': 'starting',
        'message': 'Memulai proses...',
        'scene_files': [],
        'final_output': None,
        'error': None
    }
    
    # Start processing di thread terpisah
    thread = threading.Thread(target=process_worker, args=(scenes, transition_type, merge_method))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

def process_worker(scenes, transition_type, merge_method):
    """Worker function untuk processing video"""
    global processing_status
    
    try:
        scene_files = []
        
        # Process setiap scene
        for idx, scene in enumerate(scenes, 1):
            processing_status['current_scene'] = idx
            processing_status['status'] = 'processing_scene'
            processing_status['message'] = f'Processing scene {idx}/{len(scenes)}...'
            
            output_file = os.path.join(OUTPUT_DIR, f"scene_{idx:03d}.mp4")
            
            # Convert start time to seconds
            start_sec = to_sec(scene['start_time'])
            duration = int(scene['duration'])
            
            # Blink config
            blink_config = {
                'enabled': scene.get('blink_enabled', False),
                'start': scene.get('blink_start', 0),
                'end': scene.get('blink_end', 0)
            }
            
            # Process scene
            success = process_scene(
                idx,
                start_sec,
                duration,
                output_file,
                blink_config,
                scene.get('gamer_position', 'atas')
            )
            
            if success:
                scene_files.append(output_file)
                processing_status['scene_files'].append({
                    'number': idx,
                    'path': output_file,
                    'filename': os.path.basename(output_file),
                    'size': os.path.getsize(output_file)
                })
            else:
                raise Exception(f"Failed to process scene {idx}")
            
            # Update progress
            processing_status['progress'] = int((idx / len(scenes)) * 50)  # 0-50% untuk scenes
        
        # Merge videos
        processing_status['status'] = 'merging'
        processing_status['message'] = 'Menggabungkan scenes...'
        
        if transition_type == '0':
            success = merge_videos_simple(scene_files, FINAL_OUTPUT)
        else:
            if merge_method == 'stepwise':
                success = merge_videos_with_transition_stepwise(scene_files, FINAL_OUTPUT, transition_type)
            else:
                success = merge_videos_with_transition_batch(scene_files, FINAL_OUTPUT, transition_type)
        
        if success:
            processing_status['status'] = 'completed'
            processing_status['message'] = 'Proses selesai!'
            processing_status['progress'] = 100
            processing_status['final_output'] = {
                'path': FINAL_OUTPUT,
                'filename': os.path.basename(FINAL_OUTPUT),
                'size': os.path.getsize(FINAL_OUTPUT)
            }
        else:
            raise Exception("Merge failed")
    
    except Exception as e:
        processing_status['status'] = 'error'
        processing_status['message'] = str(e)
        processing_status['error'] = str(e)
    
    finally:
        processing_status['is_processing'] = False

@app.route('/api/status')
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download processed video"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/video/<path:filename>')
def serve_video(filename):
    """Serve video untuk preview"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='video/mp4')
    return jsonify({'error': 'File not found'}), 404

@app.route('/source-video')
def serve_source_video():
    if not os.path.exists(SOURCE):
        return jsonify({'error': 'Source video not found'}), 404

    file_size = os.path.getsize(SOURCE)
    range_header = request.headers.get('Range', None)

    if not range_header:
        return send_file(SOURCE, mimetype='video/mp4', conditional=True)

    byte1, byte2 = 0, None
    match = range_header.replace('bytes=', '').split('-')

    if match[0]:
        byte1 = int(match[0])
    if len(match) > 1 and match[1]:
        byte2 = int(match[1])

    byte2 = byte2 if byte2 is not None else file_size - 1
    length = byte2 - byte1 + 1

    with open(SOURCE, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(
        data,
        206,
        mimetype='video/mp4',
        content_type='video/mp4',
        direct_passthrough=True
    )
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    rv.headers.add('Content-Length', str(length))
    return rv


@app.route('/api/youtube/download', methods=['POST'])
def youtube_download():
    if processing_status['is_processing']:
        return jsonify({'error': 'Processing video, tunggu dulu'}), 400

    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL kosong'}), 400

    def worker():
        global SOURCE
        SOURCE = download_youtube(url)

        # pastikan file siap dibaca
        for _ in range(10):
            if os.path.exists(SOURCE) and os.path.getsize(SOURCE) > 5_000_000:
                break
            time.sleep(0.5)



    threading.Thread(target=worker, daemon=True).start()
    return jsonify({'status': 'started'})

@app.route('/api/youtube/progress')
def youtube_progress():
    return jsonify(yt_progress)


if __name__ == '__main__':
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

@app.route('/api/videos')
def list_videos():
    videos = []
    for f in os.listdir(OUTPUT_DIR):
        if f.lower().endswith('.mp4'):
            path = os.path.join(OUTPUT_DIR, f)
            videos.append({
                'filename': f,
                'size': os.path.getsize(path)
            })

    return jsonify(sorted(videos, key=lambda x: x['filename']))

@app.route('/api/set-source', methods=['POST'])
def set_source():
    global SOURCE
    filename = request.json.get('filename')

    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404

    SOURCE = path
    return jsonify({'status': 'ok', 'source': filename})
