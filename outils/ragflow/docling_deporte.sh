#!/usr/bin/env bash
# Branche RAGFlow sur un serveur Docling séparé (docling-serve), ou le débranche (manuel 06, étapes 31 à 33).
# Usage : outils/ragflow/docling_deporte.sh brancher|debrancher
#   brancher   : démarre rag-docling-serve sur le réseau llm-net s'il ne tourne pas déjà (un serveur partagé, par exemple
#                celui d'Open WebUI, est réutilisé), écrit DOCLING_SERVER_URL et ALLOW_ANY_HOST=1 dans
#                donnees/ragflow/ragflow.env, puis recrée le serveur RAGFlow.
#   debrancher : remet ALLOW_ANY_HOST=0, recrée le serveur RAGFlow ; arrête et supprime rag-docling-serve seulement s'il
#                a été lancé par ce script.
# ALLOW_ANY_HOST=1 est obligatoire : sans lui, RAGFlow refuse toute adresse du réseau privé (« URL resolves to a
# non-public address »). Il vaut pour toute l'instance (agents, connecteurs), pas seulement pour Docling.
set -euo pipefail
cd "$(dirname "$0")/../.."
ENV=donnees/ragflow/ragflow.env
IMAGE="quay.io/docling-project/docling-serve-cpu:v1.38.2@sha256:7a480a1604fa3b42efeddc7db9527690d9f9bc903226136013e2bfe6b1a4dfb0"
reglage() {  # reglage NOM VALEUR : remplace la ligne NOM=… ou l'ajoute
  if grep -q "^$1=" "$ENV"; then sed -i "s|^$1=.*|$1=$2|" "$ENV"; else printf '%s=%s\n' "$1" "$2" >> "$ENV"; fi
}
attendre_ragflow() {
  for i in $(seq 60); do curl -sf http://127.0.0.1:9380/api/v1/system/healthz >/dev/null && { echo "RAGFlow prêt ($((i*3)) s)"; return; }; sleep 3; done
  echo "RAGFlow ne répond pas : docker logs rag-ragflow-server"; exit 1
}
case "${1:-}" in
  brancher)
    if [ "$(docker inspect -f '{{.State.Running}}' rag-docling-serve 2>/dev/null)" = true ]; then
      echo "Serveur rag-docling-serve déjà démarré : réutilisé"
    else
      docker rm -f rag-docling-serve >/dev/null 2>&1 || true
      docker run -d --name rag-docling-serve --network llm-net --restart unless-stopped \
        --label rag.lance-par=ragflow "$IMAGE" >/dev/null
      for i in $(seq 100); do docker logs rag-docling-serve 2>&1 | grep -q "Uvicorn running" && break; sleep 3; done
      echo "Serveur rag-docling-serve démarré"
    fi
    reglage DOCLING_SERVER_URL http://rag-docling-serve:5001
    reglage ALLOW_ANY_HOST 1
    outils/ragflow/compose.sh up -d ragflow-cpu
    attendre_ragflow
    echo "RAGFlow branché sur http://rag-docling-serve:5001 : choisir « Docling » dans « Analyseur PDF » de la base"
    ;;
  debrancher)
    reglage ALLOW_ANY_HOST 0
    outils/ragflow/compose.sh up -d ragflow-cpu
    attendre_ragflow
    if [ "$(docker inspect -f '{{index .Config.Labels "rag.lance-par"}}' rag-docling-serve 2>/dev/null)" = ragflow ]; then
      docker rm -f rag-docling-serve >/dev/null && echo "Serveur rag-docling-serve arrêté et supprimé"
    fi
    echo "RAGFlow débranché : les bases réglées sur « Docling » ne peuvent plus lire de PDF"
    ;;
  *) echo "Usage : $0 brancher|debrancher"; exit 2 ;;
esac
