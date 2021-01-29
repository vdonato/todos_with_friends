import string

import requests

headers = {"Authorization": "token FIXME"}

page = 1
while True:
    params = {"page": page, "per_page": 100, "state": "all"}
    issues = requests.get(
        "https://api.github.com/repos/streamlit/streamlit/issues",
        params=params,
        headers=headers,
    ).json()

    if not issues:
        exit()

    for issue in issues:
        if "pull_request" in issue:
            continue

        with open("titles.txt", "a") as f:
            t = issue["title"]
            if t[-1] not in string.punctuation:
                t += "."
            f.write(t)
            f.write("\n")

    page += 1
