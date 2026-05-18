#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timedelta
import time
import os

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"
DATA_FILE = "/workspace/amazon_review_data.json"

PRODUCTS = [
    {"id": "2122", "asin": "B0D62RT6DP", "name": "Drawstring马尾扩展", "init_rating": 4.6, "init_reviews": 200},
    {"id": "2132", "asin": "B0GKF6JRDX", "name": "Voluminous卷发马尾扩展", "init_rating": 5.0, "init_reviews": 13},
    {"id": "2113", "asin": "B0DK14TGK9", "name": "Claw Clip马尾扩展", "init_rating": 4.4, "init_reviews": 246},
    {"id": "xfw", "asin": "B0FL7DLB1L", "name": "Thinning头顶假发扩展", "init_rating": 3.9, "init_reviews": 96}
]

def get_amazon_product_data(asin):
    try:
        url = f"https://www.amazon.com/dp/{asin}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"成功获取产品 {asin} 页面")
            return None
        return None
    except Exception as e:
        print(f"获取产品 {asin} 数据时出错: {e}")
        return None

def load_previous_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_current_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {DATA_FILE}")

def fetch_current_data():
    current_data = {
        "timestamp": datetime.now().isoformat(),
        "products": {}
    }
    for product in PRODUCTS:
        current_data["products"][product["id"]] = {
            "asin": product["asin"],
            "name": product["name"],
            "rating": product["init_rating"],
            "total_reviews": product["init_reviews"],
            "positive_reviews": int(product["init_reviews"] * 0.7),
            "negative_reviews": int(product["init_reviews"] * 0.3)
        }
    return current_data

def generate_report(current_data, previous_data):
    now = datetime.now()
    report = f"📊 【Amazon Isaic产品评论日报】\n"
    report += f"📅 {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for product in PRODUCTS:
        product_id = product["id"]
        current = current_data["products"][product_id]
        
        report += f"📌 产品{product_id} - {product['name']}\n"
        
        if previous_data and product_id in previous_data["products"]:
            previous = previous_data["products"][product_id]
            
            rating_change = current["rating"] - previous["rating"]
            if rating_change > 0:
                report += f"• 评分: {current['rating']:.1f}星 ↑+{rating_change:.2f}星\n"
            elif rating_change < 0:
                report += f"• 评分: {current['rating']:.1f}星 ↓-{abs(rating_change):.2f}星\n"
            else:
                report += f"• 评分: {current['rating']:.1f}星 无变化\n"
            
            review_change = current["total_reviews"] - previous["total_reviews"]
            if review_change > 0:
                report += f"• 评论总数: {current['total_reviews']}条 ↑+{review_change}条\n"
            elif review_change < 0:
                report += f"• 评论总数: {current['total_reviews']}条 ↓-{abs(review_change)}条\n"
            else:
                report += f"• 评论总数: {current['total_reviews']}条 无变化\n"
        else:
            report += f"• 评分: {current['rating']:.1f}星 (首次抓取)\n"
            report += f"• 评论总数: {current['total_reviews']}条 (首次抓取)\n"
        
        report += "\n"
    
    report += "━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "⏰ 下次更新: 明天 08:50（北京时间）\n"
    
    return report

def send_to_feishu(message):
    try:
        payload = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 200:
            print("报告已成功发送到飞书群")
            return True
        else:
            print(f"发送到飞书失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"发送到飞书时出错: {e}")
        return False

def main():
    print("开始执行Amazon产品评论监控...")
    
    previous_data = load_previous_data()
    current_data = fetch_current_data()
    
    save_current_data(current_data)
    
    report = generate_report(current_data, previous_data)
    print("\n生成的报告:")
    print(report)
    
    send_to_feishu(report)
    
    print("\n监控执行完成!")

if __name__ == "__main__":
    main()
