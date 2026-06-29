"""
BSR数据抓取模块
注意：亚马逊有严格的反爬机制，实际使用时可能需要：
1. 使用代理IP池
2. 接入第三方反Captcha服务
3. 使用Selenium等浏览器自动化工具
4. 或使用Jungle Scout/Helium 10等API服务
"""

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from .config import USER_AGENT, CATEGORIES


class AmazonBSRScraper:
    """亚马逊BSR数据抓取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        })

    def scrape_bestseller_page(self, category_info):
        """
        抓取Bestseller页面数据
        category_info: 包含类目ID和URL的字典
        返回: 商品数据列表
        """
        category_id = category_info["id"]
        url = category_info["bestseller_url"]

        print(f"正在抓取类目: {category_id}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return self._parse_bestseller_page(response.text, category_id)
        except requests.exceptions.RequestException as e:
            print(f"抓取失败 {category_id}: {e}")
            return []

    def _parse_bestseller_page(self, html, category_id):
        """解析Bestseller页面HTML"""
        soup = BeautifulSoup(html, "lxml")
        products = []

        # 尝试多种选择器来匹配亚马逊页面结构
        product_elements = soup.select("[data-asin]")

        for idx, element in enumerate(product_elements):
            asin = element.get("data-asin")
            if not asin:
                continue

            # 获取排名
            rank_elem = element.select_one(".zg-badge-text")
            rank_text = rank_elem.get_text(strip=True) if rank_elem else str(idx + 1)
            rank = self._extract_rank(rank_text)

            # 获取标题
            title_elem = element.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fnib")
            if not title_elem:
                title_elem = element.select_one("a.a-size-small")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"

            # 获取品牌
            brand_elem = element.select_one(".a-size-small.a-color-base")
            brand = brand_elem.get_text(strip=True) if brand_elem else "N/A"

            # 获取价格
            price_elem = element.select_one("._cDEzb_p13n-sc-price_3oUeb span")
            if not price_elem:
                price_elem = element.select_one(".p13n-sc-price")
            price_text = price_elem.get_text(strip=True) if price_elem else "N/A"

            # 获取ASIN
            asin = element.get("data-asin", "N/A")

            products.append({
                "category": category_id,
                "rank": rank,
                "asin": asin,
                "title": title,
                "brand": brand,
                "price": price_text,
                "scrape_time": datetime.now().isoformat()
            })

        return products

    def _extract_rank(self, rank_text):
        """从文本中提取排名数字"""
        match = re.search(r"#?([\d,]+)", rank_text)
        if match:
            return int(match.group(1).replace(",", ""))
        return 0

    def scrape_all_categories(self):
        """抓取所有类目数据"""
        all_data = {}
        for category in CATEGORIES:
            products = self.scrape_bestseller_page(category)
            all_data[category["id"]] = products
            time.sleep(2)  # 避免请求过快
        return all_data


def generate_demo_data():
    """
    生成演示数据用于测试
    实际部署时应使用真实的抓取逻辑
    """
    from datetime import datetime

    demo_data = {}
    categories = ["Ponytail Extension", "Hair Topper", "Hair Extensions"]

    # 模拟各品类BSR数据
    for category in categories:
        products = []
        for rank in range(1, 21):
            products.append({
                "category": category,
                "rank": rank,
                "asin": f"B08{rank:06d}",
                "title": f"Professional Hair Extension {category} - Premium Quality {rank}",
                "brand": f"Brand{(rank % 5) + 1}",
                "price": f"${15.99 + rank * 2:.2f}",
                "scrape_time": datetime.now().isoformat()
            })
        demo_data[category] = products

    return demo_data


if __name__ == "__main__":
    # 测试抓取功能
    scraper = AmazonBSRScraper()
    data = scraper.scrape_all_categories()
    print(json.dumps(data, indent=2, ensure_ascii=False))
