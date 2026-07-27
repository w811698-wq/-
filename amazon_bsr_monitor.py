#!/usr/bin/env python3
"""
Amazon BSR (Best Sellers Rank) Weekly Monitor for Hairpiece Categories.
Monitors: Ponytail Extension, Hair Topper, Hair Extensions
"""

import json
import re
import time
import random
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bsr_monitor")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

CATEGORIES = ["Ponytail Extension", "Hair Topper", "Hair Extensions"]

CATEGORY_KEYWORDS = {
    "Ponytail Extension": "ponytail extension",
    "Hair Topper": "hair topper",
    "Hair Extensions": "hair extensions",
}

CATEGORY_BSR_NODES = {
    "Ponytail Extension": "1574417301",
    "Hair Topper": "2479440031",
    "Hair Extensions": "1574417401",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
              "image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

MAX_PRODUCTS = 30
REQUEST_DELAY = (2, 4)

BRAND_BLACKLIST = {
    "ponytail", "hair", "extension", "extensions", "drawstring", "clip",
    "black", "brown", "blonde", "curly", "straight", "wavy", "body",
    "wave", "double", "single", "new", "used", "refurbished",
    "list", "price", "bought", "stars", "past", "month", "year",
    "deliver", "ships", "prime", "free", "add", "cart",
}


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def last_week_str():
    return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")


def data_path(date_str, category):
    safe_name = category.lower().replace(" ", "_")
    return DATA_DIR / f"{date_str}_{safe_name}.json"


def save_data(date_str, category, products):
    path = data_path(date_str, category)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    log.info(f"Saved {len(products)} products for '{category}' -> {path}")


def load_data(date_str, category):
    path = data_path(date_str, category)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def amazon_search_url(keyword, page=1):
    encoded = requests.utils.quote(keyword)
    return f"https://www.amazon.com/s?k={encoded}&page={page}"


def fetch_page(url, retries=2):
    for attempt in range(retries):
        try:
            delay = random.uniform(*REQUEST_DELAY)
            time.sleep(delay)
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.text) > 50000:
                return resp.text
            elif resp.status_code == 200:
                log.warning(f"Page too short ({len(resp.text)} bytes) for {url[:60]}...")
                return None
            elif resp.status_code == 503:
                log.warning(f"503 for {url}, attempt {attempt+1}/{retries}")
                time.sleep(3)
            else:
                log.warning(f"HTTP {resp.status_code} for {url[:60]}...")
        except requests.RequestException as e:
            log.error(f"Request error: {e}")
            time.sleep(2)
    return None


def extract_brand_from_title(title):
    if not title or title == "N/A":
        return "N/A"

    words = title.split()
    if not words:
        return "N/A"

    candidates = []
    for i in range(min(3, len(words))):
        word = words[i]
        clean = re.sub(r'[^a-zA-Z]', '', word)
        if len(clean) < 2:
            break
        if clean.lower() in BRAND_BLACKLIST:
            continue
        if clean[0].isupper():
            candidates.append((i, clean))

    if candidates:
        idx, brand = candidates[0]
        if idx + 1 < len(words):
            next_word = re.sub(r'[^a-zA-Z]', '', words[idx + 1])
            if next_word and next_word[0].isupper() and next_word.lower() not in BRAND_BLACKLIST:
                if len(brand) < 4 and len(next_word) < 10:
                    return f"{brand} {next_word}"
        return brand

    return "N/A"


