import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime, timedelta
import re

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

CATEGORIES = {
    "Hair Extensions": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hair-Extensions/zgbs/beauty/702379011/ref=zg_bs_nav_beauty_3_13105931",
    "Hairpieces": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011",
    "Wigs": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hair-Replacement-Wigs/zgbs/beauty/702381011/ref=zg_bs_nav_beauty_3_702379011"
}

SEARCH_CATEGORIES = {
    "Ponytail Extension": "https://www.amazon.com/s?k=ponytail%20extension&i=beauty&ref=nb_sb_noss",
    "Hair Topper": "https://www.amazon.com/s?k=hair%20topper&i=beauty&ref=nb_sb_noss"
}

DATA_DIR = "data"
LAST_WEEK_FILE = os.path.join(DATA_DIR, "last_week_data.json")
CURRENT_DATA_FILE = os.path.join(DATA_DIR, "current_data.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

MAX_RETRIES = 3
RETRY_DELAY = 5

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def fetch_url(url):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None

def scrape_bsr_data(category_name, url, is_search=False):
    print(f"正在抓取: {category_name}")
    products = []
    
    response = fetch_url(url)
    if not response:
        print(f"抓取失败: 多次重试后仍无法获取数据")
        return products
    
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        
        if is_search:
            items = soup.find_all('div', class_='s-result-item')
        else:
            items = soup.find_all('div', class_='_cDEzb_grid-cell_1uMOS')
        
        for index, item in enumerate(items):
            rank = index + 1
            
            asin = ""
            if is_search:
                asin_elem = item.get('data-asin')
                asin = asin_elem if asin_elem else ""
            else:
                wrapper = item.find('div', class_='_cDEzb_iveVideoWrapper_JJ34T')
                asin = wrapper.get('data-asin') if wrapper else ""
            
            if not asin:
                continue
            
            title = ""
            if is_search:
                title_elem = item.find('span', class_='a-text-normal')
                title = title_elem.get_text(strip=True) if title_elem else ""
            else:
                title_elem = item.find('div', class_=lambda x: x and 'line-clamp' in x)
                if not title_elem:
                    title_elem = item.find('div', class_='_cDEzb_p13n-sc-css-line-clamp-3_g3dy1')
                title = title_elem.get_text(strip=True) if title_elem else ""
            
            brand = ""
            if is_search:
                brand_elem = item.find('span', class_='a-size-base-plus a-color-base')
                if not brand_elem:
                    brand_elem = item.find('span', class_='a-size-small a-color-secondary')
                brand = brand_elem.get_text(strip=True) if brand_elem else ""
            else:
                faceout = item.find('div', class_=lambda x: x and 'faceout' in x)
                if faceout:
                    brand_elem = faceout.find('span', class_='a-color-secondary')
                    if brand_elem:
                        brand_text = brand_elem.get_text(strip=True)
                        if 'offer from' not in brand_text.lower() and '$' not in brand_text:
                            brand = brand_text
            
            if not brand and title:
                brand = title.split()[0]
            
            if 'offer from' in brand.lower() or '$' in brand:
                brand = ""
            
            price = ""
            if is_search:
                price_elem = item.find('span', class_='a-offscreen')
                price = price_elem.get_text(strip=True) if price_elem else ""
                if not price:
                    price_elem = item.find('span', class_='a-price-whole')
                    price = price_elem.get_text(strip=True) if price_elem else ""
            else:
                price_elem = item.find('span', class_='p13n-sc-price')
                if price_elem:
                    price = price_elem.get_text(strip=True)
                else:
                    price_spans = item.find_all('span', string=re.compile(r'\$\d'))
                    for span in price_spans:
                        if '$' in span.get_text(strip=True):
                            price = span.get_text(strip=True)
                            break
                if not price:
                    color_secondary = item.find('span', class_='a-color-secondary')
                    if color_secondary:
                        text = color_secondary.get_text(strip=True)
                        match = re.search(r'\$\d+\.?\d*', text)
                        if match:
                            price = match.group()
            
            has_coupon = False
            has_deal = False
            has_lightning_deal = False
            
            if is_search:
                has_coupon = bool(item.find('span', string=re.compile(r'coupon', re.I)))
                has_deal = bool(item.find('span', string=re.compile(r'Deal|Sale|Promotion', re.I)))
                has_lightning_deal = bool(item.find('span', string=re.compile(r'Lightning Deal', re.I)))
            else:
                has_coupon = bool(item.find('span', class_='zg-item-coupon'))
                has_deal = bool(item.find('span', class_='a-badge-text')) or bool(item.find('span', string=re.compile(r'Deal|Sale|Promotion', re.I)))
                has_lightning_deal = bool(item.find('span', string=re.compile(r'Lightning Deal', re.I)))
            
            if not brand and title:
                brand = title.split()[0]
            
            products.append({
                "rank": rank,
                "asin": asin,
                "title": title[:100],
                "brand": brand[:50],
                "price": price,
                "has_coupon": has_coupon,
                "has_deal": has_deal,
                "has_lightning_deal": has_lightning_deal,
                "promotion_reason": []
            })
            
            if rank >= 50:
                break
                
        print(f"成功抓取 {len(products)} 个商品")
    except Exception as e:
        print(f"解析失败: {e}")
    
    return products

def analyze_promotion(product):
    reasons = []
    if product.get("has_coupon"):
        reasons.append("优惠券")
    if product.get("has_deal"):
        reasons.append("折扣促销")
    if product.get("has_lightning_deal"):
        reasons.append("Lightning Deal")
    
    current_month = datetime.now().month
    current_day = datetime.now().day
    if (current_month == 7 and 15 <= current_day <= 16) or (current_month == 10 and 10 <= current_day <= 11):
        reasons.append("Prime Day")
    
    return reasons

def load_last_week_data():
    if os.path.exists(LAST_WEEK_FILE):
        with open(LAST_WEEK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_current_data(data):
    with open(CURRENT_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_as_last_week():
    if os.path.exists(CURRENT_DATA_FILE):
        os.rename(CURRENT_DATA_FILE, LAST_WEEK_FILE)

def compare_data(current_data, last_week_data):
    results = {}
    
    for category, products in current_data.items():
        last_products = last_week_data.get(category, {})
        last_asin_to_rank = {p["asin"]: p["rank"] for p in last_products} if isinstance(last_products, list) else {}
        
        category_results = []
        for product in products:
            current_rank = product["rank"]
            last_rank = last_asin_to_rank.get(product["asin"])
            
            rank_change = last_rank - current_rank if last_rank else None
            
            promotion_reasons = analyze_promotion(product)
            
            category_results.append({
                **product,
                "last_rank": last_rank,
                "rank_change": rank_change,
                "promotion_reason": promotion_reasons
            })
        
        results[category] = category_results
    
    return results

def generate_feishu_message(analysis_results):
    today = datetime.now().strftime("%Y-%m-%d")
    message = f"📊 **亚马逊假发类目BSR排名周报**\n\n"
    message += f"📅 报告日期：{today}\n\n"
    
    highlight_up = []
    highlight_down = []
    stable_counts = {}
    total_products = {}
    failed_categories = []
    has_last_week_data = False
    
    for category, products in analysis_results.items():
        if not products:
            failed_categories.append(category)
            stable_counts[category] = 0
            total_products[category] = 0
            continue
        
        total_products[category] = len(products)
        up_count = 0
        down_count = 0
        stable_count = 0
        
        for product in products:
            rank_change = product["rank_change"]
            
            if rank_change is not None:
                has_last_week_data = True
                if rank_change >= 5:
                    highlight_up.append({
                        "category": category,
                        "brand": product["brand"],
                        "change": f"+{rank_change}",
                        "reasons": ", ".join(product["promotion_reason"]) if product["promotion_reason"] else "未知",
                        "title": product["title"]
                    })
                    up_count += 1
                elif rank_change <= -5:
                    highlight_down.append({
                        "category": category,
                        "brand": product["brand"],
                        "change": f"{rank_change}",
                        "reasons": ", ".join(product["promotion_reason"]) if product["promotion_reason"] else "未知",
                        "title": product["title"]
                    })
                    down_count += 1
                else:
                    stable_count += 1
        
        stable_counts[category] = stable_count
    
    if failed_categories:
        message += f"⚠️ **数据获取失败类目**: {', '.join(failed_categories)}\n\n"
    
    if not has_last_week_data:
        message += "📌 **首次运行**\n- 正在积累基准数据，下周开始进行排名对比\n\n"
    
    if highlight_up or highlight_down:
        message += "🔥 **重点异动商品**\n\n"
        
        if highlight_up:
            message += "⬆️ **排名上升≥5名**\n"
            for item in highlight_up[:10]:
                message += f"• {item['category']} | {item['brand']} | {item['change']} | {item['reasons']}\n"
        
        if highlight_down:
            message += "\n⬇️ **排名下降≥5名**\n"
            for item in highlight_down[:10]:
                message += f"• {item['category']} | {item['brand']} | {item['change']} | {item['reasons']}\n"
    
    message += "\n📈 **各品类商品数量**\n\n"
    for category, count in total_products.items():
        stable_count = stable_counts.get(category, 0)
        if has_last_week_data:
            message += f"• {category}: 共 {count} 个，稳定 {stable_count} 个\n"
        else:
            message += f"• {category}: {count} 个\n"
    
    message += "\n💡 **关键结论**\n"
    if not has_last_week_data:
        message += "- 首次运行，已成功抓取各品类数据，开始积累基准\n"
    else:
        total_up = len(highlight_up)
        total_down = len(highlight_down)
        
        if total_up > total_down:
            message += "- 本周整体表现积极，排名上升商品多于下降商品\n"
        elif total_down > total_up:
            message += "- 本周市场竞争加剧，排名下降商品较多\n"
        else:
            message += "- 本周市场相对稳定，排名变化不大\n"
        
        if any("Prime Day" in item["reasons"] for item in highlight_up + highlight_down):
            message += "- Prime Day活动对部分商品排名产生显著影响\n"
    
    return message

def send_feishu_message(message):
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
        response.raise_for_status()
        print("飞书消息发送成功")
        return True
    except Exception as e:
        print(f"飞书消息发送失败: {e}")
        return False

def main():
    ensure_data_dir()
    
    last_week_data = load_last_week_data()
    
    current_data = {}
    
    for category_name, url in CATEGORIES.items():
        products = scrape_bsr_data(category_name, url, is_search=False)
        current_data[category_name] = products
        time.sleep(2)
    
    for category_name, url in SEARCH_CATEGORIES.items():
        products = scrape_bsr_data(category_name, url, is_search=True)
        current_data[category_name] = products
        time.sleep(2)
    
    save_current_data(current_data)
    
    analysis_results = compare_data(current_data, last_week_data)
    
    feishu_message = generate_feishu_message(analysis_results)
    print("\n--- 飞书推送内容 ---")
    print(feishu_message)
    print("--- 推送内容结束 ---")
    
    send_feishu_message(feishu_message)
    
    save_as_last_week()
    
    print("\n任务完成！")

if __name__ == "__main__":
    main()
