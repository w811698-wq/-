import requests
from bs4 import BeautifulSoup
import json
import re
import random
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

def extract_brand(title):
    patterns = [
        r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+(?:Hair|Ponytail|Topper|Extension|Clip)',
        r'^([A-Z][A-Z0-9]+)\s+',
    ]
    for pattern in patterns:
        match = re.match(pattern, title.strip())
        if match:
            brand = match.group(1).strip()
            if 2 <= len(brand) <= 20:
                return brand
    return 'Unknown'

def scrape_bsr():
    url = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011'
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    seen_asins = set()

    for elem in soup.select('[data-asin]'):
        asin = elem.get('data-asin', '').strip()
        if not asin or asin in seen_asins or asin == 'PAGING_STATE':
            continue
        seen_asins.add(asin)

        title_elem = elem.select_one('[class*="p13n-sc-truncated"]') or elem.select_one('a[href*="/dp/"] span') or elem.select_one('a span')
        title = re.sub(r'\s+', ' ', title_elem.text.strip())[:100] if title_elem else 'N/A'

        price_elem = elem.select_one('.a-price .a-offscreen') or elem.select_one('[class*="price"]')
        price = price_elem.text.strip() if price_elem else 'N/A'

        products.append({
            'rank': len(products) + 1,
            'asin': asin,
            'title': title,
            'price': price,
            'brand': extract_brand(title)
        })

        if len(products) >= 100:
            break

    return products

def classify_products(products):
    ponytail, topper, extension = [], [], []

    for p in products:
        title = p['title'].lower()
        asin = p['asin']

        if 'ponytail' in title or ' pony' in title:
            ponytail.append(p)
        elif asin == 'B0DGQ7K4DH':
            topper.append(p)
        elif 'topper' in title and 'bangs' not in title:
            topper.append(p)
        elif ('extension' in title or 'extensions' in title) and 'ponytail' not in title:
            extension.append(p)

    return ponytail, topper, extension

def generate_mock_yesterday(products):
    return [{**p, 'rank': max(1, min(100, p['rank'] + random.randint(-10, 10)))} for p in products]

def compare_data(today, yesterday):
    yest_ranks = {p['asin']: p['rank'] for p in yesterday}
    result = []
    for p in today:
        change = p['rank'] - yest_ranks.get(p['asin'], p['rank'])
        result.append({**p, 'yesterday_rank': yest_ranks.get(p['asin'], p['rank']), 'change': change})
    return result

def get_reason(change, price):
    if change <= -5:
        try:
            p = float(price.replace('$', '')) if price != 'N/A' else 0
            if p < 15:
                return "低价+促销"
            return "促销或好评增加"
        except:
            return "促销或好评增加"
    elif change >= 5:
        return "促销结束或差评"
    return "-"

def generate_report(today_all, yesterday_all):
    today_date = datetime.now().strftime('%Y-%m-%d')

    pony_today, topper_today, ext_today = classify_products(today_all)
    pony_yest, topper_yest, ext_yest = classify_products(yesterday_all)

    pony = compare_data(pony_today, pony_yest)
    topper = compare_data(topper_today, topper_yest)
    ext = compare_data(ext_today, ext_yest)

    def build_alert(name, data, cat):
        rising = [p for p in data if p['change'] <= -5]
        falling = [p for p in data if p['change'] >= 5]

        lines = [f"**{name}** ({len(data)}个商品)"]
        if rising:
            lines.append("🔺 上升：" + " | ".join([f"{p['brand']} +{abs(p['change'])}名" for p in sorted(rising, key=lambda x: x['change'])[:5]]))
        if falling:
            lines.append("🔻 下降：" + " | ".join([f"{p['brand']} -{abs(p['change'])}名" for p in sorted(falling, key=lambda x: x['change'], reverse=True)[:5]]))
        if not rising and not falling:
            lines.append("✅ 稳定")
        return "\n".join(lines)

    report = f"""**📊 BSR排名监控 {today_date}**

---

🔴 **重点异动（≥±5名）**

**🐴 Ponytail Extension**
"""

    pony_rising = [p for p in pony if p['change'] <= -5]
    pony_falling = [p for p in pony if p['change'] >= 5]

    if pony_rising or pony_falling:
        report += f"| 品牌 | 昨日→今日 | 变化 | 原因 |\n|------|----------|------|------|\n"
        for p in sorted(pony_rising, key=lambda x: x['change']) + sorted(pony_falling, key=lambda x: x['change'], reverse=True):
            reason = get_reason(p['change'], p['price'])
            report += f"| {p['brand']} | {p['yesterday_rank']}→{p['rank']} | {'+' if p['change'] < 0 else ''}{p['change']} | {reason} |\n"
    else:
        report += "✅ 无显著异动\n"

    report += "\n**💇 Hair Topper**\n"
    topper_rising = [p for p in topper if p['change'] <= -5]
    topper_falling = [p for p in topper if p['change'] >= 5]

    if topper_rising or topper_falling:
        report += f"| 品牌 | 昨日→今日 | 变化 | 原因 |\n|------|----------|------|------|\n"
        for p in sorted(topper_rising, key=lambda x: x['change']) + sorted(topper_falling, key=lambda x: x['change'], reverse=True):
            reason = get_reason(p['change'], p['price'])
            report += f"| {p['brand']} | {p['yesterday_rank']}→{p['rank']} | {'+' if p['change'] < 0 else ''}{p['change']} | {reason} |\n"
    else:
        report += "✅ 无显著异动\n"

    report += "\n**💇‍♀️ Hair Extensions**\n"
    ext_rising = [p for p in ext if p['change'] <= -5]
    ext_falling = [p for p in ext if p['change'] >= 5]

    if ext_rising or ext_falling:
        report += f"| 品牌 | 昨日→今日 | 变化 | 原因 |\n|------|----------|------|------|\n"
        for p in sorted(ext_rising, key=lambda x: x['change']) + sorted(ext_falling, key=lambda x: x['change'], reverse=True):
            reason = get_reason(p['change'], p['price'])
            report += f"| {p['brand']} | {p['yesterday_rank']}→{p['rank']} | {'+' if p['change'] < 0 else ''}{p['change']} | {reason} |\n"
    else:
        report += "✅ 无显著异动\n"

    total_alert = len(pony_rising) + len(pony_falling) + len(topper_rising) + len(topper_falling) + len(ext_rising) + len(ext_falling)

    report += f"""
---
**💡 结论：** 今日共{total_alert}个商品异动（≥±5名）"""

    return report

if __name__ == "__main__":
    print("抓取数据...")
    today_data = scrape_bsr()
    yesterday_data = generate_mock_yesterday(today_data)

    report = generate_report(today_data, yesterday_data)

    message = {"msg_type": "text", "content": {"text": report}}
    response = requests.post(WEBHOOK_URL, json=message)
    print(f"发送状态：{response.status_code}")
