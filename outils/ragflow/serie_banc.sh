#!/usr/bin/env bash
# Variantes du banc, l'une après l'autre (un seul essai lourd à la fois ; free -m relevé avant chacun).
# Usage : outils/ragflow/serie_banc.sh   Journal : outils/resultats/ragflow/essai-<date>-serie-banc.log
set -uo pipefail
cd "$(dirname "$0")/../.."
J="outils/resultats/ragflow/essai-$(date +%F)-serie-banc.log"
exec >>"$J" 2>&1
banc() { echo "== $(date -Iseconds) banc $*"; free -m | awk '/Mem:/{print "RAM disponible : " $7 " Mo"}'
         timeout 3600 uv run python outils/ragflow/banc.py "$@" | grep -E '^(Q|indexation|->)' ; echo "code ${PIPESTATUS[0]}"; }
# 0. réglages par défaut (réindexe le dataset Banc-general)
banc --etiquette defaut --reindexer
# 1. contexte serré : 4096 jetons déclarés (le corpus découpé fait environ 2 240 jetons)
uv run python outils/ragflow/contexte.py 4096
banc --etiquette ctx4096
uv run python outils/ragflow/contexte.py 16384
# 2. Agentic RAG (champ reasoning=5)
banc --etiquette agentic --agentic
# 3. recherche hybride : poids des vecteurs 0,7 (défaut 0,3) et top_n 8 (défaut 6)
banc --etiquette hybride-vecteurs07-top8 --poids-vecteurs 0.7 --top-n 8
# 4. gabarits de découpage (un dataset par gabarit)
for g in paper presentation table; do banc --etiquette "gabarit-$g" --gabarit "$g" --reindexer; done
echo "== $(date -Iseconds) fin de série"
