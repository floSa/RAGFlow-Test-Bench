#!/usr/bin/env bash
# Appelle docker compose sur le projet rag-ragflow avec les bons fichiers. Usage : outils/ragflow/compose.sh <commande compose…>
set -euo pipefail
R="$(cd "$(dirname "$0")/../.." && pwd)"
exec docker compose -p rag-ragflow --env-file "$R/donnees/ragflow/ragflow.env" \
  -f "$R/sources/ragflow/docker/docker-compose.yml" -f "$R/outils/ragflow/compose.override.yml" "$@"
