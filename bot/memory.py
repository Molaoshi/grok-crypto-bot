import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "trades.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, timestamp TEXT, symbol TEXT, side TEXT, entry_price REAL, exit_price REAL, pnl REAL, fees REAL, status TEXT, backtest_id TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reflections (id INTEGER PRIMARY KEY, timestamp TEXT, key_insights TEXT)''')
    conn.commit()
    conn.close()

def log_trade(trade_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO trades (timestamp, symbol, side, entry_price, exit_price, pnl, fees, status, backtest_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade_data.get('timestamp', datetime.utcnow().isoformat()),
        trade_data.get('symbol'),
        trade_data.get('side'),
        trade_data.get('entry_price'),
        trade_data.get('exit_price'),
        trade_data.get('pnl'),
        trade_data.get('fees', 0),
        trade_data.get('status', 'closed'),
        trade_data.get('backtest_id', '')
    ))
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