import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataHandler:
    def __init__(self, config):
        self.config = config
        self.symbol = config['trading']['symbol']

    def generate_synthetic_data(self, start_date, end_date, initial_price=60000):
        dates = pd.date_range(start=start_date, end=end_date, freq='5min')
        n = len(dates)
        prices = [initial_price]
        for i in range(1, n):
            ret = np.random.normal(0.00002, 0.0015)
            if random.random() < 0.02:
                ret *= 3
            prices.append(max(prices[-1] * (1 + ret), 1000))

        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.001))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.001))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 50000, n)
        })
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        df.set_index('timestamp', inplace=True)
        return df

    def fetch_ohlcv(self, limit=500):
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        return self.generate_synthetic_data(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))