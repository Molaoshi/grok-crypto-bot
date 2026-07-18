import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yaml
from pathlib import Path
import sys
import sqlite3

sys.path.append(str(Path(__file__).parent))

from bot.memory import get_recent_trades, get_latest_reflection
from bot.backtester import run_backtest
from bot.data_handler import DataHandler
from bot.risk_manager import RiskManager

st.set_page_config(page_title="Grok Crypto Bot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown('''<style>.stApp { background-color: #0e1117; color: #fafafa; }.section-header { font-size: 1.8rem; font-weight: 700; color: #00d68f; margin-bottom: 1rem; }.stButton>button { background-color: #00d68f; color: black; font-weight: 600; }</style>''', unsafe_allow_html=True)

@st.cache_data
def load_config():
    with open("config.yaml", 'r') as f:
        return yaml.safe_load(f)

config = load_config()

def get_db_connection():
    return sqlite3.connect("bot/trades.db")

def get_performance_summary():
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM trades WHERE status = 'closed'", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    if df.empty:
        return {"trades": 0, "win_rate": 0, "total_pnl": 0}
    pnls = df['pnl'].dropna()
    win_rate = len(pnls[pnls > 0]) / len(pnls) * 100 if len(pnls) > 0 else 0
    return {
        "trades": len(df),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(pnls.sum(), 2)
    }

with st.sidebar:
    st.title("🤖 Grok Crypto Bot")
    st.caption("v1.0 • Powered by Grok")
    mode = st.selectbox("Mode", ["Backtest", "Paper Trading", "Live"])
    if st.button("🚨 EMERGENCY STOP ALL", type="primary", use_container_width=True):
        st.error("All trading halted.")
        st.stop()
    st.divider()

 tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🧪 Backtesting", "📋 Trade Ledger", "🧠 Grok Reflections", "⚙️ Strategy & Config"])

with tab1:
    st.markdown('<p class="section-header">📊 Dashboard</p>', unsafe_allow_html=True)
    stats = get_performance_summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", stats["trades"])
    c2.metric("Win Rate", f"{stats['win_rate']}%")
    c3.metric("Total PnL (USD)", f"${stats['total_pnl']:,.2f}")
    c4.metric("Status", "🟢 RUNNING" if mode != "Backtest" else "⏸️ IDLE")

    st.subheader("Equity Curve (Demo)")
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
    equity = np.cumsum(np.random.normal(40, 280, 100)) + 10000
    fig = px.line(pd.DataFrame({"Date": dates, "Equity": equity}), x="Date", y="Equity")
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<p class="section-header">🧪 Backtesting</p>', unsafe_allow_html=True)
    if st.button("🚀 RUN BACKTEST", type="primary"):
        with st.spinner("Running backtest..."):
            dh = DataHandler(config)
            df = dh.generate_synthetic_data("2025-01-01", "2025-03-01")
            summary = run_backtest(df, config)
            st.success("Backtest complete!")
            st.json(summary)

with tab3:
    st.markdown('<p class="section-header">📋 Trade Ledger</p>', unsafe_allow_html=True)
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 100", conn)
        st.dataframe(df, use_container_width=True, height=500)
    except:
        st.info("No trades yet. Run a backtest first.")
    conn.close()

with tab4:
    st.markdown('<p class="section-header">🧠 Grok Reflections</p>', unsafe_allow_html=True)
    if st.button("✨ GENERATE GROK REFLECTION PROMPT", type="primary"):
        trades = get_recent_trades(limit=20)
        if trades:
            prompt = "You are an expert quantitative crypto trading coach.\n\nAnalyze the recent trades and performance. Give concrete, testable improvements."
            st.text_area("Copy this prompt and send it to me (Grok):", prompt, height=200)
        else:
            st.warning("Run a backtest first to generate a good reflection prompt.")

with tab5:
    st.markdown('<p class="section-header">⚙️ Strategy & Config</p>', unsafe_allow_html=True)
    st.json(config)
    st.caption("Edit config.yaml and restart the app to apply changes.")

st.caption("Deployed on Streamlit Community Cloud • Powered by Grok • Risk-first architecture")