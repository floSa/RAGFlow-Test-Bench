#!/usr/bin/env bash
# Sauvegarde à froid de RAGFlow : arrêt de la pile, archive de donnees/ragflow (volumes et réglages), redémarrage.
# L'archive est faite par un conteneur jetable (les dossiers appartiennent aux utilisateurs des conteneurs).
# Usage : outils/ragflow/sauvegarder.sh   Archive : donnees/sauvegardes/ragflow-<date-heure>.tar.gz (ignoré par git)
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p donnees/sauvegardes
nom="ragflow-$(date +%Y%m%d-%H%M%S).tar.gz"
outils/ragflow/arreter.sh
docker run --rm -v "$PWD/donnees:/d" nginx:alpine tar czf "/d/sauvegardes/$nom" -C /d ragflow
outils/ragflow/demarrer.sh >/dev/null
ls -l "donnees/sauvegardes/$nom" | awk '{print "archive : " $NF " (" $5 " octets)"}'
