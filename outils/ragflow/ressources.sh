#!/usr/bin/env bash
# Mesure des ressources de la pile RAGFlow seule (hors conteneurs de modèles de LLM-Service).
# Usage : outils/ragflow/ressources.sh <étiquette>   ex. repos, indexation
# Sortie : outils/resultats/ragflow/ressources-<date>-<étiquette>.txt
set -euo pipefail
cd "$(dirname "$0")/../.."
etiq="${1:-repos}"
out="outils/resultats/ragflow/ressources-$(date +%F)-$etiq.txt"
{
  echo "date : $(date -Iseconds) ; étiquette : $etiq"
  echo "== free -m"; free -m
  echo "== docker stats (pile rag-ragflow)"
  docker stats --no-stream --format '{{.Name}};{{.MemUsage}};{{.CPUPerc}}' | grep '^rag-ragflow' | sort
  docker stats --no-stream --format '{{.Name}};{{.MemUsage}}' | grep '^rag-ragflow' | python3 -c '
import sys, re
u = {"B": 1/2**20, "KiB": 1/1024, "MiB": 1, "GiB": 1024}
t = 0
for l in sys.stdin:
    m = re.match(r"[^;]+;([\d.]+)(\w+) /", l)
    t += float(m.group(1)) * u[m.group(2)]
print(f"total pile RAGFlow : {t:.0f} Mio")'
  echo "== conteneurs de modèles (pour mémoire, hors application)"
  docker stats --no-stream --format '{{.Name}};{{.MemUsage}}' | grep -E '^(vllm-|ollama-central)' || true
  echo "== nvidia-smi"; nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null || echo "sans GPU"
  echo "== images"
  docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep -E 'ragflow|elasticsearch:8.11.3|mysql:8.0.40|kvrocks:2.16.0|nats:2.14.2|silo:RELEASE.2026-08-06' || true
  echo "== disque des données (donnees/ragflow)"; du -sh donnees/ragflow/* 2>/dev/null || echo "(certains sous-dossiers appartiennent aux utilisateurs des conteneurs : tailles partielles)"
} > "$out"
cat "$out"
