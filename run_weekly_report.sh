#!/bin/bash
# 亚马逊BSR周报定时任务脚本
# 设置: 每周一早上9点执行

cd /workspace

echo "=========================================="
echo "🚀 开始执行亚马逊BSR周报"
echo "📅 执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 激活虚拟环境（如果有）
# source venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip3 install requests -q

# 生成周报
echo "📊 生成周报..."
python3 generate_weekly_report.py

echo "✅ 周报任务完成!"
echo "📄 报告已保存至 /workspace/reports/"
echo "📤 飞书推送已完成"
