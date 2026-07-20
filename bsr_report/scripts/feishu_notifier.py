import requests
import json
import logging
from datetime import datetime
from config import FEISHU_WEBHOOK

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_change_reason(product):
    reasons = []
    
    if product.get('has_coupon', False):
        reasons.append('优惠券')
    if product.get('has_sale', False):
        reasons.append('折扣促销')
    if product.get('has_lightning_deal', False):
        reasons.append('Lightning Deal')
    
    return ', '.join(reasons) if reasons else '未知'


def build_rising_table(rising_products):
    rows = []
    
    for product in rising_products[:5]:
        reason = analyze_change_reason(product)
        row = {
            "cells": [
                {"tag": "plain_text", "text": product.get('brand', 'N/A')},
                {"tag": "plain_text", "text": f"↑{product['rank_change']}"},
                {"tag": "plain_text", "text": f"{product['previous_rank']}→{product['rank']}"},
                {"tag": "plain_text", "text": reason}
            ]
        }
        rows.append(row)
    
    return rows


def build_falling_table(falling_products):
    rows = []
    
    for product in falling_products[:5]:
        reason = analyze_change_reason(product)
        row = {
            "cells": [
                {"tag": "plain_text", "text": product.get('brand', 'N/A')},
                {"tag": "plain_text", "text": f"↓{abs(product['rank_change'])}"},
                {"tag": "plain_text", "text": f"{product['previous_rank']}→{product['rank']}"},
                {"tag": "plain_text", "text": reason}
            ]
        }
        rows.append(row)
    
    return rows


def build_stable_summary(results):
    summary_rows = []
    
    for category_name, data in results.items():
        summary_rows.append({
            "cells": [
                {"tag": "plain_text", "text": category_name},
                {"tag": "plain_text", "text": str(data['stable_count'])},
                {"tag": "plain_text", "text": str(data['rising_count'])},
                {"tag": "plain_text", "text": str(data['falling_count'])}
            ]
        })
    
    return summary_rows


def build_conclusion(results):
    conclusions = []
    
    for category_name, data in results.items():
        if data['rising_count'] > data['falling_count']:
            conclusions.append(f"{category_name}：整体上升趋势，{data['rising_count']}个商品排名提升")
        elif data['falling_count'] > data['rising_count']:
            conclusions.append(f"{category_name}：整体下降趋势，{data['falling_count']}个商品排名下降")
        else:
            conclusions.append(f"{category_name}：整体稳定，波动较小")
    
    return '\n'.join(conclusions)


def send_report(results):
    current_date = datetime.now().strftime('%Y年%m月%d日')
    
    blocks = []
    
    blocks.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"📊 **亚马逊假发类目BSR排名周报**\n\n日期：{current_date}"
        }
    })
    
    blocks.append({
        "tag": "hr"
    })
    
    blocks.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "🚀 **排名上升≥5名商品**"
        }
    })
    
    all_rising = []
    for data in results.values():
        all_rising.extend(data.get('rising_products', []))
    
    if all_rising:
        all_rising.sort(key=lambda x: x['rank_change'], reverse=True)
        rising_rows = build_rising_table(all_rising)
        
        blocks.append({
            "tag": "table",
            "header": {
                "cells": [
                    {"tag": "plain_text", "text": "品牌"},
                    {"tag": "plain_text", "text": "变化"},
                    {"tag": "plain_text", "text": "排名"},
                    {"tag": "plain_text", "text": "原因"}
                ]
            },
            "rows": rising_rows
        })
    else:
        blocks.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "无明显上升商品"
            }
        })
    
    blocks.append({
        "tag": "hr"
    })
    
    blocks.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "📉 **排名下降≥5名商品**"
        }
    })
    
    all_falling = []
    for data in results.values():
        all_falling.extend(data.get('falling_products', []))
    
    if all_falling:
        all_falling.sort(key=lambda x: x['rank_change'])
        falling_rows = build_falling_table(all_falling)
        
        blocks.append({
            "tag": "table",
            "header": {
                "cells": [
                    {"tag": "plain_text", "text": "品牌"},
                    {"tag": "plain_text", "text": "变化"},
                    {"tag": "plain_text", "text": "排名"},
                    {"tag": "plain_text", "text": "原因"}
                ]
            },
            "rows": falling_rows
        })
    else:
        blocks.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "无明显下降商品"
            }
        })
    
    blocks.append({
        "tag": "hr"
    })
    
    blocks.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "📋 **各品类稳定商品数量**"
        }
    })
    
    stable_rows = build_stable_summary(results)
    
    blocks.append({
        "tag": "table",
        "header": {
            "cells": [
                {"tag": "plain_text", "text": "类目"},
                {"tag": "plain_text", "text": "稳定"},
                {"tag": "plain_text", "text": "上升"},
                {"tag": "plain_text", "text": "下降"}
            ]
        },
        "rows": stable_rows
    })
    
    blocks.append({
        "tag": "hr"
    })
    
    conclusion = build_conclusion(results)
    blocks.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"💡 **关键结论**\n\n{conclusion}"
        }
    })
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "elements": blocks
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
        response.raise_for_status()
        logger.info("Successfully sent Feishu notification")
        return True
    except Exception as e:
        logger.error(f"Failed to send Feishu notification: {e}")
        return False


if __name__ == "__main__":
    sample_results = {
        "Ponytail Extension": {
            "stable_count": 85,
            "rising_count": 8,
            "falling_count": 7,
            "rising_products": [
                {"brand": "Brand A", "rank_change": 15, "previous_rank": 20, "rank": 5, "has_coupon": True, "has_sale": False, "has_lightning_deal": False}
            ],
            "falling_products": [
                {"brand": "Brand B", "rank_change": -12, "previous_rank": 10, "rank": 22, "has_coupon": False, "has_sale": False, "has_lightning_deal": False}
            ]
        }
    }
    send_report(sample_results)