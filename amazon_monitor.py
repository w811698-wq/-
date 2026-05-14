#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"

PRODUCTS = [
    {
        "id": "2122",
        "asin": "B0D62RT6DP",
        "initial_rating": 4.6,
        "initial_reviews": 200
    },
    {
        "id": "2132",
        "asin": "B0GKF6JRDX",
        "initial_rating": 5.0,
        "initial_reviews": 13
    },
    {
        "id": "xfw",
        "asin": "B0FL7DLB1L",
        "initial_rating": 3.9,
        "initial_reviews": 96
    }
]

DATA_DIR = Path("/workspace/amazon_monitor")
BASELINE_FILE = DATA_DIR / "baseline.json"
PREV_REVIEWS_FILE = DATA_DIR / "prev_reviews.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

def init_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_baseline():
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_baseline(data):
    with open(BASELINE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_prev_reviews():
    if PREV_REVIEWS_FILE.exists():
        with open(PREV_REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_prev_reviews(data):
    with open(PREV_REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_with_retry(url, max_retries=3, timeout=30):
    session = requests.Session()
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=get_headers(), timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
    return None

def parse_star_percentage(text):
    match = re.search(r'(\d+)%', text)
    return int(match.group(1)) if match else 0

def fetch_amazon_reviews(asin, initial_data):
    product_data = {
        "asin": asin,
        "rating": initial_data.get("initial_rating"),
        "total_reviews": initial_data.get("initial_reviews"),
        "five_star": 0,
        "four_star": 0,
        "three_star": 0,
        "two_star": 0,
        "one_star": 0,
        "recent_reviews": [],
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    base_url = f"https://www.amazon.com/dp/{asin}"
    reviews_url = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_sr?sortBy=recent"
    
    for url in [base_url, reviews_url]:
        try:
            response = fetch_with_retry(url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if not product_data.get("rating") or product_data.get("rating") == initial_data.get("initial_rating"):
                patterns = [
                    soup.select_one('#acrPopover .a-icon-alt'),
                    soup.select_one('.a-icon-star .a-icon-alt'),
                    soup.select_one('[data-asin="' + asin + '"] [class*="a-icon-alt"]'),
                    soup.select_one('span.a-icon-alt'),
                    soup.select_one('i.a-icon-star .a-icon-alt')
                ]
                for elem in patterns:
                    if elem:
                        rating_text = elem.get_text(strip=True)
                        match = re.search(r'([\d.]+)', rating_text)
                        if match:
                            product_data["rating"] = float(match.group(1))
                            break
            
            if not product_data.get("total_reviews") or product_data.get("total_reviews") == initial_data.get("initial_reviews"):
                patterns = [
                    soup.select_one('#acrCustomerReviewText'),
                    soup.select_one('[data-asin="' + asin + '"] .a-size-base'),
                    soup.select_one('.a-size-base.a-color-secondary'),
                    soup.select_one('span[data-hook="total-review-count"]')
                ]
                for elem in patterns:
                    if elem:
                        reviews_text = elem.get_text(strip=True)
                        match = re.search(r'([\d,]+)', reviews_text)
                        if match:
                            product_data["total_reviews"] = int(match.group(1).replace(',', ''))
                            break
            
            star_bars = soup.select('td.a-text-right span.a-size-base')
            star_percentages = []
            for bar in star_bars:
                percentage = parse_star_percentage(bar.get('style', ''))
                if percentage > 0:
                    star_percentages.append(percentage)
            
            if len(star_percentages) >= 5:
                if product_data.get("total_reviews"):
                    total = product_data["total_reviews"]
                    product_data["five_star"] = int(total * star_percentages[0] / 100)
                    product_data["four_star"] = int(total * star_percentages[1] / 100)
                    product_data["three_star"] = int(total * star_percentages[2] / 100)
                    product_data["two_star"] = int(total * star_percentages[3] / 100)
                    product_data["one_star"] = int(total * star_percentages[4] / 100)
            
            review_elements = soup.select('div[data-hook="review"]')
            for elem in review_elements[:10]:
                title_elem = elem.select_one('a[data-hook="review-title"]')
                body_elem = elem.select_one('span[data-hook="review-body"]')
                rating_elem = elem.select_one('i[data-hook="review-star-rating"]')
                
                if title_elem or body_elem:
                    review_text = ""
                    if title_elem:
                        review_text += title_elem.get_text(strip=True) + " "
                    if body_elem:
                        review_text += body_elem.get_text(strip=True)
                    
                    star_rating = None
                    if rating_elem:
                        try:
                            rating_text = rating_elem.get_text(strip=True)
                            match = re.search(r'([\d.]+)', rating_text)
                            if match:
                                star_rating = float(match.group(1))
                        except:
                            pass
                    
                    if review_text.strip():
                        product_data["recent_reviews"].append({
                            "rating": star_rating,
                            "text": review_text.strip()[:300]
                        })
            
            if product_data.get("rating") and product_data.get("total_reviews"):
                break
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    return product_data

def fetch_all_products():
    all_data = {}
    for product in PRODUCTS:
        print(f"Fetching product {product['id']} ({product['asin']})...")
        data = fetch_amazon_reviews(product['asin'], product)
        all_data[product['id']] = data
        
        print(f"  Rating: {data.get('rating', 'N/A')}, Reviews: {data.get('total_reviews', 'N/A')}")
        print(f"  Recent reviews captured: {len(data.get('recent_reviews', []))}")
        
        time.sleep(random.uniform(3, 6))
    
    return all_data

def calculate_changes(current, previous):
    changes = {}
    
    for product_id in current.keys():
        curr = current[product_id]
        prev = previous.get(product_id, {})
        
        changes[product_id] = {
            "rating_change": None,
            "reviews_change": 0,
            "five_star_change": 0,
            "one_star_change": 0,
            "new_reviews": []
        }
        
        if curr.get("rating") and prev.get("rating"):
            changes[product_id]["rating_change"] = round(curr["rating"] - prev["rating"], 1)
        
        if curr.get("total_reviews") and prev.get("total_reviews"):
            changes[product_id]["reviews_change"] = curr["total_reviews"] - prev["total_reviews"]
        
        if curr.get("five_star") and prev.get("five_star"):
            changes[product_id]["five_star_change"] = curr["five_star"] - prev["five_star"]
        
        if curr.get("one_star") and prev.get("one_star"):
            changes[product_id]["one_star_change"] = curr["one_star"] - prev["one_star"]
        
        if curr.get("recent_reviews") and prev.get("recent_reviews"):
            prev_review_hashes = set()
            for r in prev.get("recent_reviews", []):
                prev_review_hashes.add(hash(r.get("text", "")[:100]))
            
            for review in curr.get("recent_reviews", []):
                review_hash = hash(review.get("text", "")[:100])
                if review_hash not in prev_review_hashes:
                    changes[product_id]["new_reviews"].append(review)
    
    return changes

def format_change(value, is_rating=False):
    if value is None:
        return "-"
    if is_rating:
        sign = "+" if value > 0 else "" if value == 0 else ""
        return f"{sign}{value}星"
    else:
        sign = "+" if value > 0 else "" if value == 0 else ""
        return f"{sign}{value}条"

def send_feishu_message(message):
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": message["title"]
                },
                "template": "blue"
            },
            "elements": message["elements"]
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Feishu notification sent successfully")
            return True
        else:
            print(f"❌ Feishu notification failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send Feishu message: {e}")
        return False

def generate_report(current_data, changes, is_baseline=False):
    today = datetime.now().strftime("%Y-%m-%d")
    
    if is_baseline:
        title = f"【Amazon Isaic产品评论日报】{today} - 首次Baseline已保存"
    else:
        title = f"【Amazon Isaic产品评论日报】{today}"
    
    table_content = []
    for product in PRODUCTS:
        product_id = product["id"]
        data = current_data.get(product_id, {})
        change = changes.get(product_id, {})
        
        rating = data.get("rating") or product.get("initial_rating", "-")
        rating_display = f"{rating}星" if isinstance(rating, (int, float)) else str(rating)
        
        rating_change = change.get("rating_change")
        rating_change_display = format_change(rating_change, is_rating=True) if rating_change else ""
        
        reviews_change = change.get("reviews_change")
        reviews_change_display = f"↑+{reviews_change}条" if reviews_change and reviews_change > 0 else (f"↓{reviews_change}条" if reviews_change and reviews_change < 0 else "无变化")
        
        five_change = change.get("five_star_change")
        five_change_display = f"↑+{five_change}条" if five_change and five_change > 0 else (f"↓{five_change}条" if five_change and five_change < 0 else "-")
        
        one_change = change.get("one_star_change")
        one_change_display = f"↑+{one_change}条" if one_change and one_change > 0 else (f"↓{one_change}条" if one_change and one_change < 0 else "-")
        
        table_content.append([
            {"tag": "td", "children": [{"tag": "plain_text", "content": product_id}]},
            {"tag": "td", "children": [{"tag": "plain_text", "content": rating_display}]},
            {"tag": "td", "children": [{"tag": "plain_text", "content": reviews_change_display}]},
            {"tag": "td", "children": [{"tag": "plain_text", "content": five_change_display}]},
            {"tag": "td", "children": [{"tag": "plain_text", "content": one_change_display}]}
        ])
    
    elements = [
        {
            "tag": "table",
            "columns": [
                {"tag": "th", "children": [{"tag": "plain_text", "content": "产品编号"}]},
                {"tag": "th", "children": [{"tag": "plain_text", "content": "当前评分"}]},
                {"tag": "th", "children": [{"tag": "plain_text", "content": "评论总数变化"}]},
                {"tag": "th", "children": [{"tag": "plain_text", "content": "5星好评变化"}]},
                {"tag": "th", "children": [{"tag": "plain_text", "content": "1星差评变化"}]}
            ],
            "rows": table_content
        }
    ]
    
    if not is_baseline:
        new_reviews_section = []
        for product in PRODUCTS:
            product_id = product["id"]
            change = changes.get(product_id, {})
            new_reviews = change.get("new_reviews", [])
            
            if new_reviews:
                review_lines = [f"\n【产品 {product_id}】新增评论 ({len(new_reviews)}条):"]
                for review in new_reviews[:5]:
                    rating = review.get("rating")
                    text = review.get("text", "")[:150]
                    if rating:
                        review_lines.append(f"• {int(rating)}星: {text}...")
                    else:
                        review_lines.append(f"• {text}...")
                
                new_reviews_section.append({
                    "tag": "div",
                    "children": [{"tag": "plain_text", "content": "\n".join(review_lines)}]
                })
        
        if new_reviews_section:
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "children": [{"tag": "plain_text", "content": "📝 新增评论摘要:"}]
            })
            elements.extend(new_reviews_section)
        
        next_update = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 08:50 北京时间")
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "note",
            "children": [{"tag": "plain_text", "content": f"📅 下次更新时间: {next_update}"}]
        })
    
    return {
        "title": title,
        "elements": elements
    }

