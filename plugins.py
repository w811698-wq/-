import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import config


class SellerSpirit:
    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        self.browser.get(config.SELLER_SPIRIT_URL)
        time.sleep(3)
        try:
            self.browser.send_keys(By.NAME, 'username', username)
            self.browser.send_keys(By.NAME, 'password', password)
            self.browser.click(By.XPATH, '//button[@type="submit"]')
            time.sleep(5)
            return True
        except Exception as e:
            print(f"登录卖家精灵失败: {e}")
            return False

    def filter_products(self, filters):
        self.browser.get(f"{config.SELLER_SPIRIT_URL}/product-research")
        time.sleep(3)
        
        if 'min_price' in filters:
            self.browser.send_keys(By.NAME, 'min_price', str(filters['min_price']))
        if 'max_price' in filters:
            self.browser.send_keys(By.NAME, 'max_price', str(filters['max_price']))
        if 'min_rating' in filters:
            self.browser.send_keys(By.NAME, 'min_rating', str(filters['min_rating']))
        
        self.browser.click(By.XPATH, '//button[contains(text(), "搜索")]')
        time.sleep(5)
        
        products = self._parse_products()
        return products

    def _parse_products(self):
        products = []
        soup = BeautifulSoup(self.browser.get_page_source(), 'html.parser')
        product_items = soup.find_all('div', class_='product-item')
        
        for item in product_items:
            product = {
                'asin': item.get('data-asin', ''),
                'title': item.find('h3').text.strip() if item.find('h3') else '',
                'price': item.find('span', class_='price').text.strip() if item.find('span', class_='price') else '',
                'rating': item.find('span', class_='rating').text.strip() if item.find('span', class_='rating') else '',
                'reviews': item.find('span', class_='reviews').text.strip() if item.find('span', class_='reviews') else '',
                'monthly_sales': item.find('span', class_='sales').text.strip() if item.find('span', class_='sales') else '',
                'bsr': item.find('span', class_='bsr').text.strip() if item.find('span', class_='bsr') else ''
            }
            products.append(product)
        return products

    def get_keywords(self, seed_keyword):
        self.browser.get(f"{config.SELLER_SPIRIT_URL}/keyword-research")
        time.sleep(3)
        self.browser.send_keys(By.NAME, 'keyword', seed_keyword)
        self.browser.click(By.XPATH, '//button[contains(text(), "挖掘")]')
        time.sleep(5)
        
        keywords = self._parse_keywords()
        return keywords

    def _parse_keywords(self):
        keywords = []
        soup = BeautifulSoup(self.browser.get_page_source(), 'html.parser')
        keyword_items = soup.find_all('tr', class_='keyword-row')
        
        for item in keyword_items:
            cols = item.find_all('td')
            if len(cols) >= 5:
                keyword = {
                    'keyword': cols[0].text.strip(),
                    'search_volume': cols[1].text.strip(),
                    'competition': cols[2].text.strip(),
                    'cpc': cols[3].text.strip(),
                    'trend': cols[4].text.strip()
                }
                keywords.append(keyword)
        return keywords


class XiYou:
    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        self.browser.get(config.XIYOU_URL)
        time.sleep(3)
        try:
            self.browser.send_keys(By.NAME, 'account', username)
            self.browser.send_keys(By.NAME, 'password', password)
            self.browser.click(By.XPATH, '//button[@type="submit"]')
            time.sleep(5)
            return True
        except Exception as e:
            print(f"登录西柚插件失败: {e}")
            return False

    def get_reviews(self, asin):
        self.browser.get(f"{config.AMAZON_URL}/dp/{asin}")
        time.sleep(3)
        self.browser.click(By.XPATH, '//a[contains(@href, "reviews")]')
        time.sleep(3)
        
        reviews = self._parse_reviews()
        return reviews

    def _parse_reviews(self):
        reviews = []
        soup = BeautifulSoup(self.browser.get_page_source(), 'html.parser')
        review_items = soup.find_all('div', {'data-hook': 'review'})
        
        for item in review_items:
            review = {
                'rating': item.find('i', {'data-hook': 'review-star-rating'}).text.strip() if item.find('i', {'data-hook': 'review-star-rating'}) else '',
                'title': item.find('a', {'data-hook': 'review-title'}).text.strip() if item.find('a', {'data-hook': 'review-title'}) else '',
                'content': item.find('span', {'data-hook': 'review-body'}).text.strip() if item.find('span', {'data-hook': 'review-body'}) else '',
                'date': item.find('span', {'data-hook': 'review-date'}).text.strip() if item.find('span', {'data-hook': 'review-date'}) else ''
            }
            reviews.append(review)
        return reviews
