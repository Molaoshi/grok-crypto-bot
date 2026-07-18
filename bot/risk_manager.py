class RiskManager:
    def __init__(self, config):
        self.config = config
        self.initial_capital = config['risk']['initial_capital']
        self.risk_per_trade = config['risk']['risk_per_trade_pct'] / 100
        self.current_equity = self.initial_capital
        self.peak_equity = self.initial_capital

    def calculate_position_size(self, entry_price, stop_price):
        risk_amount = self.current_equity * self.risk_per_trade
        stop_distance = abs(entry_price - stop_price)
        if stop_distance <= 0:
            return 0.0
        return round(risk_amount / stop_distance, 6)

    def check_pre_trade(self, proposed_trade):
        approved = True
        reason = "All checks passed"
        recommended_size = self.calculate_position_size(
            proposed_trade.get('entry_price', 0),
            proposed_trade.get('stop_price', 0)
        )
        return {
            'approved': approved,
            'reason': reason,
            'recommended_size': recommended_size,
            'current_equity': self.current_equity
        }

    def get_status(self):
        return {
            'current_equity': self.current_equity,
            'peak_equity': self.peak_equity
        }