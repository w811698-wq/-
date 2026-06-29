"""
调度脚本 - 每周一执行
支持两种运行模式:
1. 直接运行: python schedule.py
2. Cron调度: 0 9 * * 1 /usr/bin/python3 /workspace/schedule.py >> /workspace/logs/cron.log 2>&1
"""

import sys
import os
import schedule
import time
import logging
from datetime import datetime

# 设置日志
LOG_DIR = "/workspace/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/schedule.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_weekly_report


def job():
    """定时执行的任务"""
    logger.info("=" * 50)
    logger.info("定时任务触发 - 开始执行周报")
    try:
        report = run_weekly_report(use_demo=False)
        logger.info(f"周报生成成功: 上升{report['summary']['total_up']}个, 下降{report['summary']['total_down']}个")
    except Exception as e:
        logger.error(f"周报生成失败: {e}")
        raise


def run_scheduler():
    """持续运行的调度器（用于测试）"""
    # 每周一早上9点执行
    schedule.every().monday.at("09:00").do(job)

    logger.info("调度器已启动，等待下周一9:00执行...")

    # 持续运行（用于测试时可设置运行时间）
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if "--once" in sys.argv:
        # 单次执行（用于测试）
        logger.info("执行单次周报任务...")
        job()
    else:
        # 持续调度
        run_scheduler()
