import argparse
import sys

from .docker_cli import docker_compose
from .log import success, info, caution, banner, debug
from .status import show_status


def prepare_environment(profile: str):
    """
    Load env and (re)generate docker-compose.
    Called only for lifecycle-changing commands.
    """
    from .env import load_env
    from .compose_builder import build_compose
    from .compose_writer import write_compose

    debug("Loading environment configuration")
    env = load_env()

    debug(f"Generating Docker Compose configuration (profile: {profile})")
    compose = build_compose(env, profile)
    write_compose(compose)

    return env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local n8n Docker orchestrator"
    )

    parser.add_argument(
        "--profile",
        default="ai",
        help="Profile to run (core, ai, tools, dev, heavy). Default: ai",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("help", help="Show available commands")
    sub.add_parser("doctor", help="Run environment diagnostics")
    sub.add_parser("status", help="Show service status")
    sub.add_parser("logs", help="Follow container logs")
    sub.add_parser("ps", help="Show container status")

    sub.add_parser("up", help="Start the environment")
    sub.add_parser("down", help="Stop the environment")
    sub.add_parser("restart", help="Restart the environment")

    destroy = sub.add_parser(
        "destroy",
        help="Destroy containers and volumes (DATA LOSS)",
    )
    destroy.add_argument(
        "--yes",
        action="store_true",
        help="Confirm data deletion",
    )

    args = parser.parse_args()

    # --------------------
    # Commands that do NOT need setup
    # --------------------

    if args.command == "help":
        print_help()
        return

    if args.command == "doctor":
        from .doctor import run_doctor
        run_doctor()
        return

    if args.command == "status":
        show_status()
        return

    # --------------------
    # Commands that MAY read Docker state only
    # --------------------

    if args.command == "logs":
        docker_compose(["logs", "-f", "--tail=200"])
        return

    if args.command == "ps":
        docker_compose(["ps"])
        return

    # --------------------
    # Lifecycle-changing commands (require setup)
    # --------------------

    try:
        prepare_environment(args.profile)

        if args.command == "up":
            info("Starting environment")
            docker_compose(["up", "-d"])

            banner("YOUR ENVIRONMENT IS READY")

            success("All containers are running")
            info("n8n is available at: http://localhost:5678")

            caution(
                "On first startup, n8n may take 30–60 seconds to finish initializing."
            )

        elif args.command == "down":
            info("Stopping environment")
            docker_compose(["down"])

        elif args.command == "restart":
            info("Restarting environment")

            docker_compose(["down"])
            docker_compose(["up", "-d"])

            success("Environment restarted successfully")

        elif args.command == "destroy":
            if not args.yes:
                sys.exit(
                    "Refusing to destroy volumes.\n"
                    "Re-run with: ./orch destroy --yes"
                )

            caution("Destroying all containers and volumes")
            docker_compose(["down", "-v"])
            success("Environment destroyed")

    except Exception as exc:
        sys.exit(f"❌ Docker command failed: {exc}")


def print_help() -> None:
    print(
        """
Eugenius n8n Orchestrator
========================

Usage:
  ./orch <command> [options]

Common commands:
  up        Start the environment
  down      Stop the environment
  restart   Restart everything (down + up)
  status    Show service status
  logs      Follow container logs
  doctor    Run environment diagnostics
  destroy   Stop and remove all data (requires --yes)

Examples:
  ./orch up
  ./orch status
  ./orch restart
  ./orch doctor

Tips:
- First startup may take a few minutes while images are built
- You can safely rerun 'up' or 'restart' at any time
- Check status if something feels slow

Need help?
- Run: ./orch doctor
- Check logs: ./orch logs
"""
    )