import json
import os
import glob
from datetime import datetime, timedelta
from config import DATA_DIR, CATEGORIES

def get_latest_data(category_name):
    pattern = f"{DATA_DIR}/{category_name.replace(' ', '_')}_*.json"
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    files.sort(key=os.path.getmtime, reverse=True)
    latest_file = files[0]
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data, latest_file

def get_last_week_data(category_name):
    pattern = f"{DATA_DIR}/{category_name.replace(' ', '_')}_*.json"
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    files.sort(key=os.path.getmtime, reverse=True)
    
    last_week_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    
    for file_path in files:
        date_str = file_path.split('_')[-1].replace('.json', '')
        if date_str <= last_week_date:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data, file_path
    
    if len(files) > 1:
        second_latest = files[1]
        with open(second_latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, second_latest
    
    return None, None

def analyze_rank_changes(current_data, previous_data):
    if not current_data or not previous_data:
        return [], [], []
    
    previous_by_asin = {item['asin']: item for item in previous_data if item['asin']}
    current_by_asin = {item['asin']: item for item in current_data if item['asin']}
    
    rising_products = []
    falling_products = []
    stable_products = []
    
    for asin, current_item in current_by_asin.items():
        if asin in previous_by_asin:
            prev_item = previous_by_asin[asin]
            rank_change = prev_item['rank'] - current_item['rank']
            
            current_item['rank_change'] = rank_change
            current_item['previous_rank'] = prev_item['rank']
            
            if rank_change >= 5:
                rising_products.append(current_item)
            elif rank_change <= -5:
                falling_products.append(current_item)
            else:
                stable_products.append(current_item)
        else:
            current_item['rank_change'] = None
            current_item['previous_rank'] = None
            stable_products.append(current_item)
    
    rising_products.sort(key=lambda x: x['rank_change'], reverse=True)
    falling_products.sort(key=lambda x: x['rank_change'])
    
    return rising_products, falling_products, stable_products

def analyze_category(category_name):
    result = get_latest_data(category_name)
    if result is None:
        return None
    current_data, current_file = result
    
    result_prev = get_last_week_data(category_name)
    previous_data, previous_file = result_prev if result_prev else (None, None)
    
    if not current_data:
        return None
    
    rising, falling, stable = analyze_rank_changes(current_data, previous_data)
    
    result = {
        'category': category_name,
        'current_date': os.path.basename(current_file).split('_')[-1].replace('.json', '') if current_file else datetime.now().strftime('%Y%m%d'),
        'previous_date': os.path.basename(previous_file).split('_')[-1].replace('.json', '') if previous_file else 'N/A',
        'total_products': len(current_data),
        'rising_count': len(rising),
        'falling_count': len(falling),
        'stable_count': len(stable),
        'rising_products': rising[:10],
        'falling_products': falling[:10],
        'stable_products': stable[:5]
    }
    
    return result

def analyze_all_categories():
    results = {}
    for category_name in CATEGORIES.keys():
        result = analyze_category(category_name)
        if result:
            results[category_name] = result
    return results

if __name__ == "__main__":
    results = analyze_all_categories()
    print(json.dumps(results, ensure_ascii=False, indent=2))