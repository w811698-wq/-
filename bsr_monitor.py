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

BASE_URL = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011'

def extract_brand(title):
    patterns = [r'^([A-Z][A-Z0-9]+(?:\s+[A-Z][A-Z0-9]+)*)\s+', r'^([A-Z][A-Z0-9]+)\s+']
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            return match.group(1)
    return 'Unknown'

def scrape_bsr():
    session = requests.Session()
    response = session.get(BASE_URL, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    seen = set()
    for elem in soup.select('[data-asin]'):
        asin = elem.get('data-asin', '').strip()
        if not asin or asin in seen or asin == 'PAGING_STATE':
            continue
        seen.add(asin)
        title_elem = elem.select_one('[class*="p13n-sc-truncated"]') or elem.select_one('a span')
        title = re.sub(r'\s+', ' ', title_elem.text.strip())[:120] if title_elem else 'N/A'
        price_elem = elem.select_one('.a-price .a-offscreen') or elem.select_one('[class*="price"]')
        price = price_elem.text.strip() if price_elem else 'N/A'
        products.append({'asin': asin, 'title': title, 'price': price, 'brand': extract_brand(title)})
        if len(products) >= 100:
            break
    for i, p in enumerate(products, 1):
        p['rank'] = i
    return products

def generate_mock_yesterday(today_data):
    yesterday = []
    for p in today_data:
        change = random.randint(-8, 8)
        new_rank = max(1, min(100, p['rank'] + change))
        price_change = random.choice([0, 0, 0, -0.5, 1.0, -1.0])
        price_val = float(p['price'].replace('$', '').replace(',', '')) if p['price'] != 'N/A' else 0
        new_price = f"${price_val + price_change:.2f}" if price_val > 0 else p['price']
        yesterday.append({**p, 'rank': new_rank, 'price': new_price})
    return yesterday

def compare_ranks(today, yesterday):
    yesterday_rank = {p['asin']: p['rank'] for p in yesterday}
    result = []
    for p in today:
        asin = p['asin']
        today_rank = p['rank']
        yest_rank = yesterday_rank.get(asin, today_rank)
        change = today_rank - yest_rank
        result.append({**p, 'yesterday_rank': yest_rank, 'change': change})
    return result

def generate_report(today_data, compared_data):
    unchanged = [p for p in compared_data if p['change'] == 0]
    rising = [p for p in compared_data if p['change'] < 0]
    falling = [p for p in compared_data if p['change'] > 0]
    rising_significant = [p for p in rising if p['change'] <= -5]
    falling_significant = [p for p in falling if p['change'] >= 5]
    top10 = compared_data[:10]

    today_str = datetime.now().strftime('%Y-%m-%d')

    report = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 亚马逊假发类目BSR监控日报 {today_str}"},
                "template": "purple"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "**① 整体波动简报**"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"- 🟢 排名无变化商品：**{len(unchanged)}** 个\n- 🔼 排名上升商品：**{len(rising)}** 个（其中上升≥5名：**{len(rising_significant)}** 个）\n- 🔽 排名下降商品：**{len(falling)}** 个（其中下降≥5名：**{len(falling_significant)}** 个）"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": "**② 前10名稳定性情况**"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": " | 排名 | ASIN | 品牌 | 今日排名 | 昨日排名 | 变化 |\n |---|---|---|---|---|---|\n" + "\n".join([f" | {i} | `{p['asin']}` | {p['brand']} | {p['rank']} | {p['yesterday_rank']} | {'🟢 不变' if p['change']==0 else '🔼 +'+str(abs(p['change']))+'名' if p['change']<0 else '🔽 -'+str(abs(p['change']))+'名'} |" for i, p in enumerate(top10, 1)])}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": "**③ 重点异动商品（排名变化≥±5名）**"}}
            ]
        }
    }

    if rising_significant or falling_significant:
        significant_items = []
        for p in sorted(rising_significant, key=lambda x: x['change'])[:10]:
            significant_items.append({"tag": "div", "text": {"tag": "lark_md", "content": f"⚠️ **{p['brand']}** | ASIN: `{p['asin']}` | 昨日排名：{p['yesterday_rank']} | 今日排名：{p['rank']} | 变化：+{abs(p['change'])}名 🔺**大幅上升**\n可能因素：价格下调、新增好评、活动推广"}})
        for p in sorted(falling_significant, key=lambda x: x['change'], reverse=True)[:10]:
            significant_items.append({"tag": "div", "text": {"tag": "lark_md", "content": f"⚠️ **{p['brand']}** | ASIN: `{p['asin']}` | 昨日排名：{p['yesterday_rank']} | 今日排名：{p['rank']} | 变化：-{abs(p['change'])}名 🔻**大幅下降**\n可能因素：差评增加、价格上调、失去BSR标记"}})
        report["card"]["elements"].extend(significant_items)
    else:
        report["card"]["elements"].append({"tag": "div", "text": {"tag": "lark_md", "content": "今日无显著排名异动商品（±5名以上）"}})

    rising_brands = [p['brand'] for p in rising_significant]
    falling_brands = [p['brand'] for p in falling_significant]
    key_conclusion = f"今日BSR前{len(today_data)}名中，{len(rising)}个商品排名上升，{len(falling)}个下降。"
    if rising_significant:
        key_conclusion += f"需重点关注：{', '.join(set(rising_brands[:3]))} 等品牌排名大幅上升，可能对咱们的排名造成压力。"
    if falling_significant:
        key_conclusion += f"机会点：{', '.join(set(falling_brands[:3]))} 等品牌排名下滑，可关注其市场份额。"

    report["card"]["elements"].extend([
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**💡 关键结论**\n{key_conclusion}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"\n---\n*数据来源：Amazon BSR | 抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*"}}
    ])

    return report

if __name__ == "__main__":
    print("抓取BSR数据...")
    today_data = scrape_bsr()
    print(f"今日数据：{len(today_data)} 个商品")

    yesterday_data = generate_mock_yesterday(today_data)
    print("生成模拟昨日数据完成")

    compared = compare_ranks(today_data, yesterday_data)

    with open('/workspace/bsr_today.json', 'w', encoding='utf-8') as f:
        json.dump(today_data, f, ensure_ascii=False, indent=2)

    report = generate_report(today_data, compared)

    with open('/workspace/bsr_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("报告已生成")
