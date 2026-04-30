import subprocess
import json

from .log import info, success, warn, caution
from .docker_cli import COMPOSE_FILE


def _docker_compose_ps():
    """
    Return docker compose ps output as parsed JSON.
    """
    cmd = [
        "docker", "compose",
        "-f", str(COMPOSE_FILE),
        "ps",
        "--format", "json",
    ]
    output = subprocess.check_output(cmd)
    return json.loads(output)


def show_status() -> None:
    info("Checking environment status")

    if not COMPOSE_FILE.exists():
        warn("Compose file not found")
        info("Nothing has been started yet")
        info("Run: ./orch up")
        return

    try:
        services = _docker_compose_ps()
    except Exception:
        warn("Unable to query Docker status")
        info("Ensure Docker Desktop is running")
        return

    if not services:
        warn("No running containers detected")
        info("Run: ./orch up")
        return

    running = []
    stopped = []
    unhealthy = []

    for svc in services:
        name = svc.get("Service", "unknown")
        state = svc.get("State", "").lower()
        health = svc.get("Health", "").lower()

        if state == "running" and health in ("", "healthy"):
            running.append(name)
        elif health == "unhealthy":
            unhealthy.append(name)
        else:
            stopped.append(name)

    # ---- Output summary ----

    if running:
        success(f"Running services: {', '.join(sorted(running))}")

    if unhealthy:
        caution(f"Unhealthy services: {', '.join(sorted(unhealthy))}")
        info(
            "These services are running but not ready yet.\n"
            "Give them another minute, or check logs with:\n"
            "  ./orch logs"
        )

    if stopped:
        warn(f"Stopped services: {', '.join(sorted(stopped))}")
        info(
            "These services are not running.\n"
            "You can try restarting with:\n"
            "  ./orch up"
        )

    if not stopped and not unhealthy:
        success("Environment looks healthy")

    info("Status check complete")
