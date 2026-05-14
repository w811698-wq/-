import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DATA_DIR = os.path.join(BASE_DIR, 'data')

for dir_path in [OUTPUT_DIR, DATA_DIR]:
    os.makedirs(dir_path, exist_ok=True)

CHROME_DRIVER_PATH = None
HEADLESS = False
TIMEOUT = 30

SELLER_SPIRIT_URL = 'https://www.sellersprite.com/'
XIYOU_URL = 'https://www.xiyouamazon.com/'
AMAZON_URL = 'https://www.amazon.com/'

PRODUCT_FILTERS = {
    'min_price': 10,
    'max_price': 100,
    'min_rating': 4.0,
    'min_monthly_sales': 100,
    'min_reviews': 50,
    'max_bsr': 10000,
    'max_days_online': 365
}

KEYWORD_FILTERS = {
    'min_search_volume': 1000,
    'max_competition': 0.7
}

SCHEDULE = {
    'enabled': False,
    'frequency': 'daily',
    'time': '08:00'
}
