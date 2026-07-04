"""
data_collection/flipkart.py

Orchestrator for Flipkart review collection.
Mirrors amazon.py — same flow, same DB writes, different parser.

Flow:
  crud.get_products_with_flipkart_url()
    → Playwright navigate to review pages
    → flipkart_parser.extract_reviews_from_page()
    → crud.mention_exists() duplicate check
    → crud.save_mention()
"""

import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

from database.models import Mention
from database import crud
from data_collection.flipkart_parser import extract_reviews_from_page
from data_collection.flipkart_utils import get_review_url

MAX_REVIEWS_PER_PRODUCT = 20
PAGES_TO_SCRAPE = 3      # Flipkart shows ~8 reviews/page


def _random_delay(lo=2.5, hi=5.0):
    time.sleep(random.uniform(lo, hi))


def get_products_with_flipkart_url():
    """
    Filter products that have a flipkart_url set.
    crud.py me abhi sirf amazon_asin wala filter hai,
    yahan directly query karte hain.
    """
    from database.db import SessionLocal
    from database.models import Product
    session = SessionLocal()
    try:
        return session.query(Product).filter(
            Product.flipkart_url.isnot(None),
            Product.flipkart_url != ""
        ).all()
    finally:
        session.close()


def collect_for_product(page, product) -> int:
    saved = 0
    collected = 0

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        if collected >= MAX_REVIEWS_PER_PRODUCT:
            break

        url = get_review_url(product.flipkart_url, page=page_num)
        print(f"    [flipkart] page {page_num} → {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20_000)
            page.wait_for_timeout(2500)
        except PwTimeout:
            print("    [TIMEOUT] Page load timeout, skipping.")
            break

        # Flipkart bot detection — redirects to login or shows empty page
        if "login" in page.url.lower():
            print("    [BLOCKED] Redirected to login. Stopping.")
            break

        reviews = extract_reviews_from_page(page)
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
                source="flipkart",
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

        _random_delay()

    return saved


def run(product_id: int = None):
    if product_id:
        product = crud.get_product_by_id(product_id)
        if not product or not product.flipkart_url:
            print(f"[ERROR] Product {product_id} not found or has no Flipkart URL.")
            return
        products = [product]
    else:
        products = get_products_with_flipkart_url()

    if not products:
        print("[INFO] No products with flipkart_url found in DB.")
        return

    print(f"\n{'═'*55}")
    print(f"  Flipkart Collector — {len(products)} product(s) to process")
    print(f"{'═'*55}")

    total_saved = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        for product in products:
            print(f"\n  Product : {product.product_name}")
            print(f"  URL     : {product.flipkart_url}")
            saved = collect_for_product(page, product)
            total_saved += saved
            print(f"  ✅ {saved} new mention(s) saved")
            _random_delay(3, 7)

        browser.close()

    print(f"\n{'═'*55}")
    print(f"  Done. Total new mentions saved: {total_saved}")
    print(f"{'═'*55}\n")