# 快速启动指南

## ✅ 已完成配置

1. ✅ BSR周报系统已部署
2. ✅ 监控类目已配置（3个类目）
3. ✅ 飞书Webhook已配置
4. ✅ 示例数据已生成
5. ✅ 测试报告已生成并推送成功

## 🚀 立即使用

### 运行周报

```bash
cd /workspace
python3 generate_weekly_report.py
```

### 设置每周自动执行（可选）

```bash
crontab -e
# 添加: 0 9 * * 1 /workspace/run_weekly_report.sh >> /workspace/logs/weekly_report.log 2>&1
```

## 📊 本周报告概览

**报告时间**: 2026年6月1日 02:14

### 重点异动

| 类目 | 上升≥5名 | 下降≥5名 | 稳定商品 |
|------|---------|---------|---------|
| Ponytail Extension | 23件 | 16件 | 11件 |
| Hair Topper | 16件 | 16件 | 18件 |
| Hair Extensions | 16件 | 12件 | 22件 |

### 本周亮点

- 🚀 **最大黑马**: Uniwigs 上升 14 名
- 📈 **总变化**: 99个商品显著变化
- ⚡ **促销影响**: 部分商品因Discount/Sale排名上升

### 原因分析

- 大部分变化标记为"自然波动"
- 2个商品检测到Discount/Sale原因
- 建议进一步调查排名大幅变化的商品

## 📁 文件位置

- **报告**: `/workspace/reports/weekly_report_20260601_021441.md`
- **数据**: `/workspace/data/current_*.json`
- **脚本**: `/workspace/*.py`

## 🔧 自定义配置

### 修改Webhook

编辑 `generate_weekly_report.py` 第6行

### 添加类目

编辑 `generate_weekly_report.py` 第9行 `self.categories` 列表

### 调整阈值

编辑 `generate_weekly_report.py` 中的 `if product['rank_change'] >= 5`

## 📞 故障排查

**飞书推送失败?**
1. 检查Webhook是否有效
2. 查看日志: `cat /workspace/logs/*.log`
3. 测试Webhook: 在飞书群添加测试消息

**数据抓取失败?**
1. 检查网络连接
2. 验证亚马逊页面结构
3. 查看错误日志

## 📅 维护计划

- 每周一自动生成周报（需配置crontab）
- 保留最近90天报告
- 定期备份数据文件

## 🎯 下一步

1. 查看详细报告: `cat /workspace/reports/weekly_report_20260601_021441.md`
2. 检查飞书群推送消息
3. 分析重点商品变化原因
4. 根据业务需求调整监控策略

---

**问题?** 查看 `/workspace/README.md` 完整文档
