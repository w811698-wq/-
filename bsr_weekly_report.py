#!/usr/bin/env python3
"""
亚马逊假发类目BSR排名周报
监控类目：Ponytail Extension, Hair Topper, Hair Extensions
功能：数据抓取、周对比、增幅监测、原因分析、飞书推送

使用说明：
1. 先运行 fetch_data.py 获取最新HTML数据（或手动将BSR页面保存到 data/html/ 目录）
2. 运行本脚本生成周报并发送到飞书

数据来源：Amazon Best Sellers 页面（WebFetch获取的markdown格式）
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ============ 配置 ============
CATEGORIES = {
    "Hair Extensions": {
        "node_id": "702379011",
        "url": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hair-Extensions/zgbs/beauty/702379011",
        "html_file": "hair_extensions.txt",
    },
    "Ponytail Extension": {
        # 从 Hairpieces 父类目中筛选 Ponytail 相关产品
        "node_id": "702380011",
        "url": "https://www.amazon.com/Best-Sellers-Hairpieces/zgbs/beauty/702380011",
        "html_file": "hairpieces.txt",
        "filter_keywords": ["ponytail", "drawstring", "afro puff", "wrap around ponytail", "claw ponytail"],
    },
    "Hair Topper": {
        # 从 Hairpieces 父类目中筛选 Hair Topper 相关产品
        "node_id": "702380011",
        "url": "https://www.amazon.com/Best-Sellers-Hairpieces/zgbs/beauty/702380011",
        "html_file": "hairpieces.txt",
        "filter_keywords": ["topper", "bangs", "hair piece for thin", "crown hair", "u-shaped", "u part"],
    },
}

DATA_DIR = Path(__file__).parent / "data"
HTML_DIR = DATA_DIR / "html"
DATA_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

RANK_CHANGE_THRESHOLD = 5


# ============ 数据解析 ============
def parse_bsr_markdown(markdown_text, category_name):
    """
    从WebFetch返回的markdown格式中提取产品数据
    每个产品的结构（可能跨多行）：
      N. #N
      [![图片alt](url)](/slug/dp/ASIN/...)
      [标题](/slug/dp/ASIN/...)
      [_评分 stars_评论数](review_link)
      [CNY 价格](link)
    """
    products = []

    # 预处理：合并被换行符分割的内容
    # 策略：将连续非空行合并为一行，保留空行作为块分隔符
    lines = markdown_text.split('\n')
    merged_blocks = []
    current_block = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_block:
                merged_blocks.append(' '.join(current_block))
                current_block = []
            merged_blocks.append('')
        else:
            current_block.append(stripped)

    if current_block:
        merged_blocks.append(' '.join(current_block))

    i = 0
    while i < len(merged_blocks):
        line = merged_blocks[i].strip()

        # 匹配排名行
        rank_match = re.match(r'^(\d+)\.\s*#(\d+)$', line)
        if rank_match:
            rank_num = int(rank_match.group(2))
            product = {"rank": rank_num, "category": category_name}

            # 向后查找各字段
            for j in range(i + 1, min(i + 10, len(merged_blocks))):
                next_line = merged_blocks[j].strip()
                if not next_line:
                    continue

                # ASIN - 从链接中提取
                if "asin" not in product:
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', next_line)
                    if asin_match:
                        product["asin"] = asin_match.group(1)

                # 标题 - 非图片的markdown链接
                if "title" not in product and next_line.startswith('[') and 'images-na.ssl' not in next_line and 'images-amazon' not in next_line and not next_line.startswith('[!['):
                    title_match = re.match(r'^\[(.+?)\]\(', next_line)
                    if title_match:
                        title = title_match.group(1).strip()
                        if title.startswith('!['):
                            continue
                        if len(title) > 10:
                            product["title"] = title
                            words = title.split()
                            product["brand"] = words[0] if words else "Unknown"

                # 评分和评论数
                if "rating" not in product:
                    rating_match = re.search(r'_?([\d.]+)\s+out\s+of\s+5\s+stars_?\s*([\d,]+)', next_line)
                    if rating_match:
                        product["rating"] = float(rating_match.group(1))
                        product["reviews"] = int(rating_match.group(2).replace(",", ""))

                # 价格 - 支持CNY和USD
                if "price" not in product:
                    price_match = re.search(r'CNY\s*([\d,]+\.\d{2})', next_line)
                    if price_match:
                        product["price"] = float(price_match.group(1).replace(",", ""))
                    else:
                        price_match = re.search(r'\$\s*([\d,]+\.\d{2})', next_line)
                        if price_match:
                            product["price"] = float(price_match.group(1).replace(",", ""))

            product.setdefault("asin", "")
            product.setdefault("title", "")
            product.setdefault("brand", "Unknown")
            product.setdefault("price", 0.0)
            product.setdefault("rating", 0.0)
            product.setdefault("reviews", 0)

            if product["asin"]:
                products.append(product)

        i += 1

    return products


def load_html_from_file(html_filename):
    """从本地文件加载HTML/markdown内容"""
    filepath = HTML_DIR / html_filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ============ 数据存储与对比 ============
def save_weekly_data(category_name, products):
    """保存本周数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = DATA_DIR / f"{category_name.replace(' ', '_')}_{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"  数据已保存: {filename}")
    return filename


