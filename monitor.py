#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import socket
from typing import Dict
import psutil

from config import Config

logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控类"""

    def __init__(self):
        self.config = Config.MONITOR_CONFIG

    def get_cpu_usage(self) -> Dict:
        """获取CPU使用率"""
        if not self.config.get('cpu', {}).get('enabled', True):
            return {'enabled': False}

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            return {
                'enabled': True,
                'usage': cpu_percent,
                'count': cpu_count,
                'threshold': self.config['cpu']['threshold']
            }
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {'enabled': True, 'usage': 0, 'error': str(e)}

    def get_memory_usage(self) -> Dict:
        """获取内存使用情况"""
        if not self.config.get('memory', {}).get('enabled', True):
            return {'enabled': False}

        try:
            mem = psutil.virtual_memory()

            return {
                'enabled': True,
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'usage_percent': mem.percent,
                'threshold': self.config['memory']['threshold']
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {'enabled': True, 'usage_percent': 0, 'error': str(e)}

    def get_disk_usage(self) -> Dict:
        """获取磁盘使用情况"""
        if not self.config.get('disk', {}).get('enabled', True):
            return {'enabled': False}

        disk_data = {'enabled': True}
        paths = self.config.get('disk', {}).get('paths', ['/'])

        try:
            for path in paths:
                try:
                    usage = psutil.disk_usage(path)
                    disk_data[path] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'usage_percent': usage.percent
                    }
                except Exception as e:
                    logger.error(f"获取磁盘 {path} 信息失败: {e}")
                    disk_data[path] = {'error': str(e)}

            disk_data['threshold'] = self.config['disk']['threshold']
            return disk_data

        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {'enabled': True, 'error': str(e)}

    def get_network_status(self) -> Dict:
        """获取网络状态"""
        if not self.config.get('network', {}).get('enabled', True):
            return {'enabled': False}

        network_data = {'enabled': True}

        try:
            net_io = psutil.net_io_counters()
            network_data['bytes_sent'] = net_io.bytes_sent
            network_data['bytes_recv'] = net_io.bytes_recv
            network_data['packets_sent'] = net_io.packets_sent
            network_data['packets_recv'] = net_io.packets_recv

            if self.config.get('network', {}).get('check_internet', True):
                network_data['internet_available'] = self._check_internet_connection()

            return network_data

        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {'enabled': True, 'error': str(e)}

    def _check_internet_connection(self) -> bool:
        """检查网络连接"""
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception as e:
            logger.warning(f"网络连接检查失败: {e}")
            return False

    def get_all_metrics(self) -> Dict:
        """获取所有监控指标"""
        return {
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_status()
        }

    def check_alerts(self) -> Dict:
        """检查是否需要告警"""
        alerts = []
        metrics = self.get_all_metrics()

        if metrics['cpu'].get('enabled') and metrics['cpu'].get('usage', 0) > metrics['cpu'].get('threshold', 80):
            alerts.append(f"CPU使用率过高: {metrics['cpu']['usage']:.1f}%")

        if metrics['memory'].get('enabled') and metrics['memory'].get('usage_percent', 0) > metrics['memory'].get('threshold', 85):
            alerts.append(f"内存使用率过高: {metrics['memory']['usage_percent']:.1f}%")

        if metrics['disk'].get('enabled'):
            for path, disk_info in metrics['disk'].items():
                if isinstance(disk_info, dict) and 'usage_percent' in disk_info:
                    if disk_info['usage_percent'] > metrics['disk'].get('threshold', 90):
                        alerts.append(f"磁盘 {path} 使用率过高: {disk_info['usage_percent']:.1f}%")

        return {
            'has_alerts': len(alerts) > 0,
            'alerts': alerts,
            'metrics': metrics
        }
