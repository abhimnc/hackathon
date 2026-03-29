import requests
import os
from dotenv import load_dotenv
import json
import logging
import re

load_dotenv()

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
logger = logging.getLogger(__name__)


def _fallback_analysis(reason="Analysis failed"):
    return {
        "summary": reason,
        "main_topics": [],
        "why_useful_for_query": []
    }


def _extract_json_object(text):
    """
    Extract and parse a JSON object from plain text or markdown code fences.
    """
    if not isinstance(text, str):
        return None

    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Direct JSON object
    if cleaned.startswith("{") and cleaned.endswith("}"):
        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            pass

    # JSON object embedded in larger text
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    return None


def _normalize_analysis(data):
    """
    Normalize different TinyFish response formats into one stable schema.
    """
    if not isinstance(data, dict):
        return _fallback_analysis("Invalid analysis response")

    # Common API layouts: direct object, nested under output/result/data.
    analysis = (
        data.get("analysis")
        or data.get("output")
        or data.get("result")
        or data.get("data")
        or data
    )

    # Some providers nest structured fields one level deeper.
    if isinstance(analysis, dict):
        analysis = (
            analysis.get("analysis")
            or analysis.get("result")
            or analysis.get("output")
            or analysis.get("data")
            or analysis
        )

    # Some APIs return JSON string in `output`/`result`.
    if isinstance(analysis, str):
        parsed = _extract_json_object(analysis)
        if parsed:
            analysis = parsed
        else:
            return {
                "summary": analysis.strip() or "No summary available",
                "main_topics": [],
                "why_useful_for_query": []
            }

    if not isinstance(analysis, dict):
        return _fallback_analysis("No structured analysis returned")

    summary = (
        analysis.get("summary")
        or analysis.get("description")
        or analysis.get("final_answer")
        or analysis.get("answer")
    )

    # Some model outputs place full JSON text inside "summary".
    if isinstance(summary, str):
        parsed_summary = _extract_json_object(summary)
        if parsed_summary:
            analysis = parsed_summary
            summary = (
                analysis.get("summary")
                or analysis.get("description")
                or analysis.get("final_answer")
                or analysis.get("answer")
            )

    if not summary:
        summary = analysis.get("title") or "No summary available"

    topics = analysis.get("main_topics") or analysis.get("topics") or []
    if isinstance(topics, str):
        topics = [topics]

    usefulness = analysis.get("why_useful_for_query") or analysis.get("why_useful") or []
    if isinstance(usefulness, str):
        usefulness = [usefulness]

    # If summary is still empty, try deriving from usefulness text.
    if summary == "No summary available" and usefulness:
        summary = usefulness[0]

    return {
        "summary": summary,
        "main_topics": topics if isinstance(topics, list) else [],
        "why_useful_for_query": usefulness if isinstance(usefulness, list) else []
    }

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
- why_useful_for_query

Query: {query}
"""
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": TINYFISH_API_KEY
    }

    try:
        if not TINYFISH_API_KEY:
            logger.error("TinyFish API key missing; cannot analyze | url=%s", url)
            return _fallback_analysis("Missing TINYFISH_API_KEY")

        logger.info("TinyFish request started | url=%s | query=%s", url, query)
        r = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        logger.info("TinyFish response received | url=%s | status=%s", url, r.status_code)

        normalized = _normalize_analysis(data)
        if normalized.get("summary") == "No summary available":
            logger.warning(
                "Summary missing after normalize | url=%s | top_level_keys=%s",
                url,
                list(data.keys()) if isinstance(data, dict) else type(data).__name__,
            )
        logger.info(
            "TinyFish normalized | url=%s | topics=%d",
            url,
            len(normalized.get("main_topics", [])),
        )
        return normalized

    except requests.exceptions.RequestException as e:
        logger.error("TinyFish request failed | url=%s | error=%s", url, str(e))
        return _fallback_analysis(f"TinyFish request failed: {str(e)}")
    except ValueError:
        logger.error("TinyFish invalid JSON | url=%s", url)
        return _fallback_analysis("TinyFish returned invalid JSON")
    except Exception as e:
        logger.exception("Unexpected TinyFish error | url=%s | error=%s", url, str(e))
        return _fallback_analysis(f"Unexpected analysis error: {str(e)}")