# TinyFish Search Explanation Engine

A two-service app that:
- searches the web with Brave Search,
- analyzes top results with TinyFish automation,
- shows results and explanations in a Streamlit UI.

The project is split into:
- `backend` (Flask API on `5001`)
- `frontend` (Streamlit app on `8501`)

## How It Works

1. You enter a query in the Streamlit UI.
2. Frontend calls `GET /search?q=<query>` on the backend.
3. Backend gets web results from Brave Search.
4. Backend analyzes each result URL with TinyFish.
5. Frontend displays title, snippet, URL, and an expandable explanation.

## Project Structure

- `backend/app.py` - Flask app (`/health`, `/search`)
- `backend/search.py` - Brave Search integration
- `backend/tinyfish_agent.py` - TinyFish analysis + normalization/fallbacks
- `frontend/app.py` - Streamlit UI
- `docker-compose.yml` - runs backend + frontend together
- `backend/Dockerfile` - backend container
- `frontend/Dockerfile` - frontend container
- `requirements.txt` - Python dependencies

## Prerequisites

- Python `3.11+`
- Docker + Docker Compose (for containerized setup)
- API keys:
  - `BRAVE_API_KEY`
  - `TINYFISH_API_KEY`

## Environment Variables

Create a `.env` file in the project root:

```env
BRAVE_API_KEY=your_brave_api_key
TINYFISH_API_KEY=your_tinyfish_api_key
```

Notes:
- Do not commit real API keys.
- If keys were ever committed, rotate/revoke them and replace immediately.

## Run With Docker (Recommended)

From the project root:

```bash
docker compose up --build
```

Then open:
- Frontend: `http://localhost:8501`
- Backend health: `http://localhost:5001/health`

## Run Locally (Without Docker)

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Start backend

```bash
python backend/app.py
```

Backend runs on `http://127.0.0.1:5001`.

### Start frontend (new terminal)

```bash
streamlit run frontend/app.py
```

Frontend runs on `http://localhost:8501`.

The frontend defaults to backend URL:
- `http://127.0.0.1:5001/search` (local)

When running with Docker Compose, frontend uses:
- `http://backend:5001/search` (set in `docker-compose.yml`)

## API Endpoints

### `GET /health`

Returns service status and uptime.

Example:

```bash
curl http://localhost:5001/health
```

### `GET /search?q=<query>`

Returns an array of results with analysis.

Example:

```bash
curl "http://localhost:5001/search?q=llm%20agents"
```

Response shape (simplified):

```json
[
  {
    "title": "Result title",
    "url": "https://example.com",
    "snippet": "Short result snippet",
    "analysis": {
      "summary": "Why this page matters",
      "main_topics": ["topic1", "topic2"],
      "why_useful_for_query": ["reason 1", "reason 2"]
    }
  }
]
```

## Troubleshooting

- `Query required` error:
  - Pass `q` parameter to `/search`.
- Empty/noisy analysis:
  - Verify `TINYFISH_API_KEY`.
  - Some pages may fail or timeout; backend includes fallback responses.
- No search results:
  - Verify `BRAVE_API_KEY` and quota/permissions.
- Frontend cannot reach backend:
  - Confirm backend is running on `5001`.
  - Check `BACKEND_URL` environment variable if running custom setup.

## License

No license file is currently included in this repository.
