#!/usr/bin/env python3
"""
飞书消息发送工具包
简单易用，一行代码发送消息到飞书群
"""
import requests
import json
from datetime import datetime


# 飞书Webhook地址
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"


def send_text(text):
    """
    发送文本消息
    
    用法:
        from feishu_send import send_text
        send_text("Hello World!")
    """
    data = {
        "msg_type": "text",
        "content": {"text": text}
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def send_card(title, content):
    """
    发送卡片消息
    
    用法:
        from feishu_send import send_card
        send_card("标题", "内容")
    """
    data = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**{title}**\n\n{content}"
                }
            ]
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 卡片发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def send_research_report(keyword, product_count, keyword_count, report_file, duration):
    """
    发送调研报告卡片
    
    用法:
        from feishu_send import send_research_report
        send_research_report(
            keyword="water bottle",
            product_count=10,
            keyword_count=50,
            report_file="report.xlsx",
            duration=120.5
        )
    """
    content = f"""
**关键词**: {keyword}

**产品数量**: {product_count} 个

**关键词数量**: {keyword_count} 个

**报告文件**: {report_file}

**调研耗时**: {duration:.1f} 秒

**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return send_card("📊 调研完成", content)


def send_progress_update(step, total_steps, status):
    """
    发送进度更新
    
    用法:
        from feishu_send import send_progress_update
        send_progress_update(3, 10, "正在分析评论...")
    """
    progress = int((step / total_steps) * 100)
    content = f"""
**进度**: {progress}%

**当前步骤**: {step}/{total_steps}

**状态**: {status}
"""
    
    return send_card("⏳ 调研进行中", content)


def send_error_report(error_msg):
    """
    发送错误报告
    
    用法:
        from feishu_send import send_error_report
        send_error_report("数据抓取失败")
    """
    content = f"""
**错误类型**: 系统异常

**错误信息**: {error_msg}

**发生时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查系统日志获取更多信息。
"""
    
    return send_card("❌ 调研出错", content)


def send_welcome_message():
    """
    发送欢迎消息
    """
    content = f"""
🤖 **亚马逊产品调研RPA**

系统已启动！

**可用功能**:
- 产品调研
- 竞品分析
- 关键词挖掘
- 评论分析

发送消息开始使用。
"""
    
    return send_card("欢迎使用", content)


# 主程序测试
if __name__ == "__main__":
    print("="*60)
    print("飞书消息发送工具 - 测试")
    print("="*60)
    print()
    
    # 测试1: 发送文本
    print("1. 测试发送文本消息...")
    send_text("🎉 测试消息\n\n时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 测试2: 发送卡片
    print("2. 测试发送卡片消息...")
    send_card(
        "测试卡片",
        "这是一条测试卡片消息\n\n✅ 系统运行正常"
    )
    print()
    
    # 测试3: 发送调研报告
    print("3. 测试发送调研报告...")
    send_research_report(
        keyword="water bottle",
        product_count=10,
        keyword_count=50,
        report_file="amazon_research_20240101.xlsx",
        duration=125.5
    )
    print()
    
    # 测试4: 发送进度
    print("4. 测试发送进度更新...")
    send_progress_update(5, 10, "正在生成报告...")
    print()
    
    print("="*60)
    print("所有测试完成！请检查飞书群消息。")
    print("="*60)
