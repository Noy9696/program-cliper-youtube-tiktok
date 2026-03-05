from serpapi import GoogleSearch
import json
import time

# ===== CONFIG =====
API_KEY = '549cecc301a42c18cb64c81760afbe05088983b56c9d1228605a1263da3d7512'

# ===== FUNGSI BANNER =====
def print_banner():
    print("=" * 80)
    print("           🗺️  GOOGLE MAPS REVIEW SCRAPER 🗺️")
    print("=" * 80)
    print()

# ===== FUNGSI INPUT =====
def get_user_input():
    print_banner()
    
    # 1. Input Nama Tempat
    print("📍 [1/3] NAMA TEMPAT")
    tempat = input("Masukkan nama tempat yang ingin di-scrape: ").strip()
    if not tempat:
        print("❌ Nama tempat tidak boleh kosong!")
        exit()
    print()
    
    # 2. Input Filter Rating
    print("⭐ [2/3] FILTER RATING")
    print("Pilih rating yang ingin diambil:")
    print("  1. Semua rating (1-5 bintang)")
    print("  2. Rating 5 bintang saja")
    print("  3. Rating 4 bintang saja")
    print("  4. Rating 3 bintang saja")
    print("  5. Rating 2 bintang saja")
    print("  6. Rating 1 bintang saja")
    print("  7. Rating 4-5 bintang (positif)")
    print("  8. Rating 1-3 bintang (negatif)")
    
    pilihan_rating = input("Pilih (1-8): ").strip()
    
    # Mapping pilihan ke filter rating
    rating_filters = {
        '1': None,  # Semua rating
        '2': [5],
        '3': [4],
        '4': [3],
        '5': [2],
        '6': [1],
        '7': [4, 5],
        '8': [1, 2, 3]
    }
    
    filter_rating = rating_filters.get(pilihan_rating, None)
    print()
    
    # 3. Input Jumlah Review
    print("📝 [3/3] JUMLAH REVIEW")
    print("Pilih jumlah review yang ingin diambil:")
    print("  1. Semua review yang tersedia")
    print("  2. Tentukan jumlah sendiri")
    
    pilihan_jumlah = input("Pilih (1-2): ").strip()
    
    if pilihan_jumlah == '2':
        try:
            jumlah_review = int(input("Masukkan jumlah review: "))
            if jumlah_review <= 0:
                print("❌ Jumlah harus lebih dari 0!")
                exit()
        except ValueError:
            print("❌ Input harus berupa angka!")
            exit()
    else:
        jumlah_review = None  # Ambil semua
    
    print()
    return tempat, filter_rating, jumlah_review

# ===== FUNGSI SCRAPING TEMPAT =====
def scrape_place(tempat):
    print("🔍 Mencari data tempat...")
    params_place = {
        'api_key': API_KEY,
        'engine': 'google_maps',
        'q': tempat,
        'hl': 'id'
    }
    
    search = GoogleSearch(params_place)
    place_results = search.get_dict()
    
    if 'place_results' not in place_results:
        print("❌ Tempat tidak ditemukan!")
        return None
    
    place_data = place_results['place_results']
    
    print(f"✅ Tempat ditemukan: {place_data.get('title')}")
    print(f"   Rating: {place_data.get('rating')} ⭐")
    print(f"   Total Review: {place_data.get('reviews')}")
    print(f"   Data ID: {place_data.get('data_id')}")
    print()
    
    return place_data

