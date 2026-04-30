import subprocess
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"


def docker_compose(args: List[str]) -> None:
    """
    Thin wrapper around `docker compose`.

    Assumes:
      - docker-compose.yml already exists
      - docker handles errors
    """
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE)] + args
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)