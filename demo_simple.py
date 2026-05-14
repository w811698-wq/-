#!/usr/bin/env python3
"""
轻量级演示脚本 - 不依赖外部库
展示项目结构和功能
"""
import os
from datetime import datetime


def ensure_dirs():
    """创建必要的目录"""
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)


def generate_demo_excel():
    """生成简单的演示输出（使用CSV格式代替Excel）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 产品池
    products_csv = os.path.join("output", f"demo_products_{timestamp}.csv")
    with open(products_csv, "w", encoding="utf-8") as f:
        f.write("ASIN,标题,价格,评分,Review数,月销量\n")
        f.write("B001234567,示例产品1,$19.99,4.5,1200,500\n")
        f.write("B007654321,示例产品2,$29.99,4.3,800,300\n")
    
    # 差评分析
    bad_reviews_csv = os.path.join("output", f"demo_bad_reviews_{timestamp}.csv")
    with open(bad_reviews_csv, "w", encoding="utf-8") as f:
        f.write("痛点关键词,频次\n")
        f.write("break,30\n")
        f.write("leak,25\n")
        f.write("small,20\n")
    
    # 好评分析
    good_reviews_csv = os.path.join("output", f"demo_good_reviews_{timestamp}.csv")
    with open(good_reviews_csv, "w", encoding="utf-8") as f:
        f.write("好评关键词,频次\n")
        f.write("durable,40\n")
        f.write("easy,35\n")
        f.write("nice,30\n")
    
    return [products_csv, bad_reviews_csv, good_reviews_csv]


def main():
    print("="*60)
    print("亚马逊产品调研自动化RPA - 轻量级演示")
    print("="*60)
    print()
    
    print("[1/4] 检查项目结构...")
    ensure_dirs()
    print("✓ 目录结构已就绪")
    print()
    
    print("[2/4] 项目文件清单:")
    files = sorted([f for f in os.listdir(".") if f.endswith(".py")])
    for f in files:
        print(f"  - {f}")
    print()
    
    print("[3/4] 核心模块说明:")
    modules = {
        "config.py": "配置文件 - 所有可配置参数",
        "browser.py": "浏览器自动化 - Selenium控制Chrome",
        "plugins.py": "插件集成 - 卖家精灵/西柚",
        "data_processor.py": "数据处理 - 清洗/分析/去重",
        "excel_exporter.py": "Excel导出 - 生成调研报告",
        "amazon_research.py": "调研引擎 - 12步核心流程",
        "main.py": "主程序入口 - 命令行界面",
        "scheduler.py": "定时调度 - 每日/每周自动执行"
    }
    for name, desc in modules.items():
        print(f"  {name:<20} {desc}")
    print()
    
    print("[4/4] 生成演示数据...")
    output_files = generate_demo_excel()
    print("✓ 演示文件已生成:")
    for f in output_files:
        print(f"  - {f}")
    print()
    
    print("="*60)
    print("项目创建完成！")
    print("="*60)
    print()
    print("下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 修改配置: 编辑 config.py")
    print("3. 运行完整演示: python main.py --demo")
    print("4. 实际使用: python main.py --keyword 'your keyword'")
    print()


if __name__ == "__main__":
    main()
