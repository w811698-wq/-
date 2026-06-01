#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime, timedelta

def generate_sample_data():
    brands = [
        'Glam Seamless', 'Bellami', 'Luxy Hair', 'Uniwigs', 'Jon Renau',
        'Hair Romance', 'Cashmere Hair', 'Miss Vida', 'Socal', 'Eva Hair',
        'VPartwap', 'Fascinate', 'BingPet', 'Meinaiparts', 'S次的'
    ]

    titles_templates = [
        'Premium {brand} Ponytail Extension - 20" Natural Wavy',
        '{brand} Clip in Hair Extensions - 18" Straight',
        'Luxury {brand} Hair Topper - Coverage Topper 4"x5"',
        '{brand} Human Hair Ponytail - 22" Curly',
        '{brand} Volume Hair Extensions - Seamless Clip in',
        'Professional {brand} Topper - Thin Hair Coverage',
        '{brand} Clip on Ponytail - Quick Weave Style',
        '{brand} Hair Pieces - 16" Short Cut',
        '{brand} Density Topper - 150% Density',
        '{brand} Ponytail Holder - Natural Looking'
    ]

    categories_data = {}

    for category in ['Ponytail Extension', 'Hair Topper', 'Hair Extensions']:
        current_products = []
        previous_products = []

        for i in range(50):
            brand = random.choice(brands)
            title_template = random.choice(titles_templates)
            title = title_template.format(brand=brand)

            asin = f"B{random.randint(1000000000, 9999999999)}"

            current_rank = i + 1
            previous_rank = current_rank + random.randint(-15, 15)

            if random.random() < 0.1:
                previous_rank = current_rank + random.randint(5, 15)
            if random.random() < 0.1:
                previous_rank = current_rank - random.randint(5, 15)

            previous_rank = max(1, min(50, previous_rank))

            current_products.append({
                'asin': asin,
                'title': title,
                'brand': brand,
                'price': round(random.uniform(15.99, 89.99), 2),
                'current_rank': current_rank,
                'category': category
            })

            previous_products.append({
                'asin': asin,
                'title': title,
                'brand': brand,
                'price': round(random.uniform(15.99, 89.99), 2),
                'previous_rank': previous_rank,
                'category': category
            })

        categories_data[category] = {
            'current': current_products,
            'previous': previous_products
        }

    return categories_data

def save_sample_data():
    import os
    os.makedirs('/workspace/data', exist_ok=True)

    sample_data = generate_sample_data()

    for category, data in sample_data.items():
        current_file = f'/workspace/data/current_{category.replace(" ", "_")}.json'
        previous_file = f'/workspace/data/previous_week_{category.replace(" ", "_")}.json'

        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(data['current'], f, ensure_ascii=False, indent=2)

        with open(previous_file, 'w', encoding='utf-8') as f:
            json.dump(data['previous'], f, ensure_ascii=False, indent=2)

    print("✅ 示例数据已生成")
    return sample_data

if __name__ == '__main__':
    save_sample_data()
