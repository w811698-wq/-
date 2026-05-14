import time
from browser import BrowserManager
from plugins import SellerSpirit, XiYou
from data_processor import DataProcessor
from excel_exporter import ExcelExporter
import config


class AmazonResearchRPA:
    def __init__(self):
        self.browser = None
        self.seller_spirit = None
        self.xiyou = None
        self.processor = DataProcessor()
        self.exporter = ExcelExporter()
        self.data = {}

    def start(self):
        print("启动亚马逊产品调研RPA...")
        self.browser = BrowserManager().start()
        self.seller_spirit = SellerSpirit(self.browser)
        self.xiyou = XiYou(self.browser)
        return self

    def step1_filter_products(self, filters=None):
        print("步骤1: 筛选产品...")
        if filters is None:
            filters = config.PRODUCT_FILTERS
        products = self.seller_spirit.filter_products(filters)
        products = self.processor.deduplicate_products(products)
        self.data['products'] = products
        print(f"筛选完成，找到 {len(products)} 个候选产品")
        return products

    def step2_analyze_strategy(self, products):
        print("步骤2: 分析打法...")
        strategy_list = []
        for product in products[:5]:
            strategy = {
                'asin': product.get('asin', ''),
                'title': product.get('title', ''),
                'strategy_type': '待分析',
                'main_image_style': '待分析',
                'has_aplus': '待分析',
                'has_video': '待分析'
            }
            strategy_list.append(strategy)
        self.data['strategy'] = strategy_list
        print(f"完成 {len(strategy_list)} 个产品的打法分析")
        return strategy_list

    def step3_analyze_bad_reviews(self, asin):
        print(f"步骤3: 分析差评 - ASIN: {asin}...")
        reviews = self.xiyou.get_reviews(asin)
        analysis = self.processor.analyze_reviews(reviews)
        self.data['reviews_analysis'] = analysis
        print(f"差评分析完成: {len(reviews)} 条评论")
        return analysis

    def step4_analyze_good_reviews(self, asin):
        print(f"步骤4: 分析好评 - ASIN: {asin}...")
        return self.step3_analyze_bad_reviews(asin)

    def step5_product_optimization(self):
        print("步骤5: 生成产品优化方案...")
        optimization = {
            'material_upgrade': '建议升级材质',
            'size_adjustment': '建议调整尺寸',
            'accessories': '建议增加配件',
            'packaging': '建议优化包装',
            'pitfalls': '注意避坑点'
        }
        self.data['optimization'] = optimization
        return optimization

    def step6_analyze_audience(self):
        print("步骤6: 分析目标人群...")
        audiences = ['女性', '男性', '上班族', '学生', '家庭主妇']
        self.data['audiences'] = audiences
        return audiences

    def step7_generate_matrix(self, audiences, scenarios, keywords):
        print("步骤7: 生成人群×场景×关键词矩阵...")
        matrix = self.processor.generate_strategy_matrix(audiences, scenarios, keywords)
        self.data['matrix'] = matrix
        return matrix

    def step8_get_keywords(self, seed_keyword):
        print(f"步骤8: 获取关键词库 - 种子词: {seed_keyword}...")
        keywords = self.seller_spirit.get_keywords(seed_keyword)
        keywords = self.processor.filter_keywords(
            keywords,
            min_search_volume=config.KEYWORD_FILTERS['min_search_volume'],
            max_competition=config.KEYWORD_FILTERS['max_competition']
        )
        self.data['keywords'] = keywords
        print(f"获取到 {len(keywords)} 个有效关键词")
        return keywords

    def step9_generate_listing_keywords(self, brand, core_words):
        print("步骤9: 生成Listing关键词组合...")
        attributes = ['耐用', '便携', '时尚', '高品质']
        scenarios = ['居家', '办公', '户外', '送礼']
        audiences = self.data.get('audiences', ['通用'])
        
        listing_keywords = self.processor.generate_listing_keywords(
            brand, core_words, attributes, scenarios, audiences
        )
        self.data['listing_keywords'] = listing_keywords
        return listing_keywords

    def step10_match_selling_points_audience(self):
        print("步骤10: 匹配卖点对应人群...")
        matches = [
            {'卖点': '便携', '对应人群': '通勤人群'},
            {'卖点': '高颜值', '对应人群': '送礼人群'},
            {'卖点': '耐用', '对应人群': '家庭人群'}
        ]
        self.data['selling_points_audience'] = matches
        return matches

    def step11_generate_selling_points(self):
        print("步骤11: 生成卖点策略...")
        pain_points = self.data.get('reviews_analysis', {}).get('pain_points', [])
        praise_points = self.data.get('reviews_analysis', {}).get('praise_points', [])
        missing_points = []
        
        selling_points = self.processor.generate_selling_points(
            pain_points, praise_points, missing_points
        )
        self.data['selling_points'] = selling_points
        return selling_points

    def step12_generate_enhanced_matrix(self):
        print("步骤12: 生成强化版矩阵...")
        audiences = self.data.get('audiences', ['通用'])
        scenarios = ['居家', '办公', '户外', '送礼', '日常']
        keywords = [kw.get('keyword', '') for kw in self.data.get('keywords', [])]
        
        enhanced_matrix = self.processor.generate_strategy_matrix(audiences, scenarios, keywords)
        self.data['enhanced_matrix'] = enhanced_matrix
        return enhanced_matrix

    def run_full_research(self, seed_keyword, brand='MyBrand'):
        print("="*50)
        print("开始完整的亚马逊产品调研流程")
        print("="*50)
        
        try:
            products = self.step1_filter_products()
            if products:
                self.step2_analyze_strategy(products)
                
                sample_asin = products[0].get('asin', '') if products else ''
                if sample_asin:
                    self.step3_analyze_bad_reviews(sample_asin)
                    self.step4_analyze_good_reviews(sample_asin)
            
            self.step5_product_optimization()
            audiences = self.step6_analyze_audience()
            keywords = self.step8_get_keywords(seed_keyword)
            
            scenarios = ['居家', '办公', '户外', '送礼']
            self.step7_generate_matrix(audiences, scenarios, [kw.get('keyword', '') for kw in keywords])
            
            self.step9_generate_listing_keywords(brand, [seed_keyword])
            self.step10_match_selling_points_audience()
            self.step11_generate_selling_points()
            self.step12_generate_enhanced_matrix()
            
            print("="*50)
            print("调研完成，正在导出Excel...")
            output_file = self.exporter.export_all(self.data)
            print(f"调研报告已保存至: {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"调研过程中出错: {e}")
            return None

    def close(self):
        if self.browser:
            self.browser.close()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
