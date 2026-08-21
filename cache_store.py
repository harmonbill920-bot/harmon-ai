import os, json, sqlite3, threading
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_FILE = os.path.join(DATA_DIR, 'harmon_cache.sqlite3')
TZ = 'Africa/Dar_es_Salaam'
LOCAL_TZ = ZoneInfo(TZ)
_LOCK = threading.RLock()


def now_iso():
    return datetime.now(LOCAL_TZ).isoformat()


def conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    c = sqlite3.connect(DB_FILE, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA busy_timeout=30000')
    c.execute('''CREATE TABLE IF NOT EXISTS api_cache (
        cache_key TEXT PRIMARY KEY,
        endpoint TEXT NOT NULL,
        params_json TEXT NOT NULL,
        saved_at TEXT NOT NULL,
        data_json TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
        cache_key TEXT PRIMARY KEY,
        fixture_id INTEGER NOT NULL,
        saved_at TEXT NOT NULL,
        data_json TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS quota (
        id INTEGER PRIMARY KEY CHECK(id=1),
        day TEXT,
        remaining INTEGER,
        limit_value INTEGER,
        blocked INTEGER DEFAULT 0,
        last_error TEXT,
        updated_at TEXT
    )''')
    c.execute('INSERT OR IGNORE INTO quota(id, day, remaining, limit_value, blocked, last_error, updated_at) VALUES(1,NULL,NULL,NULL,0,NULL,?)', (now_iso(),))
    c.commit()
    # One-time import of the previous JSON cache if the user already had it.
    legacy=os.path.join(DATA_DIR,'api_cache.json')
    try:
        count=c.execute('SELECT COUNT(*) AS n FROM api_cache').fetchone()['n']
        if count==0 and os.path.exists(legacy):
            with open(legacy,'r',encoding='utf-8') as f: old=json.load(f)
            for key,item in (old or {}).items():
                if isinstance(item,dict) and 'data' in item:
                    c.execute('INSERT OR IGNORE INTO api_cache(cache_key,endpoint,params_json,saved_at,data_json) VALUES(?,?,?,?,?)',(key,item.get('endpoint',''),json.dumps(item.get('params',{}),sort_keys=True),item.get('saved_at',now_iso()),json.dumps(item.get('data',{}),ensure_ascii=False)))
            c.commit()
    except Exception:
        pass
    return c


def get_cache(key):
    with _LOCK:
        c=conn()
        row=c.execute('SELECT * FROM api_cache WHERE cache_key=?',(key,)).fetchone()
        c.close()
        if not row: return None
        return {'saved_at':row['saved_at'], 'data':json.loads(row['data_json']), 'endpoint':row['endpoint'], 'params':json.loads(row['params_json'])}


def put_cache(key, endpoint, params, data):
    with _LOCK:
        c=conn(); c.execute('''INSERT INTO api_cache(cache_key,endpoint,params_json,saved_at,data_json) VALUES(?,?,?,?,?)
        ON CONFLICT(cache_key) DO UPDATE SET saved_at=excluded.saved_at,data_json=excluded.data_json,params_json=excluded.params_json''',
        (key,endpoint,json.dumps(params,sort_keys=True),now_iso(),json.dumps(data,ensure_ascii=False)))
        c.commit(); c.close()


def get_prediction(key):
    with _LOCK:
        c=conn(); row=c.execute('SELECT * FROM predictions WHERE cache_key=?',(key,)).fetchone(); c.close()
        if not row:return None
        return {'saved_at':row['saved_at'],'data':json.loads(row['data_json'])}


def put_prediction(key, fixture_id, data):
    with _LOCK:
        c=conn(); c.execute('''INSERT INTO predictions(cache_key,fixture_id,saved_at,data_json) VALUES(?,?,?,?)
        ON CONFLICT(cache_key) DO UPDATE SET saved_at=excluded.saved_at,data_json=excluded.data_json''',
        (key,fixture_id,now_iso(),json.dumps(data,ensure_ascii=False)))
        c.commit(); c.close()


def quota():
    with _LOCK:
        c=conn(); row=c.execute('SELECT * FROM quota WHERE id=1').fetchone(); c.close()
        return dict(row)


def set_quota(day, remaining=None, limit_value=None, blocked=None, last_error=None):
    with _LOCK:
        q=quota()
        c=conn(); c.execute('''UPDATE quota SET day=?,remaining=?,limit_value=?,blocked=?,last_error=?,updated_at=? WHERE id=1''',
            (day, remaining if remaining is not None else q.get('remaining'), limit_value if limit_value is not None else q.get('limit_value'),
             int(blocked if blocked is not None else q.get('blocked') or 0), last_error, now_iso()))
        c.commit(); c.close()
