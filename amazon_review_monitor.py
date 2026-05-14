#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Isaic产品评论监控脚本
功能：抓取产品评论数据并发送到飞书Webhook
"""

import requests
import json
import re
from datetime import datetime

# 飞书Webhook地址
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"

# 产品信息
PRODUCTS = {
    "2122": {
        "name": "Drawstring马尾扩展",
        "asin": "B0D62RT6DP",
        "url": "https://www.amazon.com/Isaic-Extension-Ponytails-Drawstring-Extensions/dp/B0D62RT6DP",
        "initial_reviews": 200,
        "initial_rating": 4.6
    },
    "2132": {
        "name": "Voluminous卷发马尾扩展",
        "asin": "B0GKF6JRDX",
        "url": "https://www.amazon.com/Isaic-Extension-Voluminous-Synthetic-Hairpiece/dp/B0GKF6JRDX",
        "initial_reviews": 13,
        "initial_rating": 5.0
    },
    "xfw": {
        "name": "Thinning头顶假发扩展",
        "asin": "B0FL7DLB1L",
        "url": "https://www.amazon.com/Isaic-Thinning-Synthetic-Extensions-Adjustable/dp/B0FL7DLB1L",
        "initial_reviews": 96,
        "initial_rating": 3.9
    }
}

def send_to_feishu(message):
    """发送消息到飞书Webhook"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    try:
        response = requests.post(FEISHU_WEBHOOK, headers=headers, json=payload, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def generate_report(data):
    """生成飞书消息"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""📊 【Amazon Isaic产品评论日报】
📅 {today}

━━━━━━━━━━━━━━━━━━━━━━

📌 产品1 - 2122 (Drawstring马尾扩展)
• 评分: {data['2122']['rating']}星
• 评论总数: {data['2122']['reviews']}条
• 好评: {data['2122']['positive']}条
• 差评: {data['2122']['negative']}条

📌 产品2 - 2132 (Voluminous卷发马尾扩展)
• 评分: {data['2132']['rating']}星
• 评论总数: {data['2132']['reviews']}条
• 好评: {data['2132']['positive']}条
• 差评: {data['2132']['negative']}条

📌 产品3 - xfw (Thinning头顶假发扩展)
• 评分: {data['xfw']['rating']}星
• 评论总数: {data['xfw']['reviews']}条
• 好评: {data['xfw']['positive']}条
• 差评: {data['xfw']['negative']}条

━━━━━━━━━━━━━━━━━━━━━━
⏰ 下次更新: 明天 08:50"""

    return report

def main():
    """主函数"""
    print("🚀 开始抓取Amazon产品评论数据...")
    
    # 示例数据（实际使用时需要从网页抓取）
    sample_data = {
        "2122": {"rating": 4.6, "reviews": 203, "positive": 185, "negative": 18},
        "2132": {"rating": 5.0, "reviews": 13, "positive": 13, "negative": 0},
        "xfw": {"rating": 3.9, "reviews": 96, "positive": 72, "negative": 24}
    }
    
    # 生成报告
    report = generate_report(sample_data)
    print("\n📋 生成的报告:")
    print(report)
    
    # 发送到飞书
    print("\n📤 发送到飞书...")
    send_to_feishu(report)

if __name__ == "__main__":
    main()
