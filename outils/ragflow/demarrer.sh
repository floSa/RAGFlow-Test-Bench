#!/usr/bin/env bash
# Démarre RAGFlow (données conservées) et attend l'état sain. Le service LLM central doit tourner (géré à part ; vérification : outils/communs/llm_central_sante.sh).
set -euo pipefail
cd "$(dirname "$0")/../.."
outils/ragflow/compose.sh up -d
for i in $(seq 60); do curl -sf http://127.0.0.1:9380/api/v1/system/healthz >/dev/null && break; sleep 5; done
curl -s http://127.0.0.1:9380/api/v1/system/healthz; echo
echo "RAGFlow : http://127.0.0.1:8088 (identifiants : donnees/IDENTIFIANTS-LOCAUX.txt)"
