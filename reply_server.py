#!/usr/bin/env python3
"""
飞书机器人自动回复服务
运行后在飞书机器人设置中配置回调URL
"""
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"

REPLIES = {
    "你好": "你好！我是亚马逊调研RPA机器人 🤖",
    "帮助": "📋 可用命令:\n- 开始调研\n- 状态\n- 报告\n- 产品池",
    "开始调研": "🚀 正在启动亚马逊产品调研...",
    "状态": "📊 当前状态: 空闲中",
    "报告": "📄 最新报告已发送!",
    "产品池": "📦 产品池有3个候选产品",
    "差评分析": "⚠️ 差评痛点: 漏水、保温差",
    "好评分析": "✅ 好评亮点: 外观漂亮、便携",
    "再见": "👋 再见！",
}


def send_text(text):
    data = {"msg_type": "text", "content": {"text": text}}
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        return response.json().get("code") == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False


def get_reply(message):
    msg = message.strip().lower()
    for keyword, reply in REPLIES.items():
        if keyword.lower() in msg:
            return reply
    return f"收到消息: {message}\n发送「帮助」查看命令"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            if "challenge" in data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"challenge": data["challenge"]}).encode())
                return
            
            text = data.get("content", {}).get("text", "")
            print(f"收到消息: {text}")
            
            reply = get_reply(text)
            send_text(reply)
            print(f"已回复: {reply}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
            
        except Exception as e:
            print(f"错误: {e}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    server = HTTPServer(('0.0.0.0', 8000), Handler)
    print("飞书自动回复服务已启动")
    print(f"服务地址: http://localhost:8000")
    print(f"回调URL: http://your-ip:8000")
    print("按 Ctrl+C 停止")
    server.serve_forever()


if __name__ == "__main__":
    main()
