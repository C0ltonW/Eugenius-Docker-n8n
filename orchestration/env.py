from pathlib import Path
from typing import Dict
from .constants import DEFAULT_PROJECT_NAME


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
ENV_DEFAULT_FILE = ROOT / "templates" / "env.default"

REQUIRED_KEYS = {
    "N8N_ENCRYPTION_KEY",
    "POSTGRES_PASSWORD",
}


def _parse_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}

    if not path.exists():
        return data

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")

    return data


def load_env() -> Dict[str, str]:
    """
    Load environment variables with the following precedence:
      1. .env (user-controlled)
      2. templates/env.default (fallbacks)

    No mutation. No auto-creation. No magic.
    """

    # Prevent common WSL foot-gun
    if str(ROOT).startswith("/mnt/"):
        raise SystemExit(
            "Do not run this project from /mnt/c.\n"
            "Clone it into your WSL home directory instead."
        )

    defaults = _parse_env_file(ENV_DEFAULT_FILE)
    user_env = _parse_env_file(ENV_FILE)

    env = {**defaults, **user_env}

    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        raise SystemExit(
            "Missing required environment values:\n"
            + "\n".join(f"  - {k}" for k in missing)
            + "\n\nFix .env before continuing."
        )

    # Always ensure project name exists (safe default)
    env.setdefault("COMPOSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)

    return env