#!/usr/bin/env bash
# ESSAI INTERMÉDIAIRE (abandonné le 11 novembre pour le GPU, voir reranker.sh) : TEI ne parle pas le format de rerank
# des pilotes de RAGFlow 1.0 (422 « missing field texts ») ; journal brut reranker-cpu-2026-11-11-tei.log.
# Reranker local sur processeur : Text Embeddings Inference (TEI) 1.8, conteneur rag-reranker, modèle BAAI/bge-reranker-v2-m3.
# Image : celle que le compose officiel de RAGFlow prévoit pour TEI (sources/ragflow/docker/.env, TEI_IMAGE_CPU),
# figée par empreinte. Ses modèles d'embedding embarqués (/data) sont masqués par le montage de donnees/reranker.
# - modèle téléchargé une fois depuis Hugging Face dans donnees/reranker/ (cache de TEI, ignoré par git) ;
# - aucune carte graphique (LLM-Service et ses conteneurs ne sont pas touchés) ;
# - réseau rag-local (RAGFlow y est déjà) : http://rag-reranker:80 ; port publié sur 127.0.0.1:6380 seulement.
# Usage : outils/ragflow/reranker_cpu.sh   Journal : outils/resultats/ragflow/reranker-<date>.log
set -euo pipefail
cd "$(dirname "$0")/../.."
IMAGE="infiniflow/text-embeddings-inference:cpu-1.8@sha256:ad4a00f5af757f7f323bdeb9e873313ed71225cf57d94658cbc9c6c17dc67d85"
MODELE="BAAI/bge-reranker-v2-m3"
PORT=6380
# lot maximal de jetons : 16384 par défaut, l'échauffement prend alors 13,6 Go de RAM et le conteneur redémarre en boucle
# (journal du 11 novembre) ; 2048 suffit pour une question et des passages de 512 jetons.
LOT=2048   # et --memory 6g : un dépassement tue le conteneur, pas WSL
J="outils/resultats/ragflow/reranker-$(date +%F).log"
mkdir -p donnees/reranker
exec > >(tee -a "$J") 2>&1
echo "== $(date -Iseconds) reranker.sh"
free -m | awk '/Mem:/{print "RAM disponible : " $7 " Mo"}'
docker network inspect rag-local >/dev/null 2>&1 || docker network create rag-local
if ! docker inspect rag-reranker >/dev/null 2>&1; then
  docker run -d --name rag-reranker --restart unless-stopped --memory 6g --network rag-local --hostname rag-reranker \
    -p 127.0.0.1:$PORT:80 -v "$PWD/donnees/reranker:/data" \
    "$IMAGE" --model-id "$MODELE" --auto-truncate --max-batch-tokens $LOT >/dev/null
fi
docker start rag-reranker >/dev/null
t0=$(date +%s)
for i in $(seq 450); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; sleep 2; done
curl -sf http://127.0.0.1:$PORT/health >/dev/null || { echo "rag-reranker pas sain"; docker logs --tail 40 rag-reranker; exit 1; }
echo "sain en $(( $(date +%s) - t0 )) s"
docker ps --filter name=rag-reranker --format 'conteneur : {{.Names}} {{.Image}} {{.Ports}}'
curl -s http://127.0.0.1:$PORT/info | python3 -c "import json,sys;d=json.load(sys.stdin);print('info :',d.get('model_id'),d.get('model_type'),d.get('version'),'max_input_length',d.get('max_input_length'))"
Q='{"query":"Quel est le délai de préavis ?","texts":["Le préavis de résiliation est de trois mois.","La cantine ouvre à midi."]}'
echo "POST /rerank (format natif de TEI) : $Q"
curl -s -w '\n(%{http_code}, %{time_total} s)\n' http://127.0.0.1:$PORT/rerank -H 'Content-Type: application/json' -d "$Q"
Q2='{"model":"'"$MODELE"'","query":"Quel est le délai de préavis ?","documents":["Le préavis de résiliation est de trois mois.","La cantine ouvre à midi."],"top_n":2}'
echo "POST /v1/rerank (format Jina/Cohere attendu par les pilotes de RAGFlow) : $Q2"
curl -s -w '\n(%{http_code}, %{time_total} s)\n' http://127.0.0.1:$PORT/v1/rerank -H 'Content-Type: application/json' -d "$Q2"
echo "depuis le réseau rag-local (conteneur rag-ragflow-server) :"
docker exec rag-ragflow-server curl -s -m 30 http://rag-reranker:80/health -o /dev/null -w 'http://rag-reranker:80/health -> %{http_code}\n' || true
docker stats --no-stream --format 'mémoire : {{.Name}} {{.MemUsage}}' rag-reranker
