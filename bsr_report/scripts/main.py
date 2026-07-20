import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amazon_scraper import scrape_all_categories
from data_analyzer import analyze_all_categories
from feishu_notifier import send_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bsr_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== 开始执行亚马逊BSR排名周报任务 ===")
    
    try:
        logger.info("步骤1：抓取亚马逊BSR数据...")
        scraped_data = scrape_all_categories()
        
        total_products = sum(len(products) for products in scraped_data.values())
        logger.info(f"成功抓取 {total_products} 个商品数据")
        
        if total_products == 0:
            logger.warning("未抓取到有效数据，使用模拟数据进行测试...")
            from mock_data_generator import generate_all_mock_data
            generate_all_mock_data()
        
        logger.info("步骤2：分析数据对比...")
        analysis_results = analyze_all_categories()
        
        if not analysis_results:
            logger.error("数据分析失败，无结果")
            return
        
        logger.info("步骤3：发送飞书周报...")
        success = send_report(analysis_results)
        
        if success:
            logger.info("=== 亚马逊BSR排名周报任务执行完成 ===")
        else:
            logger.error("=== 飞书推送失败 ===")
            
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()