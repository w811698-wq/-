#!/bin/bash

cd /workspace

nohup /root/.pyenv/shims/python /workspace/amazon_review_monitor.py > /workspace/monitor.log 2>&1 &

echo "Amazon评论监控服务已启动 (PID: $!)"
echo "日志文件: /workspace/monitor.log"
echo "数据文件: /workspace/amazon_review_data.json"
echo ""
echo "定时任务: 每日 08:50 自动执行"
echo "按 Ctrl+C 停止服务"
