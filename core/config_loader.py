import yaml
import os

def load_bootstrap_path():
    bootstrap_path = os.path.join(os.path.dirname(__file__), "../config/bootstrap.yaml")
    with open(bootstrap_path) as f:
        data = yaml.safe_load(f)
        return data["config_path"]

class ConfigLoader:
    _instance = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            if config_path is None:
                config_path = load_bootstrap_path()
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path):
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(__file__), config_path)
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, {})
            else:
                return default
        return value if value else default
