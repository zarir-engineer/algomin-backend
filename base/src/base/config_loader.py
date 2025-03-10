"""
✅ Single Source of Truth: Reads config.yml only once
✅ Global Access: Call config.get("key") from anywhere in your code
✅ Nested Keys Support: Use "api.api_key" instead of manually traversing dictionaries
✅ Performance: Avoids unnecessary file reads
"""

import yaml

class ConfigLoader:
    _instance = None  # Singleton instance

    def __new__(cls, config_path="config.yml"):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        """Retrieve nested config values using dot notation."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value else default
