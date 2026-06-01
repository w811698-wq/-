#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import os
import sys

sys.path.insert(0, '/workspace')
from generate_weekly_report import WeeklyReportGenerator

class TestBSRReporter(unittest.TestCase):

    def setUp(self):
        self.generator = WeeklyReportGenerator()

    def test_data_loading(self):
        """测试数据加载功能"""
        all_data = self.generator.load_data()

        self.assertIsInstance(all_data, dict)
        self.assertEqual(len(all_data), 3)

        for category in ['Ponytail Extension', 'Hair Topper', 'Hair Extensions']:
            self.assertIn(category, all_data)
            self.assertIn('current', all_data[category])
            self.assertIn('previous', all_data[category])

    def test_data_comparison(self):
        """测试数据对比功能"""
        current = [
            {'asin': 'B123', 'title': 'Test', 'brand': 'BrandA', 'price': 29.99, 'current_rank': 1}
        ]

        previous = [
            {'asin': 'B123', 'title': 'Test', 'brand': 'BrandA', 'price': 29.99, 'previous_rank': 5}
        ]

        result = self.generator.compare_data(current, previous)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rank_change'], 4)
        self.assertEqual(result[0]['previous_rank'], 5)
        self.assertEqual(result[0]['current_rank'], 1)

    def test_significant_changes(self):
        """测试显著变化分析"""
        products = [
            {'asin': 'B1', 'rank_change': 10},
            {'asin': 'B2', 'rank_change': 5},
            {'asin': 'B3', 'rank_change': 2},
            {'asin': 'B4', 'rank_change': -5},
            {'asin': 'B5', 'rank_change': -10}
        ]

        result = self.generator.analyze_significant_changes(products)

        self.assertEqual(len(result['significant_up']), 2)
        self.assertEqual(len(result['significant_down']), 2)

        self.assertEqual(result['significant_up'][0]['asin'], 'B1')
        self.assertEqual(result['significant_down'][0]['asin'], 'B5')

    def test_causes_analysis(self):
        """测试原因分析功能"""
        test_cases = [
            {
                'product': {'title': 'Hair Extension with Coupon', 'brand': 'Brand'},
                'expected_keywords': ['Coupon']
            },
            {
                'product': {'title': 'Hair Extension Sale 20%', 'brand': 'Brand'},
                'expected_keywords': ['Discount']
            },
            {
                'product': {'title': 'Hair Extension Lightning Deal', 'brand': 'Brand'},
                'expected_keywords': ['Deal']
            },
            {
                'product': {'title': 'Hair Extension', 'brand': 'Brand'},
                'expected_keywords': ['自然波动']
            }
        ]

        for test_case in test_cases:
            result = self.generator.analyze_causes(test_case['product'])

            for keyword in test_case['expected_keywords']:
                self.assertIn(keyword, result)

    def test_report_generation(self):
        """测试报告生成"""
        all_data = self.generator.load_data()
        report = self.generator.generate_report(all_data)

        self.assertIsInstance(report, str)
        self.assertIn('亚马逊假发类目BSR周报', report)
        self.assertIn('Ponytail Extension', report)
        self.assertIn('Hair Topper', report)
        self.assertIn('Hair Extensions', report)

    def test_feishu_webhook(self):
        """测试飞书Webhook配置"""
        self.assertIn('open.feishu.cn', self.generator.feishu_webhook)
        self.assertTrue(self.generator.feishu_webhook.startswith('https://'))

    def test_data_persistence(self):
        """测试数据持久化"""
        self.assertTrue(os.path.exists('/workspace/data'))

        for category in ['Ponytail Extension', 'Hair Topper', 'Hair Extensions']:
            category_key = category.replace(' ', '_')

            current_file = f'/workspace/data/current_{category_key}.json'
            previous_file = f'/workspace/data/previous_week_{category_key}.json'

            self.assertTrue(os.path.exists(current_file), f'{current_file} 不存在')
            self.assertTrue(os.path.exists(previous_file), f'{previous_file} 不存在')

            with open(current_file, 'r') as f:
                current_data = json.load(f)
                self.assertIsInstance(current_data, list)

            with open(previous_file, 'r') as f:
                previous_data = json.load(f)
                self.assertIsInstance(previous_data, list)

def run_tests():
    """运行所有测试"""
    print("="*60)
    print("🧪 运行BSR周报系统测试")
    print("="*60)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestBSRReporter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("="*60)

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
