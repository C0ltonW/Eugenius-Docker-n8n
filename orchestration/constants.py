DEFAULT_PROJECT_NAME = "n8nlocal"

# Profiles define which services exist and which runtime modifiers apply.
# This tool is local-dev only; profiles are about convenience, not scaling.

PROFILES = {
    # Minimal, durable local n8n
    "core": {
        "services": {"db", "n8n"},
        "modifiers": set(),
    },

    # core + DB inspection tooling
    "tools": {
        "services": {"db", "n8n", "adminer"},
        "modifiers": set(),
    },

    # Heavy workflows: more memory, shorter retention (no extra infra)
    "heavy": {
        "services": {"db", "n8n"},
        "modifiers": {"heavy"},
    },
}