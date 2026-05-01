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
    stopped = []
    unhealthy = []
    restarting = []

    for svc in services:
        name = svc.get("Service", "unknown")
        state = svc.get("State", "").lower()
        health = svc.get("Health", "").lower()

        if state == "restarting":
            restarting.append(name)
        elif state == "running" and health in ("", "healthy"):
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
    if restarting:
        caution(f"Restarting services: {', '.join(sorted(restarting))}")

        if "n8n" in restarting:
            info(
                "n8n is restarting repeatedly. This is most often caused by:\n"
                "  • A mismatched N8N_ENCRYPTION_KEY\n"
                "  • A failed first-time initialization\n\n"
                "If this is a new setup, the fastest fix is:\n"
                "  ./orch destroy --yes\n"
                "  ./orch up"
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
