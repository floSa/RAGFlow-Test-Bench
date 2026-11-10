#!/usr/bin/env bash
# Cycle complet : désinstallation (outils/communs/nettoyer.sh ragflow --oui), réinstallation, configuration,
# vérification minimale ; chaque étape chronométrée. Les images Docker restent en cache (non supprimées).
# Usage : outils/ragflow/essai_reinstallation.sh   Journal : outils/resultats/ragflow/essai-<date>-reinstallation.log
set -uo pipefail
cd "$(dirname "$0")/../.."
J="outils/resultats/ragflow/essai-$(date +%F)-reinstallation.log"
exec > >(tee "$J") 2>&1
etape() { local t=$(date +%s); echo "== $(date -Iseconds) $1"; shift; "$@"; local c=$?; echo "-> code $c en $(( $(date +%s) - t )) s"; }
# compte fictif réutilisé (mêmes identifiants) ; la clé d'API, perdue avec la base, est recréée par configurer.py
python3 -c "import json; c=json.load(open('donnees/ragflow/compte.json')); c.pop('api_key', None); json.dump(c, open('donnees/compte-ragflow.json', 'w'))"
etape "désinstallation" outils/communs/nettoyer.sh ragflow --oui
echo "après désinstallation :"; docker ps -a --filter name=rag-ragflow --format '{{.Names}}' | sed 's/^/  conteneur restant : /'
docker volume ls --format '{{.Name}}' | grep '^rag-ragflow' | sed 's/^/  volume restant : /'; ls donnees/ragflow 2>&1 | sed 's/^/  /'
mkdir -p donnees/ragflow && mv donnees/compte-ragflow.json donnees/ragflow/compte.json && chmod 600 donnees/ragflow/compte.json
etape "installation" outils/ragflow/installer.sh
etape "configuration" python3 -I outils/ragflow/configurer.py
etape "vérification minimale" uv run python outils/ragflow/verif_minimale.py
