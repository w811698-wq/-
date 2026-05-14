#!/usr/bin/env python3
"""
快速测试 - 飞书webhook
"""
import sys
import os


def test_webhook():
    """测试webhook"""
    print("="*60)
    print("飞书Webhook测试")
    print("="*60)
    print()
    
    # 尝试导入requests
    try:
        import requests
        print("✅ requests 库已安装")
    except ImportError:
        print("❌ requests 库未安装")
        print("正在安装...")
        os.system(f"{sys.executable} -m pip install requests")
        import requests
        print("✅ requests 库安装成功")
    
    print()
    
    # 测试webhook
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
    
    print(f"📧 发送测试消息...")
    
    # 简单测试消息
    data = {
        "msg_type": "text",
        "content": {
            "text": "🎉 亚马逊调研RPA - 测试消息\n\n✅ 飞书webhook配置成功！"
        }
    }
    
    try:
        import json
        response = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 消息发送成功！")
            print()
            print("📌 下一步:")
            print("  1. 检查您的飞书群收到消息了吗？")
            print("  2. 运行 'python automated_research.py' 开始调研")
            print("  3. 运行 'python automated_research.py test' 快速测试")
        else:
            print(f"❌ 消息发送失败: {result.get('msg')}")
            print()
            print("💡 提示:")
            print("  - 检查webhook链接是否正确")
            print("  - 检查机器人是否已添加到群聊")
            print("  - 检查是否有安全设置拦截")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()
    print("="*60)


if __name__ == "__main__":
    test_webhook()
