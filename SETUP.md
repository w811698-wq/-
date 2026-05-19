# Amazon Isaic 产品评论监控 - 设置指南

## 已完成的文件
- [amazon_review_monitor.py](file:///workspace/amazon_review_monitor.py) - 主要监控脚本
- [amazon_review_data.json](file:///workspace/amazon_review_data.json) - 历史数据存储文件

## 设置每日定时任务（08:50）
使用 crontab 设置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（注意调整时区）
50 8 * * * /usr/bin/python3 /workspace/amazon_review_monitor.py >> /workspace/monitor.log 2>&1
```

## 脚本功能说明
1. 自动抓取4个 Amazon 产品的评分和评论数
2. 与历史数据比较，显示变化
3. 通过飞书 Webhook 发送报告
4. 保存最新数据到 JSON 文件

## 注意事项
- Amazon 有反爬虫机制，可能需要添加代理或使用 Amazon Product Advertising API
- 首次运行时无历史数据，不会显示变化
- 飞书消息已测试可以正常发送

