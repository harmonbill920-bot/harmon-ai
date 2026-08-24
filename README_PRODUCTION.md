# Harmon Football Prediction Production Fix

This version keeps a professional mobile-first Harmon Football Prediction UI and adds a safer server-side cache.

## Important
- Never invents live minutes.
- Cached fixtures never expose a cached `elapsed` as LIVE.
- A fixture is indexed when a date is loaded, so Analyze does not need another fixture API call.
- Prediction results are cached.
- One Gunicorn worker is used on Render to reduce duplicate cache/API work on the free instance.

## Render
Build: `pip install -r requirements.txt`
Start: `gunicorn app:app --workers 1 --threads 4 --timeout 60`
Environment variable: `API_FOOTBALL_KEY`

For true multi-instance production, move the cache from SQLite to Postgres/Redis.


## Production truth + quota protection
- Today's page may request the date fixture list once per cache window.
- If the date list is cached, the optional LIVE refresh uses `fixtures?live=all` and is shared through the server cache for 20 seconds.
- Cached fixtures NEVER expose an elapsed live minute.
- When API quota is exhausted, stale cached fixtures can still be shown if available, but LIVE minutes are hidden.
- Predictions are cached by fixture + model version.
- Never put `API_FOOTBALL_KEY` in frontend JavaScript.
