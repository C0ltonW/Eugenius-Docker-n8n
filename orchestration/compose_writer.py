from pathlib import Path
from typing import Dict
import yaml


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"


def write_compose(compose: Dict) -> None:
    """
    Write docker-compose.yml from in-memory dict.

    Uses modern Compose format (no version key).
    """
    with COMPOSE_FILE.open("w") as fh:
        yaml.safe_dump(
            compose,
            fh,
            sort_keys=False,
            default_flow_style=False,
            indent=2,
        )
