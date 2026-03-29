from flask import Flask, request, jsonify
from search import search_web
from tinyfish_agent import analyze_page
import time
import logging

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

START_TIME = time.time()


def _fallback_from_result(result, query, reason=None):
    snippet = (result.get("snippet") or "").strip()
    title = (result.get("title") or "This result").strip()
    summary = snippet or f"{title} is relevant to '{query}', but live analysis is currently unavailable."

    why_useful = []
    if reason:
        why_useful.append(reason)
    why_useful.append(f"Matched from web search for '{query}'.")

    return {
        "summary": summary,
        "main_topics": [],
        "why_useful_for_query": why_useful,
    }


# -------------------------
# Health Check API
# -------------------------
@app.route("/health", methods=["GET"])
def health():

    uptime = time.time() - START_TIME

    return jsonify({
        "status": "healthy",
        "service": "search-explanation-engine",
        "uptime_seconds": round(uptime, 2)
    }), 200


# -------------------------
# Search API
# -------------------------
@app.route("/search", methods=["GET"])
def search():

    query = request.args.get("q")

    if not query:
        logger.warning("Missing query param for /search")
        return jsonify({"error": "Query required"}), 400

    logger.info("Search request started | query=%s", query)
    results = search_web(query)
    logger.info("Search returned %d web results", len(results))

    explained_results = []

    for idx, r in enumerate(results[:5], start=1):
        url = r.get("url")
        logger.info("Analyzing result %d/%d | url=%s", idx, min(len(results), 5), url)

        try:
            analysis = analyze_page(url, query)
            if "request failed" in (analysis.get("summary", "").lower()):
                logger.warning("Using local fallback after TinyFish failure | url=%s", url)
                analysis = _fallback_from_result(
                    r,
                    query,
                    "Live page analysis timed out or failed for this URL.",
                )
            logger.info(
                "Analysis complete | url=%s | topics=%d",
                url,
                len(analysis.get("main_topics", [])),
            )
            logger.info(
                "why_useful_for_query | url=%s | value=%s",
                url,
                analysis.get("why_useful_for_query", []),
            )
        except Exception as e:
            logger.exception("Analysis crashed | url=%s | error=%s", url, str(e))
            analysis = _fallback_from_result(
                r,
                query,
                "Live page analysis encountered an unexpected error.",
            )

        explained_results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("snippet"),
            "analysis": analysis
        })

    logger.info("Search request finished | query=%s | explained_results=%d", query, len(explained_results))
    return jsonify(explained_results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)