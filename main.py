from modules import fetcher, parser
import os
import time

def run_pipeline():
    print("--- PIPELINE BAŞLIYOR ---")
    
    # 1. ADIM: Veri Toplama (Scraping)
    # Örnek: İstanbul'da 2 farklı noktaya istek atalım
    coordinates_to_scan = [
        (41.045, 29.005, 41.035, 28.995), # Bölge 1
        (41.020, 29.010, 41.010, 29.000)  # Bölge 2
    ]
    
    print("1. Veri toplama aşaması...")
    for coords in coordinates_to_scan:
        ne_lat, ne_lng, sw_lat, sw_lng = coords
        
        # Fetcher modülünü çağır
        saved_file = fetcher.fetch_data(ne_lat, ne_lng, sw_lat, sw_lng)
        
        if saved_file:
            # Bot korumasına takılmamak için bekleme süresi
            time.sleep(3) 
    
    # 2. ADIM: Veri İşleme (Parsing)
    print("\n2. Veri işleme aşaması...")
    
    # Parser modülünü çağır (klasördeki her şeyi işler)
    df = parser.process_all_raw_files()
    
    if df is not None and not df.empty:
        # Sonucu kaydet
        output_path = "data/processed/istanbul_ilanlari_final.csv"
        if not os.path.exists("data/processed"):
            os.makedirs("data/processed")
            
        df.to_csv(output_path, index=False)
        print(f"\n[BAŞARILI] Toplam {len(df)} satır veri işlendi ve şuraya kaydedildi: {output_path}")
        print(df.head())
    else:
        print("\n[UYARI] Hiç veri elde edilemedi.")

if __name__ == "__main__":
    run_pipeline()