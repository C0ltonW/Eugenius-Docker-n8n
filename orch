#!/usr/bin/env bash
set -e

# --- sanity checks ---
command -v docker >/dev/null 2>&1 || {
  echo "❌ Docker is not installed."
  echo "👉 Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  exit 1
}

# --- defaults ---
PROFILE=${PROFILE:-ai}

# --- self-healing setup ---
if [ ! -f .env ]; then
  echo "⚙️  Creating .env from template..."
  cp templates/env.default .env
fi

# --- run orchestrator ---
python3 orchestrator.py --profile "$PROFILE" "$@"