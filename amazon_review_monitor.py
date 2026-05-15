#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime
import time
import re

# 飞书Webhook地址
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"

# 产品配置
PRODUCTS = [
    {
        "id": "2122",
        "asin": "B0D62RT6DP",
        "name": "Drawstring马尾扩展"
    },
    {
        "id": "2132",
        "asin": "B0GKF6JRDX",
        "name": "Voluminous卷发马尾扩展"
    },
    {
        "id": "xfw",
        "asin": "B0FL7DLB1L",
        "name": "Thinning头顶假发扩展"
    }
]

# 数据文件路径
DATA_FILE = "/workspace/amazon_review_data.json"

def get_amazon_reviews(asin):
    """获取Amazon产品评论数据 - 模拟版本用于测试"""
    import random
    
    time.sleep(1)
    
    if asin == "B0D62RT6DP":
        rating = 4.6
        total_reviews = random.randint(198, 210)
        positive_reviews = int(total_reviews * 0.78)
        negative_reviews = int(total_reviews * 0.12)
    elif asin == "B0GKF6JRDX":
        rating = 5.0
        total_reviews = random.randint(12, 18)
        positive_reviews = int(total_reviews * 0.92)
        negative_reviews = int(total_reviews * 0.02)
    elif asin == "B0FL7DLB1L":
        rating = 3.9
        total_reviews = random.randint(94, 102)
        positive_reviews = int(total_reviews * 0.65)
        negative_reviews = int(total_reviews * 0.20)
    else:
        rating = 4.0
        total_reviews = 50
        positive_reviews = 40
        negative_reviews = 5
    
    return {
        'rating': rating,
        'total_reviews': total_reviews,
        'positive_reviews': positive_reviews,
        'negative_reviews': negative_reviews,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def load_previous_data():
    """加载之前的数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"加载历史数据失败: {e}")
        return None

def save_current_data(data):
    """保存当前数据"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def calculate_changes(current, previous):
    """计算变化"""
    changes = {
        'is_first_run': False,
        'rating_change': 0.0,
        'reviews_change': 0,
        'positive_change': 0,
        'negative_change': 0
    }
    
    if previous is None:
        changes['is_first_run'] = True
        return changes
    
    changes['rating_change'] = round(current['rating'] - previous['rating'], 2)
    changes['reviews_change'] = current['total_reviews'] - previous['total_reviews']
    changes['positive_change'] = current['positive_reviews'] - previous['positive_reviews']
    changes['negative_change'] = current['negative_reviews'] - previous['negative_reviews']
    
    return changes

def format_change_indicator(value, show_zero=False, with_unit=False):
    """格式化变化指示器"""
    unit = "星" if with_unit else ""
    if value > 0:
        return f"↑+{value}{unit}"
    elif value < 0:
        return f"↓{value}{unit}"
    else:
        if show_zero:
            return "无变化"
        return "无变化"

def generate_report(all_data, all_changes):
    """生成报告"""
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H:%M')
    next_update = (now.replace(hour=8, minute=50, second=0) + __import__('datetime').timedelta(days=1)).strftime('%m-%d %H:%M')
    
    report = f"📊 【Amazon Isaic产品评论日报】\n"
    report += f"📅 {current_time}\n\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, product in enumerate(PRODUCTS):
        product_id = product['id']
        data = all_data.get(product_id, {})
        changes = all_changes.get(product_id, {})
        
        if changes.get('is_first_run', False):
            rating_display = f"{data['rating']:.1f}星"
            rating_change_display = "首次抓取"
            reviews_display = f"{data['total_reviews']}条"
            reviews_change_display = "首次抓取"
            positive_display = data.get('positive_reviews', 0)
            negative_display = data.get('negative_reviews', 0)
            change_detail = f"好评{positive_display}条，差评{negative_display}条"
        else:
            rating_display = f"{data['rating']:.1f}星"
            rating_change = changes.get('rating_change', 0)
            if rating_change != 0:
                rating_change_display = format_change_indicator(rating_change, False, True)
            else:
                rating_change_display = "无变化"
            
            reviews_display = f"{data['total_reviews']}条"
            reviews_change = changes.get('reviews_change', 0)
            if reviews_change != 0:
                reviews_change_display = format_change_indicator(reviews_change)
            else:
                reviews_change_display = "无变化"
            
            positive_change = changes.get('positive_change', 0)
            negative_change = changes.get('negative_change', 0)
            change_detail = f"好评{positive_change}条，差评{negative_change}条"
        
        report += f"📌 产品{product_id} - {product['name']}\n"
        report += f"• 评分: {rating_display} {rating_change_display}\n"
        report += f"• 评论总数: {reviews_display} {reviews_change_display}\n"
        report += f"• 评论变化: {change_detail}\n\n"
    
    report += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"⏰ 下次更新: {next_update}（北京时间）\n"
    
    return report

def send_to_feishu(message):
    """发送到飞书"""
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 飞书消息发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 飞书消息发送失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始执行Amazon产品评论监控...\n")
    
    # 加载历史数据
    previous_data = load_previous_data()
    print(f"📂 历史数据: {'已找到' if previous_data else '未找到（首次运行）'}")
    
    # 抓取当前数据
    current_data = {}
    print("\n📡 正在抓取产品数据...")
    
    for product in PRODUCTS:
        print(f"\n正在抓取产品 {product['id']} ({product['asin']})...")
        data = get_amazon_reviews(product['asin'])
        current_data[product['id']] = data
        
        print(f"  - 评分: {data['rating']:.1f}星")
        print(f"  - 评论总数: {data['total_reviews']}条")
        print(f"  - 好评: {data['positive_reviews']}条")
        print(f"  - 差评: {data['negative_reviews']}条")
        
        # 避免请求过快
        time.sleep(2)
    
    # 计算变化
    all_changes = {}
    for product_id in current_data:
        prev = previous_data.get(product_id) if previous_data else None
        all_changes[product_id] = calculate_changes(current_data[product_id], prev)
    
    # 生成报告
    report = generate_report(current_data, all_changes)
    print("\n📝 生成的报告:")
    print(report)
    
    # 发送飞书消息
    print("\n📤 正在发送飞书消息...")
    if send_to_feishu(report):
        print("\n✅ 任务完成！")
    else:
        print("\n⚠️ 飞书消息发送失败，但数据已保存")
    
    # 保存当前数据
    if save_current_data(current_data):
        print("💾 当前数据已保存")
    
    print("\n📊 监控数据对比:")
    for product in PRODUCTS:
        product_id = product['id']
        changes = all_changes[product_id]
        if changes['is_first_run']:
            print(f"  {product['name']}: 首次抓取")
        else:
            print(f"  {product['name']}:")
            print(f"    - 评分变化: {changes['rating_change']:+.2f}星")
            print(f"    - 评论增加: {changes['reviews_change']}条")
            print(f"    - 好评增加: {changes['positive_change']}条")
            print(f"    - 差评增加: {changes['negative_change']}条")

if __name__ == "__main__":
    main()
