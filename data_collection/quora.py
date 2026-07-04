from playwright.sync_api import sync_playwright

keyword = input("Enter Brand Name: ")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        f"https://www.quora.com/search?q={keyword}",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(6000)

    questions = page.locator("a[href*='/']").all()

    printed = set()

    print("\nTop Quora Results:\n")

    for q in questions:

        text = q.text_content()

        href = q.get_attribute("href")

        if (
            text
            and len(text) > 20
            and keyword.lower() in text.lower()
            and text not in printed
        ):

            printed.add(text)

            print("=" * 80)
            print(text.strip())

            if href.startswith("/"):
                print("https://www.quora.com" + href)
            else:
                print(href)

    browser.close()