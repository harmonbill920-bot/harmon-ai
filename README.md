# Harmon AI — Production Predictor

This build is designed for public launch with a central cache and strict live-data truth rules.

## Included
- Country → League → Matches
- Team search (e.g. Simba)
- Yesterday / Today / Tomorrow
- LIVE minute only when the API response is fresh/verified
- Cached data clearly labeled; never invents a LIVE minute
- SQLite central cache and API quota guard
- Prediction cache keyed by fixture + model version
- Harmon AI: 1X2, confidence, data quality, xG, O/U, BTTS, double chance, correct score, recent form, H2H, explanation
- Favorites stored in the browser
- Predictions / Leagues / Favorites / More pages
- Mobile responsive UI
- Gunicorn/Render ready

## Local
1. Copy `.env.example` to `.env` and set `API_FOOTBALL_KEY`.
2. `py -m pip install -r requirements.txt`
3. `py app.py`
4. Open `http://127.0.0.1:5000`

## Render
Build Command: `pip install -r requirements.txt`
Start Command: `gunicorn app:app --workers 2 --threads 4 --timeout 60`
Environment Variable: `API_FOOTBALL_KEY`

### Important production note
The default cache is SQLite. On hosts with ephemeral disks, cache is lost on restart/redeploy. The app still works, but for serious scale use a persistent Postgres/Redis cache later. The API quota manager and strict live verification remain active.