def load_latest_previous_data(category_name):
    """加载上周/历史数据"""
    prefix = category_name.replace(" ", "_")
    json_files = sorted(DATA_DIR.glob(f"{prefix}_*.json"))
    if len(json_files) < 2:
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    previous_files = [f for f in json_files if today not in f.name]
    if not previous_files:
        return None

    latest = previous_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_with_previous(current_products, previous_products):
    """对比本周与上周数据"""
    if not previous_products:
        return current_products

    prev_rank_map = {p["asin"]: p["rank"] for p in previous_products}
    prev_price_map = {p["asin"]: p.get("price", 0) for p in previous_products}

    for p in current_products:
        asin = p["asin"]
        p["prev_rank"] = prev_rank_map.get(asin)
        p["rank_change"] = (prev_rank_map[asin] - p["rank"]) if asin in prev_rank_map else None
        p["prev_price"] = prev_price_map.get(asin) if asin in prev_price_map else None
        p["price_change"] = round(p.get("price", 0) - prev_price_map.get(asin, 0), 2) if asin in prev_price_map else None

    return current_products


# ============ 增幅监测与原因分析 ============
def analyze_changes(products):
    """分析排名大幅变化的商品"""
    risers, fallers, new_entries = [], [], []

    for p in products:
        change = p.get("rank_change")
        if change is None:
            new_entries.append(p)
        elif change >= RANK_CHANGE_THRESHOLD:
            risers.append(p)
        elif change <= -RANK_CHANGE_THRESHOLD:
            fallers.append(p)

    return risers, fallers, new_entries


def analyze_reasons(products):
    """基于价格变化等信息分析排名变化原因"""
    for p in products:
        reasons = []

        price_change = p.get("price_change")

        if price_change is not None and price_change < 0:
            prev = p.get("prev_price", 0)
            if prev > 0:
                pct = abs(price_change) / prev * 100
                if pct >= 20:
                    reasons.append(f"大幅折扣(-{pct:.0f}%)")
                elif pct >= 10:
                    reasons.append(f"促销降价(-{pct:.0f}%)")
                else:
                    reasons.append(f"小幅降价(-{abs(price_change):.2f})")
        elif price_change is not None and price_change > 0:
            prev = p.get("prev_price", 0)
            if prev > 0:
                pct = price_change / prev * 100
                if pct >= 10:
                    reasons.append(f"涨价(+{pct:.0f}%)")

        change = p.get("rank_change")
        if change is not None and change <= -RANK_CHANGE_THRESHOLD and not any('价' in r for r in reasons):
            reasons.append("竞品上升/流量下降")
        elif change is not None and change >= RANK_CHANGE_THRESHOLD and not reasons:
            reasons.append("自然增长/竞品下降")
        elif change is None:
            reasons.append("新上榜")

        p["reason_analysis"] = reasons

    return products


