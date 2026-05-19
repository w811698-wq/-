#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"
DATA_FILE = "/workspace/amazon_review_data.json"

PRODUCTS = [
    {
        "id": "2122",
        "asin": "B0D62RT6DP",
        "name": "Drawstring马尾扩展",
        "url": "https://www.amazon.com/Isaic-Extension-Ponytails-Drawstring-Extensions/dp/B0D62RT6DP"
    },
    {
        "id": "2132",
        "asin": "B0GKF6JRDX",
        "name": "Voluminous卷发马尾扩展",
        "url": "https://www.amazon.com/Isaic-Extension-Voluminous-Synthetic-Hairpiece/dp/B0GKF6JRDX"
    },
    {
        "id": "xfw",
        "asin": "B0FL7DLB1L",
        "name": "Thinning头顶假发扩展",
        "url": "https://www.amazon.com/Isaic-Thinning-Synthetic-Extensions-Adjustable/dp/B0FL7DLB1L"
    },
    {
        "id": "2113",
        "asin": "B0F1T3BRHG",
        "name": "Isaic Hairpiece扩展",
        "url": "https://www.amazon.com/Isaic-Extension-Extensions-Synthetic-Hairpiece/dp/B0F1T3BRHG"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_amazon_product_info(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rating = None
        review_count = None
        
        rating_element = soup.find("span", {"class": "a-icon-alt"})
        if rating_element:
            rating_text = rating_element.text.strip()
            try:
                rating = float(rating_text.split()[0])
            except (IndexError, ValueError):
                pass
        
        review_count_element = soup.find("span", {"id": "acrCustomerReviewText"})
        if review_count_element:
            review_text = review_count_element.text.strip()
            try:
                review_count = int(review_text.replace(',', '').split()[0])
            except (IndexError, ValueError):
                pass
        
        return rating, review_count
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def send_feishu_message(message):
    try:
        data = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        response = requests.post(FEISHU_WEBHOOK, json=data, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Feishu message: {e}")
        return False

def main():
    old_data = load_data()
    new_data = {}
    report_lines = []
    
    report_lines.append(f"📊 Amazon Isaic 产品评论监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 50)
    
    for product in PRODUCTS:
        print(f"Fetching data for {product['name']}...")
        rating, review_count = get_amazon_product_info(product['url'])
        
        old_rating = old_data.get(product['id'], {}).get('rating')
        old_review_count = old_data.get(product['id'], {}).get('review_count')
        
        new_data[product['id']] = {
            'rating': rating,
            'review_count': review_count,
            'timestamp': datetime.now().isoformat()
        }
        
        rating_change = None
        review_change = None
        if old_rating is not None and rating is not None:
            rating_change = rating - old_rating
        if old_review_count is not None and review_count is not None:
            review_change = review_count - old_review_count
        
        report_lines.append(f"\n🔹 {product['name']} (ASIN: {product['asin']})")
        report_lines.append(f"   评分: {rating if rating is not None else 'N/A'} {'(+' + str(rating_change) + ')' if rating_change and rating_change > 0 else ('(' + str(rating_change) + ')' if rating_change and rating_change < 0 else '')}")
        report_lines.append(f"   评论数: {review_count if review_count is not None else 'N/A'} {'(+' + str(review_change) + ')' if review_change and review_change > 0 else ('(' + str(review_change) + ')' if review_change and review_change < 0 else '')}")
        report_lines.append(f"   链接: {product['url']}")
        
        time.sleep(2)
    
    save_data(new_data)
    
    message = "\n".join(report_lines)
    print("\n" + message)
    
    print("\nSending to Feishu...")
    success = send_feishu_message(message)
    if success:
        print("Message sent successfully!")
    else:
        print("Failed to send message.")

if __name__ == "__main__":
    main()

