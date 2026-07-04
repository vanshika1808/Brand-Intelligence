import psycopg2
from playwright.sync_api import sync_playwright

# ---------------- DATABASE CONNECTION ---------------- #

conn = psycopg2.connect(
    host="localhost",
    database="brand_intelligence",
    user="postgres",
    password="vanshika"
)

cursor = conn.cursor()

# ---------------- PRODUCT INPUT ---------------- #

product_id = int(input("Enter Product ID: "))

# Fetch Product Details

cursor.execute(
    """
    SELECT
        p.product_name,
        p.brand_id,
        b.brand_name
    FROM products p
    JOIN brands b
        ON p.brand_id = b.id
    WHERE p.id = %s
    """,
    (product_id,)
)

result = cursor.fetchone()

if result is None:
    print("Product Not Found")
    conn.close()
    exit()

product_name = result[0]
brand_id = result[1]
brand_name = result[2]

print("\nBrand   :", brand_name)
print("Product :", product_name)

# More Accurate Reddit Search
keyword = f"{brand_name} {product_name}"

# ---------------- REDDIT SCRAPING ---------------- #

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        f"https://www.reddit.com/search/?q={keyword}",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(6000)

    links = page.locator("a").all_text_contents()

    posts = []

    for text in links:

        text = text.strip()

        if (
            len(text) > 20
            and text not in posts
            and (
                brand_name.lower() in text.lower()
                or product_name.lower() in text.lower()
            )
        ):
            posts.append(text)

    print(f"\nFound {len(posts)} Posts\n")

    inserted = 0

    for post in posts:

        print(post)

        cursor.execute(
            """
            SELECT id
            FROM mentions
            WHERE product_id = %s
            AND title = %s
            """,
            (
                product_id,
                post
            )
        )

        existing = cursor.fetchone()

        if existing is None:

            cursor.execute(
                """
                INSERT INTO mentions
                (
                    brand_id,
                    product_id,
                    source,
                    title
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    brand_id,
                    product_id,
                    "Reddit",
                    post
                )
            )

            inserted += 1

    conn.commit()

    print(f"\n{inserted} New Reddit Posts Inserted Successfully")

    browser.close()

conn.close()