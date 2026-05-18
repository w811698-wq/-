import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

AMAZON_BASE_URL = os.getenv('AMAZON_BASE_URL', 'https://www.amazon.com')

CATEGORIES = {
    'Ponytail Extension': 'https://www.amazon.com/Best-Sellers-Beauty-Ponytail-Extensions/zgbs/beauty/11036091',
    'Hair Topper': 'https://www.amazon.com/Best-Sellers-Beauty-Hair-Toppers/zgbs/beauty/3773956011',
    'Hair Extensions': 'https://www.amazon.com/Best-Sellers-Beauty-Hair-Extensions/zgbs/beauty/3773955011'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

EXTERNAL_API_URL = os.getenv('AMAZON_DATA_API_URL', '')
EXTERNAL_API_KEY = os.getenv('AMAZON_DATA_API_KEY', '')

def scrape_bsr_data(category_url, retries=3):
    for attempt in range(retries):
        try:
            session = requests.Session()
            response = session.get(category_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            
            items = soup.find_all('div', {'data-asin': True})
            if not items:
                items = soup.find_all('li', {'data-asin': True})
            if not items:
                items = soup.select('li.zg-item-immersion')
            if not items:
                items = soup.select('.zg-item')
            
            if not items:
                print(f"  No items found on attempt {attempt + 1}")
                continue
            
            for item in items[:50]:
                asin = item.get('data-asin')
                if not asin:
                    continue
                
                rank = None
                rank_elem = item.find('span', class_='zg-bdg-text')
                if not rank_elem:
                    rank_elem = item.find('span', class_='a-badge-text')
                if not rank_elem:
                    rank_elem = item.find('span', class_='zg-rank')
                if not rank_elem:
                    rank_text = item.get('data-rank')
                    if rank_text:
                        try:
                            rank = int(rank_text)
                        except ValueError:
                            pass
                if rank_elem:
                    rank_text = rank_elem.get_text(strip=True).replace('#', '')
                    try:
                        rank = int(rank_text)
                    except ValueError:
                        pass
                
                title = None
                title_elem = item.find('span', class_='zg-item')
                if not title_elem:
                    title_elem = item.find('span', class_='a-size-base a-color-base')
                if not title_elem:
                    title_elem = item.find('div', class_='p13n-sc-truncate')
                if not title_elem:
                    title_elem = item.find('h2', class_='a-size-mini')
                if not title_elem:
                    title_elem = item.find('a', class_='a-size-small')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                
                brand = None
                brand_elem = item.find('span', class_='a-size-small a-color-secondary')
                if not brand_elem:
                    brand_elem = item.find('div', class_='a-row a-size-small')
                if not brand_elem:
                    brand_elem = item.find('span', class_='a-color-secondary')
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
                
                price = None
                price_elem = item.find('span', class_='p13n-sc-price')
                if not price_elem:
                    price_elem = item.find('span', class_='a-price-whole')
                if not price_elem:
                    price_elem = item.find('span', class_='a-color-price')
                if price_elem:
                    price = price_elem.get_text(strip=True)
                
                has_coupon = 'coupon' in str(item).lower() or 'zg-coupon' in str(item)
                has_deal = 'deal' in str(item).lower() and ('a-badge' in str(item) or 'deal' in str(item).lower())
                has_lightning_deal = 'lightning' in str(item).lower()
                
                products.append({
                    'asin': asin,
                    'rank': rank,
                    'title': title,
                    'brand': brand,
                    'price': price,
                    'has_coupon': has_coupon,
                    'has_deal': has_deal,
                    'has_lightning_deal': has_lightning_deal,
                    'scrape_time': datetime.now().isoformat()
                })
            
            if products:
                return products
            
        except Exception as e:
            print(f"Error scraping {category_url} on attempt {attempt + 1}: {str(e)}")
            continue
    
    return []

def fetch_from_external_api(category_key):
    if not EXTERNAL_API_URL:
        return None
    
    try:
        headers = {'Authorization': f'Bearer {EXTERNAL_API_KEY}'} if EXTERNAL_API_KEY else {}
        params = {'category': category_key}
        response = requests.get(EXTERNAL_API_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"External API error for {category_key}: {str(e)}")
        return None

def get_all_categories_data():
    all_data = {}
    
    for category_name, category_url in CATEGORIES.items():
        print(f"Fetching {category_name}...")
        
        external_data = fetch_from_external_api(category_name)
        if external_data:
            all_data[category_name] = external_data
            print(f"Got {len(external_data)} products from external API for {category_name}")
            continue
        
        data = scrape_bsr_data(category_url)
        all_data[category_name] = data
        print(f"Scraped {len(data)} products from Amazon for {category_name}")
    
    if all([len(data) == 0 for data in all_data.values()]):
        print("WARNING: No data fetched. Please configure external API or provide manual data.")
        print("Add AMAZON_DATA_API_URL and AMAZON_DATA_API_KEY to .env file")
        return None
    
    return all_data

def save_data(data, filename):
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {filepath}")

def load_data(filename):
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_last_week_data():
    last_week_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    filename = f'bsr_data_{last_week_date}.json'
    return load_data(filename)

def compare_with_last_week(current_data, last_week_data):
    comparison = {}
    
    for category, current_products in current_data.items():
        comparison[category] = []
        last_week_products = last_week_data.get(category, []) if last_week_data else []
        
        last_week_dict = {p['asin']: p for p in last_week_products}
        
        for product in current_products:
            asin = product['asin']
            last_week_product = last_week_dict.get(asin)
            
            rank_change = 0
            if last_week_product and last_week_product.get('rank') and product.get('rank'):
                rank_change = last_week_product['rank'] - product['rank']
            
            comparison[category].append({
                **product,
                'rank_change': rank_change
            })
    
    return comparison

def analyze_rank_changes(comparison_data):
    rising_products = []
    falling_products = []
    stable_products = []
    
    for category, products in comparison_data.items():
        for product in products:
            rank_change = product.get('rank_change', 0)
            
            if rank_change >= 5:
                rising_products.append({
                    'category': category,
                    **product
                })
            elif rank_change <= -5:
                falling_products.append({
                    'category': category,
                    **product
                })
            else:
                stable_products.append({
                    'category': category,
                    **product
                })
    
    return rising_products, falling_products, stable_products

def analyze_change_reasons(product):
    reasons = []
    
    if product.get('has_coupon'):
        reasons.append('优惠券')
    if product.get('has_deal'):
        reasons.append('促销活动')
    if product.get('has_lightning_deal'):
        reasons.append('Lightning Deal')
    
    if not reasons:
        reasons.append('未知')
    
    return ', '.join(reasons)

def generate_feishu_report(rising_products, falling_products, stable_products):
    today = datetime.now().strftime('%Y年%m月%d日')
    
    report = f"📊 **亚马逊假发类目BSR排名周报**\n\n"
    report += f"📅 日期：{today}\n\n"
    
    report += "🚀 **排名上升≥5名的商品**\n"
    if rising_products:
        report += "| 类目 | 品牌 | 排名变化 | 原因 |\n"
        report += "|------|------|----------|------|\n"
        for p in rising_products:
            reason = analyze_change_reasons(p)
            report += f"| {p['category']} | {p['brand'] or 'N/A'} | +{p['rank_change']} | {reason} |\n"
    else:
        report += "无\n"
    
    report += "\n📉 **排名下降≥5名的商品**\n"
    if falling_products:
        report += "| 类目 | 品牌 | 排名变化 | 原因 |\n"
        report += "|------|------|----------|------|\n"
        for p in falling_products:
            reason = analyze_change_reasons(p)
            report += f"| {p['category']} | {p['brand'] or 'N/A'} | {p['rank_change']} | {reason} |\n"
    else:
        report += "无\n"
    
    category_stable_counts = {}
    for p in stable_products:
        category = p['category']
        category_stable_counts[category] = category_stable_counts.get(category, 0) + 1
    
    report += "\n📊 **各品类稳定商品数量**\n"
    report += "| 类目 | 稳定商品数 |\n"
    report += "|------|------------|\n"
    for category, count in category_stable_counts.items():
        report += f"| {category} | {count} |\n"
    
    total_rising = len(rising_products)
    total_falling = len(falling_products)
    total_stable = len(stable_products)
    
    report += "\n🎯 **关键结论**\n"
    report += f"- 本周共有 {total_rising} 个商品排名上升≥5名\n"
    report += f"- 本周共有 {total_falling} 个商品排名下降≥5名\n"
    report += f"- 本周共有 {total_stable} 个商品排名稳定\n"
    
    if total_rising > total_falling:
        report += "- ✅ 整体趋势：类目表现向好\n"
    elif total_falling > total_rising:
        report += "- ❌ 整体趋势：类目表现下滑\n"
    else:
        report += "- ⚠️ 整体趋势：类目表现平稳\n"
    
    return report

def send_to_feishu(message):
    webhook_url = os.getenv('FEISHU_WEBHOOK')
    if not webhook_url:
        print("飞书Webhook未配置")
        return False
    
    payload = {
        "msg_type": "markdown",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        print("飞书消息发送成功")
        return True
    except Exception as e:
        print(f"飞书消息发送失败: {str(e)}")
        return False

def main():
    print("开始执行亚马逊BSR排名周报任务...")
    
    current_data = get_all_categories_data()
    
    if current_data is None:
        print("错误：无法获取任何数据。请配置外部API或手动提供数据。")
        return
    
    today_str = datetime.now().strftime('%Y%m%d')
    save_data(current_data, f'bsr_data_{today_str}.json')
    
    last_week_data = get_last_week_data()
    
    if not last_week_data:
        print("错误：未找到上周数据，无法进行对比分析。")
        print("请确保data目录中存在上周的数据文件（格式：bsr_data_YYYYMMDD.json）")
        return
    
    comparison_data = compare_with_last_week(current_data, last_week_data)
    
    rising, falling, stable = analyze_rank_changes(comparison_data)
    
    report = generate_feishu_report(rising, falling, stable)
    
    print("\n生成的周报内容：")
    print(report)
    
    send_to_feishu(report)
    
    print("任务完成")

if __name__ == '__main__':
    main()
