from utils.loader_factory import get_loader
from loaders.yaml_loader import YamlLoader

def test_get_loader_returns_yaml_loader():
    loader = get_loader("yaml", "data/strategies.yml")
    assert isinstance(loader, YamlLoader)
