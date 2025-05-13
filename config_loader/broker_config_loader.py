# config_loader.py
import yaml
from pathlib import Path
from config_loader.base_config_loader import BaseConfigLoader

class BrokerConfigLoader(BaseConfigLoader):
    def __init__(self, path="config_loader/common.yaml"):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = base_dir / path
        self.config = self._load_yaml(self.config_path)

    def _load_yaml(self, path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Failed to load YAML from {path}: {e}")
            return {}

    def load_credentials(self) -> dict:
        return self.config.get("smart_connect", {})

    def load_ws_config(self) -> dict:
        return self.config.get("websocket", {})