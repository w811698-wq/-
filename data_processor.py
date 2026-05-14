import re
from collections import Counter
import pandas as pd
import config


class DataProcessor:
    def __init__(self):
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'])

    def clean_text(self, text):
        if not text:
            return ''
        text = re.sub(r'[^\w\s]', ' ', text)
        text = text.lower()
        return text

    def extract_keywords(self, text, top_n=20):
        text = self.clean_text(text)
        words = text.split()
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        counter = Counter(words)
        return counter.most_common(top_n)

    def analyze_reviews(self, reviews):
        bad_reviews = [r for r in reviews if self._get_rating_value(r.get('rating', '')) <= 3]
        good_reviews = [r for r in reviews if self._get_rating_value(r.get('rating', '')) >= 4]

        bad_text = ' '.join([r.get('content', '') + ' ' + r.get('title', '') for r in bad_reviews])
        good_text = ' '.join([r.get('content', '') + ' ' + r.get('title', '') for r in good_reviews])

        pain_points = self.extract_keywords(bad_text, 30)
        praise_points = self.extract_keywords(good_text, 30)

        return {
            'bad_reviews_count': len(bad_reviews),
            'good_reviews_count': len(good_reviews),
            'pain_points': pain_points,
            'praise_points': praise_points
        }

    def _get_rating_value(self, rating_str):
        try:
            match = re.search(r'(\d+\.?\d*)', rating_str)
            return float(match.group(1)) if match else 0
        except:
            return 0

    def deduplicate_products(self, products):
        seen = set()
        unique_products = []
        for product in products:
            asin = product.get('asin', '')
            if asin and asin not in seen:
                seen.add(asin)
                unique_products.append(product)
        return unique_products

    def generate_strategy_matrix(self, audiences, scenarios, keywords):
        matrix = []
        for audience in audiences:
            row = {'audience': audience}
            for scenario in scenarios:
                key = f"{audience}_{scenario}"
                row[scenario] = [k for k in keywords if audience.lower() in k.lower() or scenario.lower() in k.lower()]
            matrix.append(row)
        return matrix

    def generate_listing_keywords(self, brand, core_words, attributes, scenarios, audiences):
        keywords = []
        for core in core_words:
            for attr in attributes:
                for scenario in scenarios:
                    for audience in audiences:
                        keyword = f"{brand} {core} {attr} {scenario} {audience}"
                        keywords.append(keyword.strip())
        return list(set(keywords))[:50]

    def generate_selling_points(self, pain_points, praise_points, missing_points):
        core_selling_points = [f"解决 {point[0]} 问题" for point in pain_points[:5]]
        differential_selling_points = [f"突出 {point[0]} 优势" for point in praise_points[:5]]
        trust_selling_points = ["品质保证", "7天无理由退换", "专业客服"]
        
        return {
            'core': core_selling_points,
            'differential': differential_selling_points,
            'trust': trust_selling_points
        }

    def filter_keywords(self, keywords, min_search_volume=1000, max_competition=0.7):
        filtered = []
        for kw in keywords:
            try:
                sv = float(kw.get('search_volume', 0))
                comp = float(kw.get('competition', 1))
                if sv >= min_search_volume and comp <= max_competition:
                    filtered.append(kw)
            except:
                continue
        return filtered
