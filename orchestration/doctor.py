import subprocess
from pathlib import Path

from .log import info, success, warn, error
from .docker_cli import COMPOSE_FILE
from .env import ROOT


def run_doctor() -> None:
    info("Running environment diagnostics")

    # Location check
    if str(ROOT).startswith("/mnt/"):
        error("Project is located under /mnt — performance issues likely")
        info("Recommendation: move the project to your WSL home directory")
        return
    success("Project location OK")

    # Docker installed
    try:
        subprocess.check_output(["docker", "--version"])
        success("Docker is installed")
    except Exception:
        error("Docker is not installed")
        info("Install Docker Desktop: https://www.docker.com/products/docker-desktop/")
        return

    # Docker running
    try:
        subprocess.check_output(["docker", "info"])
        success("Docker is running")
    except Exception:
        error("Docker is installed but not running")
        info("Start Docker Desktop and wait for it to finish initializing")
        return

    # Compose file
    if COMPOSE_FILE.exists():
        success("docker-compose.yml present")
    else:
        warn("docker-compose.yml not found")
        info("It will be generated automatically on ./orch up")

    success("Diagnostics complete")
