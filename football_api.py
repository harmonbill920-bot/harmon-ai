import os, json, hashlib, requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from cache_store import get_cache, put_cache, get_fixture_cache, quota, set_quota

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY", "").strip()
BASE_URL = "https://v3.football.api-sports.io"
TZ = "Africa/Dar_es_Salaam"
LOCAL_TZ = ZoneInfo(TZ)
REQUEST_TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12"))

# These defaults intentionally reduce API calls. Live data is never simulated.
FIXTURE_TTL = int(os.getenv("FIXTURE_CACHE_TTL_SECONDS", "300"))
TEAM_TTL = int(os.getenv("TEAM_CACHE_TTL_SECONDS", "86400"))
UPCOMING_TTL = int(os.getenv("UPCOMING_CACHE_TTL_SECONDS", "1800"))
FORM_TTL = int(os.getenv("FORM_CACHE_TTL_SECONDS", "86400"))
H2H_TTL = int(os.getenv("H2H_CACHE_TTL_SECONDS", "604800"))
ID_TTL = int(os.getenv("FIXTURE_ID_CACHE_TTL_SECONDS", "21600"))

LIVE_STATUSES = {"1H", "2H", "ET", "P", "LIVE", "HT"}
FINAL_STATUSES = {"FT", "AET", "PEN"}

def now():
    return datetime.now(LOCAL_TZ)

def _age(saved_at):
    try:
        d = datetime.fromisoformat(saved_at)
        if d.tzinfo is None:
            d = d.replace(tzinfo=LOCAL_TZ)
        return max(0, int((now() - d.astimezone(LOCAL_TZ)).total_seconds()))
    except Exception:
        return 10**9

def _key(endpoint, params):
    return hashlib.sha256(json.dumps(
        {"e": endpoint, "p": params}, sort_keys=True
    ).encode()).hexdigest()

def _error(data):
    e = data.get("errors") if isinstance(data, dict) else None
    if not e:
        return None
    if isinstance(e, dict):
        return " | ".join(f"{k}: {v}" for k, v in e.items())
    if isinstance(e, list):
        return " | ".join(map(str, e))
    return str(e)

def _quota_blocked():
    q = quota()
    today = now().date().isoformat()
    if q.get("day") != today:
        set_quota(today, remaining=None, limit_value=None, blocked=0, last_error=None)
        return False
    return bool(q.get("blocked"))

def _ttl(endpoint, params):
    if endpoint == "fixtures":
        if "id" in params: return ID_TTL
        if "date" in params: return FIXTURE_TTL
        if "team" in params: return UPCOMING_TTL
        if "from" in params: return FORM_TTL
        if "h2h" in params: return H2H_TTL
    if endpoint == "teams": return TEAM_TTL
    return FIXTURE_TTL

def _cache_response(item, error):
    if not item:
        return None
    age = _age(item["saved_at"])
    return {
        "success": True, "data": item["data"], "live": False,
        "cached": True, "saved_at": item["saved_at"],
        "age_seconds": age,
        "warning": f"Live API haijathibitishwa. Cache ina data ya {age//60} dk zilizopita.",
        "live_error": error
    }

