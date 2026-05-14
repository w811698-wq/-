#!/usr/bin/env python3
"""
亚马逊产品调研自动化RPA主程序
"""
import argparse
import sys
from amazon_research import AmazonResearchRPA


def main():
    parser = argparse.ArgumentParser(description='亚马逊产品调研自动化RPA')
    parser.add_argument('--keyword', '-k', type=str, default='water bottle', 
                        help='种子关键词')
    parser.add_argument('--brand', '-b', type=str, default='MyBrand', 
                        help='品牌名称')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='运行演示模式（模拟数据）')
    
    args = parser.parse_args()
    
    print("="*60)
    print("亚马逊产品调研自动化RPA系统")
    print("="*60)
    
    if args.demo:
        run_demo()
    else:
        try:
            with AmazonResearchRPA() as rpa:
                output_file = rpa.run_full_research(args.keyword, args.brand)
                if output_file:
                    print("\n调研完成！")
                else:
                    print("\n调研失败，请检查日志。")
        except Exception as e:
            print(f"\n错误: {e}")
            sys.exit(1)


def run_demo():
    print("\n[演示模式]")
    print("-"*60)
    
    from data_processor import DataProcessor
    from excel_exporter import ExcelExporter
    
    processor = DataProcessor()
    exporter = ExcelExporter()
    
    demo_data = {
        'products': [
            {'asin': 'B001234567', 'title': '示例产品1', 'price': '$19.99', 'rating': '4.5', 'reviews': '1200', 'monthly_sales': '500'},
            {'asin': 'B007654321', 'title': '示例产品2', 'price': '$29.99', 'rating': '4.3', 'reviews': '800', 'monthly_sales': '300'}
        ],
        'strategy': [
            {'asin': 'B001234567', 'title': '示例产品1', 'strategy_type': '精品', 'has_aplus': '是', 'has_video': '是'}
        ],
        'reviews_analysis': {
            'bad_reviews_count': 50,
            'good_reviews_count': 200,
            'pain_points': [('break', 30), ('leak', 25), ('small', 20)],
            'praise_points': [('durable', 40), ('easy', 35), ('nice', 30)]
        },
        'keywords': [
            {'keyword': 'water bottle', 'search_volume': '50000', 'competition': '0.5'},
            {'keyword': 'insulated water bottle', 'search_volume': '30000', 'competition': '0.4'}
        ],
        'matrix': [
            {'audience': '女性', '居家': ['water bottle'], '办公': ['insulated water bottle']}
        ],
        'selling_points': {
            'core': ['解决 break 问题', '解决 leak 问题'],
            'differential': ['突出 durable 优势', '突出 easy 优势'],
            'trust': ['品质保证', '7天无理由退换', '专业客服']
        }
    }
    
    output_file = exporter.export_all(demo_data)
    print(f"\n演示数据已导出至: {output_file}")
    print("\n提示: 实际运行时需要配置卖家精灵/西柚账号密码")


if __name__ == '__main__':
    main()
