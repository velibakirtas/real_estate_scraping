import pandas as pd
import numpy as np
import re
from pathlib import Path


def clean_currency(value):
    if pd.isna(value):
        return None
    
    value_str = str(value)

    clean_str = value_str.replace("₺","").replace("TL","").strip()
    clean_str = clean_str.replace(".","").replace(",",".")

    try:
        return float(clean_str)
    except ValueError:
        return None
    
def parse_rating_review(value):
    if pd.isna(value):
        return None
    
    value_str = str(value).strip()

    if "Yeni" in value_str or "New" in value_str:
        return np.nan,0
    
    match = re.search(r'([\d,]+)\s*\((\d+)\)', value_str)
    if match:
        rating_str = match.group(1).replace(",",".")
        review_count_str = match.group(2)
        return float(rating_str), int(review_count_str)
    return np.nan,0

def convert_timestamp(value,df):
    if pd.isna(value["checkin"]) or pd.isna(value["checkout"]):
        return None
    
    checkin_dt = pd.to_datetime(value["checkin"])
    checkout_dt = pd.to_datetime(value["checkout"])
    df["checkin"] = checkin_dt
    df["checkout"] = checkout_dt

    duration_nights = (checkout_dt - checkin_dt).days

    try:
        return duration_nights
    except:
        return None
    
def cal_nightly_rate(value):
    if pd.isna(value["clean_original_price"]) or pd.isna(value["duration_nights"]):
        return None
    
    discounted_nightly_rate = value["clean_discount_price"] / value["duration_nights"]
    original_nightly_rate = value["clean_original_price"] / value["duration_nights"]

    value["discounted_nightly_rate"] = discounted_nightly_rate
    value["original_nightly_rate"] = original_nightly_rate

    try:
        return value
    except:
        return None


def main(filepath):
    df = pd.read_csv(filepath)

    print("--- 1. Cleaning Pricess ---")
    df["clean_discount_price"] = df["discounted_price"].apply(clean_currency)
    df["clean_original_price"] = df["original_price"].apply(clean_currency)
    df["final_price"] = df["clean_discount_price"].fillna(df["clean_original_price"])

    print("--- 2. Cleaning Rating ---")
    rating_data = df["point_comments"].apply(lambda x: pd.Series(parse_rating_review(x)))
    df["raiting_val"] = rating_data[0]
    df["review_count"] = rating_data[1]

    print("--- 3. Converting Datetime ---")
    df["duration_nights"] = df.apply(convert_timestamp, axis=1,args=(df,))

    print("--- 4. Calculating Nightly Rate ---")
    value = df[["clean_discount_price", "clean_original_price","duration_nights"]]
    var = value.apply(cal_nightly_rate, axis=1)
    df["discounted_nightly_rate"] = var["discounted_nightly_rate"]
    df["original_nightly_rate"] = var["original_nightly_rate"]


    df = df.drop(columns = ["point_comments","discounted_price","original_price"])
    return df
    






if __name__ == "__main__":
    main()

    # print("--- 1. Cleaning Pricess ---")

    # df["clean_discount"] = df["discounted_price"].apply(clean_currency)
    # df["clean_original"] = df["original_price"].apply(clean_currency)

    # df["final_price"] = df["clean_discount"].fillna(df["clean_original"])

    # print(df[["clean_discount","clean_original","final_price"]].head())

    # print("--- 2. Cleaning Rating ---")
    # rating_data = df["point_comments"].apply(lambda x: pd.Series(parse_rating_review(x)))
    # df["raiting_val"] = rating_data[0]
    # df["review_count"] = rating_data[1]

    # print(df[["point_comments","raiting_val","review_count"]].head())
    # df = df.drop(columns = ["point_comments","discounted_price","original_price"])
    # df.to_csv('data_cleaned_step1.csv', index=False)


# --- GERİ DÖNÜNCE YAPILACAKLAR --- 
    # convert_timestamp metodu timestamp düzenleme metodu olarak değiştirilecek
    # gemini sohbetindeki kod bloğu yazılacak
    # tüm fonksiyonları doğru sırayla kullandıran ve sonunda nihai csv dosyasını oluşturan bir main metodu tanımlanacak
    


    