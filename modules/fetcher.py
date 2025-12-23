import requests
import json
import os
import copy
from datetime import datetime

# Cookie ve Headerları buraya ekle (veya ayrı bir config dosyasından çek)
COOKIE = "_user_attributes=%7B%22curr%22%3A%22TRY%22%7D; bev=1766404639_EAZDRjYmZhNzMzNG; everest_cookie=1766404639.EAMzhiZDg0ZWM1OTMwNT.KyhaXopnIF_HAlO1WkyZ-hvLppNJcwcI921xlH9K_oA; cdn_exp_fff04c39fb7a140b7=treatment; cdn_exp_21f7dc94ce371d723=control; previousTab=%7B%22id%22%3A%223ecb1b65-34bc-4f56-a3db-72802ede796c%22%7D; jitney_client_session_id=e05c2b0e-333a-495a-a854-fbab3d88b43c; jitney_client_session_created_at=1766404641.401; _cci=cban%3Aac-c88c41e8-57eb-488b-b48a-58d7407217b0; _ccv=cban%3A0_183215%3D1%2C0_200000%3D1%2C0_183345%3D1%2C0_183243%3D1%2C0_183216%3D1%2C0_179751%3D1%2C0_200003%3D1%2C0_200005%3D1%2C0_179754%3D1%2C0_179750%3D1%2C0_179737%3D1%2C0_179744%3D1%2C0_179739%3D1%2C0_179743%3D1%2C0_179749%3D1%2C0_200012%3D1%2C0_200011%3D1%2C0_183217%3D1%2C0_183219%3D1%2C0_183096%3D1%2C0_179747%3D1%2C0_179740%3D1%2C0_179752%3D1%2C0_183241%3D1%2C0_200007%3D1%2C0_183346%3D1%2C0_183095%3D1%2C0_210000%3D1%2C0_210001%3D1%2C0_210002%3D1%2C0_210003%3D1%2C0_210004%3D1%2C0_210010%3D1%2C0_210012%3D1%2C0_210008%3D1%2C0_210016%3D1%2C0_210017%3D1%2C0_210018%3D1%2C0_210020%3D1%2C0_210021%3D1%2C0_210022%3D1; tzo=180; isLowEndDevice=1; _gcl_au=1.1.1461386783.1766404762; _ga=GA1.1.1088678569.1766404762; FPID=FPID2.3.%2BPHrxasgwmXd6Keb1%2FFiLrnMx4QAiLlP6%2F9g16ja9WA%3D.1766404762; FPLC=%2B1fbWVgSj9PEQtfcC8StIMclxq0Xc5y3IabZS3fnFu2umB627NciEQ8nF2kKgkTTTES19GdsDY33uW3ycdRB%2FAAYxkzaUfL8181U2oOx%2BHzol8ZuNySNqsDeJ4jDjg%3D%3D; FPAU=1.1.1461386783.1766404762; frmfctr=compact; cfrmfctr=MOBILE; cbkp=1; ak_bmsc=B246D4B038C0F8BB372614D72E64B2B7~000000000000000000000000000000~YAAQNsETAnf6HSebAQAAjYdfRh5xXsOKzZAzh5wMNRYQ7VUB4iNK7+LiVJGRjT5mEH+Mxig+cmJ/nYgGqmP6QuAmlZB/0o8qSGuLSHFW1E+2CdxqcjBNRS4WfFbOgum90nehAtm1CALZs2IwOnj/gFc1Ky2pTsXO9JEQR7Ac2Cbis0NxpgADm2C1067IXo3/toiVd1ubYCvLSEpI3G1PA2tfDQtgnm69TYzoauVMz9bW22409rR9+4MGoOE+ER/th0kD+jq3AN6/IRXMTE+h52IyI6ondPt9r4ExNZIwkefVDV4hZ1dNmCVOVOj2CkA2eLhICYGEPNyaYmw8/zBXY6037OZWA4jvujg3yI6PoYc56up8YOKeNqcmPttUscW57d1x4RE=; jitney_client_session_updated_at=1766412228.156; bm_sv=8C819C54A1EBAC70718AB1E8A23417C8~YAAQNsETAlL8HSebAQAAa5tfRh6dwMaemWhsJpepBq7lFMx2ASnpIO2idszZ/RrGM2VIBDKnTPyzBuSbNeuT5dZd7wZCCFBZ+xlRwimC9TGIaVazbENQkyDCAi6cXOlqhfJfDoS1RCfoRWUjE4gaNH59tU8EGv0vRoW4n64vEGBoOEXzuEBUCtxDnLNrzMTZ2iMIsE7tAWLbjJ0qS8qlqxUvTW/vvQpvWpyvzsNgFtfd7vSvpOHW6Bl1ymh5h6+rId+v~1; _ga_2P6Q8PGG16=GS2.1.s1766404761$o1$g1$t1766412229$j60$l0$h0; datadome=wVIsxRtomjwQ1PcQA1xRbF093nKGgnLywOkre7_sqtxkv5lkXNGyAnmgYOY87bQIpXcYzQCOGzrIQTzMseWYWv48P5Ef9YzrtcHdSZndpAr1tuLgWZGkb_ijuysY1NG4W7_SRWsCm070Vmh4YKrd6l"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
HEADERS = {
    'content-type': 'application/json',
    'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20', 
    'user-agent': USER_AGENT,
    'cookie': COOKIE
}

