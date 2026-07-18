import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append(str(__import__('pathlib').Path(__file__).parent.parent))
from bot.memory import log_trade


def run_backtest(df, config, backtest_id=None):
    if backtest_id is None:
        backtest_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    print(f"[Backtest] Starting {backtest_id}...")

    trades = []
    equity = config['risk']['initial_capital']
    peak = equity

    # Simple loop for demo
    for i in range(200, len(df)):
        if np.random.random() > 0.7:  # Simulate some trades
            pnl = np.random.normal(50, 200)
            equity += pnl
            if equity > peak:
                peak = equity
            trade = {
                'timestamp': str(df.index[i]),
                'symbol': config['trading']['symbol'],
                'side': 'long' if pnl > 0 else 'short',
                'entry_price': float(df['close'].iloc[i-1]),
                'exit_price': float(df['close'].iloc[i]),
                'pnl': round(pnl, 2),
                'status': 'closed',
                'backtest_id': backtest_id
            }
            trades.append(trade)

    win_rate = len([t for t in trades if t['pnl'] > 0]) / len(trades) * 100 if trades else 0
    total_pnl = sum(t['pnl'] for t in trades)

    summary = {
        'backtest_id': backtest_id,
        'total_trades': len(trades),
        'win_rate_pct': round(win_rate, 1),
        'total_pnl_usd': round(total_pnl, 2),
        'max_drawdown_pct': round((peak - equity) / peak * 100, 2) if peak > equity else 0,
        'final_equity': round(equity, 2)
    }

    print(f"[Backtest] Done. Trades: {len(trades)} | PnL: ${total_pnl:,.2f}")
    return summary