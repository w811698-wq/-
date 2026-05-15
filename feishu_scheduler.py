#!/usr/bin/env python3
"""
定时发送飞书消息系统
支持定时发送报告、进度更新、提醒等功能
"""
import time
import schedule
from datetime import datetime
import requests
import json


class FeishuScheduler:
    """飞书消息定时发送器"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        
    def send_feishu_message(self, content, msg_type="interactive"):
        """发送飞书消息"""
        data = {
            'msg_type': msg_type,
            'card': {
                'config': {'wide_screen_mode': True},
                'elements': [
                    {
                        'tag': 'markdown',
                        'content': content
                    }
                ]
            }
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                print(f"✅ [{datetime.now()}] 消息发送成功")
                return True
            else:
                print(f"❌ [{datetime.now()}] 消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ [{datetime.now()}] 发送异常: {e}")
            return False
    
    def send_morning_checkin(self):
        """发送晨间签到/提醒"""
        content = f"""**🌅 早上好！开始新的一天**

**📅 日期**: {datetime.now().strftime('%Y年%m月%d日')}
**⏰ 时间**: {datetime.now().strftime('%H:%M:%S')}

---

**📋 今日建议任务**:
1. 检查店铺数据
2. 查看竞品动态
3. 处理客户反馈
4. 优化广告预算
5. 更新库存管理

---

**💪 加油！祝今日大卖！**
"""
        print(f"\n[晨间提醒] 发送中...")
        self.send_feishu_message(content)
    
    def send_market_update(self):
        """发送市场更新"""
        content = f"""**📊 市场动态简报**

**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**🔍 关键词趋势**:
- ponytail extensions: 稳定上升
- hair accessories: 季节性增长
- synthetic hair: 持续热门

---

**💰 建议关注**:
- 价格波动监控
- 竞品新品跟踪
- Review变化分析

---

**📌 建议**: 及时调整运营策略！
"""
        print(f"\n[市场更新] 发送中...")
        self.send_feishu_message(content)
    
    def send_evening_summary(self):
        """发送晚间总结"""
        content = f"""**🌙 今日运营总结**

**总结时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 今日回顾**:
- 检查数据完成 ✅
- 处理客户反馈 ✅
- 优化Listing ✅

---

**📋 明日计划**:
- 检查竞品动态
- 调整广告投放
- 处理Review

---

**😴 晚安！明天继续努力！**
"""
        print(f"\n[晚间总结] 发送中...")
        self.send_feishu_message(content)
    
    def send_weekly_report(self):
        """发送周报"""
        content = f"""**📊 周度运营报告**

**报告周期**: {datetime.now().strftime('%Y年第%W周')}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 本周表现**:
- 销售额: [待填充]
- 订单量: [待填充]
- Review数: [待填充]
- BSR排名: [待填充]

---

**🎯 下周目标**:
- 提升销量15%
- 积累20+ Reviews
- 优化3个Listing

---

**💡 建议**: 需要连接真实数据源！
"""
        print(f"\n[周报] 发送中...")
        self.send_feishu_message(content)
    
    def send_product_reminder(self):
        """发送产品提醒"""
        content = f"""**⚠️ 产品运营提醒**

**提醒时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**🔔 重要提醒**:
1. 检查ponytail extensions库存
2. 关注差评处理
3. 优化主图点击率
4. 测试不同价格点

---

**💡 建议**: 每2小时检查一次数据！
"""
        print(f"\n[产品提醒] 发送中...")
        self.send_feishu_message(content)
    
    def test_send(self):
        """测试发送"""
        content = f"""**🧪 定时发送测试**

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**✅ 定时系统正常运行中！**
如果您看到这条消息，说明定时发送功能工作正常。
"""
        print(f"\n[测试消息] 发送中...")
        self.send_feishu_message(content)


def setup_scheduler(webhook_url):
    """设置定时任务"""
    
    scheduler = FeishuScheduler(webhook_url)
    
    # 显示菜单
    print("="*60)
    print("飞书定时发送系统")
    print("="*60)
    print("\n请选择要设置的定时任务：")
    print("1. 每日晨间提醒 (09:00)")
    print("2. 每日市场更新 (12:00)")
    print("3. 每日晚间总结 (18:00)")
    print("4. 每周周报 (周一 10:00)")
    print("5. 每2小时产品提醒")
    print("6. 测试发送 (立即发送)")
    print("7. 自定义时间")
    print("0. 退出")
    print("="*60)
    
    choice = input("\n请输入选项 (0-7): ").strip()
    
    if choice == "1":
        schedule.every().day.at("09:00").do(scheduler.send_morning_checkin)
        print("✅ 已设置: 每日 09:00 晨间提醒")
        
    elif choice == "2":
        schedule.every().day.at("12:00").do(scheduler.send_market_update)
        print("✅ 已设置: 每日 12:00 市场更新")
        
    elif choice == "3":
        schedule.every().day.at("18:00").do(scheduler.send_evening_summary)
        print("✅ 已设置: 每日 18:00 晚间总结")
        
    elif choice == "4":
        schedule.every().monday.at("10:00").do(scheduler.send_weekly_report)
        print("✅ 已设置: 每周一 10:00 周报")
        
    elif choice == "5":
        schedule.every(2).hours.do(scheduler.send_product_reminder)
        print("✅ 已设置: 每2小时产品提醒")
        
    elif choice == "6":
        print("\n立即发送测试消息...")
        scheduler.test_send()
        return
        
    elif choice == "7":
        print("\n可选任务:")
        print("1. 晨间提醒")
        print("2. 市场更新")
        print("3. 晚间总结")
        print("4. 周报")
        print("5. 产品提醒")
        
        task_choice = input("\n选择任务类型 (1-5): ").strip()
        custom_time = input("输入时间 (格式: HH:MM，例如 14:30): ").strip()
        
        task_funcs = {
            "1": scheduler.send_morning_checkin,
            "2": scheduler.send_market_update,
            "3": scheduler.send_evening_summary,
            "4": scheduler.send_weekly_report,
            "5": scheduler.send_product_reminder
        }
        
        if task_choice in task_funcs:
            schedule.every().day.at(custom_time).do(task_funcs[task_choice])
            print(f"✅ 已设置: 每日 {custom_time} 执行任务")
        else:
            print("❌ 无效选项")
            return
            
    elif choice == "0":
        print("👋 退出")
        return
        
    else:
        print("❌ 无效选项")
        return
    
    # 显示已设置的任务
    print("\n" + "="*60)
    print("已设置的定时任务:")
    for job in schedule.jobs:
        print(f"  - {job}")
    print("="*60)
    print("\n调度器已启动，等待执行任务...")
    print("按 Ctrl+C 停止\n")
    
    # 启动调度器
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 调度器已停止")


def main():
    """主函数"""
    
    # 飞书webhook地址
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
    
    print("="*60)
    print("飞书定时发送系统")
    print("="*60)
    print("\n正在初始化...")
    
    # 首先测试发送
    scheduler = FeishuScheduler(WEBHOOK_URL)
    print("\n发送测试消息...")
    scheduler.test_send()
    
    # 设置定时任务
    setup_scheduler(WEBHOOK_URL)


if __name__ == "__main__":
    main()
