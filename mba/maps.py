from serpapi import GoogleSearch
import json
import time

# ===== CONFIG =====
API_KEY = '549cecc301a42c18cb64c81760afbe05088983b56c9d1228605a1263da3d7512'
TEMPAT = 'Best Motor Jatimulyo'
JUMLAH_REVIEW = 50

# ===== STEP 1: Ambil Data Tempat =====
print("🔍 Mencari data tempat...")
params_place = {
    'api_key': API_KEY,
    'engine': 'google_maps',
    'q': TEMPAT,
    'hl': 'id'
}

search = GoogleSearch(params_place)
place_results = search.get_dict()

# Cek apakah berhasil
if 'place_results' not in place_results:
    print("❌ Tempat tidak ditemukan!")
    exit()

place_data = place_results['place_results']
data_id = place_data.get('data_id')
place_id = place_data.get('place_id')

print(f"✅ Tempat ditemukan: {place_data.get('title')}")
print(f"   Rating: {place_data.get('rating')} ({place_data.get('reviews')} reviews)")
print(f"   Data ID: {data_id}")
print()

# ===== STEP 2: Ambil Reviews =====
print(f"📝 Mengambil {JUMLAH_REVIEW} reviews...")

all_reviews = []
next_page_token = None
page = 1

while len(all_reviews) < JUMLAH_REVIEW:
    print(f"   → Halaman {page}...")
    
    params_reviews = {
        'api_key': API_KEY,
        'engine': 'google_maps_reviews',
        'data_id': data_id,
        'hl': 'id',
        'sort_by': 'qualityScore'
    }
    
    # Tambahkan token untuk halaman berikutnya
    if next_page_token:
        params_reviews['next_page_token'] = next_page_token
    
    search_reviews = GoogleSearch(params_reviews)
    reviews_results = search_reviews.get_dict()
    
    # Ambil reviews dari halaman ini
    if 'reviews' in reviews_results:
        reviews = reviews_results['reviews']
        all_reviews.extend(reviews)
        print(f"   ✓ Dapat {len(reviews)} reviews (Total: {len(all_reviews)})")
    else:
        print("   ⚠ Tidak ada reviews lagi")
        break
    
    # Cek apakah ada halaman berikutnya
    if 'serpapi_pagination' in reviews_results and 'next_page_token' in reviews_results['serpapi_pagination']:
        next_page_token = reviews_results['serpapi_pagination']['next_page_token']
        page += 1
        time.sleep(1)  # Jeda 1 detik agar tidak kena rate limit
    else:
        print("   ℹ Sudah halaman terakhir")
        break

# Potong hanya sesuai JUMLAH_REVIEW
all_reviews = all_reviews[:JUMLAH_REVIEW]

print()
print(f"✅ Berhasil mengambil {len(all_reviews)} reviews!")
print()

# ===== STEP 3: Tampilkan Hasil =====
print("=" * 80)
print(f"INFORMASI TEMPAT: {place_data.get('title')}")
print("=" * 80)
print(f"Rating       : {place_data.get('rating')} ⭐")
print(f"Total Review : {place_data.get('reviews')}")
print(f"Alamat       : {place_data.get('address')}")
print(f"Telepon      : {place_data.get('phone', '-')}")
print(f"Website      : {place_data.get('website', '-')}")
print()

print("=" * 80)
print(f"REVIEWS ({len(all_reviews)} reviews)")
print("=" * 80)

for i, review in enumerate(all_reviews, 1):
    # Konversi rating ke integer untuk bintang
    rating = review.get('rating', 0)
    rating_int = int(rating) if rating else 0
    
    print(f"\n[{i}] {review.get('user', {}).get('name', 'Anonymous')}")
    print(f"    Rating: {'⭐' * rating_int} ({rating})")
    print(f"    Tanggal: {review.get('date', '-')}")
    print(f"    Review: {review.get('snippet', '-')}")
    print(f"    Likes: {review.get('likes', 0)}")

# ===== STEP 4: Simpan ke File JSON =====
output_data = {
    'tempat': {
        'nama': place_data.get('title'),
        'rating': place_data.get('rating'),
        'total_reviews': place_data.get('reviews'),
        'alamat': place_data.get('address'),
        'telepon': place_data.get('phone'),
        'website': place_data.get('website'),
        'koordinat': place_data.get('gps_coordinates')
    },
    'reviews': [
        {
            'nama': r.get('user', {}).get('name', 'Anonymous'),
            'rating': r.get('rating'),
            'tanggal': r.get('date'),
            'review': r.get('snippet'),
            'likes': r.get('likes', 0)
        }
        for r in all_reviews
    ]
}

# Nama file berdasarkan nama tempat
safe_filename = place_data.get('title', 'tempat').replace(' ', '_').replace('/', '_')
filename = f'hasil_scraping_{safe_filename}.json'

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print()
print("=" * 80)
print(f"✅ Data berhasil disimpan ke file: {filename}")
print("=" * 80)