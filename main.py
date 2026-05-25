import logging
from datetime import datetime
from amazon_scraper import AmazonBSRScraper
from data_processor import DataProcessor
from feishu_notifier import FeishuNotifier

FEISHU_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159'
CATEGORIES = ['Ponytail Extension', 'Hair Topper', 'Hair Extensions']

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
    
    scraper = AmazonBSRScraper()
    processor = DataProcessor()
    notifier = FeishuNotifier(FEISHU_WEBHOOK)
    
    all_results = {}
    all_summaries = []
    
    for category in CATEGORIES:
        logger.info(f"正在抓取 {category} 类目数据...")
        
        try:
            current_data = scraper.get_bsr_data(category)
            
            if not current_data:
                logger.warning(f"{category} 类目未抓取到数据")
                continue
            
            logger.info(f"成功抓取 {len(current_data)} 条数据")
            
            processor.save_data(current_data, category)
            
            last_week_data = processor.get_last_week_data(category)
            
            if last_week_data:
                logger.info(f"找到上周数据，共 {len(last_week_data)} 条")
                result = processor.compare_data(current_data, last_week_data)
                summary = processor.generate_summary(result, category)
            else:
                logger.info("未找到上周数据，跳过对比")
                result = {
                    'up_significant': [],
                    'down_significant': [],
                    'stable': [],
                    'new_entries': current_data,
                    'dropped': []
                }
                summary = {
                    'category': category,
                    'total_current': len(current_data),
                    'up_count': 0,
                    'down_count': 0,
                    'stable_count': 0,
                    'new_count': len(current_data),
                    'dropped_count': 0
                }
            
            all_results[category] = result
            all_summaries.append(summary)
            
            logger.info(f"{category} - 上升: {summary['up_count']}, 下降: {summary['down_count']}, 稳定: {summary['stable_count']}")
            
        except Exception as e:
            logger.error(f"处理 {category} 时发生错误: {e}")
            continue
    
    if not all_summaries:
        logger.error("未能获取任何数据，跳过飞书推送")
        return
    
    logger.info("正在生成报告...")
    report = notifier.format_report(all_results, all_summaries)
    
    logger.info("正在发送飞书消息...")
    result = notifier.send_message(report)
    
    if result and result.get('StatusCode') == 0:
        logger.info("飞书消息发送成功")
    else:
        logger.error(f"飞书消息发送失败: {result}")
    
    logger.info("=== BSR周报任务执行完成 ===")

if __name__ == '__main__':
    main()
