#!/usr/bin/env python3
"""
生成真实的 .pptx 演示文稿
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import sys

def create_pptx_presentation():
    prs = Presentation()
    
    # 第1页：封面
    slide_layout = prs.slide_layouts[0]  # 标题幻灯片
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = 'Hair Extensions 接发产品调研报告'
    subtitle.text = '亚马逊产品调研分析报告\n版本：v1.0\n报告日期：2026年5月16日'
    
    # 第2页：目录
    slide_layout = prs.slide_layouts[1]  # 标题和内容
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    body = slide.placeholders[1]
    
    title.text = '目录'
    
    tf = body.text_frame
    tf.text = '1. 产品概述\n2. 市场规模与趋势\n3. 竞争分析\n4. 关键词分析\n5. 定价策略\n6. 产品优化建议\n7. Listing优化建议\n8. 运营策略\n9. 风险评估与应对\n10. 财务预测\n11. 执行清单\n12. 总结与建议'
    
    # 第3页：产品概述
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '一、产品概述'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '1.1 产品分类'
    
    p = tf.add_paragraph()
    p.text = '• Clip-in Extensions：夹子式接发，最受欢迎（$15-50）'
    
    p = tf.add_paragraph()
    p.text = '• Tape-in Extensions：胶带式接发（$30-100）'
    
    p = tf.add_paragraph()
    p.text = '• Fusion/Keratin：热熔接发（$100-300）'
    
    p = tf.add_paragraph()
    p.text = '• Clip-in Ponytail：马尾式接发（$15-40）'
    
    p = tf.add_paragraph()
    p.text = '1.2 材质分类'
    
    p = tf.add_paragraph()
    p.text = '• Synthetic（合成纤维）：$10-30'
    
    p = tf.add_paragraph()
    p.text = '• Human Hair（真人发）：$50-300'
    
    p = tf.add_paragraph()
    p.text = '• Remy Hair（定向发）：$80-400'
    
    # 第4页：市场规模
    slide_layout = prs.slide_layouts[5]  # 空白幻灯片
    slide = prs.slides.add_slide(slide_layout)
    
    title_box = slide.shapes.title
    title_box.text = '二、市场规模与趋势'
    
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(4)
    
    table = slide.shapes.add_table(5, 2, left, top, width, height).table
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(6)
    
    data = [
        ('指标', '数据'),
        ('月搜索量', '450,000+'),
        ('平均价格', '$25-35'),
        ('平均评分', '4.2-4.5'),
        ('市场竞争度', '高'),
    ]
    
    for i, (key, value) in enumerate(data):
        row_cells = table.rows[i].cells
        row_cells[0].text = key
        row_cells[1].text = value
    
    # 第5页：竞争分析
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '三、竞争分析'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '3.1 价格区间竞争格局'
    
    p = tf.add_paragraph()
    p.text = '• $10-20：合成纤维，激烈竞争，15-20%利润率'
    
    p = tf.add_paragraph()
    p.text = '• $20-40：中档混合，中等竞争，25-35%利润率 → 推荐！'
    
    p = tf.add_paragraph()
    p.text = '• $40-80：真人发，较低竞争，40-50%利润率'
    
    p = tf.add_paragraph()
    p.text = '• $80+：高端真人发，低竞争，50-60%利润率'
    
    p = tf.add_paragraph()
    p.text = '3.2 头部竞品特征'
    
    p = tf.add_paragraph()
    p.text = '• 100+ Reviews（85%），4.0+评分（90%）'
    
    p = tf.add_paragraph()
    p.text = '• 多色可选（95%），8+张图片（88%）'
    
    # 第6页：关键词分析
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    
    title_box = slide.shapes.title
    title_box.text = '四、关键词分析'
    
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(4)
    
    table = slide.shapes.add_table(7, 5, left, top, width, height).table
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(1.5)
    table.columns[2].width = Inches(1)
    table.columns[3].width = Inches(1)
    table.columns[4].width = Inches(1.5)
    
    data = [
        ('关键词', '搜索量', '竞争', 'CPC', '推荐度'),
        ('hair extensions', '450K', '高', '$1.80', '⭐⭐⭐'),
        ('clip in hair', '180K', '高', '$1.60', '⭐⭐⭐'),
        ('human hair', '135K', '高', '$2.20', '⭐⭐'),
        ('tape in hair', '90K', '中高', '$2.00', '⭐⭐'),
        ('for women', '65K', '中', '$1.40', '⭐⭐⭐'),
        ('ponytail', '40K', '中', '$1.20', '⭐⭐⭐'),
    ]
    
    for i, row_data in enumerate(data):
        row_cells = table.rows[i].cells
        for j, cell_text in enumerate(row_data):
            row_cells[j].text = cell_text
    
    # 第7页：定价策略
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '五、定价策略'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '5.1 建议定价'
    
    p = tf.add_paragraph()
    p.text = '• 引流款：$12-18（15-20%利润率）'
    
    p = tf.add_paragraph()
    p.text = '• 主力款：$22-35（25-35%利润率）→ 推荐！'
    
    p = tf.add_paragraph()
    p.text = '• 形象款：$45-80（40-50%利润率）'
    
    p = tf.add_paragraph()
    p.text = '5.2 成本预算（Clip-in合成纤维）'
    
    p = tf.add_paragraph()
    p.text = '• 入门款：$19.99，利润$3.09'
    
    p = tf.add_paragraph()
    p.text = '• 主力款：$34.99，利润$9.49'
    
    p = tf.add_paragraph()
    p.text = '• 高端款：$69.99，利润$26.99'
    
    # 第8页：产品优化
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '六、产品优化建议'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '6.1 差评痛点解决方案'
    
    p = tf.add_paragraph()
    p.text = '• 颜色不符（48%）：实物对比图'
    
    p = tf.add_paragraph()
    p.text = '• 容易打结（42%）：抗打结材质+护理套装'
    
    p = tf.add_paragraph()
    p.text = '• 掉落/滑落（35%）：升级卡扣设计'
    
    p = tf.add_paragraph()
    p.text = '6.2 产品创新方向'
    
    p = tf.add_paragraph()
    p.text = '• 功能：自带护理套装'
    
    p = tf.add_paragraph()
    p.text = '• 包装：精美礼盒+便携收纳'
    
    # 第9页：Listing优化
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '七、Listing优化建议'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '7.1 标题优化'
    
    p = tf.add_paragraph()
    p.text = '[品牌] + 产品类型 + 材质 + 长度 + 颜色'
    
    p = tf.add_paragraph()
    p.text = '7.2 要点描述（5点）'
    
    p = tf.add_paragraph()
    p.text = '• 高品质材质、多色可选、轻松佩戴'
    
    p = tf.add_paragraph()
    p.text = '• 完美增发、礼品佳选'
    
    # 第10页：运营策略
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '八、运营策略'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '8.1 新品期（第1-3个月）'
    
    p = tf.add_paragraph()
    p.text = '• 第1周：Listing优化'
    
    p = tf.add_paragraph()
    p.text = '• 第2-4周：Vine计划、低价促销 → 30+ Reviews'
    
    p = tf.add_paragraph()
    p.text = '• 第5-8周：广告测试、站外引流 → 100+销量'
    
    p = tf.add_paragraph()
    p.text = '8.2 成长期（第4-6个月）'
    
    p = tf.add_paragraph()
    p.text = '• 精准广告、Review管理、库存优化'
    
    # 第11页：风险评估
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    
    title_box = slide.shapes.title
    title_box.text = '九、风险评估与应对'
    
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(4)
    
    table = slide.shapes.add_table(6, 5, left, top, width, height).table
    table.columns[0].width = Inches(1.5)
    table.columns[1].width = Inches(2)
    table.columns[2].width = Inches(1)
    table.columns[3].width = Inches(1)
    table.columns[4].width = Inches(3.5)
    
    data = [
        ('风险', '描述', '概率', '影响', '应对'),
        ('市场竞争', '价格战', '高', '中', '差异化'),
        ('专利侵权', '外观专利', '中', '高', '上新前检索'),
        ('差评风险', '质量问题', '中', '高', '严控质量'),
        ('平台政策', '违规下架', '低', '高', '合规经营'),
        ('供应链', '断货上涨', '中', '中', '备选供应商'),
    ]
    
    for i, row_data in enumerate(data):
        row_cells = table.rows[i].cells
        for j, cell_text in enumerate(row_data):
            row_cells[j].text = cell_text
    
    # 第12页：财务预测
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    
    title_box = slide.shapes.title
    title_box.text = '十、财务预测'
    
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(3)
    
    table = slide.shapes.add_table(5, 2, left, top, width, height).table
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(6)
    
    data = [
        ('假设条件', '月销300单，售价$34.99'),
        ('月销售额', '$10,497.00'),
        ('月成本', '$7,650.00'),
        ('月毛利', '$2,847.00'),
        ('年利润预估', '$34,164.00'),
    ]
    
    for i, (key, value) in enumerate(data):
        row_cells = table.rows[i].cells
        row_cells[0].text = key
        row_cells[1].text = value
    
    # 第13页：执行清单
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '十一、执行清单'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '上架前（2-3周）'
    
    p = tf.add_paragraph()
    p.text = '• 产品采购、质检、图片拍摄'
    
    p = tf.add_paragraph()
    p.text = '• Listing优化、关键词调研'
    
    p = tf.add_paragraph()
    p.text = '发货准备（1-2周）'
    
    p = tf.add_paragraph()
    p.text = '• FBA创建、贴标发货'
    
    p = tf.add_paragraph()
    p.text = '上架后（持续）'
    
    p = tf.add_paragraph()
    p.text = '• 数据监控、广告优化、Review管理'
    
    # 第14页：总结
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = '十二、总结与建议'
    
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.text = '12.1 核心结论'
    
    p = tf.add_paragraph()
    p.text = '• 市场：容量大但竞争激烈，需差异化'
    
    p = tf.add_paragraph()
    p.text = '• 产品：Clip-in合成纤维开始'
    
    p = tf.add_paragraph()
    p.text = '• 定价：$25-40，30%+利润率'
    
    p = tf.add_paragraph()
    p.text = '12.2 行动时间表'
    
    p = tf.add_paragraph()
    p.text = '• 立即：竞品调研、确定产品线'
    
    p = tf.add_paragraph()
    p.text = '• 1个月内：完成Listing、FBA发货'
    
    p = tf.add_paragraph()
    p.text = '• 3个月内：100+ Reviews、300+销量'
    
    # 第15页：结束页
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = '感谢观看！'
    subtitle.text = '有问题请联系我们\n报告生成：亚马逊调研RPA系统'
    
    filename = '产品调研报告_Hair_Extensions_接发产品.pptx'
    prs.save(filename)
    print(f'PowerPoint文档已生成：{filename}')
    return filename

if __name__ == '__main__':
    try:
        create_pptx_presentation()
    except Exception as e:
        print(f'错误：{e}')
        print('尝试安装python-pptx...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-pptx'])
        create_pptx_presentation()

