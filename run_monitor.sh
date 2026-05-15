#!/bin/bash
# Amazon评论监控定时任务脚本
# 用于crontab定时执行

cd /workspace

# 激活虚拟环境（如果有）
if [ -f "/workspace/venv/bin/activate" ]; then
    source /workspace/venv/bin/activate
fi

# 执行Python脚本
python3 /workspace/amazon_review_monitor.py

# 记录日志
echo "$(date): 任务执行完成" >> /workspace/amazon_review_monitor.log
