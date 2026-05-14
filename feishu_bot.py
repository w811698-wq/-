import requests
import json
import hashlib
import time
from datetime import datetime


class FeishuBot:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expire_time = 0

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                self.token_expire_time = time.time() + result.get("expire", 7200) - 100
                print(f"获取飞书Token成功，有效期至: {datetime.fromtimestamp(self.token_expire_time)}")
                return self.access_token
            else:
                print(f"获取Token失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"获取Token异常: {e}")
            return None

    def send_text_message(self, chat_id, text):
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "receive_id": chat_id,
            "receive_id_type": "chat_id",
            "content": json.dumps({"text": text}),
            "msg_type": "text"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                print(f"消息发送成功: {text}")
                return True
            else:
                print(f"消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"发送消息异常: {e}")
            return False

    def send_card_message(self, chat_id, title, content, buttons=None):
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**{title}**\n\n{content}",
                        "tag": "lark_md"
                    }
                }
            ]
        }
        
        if buttons:
            actions = []
            for btn in buttons:
                actions.append({
                    "tag": "button",
                    "text": {"content": btn["text"], "tag": "plain_text"},
                    "type": "primary" if btn.get("primary", False) else "default",
                    "url": btn.get("url", "")
                })
            card["elements"].append({"tag": "action", "actions": actions})
        
        data = {
            "receive_id": chat_id,
            "receive_id_type": "chat_id",
            "content": json.dumps(card),
            "msg_type": "interactive"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                print(f"卡片消息发送成功")
                return True
            else:
                print(f"卡片消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"发送卡片消息异常: {e}")
            return False

    def send_image_message(self, chat_id, image_url):
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "receive_id": chat_id,
            "receive_id_type": "chat_id",
            "content": json.dumps({"image_key": image_url}),
            "msg_type": "image"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                print(f"图片消息发送成功")
                return True
            else:
                print(f"图片消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"发送图片消息异常: {e}")
            return False


class FeishuAutoReply:
    def __init__(self, bot):
        self.bot = bot
        self.rules = []

    def add_rule(self, keyword, reply_text, match_type="contains"):
        """
        添加自动回复规则
        :param keyword: 触发关键词
        :param reply_text: 回复内容
        :param match_type: 匹配类型: contains(包含), exact(精确), startswith(开头)
        """
        self.rules.append({
            "keyword": keyword,
            "reply_text": reply_text,
            "match_type": match_type
        })

    def add_rules_from_dict(self, rules_dict):
        """从字典批量添加规则"""
        for keyword, reply_text in rules_dict.items():
            self.add_rule(keyword, reply_text)

    def match_rule(self, message):
        """匹配规则并返回回复"""
        message = message.strip().lower()
        
        for rule in self.rules:
            keyword = rule["keyword"].lower()
            match_type = rule["match_type"]
            
            if match_type == "contains" and keyword in message:
                return rule["reply_text"]
            elif match_type == "exact" and keyword == message:
                return rule["reply_text"]
            elif match_type == "startswith" and message.startswith(keyword):
                return rule["reply_text"]
        
        return None

    def process_message(self, chat_id, message):
        """处理消息并自动回复"""
        reply = self.match_rule(message)
        
        if reply:
            print(f"匹配到规则: '{message}' -> '{reply}'")
            self.bot.send_text_message(chat_id, reply)
            return True
        else:
            print(f"未匹配到规则: '{message}'")
            return False


class FeishuMessageReceiver:
    def __init__(self, verification_token, encrypt_key=None):
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key

    def verify_request(self, headers, body):
        """验证飞书请求的合法性"""
        try:
            token = headers.get("X-Lark-Signature")
            timestamp = headers.get("X-Lark-Request-Timestamp")
            nonce = headers.get("X-Lark-Request-Nonce")
            
            if not all([token, timestamp, nonce]):
                return False
            
            if self.encrypt_key:
                signature = self._generate_signature(timestamp, nonce, body)
                return signature == token
            return True
        except Exception as e:
            print(f"验证请求失败: {e}")
            return False

    def _generate_signature(self, timestamp, nonce, body):
        """生成签名"""
        data = f"{timestamp}{nonce}{self.encrypt_key}{body}"
        return hashlib.sha256(data.encode()).hexdigest()

    def parse_message(self, body):
        """解析消息内容"""
        try:
            data = json.loads(body)
            event = data.get("event", {})
            message = event.get("message", {})
            
            return {
                "chat_id": message.get("chat_id"),
                "sender_id": event.get("sender", {}).get("sender_id", {}).get("open_id"),
                "content": json.loads(message.get("content", "{}")).get("text", ""),
                "message_type": message.get("message_type"),
                "message_id": message.get("message_id")
            }
        except Exception as e:
            print(f"解析消息失败: {e}")
            return None
