import json
import pandas as pd
import re
import os
from pathlib import Path



def parse_single_file(filepath):
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Hata: response.json dosyası bulunamadı.")
        
    # Veri yoluna iniyoruz
    try:
        map_results = data['data']['presentation']['staysSearch']['mapResults']["staysInViewport"]
        price_datas = data['data']['presentation']['staysSearch']['results']['searchResults']
        map_search_results = data['data']['presentation']['staysSearch']['mapResults']['mapSearchResults']
    except KeyError:
        print("JSON yapısı beklenildiği gibi değil.")

    extracted_data = []

    i=1
    for result, metadata_result,price in zip(map_search_results, map_results, price_datas):

        try:
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
            original_price = result.get("structuredDisplayPrice").get("primaryLine").get("originalPrice") or result.get("structuredDisplayPrice").get("primaryLine").get("price")
            
            
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
            "badge_type": badge_type,
            "title": title,
            "subtitle": subtitle,
            "latitude": latitude,
            "longitude": longitude,
            "id": "https://www.airbnb.com.tr/rooms/" + id,
            }


            j = 1
            for line in result.get("structuredContent").get("primaryLine"):
                bed_info_body = line.get("body")
                row[f"bed_info_body_{j}"] = bed_info_body
                # print(f"bed_info_body_{i} = {bed_info_body}")
                j+=1
            extracted_data.append(row)

            i+=1
        except Exception as e:
            print(f"A problem has occurred: {e}")
    return extracted_data

def process_all_raw_files():
    all_data = []
    raw_dir=Path("data/raw")
    files = list(raw_dir.glob("*.json"))

    for filename in files:
        filepath = filename
        linstings = parse_single_file(filepath)
        all_data.extend(linstings)
        

    df = pd.DataFrame(all_data)
    return df

