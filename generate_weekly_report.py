#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime
import os

class WeeklyReportGenerator:
    def __init__(self):
        self.categories = ['Ponytail Extension', 'Hair Topper', 'Hair Extensions']
        self.feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159'

    def load_data(self):
        all_data = {}

        for category in self.categories:
            category_key = category.replace(' ', '_')

            try:
                with open(f'/workspace/data/current_{category_key}.json', 'r') as f:
                    current_data = json.load(f)
            except:
                print(f"⚠️  未找到当前数据: {category}")
                current_data = []

            try:
                with open(f'/workspace/data/previous_week_{category_key}.json', 'r') as f:
                    previous_data = json.load(f)
            except:
                print(f"⚠️  未找到历史数据: {category}")
                previous_data = []

            all_data[category] = {
                'current': current_data,
                'previous': previous_data
            }

        return all_data

    def compare_data(self, current_products, previous_products):
        previous_dict = {}
        for item in previous_products:
            previous_dict[item['asin']] = item.get('previous_rank', item.get('current_rank'))

        compared_products = []

        for product in current_products:
            asin = product['asin']
            current_rank = product['current_rank']

            if asin in previous_dict:
                prev_rank = previous_dict[asin]
                rank_change = prev_rank - current_rank
            else:
                prev_rank = current_rank
                rank_change = 0

            compared_products.append({
                **product,
                'previous_rank': prev_rank,
                'rank_change': rank_change
            })

        return compared_products

    def analyze_significant_changes(self, products):
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

        title_lower = product.get('title', '').lower()
        brand_lower = product.get('brand', '').lower()

        if 'coupon' in title_lower or 'coupon' in brand_lower:
            causes.append('🎟️ Coupon')

        if any(word in title_lower for word in ['sale', 'discount', '%', 'off', 'deal']):
            causes.append('💰 Discount/Sale')

        if any(word in title_lower for word in ['lightning', 'deal', 'promotion', 'hot']):
            causes.append('⚡ Deal/Promotion')

        if any(word in title_lower for word in ['prime day', 'prime exclusive', 'prime']) and \
           any(word in title_lower for word in ['day', 'event', 'sale']):
            causes.append('🔥 Prime Day Event')

        if not causes:
            causes.append('📊 自然波动')

        return ' '.join(causes)

    def generate_report(self, all_category_data):
        today = datetime.now()

        report_lines = []

        report_lines.append("📊 **亚马逊假发类目BSR周报**\n")
        report_lines.append(f"📅 报告日期: {today.strftime('%Y年%m月%d日 %H:%M')}")
        report_lines.append(f"📆 周次: 第{today.isocalendar()[1]}周\n")

        total_significant_changes = 0

        for category, data in all_category_data.items():
            current = data['current']
            previous = data['previous']

            if not current:
                report_lines.append(f"## 🔹 {category}")
                report_lines.append("⚠️ 暂无数据\n")
                continue

            compared_products = self.compare_data(current, previous)
            significant_changes = self.analyze_significant_changes(compared_products)

            total_significant_changes += len(significant_changes['significant_up']) + len(significant_changes['significant_down'])

            report_lines.append(f"## 🔹 {category}")
            report_lines.append(f"📈 **排名上升≥5名** ({len(significant_changes['significant_up'])}件)\n")

            if significant_changes['significant_up']:
                report_lines.append("| 品牌 | 商品名称 | 排名变化 | 当前排名 | 原因 |")
                report_lines.append("|------|---------|---------|---------|------|")

                for item in significant_changes['significant_up'][:5]:
                    title = item['title'][:40] + '...' if len(item['title']) > 40 else item['title']
                    cause = self.analyze_causes(item)
                    report_lines.append(
                        f"| {item['brand']} | {title} | **+{item['rank_change']}** | #{item['current_rank']} | {cause} |"
                    )
            else:
                report_lines.append("✅ 无显著上升")

            report_lines.append(f"\n📉 **排名下降≥5名** ({len(significant_changes['significant_down'])}件)\n")

            if significant_changes['significant_down']:
                report_lines.append("| 品牌 | 商品名称 | 排名变化 | 当前排名 | 原因 |")
                report_lines.append("|------|---------|---------|---------|------|")

                for item in significant_changes['significant_down'][:5]:
                    title = item['title'][:40] + '...' if len(item['title']) > 40 else item['title']
                    cause = self.analyze_causes(item)
                    report_lines.append(
                        f"| {item['brand']} | {title} | **{item['rank_change']}** | #{item['current_rank']} | {cause} |"
                    )
            else:
                report_lines.append("✅ 无显著下降")

            stable_count = len([p for p in compared_products if abs(p.get('rank_change', 0)) < 5])
            report_lines.append(f"\n📦 **稳定商品数量**: {stable_count}件")
            report_lines.append("")

        report_lines.append("---\n")
        report_lines.append("## 🎯 关键结论\n")

        all_up = []
        all_down = []

        for category, data in all_category_data.items():
            current = data['current']
            previous = data['previous']

            if current and previous:
                compared = self.compare_data(current, previous)
                changes = self.analyze_significant_changes(compared)
                all_up.extend(changes['significant_up'])
                all_down.extend(changes['significant_down'])

        report_lines.append(f"1. 本周共监测到 **{total_significant_changes}** 个商品排名发生显著变化（≥5名）")
        report_lines.append(f"   - 排名上升商品: {len(all_up)}件")
        report_lines.append(f"   - 排名下降商品: {len(all_down)}件\n")

        if all_up:
            top_up = all_up[0]
            report_lines.append(f"2. 🚀 **本周最大黑马**: {top_up['brand']} 上升 {top_up['rank_change']} 名")
            report_lines.append(f"   商品: {top_up['title'][:50]}...\n")

        report_lines.append("3. 💡 **建议关注**:")
        report_lines.append("   - 排名持续上升的商品可能是促销或优惠活动带来的流量")
        report_lines.append("   - 分析竞品营销策略，优化自身产品竞争力")
        report_lines.append("   - 关注即将到来的促销活动节点\n")

        report_lines.append("4. 📈 **数据说明**:")
        report_lines.append("   - 数据来源于亚马逊BSR排名")
        report_lines.append("   - 排名变化值 = 上周排名 - 本周排名（正数表示上升）")

        return '\n'.join(report_lines)

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
                result = response.json()
                if result.get('StatusCode') == 0:
                    print("✅ 飞书推送成功!")
                    return True
                else:
                    print(f"❌ 飞书推送失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print("❌ 飞书推送超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 飞书推送异常: {e}")
            return False
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False

    def save_report(self, report):
        os.makedirs('/workspace/reports', exist_ok=True)

        filename = f"/workspace/reports/weekly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 报告已保存: {filename}")
        return filename

    def run(self):
        print("="*60)
        print("🚀 亚马逊BSR周报生成器")
        print("="*60)

        print("\n📥 加载数据...")
        all_data = self.load_data()

        print("\n📊 生成报告...")
        report = self.generate_report(all_data)

        print("\n" + "="*60)
        print("📋 报告预览:")
        print("="*60)
        print(report)
        print("="*60)

        print("\n💾 保存报告...")
        self.save_report(report)

        print("\n📤 推送到飞书...")
        success = self.send_to_feishu(report)

        if success:
            print("\n✅ 周报生成并推送成功!")
        else:
            print("\n⚠️  报告已生成但推送失败，请检查飞书Webhook配置")

        return report

if __name__ == '__main__':
    generator = WeeklyReportGenerator()
    report = generator.run()