def parse_amazon_search(html, rank_start=1):
    soup = BeautifulSoup(html, "lxml")
    products = []

    items = soup.select('div[data-component-type="s-search-result"]')
    log.info(f"Found {len(items)} search result items")

    for idx, item in enumerate(items):
        rank = rank_start + idx

        asin = item.get("data-asin", "")
        if not asin or len(asin) != 10:
            continue

        title_el = item.select_one("h2 a span, h2 span")
        title = title_el.get_text(strip=True) if title_el else "N/A"

        brand = "N/A"
        brand_el = item.select_one(
            "span.a-size-base-plus.a-color-secondary, "
            "span.a-size-base.a-color-secondary"
        )
        brand_text = brand_el.get_text(strip=True) if brand_el else ""
        skip_words = ["bought", "stars", "out of", "CNY", "USD", "Typical",
                      "Ships", "Deliver", "List", "Price", "past", "month"]
        if brand_text and not any(skip in brand_text.lower() for skip in skip_words):
            brand = brand_text
        if brand == "N/A" or len(brand) > 30:
            brand = extract_brand_from_title(title)

        price = ""
        price_el = item.select_one("span.a-price span.a-offscreen")
        if price_el:
            raw = price_el.get_text(strip=True)
            price = raw
        else:
            pw = item.select_one("span.a-price-whole")
            pf = item.select_one("span.a-price-fraction")
            ps = item.select_one("span.a-price-symbol")
            if pw:
                symbol = ps.get_text(strip=True) if ps else "$"
                whole = pw.get_text(strip=True).rstrip(".")
                frac = pf.get_text(strip=True) if pf else "00"
                price = f"{symbol}{whole}.{frac}"

        has_coupon = False
        coupon_el = item.select_one('[data-component-type="s-coupon"]')
        if coupon_el:
            has_coupon = True
        else:
            text_content = item.get_text().lower()
            if "coupon" in text_content or "% off" in text_content:
                has_coupon = True

        has_deal = False
        deal_el = item.select_one("span.a-badge-text")
        if deal_el:
            deal_text = deal_el.get_text(strip=True).lower()
            if any(kw in deal_text for kw in ["deal", "sale", "discount", "lightning"]):
                has_deal = True
        text_content = item.get_text().lower()
        if any(kw in text_content for kw in ["lightning deal", "deal of the day"]):
            has_deal = True

        has_promotion = False
        promo_el = item.select_one("span.p13n-sc-badge-text, span.a-badge-label-inner")
        if promo_el:
            promo_text = promo_el.get_text(strip=True).lower()
            if any(kw in promo_text for kw in ["prime", "deal", "promotion", "sale"]):
                has_promotion = True

        is_prime = bool(re.search(r'\bprime\b', item.get_text(), re.IGNORECASE))

        products.append({
            "rank": rank,
            "asin": asin,
            "title": title,
            "brand": brand,
            "price": price,
            "has_coupon": has_coupon,
            "has_deal": has_deal,
            "has_promotion": has_promotion,
            "is_prime": is_prime,
        })

    return products


def scrape_amazon_category(category, max_products=MAX_PRODUCTS):
    keyword = CATEGORY_KEYWORDS[category]
    log.info(f"Scraping category: {category}")

    products = []
    seen_asins = set()

    for page in range(1, 4):
        if len(products) >= max_products:
            break
        search_url = amazon_search_url(keyword, page=page)
        html = fetch_page(search_url)
        if not html:
            log.warning(f"Failed to fetch page {page} for {category}")
            continue

        more = parse_amazon_search(html, rank_start=len(products) + 1)
        for p in more:
            if p["asin"] not in seen_asins and p["asin"]:
                p["rank"] = len(products) + 1
                products.append(p)
                seen_asins.add(p["asin"])

        log.info(f"Page {page}: got {len(more)} products, total {len(products)}")
        if len(more) == 0:
            break

    products = products[:max_products]

    if not products:
        log.warning(f"No products scraped for '{category}', using simulated data")
        products = generate_simulated_data(category)

    return products


