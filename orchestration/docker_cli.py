import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"


def docker_compose(args: List[str]) -> None:
    """
    Thin wrapper around `docker compose` with friendly errors.
    """
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE)] + args
    print(">>", " ".join(cmd))

    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        sys.exit(
            "❌ Docker is not installed.\n"
            "👉 Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
        )
    except subprocess.CalledProcessError:
        sys.exit(
            "❌ Docker command failed.\n"
            "👉 Is Docker running?\n"
            "👉 Try restarting Docker Desktop."
        )