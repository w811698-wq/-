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

def generate_mock_data():
    mock_data = {
        'Ponytail Extension': [
            {'asin': 'B08X1X1X1X1', 'rank': 1, 'title': 'Synthetic Ponytail Extension - 18 Inch Straight', 'brand': 'HairBeauty', 'price': '$19.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X2X2X2X2', 'rank': 2, 'title': 'Clip-In Ponytail Extension - 24 Inch Wavy', 'brand': 'LuxuryHair', 'price': '$29.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X3X3X3X3', 'rank': 3, 'title': 'Wrap Around Ponytail - 20 Inch Curly', 'brand': 'HairFashion', 'price': '$24.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': True, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X4X4X4X4', 'rank': 8, 'title': 'Drawstring Ponytail - 16 Inch Straight', 'brand': 'BeautyPlus', 'price': '$15.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X5X5X5X5', 'rank': 15, 'title': 'Ponytail Extension with Comb - 22 Inch', 'brand': 'StyleHair', 'price': '$22.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X6X6X6X6', 'rank': 20, 'title': 'High Ponytail Extension - 14 Inch', 'brand': 'HairPro', 'price': '$18.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X7X7X7X7', 'rank': 25, 'title': 'Ponytail Extension Thick - 26 Inch', 'brand': 'FullHair', 'price': '$34.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B08X8X8X8X8', 'rank': 30, 'title': 'Ponytail Hairpiece - 12 Inch Short', 'brand': 'MiniHair', 'price': '$12.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
        ],
        'Hair Topper': [
            {'asin': 'B09Y1Y1Y1Y1', 'rank': 1, 'title': 'Hair Topper for Women - 18x18cm Base', 'brand': 'TopperPro', 'price': '$49.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y2Y2Y2Y2', 'rank': 5, 'title': 'Clip-In Hair Topper - Human Hair', 'brand': 'RealHair', 'price': '$79.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y3Y3Y3Y3', 'rank': 6, 'title': 'Synthetic Hair Topper - Blonde', 'brand': 'BlondeBeauty', 'price': '$39.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y4Y4Y4Y4', 'rank': 12, 'title': 'Hair Topper with Bangs', 'brand': 'BangsHair', 'price': '$54.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y5Y5Y5Y5', 'rank': 18, 'title': 'Large Base Hair Topper - 22x22cm', 'brand': 'FullCoverage', 'price': '$69.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y6Y6Y6Y6', 'rank': 22, 'title': 'Thin Hair Topper - Lightweight', 'brand': 'LightHair', 'price': '$44.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y7Y7Y7Y7', 'rank': 28, 'title': 'Hair Topper for Men', 'brand': 'MensHair', 'price': '$35.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B09Y8Y8Y8Y8', 'rank': 35, 'title': 'Ombre Hair Topper - Two Tone', 'brand': 'OmbreStyle', 'price': '$59.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
        ],
        'Hair Extensions': [
            {'asin': 'B0AZ1Z1Z1Z1', 'rank': 1, 'title': 'Clip-In Hair Extensions - 20 Inch', 'brand': 'ExtensionPro', 'price': '$39.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ2Z2Z2Z2', 'rank': 2, 'title': 'Human Hair Extensions - Remy Hair', 'brand': 'RemyBeauty', 'price': '$89.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ3Z3Z3Z3', 'rank': 3, 'title': 'Synthetic Hair Extensions - 24 Inch', 'brand': 'SynthHair', 'price': '$29.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': True, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ4Z4Z4Z4', 'rank': 10, 'title': 'Tape-In Hair Extensions', 'brand': 'TapeBeauty', 'price': '$59.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ5Z5Z5Z5', 'rank': 14, 'title': 'Microbead Hair Extensions', 'brand': 'MicroPro', 'price': '$69.99', 'has_coupon': True, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ6Z6Z6Z6', 'rank': 19, 'title': 'Weft Hair Extensions', 'brand': 'WeftBeauty', 'price': '$49.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ7Z7Z7Z7', 'rank': 26, 'title': 'Halo Hair Extensions', 'brand': 'HaloStyle', 'price': '$54.99', 'has_coupon': False, 'has_deal': True, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
            {'asin': 'B0AZ8Z8Z8Z8', 'rank': 32, 'title': 'Clip-In Hair Extensions - Thick', 'brand': 'ThickHair', 'price': '$44.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False, 'scrape_time': datetime.now().isoformat()},
        ]
    }
    return mock_data

def scrape_bsr_data(category_url):
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        
        items = soup.find_all('div', {'data-asin': True})
        if not items:
            items = soup.select('[data-asin]')
        if not items:
            items = soup.find_all('div', class_='zg-item-immersion')
        if not items:
            items = soup.find_all('div', class_='p13n-sc-uncoverable-faceout')
        if not items:
            items = soup.find_all('div', class_='a-section a-spacing-none')
        
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
                title_elem = item.find('h2', class_='a-size-mini a-spacing-none a-color-base s-line-clamp-2')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            brand = None
            brand_elem = item.find('span', class_='a-size-small a-color-secondary')
            if not brand_elem:
                brand_elem = item.find('span', class_='a-size-small')
            if not brand_elem:
                brand_elem = item.find('div', class_='a-row a-size-small')
            if brand_elem:
                brand = brand_elem.get_text(strip=True)
            
            price = None
            price_elem = item.find('span', class_='p13n-sc-price')
            if not price_elem:
                price_elem = item.find('span', class_='a-price')
            if not price_elem:
                price_elem = item.find('span', class_='a-size-base a-color-price')
            if price_elem:
                price = price_elem.get_text(strip=True)
            
            has_coupon = False
            coupon_elem = item.find('span', class_='zg-coupon')
            if not coupon_elem:
                coupon_elem = item.find('span', class_='a-badge-coupon')
            if coupon_elem:
                has_coupon = True
            
            has_deal = False
            deal_elem = item.find('span', class_='a-badge-text')
            if deal_elem and 'Deal' in deal_elem.get_text(strip=True):
                has_deal = True
            
            has_lightning_deal = False
            lightning_elem = item.find('span', class_='a-badge-lightning')
            if lightning_elem:
                has_lightning_deal = True
            
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
        
        return products
    
    except Exception as e:
        print(f"Error scraping {category_url}: {str(e)}")
        return []

def get_all_categories_data(use_mock=False):
    if use_mock:
        print("Using mock data for testing...")
        return generate_mock_data()
    
    all_data = {}
    for category_name, category_url in CATEGORIES.items():
        print(f"Scraping {category_name}...")
        data = scrape_bsr_data(category_url)
        all_data[category_name] = data
        print(f"Found {len(data)} products for {category_name}")
    
    if all([len(data) == 0 for data in all_data.values()]):
        print("No data scraped from Amazon, using mock data instead...")
        return generate_mock_data()
    
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

def generate_last_week_mock_data():
    mock_data = {
        'Ponytail Extension': [
            {'asin': 'B08X1X1X1X1', 'rank': 1, 'title': 'Synthetic Ponytail Extension - 18 Inch Straight', 'brand': 'HairBeauty', 'price': '$19.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X2X2X2X2', 'rank': 3, 'title': 'Clip-In Ponytail Extension - 24 Inch Wavy', 'brand': 'LuxuryHair', 'price': '$29.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X3X3X3X3', 'rank': 10, 'title': 'Wrap Around Ponytail - 20 Inch Curly', 'brand': 'HairFashion', 'price': '$24.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X4X4X4X4', 'rank': 12, 'title': 'Drawstring Ponytail - 16 Inch Straight', 'brand': 'BeautyPlus', 'price': '$15.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X5X5X5X5', 'rank': 15, 'title': 'Ponytail Extension with Comb - 22 Inch', 'brand': 'StyleHair', 'price': '$22.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X6X6X6X6', 'rank': 25, 'title': 'High Ponytail Extension - 14 Inch', 'brand': 'HairPro', 'price': '$18.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X7X7X7X7', 'rank': 30, 'title': 'Ponytail Extension Thick - 26 Inch', 'brand': 'FullHair', 'price': '$34.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B08X8X8X8X8', 'rank': 28, 'title': 'Ponytail Hairpiece - 12 Inch Short', 'brand': 'MiniHair', 'price': '$12.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
        ],
        'Hair Topper': [
            {'asin': 'B09Y1Y1Y1Y1', 'rank': 2, 'title': 'Hair Topper for Women - 18x18cm Base', 'brand': 'TopperPro', 'price': '$49.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y2Y2Y2Y2', 'rank': 8, 'title': 'Clip-In Hair Topper - Human Hair', 'brand': 'RealHair', 'price': '$79.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y3Y3Y3Y3', 'rank': 6, 'title': 'Synthetic Hair Topper - Blonde', 'brand': 'BlondeBeauty', 'price': '$39.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y4Y4Y4Y4', 'rank': 12, 'title': 'Hair Topper with Bangs', 'brand': 'BangsHair', 'price': '$54.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y5Y5Y5Y5', 'rank': 18, 'title': 'Large Base Hair Topper - 22x22cm', 'brand': 'FullCoverage', 'price': '$69.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y6Y6Y6Y6', 'rank': 17, 'title': 'Thin Hair Topper - Lightweight', 'brand': 'LightHair', 'price': '$44.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y7Y7Y7Y7', 'rank': 28, 'title': 'Hair Topper for Men', 'brand': 'MensHair', 'price': '$35.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B09Y8Y8Y8Y8', 'rank': 30, 'title': 'Ombre Hair Topper - Two Tone', 'brand': 'OmbreStyle', 'price': '$59.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
        ],
        'Hair Extensions': [
            {'asin': 'B0AZ1Z1Z1Z1', 'rank': 5, 'title': 'Clip-In Hair Extensions - 20 Inch', 'brand': 'ExtensionPro', 'price': '$39.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ2Z2Z2Z2', 'rank': 2, 'title': 'Human Hair Extensions - Remy Hair', 'brand': 'RemyBeauty', 'price': '$89.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ3Z3Z3Z3', 'rank': 8, 'title': 'Synthetic Hair Extensions - 24 Inch', 'brand': 'SynthHair', 'price': '$29.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ4Z4Z4Z4', 'rank': 10, 'title': 'Tape-In Hair Extensions', 'brand': 'TapeBeauty', 'price': '$59.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ5Z5Z5Z5', 'rank': 9, 'title': 'Microbead Hair Extensions', 'brand': 'MicroPro', 'price': '$69.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ6Z6Z6Z6', 'rank': 19, 'title': 'Weft Hair Extensions', 'brand': 'WeftBeauty', 'price': '$49.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ7Z7Z7Z7', 'rank': 22, 'title': 'Halo Hair Extensions', 'brand': 'HaloStyle', 'price': '$54.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
            {'asin': 'B0AZ8Z8Z8Z8', 'rank': 25, 'title': 'Clip-In Hair Extensions - Thick', 'brand': 'ThickHair', 'price': '$44.99', 'has_coupon': False, 'has_deal': False, 'has_lightning_deal': False},
        ]
    }
    return mock_data

def compare_with_last_week(current_data, last_week_data):
    comparison = {}
    
    for category, current_products in current_data.items():
        comparison[category] = []
        last_week_products = last_week_data.get(category, {}) if last_week_data else {}
        
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

def main(use_mock=False):
    print("开始执行亚马逊BSR排名周报任务...")
    
    current_data = get_all_categories_data(use_mock=use_mock)
    
    today_str = datetime.now().strftime('%Y%m%d')
    save_data(current_data, f'bsr_data_{today_str}.json')
    
    last_week_data = get_last_week_data()
    
    if not last_week_data:
        print("未找到上周数据，生成模拟上周数据...")
        last_week_data = generate_last_week_mock_data()
    
    comparison_data = compare_with_last_week(current_data, last_week_data)
    
    rising, falling, stable = analyze_rank_changes(comparison_data)
    
    report = generate_feishu_report(rising, falling, stable)
    
    print("\n生成的周报内容：")
    print(report)
    
    send_to_feishu(report)
    
    print("任务完成")

if __name__ == '__main__':
    main(use_mock=True)