URL = "https://www.airbnb.com.tr/api/v3/StaysSearch/d9ab2c7e443b50fdce5cdcb69d4f7e7626dbab1609c981565a6c4bdbb04546e3"

BASE_PAYLOAD = {
    "operationName": "StaysSearch",
    "variables": {
        "staysSearchRequest": {
            "metadataOnly": False,
            "requestedPageType": "STAYS_SEARCH",
            "searchType": "user_map_move",
            "treatmentFlags": [
                "feed_map_decouple_m11_treatment",
                "recommended_amenities_2024_treatment_b",
                "filter_redesign_2024_treatment",
                "filter_reordering_2024_roomtype_treatment",
                "p2_category_bar_removal_treatment",
                "selected_filters_2024_treatment",
                "recommended_filters_2024_treatment_b",
                "m13_search_input_phase2_treatment",
                "m13_search_input_services_enabled"
            ],
            "maxMapItems": 9999,
            "rawParams": [] # Burası aşağıda dolacak
        },
        "staysMapSearchRequestV2": {
            "metadataOnly": False,
            "requestedPageType": "STAYS_SEARCH",
            "searchType": "user_map_move",
            "treatmentFlags": [
                "feed_map_decouple_m11_treatment",
                "recommended_amenities_2024_treatment_b",
                "filter_redesign_2024_treatment",
                "filter_reordering_2024_roomtype_treatment",
                "p2_category_bar_removal_treatment",
                "selected_filters_2024_treatment",
                "recommended_filters_2024_treatment_b",
                "m13_search_input_phase2_treatment",
                "m13_search_input_services_enabled"
            ],
            "rawParams": [] # Burası aşağıda dolacak
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

# Değişmeyen filtreler (Senin payload dosyanla aynı)
# STATIC_PARAMS = [
#     {"filterName": "acpId", "filterValues": ["5fae73c9-778e-408f-9be8-1b9111499b24"]},
#     {"filterName": "cdnCacheSafe", "filterValues": ["false"]},
#     {"filterName": "channel", "filterValues": ["EXPLORE"]},
#     {"filterName": "datePickerType", "filterValues": ["calendar"]},
#     {"filterName": "flexibleTripLengths", "filterValues": ["one_week"]},
#     {"filterName": "itemsPerGrid", "filterValues": ["50"]}, # Veriyi artırmak için 18 yerine 50 yaptım
#     {"filterName": "mapToggle", "filterValues": ["true"]},
#     {"filterName": "monthlyEndDate", "filterValues": ["2026-04-01"]},
#     {"filterName": "monthlyLength", "filterValues": ["3"]},
#     {"filterName": "monthlyStartDate", "filterValues": ["2026-01-01"]},
#     {"filterName": "placeId", "filterValues": ["ChIJexVgWlG2yhQR6B1akfSarCI"]},
#     {"filterName": "priceFilterInputType", "filterValues": ["2"]},
#     {"filterName": "priceFilterNumNights", "filterValues": ["5"]},
#     {"filterName": "query", "filterValues": ["İstanbul, Türkiye"]},
#     {"filterName": "refinementPaths", "filterValues": ["/homes"]},
#     {"filterName": "screenSize", "filterValues": ["small"]},
#     {"filterName": "searchByMap", "filterValues": ["true"]},
#     {"filterName": "searchMode", "filterValues": ["regular_search"]},
#     {"filterName": "tabId", "filterValues": ["home_tab"]},
#     {"filterName": "version", "filterValues": ["1.8.3"]},
#     {"filterName": "zoomLevel", "filterValues": ["14"]} # Zoom seviyesi veri yoğunluğunu etkiler
# ]
STATIC_PARAMS = [
    {"filterName": "channel", "filterValues": ["EXPLORE"]},
    {"filterName": "itemsPerGrid", "filterValues": ["50"]},
    {"filterName": "mapToggle", "filterValues": ["true"]},
    {"filterName": "searchByMap", "filterValues": ["true"]},
    {"filterName": "searchMode", "filterValues": ["regular_search"]},
    {"filterName": "version", "filterValues": ["1.8.3"]}
    # {"filterName": "zoomLevel", "filterValues": ["14"]}
]

def save_raw_response(data, prefix="airbnb"):
    directory = "data/raw"
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/{prefix}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[KAYIT] Veri kaydedildi: {filename}")
    return filename

def build_params(ne_lat, ne_lng, sw_lat, sw_lng, checkin, checkout, adults, zoom_level):
    """Statik parametrelere dinamik koordinatları ekler."""
    # Listeyi kopyala ki orijinali bozulmasın
    current_params = copy.deepcopy(STATIC_PARAMS)
    
    # Koordinatları ekle
    current_params.append({"filterName": "neLat", "filterValues": [str(ne_lat)]})
    current_params.append({"filterName": "neLng", "filterValues": [str(ne_lng)]})
    current_params.append({"filterName": "swLat", "filterValues": [str(sw_lat)]})
    current_params.append({"filterName": "swLng", "filterValues": [str(sw_lng)]})

    if checkin and checkout:
        current_params.append({"filterName": "checkin", "filterValues": [checkin]})
        current_params.append({"filterName": "checkout", "filterValues": [checkout]})
        current_params.append({"filterName": "datePickerType", "filterValues": ["calendar"]})

    if adults:
         current_params.append({"filterName": "adults", "filterValues": [str(adults)]})

    if zoom_level:
        current_params.append({"filterName": "zoomLevel", "filterValues": [str(zoom_level)]})

    
    return current_params

def fetch_data(ne_lat, ne_lng, sw_lat, sw_lng, checkin=None, checkout=None, adults=1, zoom_level=14):
    # Base payload'un kopyasını al
    payload = copy.deepcopy(BASE_PAYLOAD)
    
    # Koordinatları içeren parametre listesini oluştur
    dynamic_params = build_params(ne_lat, ne_lng, sw_lat, sw_lng, checkin, checkout, adults,zoom_level)
    
    # Hem V1 hem V2 isteğine parametreleri göm (Airbnb ikisine de bakıyor)
    payload["variables"]["staysSearchRequest"]["rawParams"] = dynamic_params
    payload["variables"]["staysMapSearchRequestV2"]["rawParams"] = dynamic_params

    try:
        # URL parametreleri (Requests kütüphanesi params ile ekler)
        url_params = {
            'operationName': 'StaysSearch',
            'locale': 'tr',
            'currency': 'TRY'
        }
        
        response = requests.post(URL, headers=HEADERS, params=url_params, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Veri gerçekten geldi mi kontrol et
        # Genellikle data -> presentation altında olur.
        if data.get('data') is None:
            print("[UYARI] API 'data' alanı boş döndü. Cookie veya Parametre hatası olabilir.")
            print("Dönen Mesaj:", data)
            return None

        saved_path = save_raw_response(data)
        return saved_path

    except Exception as e:
        print(f"[HATA] Fetcher hatası: {e}")
        if 'response' in locals():
            print("Status Code:", response.status_code)
            print("Response Text:", response.text[:200]) # Hatanın başını gör
        return None