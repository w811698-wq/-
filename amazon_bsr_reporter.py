#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import json
import time
import re
from bs4 import BeautifulSoup
import random

class AmazonBSRReporter:
    def __init__(self):
        self.categories = {
            'Ponytail Extension': '2288373011',
            'Hair Topper': '2288374011',
            'Hair Extensions': '2288375011'
        }
        self.feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159'

    def fetch_bsr_data(self, category_name, category_id, max_pages=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        products = []

        for page in range(1, max_pages + 1):
            try:
                url = f'https://www.amazon.com/s?k=wigs&s=review-rank&i=fashion&rh=n%3A{category_id}&page={page}'

                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    items = soup.select('[data-asin]')

                    for item in items:
                        asin = item.get('data-asin')
                        if not asin or asin == '':
                            continue

                        title_elem = item.select_one('h2 a span, .a-text-normal')
                        price_elem = item.select_one('.a-price .a-offscreen, .a-color-price')
                        brand_elem = item.select_one('.a-size-base-plus')

                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        else:
                            continue

                        price_text = price_elem.get_text(strip=True) if price_elem else 'N/A'
                        price = float(re.sub(r'[^\d.]', '', price_text)) if price_text != 'N/A' else 0

                        rank_elem = item.select_one('.s numeral')
                        rank = int(rank_elem.get_text(strip=True)) if rank_elem else len(products) + 1

                        products.append({
                            'asin': asin,
                            'title': title[:80],
                            'brand': brand_elem.get_text(strip=True) if brand_elem else 'Unknown',
                            'price': price,
                            'current_rank': len(products) + 1,
                            'category': category_name
                        })

                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"Error fetching page {page} for {category_name}: {e}")
                continue

        return products

    def fetch_weekly_data(self, category_name):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        category_id = self.categories.get(category_name)

        try:
            url = f'https://api_keepa_or_junglescout/analysis'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()

        except:
            pass

        return None

    def compare_with_previous_week(self, current_data, previous_data):
        previous_dict = {item['asin']: item['previous_rank'] for item in previous_data}

        comparison_results = []

        for product in current_data:
            asin = product['asin']

            if asin in previous_dict:
                previous_rank = previous_dict[asin]
                current_rank = product['current_rank']
                rank_change = previous_rank - current_rank

                comparison_results.append({
                    **product,
                    'previous_rank': previous_rank,
                    'rank_change': rank_change
                })
            else:
                comparison_results.append({
                    **product,
                    'previous_rank': None,
                    'rank_change': 0
                })

        return comparison_results

    def analyze_rank_changes(self, products):
        significant_up = []
        significant_down = []

        for product in products:
            if product['rank_change'] >= 5:
                significant_up.append(product)
            elif product['rank_change'] <= -5:
                significant_down.append(product)

        return {
            'significant_up': sorted(significant_up, key=lambda x: x['rank_change'], reverse=True),
            'significant_down': sorted(significant_down, key=lambda x: x['rank_change'])
        }

    def analyze_causes(self, product):
        causes = []

        if 'coupon' in product.get('title', '').lower():
            causes.append('Coupon')

        if any(word in product.get('title', '').lower() for word in ['sale', 'discount', '%']):
            causes.append('Discount')

        if any(word in product.get('title', '').lower() for word in ['deal', 'promotion', 'lightning']):
            causes.append('Deal/Promotion')

        if any(word in product.get('title', '').lower() for word in ['prime day', 'prime exclusive']):
            causes.append('Prime Day Event')

        if not causes:
            causes.append('自然波动')

        return ', '.join(causes)

    def generate_report(self, all_category_data):
        today = datetime.now().strftime('%Y-%m-%d %W')

        report_sections = []
        report_sections.append(f"📊 **亚马逊假发类目BSR周报**")
        report_sections.append(f"📅 报告日期: {datetime.now().strftime('%Y年%m月%d日')}\n")

        for category, data in all_category_data.items():
            report_sections.append(f"## 🔹 {category}")

            if data.get('significant_changes'):
                changes = data['significant_changes']

                report_sections.append(f"**📈 排名上升≥5名 ({len(changes['significant_up'])})件):**")
                if changes['significant_up']:
                    report_sections.append("| 品牌 | 排名变化 | 当前排名 | 可能原因 |")
                    report_sections.append("|------|---------|---------|---------|")
                    for item in changes['significant_up'][:5]:
                        cause = self.analyze_causes(item)
                        report_sections.append(f"| {item['brand']} | +{item['rank_change']} | #{item['current_rank']} | {cause} |")
                else:
                    report_sections.append("无")

                report_sections.append(f"\n**📉 排名下降≥5名 ({len(changes['significant_down'])})件):**")
                if changes['significant_down']:
                    report_sections.append("| 品牌 | 排名变化 | 当前排名 | 可能原因 |")
                    report_sections.append("|------|---------|---------|---------|")
                    for item in changes['significant_down'][:5]:
                        cause = self.analyze_causes(item)
                        report_sections.append(f"| {item['brand']} | {item['rank_change']} | #{item['current_rank']} | {cause} |")
                else:
                    report_sections.append("无")

            stable_count = len([p for p in data.get('all_products', []) if abs(p.get('rank_change', 0)) < 5])
            report_sections.append(f"\n**📦 稳定商品数量: {stable_count}件**\n")

        report_sections.append("## 🎯 关键结论")

        total_significant = sum(len(d['significant_changes']['significant_up'] + d['significant_changes']['significant_down'])
                                for d in all_category_data.values())

        report_sections.append(f"1. 本周共监测到{total_significant}个商品排名发生显著变化（≥5名）")
        report_sections.append("2. 重点关注排名上升商品，可能是促销或优惠活动带来的流量")
        report_sections.append("3. 建议持续跟踪高频变化商品，分析竞品营销策略")

        return '\n'.join(report_sections)

    def send_to_feishu(self, message):
        payload = {
            'msg_type': 'text',
            'content': {
                'text': message
            }
        }

        try:
            response = requests.post(self.feishu_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ 飞书推送成功")
                return True
            else:
                print(f"❌ 飞书推送失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 飞书推送异常: {e}")
            return False

    def run_weekly_report(self):
        print(f"🚀 开始生成BSR周报... ({datetime.now()})")

        all_category_data = {}

        for category_name in self.categories.keys():
            print(f"\n📦 正在抓取: {category_name}")

            try:
                current_data = self.fetch_bsr_data(category_name, self.categories[category_name])

                previous_week_data = self.load_previous_week_data(category_name)

                if previous_week_data:
                    compared_data = self.compare_with_previous_week(current_data, previous_week_data)
                else:
                    compared_data = [
                        {**item, 'previous_rank': None, 'rank_change': 0}
                        for item in current_data
                    ]

                significant_changes = self.analyze_rank_changes(compared_data)

                all_category_data[category_name] = {
                    'all_products': compared_data,
                    'significant_changes': significant_changes
                }

                print(f"✅ {category_name}: 获取{len(current_data)}条数据")

                self.save_current_data(category_name, current_data)

            except Exception as e:
                print(f"❌ {category_name}数据抓取失败: {e}")
                all_category_data[category_name] = {
                    'all_products': [],
                    'significant_changes': {'significant_up': [], 'significant_down': []}
                }

        report = self.generate_report(all_category_data)

        print("\n" + "="*50)
        print(report)
        print("="*50)

        self.send_to_feishu(report)

        self.save_report_to_file(report)

        print("\n✅ 周报生成完成!")

    def load_previous_week_data(self, category):
        try:
            with open(f'/workspace/data/previous_week_{category}.json', 'r') as f:
                return json.load(f)
        except:
            return None

    def save_current_data(self, category, data):
        try:
            import os
            os.makedirs('/workspace/data', exist_ok=True)
            with open(f'/workspace/data/current_{category}.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def save_report_to_file(self, report):
        try:
            with open(f'/workspace/reports/weekly_report_{datetime.now().strftime("%Y%m%d")}.md', 'w') as f:
                f.write(report)
        except Exception as e:
            print(f"保存报告失败: {e}")

if __name__ == '__main__':
    reporter = AmazonBSRReporter()
    reporter.run_weekly_report()
