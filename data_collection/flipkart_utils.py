"""
data_collection/flipkart_utils.py

Flipkart URL helpers and parsers.
NOTE: Flipkart review URLs are stored directly in products.flipkart_url
      because Flipkart encodes product IDs inside long slugs.
      Just store the reviews page URL in the DB — no need to construct it.

Example flipkart_url value in DB:
  https://www.flipkart.com/boat-airdopes-311/product-reviews/itmf9gh6gkhe6hum
"""

import re
from datetime import datetime


def get_review_url(flipkart_url: str, page: int = 1) -> str:
    """
    Append pagination to a Flipkart review URL.
    Flipkart uses ?page=N for pagination.
    """
    base = flipkart_url.split("?")[0]   # strip existing query params
    return f"{base}?page={page}"


def parse_flipkart_rating(text: str) -> float | None:
    """
    Flipkart shows rating as '4.2' or '4' inside a div.
    """
    if not text:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


def parse_flipkart_date(text: str) -> datetime | None:
    """
    Flipkart date format: '3 July, 2025'  or  'July 2025'
    """
    if not text:
        return None
    text = text.strip()
    formats = ["%d %B, %Y", "%B %Y", "%d %b, %Y", "%b %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None