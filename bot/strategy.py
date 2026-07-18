import pandas as pd
import numpy as np

def calculate_indicators(df, config):
    cfg = config.get('strategy', {})
    df['ema_fast'] = df['close'].ewm(span=cfg.get('ema_fast', 50), adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=cfg.get('ema_slow', 200), adjust=False).mean()
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    high_low = df['high'] - df['low']
    tr = pd.concat([high_low, np.abs(df['high'] - df['close'].shift()), np.abs(df['low'] - df['close'].shift())], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    df['trend'] = np.where(df['ema_fast'] > df['ema_slow'], 'up', 'down')
    return df

def generate_signal(df, config, current_funding=None):
    if len(df) < 200:
        return {'action': 'hold', 'confidence': 0, 'reason': 'Insufficient data'}
    df = calculate_indicators(df, config)
    latest = df.iloc[-1]
    cfg = config.get('strategy', {})

    action = 'hold'
    confidence = 0.0
    reason = ''

    if latest['trend'] == 'up' and latest['rsi'] < cfg.get('rsi_long_threshold', 45):
        action = 'long'
        confidence = 0.65
        reason = 'Uptrend + RSI pullback'
    elif latest['trend'] == 'down' and latest['rsi'] > cfg.get('rsi_short_threshold', 55):
        action = 'short'
        confidence = 0.60
        reason = 'Downtrend + RSI overbought'

    return {
        'action': action,
        'confidence': round(confidence, 2),
        'reason': reason,
        'entry_price': round(latest['close'], 2),
        'stop_price': round(latest['close'] - latest['atr'] * 2, 2),
        'target_price': round(latest['close'] + latest['atr'] * 3, 2)
    }