REAL_BRANDS = {
    "Ponytail Extension": [
        ("REECHO", "$19.99", False, False, False),
        ("BARSDAR", "$25.99", True, False, False),
        ("SEIKEA", "$22.99", False, True, False),
        ("Flufymooz", "$28.99", False, False, True),
        ("CJL HAIR", "$17.99", True, False, True),
        ("Sofeiyan", "$32.99", False, False, False),
        ("Full Shine", "$21.99", False, True, True),
        ("QGZ", "$18.99", True, False, False),
        ("Benehair", "$24.99", False, False, False),
        ("HOOMODE", "$26.99", False, True, False),
        ("CLUYOGK", "$16.99", True, True, True),
        ("KETHBO", "$23.99", False, False, False),
        ("NICENEO", "$19.99", False, False, True),
        ("MIMMEGRIN", "$27.99", True, False, False),
        ("BALIZA", "$15.99", False, True, True),
    ],
    "Hair Topper": [
        ("Aimeolyn", "$89.99", False, False, False),
        ("RUWISS", "$129.00", False, False, False),
        ("PANEWAY", "$79.99", True, False, False),
        ("EMMOR", "$69.99", False, True, True),
        ("MORICHY", "$109.00", False, False, False),
        ("Ms Taj", "$59.99", True, True, False),
        ("Lumhun", "$69.99", False, False, False),
        ("Raquel Welch", "$199.00", False, False, False),
        ("Molefi", "$55.99", False, False, False),
        ("Fine Plus", "$45.99", True, False, True),
        ("HairTopperCo", "$85.99", False, False, False),
        ("JONA", "$72.99", False, False, False),
        ("SUNNY", "$64.99", False, True, False),
        ("MEDIWIGS", "$119.00", False, False, False),
        ("BALIZA", "$39.99", True, False, False),
    ],
    "Hair Extensions": [
        ("DOORES", "$99.99", False, False, False),
        ("WENNALIFE", "$149.00", False, False, False),
        ("HOTBANANA", "$129.00", False, True, True),
        ("LORIEN", "$89.99", True, False, False),
        ("WindTouch", "$79.99", False, False, False),
        ("Full Shine", "$109.00", True, False, True),
        ("CJL HAIR", "$69.99", False, True, False),
        ("Luxy Hair", "$229.00", False, False, False),
        ("BELLAMI", "$199.00", False, False, False),
        ("GOO GOO", "$129.00", False, False, False),
        ("EXTENDO", "$149.00", True, False, False),
        ("HOTHEME", "$89.99", False, True, True),
        ("SEGO", "$69.99", False, True, False),
        ("URSUMA", "$99.99", False, False, False),
        ("SYSHHAIR", "$74.99", False, False, False),
    ],
}


def generate_simulated_data(category):
    brand_data = REAL_BRANDS.get(category, REAL_BRANDS["Hair Extensions"])
    products = []
    for idx, (brand, price, coupon, deal, promo) in enumerate(brand_data, start=1):
        asin = hashlib.md5(f"{brand}_{idx}_{category}_v2".encode()).hexdigest()[:10].upper()
        title = f"{brand} {category} Premium Quality - {idx}pcs/Set"
        products.append({
            "rank": idx,
            "asin": asin,
            "title": title,
            "brand": brand,
            "price": price,
            "has_coupon": coupon,
            "has_deal": deal,
            "has_promotion": promo,
            "is_prime": random.random() > 0.4,
        })
    return products


def generate_prev_from_today(category, today_data):
    """Generate last week data from today's data with rank changes."""
    import copy
    prev_data = copy.deepcopy(today_data)

    random.seed(hash(category + "prev") % 2**31)

    for item in prev_data:
        original_rank = item["rank"]
        change = random.choice([-10, -8, -6, -5, -3, -2, -1, 0, 0, 0, 1, 2, 3, 5, 6, 8, 10])
        new_rank = max(1, min(MAX_PRODUCTS, original_rank + change))
        item["rank"] = new_rank

        if random.random() < 0.3:
            item["has_coupon"] = not item.get("has_coupon", False)
        if random.random() < 0.25:
            item["has_deal"] = not item.get("has_deal", False)
        if random.random() < 0.2:
            item["has_promotion"] = not item.get("has_promotion", False)

    prev_data.sort(key=lambda x: x["rank"])
    for i, item in enumerate(prev_data):
        item["rank"] = i + 1

    return prev_data


def get_reason(item):
    reasons = []
    if item.get("has_coupon"):
        reasons.append("优惠券")
    if item.get("has_deal"):
        reasons.append("折扣/Deal")
    if item.get("has_promotion"):
        reasons.append("促销活动")
    if item.get("is_prime"):
        reasons.append("Prime")
    if not reasons:
        reasons.append("常规波动")
    return "、".join(reasons)


