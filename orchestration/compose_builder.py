# orchestration/compose_builder.py
from typing import Dict, Set, Iterable
from pathlib import Path
from .log import info, caution
from .constants import PROFILES, DEFAULT_PROJECT_NAME


ROOT = Path(__file__).resolve().parents[1]


def _apply_heavy_modifiers(env: Dict[str, str]) -> Dict[str, str]:
    """
    Heavy mode = runtime tuning only.
    No extra services.
    """
    result: Dict[str, str] = {}

    # Give Node more headroom for heavy workflows
    result["NODE_OPTIONS"] = env.get("NODE_OPTIONS", "--max-old-space-size=4096")

    # Reduce retention by default in heavy mode to keep DB slim during stress testing
    result["EXECUTIONS_DATA_MAX_AGE"] = env.get("EXECUTIONS_DATA_MAX_AGE", "72")

    return result


def _pick_env(env: Dict[str, str], keys: Iterable[str]) -> Dict[str, str]:
    """
    Copy selected keys from env if present and non-empty.
    Keeps compose env explicit without silently passing everything through.
    """
    out: Dict[str, str] = {}
    for k in keys:
        v = env.get(k)
        if v is not None and str(v).strip() != "":
            out[k] = v
    return out


def build_compose(env: Dict[str, str], profile: str) -> Dict:
    """
    Build an in-memory docker-compose model for n8n local development.
    """

    info(f"Building Docker Compose configuration (profile: {profile})")

    caution(
        "Do not change N8N_ENCRYPTION_KEY after first startup.\n"
        "Changing it will prevent n8n from starting and may break saved credentials."
    )

    if profile not in PROFILES:
        raise ValueError(
            f"Unknown profile '{profile}'. Available: {list(PROFILES.keys())}"
        )

    profile_cfg = PROFILES[profile]
    services_enabled: Set[str] = profile_cfg["services"]
    modifiers: Set[str] = profile_cfg["modifiers"]

    project_name = env.get("COMPOSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)

    services: Dict[str, Dict] = {}

    volume_candidates = {
        "postgres_data": {},
        "n8n_data": {},
        "n8n_files": {},
        "ollama_data": {},
    }

    # --------------------
    # Postgres
    # --------------------
    if "db" in services_enabled:
        info("Postgres service enabled")
        services["postgres"] = {
            "image": env.get("POSTGRES_IMAGE", "postgres:15"),
            "container_name": f"{project_name}_postgres",
            "environment": {
                "POSTGRES_DB": env.get("POSTGRES_DB", "n8n"),
                "POSTGRES_USER": env.get("POSTGRES_USER", "n8n"),
                "POSTGRES_PASSWORD": env["POSTGRES_PASSWORD"],
                "TZ": env.get("TZ", "America/New_York"),
            },
            "volumes": [
                "postgres_data:/var/lib/postgresql/data",
            ],
            "ports": [
                f"{env.get('POSTGRES_PORT', '5432')}:5432",
            ],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"],
                "interval": "5s",
                "timeout": "5s",
                "retries": 20,
            },
        }

    # --------------------
    # n8n
    # --------------------
    if "n8n" in services_enabled:
        n8n_port = env.get("N8N_PORT", "5678")

        n8n_env: Dict[str, str] = {
            "TZ": env.get("TZ", "America/New_York"),
            "GENERIC_TIMEZONE": env.get(
                "GENERIC_TIMEZONE", env.get("TZ", "America/New_York")
            ),

            # CRITICAL for persistence
            "N8N_ENCRYPTION_KEY": env.get("N8N_ENCRYPTION_KEY", ""),

            "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": env.get(
                "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS", "true"
            ),
            "N8N_RUNNERS_ENABLED": env.get("N8N_RUNNERS_ENABLED", "true"),

            "N8N_BASIC_AUTH_ACTIVE": env.get("N8N_BASIC_AUTH_ACTIVE", "true"),
            "N8N_BASIC_AUTH_USER": env.get("N8N_BASIC_AUTH_USER", "admin"),
            "N8N_BASIC_AUTH_PASSWORD": env.get(
                "N8N_BASIC_AUTH_PASSWORD", "change_me"
            ),

            "N8N_HOST": env.get("N8N_HOST", "localhost"),
            "N8N_PORT": n8n_port,
            "N8N_PROTOCOL": env.get("N8N_PROTOCOL", "http"),

            "DB_TYPE": "postgresdb",
            "DB_POSTGRESDB_HOST": "postgres",
            "DB_POSTGRESDB_PORT": "5432",
            "DB_POSTGRESDB_DATABASE": env.get("POSTGRES_DB", "n8n"),
            "DB_POSTGRESDB_USER": env.get("POSTGRES_USER", "n8n"),
            "DB_POSTGRESDB_PASSWORD": env.get("POSTGRES_PASSWORD", "n8n"),

            "EXECUTIONS_DATA_PRUNE": env.get("EXECUTIONS_DATA_PRUNE", "true"),
            "EXECUTIONS_DATA_MAX_AGE": env.get("EXECUTIONS_DATA_MAX_AGE", "168"),
            "EXECUTIONS_DATA_SAVE_ON_ERROR": env.get(
                "EXECUTIONS_DATA_SAVE_ON_ERROR", "all"
            ),
            "EXECUTIONS_DATA_SAVE_ON_SUCCESS": env.get(
                "EXECUTIONS_DATA_SAVE_ON_SUCCESS", "none"
            ),
            "OLLAMA_BASE_URL": env.get(
                "OLLAMA_BASE_URL", "http://ollama:11434"
            ),

        }

        # Allowlisted pass-through (AI/dev-friendly, still explicit)
        n8n_env.update(_pick_env(env, [
            "N8N_LOG_LEVEL",
            "N8N_DIAGNOSTICS_ENABLED",
            "N8N_PERSONALIZATION_ENABLED",
            "N8N_BINARY_DATA_MODE",
            "N8N_BINARY_DATA_STORAGE_PATH",
            "N8N_PAYLOAD_SIZE_MAX",
            "WEBHOOK_URL",
        ]))

        if "heavy" in modifiers:
            n8n_env.update(_apply_heavy_modifiers(env))

        services["n8n"] = {
            "container_name": f"{project_name}_n8n",
            "image": env.get("N8N_IMAGE", "docker.n8n.io/n8nio/n8n:1"),
            "ports": [
                f"{n8n_port}:{n8n_port}",
            ],
            "environment": n8n_env,
            "volumes": [
                "n8n_data:/home/node/.n8n",
                "n8n_files:/files",
            ],
            "restart": "unless-stopped",
            "extra_hosts": [
                "host.docker.internal:host-gateway",
            ],
            "healthcheck": {
                "test": [
                    "CMD-SHELL",
                    "curl -fsS http://localhost:5678/ || exit 1"
                ],
                "interval": "15s",
                "timeout": "5s",
                "retries": 20,
                "start_period": "180s",
            },

        }

        if "postgres" in services:
            services["n8n"]["depends_on"] = {
                "postgres": {"condition": "service_healthy"}
            }

        if "ollama" in services:
            services["n8n"].setdefault("depends_on", {})
            services["n8n"]["depends_on"]["ollama"] = {
                "condition": "service_started"
            }

        # Optional local Dockerfile override (path safe regardless of cwd)
        dockerfile = ROOT / "docker" / "n8n" / "Dockerfile"
        if dockerfile.exists():
            info("Local n8n Dockerfile detected — building image on the fly")
            services["n8n"]["build"] = {"context": str(dockerfile.parent)}
            services["n8n"]["image"] = f"{project_name}-n8n:dev"

    # --------------------
    # Ollama (AI sidecar)
    # --------------------
    if "ollama" in services_enabled:
        info("Ollama AI sidecar enabled")
        services["ollama"] = {
            "image": env.get("OLLAMA_IMAGE", "ollama/ollama:latest"),
            "container_name": f"{project_name}_ollama",
            "ports": [
                f"{env.get('OLLAMA_PORT', '11434')}:11434",
            ],
            "volumes": [
                "ollama_data:/root/.ollama",
            ],
            "restart": "unless-stopped",

        }
        # One-shot init container to ensure a default model is available
        services["ollama_init"] = {
            "image": env.get("OLLAMA_IMAGE", "ollama/ollama:latest"),
            "container_name": f"{project_name}_ollama_init",
            "depends_on": ["ollama"],
            "volumes": [
                "ollama_data:/root/.ollama",
            ],
            "entrypoint": [
                "sh",
                "-c",
                f"ollama pull {env.get('OLLAMA_DEFAULT_MODEL', 'llama3')}",
            ],
            "restart": "no",
        }

    # --------------------
    # Adminer (optional)
    # --------------------
    if "adminer" in services_enabled:
        info("Administrator enabled")
        services["adminer"] = {
            "image": env.get("ADMINER_IMAGE", "adminer:latest"),
            "container_name": f"{project_name}_adminer",
            "ports": [
                f"{env.get('ADMINER_PORT', '8080')}:8080",
            ],
            "restart": "unless-stopped",
            "depends_on": ["postgres"] if "postgres" in services else [],
        }

    # --------------------
    # Prune unused volumes (same pattern you already use)
    # --------------------
    used_volume_names = set()
    for svc in services.values():
        for mount in svc.get("volumes", []) or []:
            if isinstance(mount, str) and ":" in mount and not mount.startswith("."):
                used_volume_names.add(mount.split(":", 1)[0])

    volumes = {
        name: volume_candidates[name]
        for name in used_volume_names
        if name in volume_candidates
    }

    return {
        "name": project_name,
        "services": services,
        "volumes": volumes,
    }