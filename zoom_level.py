import math
import requests
import json
import time
import random
import copy

# ==========================================
# 1. SETTINGS & CONFIG
# ==========================================
URL = "https://www.airbnb.com.tr/api/v3/StaysSearch/d9ab2c7e443b50fdce5cdcb69d4f7e7626dbab1609c981565a6c4bdbb04546e3"

HEADERS = {
    'content-type': 'application/json',
    'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20', 
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    # Cookie süreli olduğu için hata alırsan güncel cookie'yi buraya yapıştır
    'cookie': "_user_attributes=%7B%22curr%22%3A%22TRY%22%7D; bev=1766404639_EAZDRjYmZhNzMzNG; everest_cookie=1766404639.EAMzhiZDg0ZWM1OTMwNT.KyhaXopnIF_HAlO1WkyZ-hvLppNJcwcI921xlH9K_oA; datadome=wVIsxRtomjwQ1PcQA1xRbF093nKGgnLywOkre7_sqtxkv5lkXNGyAnmgYOY87bQIpXcYzQCOGzrIQTzMseWYWv48P5Ef9YzrtcHdSZndpAr1tuLgWZGkb_ijuysY1NG4W7_SRWsCm070Vmh4YKrd6l" 
}

BASE_PAYLOAD = {
    "operationName": "StaysSearch",
    "variables": {
        "staysSearchRequest": {
            "metadataOnly": False,
            "requestedPageType": "STAYS_SEARCH",
            "searchType": "user_map_move",
            "treatmentFlags": ["feed_map_decouple_m11_treatment", "recommended_amenities_2024_treatment_b", "filter_redesign_2024_treatment", "filter_reordering_2024_roomtype_treatment", "p2_category_bar_removal_treatment", "selected_filters_2024_treatment", "recommended_filters_2024_treatment_b", "m13_search_input_phase2_treatment", "m13_search_input_services_enabled"],
            "maxMapItems": 9999,
            "rawParams": [] 
        },
        "staysMapSearchRequestV2": {
            "metadataOnly": False,
            "requestedPageType": "STAYS_SEARCH",
            "searchType": "user_map_move",
            "treatmentFlags": ["feed_map_decouple_m11_treatment", "recommended_amenities_2024_treatment_b", "filter_redesign_2024_treatment", "filter_reordering_2024_roomtype_treatment", "p2_category_bar_removal_treatment", "selected_filters_2024_treatment", "recommended_filters_2024_treatment_b", "m13_search_input_phase2_treatment", "m13_search_input_services_enabled"],
            "rawParams": []
        },
        "isLeanTreatment": False,
        "aiSearchEnabled": False,
        "skipExtendedSearchParams": False
    },
    "extensions": {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "d9ab2c7e443b50fdce5cdcb69d4f7e7626dbab1609c981565a6c4bdbb04546e3"
        }
    }
}

STATIC_PARAMS = [
    {"filterName": "channel", "filterValues": ["EXPLORE"]},
    {"filterName": "itemsPerGrid", "filterValues": ["50"]},
    {"filterName": "mapToggle", "filterValues": ["true"]},
    {"filterName": "searchByMap", "filterValues": ["true"]},
    {"filterName": "searchMode", "filterValues": ["regular_search"]},
    {"filterName": "version", "filterValues": ["1.8.3"]},
    {"filterName": "checkin", "filterValues": ["2026-06-01"]}, 
    {"filterName": "checkout", "filterValues": ["2026-06-06"]}  
]

# ==========================================
# 2. THE GRID ALGORITHM
# ==========================================
class GridGenerator:
    def __init__(self, target_hectares=8):
        self.target_sq_meters = target_hectares * 10000
        self.side_length_meters = math.sqrt(self.target_sq_meters)

    def _meters_to_lat_degrees(self):
        return self.side_length_meters / 111111

    def _meters_to_lng_degrees(self, latitude):
        lat_radians = math.radians(latitude)
        meters_per_degree = 111111 * math.cos(lat_radians)
        return self.side_length_meters / meters_per_degree

    def generate_tiles(self, ne_lat, ne_lng, sw_lat, sw_lng):
        center_lat = (ne_lat + sw_lat) / 2
        lat_step = self._meters_to_lat_degrees()
        lng_step = self._meters_to_lng_degrees(center_lat)
        
        tiles = []
        current_lat = sw_lat
        while current_lat < ne_lat:
            current_lng = sw_lng
            while current_lng < ne_lng:
                tile_ne_lat = min(current_lat + lat_step, ne_lat)
                tile_ne_lng = min(current_lng + lng_step, ne_lng)
                
                tiles.append({
                    "ne_lat": round(tile_ne_lat, 6),
                    "ne_lng": round(tile_ne_lng, 6),
                    "sw_lat": round(current_lat, 6),
                    "sw_lng": round(current_lng, 6)
                })
                current_lng += lng_step
            current_lat += lat_step
        return tiles

