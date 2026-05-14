# 亚马逊产品调研自动化RPA

完整的亚马逊产品调研自动化解决方案，支持卖家精灵和西柚插件，实现12项核心调研功能的自动化执行。

## 功能特性

- ✅ 自动筛选产品（价格、评分、销量、Review等条件）
- ✅ 自动分析竞品打法（主图、A+、视频、变体等）
- ✅ 自动抓取和分析差评/好评
- ✅ 自动生成产品优化方案
- ✅ 自动分析目标人群
- ✅ 自动生成人群×场景×关键词矩阵
- ✅ 自动挖掘和筛选关键词
- ✅ 自动生成Listing关键词组合
- ✅ 自动匹配卖点对应人群
- ✅ 自动生成卖点策略
- ✅ 自动生成强化版矩阵分析
- ✅ 支持定时自动执行

## 项目结构

```
/workspace/
├── config.py              # 配置文件
├── browser.py             # 浏览器自动化模块
├── plugins.py             # 卖家精灵/西柚插件集成
├── data_processor.py      # 数据处理和分析模块
├── excel_exporter.py      # Excel导出模块
├── amazon_research.py     # 核心调研引擎
├── main.py                # 主程序入口
├── scheduler.py           # 定时调度模块
├── requirements.txt       # 依赖包列表
├── output/                # 输出目录
└── data/                  # 数据目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示模式

```bash
python main.py --demo
```

### 3. 实际使用

首先修改 `config.py` 配置文件，设置好相关参数，然后运行：

```bash
python main.py --keyword "water bottle" --brand "MyBrand"
```

### 4. 定时任务

编辑 `config.py` 启用定时任务：

```python
SCHEDULE = {
    'enabled': True,
    'frequency': 'daily',  # daily 或 weekly
    'time': '08:00'
}
```

然后运行：

```bash
python scheduler.py
```

## 模块说明

### config.py
配置文件，包含：
- 输出目录设置
- Chrome浏览器配置
- 产品筛选条件
- 关键词筛选条件
- 定时任务配置

### browser.py
浏览器自动化管理，基于 Selenium：
- 自动启动/关闭Chrome
- 元素定位和交互
- 页面滚动和等待

### plugins.py
第三方插件集成：
- SellerSpirit（卖家精灵）
- XiYou（西柚插件）

### data_processor.py
数据处理模块：
- 文本清洗和关键词提取
- 评论分析（差评/好评）
- 关键词去重和筛选
- 矩阵生成
- 卖点策略生成

### excel_exporter.py
Excel导出模块：
- 多Sheet页导出
- 包含产品池、打法分析、评论分析、关键词库等
- 自动时间戳命名

### amazon_research.py
核心调研引擎，实现12项调研步骤

## 输出说明

生成的Excel报告包含以下Sheet：

1. **产品池** - 候选产品列表
2. **打法分析** - 竞品打法分析
3. **差评分析** - 差评痛点关键词
4. **好评分析** - 好评亮点关键词
5. **关键词库** - 筛选后的关键词
6. **矩阵分析** - 人群×场景×关键词矩阵
7. **卖点策略** - 核心/差异化/信任卖点

## 注意事项

⚠️ 重要提示：
- 需要卖家精灵/西柚插件的有效账号
- 实际使用前需要根据页面结构调整选择器
- 建议先在小范围内测试
- 遵守亚马逊和第三方平台的使用条款

## 技术栈

- Python 3.7+
- Selenium 4.x
- Pandas
- OpenPyXL
- BeautifulSoup4
- Schedule

## 许可证

MIT License
