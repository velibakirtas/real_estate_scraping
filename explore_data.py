import json
import pandas as pd
import re

# Dosya Yolu
FILE_PATH = 'response.json'

# def clean_price(price_str):
#     """Fiyat stringini temizler ve float'a çevirir."""
#     if not price_str: return None
#     # Sembolleri ve binlik ayıraçlarını temizle
#     clean = price_str.replace('₺', '').replace('TL', '').replace('.', '').replace(',', '.').strip()
#     try:
#         return float(clean)
#     except:
#         return None


print(f"--- VERİ KEŞİF MODU: {FILE_PATH} ---")
OUTPUT_CSV = "output.csv"

try:
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Hata: response.json dosyası bulunamadı.")
    

# Veri yoluna iniyoruz
try:
    # results = data['data']['presentation']['staysSearch']['results']['searchResults']
    map_results = data['data']['presentation']['staysSearch']['mapResults']["staysInViewport"]
    map_search_results = data['data']['presentation']['staysSearch']['mapResults']['mapSearchResults']
except KeyError:
    print("JSON yapısı beklenildiği gibi değil.")


extracted_data = []

i=1
for result, metadata_result in zip(map_search_results, map_results):

    point_comments = result.get("avgRatingLocalized") 

    # Aşağıdaki veriler ilanlarda yer alan fiyatların misafir hangi misafir tipi ve kaç adet misafir olduğu bilgilerini verir. Bu sonuçlar arama kritlerlerine göre değişir. Çocuk, bebek ve evcil hayvan genellikle fiyatta değişikliğe sebep olmaz
    adults = result.get("listingParamOverrides").get("adults") 
    children = result.get("listingParamOverrides").get("children") 
    infants = result.get("listingParamOverrides").get("infants") 
    pets = result.get("listingParamOverrides").get("pets") 

    # İlanlarda rezervasyonlar çeşitli gün sayılarında olabiliyor. Aşağıdaki datalar en erken check-in tarihini ve sonrasındaki check-out tarihlerini verir
    checkin = result.get("listingParamOverrides").get("checkin")
    checkout = result.get("listingParamOverrides").get("checkout")

    discounted_price = result.get("structuredDisplayPrice").get("primaryLine").get("discountedPrice") 
    original_price = result.get("structuredDisplayPrice").get("primaryLine").get("originalPrice") 
    

    days = result.get("structuredDisplayPrice").get("primaryLine").get("qualifier") 
    
    badges = result.get("badges")
    if len(badges)>0:
        badge_type = badges[0].get("loggingContext").get("badgeType")
    else:
        badge_type = None


    title = result.get("title")
    subtitle = result.get("subtitle")

    latitude = result.get("demandStayListing").get("location").get("coordinate").get("latitude")
    longitude = result.get("demandStayListing").get("location").get("coordinate").get("longitude")

    id = metadata_result.get("listingId")
    state = metadata_result.get("pinState")

    row = {
    "point_comments": point_comments,
    "adults": adults,
    "children": children,
    "infants": infants,
    "pets": pets,
    "checkin": checkin,
    "checkout": checkout,
    "discounted_price": discounted_price,
    "original_price": original_price,
    "days": days,
    "badge_type": badge_type,
    "title": title,
    "subtitle": subtitle,
    "latitude": latitude,
    "longitude": longitude,
    "id": "https://www.airbnb.com.tr/rooms/" + id,
    "state": state
    }

    for line in result.get("structuredContent").get("secondaryLine"):
        date_range_type = line.get("type")
        date_range_body = line.get("body")
        row["date_range_type"] = date_range_type
        row["date_range_body"] = date_range_body


    for line in result.get("structuredContent").get("primaryLine"):
        bed_info_type = line.get("type")
        bed_info_body = line.get("body")
        row["bed_info_type"] = bed_info_type
        row["bed_info_body"] = bed_info_body

    extracted_data.append(row)
    i+=1

df = pd.DataFrame(extracted_data)
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    






    





    # result.get("avgRatingLocalized") -> ev sahibi puanı ve kaç yorum barındırdığı bilgisi string ile tutulur


    # Aşağıdaki veriler ilanlarda yer alan fiyatların misafir hangi misafir tipi ve kaç adet misafir olduğu bilgilerini verir. Bu sonuçlar arama kritlerlerine göre değişir. Çocuk, bebek ve evcil hayvan genellikle fiyatta değişikliğe sebep olmaz
    # result.get("listingParamOverrides").get("adults") -> Yetişkin misafir sayısını verir (int)
    # result.get("listingParamOverrides").get("children") -> çocuk misafir sayısını verir (int)
    # result.get("listingParamOverrides").get("infants") -> bebek misafir sayısını verir (int)
    # result.get("listingParamOverrides").get("pets") -> evcil hayvan misafir sayısını verir (int)

    # İlanlarda rezervasyonlar çeşitli gün sayılarında olabiliyor. Aşağıdaki datalar en erken check-in tarihini ve sonrasındaki check-out tarihlerini verir
    # result.get("listingParamOverrides").get("checkin")
    # result.get("listingParamOverrides").get("checkout")

    # result.get("structuredDisplayPrice").get("primaryLine").get("discountedPrice") -> İndirimli fiyat bilgisini verir (str)
    # result.get("structuredDisplayPrice").get("primaryLine").get("originalPrice") -> İndirimsiz fiyat bilgisini verir (str)
    # result.get("structuredDisplayPrice").get("primaryLine").get("qualifier") -> Fiyatın kaç gün için geçerli olduğu bilgisni verir (str) (örn: (5 gün için))

    # result.get("structuredDisplayPrice").get("explanationData").get("priceDetails")[1].get("content") -> Bu bilgi string bir metin veriyor ama henüz ne ile ilgili olduğu tespit edilemedi. Diğer datalarla doğrulaması yapılacak
    # result.get("badges")[0].get("loggingContext").get("badgeType") -> Ev sahiplerinin sahip olduğu rozetin bilgisini verir  [str or None]

    # result.get("title") -> İlan başlığı bilgisini tutar (str)
    # result.get("subtitle") -> Başlık altında yer alan altyazı metnini tutar (str)

    # results.get("structuredContent").get("SecondaryLine") -> Liste halinde metadatalar tutar. Bu sebeple iterasyonla ulaşılmalıdır.
        #  i.get("type") -> Arama sonuçlarında görüntülenen tarih aralığı bilgisi için bir metadatadır.
        # i.get("body") -> Aramada görüntülenen tarih aralığını string olarak tutar. 

    # results.get("structuredContent").get("primaryLine") -> Liste halinde metadatalar tutar. Bu sebeple iterasyonla ulaşılmalıdır.
        # i.get("body") -> Arama sonucunda yatak odası ve yatak sayıları gibi bilgileri string olarak tutar.
        #  i.get("type") -> Arama sonuçlarında görüntülenen yatak(odası) bilgisi için bir metadatadır.

    # result.get("demandStayListing").get("location").get("coordinate").get("latitude") -> Enlem bilgisini verir (float)
    # result.get("demandStayListing").get("location").get("coordinate").get("longitude") -> Boylam bilgisini verir (float)

    # NOT: badges key detaylarında kalındı

    # for result in mapresults:

    # result.get("listingId") -> harita görünümünde listelenen ilanların id bilgilerini tutar. Bu id bilgileri url ile kullanılarak direkt ev/oda ilanı sayfasına gidilebilir
    # resul.get("pinState") -> Bir metadatadır fakat henüz neyi düzenlediğini anlayamadım. "FULL_PIN" ve "MINI_PIN" olmak üzere iki değer alır.
