#!/usr/bin/env python3
"""
飞书机器人自动回复服务 - 简化版
直接使用webhook进行双向通信
"""
import json
import requests
from datetime import datetime

# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"

# 回复规则
REPLIES = {
    "你好": "你好！我是亚马逊产品调研RPA机器人 🤖",
    "帮助": "📋 可用命令:\n- 开始调研\n- 状态\n- 报告\n- 产品池",
    "开始调研": "🚀 正在启动亚马逊产品调研...",
    "状态": "📊 当前状态: 空闲中",
    "报告": "📄 最新报告已发送!",
    "产品池": "📦 产品池: 3个候选产品",
    "差评分析": "⚠️ 差评痛点: 漏水、保温差",
    "好评分析": "✅ 好评亮点: 外观漂亮、便携",
    "再见": "👋 再见！",
}


def send_text(text):
    """发送文本消息"""
    data = {
        "msg_type": "text",
        "content": {"text": text}
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        result = response.json()
        return result.get("code") == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False


def get_reply(message):
    """获取自动回复"""
    message = message.strip().lower()
    
    for keyword, reply in REPLIES.items():
        if keyword.lower() in message:
            return reply
    
    return f"收到消息: {message}\n\n发送「帮助」查看可用命令"


def test_auto_reply():
    """测试自动回复功能"""
    print("="*60)
    print("飞书自动回复测试")
    print("="*60)
    print()
    
    test_messages = ["你好", "帮助", "开始调研"]
    
    for msg in test_messages:
        print(f"测试消息: {msg}")
        reply = get_reply(msg)
        print(f"自动回复: {reply}")
        
        if send_text(reply):
            print("✅ 发送成功")
        else:
            print("❌ 发送失败")
        print()
    
    print("测试完成！请检查飞书群消息")
    print("="*60)


if __name__ == "__main__":
    test_auto_reply()
