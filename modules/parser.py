import json
import pandas as pd
import os

def parse_single_file(filepath):
    """Belirtilen JSON dosyasını okur ve list of dict döner."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parsed_listings = []
    
    try:
        results = data.get('data', {}).get('presentation', {}).get('staysSearch', {}).get('results', {}).get('searchResults', [])
        
        for item in results:
            demand_stay = item.get('demandStayListing', {})
            price_info = item.get('structuredDisplayPrice', {}).get('primaryLine', {})
            
            # Fiyat parse mantığı
            price_str = price_info.get('price') or price_info.get('discountedPrice')
            price_val = None
            if price_str:
                clean_price = price_str.replace('₺', '').replace('.', '').replace(',', '.').strip()
                try:
                    price_val = float(clean_price)
                except: pass

            listing = {
                'id': demand_stay.get('id'),
                'title': item.get('nameLocalized', {}).get('localizedStringWithTranslationPreference'),
                'lat': demand_stay.get('location', {}).get('coordinate', {}).get('latitude'),
                'lng': demand_stay.get('location', {}).get('coordinate', {}).get('longitude'),
                'price': price_val,
                'rating_text': item.get('avgRatingLocalized'),
                'source_file': os.path.basename(filepath) # Hangi dosyadan geldiğini takip etmek için
            }
            parsed_listings.append(listing)
            
    except Exception as e:
        print(f"[PARSE HATASI] {filepath} dosyasında hata: {e}")
        
    return parsed_listings

def process_all_raw_files():
    """data/raw klasöründeki TÜM dosyaları işler ve tek bir DataFrame döner."""
    all_data = []
    raw_dir = "data/raw"
    
    if not os.path.exists(raw_dir):
        print("Raw klasörü bulunamadı.")
        return None

    files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
    print(f"Toplam {len(files)} dosya işlenecek...")
    
    for filename in files:
        filepath = os.path.join(raw_dir, filename)
        listings = parse_single_file(filepath)
        all_data.extend(listings)
        
    df = pd.DataFrame(all_data)
    
    return df