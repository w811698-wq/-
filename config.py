#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class Config:
    """配置文件类"""

    # 飞书Webhook配置
    FEISHU_WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL', '')

    # 定时任务配置
    CRON_EXPRESSION = os.getenv('CRON_EXPRESSION', '0 9 * * *')  # 默认每天9点执行

    # 监控指标配置
    MONITOR_CONFIG = {
        'cpu': {
            'enabled': True,
            'threshold': 80.0  # CPU使用率阈值(%)
        },
        'memory': {
            'enabled': True,
            'threshold': 85.0  # 内存使用率阈值(%)
        },
        'disk': {
            'enabled': True,
            'threshold': 90.0,  # 磁盘使用率阈值(%)
            'paths': ['/']  # 监控的磁盘路径
        },
        'network': {
            'enabled': True,
            'check_internet': True  # 是否检查网络连接
        }
    }

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'monitor.log')

    # 告警冷却时间(秒)，防止重复告警
    ALERT_COOLDOWN = int(os.getenv('ALERT_COOLDOWN', 3600))

    # 机器人名称
    BOT_NAME = os.getenv('BOT_NAME', '监控系统')
