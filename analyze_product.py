#!/usr/bin/env python3
"""
亚马逊产品调研分析工具
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime


class AmazonProductAnalyzer:
    """亚马逊产品分析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def fetch_product_page(self, url):
        """获取产品页面"""
        try:
            print(f"正在抓取页面: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"抓取失败: {e}")
            return None
    
    def parse_product_info(self, html):
        """解析产品信息"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 基本信息
        product = {
            'title': '',
            'price': '',
            'rating': '',
            'reviews_count': '',
            'asin': '',
            'brand': '',
            'description': '',
            'features': [],
            'images': [],
            'bullets': [],
        }
        
        # 标题
        title_elem = soup.find('span', {'id': 'productTitle'})
        if title_elem:
            product['title'] = title_elem.get_text(strip=True)
        
        # 价格
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            product['price'] = f"${price_elem.get_text(strip=True)}"
        
        # 评分
        rating_elem = soup.find('span', {'class': 'a-icon-alt'})
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                product['rating'] = rating_match.group(1)
        
        # 评论数
        reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if reviews_elem:
            product['reviews_count'] = reviews_elem.get_text(strip=True)
        
        # ASIN
        asin_match = re.search(r'/dp/([A-Z0-9]{10})/', html)
        if asin_match:
            product['asin'] = asin_match.group(1)
        
        # 品牌
        brand_elem = soup.find('a', {'id': 'bylineInfo'})
        if brand_elem:
            product['brand'] = brand_elem.get_text(strip=True)
        
        # 产品特性
        features = soup.find_all('li', {'class': 'a-spacing-mini'})
        for feature in features[:5]:
            text = feature.get_text(strip=True)
            if text:
                product['features'].append(text)
        
        # 要点描述
        bullets = soup.find_all('li', {'class': 'a-carousel-card'})
        for bullet in bullets[:5]:
            text = bullet.get_text(strip=True)
            if text and text not in product['bullets']:
                product['bullets'].append(text)
        
        # 图片
        images = soup.find_all('img', {'class': 'a-dynamic-image'})
        for img in images[:5]:
            src = img.get('src', '')
            if src:
                product['images'].append(src)
        
        return product
    
    def analyze_market(self, product):
        """市场分析"""
        analysis = {
            'market_opportunity': '',
            'pricing_analysis': '',
            'difficulty_level': '',
            'estimated_monthly_revenue': '',
            'top_competitors': [],
            'keywords': [],
        }
        
        # 价格分析
        try:
            price_str = product.get('price', '').replace('$', '').replace(',', '')
            if price_str:
                price = float(price_str)
                
                if price < 20:
                    analysis['pricing_analysis'] = '低价位竞争激烈，适合走量'
                elif 20 <= price < 40:
                    analysis['pricing_analysis'] = '中价位，利润空间适中'
                else:
                    analysis['pricing_analysis'] = '高价位，需要高品质支撑'
                
                # 估算月收入
                monthly_sales = 300  # 假设
                analysis['estimated_monthly_revenue'] = f"约 ${price * monthly_sales:.2f}/月"
        except:
            analysis['pricing_analysis'] = '价格数据不可用'
        
        # 难度评估
        reviews_str = product.get('reviews_count', '0')
        try:
            reviews_num = int(re.sub(r'[^\d]', '', reviews_str))
            if reviews_num > 1000:
                analysis['difficulty_level'] = '高 - 市场已饱和，需要差异化'
            elif reviews_num > 500:
                analysis['difficulty_level'] = '中 - 有机会，需要精细运营'
            else:
                analysis['difficulty_level'] = '低 - 市场较新，机会较大'
        except:
            analysis['difficulty_level'] = '无法评估'
        
        # 关键词提取
        title = product.get('title', '')
        if title:
            words = re.findall(r'\b[a-z]+\b', title.lower())
            keywords = [w for w in words if len(w) > 3 and w not in ['with', 'for', 'the', 'and', 'inch', 'inch']]
            analysis['keywords'] = list(set(keywords))[:10]
        
        return analysis
    
    def generate_report(self, product, analysis):
        """生成调研报告"""
        report = f"""
{'='*80}
亚马逊产品调研分析报告
{'='*80}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
一、产品基本信息
{'='*80}

ASIN: {product.get('asin', 'N/A')}
品牌: {product.get('brand', 'N/A')}
标题: {product.get('title', 'N/A')}
价格: {product.get('price', 'N/A')}
评分: {product.get('rating', 'N/A')} ⭐
评论数: {product.get('reviews_count', 'N/A')}

{'='*80}
二、产品特性
{'='*80}
"""
        
        if product.get('features'):
            report += '\n主要特性:\n'
            for i, feature in enumerate(product['features'], 1):
                report += f"{i}. {feature}\n"
        
        if product.get('bullets'):
            report += '\n产品要点:\n'
            for i, bullet in enumerate(product['bullets'], 1):
                report += f"{i}. {bullet}\n"
        
        report += f"""
{'='*80}
三、市场分析
{'='*80}

价格分析: {analysis.get('pricing_analysis', 'N/A')}
竞争难度: {analysis.get('difficulty_level', 'N/A')}
估算月收入: {analysis.get('estimated_monthly_revenue', 'N/A')}

{'='*80}
四、关键词分析
{'='*80}
"""
        
        if analysis.get('keywords'):
            report += '\n相关关键词:\n'
            for i, keyword in enumerate(analysis['keywords'], 1):
                report += f"{i}. {keyword}\n"
        
        report += f"""
{'='*80}
五、调研结论
{'='*80}

"""
        
        if analysis.get('difficulty_level') == '高 - 市场已饱和，需要差异化':
            report += '⚠️ 市场已饱和，竞争激烈。建议:\n'
            report += '   - 寻找差异化卖点\n'
            report += '   - 优化产品品质\n'
            report += '   - 降低定价预期\n'
            report += '   - 注重Review积累\n'
        elif analysis.get('difficulty_level') == '中 - 有机会，需要精细运营':
            report += '💡 市场有机会，但需要精细运营。建议:\n'
            report += '   - 找准细分市场\n'
            report += '   - 优化Listing\n'
            report += '   - 关注客户反馈\n'
            report += '   - 做好客服工作\n'
        else:
            report += '✅ 市场较新，机会较大。建议:\n'
            report += '   - 快速入场抢占市场\n'
            report += '   - 建立品牌认知\n'
            report += '   - 积累Review\n'
        
        report += f"""
{'='*80}
六、产品链接
{'='*80}

产品链接: https://www.amazon.com/dp/{product.get('asin', 'N/A')}

{'='*80}
"""
        
        return report
    
    def save_report(self, report, filename='product_analysis_report.txt'):
        """保存报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        return filename


def main():
    """主函数"""
    url = "https://www.amazon.com/Stamped-Glorious-Ponytail-Extension-Synthetic/dp/B0F2SSRYD8/ref=zg_bs_g_702380011_d_sccl_41/146-6844278-5293026?psc=1"
    
    print("="*60)
    print("亚马逊产品调研分析")
    print("="*60)
    print()
    
    analyzer = AmazonProductAnalyzer()
    
    # 抓取页面
    print("1. 抓取产品页面...")
    html = analyzer.fetch_product_page(url)
    
    if not html:
        print("抓取失败，请检查网络或URL")
        return
    
    # 解析产品信息
    print("2. 解析产品信息...")
    product = analyzer.parse_product_info(html)
    
    # 市场分析
    print("3. 进行市场分析...")
    analysis = analyzer.analyze_market(product)
    
    # 生成报告
    print("4. 生成调研报告...")
    report = analyzer.generate_report(product, analysis)
    
    # 保存报告
    print("5. 保存报告...")
    filename = analyzer.save_report(report, 'product_analysis_report.txt')
    
    print()
    print("="*60)
    print("✅ 调研分析完成！")
    print("="*60)
    print()
    
    # 输出报告
    print(report)
    
    return report, product, analysis


if __name__ == "__main__":
    report, product, analysis = main()
