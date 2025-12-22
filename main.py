from modules import fetcher, parser
import os
import time
import sys

def get_input(prompt_text, default=None):
    """Kullanıcıdan veri alır, boş bırakırsa varsayılanı döner."""
    if default:
        user_input = input(f"{prompt_text} (Varsayılan: {default}): ")
        return user_input if user_input.strip() else default
    else:
        return input(f"{prompt_text}: ")
    
def get_float_input(prompt_text):
    """Kullanıcıdan mutlaka float (koordinat) değeri ister."""
    while True:
        val = input(f"{prompt_text}: ")
        try:
            return float(val.replace(',', '.')) # Virgül girerse noktaya çevir
        except ValueError:
            print("Lütfen geçerli bir sayısal koordinat girin!")

def main():
    print("###############################################")
    print("###   AIRBNB DİNAMİK VERİ TOPLAMA ARACI   ###")
    print("###############################################\n")

    # --- 1. ADIM: Tarih Bilgisi ---
    print("--- TARİH SEÇİMİ ---")
    checkin = get_input("Giriş Tarihi (YYYY-AA-GG)", "2024-06-01")
    checkout = get_input("Çıkış Tarihi (YYYY-AA-GG)", "2024-06-06")
    
    # --- 2. ADIM: Misafir Bilgisi ---
    print("\n--- MİSAFİR BİLGİSİ ---")
    adults = get_input("Yetişkin Sayısı", "1")
    
    # --- 3. ADIM: Koordinat / Bölge Bilgisi ---
    print("\n--- BÖLGE VE KOORDİNATLAR ---")
    try:
        region_count = int(get_input("Kaç farklı dikdörtgen bölge tarayacaksınız?", "1"))
    except:
        region_count = 1

    regions = []
    for i in range(region_count):
        print(f"\n[{i+1}. BÖLGE TANIMLAMA]")
        print("İpucu: Haritada sağ üst köşe (NE) ve sol alt köşe (SW) gereklidir.")
        
        ne_lat = get_float_input(f"Bölge {i+1} - Kuzey Doğu (NE) ENLEM (Lat)")
        ne_lng = get_float_input(f"Bölge {i+1} - Kuzey Doğu (NE) BOYLAM (Lng)")
        sw_lat = get_float_input(f"Bölge {i+1} - Güney Batı (SW) ENLEM (Lat)")
        sw_lng = get_float_input(f"Bölge {i+1} - Güney Batı (SW) BOYLAM (Lng)")

        zoom_level = get_input(f"Bölge {i+1} - Zoom Seviyesi (Varsayılan: 14)")
        
        regions.append((ne_lat, ne_lng, sw_lat, sw_lng,zoom_level))

    # --- 4. ADIM: Onay ve Başlatma ---
    print("\n" + "="*40)
    print(f"Toplam {len(regions)} bölge taranacak.")
    print(f"Tarih: {checkin} - {checkout}")
    print(f"Misafir: {adults} Yetişkin")
    print("="*40)
    
    confirm = input("İşlemi başlatmak için 'e' yazıp Enter'a basın: ")
    if confirm.lower() != 'e':
        print("İşlem iptal edildi.")
        sys.exit()

    print("\n>>> SCRAPING BAŞLIYOR...\n")
    
    successful_fetches = 0
    for idx, (ne_lat, ne_lng, sw_lat, sw_lng,zoom_level) in enumerate(regions):
        print(f"İstek gönderiliyor: Bölge {idx+1}/{len(regions)}...")
        
        path = fetcher.fetch_data(
            ne_lat=ne_lat, ne_lng=ne_lng, 
            sw_lat=sw_lat, sw_lng=sw_lng,
            checkin=checkin, checkout=checkout,
            adults=adults, zoom_level=zoom_level
        )
        
        if path:
            successful_fetches += 1
            # Bot koruması için bekleme
            time.sleep(2)
        else:
            print(f"UYARI: Bölge {idx+1} için veri alınamadı!")

    # --- 5. ADIM: Veri İşleme (Parsing) ---
    if successful_fetches > 0:
        print("\n>>> PARSE İŞLEMİNE GEÇİLİYOR...")
        df = parser.process_all_raw_files()
        
        if df is not None and not df.empty:
            output_file = f"data/processed/search_result_{checkin}_{checkout}.csv"
            # Klasör kontrolü
            if not os.path.exists("data/processed"):
                os.makedirs("data/processed")
                
            df.to_csv(output_file, index=False)
            print(f"\n[MUTLU SON] Tüm işlemler tamamlandı! 🎉")
            print(f"Toplam İlan: {len(df)}")
            print(f"Dosya Yolu: {output_file}")
            print(df[['title', 'price_numeric', 'rating_text']].head())
        else:
            print("Veri çekildi ama parse edilemedi.")
    else:
        print("Hiçbir bölgeden veri çekilemedi.")

if __name__ == "__main__":
    main()

# Test Coordinates
# #         (41.045, 29.005, 41.035, 28.995), # Bölge 1
# #         (41.020, 29.010, 41.010, 29.000)  # Bölge 2
