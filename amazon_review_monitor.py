#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Isaic产品评论监控脚本
功能：抓取产品评论数据并发送到飞书Webhook
"""

import requests
import json
import re
import os
from datetime import datetime
from urllib.parse import urljoin

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"

PRODUCTS = {
    "2122": {
        "name": "Drawstring马尾扩展",
        "asin": "B0D62RT6DP",
        "url": "https://www.amazon.com/Isaic-Extension-Ponytails-Drawstring-Extensions/dp/B0D62RT6DP",
        "initial_reviews": 0,
        "initial_rating": 0.0
    },
    "2132": {
        "name": "Voluminous卷发马尾扩展",
        "asin": "B0GKF6JRDX",
        "url": "https://www.amazon.com/Isaic-Extension-Voluminous-Synthetic-Hairpiece/dp/B0GKF6JRDX",
        "initial_reviews": 0,
        "initial_rating": 0.0
    },
    "xfw": {
        "name": "Thinning头顶假发扩展",
        "asin": "B0FL7DLB1L",
        "url": "https://www.amazon.com/Isaic-Thinning-Synthetic-Extensions-Adjustable/dp/B0FL7DLB1L",
        "initial_reviews": 0,
        "initial_rating": 0.0
    },
    "2113": {
        "name": "Isaic Hairpiece扩展",
        "asin": "B0F1T3BRHG",
        "url": "https://www.amazon.com/Isaic-Extension-Extensions-Synthetic-Hairpiece/dp/B0F1T3BRHG",
        "initial_reviews": 0,
        "initial_rating": 0.0
    }
}

DATA_FILE = "/workspace/amazon_review_data.json"

def load_previous_data():
    """加载之前保存的数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_current_data(data):
    """保存当前数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_reviews_count_and_rating(html_content):
    """从HTML内容中提取评论数和评分"""
    # 尝试多种模式匹配
    # 模式1: "(XXX) ratings"
    reviews_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*ratings',
        r'(\d{1,3}(?:,\d{3})*)\s*customer\s+reviews',
        r'(\d{1,3}(?:,\d{3})*)\s*global\s+reviews',
        r'(\d{1,3}(?:,\d{3})*)\s*reviews'
    ]
    
    reviews = None
    for pattern in reviews_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            reviews = int(re.sub(r'[,]', '', match.group(1)))
            break
    
    # 匹配评分: "X.X out of 5 stars"
    rating = None
    rating_match = re.search(r'([\d.]+)\s*out\s*of\s*5\s*stars', html_content, re.IGNORECASE)
    if rating_match:
        rating = float(rating_match.group(1))
    
    return reviews, rating

def fetch_product_data(product_id, product_info):
    """抓取单个产品数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(product_info['url'], headers=headers, timeout=15)
        response.raise_for_status()
        
        reviews, rating = get_reviews_count_and_rating(response.text)
        
        return {
            "reviews": reviews or product_info['initial_reviews'],
            "rating": rating or product_info['initial_rating'],
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"抓取{product_id}失败: {e}")
        return {
            "reviews": product_info['initial_reviews'],
            "rating": product_info['initial_rating'],
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

def calculate_changes(current, previous):
    """计算数据变化"""
    if not previous:
        return {
            "reviews_change": 0,
            "rating_change": 0.0,
            "is_first_run": True
        }
    
    reviews_change = current['reviews'] - previous['reviews']
    rating_change = round(current['rating'] - previous['rating'], 1)
    
    return {
        "reviews_change": reviews_change,
        "rating_change": rating_change,
        "is_first_run": False
    }

def format_change(value, is_rating=False):
    """格式化变化值"""
    if value == 0:
        return "无变化"
    elif value > 0:
        prefix = "↑" if not is_rating else "+"
        return f"{prefix}{value}" + ("星" if is_rating else "条")
    else:
        prefix = "↓" if not is_rating else ""
        return f"{prefix}{value}" + ("星" if is_rating else "条")

def generate_report(product_data, changes):
    """生成飞书报告"""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d %H:%M")
    next_run = now.replace(day=now.day + 1, hour=8, minute=50, second=0)
    if now.hour >= 8 and now.minute >= 50:
        next_run = next_run.replace(day=now.day + 1)
    
    report_lines = [
        f"📊 【Amazon Isaic产品评论日报】",
        f"📅 {today_str}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    for product_id, product_info in PRODUCTS.items():
        current = product_data[product_id]
        change = changes[product_id]
        
        if change['is_first_run']:
            change_text = "（首次抓取）"
        else:
            reviews_change = format_change(change['reviews_change'])
            rating_change = format_change(change['rating_change'], is_rating=True)
            change_text = f"（评论{reviews_change}，评分{rating_change}）"
        
        report_lines.extend([
            f"📌 产品{product_id} - {product_info['name']}",
            f"• 评分: {current['rating']}星 {change_text}",
            f"• 评论总数: {current['reviews']}条",
            ""
        ])
    
    report_lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"⏰ 下次更新: {next_run.strftime('%Y-%m-%d %H:%M')}（北京时间）"
    ])
    
    return "\n".join(report_lines)

def send_to_feishu(message):
    """发送消息到飞书"""
    try:
        payload = {
            "msg_type": "text",
            "content": {"text": message}
        }
        response = requests.post(
            FEISHU_WEBHOOK,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=10
        )
        result = response.json()
        return result.get('code') == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 Amazon Isaic产品评论监控")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    previous_data = load_previous_data()
    current_data = {}
    changes = {}
    
    for product_id, product_info in PRODUCTS.items():
        print(f"\n📦 正在抓取 {product_id} ({product_info['name']})...")
        
        data = fetch_product_data(product_id, product_info)
        current_data[product_id] = data
        
        prev = previous_data.get(product_id) if previous_data else None
        changes[product_id] = calculate_changes(data, prev)
        
        if changes[product_id]['is_first_run']:
            print(f"   ✅ 首次抓取: 评分{data['rating']}星, 评论{data['reviews']}条")
        else:
            reviews_change = format_change(changes[product_id]['reviews_change'])
            rating_change = format_change(changes[product_id]['rating_change'], is_rating=True)
            print(f"   ✅ 评分: {data['rating']}星 ({rating_change}), 评论: {data['reviews']}条 ({reviews_change})")
    
    save_current_data(current_data)
    print(f"\n💾 数据已保存到: {DATA_FILE}")
    
    report = generate_report(current_data, changes)
    print("\n📋 生成报告:")
    print("-" * 50)
    print(report)
    print("-" * 50)
    
    print("\n📤 发送到飞书...")
    if send_to_feishu(report):
        print("✅ 发送成功!")
    else:
        print("❌ 发送失败")
    
    print("\n" + "=" * 50)
    print("✨ 任务完成!")
    print("=" * 50)

if __name__ == "__main__":
    main()