def api_request(endpoint, params=None, force=False):
    params = params or {}
    key = _key(endpoint, params)
    item = get_cache(key)
    ttl = _ttl(endpoint, params)

    if item and not force and _age(item["saved_at"]) < ttl:
        return {
            "success": True, "data": item["data"], "live": False,
            "cached": True, "saved_at": item["saved_at"],
            "age_seconds": _age(item["saved_at"]),
            "warning": f"Cache: data imesasishwa {_age(item['saved_at'])//60} dk zilizopita."
        }

    if not API_KEY:
        return _cache_response(item, "API_FOOTBALL_KEY haijawekwa") or {
            "success": False, "error": "API_FOOTBALL_KEY haijawekwa kwenye environment."
        }

    if _quota_blocked():
        q = quota()
        return _cache_response(item, q.get("last_error") or "Daily API quota reached") or {
            "success": False,
            "error": q.get("last_error") or "Daily API quota reached",
            "quota_blocked": True
        }

    try:
        r = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers={"x-apisports-key": API_KEY},
            params=params, timeout=REQUEST_TIMEOUT
        )
        try:
            data = r.json()
        except Exception:
            data = {}
        err = _error(data)
        remaining = r.headers.get("x-ratelimit-requests-remaining") or r.headers.get("X-RateLimit-Remaining")
        limit = r.headers.get("x-ratelimit-requests-limit") or r.headers.get("X-RateLimit-Limit")
        try: remaining_i = int(remaining) if remaining is not None else None
        except Exception: remaining_i = None
        try: limit_i = int(limit) if limit is not None else None
        except Exception: limit_i = None
        day = now().date().isoformat()

        if r.ok and not err:
            put_cache(key, endpoint, params, data)
            set_quota(day, remaining_i, limit_i, remaining_i == 0 if remaining_i is not None else False, None)
            return {
                "success": True, "data": data, "live": True, "cached": False,
                "saved_at": now().isoformat(),
                "quota_remaining": remaining_i, "quota_limit": limit_i
            }

        error = err or f"HTTP {r.status_code}"
        is_limit = ("request limit" in error.lower() or "quota" in error.lower() or r.status_code in (403, 429))
        set_quota(day, 0 if is_limit else remaining_i, limit_i, is_limit, error)
        return _cache_response(item, error) or {
            "success": False, "error": error, "live": False, "quota_blocked": is_limit
        }
    except Exception as exc:
        return _cache_response(item, str(exc)) or {
            "success": False, "error": str(exc), "live": False
        }

def normalize_fixture(item, verified=False, saved_at=None, warning=None):
    f = item.get("fixture") or {}
    l = item.get("league") or {}
    t = item.get("teams") or {}
    h, a = t.get("home") or {}, t.get("away") or {}
    s = f.get("status") or {}
    g = item.get("goals") or {}
    return {
        "fixture_id": f.get("id"), "date": f.get("date"),
        "status": s.get("short"), "status_long": s.get("long"),
        "elapsed": s.get("elapsed") if verified else None,
        "live_verified": bool(verified),
        "data_source": "LIVE API" if verified else "CACHE",
        "cache_saved_at": saved_at, "warning": warning,
        "league_id": l.get("id"), "league_name": l.get("name", "Football"),
        "country": l.get("country") or "International",
        "league_logo": l.get("logo") or "", "season": l.get("season"),
        "home_id": h.get("id"), "home_team": h.get("name", "Home"),
        "home_logo": h.get("logo") or "", "away_id": a.get("id"),
        "away_team": a.get("name", "Away"), "away_logo": a.get("logo") or "",
        "home_goals": g.get("home"), "away_goals": g.get("away")
    }

def get_fixtures_by_date(date_str):
    r = api_request("fixtures", {"date": date_str, "timezone": TZ})
    if not r.get("success"): return r
    arr = r["data"].get("response", []) or []
    matches = [normalize_fixture(x, r.get("live", False), r.get("saved_at"), r.get("warning")) for x in arr]
    # Store individual fixture payloads in the same server cache so Analyze does not
    # make a second fixture API call for every click.
    for x in arr:
        fid = ((x.get("fixture") or {}).get("id"))
        if fid:
            put_cache(f"fixture_index:{fid}", "fixture_index", {"id": fid}, x)
    return {**r, "matches": matches, "count": len(matches)}

