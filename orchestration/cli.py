import argparse
import sys

from .compose_builder import build_compose
from .compose_writer import write_compose
from .docker_cli import docker_compose
from .env import load_env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local n8n Docker orchestrator"
    )

    parser.add_argument(
        "--profile",
        default="ai",
        help="Profile to run (core, ai, tools, dev, heavy). Default: ai",
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sub.add_parser("up", help="Start the stack")
    sub.add_parser("down", help="Stop the stack")
    sub.add_parser("logs", help="Follow logs")
    sub.add_parser("ps", help="Show container status")

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

    # --- Load env ---
    try:
        env = load_env()
    except Exception as exc:
        sys.exit(f"❌ Failed to load environment: {exc}")

    # --- Build + write compose ---
    try:
        compose = build_compose(env, args.profile)
        write_compose(compose)
    except Exception as exc:
        sys.exit(f"❌ Failed to generate compose file: {exc}")

    # --- Dispatch docker commands ---
    try:
        if args.command == "up":
            docker_compose(["up", "-d"])

        elif args.command == "down":
            docker_compose(["down"])

        elif args.command == "logs":
            docker_compose(["logs", "-f", "--tail=200"])

        elif args.command == "ps":
            docker_compose(["ps"])

        elif args.command == "destroy":
            if not args.yes:
                sys.exit(
                    "❌ Refusing to destroy volumes.\n"
                    "Re-run with: ./orch destroy --yes"
                )
            docker_compose(["down", "-v"])

    except Exception as exc:
        sys.exit(f"❌ Docker command failed: {exc}")