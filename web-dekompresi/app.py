from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import os
import json
import subprocess
import threading
from datetime import datetime
import time

# Import core optimizer
from tiktok_optimizer import get_video_info, optimize_for_tiktok

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/uploads/outputs'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global progress tracker
processing_status = {}

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Upload video input"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get video info
        info = get_video_info(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'url': url_for('static', filename=f'uploads/{filename}'),
            'info': {
                'duration': round(info['duration'], 2),
                'width': info['width'],
                'height': info['height'],
                'fps': info['fps'],
                'bitrate': info['bitrate'],
                'has_audio': info['has_audio'],
                'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
            }
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """Upload audio file (background or sound effect)"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
        })
    
    return jsonify({'error': 'Invalid audio file type'}), 400

def process_video_thread(job_id, input_path, output_path, preset, audio_config, sound_effects):
    """Background thread untuk processing video"""
    try:
        processing_status[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Initializing...',
            'start_time': time.time()
        }
        
        # Custom callback untuk update progress
        def update_progress(progress, message):
            processing_status[job_id]['progress'] = progress
            processing_status[job_id]['message'] = message
        
        # Process video
        success = optimize_for_tiktok(
            input_path, 
            output_path, 
            preset, 
            audio_config, 
            sound_effects
        )
        
        if success:
            # Get output info
            output_size = os.path.getsize(output_path) / (1024 * 1024)
            input_size = os.path.getsize(input_path) / (1024 * 1024)
            
            processing_status[job_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Processing completed!',
                'output_file': os.path.basename(output_path),
                'output_url': url_for('static', filename=f'uploads/outputs/{os.path.basename(output_path)}'),
                'output_size_mb': round(output_size, 2),
                'input_size_mb': round(input_size, 2),
                'compression_ratio': round((1 - output_size/input_size) * 100, 1) if input_size > 0 else 0,
                'processing_time': round(time.time() - processing_status[job_id]['start_time'], 1)
            }
        else:
            processing_status[job_id] = {
                'status': 'error',
                'progress': 0,
                'message': 'Processing failed!'
            }
    
    except Exception as e:
        processing_status[job_id] = {
            'status': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}'
        }

@app.route('/process', methods=['POST'])
def process_video():
    """Start video processing"""
    data = request.json
    
    # Validate input
    if 'input_file' not in data or 'preset' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    input_path = data['input_file']
    preset = data['preset']
    
    # Parse audio config
    audio_config = {
        'use_external_audio': data.get('use_background_audio', False),
        'keep_original': data.get('keep_original_audio', True),
        'original_volume': data.get('original_volume', 100),
        'external_volume': data.get('background_volume', 100)
    }
    
    if audio_config['use_external_audio']:
        audio_config['external_audio_path'] = data.get('background_audio_file', '')
    
    # Parse sound effects
    sound_effects = data.get('sound_effects', [])
    
    # Generate output filename
    input_name = os.path.splitext(os.path.basename(input_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{input_name}_tiktok_{preset}_{timestamp}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Create job ID
    job_id = f"job_{timestamp}"
    
    # Start processing in background thread
    thread = threading.Thread(
        target=process_video_thread,
        args=(job_id, input_path, output_path, preset, audio_config, sound_effects)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'Processing started'
    })

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get processing status"""
    if job_id in processing_status:
        return jsonify(processing_status[job_id])
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed video"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/history')
def get_history():
    """Get processing history"""
    outputs_dir = app.config['OUTPUT_FOLDER']
    files = []
    
    if os.path.exists(outputs_dir):
        for filename in os.listdir(outputs_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(outputs_dir, filename)
                files.append({
                    'filename': filename,
                    'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                    'url': url_for('static', filename=f'uploads/outputs/{filename}')
                })
    
    # Sort by created time (newest first)
    files.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({'files': files})

if __name__ == '__main__':
    print("="*70)
    print("🚀 TIKTOK OPTIMIZER WEB APP")
    print("="*70)
    print("\n🌐 Server starting...")
    print("📍 URL: http://localhost:5000")
    print("\n💡 Press CTRL+C to stop server")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
