#!/usr/bin/env bash
# Script to install Docker & Docker Compose and start Postgres via docker-compose on Ubuntu
# Run as root or with sudo: sudo bash scripts/setup_docker_db.sh

set -euo pipefail

echo "Installing Docker Engine and docker-compose-plugin..."
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Create docker group and add current user if needed
if ! getent group docker > /dev/null; then
  groupadd docker || true
fi

# Start docker
systemctl enable --now docker

echo "Starting Postgres via docker-compose..."
# Ensure we are at project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Bring up postgres service
/usr/bin/docker compose up -d postgres

echo "Postgres should be running. Check 'docker ps' for container status."

echo "If you used the example .env, connect with:\n  postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/kislorod"