# ============ 飞书推送 ============
def build_feishu_message(categories_data, report_date):
    """构建飞书消息卡片"""

    all_risers, all_fallers, all_new = [], [], []
    stable_counts, total_counts = {}, {}

    for cat_name, data in categories_data.items():
        all_risers.extend([(cat_name, p) for p in data["risers"]])
        all_fallers.extend([(cat_name, p) for p in data["fallers"]])
        all_new.extend([(cat_name, p) for p in data["new_entries"]])
        total = len(data["products"])
        changed = len(data["risers"]) + len(data["fallers"]) + len(data["new_entries"])
        stable_counts[cat_name] = max(0, total - changed)
        total_counts[cat_name] = total

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 亚马逊假发类目 BSR 排名周报**\n📅 报告日期: **{report_date}**\n🔍 监控范围: Top30 × 3个类目"
            }
        },
        {"tag": "hr"}
    ]

    # 排名上升表格
    if all_risers:
        rows = []
        for cat, p in sorted(all_risers, key=lambda x: -x[1]["rank_change"])[:10]:
            reason = " | ".join(p.get("reason_analysis", ["未知"]))
            rows.append(f"| {p.get('brand', 'N/A')[:12]} | #{p['rank']} | **↑{p['rank_change']}** | {reason} |")
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**🟢 排名上升 ≥{0} 名 ({1} 个)**\n| 品牌 | 当前排名 | 变化 | 可能原因 |\n|------|----------|------|----------|\n".format(RANK_CHANGE_THRESHOLD, len(all_risers)) + "\n".join(rows)
            }
        })
    else:
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**🟢 排名上升 ≥{RANK_CHANGE_THRESHOLD} 名**\n本周无显著上升"}})

    elements.append({"tag": "hr"})

    # 排名下降表格
    if all_fallers:
        rows = []
        for cat, p in sorted(all_fallers, key=lambda x: x[1]["rank_change"])[:10]:
            change = abs(p["rank_change"])
            reason = " | ".join(p.get("reason_analysis", ["未知"]))
            rows.append(f"| {p.get('brand', 'N/A')[:12]} | #{p['rank']} | **↓{change}** | {reason} |")
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**🔴 排名下降 ≥{0} 名 ({1} 个)**\n| 品牌 | 当前排名 | 变化 | 可能原因 |\n|------|----------|------|----------|\n".format(RANK_CHANGE_THRESHOLD, len(all_fallers)) + "\n".join(rows)
            }
        })
    else:
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**🔴 排名下降 ≥{RANK_CHANGE_THRESHOLD} 名**\n本周无显著下降"}})

    elements.append({"tag": "hr"})

    # 新上榜
    if all_new:
        rows = []
        for cat, p in all_new[:8]:
            rows.append(f"| {p.get('brand', 'N/A')[:14]} | {cat[:16]} | #{p['rank']} | ${p.get('price', 0):.0f} | ⭐{p.get('rating', 0)} |")
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🆕 新上榜商品 ({len(all_new)} 个)**\n| 品牌 | 类目 | 排名 | 价格 | 评分 |\n|------|------|------|------|------|\n" + "\n".join(rows)
            }
        })

    elements.append({"tag": "hr"})

    # 稳定性统计
    stability_lines = []
    for cat in ["Hair Extensions", "Ponytail Extension", "Hair Topper"]:
        t = total_counts.get(cat, 0)
        s = stable_counts.get(cat, 0)
        pct = (s / t * 100) if t > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        stability_lines.append(f"| **{cat[:18]}** | {s}/{t} | {bar} {pct:.0f}% |")

    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "**📋 各品类稳定性概览**\n| 类目 | 稳定商品数 | 占比图 |\n|------|------------|--------|\n" + "\n".join(stability_lines)
        }
    })

    elements.append({"tag": "hr"})

    # 关键结论
    conclusions = []

    total_up, total_down, total_new = len(all_risers), len(all_fallers), len(all_new)

    if total_up > total_down:
        conclusions.append(f"整体趋势偏**正向**: 上升{total_up}个 vs 下降{total_down}个")
    elif total_down > total_up:
        conclusions.append(f"整体趋势偏**负向**: 下降{total_down}个 vs 上升{total_up}个，需关注竞品动作")
    else:
        conclusions.append("市场格局相对**稳定**，无明显趋势性波动")

    # 价格因素
    price_moved = sum(1 for _, p in all_risers + all_fallers if p.get("price_change") and p["price_change"] != 0)
    if price_moved > 0:
        conclusions.append(f"{price_moved}个异动商品伴随价格变动，**定价策略**仍是影响排名的关键因素")

    now = datetime.now()
    if now.month == 7 and now.day >= 8 and now.day <= 16:
        conclusions.append("⚠️ **Prime Day期间**，排名波动可能受大型促销活动影响")
    elif now.month == 11 and now.day >= 20:
        conclusions.append("⚠️ **黑五/网一**期间，排名波动较大属正常现象")

    if total_new > 3:
        conclusions.append(f"有{total_new}个新商品进入榜单，市场竞争持续加剧")
    elif total_new == 0:
        conclusions.append("榜单头部格局稳定，无新进入者")

    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "**💡 关键结论 & 建议**\n" + "\n".join(f"- {c}" for c in conclusions)
        }
    })

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📊 亚马逊假发 BSR 周报"},
                "template": "blue"
            },
            "elements": elements
        }
    }


