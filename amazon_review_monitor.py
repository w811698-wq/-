#!/usr/bin/env python3
import requests
import json
import os
import datetime
from bs4 import BeautifulSoup
import time

# 产品配置
PRODUCTS = [
    {
        'id': '2122',
        'asin': 'B0D62RT6DP',
        'name': 'Drawstring马尾扩展',
        'initial_rating': 4.6,
        'initial_reviews': 200
    },
    {
        'id': '2132',
        'asin': 'B0GKF6JRDX',
        'name': 'Voluminous卷发马尾扩展',
        'initial_rating': 5.0,
        'initial_reviews': 13
    },
    {
        'id': '2113',
        'asin': 'B0DK14TGK9',
        'name': 'Claw Clip马尾扩展',
        'initial_rating': 4.4,
        'initial_reviews': 246
    },
    {
        'id': 'xfw',
        'asin': 'B0FL7DLB1L',
        'name': 'Thinning头顶假发扩展',
        'initial_rating': 3.9,
        'initial_reviews': 96
    }
]

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/5fbf44f5-f82c-4f24-8026-0592984641e2"
DATA_FILE = "/workspace/amazon_review_data.json"

def get_amazon_product_data(asin):
    """获取Amazon产品的评分和评论数"""
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 尝试多种方式获取评分
        rating = None
        rating_selectors = [
            '#acrPopover span.a-size-base.a-color-base',
            '#acrPopover',
            'span[data-hook="rating-out-of-text"]',
            '.a-icon-alt'
        ]
        
        for selector in rating_selectors:
            rating_element = soup.select_one(selector)
            if rating_element:
                try:
                    text = rating_element.get_text(strip=True)
                    # 尝试从文本中提取数字
                    import re
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        rating = float(match.group(1))
                        if 1.0 <= rating <= 5.0:
                            break
                except:
                    continue
        
        # 尝试多种方式获取评论数
        review_count = None
        review_selectors = [
            '#acrCustomerReviewText',
            'span[data-hook="total-review-count"]',
            '#totalReviewCount'
        ]
        
        for selector in review_selectors:
            review_element = soup.select_one(selector)
            if review_element:
                try:
                    review_text = review_element.get_text(strip=True)
                    import re
                    numbers = re.findall(r'\d+', review_text)
                    if numbers:
                        review_count = int(''.join(numbers))
                        break
                except:
                    continue
        
        return {
            'rating': rating,
            'review_count': review_count
        }
    except Exception as e:
        print(f"获取ASIN {asin} 数据时出错: {e}")
        return None

def load_previous_data():
    """加载前一天的数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据文件时出错: {e}")
    return None

def save_current_data(data):
    """保存当前数据"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据文件时出错: {e}")

def generate_report(current_data, previous_data):
    """生成报告"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    
    report = f"📊 【Amazon Isaic产品评论日报】\n"
    report += f"📅 {date_str}\n\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for product in PRODUCTS:
        product_id = product['id']
        current = current_data.get(product_id, {})
        
        # 确定基准数据
        if previous_data and product_id in previous_data:
            prev = previous_data[product_id]
            base_rating = prev.get('rating')
            base_reviews = prev.get('review_count')
            is_first = False
        else:
            base_rating = product['initial_rating']
            base_reviews = product['initial_reviews']
            is_first = True
        
        current_rating = current.get('rating')
        current_reviews = current.get('review_count')
        
        # 生成产品报告
        report += f"📌 产品{product_id} - {product['name']}\n"
        
        if current_rating is not None and base_rating is not None:
            rating_change = current_rating - base_rating
            if rating_change > 0:
                report += f"• 评分: {current_rating:.1f}星 ↑+{rating_change:.2f}星\n"
            elif rating_change < 0:
                report += f"• 评分: {current_rating:.1f}星 ↓{rating_change:.2f}星\n"
            else:
                report += f"• 评分: {current_rating:.1f}星 无变化\n"
        elif current_rating is not None:
            report += f"• 评分: {current_rating:.1f}星\n"
        else:
            report += f"• 评分: 获取失败\n"
        
        if current_reviews is not None and base_reviews is not None:
            review_change = current_reviews - base_reviews
            if review_change > 0:
                report += f"• 评论总数: {current_reviews}条 ↑+{review_change}条\n"
            elif review_change < 0:
                report += f"• 评论总数: {current_reviews}条 ↓{review_change}条\n"
            else:
                report += f"• 评论总数: {current_reviews}条 无变化\n"
        elif current_reviews is not None:
            report += f"• 评论总数: {current_reviews}条\n"
        else:
            report += f"• 评论总数: 获取失败\n"
        
        report += "\n"
    
    report += "━━━━━━━━━━━━━━━━━━━━\n"
    report += "⏰ 下次更新: 明天 08:50（北京时间）\n"
    
    return report

def send_to_feishu(message):
    """发送消息到飞书"""
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('code') == 0:
            print("消息已成功发送到飞书")
            return True
        else:
            print(f"发送失败: {result}")
            return False
    except Exception as e:
        print(f"发送飞书消息时出错: {e}")
        return False

def main():
    print("开始执行Amazon产品评论监控...")
    
    # 加载前一天的数据
    previous_data = load_previous_data()
    
    # 抓取当前数据
    current_data = {}
    for product in PRODUCTS:
        print(f"正在获取产品 {product['id']} ({product['name']}) 的数据...")
        data = get_amazon_product_data(product['asin'])
        
        # 确保有评分和评论数数据
        rating = data.get('rating') if data else None
        review_count = data.get('review_count') if data else None
        
        # 如果获取不到数据，使用初始数据
        if rating is None:
            rating = product['initial_rating']
        if review_count is None:
            review_count = product['initial_reviews']
        
        current_data[product['id']] = {
            'rating': rating,
            'review_count': review_count
        }
        
        print(f"  评分: {rating}, 评论数: {review_count}")
        time.sleep(1)  # 避免请求过快
    
    # 保存当前数据
    save_current_data(current_data)
    
    # 生成报告
    report = generate_report(current_data, previous_data)
    print("\n生成的报告:")
    print(report)
    
    # 发送到飞书
    print("\n正在发送报告到飞书...")
    send_to_feishu(report)
    
    print("\n任务完成!")

if __name__ == "__main__":
    main()
