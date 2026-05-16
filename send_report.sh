#!/bin/bash
curl -X POST 'https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26' \
  -H 'Content-Type: application/json' \
  -d '{
    "msg_type": "interactive",
    "card": {
      "config": {
        "wide_screen_mode": true
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "**📊 Hair Extensions 产品调研报告**\n\n**调研时间**: 2026-05-15\n\n---\n\n**🔍 市场规模**\n- 月搜索量: 450,000+\n- 市场竞争度: 高\n- 平均价格: $25-35\n- 平均评分: 4.2-4.5\n\n---\n\n**📈 产品分类**\n| 类型 | 价格区间 |\n|------|---------|  \n| Clip-in Extensions | $15-50 |\n| Tape-in Extensions | $30-100 |\n| Human Hair | $50-300 |\n| Ponytail Extension | $15-40 |\n\n---\n\n**⏰ 热门规格**\n- 长度: 12\"-26\"\n- 材质: Synthetic/Human Hair\n- 款式: 直发、波浪、卷发\n\n---\n\n**💰 定价策略**\n| 策略 | 价格 | 利润率 |\n|------|------|--------|\n| 引流款 | $12-18 | 15-20% |\n| 主力款 | $22-35 | 25-35% |\n| 高端款 | $45-80 | 40-50% |\n\n---\n\n**🎯 目标人群**\n1. 日常时尚 - Clip-in, Ponytail\n2. 专业造型师 - Human Hair\n3. 新娘/特殊场合 - Virgin Hair\n4. 青少年 - Synthetic\n\n---\n\n**🔑 核心关键词**\n- hair extensions (450K搜索)\n- clip in hair extensions (180K)\n- human hair extensions (135K)\n\n---\n\n**⚠️ 主要痛点**\n1. 颜色不符 (48%)\n2. 容易打结 (42%)\n3. 掉落/滑落 (35%)\n\n**✅ 好评亮点**\n1. 自然逼真\n2. 佩戴方便\n3. 价格实惠\n\n---\n\n**💡 建议**\n- 从Clip-in合成纤维开始\n- 主力款售价$25-40\n- 保证30%+利润率\n- 注重产品质量和图片\n\n---\n\n**📁 完整报告已生成**\n- Markdown: 产品调研报告_Hair_Extensions_接发产品.md\n- Excel: hair_extensions_research_report.xlsx\n\n请查看workspace目录获取完整报告！"
        }
      ]
    }
  }'
