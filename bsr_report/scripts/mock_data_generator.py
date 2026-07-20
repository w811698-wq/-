import json
import os
from datetime import datetime, timedelta
from config import DATA_DIR, CATEGORIES

MOCK_PRODUCTS = {
    "Ponytail Extension": [
        {"asin": "B06VSHBCDV", "title": "Drawstring Ponytail Extension Synthetic Hair", "brand": "LUCYHAIR", "price": "$57.99", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B07Z8FRWBG", "title": "Wrap Around Ponytail Extension Long Wavy", "brand": "S-noilite", "price": "$39.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B0FYPBZQ3Z", "title": "Clip in Ponytail Extension Curly Hair", "brand": "REECHO", "price": "$419.90", "has_coupon": False, "has_sale": False, "has_lightning_deal": True},
        {"asin": "B088FNNVZ8", "title": "Afro Puff Drawstring Ponytail Extension", "brand": "rosmile", "price": "$7.63", "has_coupon": True, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B095GVPNLS", "title": "Messy Bun Hair Piece Wavy Curly", "brand": "CJL HAIR", "price": "$9.90", "has_coupon": False, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0C8MWKZTT", "title": "26 inch Black Ponytail Extension", "brand": "Sofeiyan", "price": "$9.49", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B07CTRP273", "title": "Tape in Hair Extensions Human Hair", "brand": "Full Shine", "price": "$39.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B08P6HBCKL", "title": "Afro Puff Drawstring Ponytail Kinky", "brand": "Yinmei Baibian", "price": "$6.99", "has_coupon": False, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0B63MCSLR", "title": "Claw Long Wavy Ponytail Extension", "brand": "ORSUNCER", "price": "$22.99", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0D3CJS74F", "title": "Drawstring Ponytail Extension Deep Curly", "brand": "Alebery", "price": "$32.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
    ],
    "Hair Topper": [
        {"asin": "B07XVK5L8Q", "title": "Hair Topper for Women Real Human Hair", "brand": "Benehair", "price": "$89.99", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B08N5KZV8Z", "title": "Clip in Hair Topper Extension", "brand": "Remy Hair", "price": "$129.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B096HQKPF5", "title": "Synthetic Hair Topper for Thinning Hair", "brand": "S-noilite", "price": "$45.99", "has_coupon": False, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0B5X7HJZJ", "title": "Human Hair Topper with Bangs", "brand": "REECHO", "price": "$159.00", "has_coupon": True, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B0C7L3WQK7", "title": "Hair Topper Clip in Extension", "brand": "LUCYHAIR", "price": "$68.99", "has_coupon": False, "has_sale": False, "has_lightning_deal": True},
    ],
    "Hair Extensions": [
        {"asin": "B07TWZ7XLB", "title": "Tape in Hair Extensions Human Hair", "brand": "Full Shine", "price": "$18.99", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B08N5KZV8Z", "title": "Clip in Hair Extensions Real Human", "brand": "Benehair", "price": "$79.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B096HQKPF5", "title": "Synthetic Clip in Hair Extensions", "brand": "S-noilite", "price": "$25.99", "has_coupon": False, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0B5X7HJZJ", "title": "Micro Loop Hair Extensions", "brand": "REECHO", "price": "$59.99", "has_coupon": True, "has_sale": True, "has_lightning_deal": False},
        {"asin": "B0C7L3WQK7", "title": "Weft Hair Extensions Human Hair", "brand": "LUCYHAIR", "price": "$49.99", "has_coupon": False, "has_sale": False, "has_lightning_deal": True},
        {"asin": "B0DJVBXWSQ", "title": "Hair Tinsel Kit for Girls", "brand": "Holographic", "price": "$9.97", "has_coupon": True, "has_sale": False, "has_lightning_deal": False},
        {"asin": "B0DN9YWXN9", "title": "Clip in Hair Extensions Real Human", "brand": "CJL HAIR", "price": "$34.99", "has_coupon": False, "has_sale": True, "has_lightning_deal": False},
    ]
}


def generate_mock_data(category_name, date_offset=0):
    date = datetime.now() - timedelta(days=date_offset)
    date_str = date.strftime('%Y%m%d')
    
    products = MOCK_PRODUCTS.get(category_name, [])
    result = []
    
    for idx, product in enumerate(products, 1):
        result.append({
            'rank': idx,
            'asin': product['asin'],
            'title': product['title'],
            'brand': product['brand'],
            'price': product['price'],
            'has_coupon': product['has_coupon'],
            'has_sale': product['has_sale'],
            'has_lightning_deal': product['has_lightning_deal'],
            'category': category_name,
            'scraped_at': date.isoformat()
        })
    
    filename = f"{category_name.replace(' ', '_')}_{date_str}.json"
    filepath = f"{DATA_DIR}/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Generated mock data for {category_name} on {date_str}")
    return result


def generate_all_mock_data():
    for category_name in CATEGORIES.keys():
        generate_mock_data(category_name, date_offset=0)
        generate_mock_data(category_name, date_offset=7)


if __name__ == "__main__":
    generate_all_mock_data()