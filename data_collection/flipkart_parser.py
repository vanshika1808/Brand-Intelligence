"""
data_collection/flipkart_parser.py

Extracts reviews from a Flipkart product-reviews page using Playwright.

Flipkart's CSS classes are minified and change with deployments,
so we use stable structural selectors instead of class names.
"""

from data_collection.flipkart_utils import parse_flipkart_rating, parse_flipkart_date


def extract_reviews_from_page(page) -> list[dict]:
    """
    Parse review blocks from the current Playwright page.

    Flipkart review block structure (as of mid-2026):
      <div data-id="...">           ← review container
        <div>4.2</div>              ← rating (inside coloured box)
        <p>Review title</p>
        <div>Review body text</div>
        <p>author, date</p>
      </div>
    """
    reviews = []

    # Primary selector: review cards identified by data-id attribute
    # Flipkart marks each review card with a unique data-id
    blocks = page.locator("div[data-id]")
    count = blocks.count()
    print(f"    DEBUG: {count} review block(s) found on page")

    if count == 0:
        # Fallback: look for the review-wrapper class pattern
        # This handles layout changes
        blocks = page.locator("div._27M-vq, div.col._2wzgFH, div.RcXBOT")
        count = blocks.count()
        print(f"    DEBUG (fallback): {count} block(s)")

    for i in range(count):
        block = blocks.nth(i)

        try:
            # Rating: first number-only text inside the block (e.g. "4" or "4.2")
            rating_text = block.locator(
                "div._3LWZlK, div[class*='rating'] span, div[class*='star']"
            ).first.inner_text(timeout=1500)
            rating = parse_flipkart_rating(rating_text)
        except Exception:
            rating = None

        try:
            # Title: bold/prominent <p> near top of card
            title = block.locator(
                "p._2-N8zT, p[class*='title'], p[class*='head']"
            ).first.inner_text(timeout=1500)
        except Exception:
            title = None

        try:
            # Review body: longest text block inside the card
            content = block.locator(
                "div.t-ZTKy div div, div[class*='review'] div div"
            ).first.inner_text(timeout=1500)
        except Exception:
            content = None

        try:
            # Author + date string: "Ravi Kumar, July 2025"
            meta = block.locator(
                "p._2sc7ZR, p[class*='author'], p[class*='meta']"
            ).first.inner_text(timeout=1500)
            # meta looks like: "Ravi Kumar\n3 July, 2025" or "Certified Buyer, 3 July, 2025"
            parts = [p.strip() for p in meta.replace("\n", ",").split(",") if p.strip()]
            author = parts[0] if parts else None

            # Find the date part (contains digit + month pattern)
            import re
            date_str = None
            for part in parts[1:]:
                if re.search(r"\d{4}|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", part):
                    date_str = part.strip()
                    break
            review_date = parse_flipkart_date(date_str) if date_str else None
        except Exception:
            author = None
            review_date = None

        # Skip empty blocks (Flipkart sometimes has ad cards with data-id)
        if not content and not title:
            continue

        reviews.append({
            "title": title,
            "content": content,
            "rating": rating,
            "author": author,
            "created_at": review_date,
        })

    return reviews