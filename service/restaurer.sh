#!/usr/bin/env bash
# Restauration à froid : arrêt, remplacement de donnees/ragflow par le contenu de l'archive, redémarrage.
# Usage : service/restaurer.sh donnees/sauvegardes/ragflow-<date-heure>.tar.gz
set -euo pipefail
cd "$(dirname "$0")/.."
arch="${1:?usage : restaurer.sh <archive dans donnees/sauvegardes>}"
[ -f "$arch" ] || { echo "archive introuvable : $arch"; exit 1; }
service/arreter.sh
docker run --rm -v "$PWD/donnees:/d" nginx:alpine sh -c "rm -rf /d/ragflow && tar xzf /d/sauvegardes/$(basename "$arch") -C /d"
service/demarrer.sh >/dev/null
echo "restauré depuis $arch"
