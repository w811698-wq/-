"""
主程序入口
执行BSR监控和数据对比
"""

import sys
import os
import shutil
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amazon_bsr_monitor.config import CURRENT_DATA_DIR, PREVIOUS_DATA_DIR
from amazon_bsr_monitor.scraper import AmazonBSRScraper, generate_demo_data
from amazon_bsr_monitor.analyzer import load_data, save_data, generate_analysis_report
from amazon_bsr_monitor.feishu_sender import send_weekly_report


def run_weekly_report(use_demo=False):
    """
    执行周报任务

    Args:
        use_demo: 是否使用演示数据（当无法抓取真实数据时）
    """
    print("=" * 50)
    print("亚马逊假发类BSR周报任务开始")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 步骤1: 备份上周数据
    print("\n[1/4] 备份上周数据...")
    if os.path.exists(CURRENT_DATA_DIR):
        # 清空previous目录
        if os.path.exists(PREVIOUS_DATA_DIR):
            shutil.rmtree(PREVIOUS_DATA_DIR)
        # 复制current到previous
        shutil.copytree(CURRENT_DATA_DIR, PREVIOUS_DATA_DIR)
        print("上周数据已备份")
    else:
        print("无上周数据可备份（首次运行）")

    # 步骤2: 抓取本周数据
    print("\n[2/4] 抓取本周BSR数据...")
    if use_demo:
        print("使用演示数据...")
        current_data = generate_demo_data()
    else:
        scraper = AmazonBSRScraper()
        current_data = scraper.scrape_all_categories()

    # 保存本周数据
    save_data(current_data, CURRENT_DATA_DIR)
    print(f"已抓取 {sum(len(v) for v in current_data.values())} 条商品数据")

    # 步骤3: 数据对比分析
    print("\n[3/4] 数据对比分析...")
    previous_data = load_data(PREVIOUS_DATA_DIR)
    report = generate_analysis_report(current_data, previous_data)

    print(f"排名上升≥5位: {report['summary']['total_up']}个")
    print(f"排名下降≥5位: {report['summary']['total_down']}个")
    print(f"新上榜: {report['summary']['total_new']}个")
    print(f"掉出榜单: {report['summary']['total_dropped']}个")

    # 步骤4: 发送飞书通知
    print("\n[4/4] 发送飞书通知...")
    success = send_weekly_report(report)

    if success:
        print("周报任务完成！")
    else:
        print("飞书通知发送失败，请检查配置")

    return report


if __name__ == "__main__":
    # 检查是否传入--demo参数
    use_demo = "--demo" in sys.argv
    run_weekly_report(use_demo=use_demo)
