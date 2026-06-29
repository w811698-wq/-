"""
配置模块
"""

# 飞书Webhook
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

# 监控类目
CATEGORIES = [
    {
        "id": "Ponytail Extension",
        "amazon_url": "https://www.amazon.com/s?rh=n%3A13197621011&fs=true&ref=lp_13197621011_srn",
        "bestseller_url": "https://www.amazon.com/gp/bestsellers/beauty/13197621011/"
    },
    {
        "id": "Hair Topper",
        "amazon_url": "https://www.amazon.com/s?rh=n%3A13197923011&fs=true&ref=lp_13197923011_srn",
        "bestseller_url": "https://www.amazon.com/gp/bestsellers/beauty/13197923011/"
    },
    {
        "id": "Hair Extensions",
        "amazon_url": "https://www.amazon.com/s?rh=n%3A13191831011&fs=true&ref=lp_13191831011_srn",
        "bestseller_url": "https://www.amazon.com/gp/bestsellers/beauty/13191831011/"
    }
]

# 数据存储路径
DATA_DIR = "/workspace/data"
CURRENT_DATA_DIR = f"{DATA_DIR}/current"
PREVIOUS_DATA_DIR = f"{DATA_DIR}/previous"

# 变化阈值
RANK_CHANGE_THRESHOLD = 5

# 用户代理（用于爬虫）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
