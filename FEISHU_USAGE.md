# 飞书消息发送工具包使用指南

## 📦 快速开始

### 1. 安装依赖
```bash
pip install requests
```

### 2. 发送消息（最简单方式）

```python
from feishu_send import send_text

send_text("Hello World!")
```

---

## 🎯 核心功能

### 📝 发送文本消息
```python
from feishu_send import send_text

# 发送简单文本
send_text("调研已完成！")

# 发送多行文本
send_text("""📊 调研报告

关键词: water bottle
产品数: 10
状态: 完成
""")
```

### 🎴 发送卡片消息
```python
from feishu_send import send_card

send_card(
    "调研完成",
    "关键词: water bottle\n\n产品数: 10个"
)
```

### 📊 发送调研报告
```python
from feishu_send import send_research_report

send_research_report(
    keyword="water bottle",
    product_count=10,
    keyword_count=50,
    report_file="报告.xlsx",
    duration=120.5
)
```

### ⏳ 发送进度更新
```python
from feishu_send import send_progress_update

send_progress_update(
    step=5,
    total_steps=10,
    status="正在分析评论..."
)
```

### ❌ 发送错误报告
```python
from feishu_send import send_error_report

send_error_report("数据抓取失败，请检查网络")
```

---

## 🔧 在调研RPA中集成

```python
from feishu_send import (
    send_text,
    send_card,
    send_research_report,
    send_progress_update
)

def run_research(keyword):
    # 启动通知
    send_card("🚀 开始调研", f"关键词: {keyword}")
    
    # 进度更新
    for i in range(1, 11):
        send_progress_update(i, 10, f"步骤 {i}/10")
        time.sleep(1)
    
    # 完成报告
    send_research_report(
        keyword=keyword,
        product_count=10,
        keyword_count=50,
        report_file="report.xlsx",
        duration=120.5
    )
```

---

## 📋 完整使用示例

```python
#!/usr/bin/env python3
"""
亚马逊调研RPA - 使用飞书通知
"""
import time
from feishu_send import (
    send_text,
    send_card,
    send_research_report,
    send_progress_update
)

def main():
    # 1. 发送启动消息
    send_card("🚀", "开始亚马逊产品调研")
    
    # 2. 模拟调研步骤
    steps = [
        "筛选产品",
        "分析竞品",
        "抓取评论",
        "分析差评",
        "分析好评",
        "挖掘关键词",
        "生成矩阵",
        "整理数据",
        "生成报告"
    ]
    
    for i, step in enumerate(steps, 1):
        send_progress_update(i, len(steps), step)
        time.sleep(1)  # 模拟处理
    
    # 3. 发送完成报告
    send_research_report(
        keyword="water bottle",
        product_count=15,
        keyword_count=68,
        report_file="amazon_wb_20240101.xlsx",
        duration=12.5
    )

if __name__ == "__main__":
    main()
```

---

## 🎨 高级用法

### 自定义卡片样式
```python
from feishu_send import send_card

content = """
**核心功能**:
- ✅ 产品筛选
- ✅ 竞品分析
- ✅ 评论分析

**使用方法**:
1. 安装 requests
2. 导入模块
3. 调用函数
"""

send_card("亚马逊调研RPA", content)
```

---

## 📞 技术支持

如遇问题，请检查：
1. 网络连接是否正常
2. Webhook URL是否正确
3. 飞书机器人是否正常

---

## 🎉 开始使用

```python
from feishu_send import send_text

# 发送第一条消息
send_text("🚀 飞书消息发送工具已准备就绪！")
```

现在您可以开始使用了！