def send_to_feishu(message):
    """发送消息到飞书 Webhook"""
    try:
        resp = requests.post(
            FEISHU_WEBHOOK,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        result = resp.json()
        if result.get("code") == 0 or result.get("StatusCode") == 0:
            print("✅ 飞书推送成功!")
            return True
        else:
            print(f"❌ 飞书推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 飞书推送异常: {e}")
        return False


# ============ 主流程 ============
def run_report():
    """执行完整的周报流程"""
    report_date = datetime.now().strftime("%Y-%m-%d %A")
    print("=" * 60)
    print(f"  亚马逊假发类目 BSR 排名周报")
    print(f"  执行时间: {report_date}")
    print("=" * 60)

    categories_data = {}

    for cat_name, config in CATEGORIES.items():
        print(f"\n{'─' * 40}")
        print(f"▶ 处理类目: {cat_name}")
        print(f"  配置文件: {config['html_file']}")

        # 加载本地HTML数据
        content = load_html_from_file(config["html_file"])

        if not content:
            print(f"  ⚠️ 未找到数据文件: {config['html_file']}")
            print(f"     请先运行 fetch_data.py 获取数据")
            continue

        # 解析产品数据
        all_products = parse_bsr_markdown(content, cat_name)
        print(f"  📄 页面解析到 {len(all_products)} 个商品")

        # 按关键词筛选（如果有配置）
        filter_keywords = config.get("filter_keywords")
        if filter_keywords:
            products = []
            for p in all_products:
                title_lower = p.get("title", "").lower()
                if any(kw in title_lower for kw in filter_keywords):
                    products.append(p)
            # 重新编号排名
            for idx, p in enumerate(products):
                p["rank"] = idx + 1
            print(f"  🔍 关键词筛选后: {len(products)} 个 (关键词: {filter_keywords})")
        else:
            products = all_products

        if not products:
            print(f"  ⚠️ 筛选后无商品，使用全部数据")
            products = all_products

        if not products:
            print(f"  ❌ 无商品数据，跳过此类目")
            continue

        # 保存本周数据
        save_weekly_data(cat_name, products)

        # 与上周数据对比
        previous = load_latest_previous_data(cat_name)
        if previous:
            print(f"  📂 找到上周数据: {len(previous)} 个商品")
            compare_with_previous(products, previous)
        else:
            print(f"  ℹ️ 无上周历史数据(首次运行)")
            for p in products:
                p.update(prev_rank=None, rank_change=None, prev_price=None, price_change=None)

        # 增幅监测
        risers, fallers, new_entries = analyze_changes(products)
        print(f"  📈 上升≥{RANK_CHANGE_THRESHOLD}: {len(risers)}")
        print(f"  📉 下降≤-{RANK_CHANGE_THRESHOLD}: {len(fallers)}")
        print(f"  🆕 新上榜: {len(new_entries)}")

        # 原因分析
        analyze_reasons(risers + fallers + new_entries)

        categories_data[cat_name] = {
            "products": products,
            "risers": risers,
            "fallers": fallers,
            "new_entries": new_entries,
        }

    if not categories_data:
        print("\n" + "=" * 60)
        print("❌ 所有类目均无数据，无法生成报告")
        print("提示: 请先运行 python3 fetch_data.py 获取最新数据")
        print("=" * 60)
        return False

    # 构建并保存报告
    message = build_feishu_message(categories_data, report_date)
    report_path = DATA_DIR / f"report_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存: {report_path}")

    # 发送到飞书
    print("\n📤 正在发送到飞书...")
    success = send_to_feishu(message)

    print("\n" + "=" * 60)
    if success:
        print("  ✅ 周报完成并成功推送!")
    else:
        print("  ⚠️ 周报已生成但推送可能失败")
    print("=" * 60)

    return success


if __name__ == "__main__":
    run_report()
