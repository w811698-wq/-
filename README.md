# 亚马逊假发类目BSR周报系统

## 功能概述

自动化抓取亚马逊假发类目BSR排名数据，与上周数据对比分析，识别排名显著变化的商品，并推送到飞书群。

## 监控类目

- Ponytail Extension（马尾接发）
- Hair Topper（头顶补发片）
- Hair Extensions（头发接发）

## 文件结构

```
/workspace/
├── amazon_bsr_reporter.py          # BSR数据抓取主程序
├── generate_sample_data.py        # 示例数据生成器
├── generate_weekly_report.py       # 周报生成和推送
├── run_weekly_report.sh             # 定时任务执行脚本
├── crontab_config.txt              # Crontab配置示例
├── data/                            # 数据存储目录
│   ├── current_*.json              # 当前数据
│   └── previous_week_*.json       # 上周数据
├── reports/                        # 报告存储目录
│   └── weekly_report_*.md          # 历史周报
└── logs/                           # 日志目录（可选）
```

## 使用方法

### 1. 手动执行周报

```bash
cd /workspace
python3 generate_weekly_report.py
```

### 2. 设置定时任务（每周一执行）

```bash
# 编辑crontab
crontab -e

# 添加以下行（每周一早上9点执行）
0 9 * * 1 /workspace/run_weekly_report.sh >> /workspace/logs/weekly_report.log 2>&1

# 保存并退出
```

### 3. 查看历史报告

```bash
ls -lh /workspace/reports/
cat /workspace/reports/weekly_report_20260601.md
```

## 报告内容

### 重点异动表格

每个类目显示:
- **排名上升≥5名的商品**: 品牌、排名变化、原因分析
- **排名下降≥5名的商品**: 品牌、排名变化、原因分析

### 原因分析

系统会自动识别以下原因:
- 🎟️ Coupon（优惠券）
- 💰 Discount/Sale（折扣促销）
- ⚡ Deal/Promotion（促销活动）
- 🔥 Prime Day Event（Prime会员日）
- 📊 自然波动

### 关键结论

- 本周显著变化商品总数
- 最大黑马商品
- 运营建议

## 飞书推送

报告会自动推送到配置的飞书群Webhook:
- 推送地址: `https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159`

## 数据抓取说明

系统通过抓取亚马逊搜索结果页面的BSR排名数据，包括:
- ASIN（商品标识）
- 产品标题
- 品牌
- 当前价格
- 当前BSR排名

**注意**: 真实环境需要处理反爬虫机制，建议:
- 使用代理IP池
- 添加延时请求
- 遵守robots.txt
- 考虑使用Jungle Scout、Helium 10等第三方API

## 扩展功能

### 添加新类目

编辑 `generate_weekly_report.py`:

```python
self.categories = [
    'Ponytail Extension',
    'Hair Topper',
    'Hair Extensions',
    '新类目名称'  # 添加新类目
]
```

### 修改Webhook

编辑 `generate_weekly_report.py`:

```python
self.feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址'
```

### 调整变化阈值

默认监测排名变化≥5名的商品，修改 `generate_weekly_report.py`:

```python
if product['rank_change'] >= 5:  # 改为 >= 10 可只监测更大变化
```

## 故障排查

### 飞书推送失败

1. 检查Webhook地址是否正确
2. 确认Webhook未被禁用
3. 查看飞书机器人权限设置

### 数据抓取失败

1. 网络连接是否正常
2. 亚马逊是否更新了页面结构
3. 是否触发了反爬虫机制

### 依赖问题

```bash
pip3 install requests
```

## 维护建议

1. **每周一执行**: 建议设置自动定时任务
2. **数据备份**: 定期备份 `data/` 目录
3. **日志监控**: 定期检查 `logs/` 日志文件
4. **报告归档**: 每月整理历史报告

## 联系方式

如有问题，请检查:
1. `/workspace/logs/` 中的错误日志
2. 飞书群推送消息
3. `/workspace/reports/` 中的报告文件
