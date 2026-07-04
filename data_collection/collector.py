"""
data_collection/collector.py

Master collector — ek jagah se saare platforms chalao.

Usage:
    from data_collection.collector import run_all
    run_all()
    run_all(platform="amazon")
    run_all(platform="flipkart")
    run_all(product_id=3)
"""

from data_collection import amazon, flipkart


def run_all(platform: str = "all", product_id: int = None):
    """
    Args:
        platform  : "all" | "amazon" | "flipkart"
        product_id: agar diya to sirf us ek product ke liye
    """
    print(f"\n{'█'*55}")
    print(f"  Brand Intelligence — Data Collection")
    print(f"  Platform : {platform.upper()}")
    print(f"{'█'*55}")

    if platform in ("all", "amazon"):
        print("\n▶  Starting Amazon collection...")
        amazon.run(product_id=product_id)

    if platform in ("all", "flipkart"):
        print("\n▶  Starting Flipkart collection...")
        flipkart.run(product_id=product_id)

    print("\n✅  Collection complete.\n")