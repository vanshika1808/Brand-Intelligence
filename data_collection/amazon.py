"""
data_collection/amazon.py

Amazon ke liye requests + BeautifulSoup + browser cookies.
"""

import re
import time
import random
import requests
import browser_cookie3
from bs4 import BeautifulSoup
from datetime import datetime

from database.models import Mention
from database import crud
from data_collection.amazon_utils import build_review_url, parse_rating, parse_review_date

MAX_REVIEWS_PER_PRODUCT = 20
PAGES_TO_SCRAPE = 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
}


def get_amazon_cookies():
    """Chrome se Amazon.in ke cookies lo."""
    try:
        cookies = browser_cookie3.chrome(domain_name=".amazon.in")
        print("    [COOKIES] Chrome se Amazon cookies load ho gayi ✅")
        return cookies
    except Exception as e:
        print(f"    [COOKIES] Chrome cookies nahi mili: {e}")
        print("    [COOKIES] Edge try kar raha hun...")
        try:
            cookies = browser_cookie3.edge(domain_name=".amazon.in")
            print("    [COOKIES] Edge se Amazon cookies load ho gayi ✅")
            return cookies
        except Exception as e2:
            print(f"    [COOKIES] Edge bhi fail: {e2}")
            return None


def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_reviews_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    nodes = soup.find_all(attrs={"data-hook": "review"})
    print(f"    DEBUG: Found {len(nodes)} review blocks on page")

    reviews = []
    for node in nodes:
        rating_el = node.select_one("[data-hook='review-star-rating'] .a-icon-alt")
        rating = parse_rating(rating_el.get_text()) if rating_el else None

        title_el = node.select_one("[data-hook='review-title']")
        title = None
        if title_el:
            spans = title_el.find_all("span", recursive=False)
            title = clean(spans[-1].get_text()) if spans else clean(title_el.get_text())

        body_el = node.select_one("[data-hook='review-body']")
        content = clean(body_el.get_text()) if body_el else None

        author_el = node.select_one(".a-profile-name")
        author = clean(author_el.get_text()) if author_el else None

        date_el = node.select_one("[data-hook='review-date']")
        created_at = parse_review_date(date_el.get_text()) if date_el else None

        if title or content:
            reviews.append({
                "title": title,
                "content": content,
                "rating": rating,
                "author": author,
                "created_at": created_at,
            })

    return reviews


def fetch_page_html(url: str, cookies) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, cookies=cookies, timeout=15)
        resp.raise_for_status()

        if "captcha" in resp.text.lower() or "validateCaptcha" in resp.text:
            print("    [BLOCKED] CAPTCHA detected.")
            return None
        if "ap/signin" in resp.url or "signin" in resp.url:
            print("    [BLOCKED] Redirected to login — cookies kaam nahi ki.")
            print("    ➡  Amazon.in browser me open karo aur login karo, phir dobara chalao.")
            return None

        return resp.text
    except requests.RequestException as e:
        print(f"    [ERROR] {e}")
        return None


def collect_for_product(product, cookies) -> int:
    saved = 0
    collected = 0

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        if collected >= MAX_REVIEWS_PER_PRODUCT:
            break

        url = build_review_url(product.amazon_asin, page=page_num)
        print(f"    [amazon] page {page_num} → {url}")

        html = fetch_page_html(url, cookies)
        if not html:
            break

        reviews = parse_reviews_from_html(html)
        if not reviews:
            print("    No reviews found on this page, stopping.")
            break

        for r in reviews:
            if collected >= MAX_REVIEWS_PER_PRODUCT:
                break

            content = r.get("content") or ""
            title = r.get("title") or ""

            if crud.mention_exists(product.id, content):
                print(f"    [SKIP] Duplicate: {title[:40]!r}")
                continue

            mention = Mention(
                brand_id=product.brand_id,
                product_id=product.id,
                source="amazon",
                title=title,
                content=content,
                author=r.get("author"),
                rating=r.get("rating"),
                score=None,
                created_at=r.get("created_at") or datetime.utcnow(),
                sentiment=None,
                cluster_id=None,
            )
            crud.save_mention(mention)
            saved += 1
            collected += 1
            print(f"    [SAVED] ⭐{r.get('rating')} | {title[:50]!r}")

        time.sleep(random.uniform(2, 4))

    return saved


def run(product_id: int = None):
    # Cookies ek baar load karo — saare products ke liye same use hongi
    cookies = get_amazon_cookies()
    if not cookies:
        print("[ERROR] Browser cookies nahi mili. Amazon.in me login karo pehle.")
        return

    if product_id:
        product = crud.get_product_by_id(product_id)
        if not product or not product.amazon_asin:
            print(f"[ERROR] Product {product_id} not found or has no ASIN.")
            return
        products = [product]
    else:
        products = crud.get_products_with_asin()

    if not products:
        print("[INFO] No products with amazon_asin found in DB.")
        return

    print(f"\n{'═'*55}")
    print(f"  Amazon Collector — {len(products)} product(s) to process")
    print(f"{'═'*55}")

    total_saved = 0
    for product in products:
        print(f"\n  Product : {product.product_name}")
        print(f"  ASIN    : {product.amazon_asin}")
        saved = collect_for_product(product, cookies)
        total_saved += saved
        print(f"  ✅ {saved} new mention(s) saved")
        time.sleep(random.uniform(3, 6))

    print(f"\n{'═'*55}")
    print(f"  Done. Total new mentions saved: {total_saved}")
    print(f"{'═'*55}\n")