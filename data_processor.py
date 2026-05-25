import os
import json
from datetime import datetime, timedelta

class DataProcessor:
    DATA_DIR = 'data'
    
    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
    
    def save_data(self, data, category):
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{self.DATA_DIR}/{category}_{today}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def get_last_week_data(self, category):
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        filename = f"{self.DATA_DIR}/{category}_{last_week}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_all_historical_data(self, category):
        files = [f for f in os.listdir(self.DATA_DIR) if f.startswith(category)]
        files.sort()
        return files
    
    def compare_data(self, current_data, last_week_data):
        if not last_week_data:
            return {
                'up_significant': [],
                'down_significant': [],
                'stable': [],
                'new_entries': [],
                'dropped': []
            }
        
        current_by_asin = {item['asin']: item for item in current_data}
        last_week_by_asin = {item['asin']: item for item in last_week_data}
        
        up_significant = []
        down_significant = []
        stable = []
        new_entries = []
        dropped = []
        
        for asin, current in current_by_asin.items():
            if asin in last_week_by_asin:
                last_rank = last_week_by_asin[asin]['rank']
                current_rank = current['rank']
                
                if last_rank and current_rank:
                    change = last_rank - current_rank
                    
                    if change >= 5:
                        reason = self._analyze_reason(current)
                        up_significant.append({
                            'brand': current['brand'],
                            'asin': current['asin'],
                            'title': current['title'],
                            'last_rank': last_rank,
                            'current_rank': current_rank,
                            'change': change,
                            'reason': reason,
                            'price': current['price']
                        })
                    elif change <= -5:
                        reason = self._analyze_reason(current)
                        down_significant.append({
                            'brand': current['brand'],
                            'asin': current['asin'],
                            'title': current['title'],
                            'last_rank': last_rank,
                            'current_rank': current_rank,
                            'change': change,
                            'reason': reason,
                            'price': current['price']
                        })
                    else:
                        stable.append({
                            'brand': current['brand'],
                            'asin': current['asin'],
                            'title': current['title'],
                            'last_rank': last_rank,
                            'current_rank': current_rank,
                            'change': change,
                            'price': current['price']
                        })
        
        for asin in last_week_by_asin:
            if asin not in current_by_asin:
                dropped.append(last_week_by_asin[asin])
        
        for asin in current_by_asin:
            if asin not in last_week_by_asin:
                new_entries.append(current_by_asin[asin])
        
        return {
            'up_significant': up_significant,
            'down_significant': down_significant,
            'stable': stable,
            'new_entries': new_entries,
            'dropped': dropped
        }
    
    def _analyze_reason(self, product):
        reasons = []
        
        if product.get('has_coupon'):
            reasons.append('优惠券')
        if product.get('has_deal'):
            reasons.append('促销活动')
        
        if self._is_prime_day():
            reasons.append('Prime Day')
        
        if self._is_lightning_deal(product):
            reasons.append('Lightning Deal')
        
        return ', '.join(reasons) if reasons else '未知'
    
    def _is_prime_day(self):
        today = datetime.now()
        return (today.month == 7 or today.month == 10) and 10 <= today.day <= 20
    
    def _is_lightning_deal(self, product):
        title = product.get('title', '').lower()
        return 'lightning deal' in title
    
    def generate_summary(self, comparison_result, category):
        summary = {
            'category': category,
            'total_current': len(comparison_result['up_significant']) + 
                           len(comparison_result['down_significant']) + 
                           len(comparison_result['stable']),
            'up_count': len(comparison_result['up_significant']),
            'down_count': len(comparison_result['down_significant']),
            'stable_count': len(comparison_result['stable']),
            'new_count': len(comparison_result['new_entries']),
            'dropped_count': len(comparison_result['dropped'])
        }
        return summary

if __name__ == '__main__':
    processor = DataProcessor()
    
    sample_current = [
        {'asin': 'B012345678', 'title': 'Product A', 'brand': 'Brand A', 'rank': 5, 'price': '$29.99', 'has_coupon': True, 'has_deal': False},
        {'asin': 'B012345679', 'title': 'Product B', 'brand': 'Brand B', 'rank': 15, 'price': '$39.99', 'has_coupon': False, 'has_deal': True},
        {'asin': 'B012345680', 'title': 'Product C', 'brand': 'Brand C', 'rank': 25, 'price': '$19.99', 'has_coupon': False, 'has_deal': False}
    ]
    
    sample_last_week = [
        {'asin': 'B012345678', 'title': 'Product A', 'brand': 'Brand A', 'rank': 12, 'price': '$29.99', 'has_coupon': False, 'has_deal': False},
        {'asin': 'B012345679', 'title': 'Product B', 'brand': 'Brand B', 'rank': 8, 'price': '$49.99', 'has_coupon': False, 'has_deal': False},
        {'asin': 'B012345681', 'title': 'Product D', 'brand': 'Brand D', 'rank': 30, 'price': '$25.99', 'has_coupon': False, 'has_deal': False}
    ]
    
    result = processor.compare_data(sample_current, sample_last_week)
    print("Up significant:", result['up_significant'])
    print("Down significant:", result['down_significant'])
    print("Stable:", result['stable'])
    print("New:", result['new_entries'])
    print("Dropped:", result['dropped'])
    
    summary = processor.generate_summary(result, 'Test Category')
    print("Summary:", summary)