# ==========================================
# 3. THE OPTIMIZER ENGINE (UPDATED)
# ==========================================
def run_global_zoom_test(wide_ne_lat, wide_ne_lng, wide_sw_lat, wide_sw_lng):
    # 1. Generate the Grid
    print("--- 1. Grid Oluşturuluyor ---")
    generator = GridGenerator(target_hectares=8)
    tiles = generator.generate_tiles(wide_ne_lat, wide_ne_lng, wide_sw_lat, wide_sw_lng)
    
    total_tiles = len(tiles)
    print(f"✅ Toplam {total_tiles} adet parça (tile) oluşturuldu.")
    if total_tiles == 0:
        print("❌ Hiç tile oluşturulamadı, koordinatları kontrol et.")
        return

    # 2. Define Zoom Levels to Test
    # Genelde 1-10 arası çok geniştir, 18+ çok yakındır. 2-15 arası ideal test aralığıdır.
    zoom_levels = [i for i in range(14, 22)] 
    
    results = {} # {zoom_level: total_listings_count}

    print("\n--- 2. Global Zoom Testi Başlıyor ---")
    print(f"ℹ️  Toplam İşlem Sayısı Tahmini: {len(zoom_levels) * total_tiles} istek.\n")

    for zoom in zoom_levels:
        print(f"🔵 Testing Zoom Level: {zoom}")
        zoom_total_listings = 0
        success_count = 0
        
        # O zoom seviyesi için tüm tile'ları gez
        for i, tile in enumerate(tiles):
            # Progress bar benzeri log
            print(f"\r   └── Tile {i+1}/{total_tiles} taranıyor...", end="")
            
            payload = copy.deepcopy(BASE_PAYLOAD)
            
            current_params = copy.deepcopy(STATIC_PARAMS)
            current_params.append({"filterName": "neLat", "filterValues": [str(tile['ne_lat'])]})
            current_params.append({"filterName": "neLng", "filterValues": [str(tile['ne_lng'])]})
            current_params.append({"filterName": "swLat", "filterValues": [str(tile['sw_lat'])]})
            current_params.append({"filterName": "swLng", "filterValues": [str(tile['sw_lng'])]})
            current_params.append({"filterName": "zoomLevel", "filterValues": [str(zoom)]})

            payload["variables"]["staysSearchRequest"]["rawParams"] = current_params
            payload["variables"]["staysMapSearchRequestV2"]["rawParams"] = current_params
            
            try:
                url_params = {'operationName': 'StaysSearch', 'locale': 'tr', 'currency': 'TRY'}
                response = requests.post(URL, headers=HEADERS, params=url_params, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    items = []
                    # Path 1
                    try:
                        items = data['data']['presentation']['staysSearch']['mapResults']['mapSearchResults']
                    except:
                        pass
                    
                    # Path 2 (Fallback)
                    if not items:
                        try:
                            items = data.get('data', {}).get('presentation', {}).get('staysSearch', {}).get('results', {}).get('searchResults', [])
                        except:
                            pass
                    
                    count = len(items) if items else 0
                    zoom_total_listings += count
                    success_count += 1
                else:
                    # Rate limit vs. durumunda çok log basmamak için sadece status code
                    pass 
                    
            except Exception as e:
                pass # Hata durumunda devam et

            # Rate Limit Koruması (Her tile arası bekleme)
            # Eğer tile sayısı çoksa burayı 0.5 - 1.5 arası yapabilirsin.
            time.sleep(random.uniform(1.0, 2.0))

        # Zoom döngüsü sonu raporu
        results[zoom] = zoom_total_listings
        print(f"\n   ✅ Zoom {zoom} Tamamlandı. Toplam Veri: {zoom_total_listings} (Başarılı İstek: {success_count}/{total_tiles})")
        print("-" * 40)
        
        # Her zoom level arası biraz daha uzun mola verelim
        time.sleep(3)

    # 4. Final Rapor
    print("\n\n==========================================")
    print("🏆 OPTİMİZASYON SONUÇLARI")
    print("==========================================")
    
    if results:
        # En çok veri getiren zoom değerini bul
        best_zoom = max(results, key=results.get)
        max_data = results[best_zoom]
        
        print(f"{'Zoom Level':<12} | {'Toplam İlan'}")
        print("-" * 25)
        for z, c in results.items():
            mark = "⭐" if z == best_zoom else ""
            print(f"{z:<12} | {c} {mark}")
            
        print(f"\n✅ Önerilen İdeal Zoom Seviyesi: {best_zoom}")
        print(f"📈 Bu seviyede toplam {max_data} adet veri yakalandı.")
    else:
        print("❌ Hiçbir veri alınamadı. Cookie veya header'ları kontrol edin.")

if __name__ == "__main__":
    # Test Alanı (İstanbul - Nispeten küçük bir alan seçildi test hızlı bitsin diye)
    # Gerçek taramada burayı genişletebilirsin.
    WIDE_NE_LAT = 41.045
    WIDE_NE_LNG = 29.005
    WIDE_SW_LAT = 41.035
    WIDE_SW_LNG = 28.995

    run_global_zoom_test(WIDE_NE_LAT, WIDE_NE_LNG, WIDE_SW_LAT, WIDE_SW_LNG)