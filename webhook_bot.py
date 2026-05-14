#!/usr/bin/env python3
"""
飞书自定义机器人 - Webhook版本
使用webhook直接发送消息，无需复杂配置
"""
import requests
import json
from datetime import datetime


class FeishuWebhookBot:
    """飞书自定义机器人 - Webhook版本"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_text(self, text):
        """发送文本消息"""
        data = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        return self._send_request(data)
    
    def send_card(self, title, content, buttons=None):
        """发送卡片消息"""
        elements = [
            {
                "tag": "markdown",
                "content": f"**{title}**\n\n{content}"
            }
        ]
        
        if buttons:
            actions = []
            for btn in buttons:
                actions.append({
                    "tag": "button",
                    "text": {
                        "content": btn.get("text", "按钮"),
                        "tag": "plain_text"
                    },
                    "type": btn.get("type", "primary"),
                    "url": btn.get("url", "")
                })
            elements.append({"tag": "action", "actions": actions})
        
        data = {
            "msg_type": "interactive",
            "card": {
                "elements": elements
            }
        }
        return self._send_request(data)
    
    def send_image(self, image_key):
        """发送图片消息"""
        data = {
            "msg_type": "image",
            "content": {
                "image_key": image_key
            }
        }
        return self._send_request(data)
    
    def send_richtext(self, title, content_list):
        """发送富文本消息"""
        content = []
        for item in content_list:
            if item.get("type") == "text":
                content.append({
                    "tag": "text",
                    "text": item.get("text", "")
                })
            elif item.get("type") == "a":
                content.append({
                    "tag": "a",
                    "text": item.get("text", ""),
                    "href": item.get("href", "")
                })
        
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [content]
                    }
                }
            }
        }
        return self._send_request(data)
    
    def _send_request(self, data):
        """发送HTTP请求"""
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ 消息发送成功")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('msg', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False


# --- 快捷使用函数 ---

# 从用户提供的链接初始化
DEFAULT_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"

_bot_instance = None

def get_bot():
    """获取默认机器人实例"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = FeishuWebhookBot(DEFAULT_WEBHOOK)
    return _bot_instance

def send(text):
    """快速发送文本消息"""
    return get_bot().send_text(text)

def send_card(title, content):
    """快速发送卡片消息"""
    return get_bot().send_card(title, content)


# --- 示例用法 ---

if __name__ == "__main__":
    print("="*60)
    print("飞书自定义机器人 - Webhook版本")
    print("="*60)
    print()
    
    bot = FeishuWebhookBot(DEFAULT_WEBHOOK)
    
    print("📧 发送测试消息...")
    bot.send_text(f"🤖 测试消息\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📬 发送测试卡片...")
    bot.send_card(
        "测试通知",
        "这是一条卡片消息\n\n✅ 系统运行正常\n📊 数据已更新"
    )
    print()
    
    print("="*60)
    print("测试完成！")
    print("="*60)
