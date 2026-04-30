import subprocess
import sys
from pathlib import Path
from typing import List
from .log import info, warn


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"


def docker_compose(args: List[str]) -> None:
    """
    Thin wrapper around `docker compose` with friendly errors.
    """
    info("Starting Docker containers")
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE)] + args
    print(">>", " ".join(cmd))

    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        sys.exit(
            " Docker is not installed.\n"
            " Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
        )
    except subprocess.CalledProcessError:
        warn(
            "Docker failed to complete the requested operation.\n"
            "Possible causes:\n"
            "  - Docker Desktop is not running\n"
            "  - A required port is already in use\n"
            "  - Previous containers are in a bad state\n\n"
            "Try:\n"
            "  1. Restart Docker Desktop\n"
            "  2. Run ./orch down && ./orch up"
        )
        sys.exit(1)