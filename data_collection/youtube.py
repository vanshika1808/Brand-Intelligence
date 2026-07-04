from playwright.sync_api import sync_playwright

keyword = input("Enter Brand Name: ")

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    # Search Videos
    page.goto(
        f"https://www.youtube.com/results?search_query={keyword}",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(5000)

    videos = page.locator("#video-title")

    first_video = videos.nth(0)

    href = first_video.get_attribute("href")

    video_url = "https://www.youtube.com" + href

    print("\nOpening Video:")
    print(video_url)

    # Open First Video
    page.goto(
        video_url,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(5000)

    # Scroll multiple times
    for _ in range(5):

        page.mouse.wheel(0, 3000)

        page.wait_for_timeout(3000)

    # Debug
    comment_count = page.locator("#content-text").count()

    print("\nComments Found:", comment_count)

    if comment_count > 0:

        comments = page.locator(
            "#content-text"
        ).all_text_contents()

        print("\nFIRST 20 COMMENTS:\n")

        for comment in comments[:20]:

            comment = comment.strip()

            if comment:

                print(comment)

                print("-" * 80)

    else:

        print(
            "\nNo comments loaded."
        )

    browser.close()