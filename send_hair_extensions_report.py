#!/usr/bin/env python3
"""
发送Hair Extensions调研报告到飞书
"""
import requests
from datetime import datetime


def send_to_feishu():
    """发送调研报告摘要到飞书"""
    
    WEBHOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26'
    
    content = f"""**📊 Hair Extensions 产品调研报告**

**调研时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**🔍 市场规模**
- 月搜索量: 450,000+
- 市场竞争度: 高
- 平均价格: $25-35
- 平均评分: 4.2-4.5

---

**📈 产品分类**

| 类型 | 价格区间 |
|------|---------|
| Clip-in Extensions | $15-50 |
| Tape-in Extensions | $30-100 |
| Human Hair | $50-300 |
| Ponytail Extension | $15-40 |

---

**⏰ 热门规格**
- 长度: 12"-26"
- 材质: Synthetic/Human Hair
- 款式: 直发、波浪、卷发

---

**💰 定价策略**

| 策略 | 价格 | 利润率 |
|------|------|--------|
| 引流款 | $12-18 | 15-20% |
| 主力款 | $22-35 | 25-35% |
| 高端款 | $45-80 | 40-50% |

---

**🎯 目标人群**
1. 日常时尚 - Clip-in, Ponytail
2. 专业造型师 - Human Hair
3. 新娘/特殊场合 - Virgin Hair
4. 青少年 - Synthetic

---

**🔑 核心关键词**
- hair extensions (450K搜索)
- clip in hair extensions (180K)
- human hair extensions (135K)

---

**⚠️ 主要痛点**
1. 颜色不符 (48%)
2. 容易打结 (42%)
3. 掉落/滑落 (35%)

**✅ 好评亮点**
1. 自然逼真
2. 佩戴方便
3. 价格实惠

---

**💡 建议**
- 从Clip-in合成纤维开始
- 主力款售价$25-40
- 保证30%+利润率
- 注重产品质量和图片

---

**📁 完整报告已生成**
- Markdown: 产品调研报告_Hair_Extensions_接发产品.md
- Excel: hair_extensions_research_report.xlsx

请查看workspace目录获取完整报告！
"""
    
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
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 0:
            print('✅ 调研报告已发送到飞书群')
            return True
        else:
            print(f'发送失败: {result.get("msg")}')
            return False
    except Exception as e:
        print(f'发送异常: {e}')
        return False


if __name__ == "__main__":
    print("="*60)
    print("发送Hair Extensions调研报告到飞书")
    print("="*60)
    print()
    
    success = send_to_feishu()
    
    if success:
        print("\n✅ 发送成功！")
        print("请检查飞书群查看调研报告")
    else:
        print("\n❌ 发送失败")
    
    print("="*60)
