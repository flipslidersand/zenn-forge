from pathlib import Path
import yaml

_DEFAULT = Path(__file__).parent.parent.parent / "config.yaml"


def load(path: Path = _DEFAULT) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
