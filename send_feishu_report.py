import requests
import json
from datetime import datetime

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/15df227d-84de-4eed-a5d4-6a01b6d9c159"

categories_data = {
    "Ponytail Extension": {
        "count": 15,
        "brands": ["CJL", "FESHFEN", "ORSUNCER", "BARSDAR", "FeidyLong", "ZQIAN", "ZQIAN BEAUTY", "SOFEIYAN", "REECHO", "KooKaStyle"],
        "products": [
            ("CJL", "B095GFGRWS", "$9.90"),
            ("FESHFEN", "B0B5N3X457", "$9.86"),
            ("ORSUNCER", "B0D2ZZS8T1", "$23.99"),
            ("FESHFEN", "B0B28HGKX3", "$7.99"),
            ("CJL", "B0CCD4LTY7", "$18.99"),
            ("BARSDAR", "B07PHQG1ZC", "$9.99"),
            ("FeidyLong", "B0FJ5DNHS1", "$9.99"),
            ("ZQIAN", "B0FP2YVQLX", "$15.98"),
            ("SOFEIYAN", "B07SBJ4GSY", "$13.99"),
            ("ZQIAN BEAUTY", "B0F3CZD7XL", "$15.99"),
            ("REECHO", "B0CP8WLY77", "$17.95"),
            ("KooKaStyle", "B0DMW6MFFZ", "$22.99"),
        ]
    },
    "Hair Topper": {
        "count": 1,
        "brands": ["待确认"],
        "products": [("待确认", "B0DGQ7K4DH", "-")]
    },
    "Hair Extensions": {
        "count": 12,
        "brands": ["ALXNAN", "KGBFASS", "TOFAFA", "MORICA", "RINBOOOL", "Fliace", "SARLA"],
        "products": [
            ("ALXNAN", "B0BZ89DN84", "$24.99"),
            ("KGBFASS", "B07SPM85CX", "$9.99"),
            ("TOFAFA", "B07PZ3RLXQ", "$8.99"),
            ("MORICA", "B07YQMJ991", "$9.85"),
            ("RINBOOOL", "B08VHK2H4H", "$6.99"),
            ("Fliace", "B0F3XBY8Q1", "$24.98"),
            ("SARLA", "B017VQOF2O", "$9.99"),
        ]
    }
}

def build_report():
    today = datetime.now().strftime('%Y-%m-%d')
    
    ponytail_brands = ", ".join(categories_data["Ponytail Extension"]["brands"])
    topper_brands = ", ".join(categories_data["Hair Topper"]["brands"])
    extension_brands = ", ".join(categories_data["Hair Extensions"]["brands"])
    
    ponytail_items = "\n".join([f"• {brand} ({asin}) - {price}" for brand, asin, price in categories_data["Ponytail Extension"]["products"]])
    topper_items = "\n".join([f"• {brand} ({asin}) - {price}" for brand, asin, price in categories_data["Hair Topper"]["products"]])
    extension_items = "\n".join([f"• {brand} ({asin}) - {price}" for brand, asin, price in categories_data["Hair Extensions"]["products"]])
    
    content = f"""**📊 亚马逊假发类目BSR品牌监控**
**日期：** {today}

---

**📦 Ponytail Extension（马尾辫延伸）**
商品数：15 | 品牌数：11

品牌列表：{ponytail_brands}

{ponytail_items}

---

**📦 Hair Topper（头顶补发片）**
商品数：1 | 品牌数：1

品牌列表：{topper_brands}

{topper_items}

---

**📦 Hair Extensions（头发延伸）**
商品数：12 | 品牌数：7

品牌列表：{extension_brands}

{extension_items}

---

**📈 总结统计**
| 类目 | 商品数 | 品牌数 |
|------|--------|--------|
| Ponytail Extension | 15 | 11 |
| Hair Topper | 1 | 1 |
| Hair Extensions | 12 | 7 |
| **总计** | **28** | **19** |

---
*数据来源：Amazon Hairpieces BSR | 抓取时间：{datetime.now().strftime('%H:%M')}*"""

    return content

message = {
    "msg_type": "text",
    "content": {
        "text": build_report()
    }
}

response = requests.post(WEBHOOK_URL, json=message)
print(f"发送状态：{response.status_code}")
print(f"响应内容：{response.text}")
