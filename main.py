"""
main.py — Brand Intelligence Entry Point

Commands:
    python main.py collect                        # saare platforms, saare products
    python main.py collect --platform amazon      # sirf Amazon
    python main.py collect --platform flipkart    # sirf Flipkart
    python main.py collect --product-id 3         # sirf ek product

    python main.py serve                          # dashboard API start karo
"""

import argparse
from data_collection.collector import run_all


def main():
    parser = argparse.ArgumentParser(
        description="Brand Intelligence — data collection + dashboard"
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── collect ──────────────────────────────────────
    collect_parser = subparsers.add_parser("collect", help="Collect reviews from platforms")
    collect_parser.add_argument(
        "--platform",
        choices=["all", "amazon", "flipkart"],
        default="all",
        help="Which platform to scrape (default: all)",
    )
    collect_parser.add_argument(
        "--product-id",
        type=int,
        default=None,
        help="Collect only for this product ID",
    )

    # ── serve ─────────────────────────────────────────
    subparsers.add_parser("serve", help="Start the dashboard API server")

    args = parser.parse_args()

    if args.command == "collect":
        run_all(platform=args.platform, product_id=args.product_id)

    elif args.command == "serve":
        import uvicorn
        uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()