def setup_cron_job():
    script_path = Path("/workspace/amazon_monitor.py").resolve()
    cron_time = "50 8 * * *"
    cron_command = f'cd /workspace && /usr/bin/python3 {script_path} >> /workspace/amazon_monitor.log 2>&1'
    cron_entry = f"{cron_time} {cron_command}\n"
    
    try:
        existing_cron = os.popen('crontab -l 2>/dev/null').read()
        
        if str(script_path) in existing_cron:
            print("⏰ Cron job already exists")
            return True
        
        new_cron = existing_cron + cron_entry
        
        process = os.popen('crontab -', 'w')
        process.write(new_cron)
        process.close()
        
        print(f"✅ Cron job set up: {cron_time} daily (Beijing time)")
        return True
    except Exception as e:
        print(f"⚠️ Could not set up cron job: {e}")
        print("  Please manually add this cron entry:")
        print(f"  {cron_time} {cron_command}")
        return False

def main():
    init_data_dir()
    
    print("="*60)
    print("  Amazon Isaic 产品评论监控系统")
    print("="*60)
    
    baseline = load_baseline()
    
    if baseline is None:
        print("\n[首次运行] 正在抓取baseline数据...")
        current_data = fetch_all_products()
        
        baseline = {
            "data": current_data,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_baseline(baseline)
        
        report = generate_report(current_data, {}, is_baseline=True)
        send_feishu_message(report)
        
        prev_reviews = {}
        for product_id, data in current_data.items():
            prev_reviews[product_id] = data.get("recent_reviews", [])
        save_prev_reviews(prev_reviews)
        
        print("\n✅ Baseline数据已保存并发送飞书通知")
        print(f"   保存位置: {BASELINE_FILE}")
        
        setup_cron_job()
        
    else:
        print("\n[日常监控] 正在抓取最新数据...")
        current_data = fetch_all_products()
        
        changes = calculate_changes(current_data, baseline["data"])
        
        report = generate_report(current_data, changes, is_baseline=False)
        success = send_feishu_message(report)
        
        baseline["data"] = current_data
        baseline["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_baseline(baseline)
        
        prev_reviews = {}
        for product_id, data in current_data.items():
            prev_reviews[product_id] = data.get("recent_reviews", [])
        save_prev_reviews(prev_reviews)
        
        print("\n📊 数据对比:")
        for product in PRODUCTS:
            product_id = product["id"]
            change = changes.get(product_id, {})
            rating = current_data.get(product_id, {}).get("rating", "-")
            reviews = current_data.get(product_id, {}).get("total_reviews", "-")
            print(f"   产品 {product_id}: 评分={rating}星, 评论数={reviews}")
            print(f"     - 评论数变化: {change.get('reviews_change', 0)}")
            print(f"     - 新增评论: {len(change.get('new_reviews', []))}条")

if __name__ == "__main__":
    main()
