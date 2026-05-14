import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

url = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hairpieces/zgbs/beauty/702380011/ref=zg_bs_nav_beauty_3_702379011'

try:
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for different selectors
    print("=== Checking page structure ===")

    # Look for any product links
    links = soup.select('a[href*="/dp/"]')
    print(f"Found {len(links)} product links")

    # Look for the main list
    list_items = soup.select('#zg-browse-root ul li')
    print(f"Found {len(list_items)} list items")

    # Check for any structured data
    scripts = soup.select('script[type="application/ld+json"]')
    print(f"Found {len(scripts)} JSON-LD scripts")

    for i, script in enumerate(scripts[:2]):
        try:
            data = json.loads(script.string)
            print(f"Script {i}: {json.dumps(data, indent=2)[:500]}")
        except:
            pass

    # Check for best seller specific elements
    bsr_items = soup.select('[data-asin]')
    print(f"Found {len(bsr_items)} data-asin elements")

    # Print sample of the page content
    print("\n=== Sample content ===")
    content = soup.get_text()[:2000]
    print(content)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
