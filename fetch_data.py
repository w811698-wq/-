#!/usr/bin/env python3
"""
数据抓取脚本：使用WebFetch获取亚马逊BSR页面
由于亚马逊对直接HTTP请求有反爬措施，此脚本需要通过外部工具获取页面内容

使用方法：
1. 手动方式：将BSR页面的HTML/markdown内容保存到 data/html/ 目录
2. 自动方式：使用本脚本通过 curl + 特殊headers 获取

每个类目抓取Top30商品（Amazon每页展示30个）
"""

import os
import subprocess
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HTML_DIR = DATA_DIR / "html"
HTML_DIR.mkdir(parents=True, exist_ok=True)

# 类目配置
CATEGORIES = {
    "hair_extensions": {
        "name": "Hair Extensions",
        "url": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hair-Extensions/zgbs/beauty/702379011",
        "output": "hair_extensions.txt",
    },
    "hairpieces": {
        "name": "Hairpieces (Ponytail Extensions & Hair Toppers)",
        "url": "https://www.amazon.com/Best-Sellers-Hairpieces/zgbs/beauty/702380011",
        "output": "hairpieces.txt",
    },
}


def fetch_with_curl(url, output_file):
    """使用curl获取页面（带完整浏览器headers）"""
    headers = [
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Accept-Encoding: identity",
        "-H", "Cache-Control: no-cache",
        "-H", "Pragma: no-cache",
        "-H", "Sec-Ch-Ua: \"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "-H", "Sec-Ch-Ua-Mobile: ?0",
        "-H", "Sec-Ch-Ua-Platform: \"macOS\"",
        "-H", "Sec-Fetch-Dest: document",
        "-H", "Sec-Fetch-Mode: navigate",
        "-H", "Sec-Fetch-Site: none",
        "-H", "Sec-Fetch-User: ?1",
        "-H", "Upgrade-Insecure-Requests: 1",
    ]

    cmd = ["curl", "-s", "-L", "--max-time", "30"] + headers + [url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        content = result.stdout

        if len(content) < 1000 or "captcha" in content.lower() or "robot" in content.lower():
            print(f"  ⚠️ 被反爬拦截(CAPTCHA)，需要手动获取")
            return False

        output_path = HTML_DIR / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ 已保存: {output_path} ({len(content)} bytes)")
        return True

    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        return False


def fetch_all():
    """抓取所有类目数据"""
    print("=" * 50)
    print("  亚马逊BSR数据抓取")
    print("=" * 50)

    results = {}

    for key, config in CATEGORIES.items():
        print(f"\n▶ {config['name']}")
        print(f"  URL: {config['url']}")

        success = fetch_with_curl(config["url"], config["output"])
        results[key] = success

        if not success:
            print(f"\n  📝 手动获取方法:")
            print(f"  1. 在浏览器中打开: {config['url']}")
            print(f"  2. 保存页面内容到: {HTML_DIR / config['output']}")
            print(f"  3. 或使用WebFetch工具获取页面内容")

        time.sleep(5)  # 类目间间隔

    print("\n" + "=" * 50)
    print("  抓取完成!")
    for key, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {CATEGORIES[key]['name']}")
    print("=" * 50)

    return all(results.values())


if __name__ == "__main__":
    fetch_all()
