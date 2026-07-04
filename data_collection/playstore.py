import psycopg2
from google_play_scraper import search, reviews

conn = psycopg2.connect(
    host = "localhost",
    database = "brand_intelligence",
    user = "postgres",
    password = "vanshika"
)
cursor = conn.cursor()

keyword = input("Enter Brand Name:")
cursor.execute(
    """
    SELECT id
    FROM brands
    WHERE LOWER(brand_name)=LOWER(%s)
    """,
    (keyword,)
)

result = cursor.fetchone()
if result is None:

    cursor.execute(
        """
        INSERT INTO brands(brand_name)
        VALUES(%s)
        RETURNING id
        """,
        (keyword,)
    )

    brand_id = cursor.fetchone()[0]
    conn.commit()

else:

    brand_id = result[0]
results = search(
    keyword,
    lang="en",
    country="in",
    n_hits=10
)
ignore_words = [
    "partner",
    "delivery",
    "picker",
    "seller",
    "driver",
    "merchant",
    "vendor",
    "onboarding",
    "employee",
    "staff",
    "nexus"
]
selected_app = None

for app in results:

    title = app["title"]
    title_lower = title.lower()

    if any(word in title_lower for word in ignore_words):
        continue

    if not title_lower.startswith(keyword.lower()):
        continue

    selected_app = app
    break
if selected_app is None:

    print("No Consumer App Found")

    conn.close()

    exit()
print("\nMain App Found")

print(selected_app["title"])
print(selected_app["appId"])
if selected_app["appId"] is None:

    print("App ID not found.")

    conn.close()

    exit()
result, _ = reviews(
    selected_app["appId"],
    lang="en",
    country="in",
    count=100
)
inserted = 0

for review in result:

    content = review["content"]
    if not content.strip():
     continue
    rating = review["score"]
    author = review["userName"]
    created = review["at"]
    cursor.execute(
        """
        SELECT id
        FROM mentions
        WHERE brand_id=%s
        AND content=%s
        """,
        (
            brand_id,
            content
        )
    )

    existing = cursor.fetchone()
    if existing is None:

        cursor.execute(
            """
            INSERT INTO mentions
            (
                brand_id,
                source,
                title,
                content,
                author,
                rating,
                created_at
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                brand_id,
                "Play Store",
                selected_app["title"],
                content,
                author,
                rating,
                created
            )
        )

        inserted += 1
conn.commit()

print(f"\n{inserted} New Reviews Inserted Successfully")

conn.close()