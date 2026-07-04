from data_collection.amazon_utils import parse_rating, parse_review_date


def extract_reviews_from_page(page) -> list[dict]:
    reviews = []

    review_blocks = page.locator("[data-hook='review']")
    count = review_blocks.count()
    print(f"DEBUG: Found {count} review blocks on page")

    for i in range(count):
        block = review_blocks.nth(i)

        try:
            title = block.locator(
                "a[data-hook='review-title'] span"
            ).last.inner_text(timeout=2000)
        except Exception:
            title = None

        try:
            content = block.locator(
                "span[data-hook='review-body'] span"
            ).first.inner_text(timeout=2000)
        except Exception:
            content = None

        try:
            rating_text = block.locator(
                "i[data-hook='review-star-rating'] span"
            ).first.inner_text(timeout=2000)
            rating = parse_rating(rating_text)
        except Exception:
            rating = None

        try:
            date_text = block.locator(
                "span[data-hook='review-date']"
            ).first.inner_text(timeout=2000)
            review_date = parse_review_date(date_text)
        except Exception:
            review_date = None

        if title or content:
            reviews.append(
                {
                    "title": title,
                    "content": content,
                    "rating": rating,
                    "created_at": review_date,
                }
            )

    return reviews