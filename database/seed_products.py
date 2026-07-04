"""
seed_products.py

Sirf physical products jo Amazon/Flipkart pe listed hain.
Service brands (Zepto, Blinkit, Swiggy) yahan nahi hain —
unke liye alag Reddit/Twitter scraper banega baad mein.
"""

from database.db import SessionLocal
from database.models import Brand, Product

session = SessionLocal()

brands = {
    brand.brand_name.lower(): brand
    for brand in session.query(Brand).all()
}

products = [

    # ─────────────────── Amul ─────────────────── #

    Product(
        brand_id=brands["amul"].id,
        product_name="Amul Butter",
        amazon_asin="B09VZD4L1L",
        flipkart_url=(
            "https://www.flipkart.com/amul-pasteurised-salted-butter"
            "/product-reviews/itmd8456fd5e5276"
            "?pid=BUTEZ3B9DMEJU3PR&marketplace=FLIPKART"
        )
    ),

    Product(
        brand_id=brands["amul"].id,
        product_name="Amul Cheese",
        amazon_asin=None,
        flipkart_url=None
    ),

    # ─────────────────── Lux ─────────────────── #

    Product(
        brand_id=brands["lux"].id,
        product_name="Lux Even Toned Soap",
        amazon_asin="B096NCWYMY",
        flipkart_url=(
            "https://www.flipkart.com/lux-soft-glow-rose-vitamin-e-soap-bar-bathing"
            "/product-reviews/itmb7ba46f3e49be"
            "?pid=SOPFTHUKMGZUWZAF&marketplace=FLIPKART"
        )
    ),

    Product(
        brand_id=brands["lux"].id,
        product_name="Lux Soft Rose Body Wash",
        amazon_asin="B09KHFW8K9",
        flipkart_url=(
            "https://www.flipkart.com/lux-magnolia-magic-bodywash-with-niacinamide-radiant-bouncy-skin-feel"
            "/product-reviews/itm934c5c46ced2e"
            "?pid=BWSGFVHCGBGZJRNM&marketplace=FLIPKART"
        )
    ),

    # ─────────────────── Hocco ─────────────────── #
    # Flipkart pe available nahi — sirf Amazon se scrape hoga

    Product(
        brand_id=brands["hocco"].id,
        product_name="HOCCO Chocolate Brownie Dessert Mix",
        amazon_asin="B0F23XR4CV",
        flipkart_url=None
    ),

    Product(
        brand_id=brands["hocco"].id,
        product_name="HOCCO Bhaji",
        amazon_asin="B08KSBCWSV",
        flipkart_url=None
    ),

    # ─────────────────── boAt ─────────────────── #

    Product(
        brand_id=brands["boat"].id,
        product_name="boAt Airdopes 311",
        amazon_asin="B0CZ3ZPD8B",
        flipkart_url=(
            "https://www.flipkart.com/boat-airdopes-311-pro-w-50-hrs-playback-asap-charge"
            "-dual-mics-enx-technology-bluetooth-headset"
            "/product-reviews/itmdf2c606e0fc42"
            "?pid=ACCGZ5TF3PNEAQAD&marketplace=FLIPKART"
        )
    ),

    Product(
        brand_id=brands["boat"].id,
        product_name="boAt Rockerz 255 Pro",
        amazon_asin="B08TV2P1N8",
        flipkart_url=(
            "https://www.flipkart.com/boat-rockerz-255-pro-bluetooth-headset"
            "/product-reviews/itmc47981e3dac36"
            "?pid=ACCGU3DA4PKE8U9U&marketplace=FLIPKART"
        )
    ),

    # ─────────────────── Noise ─────────────────── #

    Product(
        brand_id=brands["noise"].id,
        product_name="Noise ColorFit Pro 5 Max",
        amazon_asin="B0CFYNMFRF",
        flipkart_url=(
            "https://www.flipkart.com/noise-pro-5-max-1-96-amoled-display-post-workout"
            "-analysis-diy-watch-face-bt-calling-smartwatch"
            "/product-reviews/itm87ff62d6bfe82"
            "?pid=SMWGSGQZ9HZPENMN&marketplace=FLIPKART"
        )
    ),

    Product(
        brand_id=brands["noise"].id,
        product_name="Noise Buds VS104",
        amazon_asin="B09Y5MK1KB",
        flipkart_url=None   # Flipkart pe official listing nahi mili
    ),

]

# ── Step 1: Service brands ke dummy products delete karo ── #
SERVICE_BRAND_NAMES = ["zepto", "blinkit", "swiggy"]

for brand_name in SERVICE_BRAND_NAMES:
    if brand_name in brands:
        deleted = session.query(Product).filter_by(
            brand_id=brands[brand_name].id
        ).delete()
        if deleted:
            print(f"  [DELETE] {deleted} product(s) removed for brand: {brand_name}")

session.flush()

# ── Step 2: Upsert actual products ── #
for product in products:
    existing = session.query(Product).filter_by(
        product_name=product.product_name
    ).first()

    if existing is None:
        session.add(product)
        print(f"  [INSERT] {product.product_name}")
    else:
        changed = False
        if existing.amazon_asin != product.amazon_asin:
            existing.amazon_asin = product.amazon_asin
            changed = True
        if existing.flipkart_url != product.flipkart_url:
            existing.flipkart_url = product.flipkart_url
            changed = True
        if changed:
            print(f"  [UPDATE] {product.product_name}")
        else:
            print(f"  [SKIP]   {product.product_name}")

session.commit()
session.close()
print("\n✅ seed_products.py done.\n")