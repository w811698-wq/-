#!/usr/bin/env python3
"""
定时调度器 - 每周一自动执行BSR周报
使用 Python schedule 库实现定时任务
"""

import schedule
import time
import subprocess
import datetime


def run_weekly_job():
    """执行周报任务"""
    print(f"\n{'='*60}")
    print(f"  定时任务触发: {datetime.datetime.now()}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            ["python3", "/workspace/bsr_weekly_report.py"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
    except Exception as e:
        print(f"执行失败: {e}")


# 每周一 09:00 执行
schedule.every().monday.at("09:00").do(run_weekly_job)

print("BSR周报定时调度器已启动")
print("调度规则: 每周一 09:00 (UTC)")
print("按 Ctrl+C 退出\n")

# 立即执行一次（可选）
# run_weekly_job()

while True:
    schedule.run_pending()
    time.sleep(60)  # 每分钟检查一次
