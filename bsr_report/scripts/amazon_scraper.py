import requests
import re
import json
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from config import HEADERS, CATEGORIES, DATA_DIR, TOP_N

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Failed to fetch page: {e}")
        return None


def parse_bsr_data(html, category_name):
    products = []
    if not html:
        return products

    soup = BeautifulSoup(html, 'html.parser')
    
    items = soup.find_all('div', {'class': re.compile(r'zg-grid-general-faceout|zg-item|p13n-grid-item|a-section')})
    
    if not items:
        items = soup.find_all('span', {'class': 'zg-item'})
    
    if not items:
        items = soup.find_all('li', {'id': re.compile(r'item_\d+')})
    
    if not items:
        items = soup.find_all('div', {'data-asin': True})
    
    logger.info(f"Found {len(items)} items to parse")
    
    for idx, item in enumerate(items[:TOP_N], 1):
        try:
            asin = item.get('data-asin', '')
            
            if not asin:
                link_tag = item.find('a', href=True)
                if link_tag:
                    asin_match = re.search(r'/dp/([A-Z0-9]+)', link_tag['href'])
                    if asin_match:
                        asin = asin_match.group(1)
            
            title_tag = item.find('span', {'class': 'zg-text-center-align'})
            if not title_tag:
                title_tag = item.find('div', {'class': 'p13n-sc-truncate'})
            if not title_tag:
                title_tag = item.find('span', {'class': re.compile(r'[Aa]size-medium')})
            if not title_tag:
                title_tag = item.find('h2')
            if not title_tag:
                title_tag = item.find('span', {'class': re.compile(r'truncate|title')})
            if not title_tag:
                title_tag = item.find('a', {'class': re.compile(r'link|title')})
            if not title_tag:
                title_tag = item.find('div', {'class': re.compile(r'title|name')})
            
            title = title_tag.get_text(strip=True) if title_tag else ''
            
            brand_tag = item.find('span', {'class': 'a-size-small a-color-secondary'})
            if not brand_tag:
                brand_tag = item.find('span', {'class': re.compile(r'brand|a-color-secondary')})
            if not brand_tag:
                brand_tag = item.find('div', {'class': re.compile(r'brand')})
            if not brand_tag:
                brand_tag = item.find('span', {'class': 'a-size-mini'})
            
            brand = ''
            if brand_tag:
                brand_text = brand_tag.get_text(strip=True)
                if not re.match(r'\d+ offers? from', brand_text, re.IGNORECASE):
                    brand = brand_text
            
            price_tag = item.find('span', {'class': 'p13n-sc-price'})
            if not price_tag:
                price_tag = item.find('span', {'class': 'a-price-whole'})
            if not price_tag:
                price_tag = item.find('span', {'class': re.compile(r'price')})
            if not price_tag:
                price_tag = item.find('span', text=re.compile(r'\$\d+'))
            
            price = price_tag.get_text(strip=True) if price_tag else ''
            
            if re.match(r'\d+ offers? from', brand, re.IGNORECASE) and not price:
                price_match = re.search(r'\$[\d.]+', brand)
                if price_match:
                    price = price_match.group(0)
                brand = ''
            
            coupon_tag = item.find('span', string=re.compile(r'coupon', re.IGNORECASE))
            has_coupon = bool(coupon_tag)
            
            sale_tag = item.find('span', string=re.compile(r'sale|deal', re.IGNORECASE))
            has_sale = bool(sale_tag)
            
            lightning_deal = bool(item.find('span', string=re.compile(r'Lightning Deal', re.IGNORECASE)))
            
            if asin or title:
                products.append({
                    'rank': idx,
                    'asin': asin,
                    'title': title[:200] if title else '',
                    'brand': brand,
                    'price': price,
                    'has_coupon': has_coupon,
                    'has_sale': has_sale,
                    'has_lightning_deal': lightning_deal,
                    'category': category_name,
                    'scraped_at': datetime.now().isoformat()
                })
        except Exception as e:
            logger.warning(f"Failed to parse item {idx}: {e}")
            continue
    
    return products


def save_data(products, category_name):
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{category_name.replace(' ', '_')}_{date_str}.json"
    filepath = f"{DATA_DIR}/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(products)} products to {filepath}")
    return filepath


def scrape_category(category_name, url):
    logger.info(f"Starting to scrape {category_name}...")
    html = fetch_page(url)
    
    if not html:
        logger.error(f"Failed to get HTML for {category_name}")
        save_data([], category_name)
        return []
    
    products = parse_bsr_data(html, category_name)
    logger.info(f"Scraped {len(products)} products for {category_name}")
    
    save_data(products, category_name)
    
    return products


def scrape_all_categories():
    all_data = {}
    for category_name, info in CATEGORIES.items():
        products = scrape_category(category_name, info['url'])
        all_data[category_name] = products
        time.sleep(2)
    
    return all_data


if __name__ == "__main__":
    scrape_all_categories()