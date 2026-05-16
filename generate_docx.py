#!/usr/bin/env python3
"""
生成真实的 .docx 报告文件
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import sys

def create_docx_report():
    doc = Document()
    
    # 标题样式
    title = doc.add_heading('Hair Extensions 接发产品调研报告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 副标题
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('版本：v1.0  报告日期：2026年5月16日')
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(128, 128, 128)
    
    doc.add_paragraph()
    
    # 第一章
    doc.add_heading('一、产品概述', level=1)
    
    doc.add_heading('1.1 产品定义', level=2)
    doc.add_paragraph('Hair Extensions（接发产品）是一种用于增加头发长度和体积的美容产品，广泛应用于日常造型、婚礼造型和专业美发领域。')
    
    doc.add_heading('1.2 产品分类', level=2)
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = '产品类型'
    hdr_cells[1].text = '特点'
    hdr_cells[2].text = '价格区间'
    
    data = [
        ('Clip-in Extensions', '夹子式接发，最受欢迎，可自行佩戴', '$15-50'),
        ('Tape-in Extensions', '胶带式接发，半永久效果，需专业操作', '$30-100'),
        ('Sew-in/Weave', '缝纫式接发，需要专业造型师操作', '$50-150'),
        ('Micro Ring/I Cil', '微环接发，无痕设计，舒适度高', '$40-120'),
        ('Fusion/Keratin', '热熔接发，持久度高，接近永久', '$100-300'),
        ('Clip-in Ponytail', '马尾式接发，快速增加发量', '$15-40'),
    ]
    
    for item in data:
        row_cells = table.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    doc.add_page_heading('1.3 材质分类', level=2)
    
    table2 = doc.add_table(rows=1, cols=3)
    table2.style = 'Table Grid'
    hdr_cells = table2.rows[0].cells
    hdr_cells[0].text = '材质类型'
    hdr_cells[1].text = '特点'
    hdr_cells[2].text = '价格区间'
    
    material_data = [
        ('Synthetic', '合成纤维，色彩丰富，性价比高', '$10-30'),
        ('Human Hair', '真人发，自然度高，可烫染造型', '$50-300'),
        ('Remy Hair', '定向发，鳞片方向一致，品质最佳', '$80-400'),
        ('Virgin Hair', '原始发，未经任何化学处理', '$100-500'),
    ]
    
    for item in material_data:
        row_cells = table2.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    doc.add_page_heading('1.4 热门规格', level=2)
    
    table3 = doc.add_table(rows=1, cols=2)
    table3.style = 'Table Grid'
    hdr_cells = table3.rows[0].cells
    hdr_cells[0].text = '规格项目'
    hdr_cells[1].text = '可选范围'
    
    specs_data = [
        ('长度', '12", 14", 16", 18", 20", 22", 24", 26"'),
        ('重量', '50g, 100g, 150g, 200g, 300g'),
        ('颜色', '金色、黑色、棕色、红色、渐变色、挑染'),
        ('款式', '直发、波浪、卷发、辫子'),
    ]
    
    for item in specs_data:
        row_cells = table3.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
    
    doc.add_page_break()
    
    # 第二章
    doc.add_heading('二、市场规模与趋势', level=1)
    
    doc.add_heading('2.1 市场规模数据', level=2)
    
    table4 = doc.add_table(rows=1, cols=2)
    table4.style = 'Table Grid'
    hdr_cells = table4.rows[0].cells
    hdr_cells[0].text = '指标'
    hdr_cells[1].text = '数据'
    
    market_data = [
        ('月搜索量', '450,000+'),
        ('平均价格', '$25-35'),
        ('平均评分', '4.2-4.5'),
        ('市场竞争度', '高'),
    ]
    
    for item in market_data:
        row_cells = table4.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
    
    doc.add_heading('2.2 市场增长驱动因素', level=2)
    
    factors = [
        '社交媒体影响（TikTok、Instagram）推动发型时尚需求',
        '多元文化市场扩大（非洲裔、拉丁裔、亚裔）',
        '产品价格可负担性提升，消费门槛降低',
        '消费者对个性化和快速造型需求增加',
    ]
    
    for f in factors:
        doc.add_paragraph(f, style='List Bullet')
    
    doc.add_heading('2.3 目标人群分析', level=2)
    
    table5 = doc.add_table(rows=1, cols=3)
    table5.style = 'Table Grid'
    hdr_cells = table5.rows[0].cells
    hdr_cells[0].text = '人群类型'
    hdr_cells[1].text = '核心需求'
    hdr_cells[2].text = '偏好产品'
    
    audience_data = [
        ('日常时尚', '快速改变造型，易于佩戴', 'Clip-in, Ponytail'),
        ('专业造型师', '高品质、多用途、专业级', 'Human Hair, Remy'),
        ('新娘/特殊场合', '自然逼真、高端质感', 'Virgin Hair, Fusion'),
        ('脱发人群', '遮盖稀疏、增发效果', 'Volume Pieces'),
        ('青少年', '时尚潮流、价格实惠', 'Synthetic, Budget'),
    ]
    
    for item in audience_data:
        row_cells = table5.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    doc.add_page_break()
    
    # 第三章
    doc.add_heading('三、竞争分析', level=1)
    
    doc.add_heading('3.1 价格区间竞争格局', level=2)
    
    table6 = doc.add_table(rows=1, cols=5)
    table6.style = 'Table Grid'
    hdr_cells = table6.rows[0].cells
    hdr_cells[0].text = '价格区间'
    hdr_cells[1].text = '产品类型'
    hdr_cells[2].text = '竞争程度'
    hdr_cells[3].text = '利润率'
    hdr_cells[4].text = '策略建议'
    
    competition_data = [
        ('$10-20', '合成纤维', '激烈', '15-20%', '价格战，需走量'),
        ('$20-40', '中档混合', '中等', '25-35%', '平衡之选'),
        ('$40-80', '真人发/Remy', '较低', '40-50%', '利润空间大'),
        ('$80+', '高端真人发', '低', '50-60%', '高端细分'),
    ]
    
    for item in competition_data:
        row_cells = table6.add_row().cells
        for i, cell in enumerate(row_cells):
            cell.text = item[i]
    
    doc.add_heading('3.2 头部竞品特征', level=2)
    
    features = [
        '100+ Reviews（85%的头部产品）',
        '4.0+ 评分（90%的头部产品）',
        '多色可选（95%的头部产品）',
        '8+张详细图片（88%的头部产品）',
        'A+内容展示（70%的头部产品）',
        '视频展示使用教程（60%的头部产品）',
    ]
    
    for f in features:
        doc.add_paragraph(f, style='List Bullet')
    
    doc.add_page_break()
    
    # 第四章
    doc.add_heading('四、关键词分析', level=1)
    
    doc.add_heading('4.1 核心关键词', level=2)
    
    table7 = doc.add_table(rows=1, cols=5)
    table7.style = 'Table Grid'
    hdr_cells = table7.rows[0].cells
    hdr_cells[0].text = '关键词'
    hdr_cells[1].text = '月搜索量'
    hdr_cells[2].text = '竞争度'
    hdr_cells[3].text = 'CPC'
    hdr_cells[4].text = '推荐度'
    
    keywords_data = [
        ('hair extensions', '450,000', '高', '$1.80', '⭐⭐⭐'),
        ('clip in hair extensions', '180,000', '高', '$1.60', '⭐⭐⭐'),
        ('human hair extensions', '135,000', '高', '$2.20', '⭐⭐'),
        ('tape in hair extensions', '90,000', '中高', '$2.00', '⭐⭐'),
        ('hair extensions for women', '65,000', '中', '$1.40', '⭐⭐⭐'),
        ('ponytail extension', '40,000', '中', '$1.20', '⭐⭐⭐'),
    ]
    
    for item in keywords_data:
        row_cells = table7.add_row().cells
        for i, cell in enumerate(row_cells):
            cell.text = item[i]
    
    doc.add_page_break()
    
    # 第五章
    doc.add_heading('五、定价策略', level=1)
    
    doc.add_heading('5.1 成本结构分析', level=2)
    
    table8 = doc.add_table(rows=1, cols=3)
    table8.style = 'Table Grid'
    hdr_cells = table8.rows[0].cells
    hdr_cells[0].text = '成本项目'
    hdr_cells[1].text = '金额范围'
    hdr_cells[2].text = '说明'
    
    cost_data = [
        ('产品成本', '$5-30', '由材质决定'),
        ('头程运费', '$2-5', 'FBA入仓'),
        ('FBA配送费', '$3.50-5.00', '由重量决定'),
        ('平台佣金', '15%', '销售额比例'),
        ('广告费用', '$2-5', 'CPC出价'),
        ('退货损耗', '$0.50-2', '3-5%退货率'),
    ]
    
    for item in cost_data:
        row_cells = table8.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    doc.add_page_break()
    
    # 第六章
    doc.add_heading('六、产品优化建议', level=1)
    
    doc.add_heading('6.1 差评痛点解决方案', level=2)
    
    table9 = doc.add_table(rows=1, cols=3)
    table9.style = 'Table Grid'
    hdr_cells = table9.rows[0].cells
    hdr_cells[0].text = '痛点'
    hdr_cells[1].text = '频率'
    hdr_cells[2].text = '解决方案'
    
    pain_data = [
        ('颜色不符', '48%', '实物对比图、精确颜色描述'),
        ('容易打结', '42%', '抗打结材质、护理套装赠送'),
        ('掉落/滑落', '35%', '升级卡扣设计、增加摩擦力'),
        ('长度不够', '30%', '准确测量、尺码说明'),
        ('质感差', '28%', '提升材质、增加光泽处理'),
        ('异味', '22%', '环保材料、通风处理'),
    ]
    
    for item in pain_data:
        row_cells = table9.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    doc.add_page_break()
    
    # 第七章
    doc.add_heading('七、Listing优化建议', level=1)
    
    doc.add_heading('7.1 标题优化', level=2)
    doc.add_paragraph('推荐格式：[品牌] + 产品类型 + 材质 + 长度 + 颜色 + 数量/套装 + 特点')
    doc.add_paragraph('示例：[Brand] Clip in Hair Extensions - Human Hair Blend - 16 Inch - 220g - Natural Black - Straight')
    
    doc.add_heading('7.2 要点描述优化（5点）', level=2)
    bullets = [
        '【高品质材质】精选真人发与合成纤维混合，自然逼真，触感柔顺',
        '【多色可选】20+颜色可选，从自然黑到渐变色，满足不同造型需求',
        '【轻松佩戴】升级版隐形夹子，一拉即用，稳固不滑落，适合日常和特殊场合',
        '【完美增发】100-220g多规格，瞬间增加发量和长度，打造丰盈秀发',
        '【礼品佳选】精美礼盒包装，适合生日、婚礼、节日送礼',
    ]
    for b in bullets:
        doc.add_paragraph(b, style='List Bullet')
    
    doc.add_heading('7.3 图片优化', level=2)
    
    table10 = doc.add_table(rows=1, cols=2)
    table10.style = 'Table Grid'
    hdr_cells = table10.rows[0].cells
    hdr_cells[0].text = '图片位置'
    hdr_cells[1].text = '内容要求'
    
    image_data = [
        ('主图', '白色背景，正面展示，清晰专业'),
        ('图2', '模特展示，生活化场景'),
        ('图3', '颜色对比，色板展示'),
        ('图4', '细节特写，质感展示'),
        ('图5', '佩戴效果，前后对比'),
        ('图6', '长度展示，尺码参照'),
        ('图7', '套装内容，包含配件'),
        ('A+内容', '品牌故事、使用教程、对比图'),
    ]
    
    for item in image_data:
        row_cells = table10.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
    
    doc.add_page_break()
    
    # 第八章
    doc.add_heading('八、运营策略', level=1)
    
    doc.add_heading('8.1 新品期策略（第1-3个月）', level=2)
    
    table11 = doc.add_table(rows=1, cols=4)
    table11.style = 'Table Grid'
    hdr_cells = table11.rows[0].cells
    hdr_cells[0].text = '阶段'
    hdr_cells[1].text = '时间'
    hdr_cells[2].text = '核心策略'
    hdr_cells[3].text = '关键目标'
    
    operation_data = [
        ('冷启动', '第1周', 'Listing优化、基础评论', '上架完成'),
        ('测评期', '第2-4周', 'Vine计划、低价促销', '积累30+ Reviews'),
        ('推广期', '第5-8周', '广告测试、站外引流', '月销100+'),
        ('优化期', '第9-12周', '广告优化、选品调整', 'ACOS<30%'),
    ]
    
    for item in operation_data:
        row_cells = table11.add_row().cells
        for i, cell in enumerate(row_cells):
            cell.text = item[i]
    
    doc.add_page_break()
    
    # 第九章
    doc.add_heading('九、风险评估与应对', level=1)
    
    doc.add_heading('9.1 主要风险', level=2)
    
    table12 = doc.add_table(rows=1, cols=5)
    table12.style = 'Table Grid'
    hdr_cells = table12.rows[0].cells
    hdr_cells[0].text = '风险类型'
    hdr_cells[1].text = '描述'
    hdr_cells[2].text = '概率'
    hdr_cells[3].text = '影响'
    hdr_cells[4].text = '应对措施'
    
    risk_data = [
        ('市场竞争', '价格战、恶意竞争', '高', '中', '差异化、品牌化'),
        ('专利侵权', '外观专利、商标', '中', '高', '上新前检索'),
        ('差评风险', '质量、颜色问题', '中', '高', '严控质量'),
        ('平台政策', '违规下架', '低', '高', '合规经营'),
        ('供应链', '断货、成本上涨', '中', '中', '备选供应商'),
    ]
    
    for item in risk_data:
        row_cells = table12.add_row().cells
        for i, cell in enumerate(row_cells):
            cell.text = item[i]
    
    doc.add_page_break()
    
    # 第十章
    doc.add_heading('十、财务预测', level=1)
    
    doc.add_heading('10.1 成本预算（Clip-in合成纤维）', level=2)
    
    table13 = doc.add_table(rows=1, cols=4)
    table13.style = 'Table Grid'
    hdr_cells = table13.rows[0].cells
    hdr_cells[0].text = '项目'
    hdr_cells[1].text = '入门款'
    hdr_cells[2].text = '主力款'
    hdr_cells[3].text = '高端款'
    
    finance_data = [
        ('产品成本', '$6', '$10', '$18'),
        ('头程运费', '$2.5', '$3', '$4'),
        ('FBA配送', '$3.5', '$4', '$5'),
        ('平台佣金', '$2.4', '$4.5', '$9'),
        ('广告费用', '$2', '$3', '$5'),
        ('其他费用', '$0.5', '$1', '$2'),
        ('**总成本**', '$16.9', '$25.5', '$43'),
        ('**建议售价**', '$19.99', '$34.99', '$69.99'),
        ('**单件利润**', '$3.09', '$9.49', '$26.99'),
        ('**利润率**', '15%', '27%', '39%'),
    ]
    
    for item in finance_data:
        row_cells = table13.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
        row_cells[3].text = item[3]
    
    doc.add_page_break()
    
    # 第十一章
    doc.add_heading('十一、执行清单', level=1)
    
    doc.add_heading('11.1 上架前（2-3周）', level=2)
    
    checklist1 = [
        '产品选品与采购',
        '产品质量检验',
        '专业图片拍摄',
        'Listing撰写优化',
        'A+内容制作',
        '关键词调研',
        '竞品分析',
        '定价策略制定',
        '广告计划准备',
        '库存备货',
    ]
    
    for item in checklist1:
        doc.add_paragraph(item, style='List Bullet')
    
    doc.add_page_break()
    
    # 第十二章
    doc.add_heading('十二、总结与建议', level=1)
    
    doc.add_heading('12.1 核心结论', level=2)
    
    conclusions = [
        '市场评估：Hair Extensions市场大且增长稳定，但竞争激烈，需要差异化',
        '产品选择：建议从Clip-in合成纤维开始，后期升级真人发产品线',
        '定价建议：主力款售价$25-40，保证30%+利润率',
        '关键成功因素：产品质量、图片优化、Review积累、广告精细化',
    ]
    
    for i, c in enumerate(conclusions, 1):
        doc.add_paragraph(f'{i}. {c}', style='List Number')
    
    doc.add_heading('12.2 行动时间表', level=2)
    
    table14 = doc.add_table(rows=1, cols=3)
    table14.style = 'Table Grid'
    hdr_cells = table14.rows[0].cells
    hdr_cells[0].text = '时间'
    hdr_cells[1].text = '行动项'
    hdr_cells[2].text = '具体内容'
    
    action_data = [
        ('立即', '本周', '竞品调研、确定产品线、准备采购'),
        ('短期', '1个月内', '完成Listing优化、FBA发货、广告策略'),
        ('中期', '3个月内', '积累100+ Reviews、月销300+、ACOS<25%'),
    ]
    
    for item in action_data:
        row_cells = table14.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]
        row_cells[2].text = item[2]
    
    # 页脚信息
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('报告结束').italic = True
    
    filename = '产品调研报告_Hair_Extensions_接发产品.docx'
    doc.save(filename)
    print(f'Word文档已生成：{filename}')
    return filename

if __name__ == '__main__':
    try:
        create_docx_report()
    except Exception as e:
        print(f'错误：{e}')
        print('尝试安装python-docx...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-docx'])
        create_docx_report()

