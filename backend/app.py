from flask import Flask, request, jsonify
from search import search_web
from tinyfish_agent import analyze_page
import time

app = Flask(__name__)

START_TIME = time.time()


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
        return jsonify({"error": "Query required"}), 400

    results = search_web(query)

    explained_results = []

    for r in results[:5]:

        try:
            analysis = analyze_page(r["url"], query)
        except Exception as e:
            analysis = {
                "summary": "Analysis failed",
                "main_topics": [],
                "difficulty": "unknown",
                "why_useful_for_query": []
            }

        explained_results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("snippet"),
            "analysis": analysis
        })

    return jsonify(explained_results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)