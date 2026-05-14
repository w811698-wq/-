import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

asin = 'B0DGQ7K4DH'
url = f'https://www.amazon.com/dp/{asin}'

print(f"抓取商品详情：{asin}")

session = requests.Session()
response = session.get(url, headers=headers, timeout=30)
print(f"状态码：{response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

title_elem = soup.select_one('#productTitle')
title = title_elem.text.strip() if title_elem else 'N/A'
print(f"标题：{title}")

brand_elem = soup.select_one('#bylineInfo') or soup.select_one('[class*="brand"]') or soup.select_one('a[id*="badge"]')
if brand_elem:
    brand = brand_elem.text.strip()
    brand = re.sub(r'^Visit the\s+', '', brand)
    brand = re.sub(r'\s+Store$', '', brand)
else:
    brand = 'Unknown'
print(f"品牌：{brand}")

price_elem = soup.select_one('.a-price .a-offscreen') or soup.select_one('#priceblock_ourprice') or soup.select_one('.a-offscreen')
if price_elem:
    price = price_elem.text.strip()
else:
    price_elem = soup.select_one('[class*="price"]')
    price = price_elem.text.strip() if price_elem else 'N/A'
print(f"价格：{price}")