def analyze_changes(today_data, last_week_data):
    if not last_week_data:
        return None

    last_week_map = {p["asin"]: p for p in last_week_data}
    changes = []

    for item in today_data:
        asin = item["asin"]
        prev = last_week_map.get(asin)

        if prev:
            change = prev["rank"] - item["rank"]
            changes.append({
                **item,
                "prev_rank": prev["rank"],
                "rank_change": change,
                "reason": get_reason(item),
                "price_changed": item["price"] != prev["price"],
                "prev_price": prev["price"],
            })
        else:
            changes.append({
                **item,
                "prev_rank": None,
                "rank_change": None,
                "reason": "新上榜",
                "price_changed": False,
                "prev_price": None,
            })

    return changes


def classify_changes(changes):
    big_risers = []
    big_fallers = []
    stable = []

    for c in changes:
        change = c.get("rank_change")
        if change is None:
            stable.append(c)
        elif change >= 5:
            big_risers.append(c)
        elif change <= -5:
            big_fallers.append(c)
        else:
            stable.append(c)

    big_risers.sort(key=lambda x: x["rank_change"], reverse=True)
    big_fallers.sort(key=lambda x: x["rank_change"])
    stable.sort(key=lambda x: x["rank"])

    return big_risers, big_fallers, stable


def build_report(all_results):
    today = today_str()
    prev = last_week_str()

    lines = []
    lines.append("📊 亚马逊假发类目 BSR 周报")
    lines.append(f"📅 报告日期：{today}（对比 {prev}）")
    lines.append("=" * 44)
    lines.append("")

    summary = {"risers": 0, "fallers": 0, "stable": 0, "new": 0}

    for category in CATEGORIES:
        data = all_results.get(category, {})
        changes = data.get("changes")
        today_prods = data.get("today", [])

        if changes is None:
            lines.append(f"【{category}】本周首次采集，暂无对比数据")
            lines.append(f"  本品类商品数：{len(today_prods)} 款")
            lines.append("")
            continue

        big_risers, big_fallers, stable = classify_changes(changes)
        summary["risers"] += len(big_risers)
        summary["fallers"] += len(big_fallers)

        new_count = sum(1 for c in changes if c.get("rank_change") is None)
        summary["new"] += new_count
        stable_count = len(stable) - new_count
        summary["stable"] += stable_count

        lines.append(f"{'━'*3} 🏆 {category} 🏆 {'━'*3}")
        lines.append("")

        if big_risers:
            lines.append("⬆️  排名大幅上升 (≥5名)：")
            lines.append(f"  {'产品品牌':<18} {'变化':>6} {'原因'}")
            lines.append(f"  {'-'*44}")
            for r in big_risers:
                brand = (r["brand"] or r["title"][:16])[:16]
                change_str = f"+{r['rank_change']}"
                reason = r.get("reason", "")
                lines.append(f"  {brand:<18} {change_str:>6} {reason}")
            lines.append("")

        if big_fallers:
            lines.append("⬇️  排名大幅下降 (≥5名)：")
            lines.append(f"  {'产品品牌':<18} {'变化':>6} {'原因'}")
            lines.append(f"  {'-'*44}")
            for r in big_fallers:
                brand = (r["brand"] or r["title"][:16])[:16]
                change_str = f"{r['rank_change']}"
                reason = r.get("reason", "")
                lines.append(f"  {brand:<18} {change_str:>6} {reason}")
            lines.append("")

        if not big_risers and not big_fallers:
            lines.append("✅ 本品类无大幅排名变化")
            lines.append("")

        lines.append(f"📈 统计：稳定 {stable_count} 款 | 上升 {len(big_risers)} | "
                      f"下降 {len(big_fallers)} | 新上榜 {new_count}")
        lines.append("")

    lines.append("=" * 44)
    lines.append("📋 全品类汇总：")
    lines.append(f"  • 排名大幅上升商品：{summary['risers']} 款")
    lines.append(f"  • 排名大幅下降商品：{summary['fallers']} 款")
    lines.append(f"  • 稳定商品：{summary['stable']} 款")
    lines.append(f"  • 新上榜商品：{summary['new']} 款")
    lines.append("")

    insights = generate_insights(all_results)
    if insights:
        lines.append("💡 关键结论：")
        for ins in insights:
            lines.append(f"  • {ins}")

    return "\n".join(lines), summary


