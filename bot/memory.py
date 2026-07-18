import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "trades.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, timestamp TEXT, symbol TEXT, side TEXT, entry_price REAL, exit_price REAL, pnl REAL, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reflections (id INTEGER PRIMARY KEY, timestamp TEXT, key_insights TEXT)''')
    conn.commit()
    conn.close()

def get_recent_trades(limit=20):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(f"SELECT * FROM trades ORDER BY timestamp DESC LIMIT {limit}", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df.to_dict('records') if not df.empty else []

def get_latest_reflection():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM reflections ORDER BY timestamp DESC LIMIT 1", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()

init_db()