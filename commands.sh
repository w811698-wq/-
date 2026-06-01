#!/bin/bash

# 亚马逊BSR周报系统 - 常用命令速查

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║     🚀 亚马逊BSR周报系统 - 常用命令速查                          ║
╚════════════════════════════════════════════════════════════════╝

📌 核心操作

  🔹 生成周报并推送
     cd /workspace
     python3 generate_weekly_report.py

  🔹 生成示例数据
     python3 generate_sample_data.py

  🔹 运行系统测试
     python3 test_system.py


📌 定时任务

  🔹 设置每周一执行（每天9点）
     crontab -e
     # 添加: 0 9 * * 1 /workspace/run_weekly_report.sh


📌 文件查看

  🔹 查看最新报告
     cat /workspace/reports/$(ls -t /workspace/reports/ | head -1)

  🔹 查看所有报告
     ls -lh /workspace/reports/

  🔹 查看当前数据
     cat /workspace/data/current_Ponytail_Extension.json | head -20

  🔹 查看上周数据
     cat /workspace/data/previous_week_Ponytail_Extension.json | head -20


📌 日志查看

  🔹 查看执行日志
     cat /workspace/logs/weekly_report.log

  🔹 实时查看日志
     tail -f /workspace/logs/weekly_report.log


📌 数据管理

  🔹 备份数据
     tar -czf backup_$(date +%Y%m%d).tar.gz /workspace/data/

  🔹 清理旧报告（保留90天）
     find /workspace/reports/ -name "*.md" -mtime +90 -delete

  🔹 查看数据大小
     du -sh /workspace/data/
     du -sh /workspace/reports/


📌 系统信息

  🔹 查看Python版本
     python3 --version

  🔹 查看依赖包
     pip3 list | grep requests

  🔹 安装依赖
     pip3 install requests


📌 故障排查

  🔹 测试飞书Webhook
     curl -X POST \
       -H "Content-Type: application/json" \
       -d '{"msg_type":"text","content":{"text":"Test"}}' \
       "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

  🔹 检查Python模块
     python3 -c "import requests; print('requests OK')"

  🔹 查看磁盘空间
     df -h /workspace


📌 文档资源

  🔹 快速开始
     cat /workspace/QUICKSTART.md

  🔹 完整文档
     cat /workspace/README.md

  🔹 系统架构
     cat /workspace/ARCHITECTURE.md

  🔹 交付清单
     cat /workspace/DELIVERY.md


╔════════════════════════════════════════════════════════════════╗
║  ⚡ 快捷操作                                                   ║
╚════════════════════════════════════════════════════════════════╝

  1️⃣ 立即生成周报
     cd /workspace && python3 generate_weekly_report.py

  2️⃣ 查看最新报告
     ls -t /workspace/reports/ | head -1 | xargs cat

  3️⃣ 运行测试
     cd /workspace && python3 test_system.py


╔════════════════════════════════════════════════════════════════╗
║  📊 本周数据摘要                                               ║
╚════════════════════════════════════════════════════════════════╝

  📅 报告时间: 2026-06-01 02:14
  📦 总商品数: 150个（3个类目 × 50个）
  📈 显著变化: 99个商品

  Ponytail Extension:
    - 上升≥5名: 23件
    - 下降≥5名: 16件
    - 稳定商品: 11件

  Hair Topper:
    - 上升≥5名: 16件
    - 下降≥5名: 16件
    - 稳定商品: 18件

  Hair Extensions:
    - 上升≥5名: 16件
    - 下降≥5名: 12件
    - 稳定商品: 22件

  🚀 最大黑马: Uniwigs (上升14名)


╔════════════════════════════════════════════════════════════════╗
║  💡 提示                                                        ║
╚════════════════════════════════════════════════════════════════╝

  • 运行 generate_weekly_report.py 开始生成周报
  • 查看 reports/ 目录中的历史报告
  • 设置 crontab 实现每周自动执行
  • 查看 README.md 了解更多功能

  ⚠️  真实环境需要配置亚马逊数据源

EOF
