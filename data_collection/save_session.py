"""
data_collection/save_session.py

ONE-TIME SCRIPT.
Run this manually once. It opens a real browser window,
lets you log in to Amazon by hand, then saves the logged-in
session (cookies, tokens) to a file called amazon_session.json.

After this, amazon.py will reuse that saved session instead
of hitting Amazon as a fresh/anonymous visitor.
"""

from playwright.sync_api import sync_playwright


def save_amazon_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.amazon.in")

        print("\n>>> Browser window khul gaya hai.")
        print(">>> Usme manually apna Amazon account se login karo.")
        print(">>> Login complete hone ke baad, yahan terminal mein wapas aakar Enter dabao.\n")

        input("Login ho gaya? Enter dabao continue karne ke liye... ")

        context.storage_state(path="amazon_session.json")
        print("\n✅ Session save ho gaya: amazon_session.json")

        browser.close()


if __name__ == "__main__":
    save_amazon_session()