# ===== FUNGSI SCRAPING REVIEWS =====
def scrape_reviews(data_id, filter_rating=None, max_reviews=None):
    print(f"📝 Mengambil reviews...")
    if filter_rating:
        print(f"   🔍 Filter: Rating {filter_rating}")
    if max_reviews:
        print(f"   🎯 Target: {max_reviews} reviews")
    else:
        print(f"   🎯 Target: Semua reviews")
    print()
    
    all_reviews = []
    next_page_token = None
    page = 1
    
    while True:
        # Cek apakah sudah mencapai target
        if max_reviews and len(all_reviews) >= max_reviews:
            print(f"   ✓ Target {max_reviews} reviews tercapai!")
            break
        
        print(f"   → Halaman {page}...")
        
        params_reviews = {
            'api_key': API_KEY,
            'engine': 'google_maps_reviews',
            'data_id': data_id,
            'hl': 'id',
            'sort_by': 'qualityScore'
        }
        
        if next_page_token:
            params_reviews['next_page_token'] = next_page_token
        
        search_reviews = GoogleSearch(params_reviews)
        reviews_results = search_reviews.get_dict()
        
        if 'reviews' in reviews_results:
            reviews = reviews_results['reviews']
            
            # Filter berdasarkan rating jika ada
            if filter_rating:
                reviews = [r for r in reviews if r.get('rating') in filter_rating]
            
            all_reviews.extend(reviews)
            print(f"   ✓ Dapat {len(reviews)} reviews (Total: {len(all_reviews)})")
        else:
            print("   ℹ Tidak ada reviews lagi")
            break
        
        # Cek halaman berikutnya
        if 'serpapi_pagination' in reviews_results and 'next_page_token' in reviews_results['serpapi_pagination']:
            next_page_token = reviews_results['serpapi_pagination']['next_page_token']
            page += 1
            time.sleep(1)
        else:
            print("   ℹ Sudah halaman terakhir")
            break
    
    # Potong sesuai max_reviews jika ada
    if max_reviews:
        all_reviews = all_reviews[:max_reviews]
    
    return all_reviews

# ===== FUNGSI TAMPILKAN HASIL =====
def display_results(place_data, reviews):
    print()
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
    print(f"REVIEWS ({len(reviews)} reviews)")
    print("=" * 80)
    
    for i, review in enumerate(reviews, 1):
        rating = review.get('rating', 0)
        rating_int = int(rating) if rating else 0
        
        print(f"\n[{i}] {review.get('user', {}).get('name', 'Anonymous')}")
        print(f"    Rating: {'⭐' * rating_int} ({rating})")
        print(f"    Tanggal: {review.get('date', '-')}")
        print(f"    Review: {review.get('snippet', '-')}")
        print(f"    Likes: {review.get('likes', 0)}")

# ===== FUNGSI SIMPAN KE JSON =====
def save_to_json(place_data, reviews, filter_rating):
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
        'filter': {
            'rating': filter_rating if filter_rating else 'Semua',
            'jumlah_diambil': len(reviews)
        },
        'reviews': [
            {
                'nama': r.get('user', {}).get('name', 'Anonymous'),
                'rating': r.get('rating'),
                'tanggal': r.get('date'),
                'review': r.get('snippet'),
                'likes': r.get('likes', 0)
            }
            for r in reviews
        ]
    }
    
    # Nama file
    safe_filename = place_data.get('title', 'tempat').replace(' ', '_').replace('/', '_')
    
    if filter_rating:
        rating_str = '_'.join(map(str, filter_rating))
        filename = f'hasil_{safe_filename}_rating{rating_str}.json'
    else:
        filename = f'hasil_{safe_filename}_semua_rating.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return filename

# ===== MAIN PROGRAM =====
def main():
    try:
        # 1. Input dari user
        tempat, filter_rating, jumlah_review = get_user_input()
        
        # 2. Scrape data tempat
        place_data = scrape_place(tempat)
        if not place_data:
            return
        
        data_id = place_data.get('data_id')
        
        # 3. Scrape reviews
        reviews = scrape_reviews(data_id, filter_rating, jumlah_review)
        
        print()
        print(f"✅ Berhasil mengambil {len(reviews)} reviews!")
        print()
        
        # 4. Tampilkan hasil
        display_results(place_data, reviews)
        
        # 5. Simpan ke JSON
        filename = save_to_json(place_data, reviews, filter_rating)
        
        print()
        print("=" * 80)
        print(f"✅ Data berhasil disimpan ke file: {filename}")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n❌ Program dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
