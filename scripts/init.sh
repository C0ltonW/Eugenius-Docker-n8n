#!/usr/bin/env bash
set -e

echo "▶ Initializing project..."

# Ensure .env exists
if [ ! -f .env ]; then
  cp templates/env.default .env
  echo "✅ .env created from template"
else
  echo "✅ .env already exists"
fi

# Create required directories
mkdir -p data logs

# Ensure orchestrator is executable
chmod +x orchestrator.py

echo "✅ Initialization complete"
echo "Run: ./orch up"
