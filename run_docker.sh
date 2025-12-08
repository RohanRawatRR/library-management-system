#!/usr/bin/env sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Build and start containers (migrations run in entrypoint)
docker compose up --build -d

echo "App is running at http://localhost:8000"
echo "Use 'docker compose logs -f' to see logs."

