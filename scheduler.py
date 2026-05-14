#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime
from typing import Callable, Optional
import re

from config import Config

logger = logging.getLogger(__name__)


class CronScheduler:
    """Cron表达式调度器"""

    def __init__(self, cron_expression: str = None):
        self.cron_expression = cron_expression or Config.CRON_EXPRESSION
        self.running = False
        self.last_run_time = None

    def parse_cron(self, cron_expr: str) -> dict:
        """解析Cron表达式"""
        parts = cron_expr.split()

        if len(parts) != 5:
            raise ValueError("Cron表达式必须包含5个部分: 分 时 日 月 周")

        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4]
        }

    def should_run(self, cron_parts: dict) -> bool:
        """判断当前时间是否应该执行任务"""
        now = datetime.now()

        minute = now.minute
        hour = now.hour
        day = now.day
        month = now.month
        weekday = now.weekday()

        if not self._match_cron_field(cron_parts['minute'], minute, 0, 59):
            return False
        if not self._match_cron_field(cron_parts['hour'], hour, 0, 23):
            return False
        if not self._match_cron_field(cron_parts['day'], day, 1, 31):
            return False
        if not self._match_cron_field(cron_parts['month'], month, 1, 12):
            return False
        if not self._match_cron_field(cron_parts['weekday'], weekday, 0, 6):
            return False

        return True

    def _match_cron_field(self, field: str, value: int, min_val: int, max_val: int) -> bool:
        """匹配Cron字段"""
        if field == '*':
            return True

        if ',' in field:
            values = [int(v) for v in field.split(',')]
            return value in values

        if '/' in field:
            parts = field.split('/')
            start = int(parts[0]) if parts[0] != '*' else min_val
            step = int(parts[1])
            return (value - start) % step == 0 and start <= value <= max_val

        if '-' in field:
            parts = field.split('-')
            start, end = int(parts[0]), int(parts[1])
            return start <= value <= end

        return int(field) == value

    def run_task(self, task_func: Callable, check_interval: int = 60) -> None:
        """运行定时任务"""
        self.running = True
        cron_parts = self.parse_cron(self.cron_expression)

        logger.info(f"定时调度器已启动，表达式: {self.cron_expression}")
        logger.info(f"任务函数: {task_func.__name__}")

        while self.running:
            try:
                if self.should_run(cron_parts):
                    logger.info("到达执行时间，开始执行任务...")
                    self.last_run_time = datetime.now()

                    try:
                        task_func()
                        logger.info("任务执行成功")
                    except Exception as e:
                        logger.error(f"任务执行失败: {e}")

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("收到停止信号，正在关闭调度器...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"调度器异常: {e}")
                time.sleep(check_interval)

        logger.info("定时调度器已停止")

    def stop(self) -> None:
        """停止调度器"""
        self.running = False


class SimpleScheduler:
    """简单定时调度器（基于间隔）"""

    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self.running = False
        self.last_run_time = None

    def run_task(self, task_func: Callable, on_start: bool = False) -> None:
        """运行定时任务"""
        self.running = True
        logger.info(f"简单调度器已启动，间隔: {self.interval}秒")

        if on_start:
            logger.info("立即执行首次任务...")
            self._execute_task(task_func)

        while self.running:
            time.sleep(self.interval)
            if self.running:
                self._execute_task(task_func)

        logger.info("简单调度器已停止")

    def _execute_task(self, task_func: Callable) -> None:
        """执行任务"""
        try:
            self.last_run_time = datetime.now()
            logger.info(f"执行任务: {task_func.__name__}...")
            task_func()
            logger.info("任务执行成功")
        except Exception as e:
            logger.error(f"任务执行失败: {e}")

    def stop(self) -> None:
        """停止调度器"""
        self.running = False