def get_fixture(fixture_id):
    cached = get_fixture_cache(fixture_id)
    if cached:
        return {
            "success": True, "item": cached["data"],
            "match": normalize_fixture(cached["data"], False, cached["saved_at"],
                                        "Fixture details kutoka server cache; live haijathibitishwa."),
            "live": False, "cached": True, "saved_at": cached["saved_at"],
            "warning": "Fixture details kutoka server cache; live haijathibitishwa."
        }
    r = api_request("fixtures", {"id": fixture_id, "timezone": TZ})
    if not r.get("success"): return r
    arr = r["data"].get("response", []) or []
    if not arr: return {"success": False, "error": "Fixture haijapatikana."}
    return {**r, "item": arr[0],
            "match": normalize_fixture(arr[0], r.get("live", False), r.get("saved_at"), r.get("warning"))}

def search_teams(query):
    q = (query or "").strip()
    if len(q) < 2:
        return {"success": False, "error": "Andika angalau herufi 2."}
    r = api_request("teams", {"search": q})
    if not r.get("success"): return r
    teams = []
    for x in r["data"].get("response", [])[:20]:
        t = x.get("team") or {}
        if t.get("id"):
            teams.append({"id": t["id"], "name": t.get("name", "Unknown"), "logo": t.get("logo", "")})
    return {**r, "teams": teams}

def get_team_upcoming(team_id, n=10):
    r = api_request("fixtures", {"team": team_id, "next": max(1, min(n, 10)), "timezone": TZ})
    if not r.get("success"): return r
    return {**r, "matches": [
        normalize_fixture(x, r.get("live", False), r.get("saved_at"), r.get("warning"))
        for x in r["data"].get("response", []) or []
    ], "count": len(r["data"].get("response", []) or [])}

def get_recent_form(team_id, days=180, limit=10):
    end = now().date()
    start = end - timedelta(days=days)
    r = api_request("fixtures", {"team": team_id, "from": start.isoformat(), "to": end.isoformat(), "timezone": TZ})
    if not r.get("success"): return r
    arr = []
    for x in r["data"].get("response", []) or []:
        st = ((x.get("fixture") or {}).get("status") or {}).get("short")
        if st in FINAL_STATUSES: arr.append(x)
    arr.sort(key=lambda x: (x.get("fixture") or {}).get("date", ""), reverse=True)
    arr = arr[:limit]
    w = d = l = gf = ga = 0
    form = []
    for m in arr:
        t, g = m.get("teams") or {}, m.get("goals") or {}
        h, a = t.get("home") or {}, t.get("away") or {}
        hg, ag = g.get("home"), g.get("away")
        if hg is None or ag is None: continue
        x, y = (hg, ag) if h.get("id") == team_id else ((ag, hg) if a.get("id") == team_id else (None, None))
        if x is None: continue
        gf += x; ga += y
        if x > y: w += 1; form.append("W")
        elif x == y: d += 1; form.append("D")
        else: l += 1; form.append("L")
    n = w + d + l
    return {**r, "form": {
        "matches": n, "wins": w, "draws": d, "losses": l,
        "goals_for": gf, "goals_against": ga,
        "points_per_game": round((w*3+d)/n, 2) if n else 0,
        "goals_per_game": round(gf/n, 2) if n else 0,
        "conceded_per_game": round(ga/n, 2) if n else 0,
        "form_string": " ".join(form) if form else "N/A"
    }}

def get_h2h(home_id, away_id):
    r = api_request("fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "timezone": TZ})
    if not r.get("success"): return r
    hw = dr = aw = hg = ag = n = 0
    for m in r["data"].get("response", []) or []:
        t, g = m.get("teams") or {}, m.get("goals") or {}
        hs, aws = g.get("home"), g.get("away")
        h, a = t.get("home") or {}, t.get("away") or {}
        if hs is None or aws is None: continue
        x, y = (hs, aws) if h.get("id") == home_id else ((aws, hs) if a.get("id") == home_id else (None, None))
        if x is None: continue
        n += 1; hg += x; ag += y
        if x > y: hw += 1
        elif x == y: dr += 1
        else: aw += 1
    return {**r, "h2h": {
        "matches": n, "home_wins": hw, "draws": dr, "away_wins": aw,
        "home_goals": hg, "away_goals": ag
    }}
