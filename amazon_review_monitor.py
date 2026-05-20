#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
import schedule

FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def load_previous_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"last_update": None, "products": {}}
    return {"last_update": None, "products": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_product_reviews(product):
    try:
        response = requests.get(product['url'], headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if len(response.text) < 10000:
            print(f"产品{product['id']}返回内容过短，可能是反爬虫页面")
            return {
                "rating": None,
                "review_count": None,
                "fetch_time": datetime.now().isoformat(),
                "fetch_success": False,
                "error": "Page too short, likely CAPTCHA or anti-bot protection"
            }

        rating = None
        review_count = None

        rating_selectors = [
            'i[data-hook="average-star-rating"] .a-icon-alt',
            '#acrPopover[title]',
            'span[data-hook="rating-out-of-text"]',
            '[data-hook="average-star-rating"] .a-icon-alt',
            '.a-icon-alt'
        ]

        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get('title', '') or rating_elem.get_text(strip=True)
                rating_match = ''.join(filter(lambda x: x.isdigit() or x == '.', rating_text))
                try:
                    rating = float(rating_match)
                    if 0 <= rating <= 5:
                        break
                except (ValueError, IndexError):
                    continue

        review_selectors = [
            '#acrCustomerReviewText',
            '[data-hook="total-review-count"]',
            '#acrCustomerReviewText[aria-label]',
            'span[data-hook="total-review-count"]'
        ]

        for selector in review_selectors:
            review_elem = soup.select_one(selector)
            if review_elem:
                review_text = review_elem.get('aria-label', '') or review_elem.get_text(strip=True)
                review_text = review_text.replace(',', '').replace(' ratings', '').replace(' reviews', '').replace(' rating', '').replace(' review', '').replace(' global ratings', '').replace('global ratings', '')
                review_numbers = ''.join(filter(str.isdigit, review_text))
                try:
                    review_count = int(review_numbers)
                    if review_count > 0:
                        break
                except (ValueError, IndexError):
                    continue

        return {
            "rating": rating,
            "review_count": review_count,
            "fetch_time": datetime.now().isoformat(),
            "fetch_success": True
        }
    except Exception as e:
        print(f"Error fetching {product['id']}: {str(e)}")
        return {
            "rating": None,
            "review_count": None,
            "fetch_time": datetime.now().isoformat(),
            "fetch_success": False,
            "error": str(e)
        }

def calculate_change(current, previous):
    if previous is None:
        return {"rating_change": 0, "review_change": 0}

    rating_change = 0
    review_change = 0

    if current.get("rating") is not None and previous.get("rating") is not None:
        rating_change = round(current["rating"] - previous["rating"], 2)

    if current.get("review_count") is not None and previous.get("review_count") is not None:
        review_change = current["review_count"] - previous.get("review_count", 0)

    return {"rating_change": rating_change, "review_change": review_change}

def format_change_emoji(change):
    if change > 0:
        return f"↑ +{change}"
    elif change < 0:
        return f"↓ {change}"
    else:
        return "— 不变"

def send_feishu_message(message):
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }

    try:
        response = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            print("飞书消息发送成功")
            return True
        else:
            print(f"飞书消息发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"发送飞书消息失败: {str(e)}")
        return False

def generate_report(current_data, previous_data):
    report_lines = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_lines.append(f"📊 Amazon Isaic 产品评论监控报告")
    report_lines.append(f"🕐 生成时间: {current_time}")
    report_lines.append("")

    report_lines.append("📋 产品详情：")
    report_lines.append("")

    for product in PRODUCTS:
        product_id = product['id']
        current_product = current_data.get('products', {}).get(product_id, {})
        previous_product = previous_data.get('products', {}).get(product_id, {}) if previous_data else {}

        rating = current_product.get('rating', 'N/A')
        review_count = current_product.get('review_count', 'N/A')
        fetch_success = current_product.get('fetch_success', False)

        if previous_product:
            changes = calculate_change(current_product, previous_product)
            rating_change_emoji = format_change_emoji(changes['rating_change'])
            review_change_emoji = format_change_emoji(changes['review_change'])
        else:
            rating_change_emoji = ""
            review_change_emoji = ""

        status_emoji = "✅" if fetch_success else "❌"

        report_lines.append(f"{status_emoji} 产品{product_id} - {product['name']}")
        report_lines.append(f"   ASIN: {product['asin']}")
        if fetch_success:
            rating_display = f"{rating}星" if isinstance(rating, (int, float)) else rating
            review_display = f"{review_count}条" if isinstance(review_count, int) else review_count
            report_lines.append(f"   ⭐ 评分: {rating_display} {rating_change_emoji}")
            report_lines.append(f"   💬 评论: {review_display} {review_change_emoji}")
        else:
            report_lines.append(f"   ⚠️ 获取失败")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append(f"📅 数据更新: {current_data.get('last_update', 'N/A')}")

    return "\n".join(report_lines)

def monitor_and_report():
    print(f"[{datetime.now().isoformat()}] 开始执行监控任务...")

    previous_data = load_previous_data()

    current_data = {
        "last_update": datetime.now().isoformat(),
        "products": {}
    }

    for product in PRODUCTS:
        print(f"正在抓取产品{product['id']}...")
        product_data = fetch_product_reviews(product)
        current_data['products'][product['id']] = product_data

        if not product_data['fetch_success']:
            print(f"产品{product['id']}抓取失败")

        time.sleep(2)

    save_data(current_data)
    print(f"数据已保存到 {DATA_FILE}")

    report = generate_report(current_data, previous_data)
    send_feishu_message(report)

    print("监控任务完成")
    return True

def run_scheduler():
    schedule.every().day.at("08:50").do(monitor_and_report)
    print("定时任务已设置: 每日 08:50 执行")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        monitor_and_report()
    else:
        print("Amazon Isaic 产品评论监控系统")
        print("=" * 40)
        print("模式: 定时执行 (每日 08:50)")
        print("首次运行将立即执行一次监控...")
        print("=" * 40)

        monitor_and_report()

        print("")
        run_scheduler()
