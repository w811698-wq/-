#!/usr/bin/env python3
"""
亚马逊产品调研RPA - 完整集成版
使用飞书应用凭证发送消息
"""
import os
import sys
import time
from datetime import datetime
from excel_exporter import ExcelExporter
from feishu_app_bot import FeishuAppBot, get_bot


# 初始化机器人
bot = get_bot()

# 默认配置
DEFAULT_KEYWORD = "water bottle"
RESEARCH_CONFIG = {
    "min_price": 10,
    "max_price": 100,
    "min_rating": 4.0,
    "min_reviews": 50,
}


def send_notification(title, content, is_card=True):
    """发送通知到飞书"""
    try:
        # 注意: 需要提供有效的 open_id 或 chat_id
        # 以下为示例，可根据实际情况修改
        receiver_id = ""  # TODO: 替换为实际ID
        
        if is_card:
            bot.send_card(receiver_id, title, content)
        else:
            bot.send_message_to_user(receiver_id, text=f"{title}\n\n{content}")
    except Exception as e:
        print(f"发送通知失败: {e}")


def test_connection():
    """测试连接"""
    print("="*60)
    print("飞书应用连接测试")
    print("="*60)
    print()
    
    print("🔑 获取Access Token...")
    token = bot.get_access_token()
    
    if token:
        print("✅ 连接成功!")
        print(f"Token: {token[:20]}...")
        return True
    else:
        print("❌ 连接失败")
        return False


def send_welcome_message():
    """发送欢迎消息"""
    welcome_text = f"""
🤖 亚马逊产品调研RPA - 已启动

⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 可用命令:
• 开始调研 [关键词] - 启动产品调研
• 状态 - 查看系统状态
• 帮助 - 显示帮助信息

💡 发送命令开始使用
"""
    print(welcome_text)


def run_research_simulation(keyword=DEFAULT_KEYWORD):
    """模拟调研流程"""
    print("="*60)
    print(f"亚马逊产品调研 - 关键词: {keyword}")
    print("="*60)
    print()
    
    steps = [
        (10, "初始化调研任务"),
        (30, "筛选候选产品"),
        (50, "分析竞品打法"),
        (70, "分析评论数据"),
        (90, "生成调研报告"),
        (100, "完成!"),
    ]
    
    for progress, status in steps:
        print(f"[{progress}%] {status}")
        time.sleep(1.5)
    
    # 生成Excel报告
    exporter = ExcelExporter()
    sample_data = {
        "products": [
            {
                "asin": "B001",
                "title": f"{keyword} - 保温杯 Pro",
                "price": "$29.99",
                "rating": "4.5",
                "reviews": "1200",
                "monthly_sales": "500"
            },
            {
                "asin": "B002",
                "title": f"{keyword} - 便携水壶",
                "price": "$19.99",
                "rating": "4.3",
                "reviews": "800",
                "monthly_sales": "300"
            },
            {
                "asin": "B003",
                "title": f"{keyword} - 运动水瓶",
                "price": "$24.99",
                "rating": "4.7",
                "reviews": "2000",
                "monthly_sales": "800"
            },
        ],
        "reviews_analysis": {
            "pain_points": [
                ("漏水", 45),
                ("保温效果差", 38),
                ("容量小", 32),
                ("材质劣质", 28),
                ("易变形", 25),
            ],
            "praise_points": [
                ("保温效果好", 52),
                ("外观漂亮", 45),
                ("便携", 40),
                ("性价比高", 38),
                ("密封好", 35),
            ]
        },
        "keywords": [
            {"keyword": keyword, "search_volume": "50000", "competition": "0.5"},
            {"keyword": f"{keyword} insulated", "search_volume": "30000", "competition": "0.4"},
            {"keyword": f"{keyword} stainless steel", "search_volume": "25000", "competition": "0.45"},
        ],
        "matrix": [
            {"人群": "运动爱好者", "场景": "健身", "关键词": "运动水瓶 健身"},
            {"人群": "上班族", "场景": "办公", "关键词": "办公室水杯"},
            {"人群": "户外", "场景": "徒步", "关键词": "徒步水瓶"},
        ],
        "selling_points": {
            "core": ["解决漏水问题", "提升保温效果", "增大容量"],
            "differential": ["优质不锈钢材质", "人体工学设计"],
            "trust": ["1年质保", "30天无理由退换"],
        }
    }
    
    report_file = exporter.export_all(sample_data)
    
    print()
    print("="*60)
    print("✅ 调研完成!")
    print("="*60)
    print()
    print(f"📊 调研摘要:")
    print(f"  • 产品数量: {len(sample_data['products'])}")
    print(f"  • 关键词数量: {len(sample_data['keywords'])}")
    print(f"  • 报告文件: {os.path.basename(report_file)}")
    print()
    
    return report_file


def interactive_mode():
    """交互模式"""
    print("="*60)
    print("亚马逊产品调研RPA - 交互模式")
    print("="*60)
    print()
    
    commands = {
        "1": ("开始调研", lambda: run_research_simulation()),
        "2": ("测试连接", test_connection),
        "3": ("发送测试消息", lambda: print("请使用 send_test_message() 函数")),
        "0": ("退出", None),
    }
    
    while True:
        print("\n📋 菜单:")
        for key, (name, _) in commands.items():
            print(f"  {key}. {name}")
        print()
        
        choice = input("请选择 (0-3): ").strip()
        
        if choice in commands:
            if choice == "0":
                print("\n👋 再见!")
                break
            else:
                func = commands[choice][1]
                if func:
                    func()
        else:
            print("\n⚠️ 无效选择")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == "test":
            test_connection()
        elif sys.argv[1] == "demo":
            run_research_simulation()
        else:
            keyword = sys.argv[1]
            run_research_simulation(keyword)
    else:
        # 交互模式
        if test_connection():
            send_welcome_message()
            interactive_mode()


if __name__ == "__main__":
    main()
