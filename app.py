import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, render_template, jsonify, request
from football_api import (
    get_fixtures_by_date, get_fixture, search_teams, get_team_upcoming,
    TZ, quota
)
from predictor_engine import predict_match

app = Flask(__name__)
TZOBJ = ZoneInfo(TZ)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

@app.route("/api/health")
def health():
    q = quota()
    return jsonify({
        "success": True,
        "api_configured": bool(os.getenv("API_FOOTBALL_KEY")),
        "quota": q,
        "today": datetime.now(TZOBJ).date().isoformat()
    })

@app.route("/api/matches")
def matches():
    date = request.args.get("date") or datetime.now(TZOBJ).date().isoformat()
    refresh_live = request.args.get("live", "0") == "1"
    r = get_fixtures_by_date(date, refresh_live=refresh_live)
    if not r.get("success"):
        return jsonify({
            "success": False, "error": r.get("error", "API error"),
            "live": False, "quota": quota()
        }), 502
    return jsonify({
        "success": True, "date": date, "count": r["count"],
        "matches": r["matches"], "live": r.get("live", False),
        "cached": r.get("cached", False), "warning": r.get("warning"),
        "saved_at": r.get("saved_at"), "quota": quota(), "live_refresh": r.get("live_refresh", False),
        "live_refresh_error": r.get("live_refresh_error")
    })

@app.route("/api/team-search")
def team_search():
    r = search_teams(request.args.get("q", ""))
    if not r.get("success"):
        return jsonify(r), 502
    return jsonify(r)

@app.route("/api/team/<int:team_id>/upcoming")
def team_upcoming(team_id):
    try:
        n = max(1, min(int(request.args.get("next", 10)), 10))
    except ValueError:
        n = 10
    r = get_team_upcoming(team_id, n)
    if not r.get("success"):
        return jsonify(r), 502
    return jsonify(r)

@app.route("/api/analyze/<int:fixture_id>")
def analyze(fixture_id):
    fx = get_fixture(fixture_id)
    if not fx.get("success"):
        return jsonify(fx), 502
    m = fx["match"]
    p = predict_match(m["home_id"], m["away_id"], fixture_id, league_id=m.get("league_id"), season=m.get("season"))
    if not p.get("success"):
        return jsonify({
            "success": False, "error": p.get("error"),
            "data_available": False
        }), 502
    item = fx["item"]
    f = item.get("fixture") or {}
    l = item.get("league") or {}
    t = item.get("teams") or {}
    s = f.get("status") or {}
    return jsonify({
        "success": True,
        "match": m,
        "fixture": {
            "id": fixture_id, "date": f.get("date"),
            "status": s.get("short"),
            # elapsed is ONLY exposed when this exact response was live verified
            "elapsed": s.get("elapsed") if fx.get("live") else None
        },
        "home": t.get("home") or {}, "away": t.get("away") or {},
        "league": l, "harmon_ai": p,
        "live": fx.get("live", False), "cached": fx.get("cached", False),
        "warning": fx.get("warning"), "quota": quota()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
