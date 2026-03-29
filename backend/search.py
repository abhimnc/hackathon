import requests
import os
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

def search_web(query):

    url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }

    params = {
        "q": query,
        "count": 10
    }

    r = requests.get(url, headers=headers, params=params)

    data = r.json()

    results = []

    if "web" not in data:
        return results

    for item in data["web"]["results"]:

        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("description")
        })

    return results