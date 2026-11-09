#!/usr/bin/env bash
# Arrête RAGFlow (données conservées dans donnees/ragflow). LLM-Service n'est jamais arrêté ici : il est partagé.
set -euo pipefail
cd "$(dirname "$0")/../.."
outils/ragflow/compose.sh stop
echo "RAGFlow arrêté."
