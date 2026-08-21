# Harmon AI Production Fix

This version keeps a professional mobile-first Harmon AI UI and adds a safer server-side cache.

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
