#!/usr/bin/env python3
"""
飞书定时发送 - 快速测试版
立即发送消息，测试功能是否正常
"""
import requests
import json
from datetime import datetime
import time


def send_feishu_message(content, webhook_url):
    """发送飞书消息"""
    data = {
        'msg_type': 'interactive',
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
        response = requests.post(webhook_url, json=data, timeout=10)
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


def send_test_message(webhook_url):
    """发送测试消息"""
    content = f"""**✅ 定时发送测试**

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**🎉 测试成功！**
如果您看到这条消息，说明发送功能工作正常！

---

**💡 下一步**:
1. 运行 feishu_scheduler.py 设置定时任务
2. 选择您想要的定时提醒
3. 保持程序运行，等待定时触发

---

**⏰ 定时任务选项**:
- 每日晨间提醒
- 每日市场更新
- 每日晚间总结
- 每周周报
- 每2小时提醒
"""
    
    print("\n发送测试消息...")
    send_feishu_message(content, webhook_url)


def send_daily_summary(webhook_url):
    """发送日报"""
    content = f"""**📊 每日运营简报**

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 今日检查项**:
- [ ] 检查销售数据
- [ ] 查看竞品动态
- [ ] 处理客户反馈
- [ ] 优化广告预算
- [ ] 更新库存状态

---

**⚠️ 待办事项**:
1. 检查新Review
2. 回复客户消息
3. 调整广告出价
4. 监控BSR排名

---

**💪 加油！让我们一起把产品做得更好！**
"""
    
    print("\n发送日报...")
    send_feishu_message(content, webhook_url)


def send_weekly_report(webhook_url):
    """发送周报"""
    content = f"""**📊 周度运营报告**

**报告周期**: {datetime.now().strftime('%Y年第%W周')}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 本周回顾**:
- 销售额: [待填充数据]
- 订单量: [待填充数据]
- Review数: [待填充数据]
- BSR排名: [待填充数据]

---

**🎯 下周目标**:
1. 提升销量 15%
2. 积累 20+ Reviews
3. 优化 3个Listing
4. 扩展 1个变体

---

**💡 建议**: 连接真实数据源以获得准确报告！
"""
    
    print("\n发送周报...")
    send_feishu_message(content, webhook_url)


def send_product_reminder(webhook_url):
    """发送产品提醒"""
    content = f"""**⚠️ 产品运营提醒**

**提醒时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**🔔 重点关注**:
1. 检查 ponytail extensions 库存
2. 关注差评处理
3. 优化主图点击率
4. 测试不同价格点
5. 监控竞品动态

---

**📌 建议**: 每2小时检查一次关键指标！
"""
    
    print("\n发送产品提醒...")
    send_feishu_message(content, webhook_url)


def main():
    """主函数"""
    
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
    
    print("="*60)
    print("飞书定时发送 - 快速测试")
    print("="*60)
    print()
    
    print("请选择要发送的消息：")
    print("1. 测试消息 (推荐)")
    print("2. 日报")
    print("3. 周报")
    print("4. 产品提醒")
    print("5. 全部发送 (测试用)")
    print()
    
    choice = input("请输入选项 (1-5): ").strip()
    
    if choice == "1":
        send_test_message(WEBHOOK_URL)
    elif choice == "2":
        send_daily_summary(WEBHOOK_URL)
    elif choice == "3":
        send_weekly_report(WEBHOOK_URL)
    elif choice == "4":
        send_product_reminder(WEBHOOK_URL)
    elif choice == "5":
        print("\n将发送所有消息，间隔3秒...")
        send_test_message(WEBHOOK_URL)
        time.sleep(3)
        send_daily_summary(WEBHOOK_URL)
        time.sleep(3)
        send_weekly_report(WEBHOOK_URL)
        time.sleep(3)
        send_product_reminder(WEBHOOK_URL)
    else:
        print("❌ 无效选项")
        print("默认发送测试消息...")
        send_test_message(WEBHOOK_URL)
    
    print("\n" + "="*60)
    print("发送完成！")
    print("请检查飞书群查看消息")
    print("="*60)
    print()
    print("💡 提示: 如需定时发送，请运行 feishu_scheduler.py")


if __name__ == "__main__":
    main()
