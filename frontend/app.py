import streamlit as st
import requests
import re

# ---------- UI STYLE ----------
st.set_page_config(page_title="Search Explanation Engine", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-width: 800px;
    }

    .result-title a {
        color: #1a0dab;
        text-decoration: none;
        font-size: 22px;
        font-weight: 500;
    }

    .result-title a:hover {
        text-decoration: underline;
    }

    .rating {
        color: #f5b301;
        font-size: 16px;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HELPERS ----------

def clean_html(text):
    """Remove HTML tags like <strong>"""
    if not text:
        return ""
    return re.sub("<.*?>", "", text)


def compute_rating(analysis):

    score = 0

    if analysis.get("summary"):
        score += 3

    if analysis.get("main_topics"):
        score += 3

    if analysis.get("difficulty") not in ["Unknown", None]:
        score += 2

    if analysis.get("why_useful_for_query"):
        score += 2

    return max(score, 1)


def rating_stars(score):

    stars = "⭐" * score
    return f"{score}/10 {stars}"


# ---------- CONFIG ----------

import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001/search")

# ---------- HEADER ----------

st.title("🔎 Search Explanation Engine")

query = st.text_input("Search the web")

# ---------- SEARCH ----------

if st.button("Search"):

    if not query.strip():
        st.warning("Please enter a search query.")
        st.stop()

    with st.spinner("Searching and analyzing pages..."):

        try:
            response = requests.get(
                BACKEND_URL,
                params={"q": query},
                timeout=600
            )

            if response.status_code != 200:
                st.error("Backend error.")
                st.stop()

            results = response.json()

        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
            st.stop()

    if not results:
        st.info("No results found.")
        st.stop()

    # ---------- RESULTS ----------

    for result in results:

        title = result.get("title", "No title")
        snippet = clean_html(result.get("snippet", ""))
        url = result.get("url", "#")

        analysis = result.get("analysis", {})

        # Title (Google-style)
        st.markdown(
            f"<div class='result-title'><a href='{url}' target='_blank'>{title}</a></div>",
            unsafe_allow_html=True
        )

        # URL
        st.caption(url)

        # Snippet
        if snippet:
            st.write(snippet)

        # Rating
        rating = compute_rating(analysis)

        st.markdown(
            f"<div class='rating'>Rating: {rating_stars(rating)}</div>",
            unsafe_allow_html=True
        )

        # Explanation (Expandable)
        with st.expander("Why this result"):

            summary = analysis.get("summary", "No summary available.")
            topics = analysis.get("main_topics", [])
            difficulty = analysis.get("difficulty", "Unknown")
            usefulness = analysis.get("why_useful_for_query", [])

            st.write("**Summary:**", summary)

            if topics:
                st.write("**Topics:**", ", ".join(topics))

            st.write("**Difficulty:**", difficulty)

            if usefulness:
                st.write("**Why useful:**")
                for u in usefulness:
                    st.write(f"- {u}")

        st.divider()