import yaml
from pathlib import Path


class StrategyLoader:
    def __init__(self, path="data/strategies.yaml"):
        self.path = Path(path)
        self.data = self._load_yaml()

    def _load_yaml(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Strategy YAML not found: {self.path}")
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def extract_subscription_tokens(self, strategy_type="limit_order_strategies"):
        """
        Returns a list of dicts: [{exchangeType: 1, tokens: [...]}, ...]
        """
        token_map = {}
        strategies = self.data.get(strategy_type, [])
        for strat in strategies:
            exchange_type = strat.get("exchangeType", 1)  # default to NSE
            token = strat.get("symbol_token")
            if token:
                token_map.setdefault(exchange_type, []).append(token)

        return [
            {"exchangeType": k, "tokens": v}
            for k, v in token_map.items()
        ]
