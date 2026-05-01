import subprocess
import json

from .log import info, success, warn, caution
from .docker_cli import COMPOSE_FILE


def _docker_running() -> bool:
    try:
        subprocess.check_output(
            ["docker", "info"],
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False

def _docker_compose_ps():
    """
    Return docker compose ps output as a list of JSON objects.
    Handles one-JSON-object-per-line output correctly.
    """
    cmd = [
        "docker", "compose",
        "-f", str(COMPOSE_FILE),
        "ps",
        "--format", "json",
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,  # critical: do NOT fail on exit code
    )

    services = []

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        services.append(json.loads(line))

    return services


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
        if not _docker_running():
            warn("Docker is not running")
            info("Start Docker Desktop and wait for it to finish initializing")
            return

        warn("Docker is running, but service status could not be determined")
        info(
            "This usually means one or more services are restarting or unhealthy.\n"
            "Next steps:\n"
            "  • Check logs: ./orch logs\n"
            "  • Check container state: ./orch ps"
        )
        return

    if not services:
        warn("No running containers detected")
        info("Run: ./orch up")
        return

    running = []
    starting = []
    restarting = []
    unhealthy = []
    stopped = []

    for svc in services:
        name = svc.get("Service", "unknown")
        state = svc.get("State", "").lower()
        health = svc.get("Health", "").lower()

        if state == "restarting":
            restarting.append(name)

        elif health == "starting":
            starting.append(name)

        elif health == "unhealthy":
            unhealthy.append(name)

        elif state == "running":
            running.append(name)
        else:
            stopped.append(name)


    # ---- Output summary ----
    if running:
        success(f"Running services: {', '.join(sorted(running))}")

    if starting:
        info(f"Starting services: {', '.join(sorted(starting))}")
        info(
            "These services are initializing.\n"
            "This is normal on first startup and may take a minute."
        )

    if restarting:
        caution(f"Restarting services: {', '.join(sorted(restarting))}")
        if "n8n" in restarting:
            info(
                "n8n is restarting repeatedly.\n"
                "If this is a new setup, try:\n"
                "  ./orch destroy --yes\n"
                "  ./orch up"
            )

    if unhealthy:
        caution(f"Unhealthy services: {', '.join(sorted(unhealthy))}")
        info("Check logs with:\n  ./orch logs")

    if stopped:
        warn(f"Stopped services: {', '.join(sorted(stopped))}")
        info("Run:\n  ./orch up")

    if not stopped and not unhealthy and not restarting and not starting:
        success("Environment looks healthy")

    info("Status check complete")
