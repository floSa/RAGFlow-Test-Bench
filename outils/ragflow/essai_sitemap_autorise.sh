#!/usr/bin/env bash
# Rejoue essai_sitemap.py avec ALLOW_ANY_HOST=1 (adresses privées autorisées), puis rétablit le réglage d'origine.
# Le réglage ouvre aussi les agents et les outils web aux adresses privées : jamais laissé en place.
# Usage : outils/ragflow/essai_sitemap_autorise.sh   Sortie : outils/resultats/ragflow/essai-<date>-sitemap-autorise.log
set -uo pipefail
cd "$(dirname "$0")/../.."
ENVF=donnees/ragflow/ragflow.env
J="outils/resultats/ragflow/essai-$(date +%F)-sitemap-autorise.log"
sante() { for i in $(seq 60); do curl -sf http://127.0.0.1:9380/api/v1/system/healthz >/dev/null && return 0; sleep 3; done; return 1; }
echo "ALLOW_ANY_HOST=1  # temporaire, essai_sitemap_autorise.sh" >> "$ENVF"
outils/ragflow/compose.sh up -d ragflow-cpu >/dev/null 2>&1; sante && echo "serveur redémarré avec ALLOW_ANY_HOST=1"
docker exec rag-ragflow-server printenv ALLOW_ANY_HOST
uv run python outils/ragflow/essai_sitemap.py
mv "outils/resultats/ragflow/essai-$(date +%F)-sitemap.log" "$J"
sed -i '/essai_sitemap_autorise.sh/d' "$ENVF"
outils/ragflow/compose.sh up -d ragflow-cpu >/dev/null 2>&1; sante && echo "réglage rétabli : ALLOW_ANY_HOST=$(docker exec rag-ragflow-server printenv ALLOW_ANY_HOST)" | tee -a "$J"
