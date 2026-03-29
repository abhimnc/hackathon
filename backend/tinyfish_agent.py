import requests
import os
from dotenv import load_dotenv

load_dotenv()

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")

def analyze_page(url, query):

    endpoint = "https://agent.tinyfish.ai/v1/automation/run"

    payload = {
        "url": url,
        "goal": f"""
Analyze this webpage and extract structured information.

Return JSON with:
- title
- summary
- main_topics
- difficulty (Beginner / Intermediate / Advanced)
- why_useful_for_query

Query: {query}
"""
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": TINYFISH_API_KEY
    }

    try:

        r = requests.post(endpoint, json=payload, headers=headers, timeout=60)

        return r.json()

    except:

        return {
            "summary": "Analysis failed",
            "main_topics": [],
            "difficulty": "unknown",
            "why_useful_for_query": []
        }