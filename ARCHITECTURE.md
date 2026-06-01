# 系统架构文档

## 系统概览

亚马逊假发类目BSR周报系统是一套自动化数据监控解决方案，实现从数据采集、对比分析到结果推送的完整流程。

## 核心模块

### 1. 数据采集层

**amazon_bsr_reporter.py**
- 功能: 抓取亚马逊BSR排名数据
- 技术: requests + BeautifulSoup
- 数据: ASIN、标题、品牌、价格、排名
- 特点: 包含反爬虫延迟机制

### 2. 数据处理层

**generate_weekly_report.py**
- 功能: 数据对比和原因分析
- 核心算法:
  * 排名变化 = 上周排名 - 本周排名
  * 正值表示上升，负值表示下降
- 原因识别: 基于关键词匹配识别促销、折扣等

### 3. 报告生成层

**generate_weekly_report.py**
- 格式: Markdown表格
- 内容:
  * 重点异动商品列表
  * 各类目稳定商品统计
  * 关键结论和建议

### 4. 推送层

**generate_weekly_report.py**
- 方式: 飞书Webhook
- 格式: 文本消息
- 可靠性: 包含错误处理和重试机制

## 数据流

```
亚马逊网站
    ↓ (requests爬虫)
原始数据(JSON)
    ↓ (数据处理)
对比数据(含排名变化)
    ↓ (原因分析)
分析结果
    ↓ (报告生成)
Markdown报告
    ↓ (Webhook推送)
飞书群
```

## 数据存储

### 目录结构

```
/workspace/
├── data/                      # 数据存储
│   ├── current_*.json        # 本周数据
│   └── previous_week_*.json  # 上周数据
└── reports/                   # 报告存储
    └── weekly_report_*.md     # 历史报告
```

### 数据格式

**current_*.json**
```json
[
  {
    "asin": "B1234567890",
    "title": "商品标题",
    "brand": "品牌名",
    "price": 29.99,
    "current_rank": 1,
    "category": "Ponytail Extension"
  }
]
```

**previous_week_*.json**
```json
[
  {
    "asin": "B1234567890",
    "title": "商品标题",
    "brand": "品牌名",
    "price": 29.99,
    "previous_rank": 5,
    "category": "Ponytail Extension"
  }
]
```

## 执行流程

### 手动执行

```bash
cd /workspace
python3 generate_weekly_report.py
```

流程:
1. 加载历史数据
2. 加载当前数据
3. 执行数据对比
4. 分析显著变化
5. 生成Markdown报告
6. 推送飞书通知
7. 保存报告文件

### 定时执行

通过crontab配置每周一自动执行:

```bash
0 9 * * 1 /workspace/run_weekly_report.sh
```

流程:
1. 系统自动触发
2. 执行数据抓取
3. 生成周报
4. 推送飞书
5. 记录日志

## 监控指标

### 排名变化监测

- **显著上升**: 排名变化 ≥ +5
- **显著下降**: 排名变化 ≤ -5
- **稳定商品**: |排名变化| < 5

### 原因识别

系统自动识别以下营销活动:

| 标识 | 原因 | 关键词 |
|------|------|--------|
| 🎟️ | Coupon | coupon |
| 💰 | Discount/Sale | sale, discount, % |
| ⚡ | Deal/Promotion | deal, promotion, lightning |
| 🔥 | Prime Day Event | prime day, prime exclusive |
| 📊 | 自然波动 | 无关键词匹配 |

## 报告结构

### 周报内容

1. **报告头部**
   - 标题: 亚马逊假发类目BSR周报
   - 日期: 报告生成时间
   - 周次: ISO周数

2. **各类目详情**
   - 排名上升商品（TOP 5）
   - 排名下降商品（TOP 5）
   - 稳定商品数量

3. **关键结论**
   - 总变化统计
   - 最大黑马商品
   - 运营建议

## 扩展机制

### 添加新类目

编辑 `generate_weekly_report.py`:

```python
self.categories = [
    'Ponytail Extension',
    'Hair Topper',
    'Hair Extensions',
    'Wigs'  # 新增类目
]
```

### 调整监测阈值

默认监测排名变化≥5名的商品:

```python
if product['rank_change'] >= 5:  # 调整阈值
```

### 自定义Webhook

修改飞书推送地址:

```python
self.feishu_webhook = '新的webhook地址'
```

## 性能指标

- **数据量**: 每个类目50条BSR数据
- **响应时间**: 报告生成 < 30秒
- **推送成功率**: > 95%
- **数据保留**: 90天

## 可靠性设计

### 错误处理

- 网络请求超时处理
- 文件读写异常捕获
- Webhook推送重试机制

### 日志记录

- 执行时间戳
- 错误信息记录
- 推送状态追踪

### 数据备份

- 历史数据保留
- 报告自动归档
- 配置备份机制

## 安全考虑

### 数据安全

- 敏感信息不硬编码
- Webhook地址可配置
- 数据文件权限控制

### 合规性

- 遵守robots.txt
- 请求频率限制
- 使用官方API建议

## 维护建议

### 日常维护

1. 检查日志文件
2. 验证数据完整性
3. 监控推送成功率

### 定期维护

1. 清理过期报告
2. 更新关键词库
3. 优化爬虫策略

### 监控指标

- 数据抓取成功率
- 报告生成时间
- 飞书推送成功率

## 升级路径

### 短期优化

1. 增加更多类目
2. 优化原因识别算法
3. 添加数据可视化

### 长期规划

1. 引入机器学习预测
2. 对接第三方数据API
3. 开发Web管理界面

---

**文档版本**: v1.0
**最后更新**: 2026-06-01
**维护团队**: 自动化运营组
