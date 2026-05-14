#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests

from config import Config

logger = logging.getLogger(__name__)


class FeishuNotifier:
    """飞书通知推送类"""

    def __init__(self, webhook_url: str = None, bot_name: str = None):
        self.webhook_url = webhook_url or Config.FEISHU_WEBHOOK_URL
        self.bot_name = bot_name or Config.BOT_NAME
        self.timeout = 10

    def send_message(self, content: str) -> bool:
        """发送文本消息到飞书"""
        if not self.webhook_url:
            logger.error("飞书Webhook URL未配置")
            return False

        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }

            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=self.timeout
            )

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书消息推送成功")
                return True
            else:
                logger.error(f"飞书消息推送失败: {result.get('msg')}")
                return False

        except requests.RequestException as e:
            logger.error(f"飞书消息推送异常: {e}")
            return False

    def send_rich_message(self, title: str, content: str) -> bool:
        """发送富文本消息到飞书"""
        if not self.webhook_url:
            logger.error("飞书Webhook URL未配置")
            return False

        try:
            payload = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": title,
                            "content": [
                                [
                                    {
                                        "tag": "text",
                                        "text": content
                                    }
                                ]
                            ]
                        }
                    }
                }
            }

            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=self.timeout
            )

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书富文本消息推送成功")
                return True
            else:
                logger.error(f"飞书富文本消息推送失败: {result.get('msg')}")
                return False

        except requests.RequestException as e:
            logger.error(f"飞书富文本消息推送异常: {e}")
            return False

    def send_card_message(self, card: Dict) -> bool:
        """发送卡片消息到飞书"""
        if not self.webhook_url:
            logger.error("飞书Webhook URL未配置")
            return False

        try:
            payload = {
                "msg_type": "interactive",
                "card": card
            }

            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=self.timeout
            )

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书卡片消息推送成功")
                return True
            else:
                logger.error(f"飞书卡片消息推送失败: {result.get('msg')}")
                return False

        except requests.RequestException as e:
            logger.error(f"飞书卡片消息推送异常: {e}")
            return False

    def send_monitor_report(self, monitor_data: Dict) -> bool:
        """发送监控报告到飞书"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        elements = []

        if 'cpu' in monitor_data and monitor_data['cpu'].get('enabled'):
            cpu_info = monitor_data['cpu']
            cpu_status = "🔴 警告" if cpu_info.get('usage', 0) > Config.MONITOR_CONFIG['cpu']['threshold'] else "✅ 正常"
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**CPU使用率**: {cpu_info.get('usage', 0):.1f}% {cpu_status}\n{'-'*30}"
                }
            })

        if 'memory' in monitor_data and monitor_data['memory'].get('enabled'):
            mem_info = monitor_data['memory']
            mem_status = "🔴 警告" if mem_info.get('usage_percent', 0) > Config.MONITOR_CONFIG['memory']['threshold'] else "✅ 正常"
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**内存使用率**: {mem_info.get('usage_percent', 0):.1f}% {mem_status}\n{'-'*30}"
                }
            })

        if 'disk' in monitor_data and monitor_data['disk'].get('enabled'):
            for path, disk_info in monitor_data['disk'].items():
                if isinstance(disk_info, dict) and 'usage_percent' in disk_info:
                    disk_status = "🔴 警告" if disk_info.get('usage_percent', 0) > Config.MONITOR_CONFIG['disk']['threshold'] else "✅ 正常"
                    elements.append({
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**磁盘 {path}**: {disk_info.get('usage_percent', 0):.1f}% {disk_status}\n{'-'*30}"
                        }
                    })

        if 'network' in monitor_data and monitor_data['network'].get('enabled'):
            net_info = monitor_data['network']
            net_status = "✅ 正常" if net_info.get('internet_available') else "🔴 异常"
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**网络状态**: {net_status}\n{'-'*30}"
                }
            })

        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 {self.bot_name} - 系统监控报告"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**🕐 监控时间**: {timestamp}"
                    }
                },
                {"tag": "hr"},
                *elements,
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "由自动化监控系统生成"
                        }
                    ]
                }
            ]
        }

        return self.send_card_message(card)
