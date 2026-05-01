from pathlib import Path
from typing import Dict, Set
from .log import info, warn
import secrets

from .constants import DEFAULT_PROJECT_NAME


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
ENV_DEFAULT_FILE = ROOT / "templates" / "env.default"


# --------------------
# Parsing helpers
# --------------------

def _parse_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}

    if not path.exists():
        return data

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")

    return data


def _write_env_file(path: Path, env: Dict[str, str]) -> None:
    lines = []
    for k, v in sorted(env.items()):
        lines.append(f'{k}="{v}"')
    path.write_text("\n".join(lines) + "\n")


# --------------------
# Environment loader
# --------------------

def load_env() -> Dict[str, str]:
    """
    Load environment variables with the following precedence:

      1. .env (user-controlled, persisted)
      2. templates/env.default (repo-controlled defaults)

    Behavior:
    - Dev mode: generates required secrets if missing
    - Non-dev mode: fails fast if required secrets are missing
    - Warns on unknown keys (prevents config drift)
    """

    # --- WSL safety check ---
    if str(ROOT).startswith("/mnt/"):
        raise SystemExit(
            "Do not run this project from /mnt/c.\n"
            "Clone it into your WSL home directory instead."
        )

    info("Loading environment configuration")

    defaults = _parse_env_file(ENV_DEFAULT_FILE)
    user_env = _parse_env_file(ENV_FILE)

    env: Dict[str, str] = {**defaults, **user_env}

    # Environment mode
    env_mode = env.get("ENV_MODE", "dev").lower()

    if env_mode not in {"dev", "ci", "prod"}:
        raise RuntimeError(
            f"Invalid ENV_MODE '{env_mode}'. "
            "Expected one of: dev, ci, prod"
        )

    # Required secrets
    generated = False

    if not env.get("N8N_ENCRYPTION_KEY"):
        if env_mode == "dev":
            env["N8N_ENCRYPTION_KEY"] = secrets.token_hex(32)
            generated = True
        else:
            raise RuntimeError(
                "N8N_ENCRYPTION_KEY is required in non-dev environments"
            )

    if not env.get("POSTGRES_PASSWORD"):
        if env_mode == "dev":
            env["POSTGRES_PASSWORD"] = secrets.token_hex(16)
            generated = True
        else:
            raise RuntimeError(
                "POSTGRES_PASSWORD is required in non-dev environments"
            )

    if generated:
        warn(
            "Generated missing secrets and wrote them to .env.\n"
            "Review this file before committing or deploying."
        )
        _write_env_file(ENV_FILE, env)

    # Project name (always exists)
    env.setdefault("COMPOSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)

    # Unknown key detection

    known_keys: Set[str] = set(defaults) | {
        "POSTGRES_PASSWORD",
        "N8N_ENCRYPTION_KEY",
        "COMPOSE_PROJECT_NAME",
        "ENV_MODE",
    }

    unknown_keys = set(env) - known_keys
    if unknown_keys:
        warn(
            "Unknown environment variables detected:\n"
            + "\n".join(f"  - {k}" for k in sorted(unknown_keys))
        )

    info("Environment ready")
    return env
``