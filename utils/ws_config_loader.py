import yaml
from pathlib import Path
from core.errors import YAMLLoadError

class ConfigLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path="data/config.yaml", common_path="config_loader/common.yaml"):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = base_dir / config_path
        self.common_path = base_dir / common_path

        self.config = self._load_yaml(self.config_path)
        self.common = self._load_yaml(self.common_path)

    def _load_yaml(self, config_path):
        try:
            config_path = Path(config_path)
            if not config_path.is_absolute():
                base_dir = Path(__file__).resolve().parent.parent
                config_path = base_dir / config_path

            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except YAMLLoadError as e:
            print(e)

    def get(self, key, default=None):
        """
        Get from config.yaml using dotted path (e.g., "api_key")
        """
        return self._get_nested(self.config, key, default)

    def get_common(self, key, default=None):
        """
        Get from common.yaml using dotted path (e.g., "websocket.tokenList")
        """
        return self._get_nested(self.common, key, default)

    def _get_nested(self, data_dict, dotted_key, default):
        keys = dotted_key.split(".")
        val = data_dict
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, default)
            else:
                return default
        return val if val else default


    @classmethod
    def from_config(cls):
        config_loader = ConfigLoader()

        api_key = config_loader.get("api_key")
        client_id = config_loader.get("client_id")

        instance = cls(api_key, client_id)

        # Load WS config into instance
        instance.load_ws_config()

        return instance

    def load_ws_config(self):
        from core.strategy_loader import StrategyLoader
        from utils.ws_config_loader import ConfigLoader

        # Load general WS config
        config = ConfigLoader("config_loader/common.yaml").get("websocket", {})
        self.mode = config.get("mode", "full")  # fallback to 'full' if missing
        self.correlation_id = f"limit_order_{int(time.time())}"

        # Load tokens from strategies.yaml
        strategy_loader = StrategyLoader()
        self.token_list = strategy_loader.extract_subscription_tokens("limit_order_strategies")

        print(f"✅ WS mode: {self.mode}")
        print(f"✅ Subscriptions: {self.token_list}")

def load_ws_config(path="config_loader/common.yaml"):
    with open(Path(path)) as f:
        data = yaml.safe_load(f)
    return data.get("websocket", {})
