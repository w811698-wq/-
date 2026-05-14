#!/usr/bin/env python3
"""
飞书应用机器人 - 使用App ID和App Secret
支持发送消息到用户或群组
"""
import requests
import json
from datetime import datetime
from app_config import FEISHU_APP_ID, FEISHU_APP_SECRET, DEFAULT_RECEIVER_ID


class FeishuAppBot:
    """飞书应用机器人 - 使用tenant_access_token"""
    
    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or FEISHU_APP_ID
        self.app_secret = app_secret or FEISHU_APP_SECRET
        self.access_token = None
        self.token_expire_time = 0
    
    def get_access_token(self):
        """获取tenant_access_token"""
        if self.access_token and datetime.now().timestamp() < self.token_expire_time:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                expire = result.get("expire", 7200)
                self.token_expire_time = datetime.now().timestamp() + expire - 100
                print(f"✅ 获取Token成功 (有效期: {expire}秒)")
                return self.access_token
            else:
                print(f"❌ 获取Token失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"❌ 获取Token异常: {e}")
            return None
    
    def send_message_to_user(self, open_id, msg_type="text", content=None, text=None):
        """发送消息给用户"""
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if msg_type == "text" and text:
            msg_content = json.dumps({"text": text})
        elif content:
            msg_content = content
        else:
            print("❌ 未提供消息内容")
            return False
        
        data = {
            "receive_id": open_id,
            "receive_id_type": "open_id",
            "content": msg_content,
            "msg_type": msg_type
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ 消息发送成功 (to open_id: {open_id})")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
            return False
    
    def send_message_to_chat(self, chat_id, msg_type="text", content=None, text=None):
        """发送消息到群组"""
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if msg_type == "text" and text:
            msg_content = json.dumps({"text": text})
        elif content:
            msg_content = content
        else:
            print("❌ 未提供消息内容")
            return False
        
        data = {
            "receive_id": chat_id,
            "receive_id_type": "chat_id",
            "content": msg_content,
            "msg_type": msg_type
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ 消息发送成功 (to chat_id: {chat_id})")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
            return False
    
    def send_card(self, receiver_id, title, content, buttons=None):
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
        
        card_content = {
            "config": {"wide_screen_mode": True},
            "elements": elements
        }
        
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "receive_id": receiver_id,
            "receive_id_type": "open_id",
            "content": json.dumps(card_content),
            "msg_type": "interactive"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ 卡片消息发送成功")
                return True
            else:
                print(f"❌ 卡片消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 发送卡片消息异常: {e}")
            return False
    
    def get_user_info(self, open_id):
        """获取用户信息"""
        token = self.get_access_token()
        if not token:
            return None
        
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/{open_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("user")
            else:
                print(f"❌ 获取用户信息失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return None


# 全局实例
_bot_instance = None

def get_bot():
    """获取机器人实例"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = FeishuAppBot()
    return _bot_instance


def send_to_user(open_id, text):
    """发送文本消息给用户"""
    return get_bot().send_message_to_user(open_id, text=text)


def send_to_chat(chat_id, text):
    """发送文本消息到群组"""
    return get_bot().send_message_to_chat(chat_id, text=text)


def send_card_message(receiver_id, title, content):
    """发送卡片消息"""
    return get_bot().send_card(receiver_id, title, content)


# 快速使用
if __name__ == "__main__":
    print("="*60)
    print("飞书应用机器人 - App ID/Secret版本")
    print("="*60)
    print()
    print(f"App ID: {FEISHU_APP_ID}")
    print()
    
    bot = FeishuAppBot()
    
    print("🔑 测试连接...")
    token = bot.get_access_token()
    
    if token:
        print(f"✅ 连接成功!")
        print()
        
        print("📧 发送测试消息...")
        print("请提供接收者的 open_id 或 chat_id")
        print()
        print("💡 提示:")
        print("  - open_id 格式: ou_xxxxx")
        print("  - chat_id 格式: oc_xxxxx")
        print()
        
        receiver_id = input("请输入接收者ID (或按回车跳过): ").strip()
        
        if receiver_id:
            if receiver_id.startswith("oc_"):
                bot.send_message_to_chat(receiver_id, text=f"🎉 测试消息\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                bot.send_message_to_user(receiver_id, text=f"🎉 测试消息\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("跳过发送测试消息")
        
        print()
        print("✅ 测试完成!")
    else:
        print("❌ 连接失败，请检查App ID和App Secret")
    
    print("="*60)
