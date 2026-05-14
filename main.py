#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
from datetime import datetime

from config import Config
from monitor import SystemMonitor
from feishu_notifier import FeishuNotifier
from scheduler import CronScheduler, SimpleScheduler


logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MonitorApp:
    """监控应用主类"""

    def __init__(self):
        self.monitor = SystemMonitor()
        self.notifier = FeishuNotifier()

    def run_monitor_task(self) -> None:
        """执行监控任务"""
        logger.info("开始执行监控任务...")

        metrics = self.monitor.get_all_metrics()
        logger.info(f"获取到监控数据: {metrics}")

        alert_info = self.monitor.check_alerts()

        if alert_info['has_alerts']:
            logger.warning(f"检测到告警: {alert_info['alerts']}")
            self._send_alert(alert_info)
        else:
            logger.info("所有指标正常")

        self.notifier.send_monitor_report(metrics)

    def _send_alert(self, alert_info: dict) -> None:
        """发送告警通知"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        alert_text = f"⚠️ 系统告警通知\n\n🕐 时间: {timestamp}\n\n"

        for alert in alert_info['alerts']:
            alert_text += f"• {alert}\n"

        alert_text += "\n请及时检查系统状态！"

        self.notifier.send_message(alert_text)

    def test_connection(self) -> bool:
        """测试飞书连接"""
        logger.info("测试飞书Webhook连接...")

        success = self.notifier.send_message(f"🔔 {Config.BOT_NAME} 连接测试\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n连接成功！")

        if success:
            logger.info("飞书连接测试成功")
        else:
            logger.error("飞书连接测试失败")

        return success

    def show_status(self) -> None:
        """显示当前系统状态"""
        logger.info("获取系统状态...")

        metrics = self.monitor.get_all_metrics()

        print("\n" + "="*50)
        print(f"{Config.BOT_NAME} - 系统状态报告")
        print("="*50)
        print(f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*50)

        cpu = metrics.get('cpu', {})
        if cpu.get('enabled'):
            cpu_status = "🔴 过高" if cpu.get('usage', 0) > cpu.get('threshold', 80) else "✅ 正常"
            print(f"CPU使用率: {cpu.get('usage', 0):.1f}% {cpu_status}")

        memory = metrics.get('memory', {})
        if memory.get('enabled'):
            mem_status = "🔴 过高" if memory.get('usage_percent', 0) > memory.get('threshold', 85) else "✅ 正常"
            print(f"内存使用率: {memory.get('usage_percent', 0):.1f}% {mem_status}")

        disk = metrics.get('disk', {})
        if disk.get('enabled'):
            for path, disk_info in disk.items():
                if isinstance(disk_info, dict) and 'usage_percent' in disk_info:
                    disk_status = "🔴 过高" if disk_info['usage_percent'] > disk.get('threshold', 90) else "✅ 正常"
                    print(f"磁盘 {path}: {disk_info['usage_percent']:.1f}% {disk_status}")

        network = metrics.get('network', {})
        if network.get('enabled'):
            net_status = "✅ 正常" if network.get('internet_available') else "🔴 异常"
            print(f"网络状态: {net_status}")

        print("="*50 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description=f'{Config.BOT_NAME} - 定时推送飞书的监控系统')

    parser.add_argument(
        'mode',
        choices=['cron', 'interval', 'once', 'status', 'test'],
        help='运行模式: cron(定时执行) / interval(间隔执行) / once(执行一次) / status(查看状态) / test(测试连接)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='间隔模式的间隔秒数(默认3600秒)'
    )

    parser.add_argument(
        '--webhook',
        type=str,
        help='飞书Webhook URL(会覆盖环境变量和配置文件)'
    )

    args = parser.parse_args()

    if args.webhook:
        Config.FEISHU_WEBHOOK_URL = args.webhook

    app = MonitorApp()

    if args.mode == 'test':
        success = app.test_connection()
        sys.exit(0 if success else 1)

    elif args.mode == 'status':
        app.show_status()
        sys.exit(0)

    elif args.mode == 'once':
        app.run_monitor_task()
        sys.exit(0)

    elif args.mode == 'cron':
        scheduler = CronScheduler()
        scheduler.run_task(app.run_monitor_task)

    elif args.mode == 'interval':
        scheduler = SimpleScheduler(interval_seconds=args.interval)
        scheduler.run_task(app.run_monitor_task, on_start=True)


if __name__ == '__main__':
    main()
