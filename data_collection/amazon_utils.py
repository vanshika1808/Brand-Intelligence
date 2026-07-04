from datetime import datetime


def build_review_url(asin: str, page: int = 1) -> str:
    return (
        f"https://www.amazon.in/product-reviews/{asin}/"
        f"?ie=UTF8&reviewerType=all_reviews&pageNumber={page}"
    )


def parse_rating(rating_text: str) -> float | None:
    if not rating_text:
        return None
    try:
        return float(rating_text.strip().split(" ")[0])
    except (ValueError, IndexError):
        return None


def parse_review_date(date_text: str) -> datetime | None:
    if not date_text:
        return None
    try:
        cleaned = date_text.split(" on ")[-1].strip()
        return datetime.strptime(cleaned, "%d %B %Y")
    except (ValueError, IndexError):
        return None