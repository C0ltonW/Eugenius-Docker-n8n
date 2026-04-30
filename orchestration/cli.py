import argparse

from .compose_builder import build_compose
from .compose_writer import write_compose
from .docker_cli import docker_compose
from .env import load_env


def main():
    parser = argparse.ArgumentParser(
        description="Local n8n Docker orchestrator"
    )

    parser.add_argument(
        "--profile",
        default="core",
        help="Profile: core, ai, tools, dev, heavy",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("up")
    sub.add_parser("down")
    sub.add_parser("logs")
    sub.add_parser("ps")

    destroy = sub.add_parser("destroy")
    destroy.add_argument(
        "--yes",
        action="store_true",
        help="Confirm data deletion",
    )

    args = parser.parse_args()

    # --- Load env and generate compose ---
    env = load_env()
    compose = build_compose(env, args.profile)
    write_compose(compose)

    # --- Dispatch docker commands ---
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
            raise SystemExit(
                "Refusing to destroy volumes. Re-run with --yes."
            )
        docker_compose(["down", "-v"])