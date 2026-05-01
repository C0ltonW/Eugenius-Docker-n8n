from pathlib import Path
from typing import Dict
from .log import info, warn
import secrets

from .constants import DEFAULT_PROJECT_NAME


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
ENV_DEFAULT_FILE = ROOT / "templates" / "env.default"


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

def _write_env_file(path: Path, env: dict) -> None:
    lines = []
    for k, v in env.items():
        lines.append(f'{k}="{v}"')
    path.write_text("\n".join(lines) + "\n")


def load_env() -> Dict[str, str]:
    """
    Load environment variables with the following precedence:
      1. .env (user-controlled)
      2. templates/env.default (fallbacks)

    Safe defaults are generated where required.
    No user interaction required for first run.
    """

    # Prevent common WSL foot-gun


    if str(ROOT).startswith("/mnt/"):
        raise SystemExit(
            " Do not run this project from /mnt/c.\n"
            " Clone it into your WSL home directory instead."
        )

    defaults = _parse_env_file(ENV_DEFAULT_FILE)
    user_env = _parse_env_file(ENV_FILE)

    env = {**defaults, **user_env}
    info("Loading environment configuration")

    # --- Generate required secrets if missing ---
    generated = False

    key = env.get("N8N_ENCRYPTION_KEY", "").strip()

    if not key:
        env["N8N_ENCRYPTION_KEY"] = secrets.token_hex(32)
        generated = True

    if not env.get("POSTGRES_PASSWORD"):
        env["POSTGRES_PASSWORD"] = secrets.token_hex(16)
        generated = True

    if generated:
        info("Persisting generated secrets to .env")
        _write_env_file(ENV_FILE, env)

    # --- Ensure project name always exists ---
    env.setdefault("COMPOSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)

    info("Environment ready")
    return env