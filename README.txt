Harmon AI - Production Cache Edition

1) Copy .env.example to .env and set API_FOOTBALL_KEY.
2) Install: py -m pip install -r requirements.txt
3) Run: py app.py
4) Open: http://127.0.0.1:5000

Architecture:
- Shared SQLite cache for API responses and predictions.
- Daily quota state prevents repeated calls after API quota is exhausted.
- Cached data is never labelled as verified LIVE.
- Fixture cache default is 15 minutes (free-plan friendly).
- Team search cache 24h, upcoming 30m, form 6h, H2H 24h.
- Prediction results are cached so many users do not recompute the same match.

For production, use a paid API plan if you need frequent live updates. Never put the API key in frontend code.
