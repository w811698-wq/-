import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

BASE_URL = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011'

def extract_brand_from_title(title):
    patterns = [
        r'^([A-Z][A-Z0-9]+(?:\s+[A-Z][A-Z0-9]+)*)\s+(?:Hair|Bangs|Clip|Ponytail|Bun|Extension)',
        r'^([A-Z][A-Z0-9]+)\s+',
    ]
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            return match.group(1)
    return 'Unknown'

def scrape_page(url):
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        seen_asins = set()
        asin_elements = soup.select('[data-asin]')

        for elem in asin_elements:
            asin = elem.get('data-asin', '').strip()
            if not asin or asin in seen_asins or asin == 'PAGING_STATE':
                continue
            seen_asins.add(asin)

            title_elem = elem.select_one('[class*="p13n-sc-truncated"]')
            if not title_elem:
                title_elem = elem.select_one('a[href*="/dp/"] span')
            if not title_elem:
                title_elem = elem.select_one('a span')

            title = title_elem.text.strip() if title_elem else 'N/A'
            title = re.sub(r'\s+', ' ', title)[:120]

            price_elem = elem.select_one('.a-price .a-offscreen')
            if not price_elem:
                price_elem = elem.select_one('[class*="price"]')
            price = price_elem.text.strip() if price_elem else 'N/A'

            brand = extract_brand_from_title(title)

            products.append({
                'asin': asin,
                'title': title,
                'price': price,
                'brand': brand
            })

        return products, soup
    except Exception as e:
        print(f"Error scraping page: {e}")
        return [], None

print("Starting BSR scrape...")
all_products = []
seen_asins = set()

page = 1
while len(all_products) < 100:
    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?pg={page}"

    print(f"Scraping page {page}...")
    products, soup = scrape_page(url)

    if not products:
        break

    for p in products:
        if p['asin'] not in seen_asins:
            seen_asins.add(p['asin'])
            all_products.append(p)

    if len(products) < 30:
        break
    page += 1

for i, p in enumerate(all_products[:100], 1):
    p['rank'] = i

today_data = all_products[:100]
print(f"\n=== Extracted {len(today_data)} products ===")

with open('/workspace/bsr_today.json', 'w', encoding='utf-8') as f:
    json.dump(today_data, f, ensure_ascii=False, indent=2)

print("Data saved to bsr_today.json")
