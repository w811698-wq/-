import os
import pandas as pd
from datetime import datetime
import config


class ExcelExporter:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def export_all(self, data):
        filename = f"amazon_research_{self.timestamp}.xlsx"
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            self._export_products(data.get('products', []), writer)
            self._export_strategy(data.get('strategy', []), writer)
            self._export_reviews_analysis(data.get('reviews_analysis', {}), writer)
            self._export_keywords(data.get('keywords', []), writer)
            self._export_matrix(data.get('matrix', []), writer)
            self._export_selling_points(data.get('selling_points', {}), writer)
        
        return filepath

    def _export_products(self, products, writer):
        if not products:
            return
        df = pd.DataFrame(products)
        df.to_excel(writer, sheet_name='产品池', index=False)

    def _export_strategy(self, strategy, writer):
        if not strategy:
            return
        df = pd.DataFrame(strategy)
        df.to_excel(writer, sheet_name='打法分析', index=False)

    def _export_reviews_analysis(self, reviews_analysis, writer):
        if not reviews_analysis:
            return
        
        pain_df = pd.DataFrame(reviews_analysis.get('pain_points', []), columns=['痛点关键词', '频次'])
        praise_df = pd.DataFrame(reviews_analysis.get('praise_points', []), columns=['好评关键词', '频次'])
        
        pain_df.to_excel(writer, sheet_name='差评分析', index=False)
        praise_df.to_excel(writer, sheet_name='好评分析', index=False, startrow=0)

    def _export_keywords(self, keywords, writer):
        if not keywords:
            return
        df = pd.DataFrame(keywords)
        df.to_excel(writer, sheet_name='关键词库', index=False)

    def _export_matrix(self, matrix, writer):
        if not matrix:
            return
        df = pd.DataFrame(matrix)
        df.to_excel(writer, sheet_name='矩阵分析', index=False)

    def _export_selling_points(self, selling_points, writer):
        if not selling_points:
            return
        
        data = []
        for point_type, points in selling_points.items():
            for point in points:
                data.append({'类型': point_type, '卖点': point})
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='卖点策略', index=False)

    def export_products_only(self, products):
        filename = f"product_pool_{self.timestamp}.xlsx"
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        df = pd.DataFrame(products)
        df.to_excel(filepath, index=False)
        return filepath