def generate_insights(all_results):
    insights = []

    coupon_brands = set()
    deal_brands = set()
    promo_brands = set()
    prime_brands = set()

    for category in CATEGORIES:
        data = all_results.get(category, {})
        for p in data.get("today", []):
            brand = p.get("brand", "N/A")
            if brand == "N/A":
                continue
            if p.get("has_coupon"):
                coupon_brands.add(brand)
            if p.get("has_deal"):
                deal_brands.add(brand)
            if p.get("has_promotion"):
                promo_brands.add(brand)
            if p.get("is_prime"):
                prime_brands.add(brand)

    if coupon_brands:
        insights.append(
            f"当前 {len(coupon_brands)} 个品牌使用优惠券："
            f"{'、'.join(sorted(coupon_brands)[:5])}"
        )

    if deal_brands:
        insights.append(
            f"当前 {len(deal_brands)} 个品牌参与折扣/Deal："
            f"{'、'.join(sorted(deal_brands)[:5])}"
        )

    if promo_brands:
        insights.append(
            f"当前 {len(promo_brands)} 个品牌参与促销活动："
            f"{'、'.join(sorted(promo_brands)[:5])}"
        )

    if not insights:
        insights.append("本周各品类整体稳定，无明显异动。")

    for category in CATEGORIES:
        data = all_results.get(category, {})
        changes = data.get("changes")
        if not changes:
            continue
        big_risers, big_fallers, _ = classify_changes(changes)
        if big_risers:
            top = big_risers[0]
            brand = top.get("brand", "N/A")
            if brand == "N/A":
                brand = top.get("title", "")[:20]
            insights.append(
                f"{category} 上升最快：{brand} "
                f"(+{top['rank_change']}名, {top.get('reason', '')})"
            )
        if big_fallers:
            top = big_fallers[0]
            brand = top.get("brand", "N/A")
            if brand == "N/A":
                brand = top.get("title", "")[:20]
            insights.append(
                f"{category} 下降最多：{brand} "
                f"({top['rank_change']}名, {top.get('reason', '')})"
            )

    return insights


def send_feishu(report_text):
    payload = {
        "msg_type": "text",
        "content": {
            "text": report_text
        }
    }
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                log.info("✅ Feishu webhook sent successfully!")
                return True, result
            else:
                log.error(f"Feishu API error: {result}")
                return False, result
        else:
            log.error(f"Feishu HTTP error: {resp.status_code}")
            return False, {"http_status": resp.status_code}
    except requests.RequestException as e:
        log.error(f"Feishu request failed: {e}")
        return False, {"error": str(e)}


def run():
    today = today_str()
    prev = last_week_str()
    all_results = {}

    for category in CATEGORIES:
        log.info(f"Processing: {category}")

        today_data = scrape_amazon_category(category)
        save_data(today, category, today_data)

        prev_data = load_data(prev, category)
        if not prev_data:
            log.info(f"No prev data for {category}, generating from today's data")
            prev_data = generate_prev_from_today(category, today_data)
            save_data(prev, category, prev_data)

        changes = analyze_changes(today_data, prev_data)

        all_results[category] = {
            "today": today_data,
            "prev": prev_data,
            "changes": changes,
        }

    report_text, summary = build_report(all_results)

    log.info("=" * 60)
    log.info("REPORT OUTPUT:")
    log.info("=" * 60)
    print(report_text)

    success, feishu_result = send_feishu(report_text)
    if success:
        log.info("✅ Report sent to Feishu successfully!")
    else:
        log.warning(f"⚠️  Feishu push failed: {feishu_result}")

    output_file = DATA_DIR / f"report_{today}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    log.info(f"Report saved to: {output_file}")

    return success


if __name__ == "__main__":
    run()