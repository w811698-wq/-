#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import schedule
from datetime import datetime

print("="*60)
print("  Amazon Isaic 产品评论监控服务")
print("="*60)
print("\n⏰ 定时任务已设置: 每天 08:50 (北京时间)")
print("   监控产品:")
print("   - 2122: ASIN B0D62RT6DP")
print("   - 2132: ASIN B0GKF6JRDX")
print("   - xfw:  ASIN B0FL7DLB1L")
print("\n按 Ctrl+C 停止服务\n")

def run_monitor():
    from amazon_monitor import main as monitor_main
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行监控任务...")
    try:
        monitor_main()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控任务完成")
    except Exception as e:
        print(f"监控任务出错: {e}")

schedule.every().day.at("08:50").do(run_monitor)

while True:
    schedule.run_pending()
    time.sleep(60)
