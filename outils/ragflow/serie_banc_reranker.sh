#!/usr/bin/env bash
# Banc avec et sans reranker (service LLM central), l'un après l'autre : un seul essai lourd à la fois ;
# free -m, VRAM (nvidia-smi) et RAM des conteneurs llm-* relevés avant chacun.
# Le banc « defaut » (avec --reindexer) se lance d'abord à part ; ce script enchaîne les trois autres sur la même base.
# Usage : outils/ragflow/serie_banc_reranker.sh   Journal : outils/resultats/ragflow/essai-<date>-serie-banc.log
set -uo pipefail
cd "$(dirname "$0")/../.."
J="outils/resultats/ragflow/essai-$(date +%F)-serie-banc.log"
releve() { free -m; nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
           docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' llm-central llm-swap llm-speaches; }
banc() { e="$1"; shift
         { echo "== $(date -Iseconds) banc --etiquette $e $*"; releve; } >>"$J" 2>&1
         timeout 5400 uv run python outils/ragflow/banc.py --etiquette "$e" "$@" \
           >"outils/resultats/ragflow/essai-$(date +%F)-banc-$e.log" 2>&1
         echo "code $? ($(date -Iseconds))" >>"$J"; }
banc defaut-reranker --reranker
banc hybride-vecteurs07-top8 --poids-vecteurs 0.7 --top-n 8
banc hybride-vecteurs07-top8-reranker --poids-vecteurs 0.7 --top-n 8 --reranker
{ echo "== $(date -Iseconds) fin de série"; releve; } >>"$J" 2>&1
