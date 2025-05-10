from unittest.mock import MagicMock
from core.config_loader import ConfigLoader

def test_config_loader_with_mock_loader():
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "db": {
            "host": "localhost",
            "port": 5432
        }
    }

    config_loader = ConfigLoader(loader=mock_loader)
    assert config_loader.get("db.host") == "localhost"
    assert config_loader.get("db.port") == 5432
    assert config_loader.get("db.user", "default_user") == "default_user"
