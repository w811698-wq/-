#!/usr/bin/env python3
"""
亚马逊产品调研自动化 - Webhook版本
使用飞书自定义机器人发送通知
"""
import os
import time
from datetime import datetime
from webhook_bot import FeishuWebhookBot
from excel_exporter import ExcelExporter


# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
DEFAULT_KEYWORD = "water bottle"

# 初始化机器人
bot = FeishuWebhookBot(WEBHOOK_URL)


def send_start_notification(keyword):
    """发送启动通知"""
    bot.send_card(
        "🚀 开始调研",
        f"关键词: **{keyword}**\n\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "正在初始化..."
    )


def send_progress_update(step, progress, status):
    """发送进度更新"""
    steps = [
        "筛选产品",
        "分析竞品",
        "分析评论",
        "挖掘关键词",
        "生成报告",
    ]
    
    if step < len(steps):
        current_step = steps[step]
        bot.send_text(
            f"⏳ 进度更新 ({progress}%)\n\n"
            f"当前步骤: {current_step}\n"
            f"状态: {status}"
        )


def send_complete_report(result):
    """发送完成报告"""
    report = (
        f"✅ 调研完成\n\n"
        f"产品数: {result['product_count']}\n"
        f"关键词: {result['keyword_count']}\n"
        f"报告: {result['report_file']}\n\n"
        f"耗时: {result['duration']:.1f}秒"
    )
    bot.send_card("📊 调研完成", report)


def run_research(keyword=DEFAULT_KEYWORD):
    """运行完整调研流程"""
    start_time = time.time()
    
    # 发送启动通知
    send_start_notification(keyword)
    
    try:
        # 模拟调研步骤
        steps = [
            (10, "筛选产品中..."),
            (30, "分析竞品中..."),
            (50, "分析评论中..."),
            (70, "挖掘关键词中..."),
            (90, "生成报告中..."),
            (100, "完成！"),
        ]
        
        for i, (progress, status) in enumerate(steps):
            if progress < 100:
                send_progress_update(i, progress, status)
            time.sleep(1.5)
        
        # 生成模拟数据
        exporter = ExcelExporter()
        sample_data = {
            "products": [
                {"asin": "B001", "title": f"{keyword} - 产品1", "price": "$29.99", "rating": "4.5"},
                {"asin": "B002", "title": f"{keyword} - 产品2", "price": "$19.99", "rating": "4.3"},
                {"asin": "B003", "title": f"{keyword} - 产品3", "price": "$34.99", "rating": "4.7"},
            ],
            "reviews_analysis": {
                "pain_points": [("break", 30), ("leak", 25), ("small", 20)],
                "praise_points": [("durable", 40), ("easy", 35), ("nice", 30)],
            },
            "keywords": [
                {"keyword": keyword, "search_volume": "50000", "competition": "0.5"},
                {"keyword": f"{keyword} best", "search_volume": "30000", "competition": "0.4"},
            ],
        }
        
        report_file = exporter.export_all(sample_data)
        
        # 发送完成报告
        result = {
            "product_count": len(sample_data["products"]),
            "keyword_count": len(sample_data["keywords"]),
            "report_file": os.path.basename(report_file),
            "duration": time.time() - start_time,
        }
        
        send_complete_report(result)
        
        return True
        
    except Exception as e:
        bot.send_text(f"❌ 调研失败\n\n错误: {e}")
        return False


def quick_test():
    """快速测试"""
    print("="*60)
    print("亚马逊产品调研 - Webhook版本")
    print("="*60)
    print()
    
    print("📧 发送测试消息...")
    bot.send_text(f"🤖 亚马逊调研RPA测试\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🚀 运行模拟调研...")
    success = run_research("water bottle")
    print()
    
    if success:
        print("✅ 所有测试完成！")
    else:
        print("❌ 测试失败")
    
    print("="*60)


def interactive_mode():
    """交互模式"""
    print("="*60)
    print("亚马逊产品调研 - 交互模式")
    print("="*60)
    print()
    
    while True:
        print("请选择:")
        print("  1. 快速测试")
        print("  2. 开始调研")
        print("  3. 仅发送测试消息")
        print("  0. 退出")
        print()
        
        choice = input("请选择 (0-3): ").strip()
        
        if choice == "1":
            quick_test()
        elif choice == "2":
            keyword = input("请输入关键词 (默认: water bottle): ").strip()
            if not keyword:
                keyword = DEFAULT_KEYWORD
            print(f"\n开始调研: {keyword}")
            run_research(keyword)
        elif choice == "3":
            print("发送测试消息...")
            bot.send_text("🎯 测试消息\n\n这是来自亚马逊调研RPA的测试消息！")
        elif choice == "0":
            print("\n👋 再见！")
            break
        else:
            print("\n⚠️ 无效选择")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == "test":
            quick_test()
        else:
            keyword = sys.argv[1]
            run_research(keyword)
    else:
        # 交互模式
        interactive_mode()
