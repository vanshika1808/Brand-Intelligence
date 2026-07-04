from curl_cffi import requests

keyword = input("Enter Product Name: ")

url = f"https://www.reddit.com/search.json?q={keyword}"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    impersonate="chrome"
)

print("Status Code:", response.status_code)

if response.status_code == 200:

    data = response.json()

    posts = data["data"]["children"]

    print("\nPosts Found:", len(posts))

    print()

    for post in posts[:10]:

        post = post["data"]

        print("=" * 70)

        print("TITLE:")
        print(post["title"])

        print()

        print("AUTHOR:")
        print(post["author"])

        print()

        print("SCORE:")
        print(post["score"])

        print()

        print("URL:")
        print("https://reddit.com" + post["permalink"])

else:

    print(response.text)