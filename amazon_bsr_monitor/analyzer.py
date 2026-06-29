"""
数据分析与对比模块
"""

import json
import os
from datetime import datetime
from .config import CURRENT_DATA_DIR, PREVIOUS_DATA_DIR, RANK_CHANGE_THRESHOLD, CATEGORIES


def load_data(data_dir):
    """加载指定目录的数据"""
    data = {}
    if not os.path.exists(data_dir):
        return data

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            category = filename.replace(".json", "")
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data[category] = json.load(f)
    return data


def save_data(data, data_dir):
    """保存数据到指定目录"""
    os.makedirs(data_dir, exist_ok=True)
    for category, products in data.items():
        filepath = os.path.join(data_dir, f"{category}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)


def compare_data(current_data, previous_data):
    """
    对比本周与上周数据
    返回变化分析结果
    """
    changes = {
        "ranking_up": [],      # 排名上升
        "ranking_down": [],    # 排名下降
        "new_entries": [],    # 新上榜
        "dropped": []          # 掉出榜单
    }

    for category in CATEGORIES:
        cat_id = category["id"]
        current_products = current_data.get(cat_id, [])
        previous_products = previous_data.get(cat_id, [])

        # 建立ASIN索引
        previous_index = {p["asin"]: p for p in previous_products}

        for product in current_products:
            asin = product["asin"]
            if asin in previous_index:
                prev_rank = previous_index[asin]["rank"]
                curr_rank = product["rank"]
                rank_change = prev_rank - curr_rank  # 正数表示上升

                if abs(rank_change) >= RANK_CHANGE_THRESHOLD:
                    change_record = {
                        "category": cat_id,
                        "asin": asin,
                        "title": product["title"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "previous_rank": prev_rank,
                        "current_rank": curr_rank,
                        "rank_change": rank_change,
                        "change_type": "up" if rank_change > 0 else "down"
                    }

                    if rank_change > 0:
                        changes["ranking_up"].append(change_record)
                    else:
                        changes["ranking_down"].append(change_record)
            else:
                # 新上榜商品
                changes["new_entries"].append({
                    "category": cat_id,
                    "asin": asin,
                    "title": product["title"],
                    "brand": product["brand"],
                    "price": product["price"],
                    "current_rank": product["rank"]
                })

        # 检测掉出榜单的商品
        current_asins = {p["asin"] for p in current_products}
        for product in previous_products:
            if product["asin"] not in current_asins:
                changes["dropped"].append({
                    "category": cat_id,
                    "asin": product["asin"],
                    "title": product["title"],
                    "brand": product["brand"],
                    "previous_rank": product["rank"]
                })

    return changes


def analyze_reason(product):
    """
    分析排名变化的可能原因
    注意：这是基于标题/价格的推测，实际情况需要更深入的数据
    """
    title_lower = product.get("title", "").lower()
    price_text = product.get("price", "")

    reasons = []

    # 检查标题中的促销关键词
    promotion_keywords = ["deal", "sale", "lightning", "prime day", "coupon", "discount", "hot", "bestseller"]

    for keyword in promotion_keywords:
        if keyword in title_lower:
            if "coupon" in keyword or "discount" in title_lower:
                reasons.append("优惠券")
            elif "deal" in keyword or "sale" in keyword:
                reasons.append("折扣活动")
            elif "lightning" in keyword:
                reasons.append("Lightning Deal")
            elif "prime" in keyword:
                reasons.append("Prime Day")
            else:
                reasons.append("促销活动")
            break

    # 检查价格中的折扣标识
    if "$" in price_text and ("," in price_text or "." in price_text):
        # 提取数字价格
        try:
            price = float(price_text.replace("$", "").replace(",", ""))
            if price < 15:
                reasons.append("低价促销")
        except:
            pass

    if not reasons:
        reasons.append("自然波动")

    return " / ".join(reasons)


def generate_analysis_report(current_data, previous_data):
    """生成完整的数据分析报告"""

    # 数据对比
    changes = compare_data(current_data, previous_data)

    # 统计稳定商品
    stable_count = {}
    for category in CATEGORIES:
        cat_id = category["id"]
        current_products = current_data.get(cat_id, [])
        previous_products = previous_data.get(cat_id, [])

        previous_index = {p["asin"]: p for p in previous_products}
        stable = 0

        for product in current_products:
            if product["asin"] in previous_index:
                prev_rank = previous_index[product["asin"]]["rank"]
                curr_rank = product["rank"]
                if abs(prev_rank - curr_rank) < RANK_CHANGE_THRESHOLD:
                    stable += 1

        stable_count[cat_id] = stable

    # 为变化商品添加原因分析
    for item in changes["ranking_up"] + changes["ranking_down"]:
        item["reason"] = analyze_reason(item)

    report = {
        "generate_time": datetime.now().isoformat(),
        "changes": changes,
        "stable_count": stable_count,
        "summary": {
            "total_up": len(changes["ranking_up"]),
            "total_down": len(changes["ranking_down"]),
            "total_new": len(changes["new_entries"]),
            "total_dropped": len(changes["dropped"])
        }
    }

    return report


if __name__ == "__main__":
    # 测试
    current = load_data(CURRENT_DATA_DIR)
    previous = load_data(PREVIOUS_DATA_DIR)
    report = generate_analysis_report(current, previous)
    print(json.dumps(report, indent=2, ensure_ascii=False))
