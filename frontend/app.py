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


        # Explanation (Expandable)
        with st.expander("Why this result"):

            summary = analysis.get("summary", "No summary available.")
            topics = analysis.get("main_topics", [])

            st.markdown(f"**title:** {title}")
            st.markdown(f"**summary:** {summary}")

            if topics:
                st.markdown(f"**main\\_topics:** {', '.join(topics)}")

        st.divider()