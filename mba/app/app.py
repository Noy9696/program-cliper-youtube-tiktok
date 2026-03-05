from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from serpapi import GoogleSearch
import json
import time
import csv
import pandas as pd
from datetime import datetime
import threading
import queue
import os
import re
from urllib.parse import unquote
import requests

app = Flask(__name__)
CORS(app)

# ===== CONFIG =====
API_KEY = '549cecc301a42c18cb64c81760afbe05088983b56c9d1228605a1263da3d7512'

# Queue untuk menampung job
job_queue = queue.Queue()
jobs_status = {}
jobs_results = {}
current_job_id = 0
is_processing = False

# ===== FUNGSI RESOLVE SHORT URL =====
def resolve_short_url(url):
    """Resolve shortened URL (goo.gl, maps.app.goo.gl) ke URL penuh"""
    try:
        print(f"[DEBUG] Resolving short URL: {url}")
        
        # Follow redirect tanpa download content
        response = requests.head(url, allow_redirects=True, timeout=10)
        resolved_url = response.url
        
        print(f"[DEBUG] Resolved to: {resolved_url}")
        return resolved_url
        
    except Exception as e:
        print(f"[ERROR] Failed to resolve URL: {str(e)}")
        # Jika gagal resolve, coba gunakan requests.get
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            return response.url
        except:
            return url  # Return original jika gagal

# ===== FUNGSI EKSTRAK PLACE_ID DARI URL =====
def extract_place_info_from_url(url):
    """
    Ekstrak informasi tempat dari berbagai format Google Maps URL
    """
    # Resolve short URL jika ada
    if 'goo.gl' in url or 'maps.app.goo.gl' in url:
        url = resolve_short_url(url)
    
    print(f"[DEBUG] Processing URL: {url}")
    
    # Decode URL jika ter-encode
    url = unquote(url)
    
    # Method 1: Cari CID (Contributed ID) - paling reliable
    cid_match = re.search(r'!1s(0x[a-fA-F0-9]+:0x[a-fA-F0-9]+)', url)
    if cid_match:
        data_id = cid_match.group(1)
        print(f"[DEBUG] Found CID data_id: {data_id}")
        return {'type': 'data_id', 'value': data_id}
    
    # Method 2: Cari data_id di bagian data= parameter
    data_param_match = re.search(r'data=.*?([0-9]s0x[a-fA-F0-9]+:0x[a-fA-F0-9]+)', url)
    if data_param_match:
        data_id = data_param_match.group(1).split('s', 1)[1]  # Remove leading number
        print(f"[DEBUG] Found data_id in data param: {data_id}")
        return {'type': 'data_id', 'value': data_id}
    
    # Method 3: Cari format 0x langsung
    data_id_match = re.search(r'(0x[a-fA-F0-9]+:0x[a-fA-F0-9]+)', url)
    if data_id_match:
        data_id = data_id_match.group(1)
        print(f"[DEBUG] Found direct data_id: {data_id}")
        return {'type': 'data_id', 'value': data_id}
    
    # Method 4: Cari place_id
    place_id_match = re.search(r'place_id=([^&]+)', url)
    if place_id_match:
        place_id = place_id_match.group(1)
        print(f"[DEBUG] Found place_id: {place_id}")
        return {'type': 'place_id', 'value': place_id}
    
    # Method 5: Ekstrak nama dari URL path
    place_name_match = re.search(r'/place/([^/@]+)', url)
    if place_name_match:
        place_name = place_name_match.group(1).replace('+', ' ').replace('%20', ' ')
        print(f"[DEBUG] Found place name from path: {place_name}")
        return {'type': 'name', 'value': place_name}
    
    # Method 6: Cari di search query
    search_match = re.search(r'[?&]q=([^&]+)', url)
    if search_match:
        search_query = search_match.group(1).replace('+', ' ').replace('%20', ' ')
        print(f"[DEBUG] Found search query: {search_query}")
        return {'type': 'name', 'value': search_query}
    
    # Method 7: Last resort - extract dari title di URL
    title_match = re.search(r'/maps/.*?/([^/]+)/@', url)
    if title_match:
        title = title_match.group(1).replace('+', ' ').replace('%20', ' ')
        print(f"[DEBUG] Found title from URL: {title}")
        return {'type': 'name', 'value': title}
    
    print("[DEBUG] No place info found in URL")
    return None

