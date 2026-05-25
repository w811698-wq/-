import requests
import json
from datetime import datetime

class FeishuNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_message(self, text):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'msg_type': 'text',
            'content': {
                'text': text
            }
        }
        
        try:
            response = requests.post(self.webhook_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to send message: {e}")
            return None
    
    def format_report(self, all_results, all_summaries):
        today = datetime.now().strftime('%Y年%m月%d日')
        
        lines = []
        lines.append(f"📊 亚马逊假发类目BSR排名周报 - {today}")
        lines.append("---")
        
        all_up = []
        all_down = []
        
        for category, result in all_results.items():
            all_up.extend([{'category': category, **item} for item in result['up_significant']])
            all_down.extend([{'category': category, **item} for item in result['down_significant']])
        
        if all_up:
            lines.append("📈 排名上升显著商品（≥5名）")
            lines.append("| 类目 | 品牌 | 排名变化 | 原因分析 |")
            lines.append("| --- | --- | --- | --- |")
            for item in all_up:
                change_text = f"+{item['change']}（#{item['last_rank']}→#{item['current_rank']}）"
                lines.append(f"| {item['category']} | {item['brand'] or 'N/A'} | {change_text} | {item['reason']} |")
            lines.append("")
        
        if all_down:
            lines.append("📉 排名下降显著商品（≥5名）")
            lines.append("| 类目 | 品牌 | 排名变化 | 原因分析 |")
            lines.append("| --- | --- | --- | --- |")
            for item in all_down:
                change_text = f"{item['change']}（#{item['last_rank']}→#{item['current_rank']}）"
                lines.append(f"| {item['category']} | {item['brand'] or 'N/A'} | {change_text} | {item['reason']} |")
            lines.append("")
        
        lines.append("📊 各品类稳定商品数量")
        lines.append("| 类目 | 稳定商品数 | 上升数 | 下降数 | 新进入 | 掉出榜单 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for summary in all_summaries:
            lines.append(f"| {summary['category']} | {summary['stable_count']} | {summary['up_count']} | {summary['down_count']} | {summary['new_count']} | {summary['dropped_count']} |")
        
        lines.append("")
        lines.append("🎯 关键结论")
        
        total_up = sum(s['up_count'] for s in all_summaries)
        total_down = sum(s['down_count'] for s in all_summaries)
        total_stable = sum(s['stable_count'] for s in all_summaries)
        
        conclusion = f"本周共监控 {sum(s['total_current'] for s in all_summaries)} 个商品，其中 "
        if total_up > 0:
            conclusion += f"{total_up} 个商品排名显著上升，"
        if total_down > 0:
            conclusion += f"{total_down} 个商品排名显著下降，"
        conclusion += f"{total_stable} 个商品排名稳定。"
        
        if total_up > total_down:
            conclusion += "整体趋势偏积极。"
        elif total_down > total_up:
            conclusion += "整体趋势需关注。"
        else:
            conclusion += "整体趋势平稳。"
        
        lines.append(conclusion)
        
        return "\n".join(lines)

if __name__ == '__main__':
    webhook_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159'
    notifier = FeishuNotifier(webhook_url)
    
    sample_results = {
        'Ponytail Extension': {
            'up_significant': [
                {'brand': 'Brand A', 'last_rank': 20, 'current_rank': 10, 'change': 10, 'reason': '优惠券'}
            ],
            'down_significant': [
                {'brand': 'Brand B', 'last_rank': 5, 'current_rank': 15, 'change': -10, 'reason': '未知'}
            ],
            'stable': [],
            'new_entries': [],
            'dropped': []
        },
        'Hair Topper': {
            'up_significant': [],
            'down_significant': [],
            'stable': [],
            'new_entries': [],
            'dropped': []
        },
        'Hair Extensions': {
            'up_significant': [],
            'down_significant': [],
            'stable': [],
            'new_entries': [],
            'dropped': []
        }
    }
    
    sample_summaries = [
        {'category': 'Ponytail Extension', 'stable_count': 15, 'up_count': 2, 'down_count': 1, 'new_count': 3, 'dropped_count': 2, 'total_current': 20},
        {'category': 'Hair Topper', 'stable_count': 18, 'up_count': 1, 'down_count': 1, 'new_count': 2, 'dropped_count': 2, 'total_current': 20},
        {'category': 'Hair Extensions', 'stable_count': 16, 'up_count': 3, 'down_count': 2, 'new_count': 2, 'dropped_count': 1, 'total_current': 20}
    ]
    
    report = notifier.format_report(sample_results, sample_summaries)
    print(report)
    print("\n" + "="*50 + "\n")
    
    result = notifier.send_message(report)
    print("Send result:", result)
