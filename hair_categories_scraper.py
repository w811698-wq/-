import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def extract_brand(title):
    patterns = [
        r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+(?:Hair|Ponytail|Topper|Extension|Clip)',
        r'^([A-Z][A-Za-z]+)\s+',
        r'^([A-Za-z]+\s+[A-Za-z]+)\s+(?:Hair|Ponytail|Topper)',
    ]
    for pattern in patterns:
        match = re.match(pattern, title.strip())
        if match:
            brand = match.group(1).strip()
            if 2 <= len(brand) <= 25:
                return brand
    return 'Unknown'

print("抓取 Hairpieces 主类目数据...")
url = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011'
session = requests.Session()
response = session.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

all_products = []
seen_asins = set()

for elem in soup.select('[data-asin]'):
    asin = elem.get('data-asin', '').strip()
    if not asin or asin in seen_asins or asin == 'PAGING_STATE':
        continue
    seen_asins.add(asin)
    
    title_elem = elem.select_one('[class*="p13n-sc-truncated"]') or elem.select_one('a[href*="/dp/"] span') or elem.select_one('a span')
    title = re.sub(r'\s+', ' ', title_elem.text.strip())[:120] if title_elem else 'N/A'
    
    price_elem = elem.select_one('.a-price .a-offscreen') or elem.select_one('[class*="price"]')
    price = price_elem.text.strip() if price_elem else 'N/A'
    
    brand = extract_brand(title)
    
    all_products.append({
        'rank': len(all_products) + 1,
        'asin': asin,
        'title': title,
        'price': price,
        'brand': brand
    })

print(f"成功抓取 {len(all_products)} 个商品")

target_asin = 'B0DGQ7K4DH'
print(f"\n抓取指定商品 {target_asin}...")

product_url = f'https://www.amazon.com/dp/{target_asin}'
resp = session.get(product_url, headers=headers, timeout=30)
soup2 = BeautifulSoup(resp.text, 'html.parser')

title_elem = soup2.select_one('#productTitle')
title = title_elem.text.strip() if title_elem else 'N/A'

brand_elem = soup2.select_one('#bylineInfo') or soup2.select_one('[brand]')
if brand_elem:
    brand = brand_elem.text.strip().replace('Visit the ', '').replace(' Store', '')
else:
    brand = extract_brand(title)

price_elem = soup2.select_one('.a-price .a-offscreen') or soup2.select_one('#priceblock_ourprice') or soup2.select_one('#priceblock_dealprice')
price = price_elem.text.strip() if price_elem else 'N/A'

target_product = {
    'rank': 0,
    'asin': target_asin,
    'title': title,
    'price': price,
    'brand': brand
}

print(f"商品信息：")
print(f"  标题：{title}")
print(f"  品牌：{brand}")
print(f"  价格：{price}")

ponytail_products = [p for p in all_products if 'Ponytail' in p['title'] or ' pony' in p['title'].lower()]
topper_products = [p for p in all_products if 'topper' in p['title'].lower() and 'bangs' not in p['title'].lower()]
extension_products = [p for p in all_products if ('Extension' in p['title'] or 'Extensions' in p['title']) and 'Pony' not in p['title']]

topper_products.append(target_product)

results = {
    'Ponytail Extension': ponytail_products,
    'Hair Topper': topper_products,
    'Hair Extensions': extension_products
}

with open('/workspace/hair_categories.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("📊 各品类商品及品牌分布：")
print("="*80)

for name, products in results.items():
    brands = set(p['brand'] for p in products if p['brand'] != 'Unknown')
    print(f"\n📦 {name}")
    print(f"商品数量：{len(products)}")
    print(f"品牌数量：{len(brands)}")
    if brands:
        print(f"品牌列表：{', '.join(sorted(brands))}")
    else:
        print("品牌列表：无")
    
    if products:
        print("\n详细商品：")
        for p in products:
            print(f"  {p['brand']} | {p['asin']} | {p['price']} | {p['title'][:60]}...")

all_brands = set()
for products in results.values():
    for p in products:
        if p['brand'] != 'Unknown':
            all_brands.add(p['brand'])

print("\n" + "="*80)
print(f"📈 总品牌数量：{len(all_brands)}")
print(f"所有品牌：{', '.join(sorted(all_brands))}")