# ===== FUNGSI SCRAPING TEMPAT BY NAME =====
def scrape_place_by_name(place_name):
    """Scrape data tempat dari nama tempat"""
    
    print(f"[INFO] Searching for: {place_name}")
    
    try:
        # Search by name
        params = {
            'api_key': API_KEY,
            'engine': 'google_maps',
            'q': place_name,
            'hl': 'id'
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        print(f"[DEBUG] API Response keys: {results.keys()}")
        
        # Method 1: Cek local_results
        if 'local_results' in results and len(results['local_results']) > 0:
            first = results['local_results'][0]
            print(f"[SUCCESS] Found: {first.get('title')}")
            
            # Fetch full details jika ada data_id
            if 'data_id' in first:
                print(f"[INFO] Fetching full details...")
                detail_params = {
                    'api_key': API_KEY,
                    'engine': 'google_maps',
                    'data_id': first['data_id'],
                    'hl': 'id'
                }
                
                detail_search = GoogleSearch(detail_params)
                detail_results = detail_search.get_dict()
                
                if 'place_results' in detail_results:
                    print(f"[SUCCESS] Got full place details")
                    return detail_results['place_results']
            
            # Return first result
            return first
        
        # Method 2: Cek place_results
        elif 'place_results' in results:
            print(f"[SUCCESS] Found: {results['place_results'].get('title')}")
            return results['place_results']
        
        print("[ERROR] No results found")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
# ===== FUNGSI SCRAPING REVIEWS =====
# ===== FUNGSI SCRAPING REVIEWS (FIXED - UNLIMITED) =====
def scrape_reviews(data_id, filter_rating=None, max_reviews=None):
    """Scrape reviews dari tempat - support unlimited reviews"""
    all_reviews = []
    next_page_token = None
    page = 1
    max_pages = 300  # Safety limit (300 pages x 10 reviews = 3000 reviews)
    
    print(f"[INFO] Target: {'ALL' if not max_reviews else max_reviews} reviews")
    
    while page <= max_pages:
        # Stop jika sudah mencapai target
        if max_reviews and len(all_reviews) >= max_reviews:
            print(f"[INFO] Target {max_reviews} reviews tercapai!")
            break
        
        print(f"[INFO] Fetching page {page}... (Total so far: {len(all_reviews)})")
        
        params = {
            'api_key': API_KEY,
            'engine': 'google_maps_reviews',
            'data_id': data_id,
            'hl': 'id',
            'sort_by': 'qualityScore',
            'num': 10  # Reviews per page (max 10 di SerpApi)
        }
        
        if next_page_token:
            params['next_page_token'] = next_page_token
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if 'reviews' in results and len(results['reviews']) > 0:
                reviews = results['reviews']
                
                # Filter rating jika diperlukan
                if filter_rating:
                    reviews = [r for r in reviews if r.get('rating') in filter_rating]
                
                all_reviews.extend(reviews)
                print(f"[SUCCESS] Got {len(reviews)} reviews | Total: {len(all_reviews)}")
                
                # Update progress setiap 10 halaman
                if page % 10 == 0:
                    print(f"[PROGRESS] {len(all_reviews)} reviews collected...")
            else:
                print("[INFO] No more reviews available")
                break
            
            # Check pagination
            if 'serpapi_pagination' in results and 'next_page_token' in results['serpapi_pagination']:
                next_page_token = results['serpapi_pagination']['next_page_token']
                page += 1
                
                # Delay untuk menghindari rate limit
                # Setiap 50 request, delay lebih lama
                if page % 50 == 0:
                    print(f"[INFO] Rate limit protection: sleeping 5 seconds...")
                    time.sleep(5)
                else:
                    time.sleep(1)  # Normal delay
            else:
                print("[INFO] No more pages available")
                break
                
        except Exception as e:
            print(f"[ERROR] Page {page} failed: {str(e)}")
            # Jika error, coba lanjut ke page berikutnya (mungkin temporary error)
            if page < 5:  # Jika masih awal, break aja
                break
            page += 1
            time.sleep(2)
            continue
    
    # Potong sesuai max_reviews jika ada
    if max_reviews:
        all_reviews = all_reviews[:max_reviews]
    
    print(f"[SUCCESS] Total reviews collected: {len(all_reviews)}")
    return all_reviews
# ===== FUNGSI SIMPAN FILE =====
def save_files(place_data, reviews, filter_rating, output_formats, job_id):
    """Simpan hasil scraping ke file"""
    safe_filename = place_data.get('title', 'tempat').replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f'output/{job_id}_{safe_filename}_{timestamp}'
    
    os.makedirs('output', exist_ok=True)
    
    saved_files = []
    
    # JSON
    if 'json' in output_formats:
        output_data = {
            'metadata': {
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_reviews': len(reviews),
                'filter_rating': filter_rating if filter_rating else 'Semua'
            },
            'tempat': {
                'nama': place_data.get('title'),
                'rating': place_data.get('rating'),
                'total_reviews_google': place_data.get('reviews'),
                'alamat': place_data.get('address'),
                'telepon': place_data.get('phone'),
                'website': place_data.get('website'),
                'koordinat': {
                    'latitude': place_data.get('gps_coordinates', {}).get('latitude'),
                    'longitude': place_data.get('gps_coordinates', {}).get('longitude')
                }
            },
            'reviews': [
                {
                    'no': i + 1,
                    'nama_reviewer': r.get('user', {}).get('name', 'Anonymous'),
                    'rating': r.get('rating'),
                    'tanggal': r.get('date'),
                    'review_text': r.get('snippet'),
                    'likes': r.get('likes', 0)
                }
                for i, r in enumerate(reviews)
            ]
        }
        
        filename = f'{base_filename}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        saved_files.append(filename)
    
    # CSV
    if 'csv' in output_formats:
        filename = f'{base_filename}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['INFORMASI TEMPAT'])
            writer.writerow(['Nama', place_data.get('title')])
            writer.writerow(['Rating', place_data.get('rating')])
            writer.writerow(['Total Reviews', place_data.get('reviews')])
            writer.writerow(['Alamat', place_data.get('address')])
            writer.writerow([])
            writer.writerow(['No', 'Nama Reviewer', 'Rating', 'Tanggal', 'Review Text', 'Likes'])
            
            for i, review in enumerate(reviews, 1):
                writer.writerow([
                    i,
                    review.get('user', {}).get('name', 'Anonymous'),
                    review.get('rating', '-'),
                    review.get('date', '-'),
                    review.get('snippet', '-'),
                    review.get('likes', 0)
                ])
        saved_files.append(filename)
    
    # Excel
    if 'excel' in output_formats:
        filename = f'{base_filename}.xlsx'
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            info_data = {
                'Field': ['Nama', 'Rating', 'Total Reviews', 'Alamat'],
                'Value': [
                    place_data.get('title'),
                    place_data.get('rating'),
                    place_data.get('reviews'),
                    place_data.get('address')
                ]
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Info Tempat', index=False)
            
            reviews_data = []
            for i, review in enumerate(reviews, 1):
                reviews_data.append({
                    'No': i,
                    'Nama Reviewer': review.get('user', {}).get('name', 'Anonymous'),
                    'Rating': review.get('rating', '-'),
                    'Tanggal': review.get('date', '-'),
                    'Review Text': review.get('snippet', '-'),
                    'Likes': review.get('likes', 0)
                })
            
            df_reviews = pd.DataFrame(reviews_data)
            df_reviews.to_excel(writer, sheet_name='Reviews', index=False)
        saved_files.append(filename)
    
    return saved_files

# ===== WORKER THREAD =====
# ===== WORKER THREAD (with progress update) =====
def process_queue():
    global is_processing
    
    while True:
        try:
            job = job_queue.get(timeout=1)
            job_id = job['id']
            
            is_processing = True
            jobs_status[job_id] = {
                'status': 'processing',
                'message': 'Mencari tempat...',
                'progress': 10,
                'place_name': job['place_name']
            }
            
            try:
                print(f"\n[JOB {job_id}] Starting...")
                print(f"[JOB {job_id}] Place: {job['place_name']}")
                
                # Scrape tempat
                jobs_status[job_id]['message'] = 'Mengambil data tempat...'
                jobs_status[job_id]['progress'] = 20
                
                place_data = scrape_place_by_name(job['place_name'])
                
                if not place_data:
                    jobs_status[job_id] = {
                        'status': 'error',
                        'message': 'Tempat tidak ditemukan!',
                        'progress': 0,
                        'place_name': job['place_name']
                    }
                    job_queue.task_done()
                    continue
                
                # Scrape reviews dengan progress tracking
                jobs_status[job_id]['message'] = f"Mengambil reviews {place_data.get('title')}..."
                jobs_status[job_id]['progress'] = 30
                jobs_status[job_id]['place_name'] = place_data.get('title')
                
                # Fungsi callback untuk update progress
                def update_review_progress(current, total_so_far):
                    # Progress dari 30% ke 80% berdasarkan jumlah reviews
                    if job['max_reviews']:
                        progress_pct = min(80, 30 + (50 * total_so_far / job['max_reviews']))
                    else:
                        # Jika unlimited, increment pelan-pelan
                        progress_pct = min(75, 30 + (total_so_far / 20))
                    
                    jobs_status[job_id]['progress'] = int(progress_pct)
                    jobs_status[job_id]['message'] = f"Mengambil reviews... ({total_so_far} reviews)"
                
                # Scrape reviews
                reviews = scrape_reviews_with_callback(
                    place_data.get('data_id'),
                    job['filter_rating'],
                    job['max_reviews'],
                    update_review_progress
                )
                
                # Simpan file
                jobs_status[job_id]['message'] = 'Menyimpan file...'
                jobs_status[job_id]['progress'] = 85
                
                saved_files = save_files(
                    place_data,
                    reviews,
                    job['filter_rating'],
                    job['output_formats'],
                    job_id
                )
                
                # Selesai
                jobs_status[job_id] = {
                    'status': 'completed',
                    'message': f'Selesai! {len(reviews)} reviews',
                    'progress': 100,
                    'place_name': place_data.get('title'),
                    'total_reviews': len(reviews),
                    'files': saved_files
                }
                
                print(f"[JOB {job_id}] DONE!\n")
                
            except Exception as e:
                print(f"[JOB {job_id}] ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                
                jobs_status[job_id] = {
                    'status': 'error',
                    'message': f'Error: {str(e)}',
                    'progress': 0,
                    'place_name': job['place_name']
                }
            
            job_queue.task_done()
            
        except queue.Empty:
            is_processing = False
            time.sleep(1)

# ===== FUNGSI SCRAPING REVIEWS WITH CALLBACK =====
def scrape_reviews_with_callback(data_id, filter_rating=None, max_reviews=None, progress_callback=None):
    """Scrape reviews dengan progress callback"""
    all_reviews = []
    next_page_token = None
    page = 1
    max_pages = 300
    
    print(f"[INFO] Target: {'ALL' if not max_reviews else max_reviews} reviews")
    
    while page <= max_pages:
        if max_reviews and len(all_reviews) >= max_reviews:
            break
        
        print(f"[INFO] Page {page}... (Total: {len(all_reviews)})")
        
        params = {
            'api_key': API_KEY,
            'engine': 'google_maps_reviews',
            'data_id': data_id,
            'hl': 'id',
            'sort_by': 'qualityScore',
            'num': 10
        }
        
        if next_page_token:
            params['next_page_token'] = next_page_token
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if 'reviews' in results and len(results['reviews']) > 0:
                reviews = results['reviews']
                
                if filter_rating:
                    reviews = [r for r in reviews if r.get('rating') in filter_rating]
                
                all_reviews.extend(reviews)
                
                # Callback untuk update progress
                if progress_callback:
                    progress_callback(page, len(all_reviews))
                
                print(f"[SUCCESS] Got {len(reviews)} reviews | Total: {len(all_reviews)}")
            else:
                break
            
            if 'serpapi_pagination' in results and 'next_page_token' in results['serpapi_pagination']:
                next_page_token = results['serpapi_pagination']['next_page_token']
                page += 1
                
                if page % 50 == 0:
                    print(f"[INFO] Rate limit protection: sleeping 5s...")
                    time.sleep(5)
                else:
                    time.sleep(1)
            else:
                break
                
        except Exception as e:
            print(f"[ERROR] Page {page}: {str(e)}")
            if page < 5:
                break
            page += 1
            time.sleep(2)
            continue
    
    if max_reviews:
        all_reviews = all_reviews[:max_reviews]
    
    print(f"[SUCCESS] Total: {len(all_reviews)} reviews")
    return all_reviews
worker_thread = threading.Thread(target=process_queue, daemon=True)
worker_thread.start()

# ===== API ENDPOINTS =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_job', methods=['POST'])
def add_job():
    global current_job_id
    
    data = request.json
    current_job_id += 1
    
    filter_rating = None
    if data['filter_rating'] != 'all':
        if data['filter_rating'] == 'positive':
            filter_rating = [4, 5]
        elif data['filter_rating'] == 'negative':
            filter_rating = [1, 2, 3]
        else:
            filter_rating = [int(data['filter_rating'])]
    
    max_reviews = None if data['max_reviews'] == 'all' else int(data['max_reviews'])
    
    job = {
        'id': current_job_id,
        'place_name': data['place_name'],  # Ganti dari url jadi place_name
        'filter_rating': filter_rating,
        'max_reviews': max_reviews,
        'output_formats': data['output_formats']
    }
    
    job_queue.put(job)
    jobs_status[current_job_id] = {
        'status': 'queued',
        'message': 'Menunggu antrian...',
        'progress': 0,
        'place_name': data['place_name']
    }
    
    print(f"\n[API] Job #{current_job_id} added: {data['place_name']}")
    
    return jsonify({
        'success': True,
        'job_id': current_job_id,
        'message': 'Job ditambahkan'
    })

@app.route('/api/jobs_status')
def get_jobs_status():
    return jsonify(jobs_status)

@app.route('/api/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🗺️  GOOGLE MAPS SCRAPER")
    print("="*60)
    print("📍 http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)