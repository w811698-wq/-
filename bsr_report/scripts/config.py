import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

CATEGORIES = {
    "Ponytail Extension": {
        "url": "https://www.amazon.com/Best-Sellers-Beauty-Ponytail-Extensions/zgbs/beauty/11036071",
        "category_id": "ponytail"
    },
    "Hair Topper": {
        "url": "https://www.amazon.com/Best-Sellers-Beauty-Hair-Toppers/zgbs/beauty/11036061",
        "category_id": "topper"
    },
    "Hair Extensions": {
        "url": "https://www.amazon.com/Best-Sellers-Beauty-Hair-Extensions/zgbs/beauty/11036051",
        "category_id": "extensions"
    }
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive'
}

TOP_N = 100