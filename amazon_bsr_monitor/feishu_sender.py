"""
飞书推送模块
"""

import requests
import json
from datetime import datetime
from .config import FEISHU_WEBHOOK


class FeishuSender:
    """飞书消息推送"""

    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or FEISHU_WEBHOOK

    def send_message(self, content):
        """发送富文本消息"""
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            result = response.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print("飞书消息发送成功")
                return True
            else:
                print(f"飞书消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"飞书消息发送异常: {e}")
            return False

    def send_card(self, card_content):
        """发送卡片消息"""
        payload = {
            "msg_type": "interactive",
            "card": card_content
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            result = response.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print("飞书卡片消息发送成功")
                return True
            else:
                print(f"飞书卡片消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"飞书卡片消息发送异常: {e}")
            return False


def format_report_for_feishu(report):
    """
    将报告格式化为飞书消息
    简洁明了的格式
    """
    changes = report["changes"]
    stable_count = report["stable_count"]
    summary = report["summary"]

    # 标题
    date_str = datetime.now().strftime("%Y年%m月%d日")
    title = f"📊 亚马逊假发类BSR周报 - {date_str}\n"

    # 关键结论摘要
    conclusion = f"\n✅ 关键结论:\n"
    conclusion += f"• 本周排名上升≥5位商品: {summary['total_up']}个\n"
    conclusion += f"• 本周排名下降≥5位商品: {summary['total_down']}个\n"
    conclusion += f"• 新上榜商品: {summary['total_new']}个\n"
    conclusion += f"• 掉出榜单商品: {summary['total_dropped']}个\n"

    # 重点异动表格
    table_section = "\n📈 重点异动商品:\n"

    # 上升商品
    if changes["ranking_up"]:
        table_section += "\n🔼 排名上升:\n"
        table_section += "品牌 | 变化 | 原因\n"
        table_section += "---|---|---\n"
        for item in changes["ranking_up"][:10]:  # 最多显示10个
            table_section += f"{item['brand']} | +{item['rank_change']} | {item['reason']}\n"

    # 下降商品
    if changes["ranking_down"]:
        table_section += "\n🔽 排名下降:\n"
        table_section += "品牌 | 变化 | 原因\n"
        table_section += "---|---|---\n"
        for item in changes["ranking_down"][:10]:  # 最多显示10个
            table_section += f"{item['brand']} | {item['rank_change']} | {item['reason']}\n"

    # 各品类稳定商品数量
    stable_section = "\n📦 各品类稳定商品数量 (排名变化<5):\n"
    for category, count in stable_count.items():
        stable_section += f"• {category}: {count}个\n"

    return title + conclusion + table_section + stable_section


def send_weekly_report(report):
    """发送周报到飞书"""
    sender = FeishuSender()
    message = format_report_for_feishu(report)
    return sender.send_message(message)


if __name__ == "__main__":
    # 测试
    test_report = {
        "changes": {
            "ranking_up": [
                {"brand": "Luvens", "rank_change": 8, "reason": "Prime Day"}
            ],
            "ranking_down": [],
            "new_entries": [],
            "dropped": []
        },
        "stable_count": {
            "Ponytail Extension": 15,
            "Hair Topper": 12,
            "Hair Extensions": 18
        },
        "summary": {
            "total_up": 1,
            "total_down": 0,
            "total_new": 0,
            "total_dropped": 0
        }
    }
    message = format_report_for_feishu(test_report)
    print(message)
