HARMON AI PREDICTOR - FINAL FIX

Files included:
- app.py
- football_api.py
- predictor_engine.py
- templates/index.html
- static/style.css

ROOT CAUSE FIXED:
The old app was calling extra API endpoints (odds, H2H and
API-Football predictions) and was hiding Harmon AI failures.
That is why the UI could show 0%, N/A and undefined.

The new app:
- calls the Harmon statistical engine directly
- does NOT call /predictions
- does NOT call odds
- does NOT call H2H twice
- reports a real prediction-engine error instead of fake 0%
- uses cache/local fallbacks where possible
- handles the Free-plan Season requirement more safely

COPY:
1. Backup your current files first.
2. Copy football_api.py to the project root.
3. Copy app.py to the project root.
4. Copy predictor_engine.py to the project root.
5. Copy templates/index.html over the current one.
6. Keep your existing .env, model/, data/ and requirements.txt.

RUN:
    py app.py

Then:
    http://127.0.0.1:5000

Chrome:
    Ctrl + F5

IMPORTANT:
Do not change .env.
Do not paste the API key into code.
