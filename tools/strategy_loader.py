import yaml
import os

def load_limit_order_strategies():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "../data/strategies.yml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return data.get("limit_order_strategies", [])


from loaders.yaml_loader import YamlLoader

loader = YamlLoader('data/strategies.yml')
strategies = loader.load()
