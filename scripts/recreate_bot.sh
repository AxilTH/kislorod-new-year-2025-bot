#!/usr/bin/env bash
# Safely recreate the 'bot' service so it picks up updated .env and image.
# Usage: ./scripts/recreate_bot.sh
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Rebuilding image and recreating bot container (no deps)..."
docker compose build bot
# --no-deps prevents postgres/api recreation; --force-recreate ensures new env is applied
docker compose up -d --no-deps --force-recreate bot

echo "Tailing bot logs (press Ctrl-C to stop)"
docker compose logs -f --tail 200 bot
